#!/usr/bin/env python3
"""Work out which comments a branch actually touched.

The sweep must not hand an agent a file and the instruction to improve it: that produces a diff no
reviewer asked for and a comment budget nobody can defend. This script narrows the job to the members
the branch changed, by intersecting the changed line ranges with the declaration ranges `sb map`
reports, and it does so without a model, because the intersection is arithmetic.

Two kinds of target come out. A `doc` target is a declaration whose doc comment or body the branch
touched. An `inline` target is a `//` or `/* */` comment inside a changed range, addressed by its own
opening words rather than by a line number, because line numbers move the moment the sweep edits
anything above them.

  survey  build the target list for every Java file the branch touched
  pairs   the before and after material for one file, for the sweeper and the judge
  touched the line numbers a given ref-to-disk diff changed, for classifying a build failure
  ledger  record which files are finished, so a later run resumes instead of starting over

The ledger keys on file content, not on target identity. A target id moves the moment the sweep
rewrites the comment it is named after, so an id-keyed ledger would fail to match exactly the entries
it just wrote; a file whose bytes are unchanged since it was approved, on the other hand, provably has
nothing new to sweep. The same property re-opens a file the moment anyone edits it again, which is the
behaviour you want when the branch grows after a sweep.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from strip_java_comments import ParseError, Span, Unverifiable  # noqa: E402
from strip_java_comments import scan as scan_java  # noqa: E402
from strip_go_comments import scan as scan_go  # noqa: E402


@dataclass(frozen=True)
class Language:
    """One language the sweep can read.

    `scan` is most of the language surface: it returns the comment spans of a source file, or raises
    ParseError / Unverifiable, and both the target survey and the comment-only oracle go through it.
    Adding a language is an entry here plus a scanner with that signature.

    `docs_by_position` is the one thing a scanner cannot settle on its own. In Java a doc comment is
    spelled differently from an ordinary one (`/**`), so the lexer labels it. In Go it is spelled
    identically and identified by where it sits — immediately above a declaration — which only the
    caller knows, because only the caller has the declaration line numbers. Set it for any language
    whose doc comments are positional, or every doc comment will also be collected as an inline
    target and swept twice.
    """

    name: str
    suffixes: Tuple[str, ...]
    scan: Callable[[str], List[Span]]
    is_test: Callable[[str], bool]
    docs_by_position: bool = False


LANGUAGES: Tuple[Language, ...] = (
    Language(
        name="java",
        suffixes=(".java",),
        scan=scan_java,
        is_test=lambda path: "/src/test/" in f"/{path}" or path.endswith("Test.java"),
    ),
    Language(
        name="go",
        suffixes=(".go",),
        scan=scan_go,
        is_test=lambda path: path.endswith("_test.go"),
        docs_by_position=True,
    ),
)


# A package-level grouped declaration: `const (`, `var (`, `type (` at column 0. Used only under
# Language.docs_by_position, where the comment above such a block is a doc comment that no
# declaration line can be matched against.
_GROUP_DECL = re.compile(r"(const|var|type)\s*\(")

# The generated-code banner, per https://go.dev/s/generatedcode, which every generator in this space
# emits and every other tool keys on. It has to appear near the top, before the code proper.
_GENERATED = re.compile(r"^(//|/\*|\s*\*)\s*Code generated .* DO NOT EDIT\.", re.MULTILINE)


def _is_generated(root: str, path: str) -> bool:
    """Whether a file announces itself as generated, and so has no comment a human should edit.

    Diff-scoped runs rarely meet one, because a regenerated artifact usually lands in the same commit
    as the source it came from and nobody reviews it. A path-scoped run meets them constantly: the
    first survey of `api/v1` proposed 110 targets in `zz_generated.deepcopy.go`, every one of them a
    banner controller-gen would overwrite on the next `make generate`.
    """
    try:
        with open(os.path.join(root, path), "r", encoding="utf-8", errors="surrogateescape") as fh:
            head = fh.read(2048)
    except OSError:
        return False
    return bool(_GENERATED.search(head))


def language_for(path: str) -> Optional[Language]:
    """The language that owns path, or None when no scanner claims the suffix."""
    for lang in LANGUAGES:
        if path.endswith(lang.suffixes):
            return lang
    return None


SUPPORTED = ", ".join(suffix for lang in LANGUAGES for suffix in lang.suffixes)

# Comments the sweep must not touch, because their text is read by something other than a human.
# Rewording any of these is a silent behaviour change, so the filter lives here rather than in a
# prompt, where a model could talk itself past it.
NO_TOUCH = [
    (re.compile(r"CHECKSTYLE:?\s*(ON|OFF)", re.I), "checkstyle suppression"),
    (re.compile(r"@formatter:\s*(on|off)", re.I), "formatter directive"),
    (re.compile(r"spotless:\s*(on|off)", re.I), "spotless directive"),
    (re.compile(r"//\s*noinspection", re.I), "IDE inspection directive"),
    (re.compile(r"\$NON-NLS-"), "externalized-string marker"),
    (re.compile(r"\b(TODO|FIXME|XXX|HACK)\b"), "task marker"),
    (re.compile(r"https?://"), "carries a link"),
    (re.compile(r"(?<![A-Za-z0-9_])#\d+"), "cites an issue"),
    (re.compile(r"DO NOT EDIT|Generated by\b", re.I), "generated-file marker"),
]

# One comment line that a tool reads rather than a human: a controller-gen marker (`// +kubebuilder:`,
# `// +optional`, `// +listType`), the `//go:` family, or a nolint directive. Kept language-agnostic
# because the cost of missing one is that a sweeper edits it.
_MARKER_LINE = re.compile(r"^\s*(?://\s*\+\w|//go:|//\s*nolint)", re.I)


def _all_markers(text: str) -> bool:
    """Whether every line of a comment block is a marker, so no human wrote any of it.

    Deliberately not a substring test. A real doc comment often *ends* in markers — every validated
    field under `api/v1` does — and a block containing `+kubebuilder` anywhere is exactly the kind of
    comment the sweep exists to review. Only a block with no prose at all is off limits.
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return bool(lines) and all(_MARKER_LINE.match(ln) for ln in lines)


# A declaration whose comment is worth more attention, in the order the sweeper should spend it.
_VISIBILITY_RANK = {"public": 0, "protected": 1, "internal": 2, "package": 2, "": 3, "private": 4}
_CLASS_RANK = {"rewritten": 0, "code-only": 1, "new": 2, "undocumented": 3, "unchanged": 4}

# `sb map` wraps every file in a namespace node standing for the package declaration. It is not a
# member and must not appear in a qualified name.
_SKIP_KINDS = {"namespace", "module", "import"}


class Failed(Exception):
    """A command this script depends on did not do what it was asked."""


def git(root: str, *args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", "-C", root, *args], capture_output=True)
    if check and proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="surrogateescape").strip()
        raise Failed(f"git {' '.join(args)}: {stderr}")
    return proc.stdout.decode("utf-8", errors="surrogateescape")


def sb_map(path: str) -> dict:
    """Return the `sb map --json` payload for one file.

    `sb` reports a bad path on stderr with a non-zero exit and nothing on stdout, so an empty result
    is a real answer and never a swallowed error -- provided stderr is not silenced, which is why
    this does not redirect it.
    """
    proc = subprocess.run(["sb", "map", path, "--json", "--compact"], capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise Failed(f"sb map {path}: exit {proc.returncode}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def body_of(src: str, decl: Decl) -> str:
    """Return a declaration's source, sliced by its own line range.

    `sb show` matches a symbol by name, which silently returns the wrong overload -- it handed back the
    no-argument `read()` for a target whose signature was `read(byte[], int, int)`. The line range came
    from the same `sb map` payload as the target, so slicing it is both exact and free.
    """
    lines = src.splitlines()
    return "\n".join(lines[decl.start_line - 1 : decl.end_line])


# ---------------------------------------------------------------- declarations


@dataclass
class Decl:
    qualified_name: str
    name: str
    kind: str
    signature: str
    visibility: str
    start_line: int
    end_line: int
    doc_start_line: int  # equals start_line when there is no doc comment
    docs: str
    depth: int


def _doc_start_line(src: str, decl: dict) -> int:
    offset = decl.get("doc_start_byte")
    if offset is None or not decl.get("docs"):
        return decl["start_line"]
    # doc_start_byte indexes the raw bytes; count newlines in the prefix to reach a line number.
    return src.encode("utf-8", "surrogateescape")[:offset].count(b"\n") + 1


def flatten(payload: dict, src: str) -> list[Decl]:
    files = payload.get("files") or []
    if not files:
        return []
    out: list[Decl] = []

    def walk(nodes: list[dict], prefix: list[str], depth: int) -> None:
        for node in nodes:
            kind = node.get("kind", "")
            children = node.get("children") or []
            if kind in _SKIP_KINDS:
                if kind == "namespace" and node.get("docs"):
                    out.append(
                        Decl(
                            qualified_name=node.get("name") or "<package>",
                            name=node.get("name") or "<package>",
                            kind="package",
                            signature=node.get("signature", ""),
                            visibility=node.get("visibility") or "public",
                            start_line=node["start_line"],
                            end_line=node["end_line"],
                            doc_start_line=_doc_start_line(src, node),
                            docs="\n".join(node.get("docs") or []),
                            depth=depth,
                        )
                    )
                walk(children, prefix, depth)
                continue
            name = node.get("name") or "<anonymous>"
            chain = prefix + [name]
            out.append(
                Decl(
                    qualified_name=".".join(chain),
                    name=name,
                    kind=kind,
                    signature=node.get("signature", ""),
                    visibility=node.get("visibility") or "",
                    start_line=node["start_line"],
                    end_line=node["end_line"],
                    doc_start_line=_doc_start_line(src, node),
                    docs="\n".join(node.get("docs") or []),
                    depth=depth,
                )
            )
            walk(children, chain, depth + 1)

    walk(files[0].get("declarations") or [], [], 0)
    return out


def attach_package_doc(
    decls: list[Decl], spans: list[Span], src: str, path: str, lang: Language
) -> dict | None:
    """Materialize a package declaration and its leading package comment.

    ast-bro 3.x/4.x omits package docs and `flatten` normally discards the namespace node. The
    source position is unambiguous: package documentation is the comment group immediately before
    the package declaration.
    """
    package_line = _package_line(src)
    if package_line == 0:
        return None
    package_match = re.search(r"^\s*package\s+([\w.]+)", src, re.MULTILINE)
    package_name = package_match.group(1) if package_match else "<package>"
    by_end = {span.end_line: span for span in merge_comment_blocks(src, spans)}
    span = by_end.get(package_line - 1)
    if span is None:
        return None
    if lang.name == "java" and os.path.basename(path) != "package-info.java":
        return {
            "line": span.start_line,
            "endLine": span.end_line,
            "reason": "comment before the package declaration in a regular Java file",
        }
    if _all_markers(span.text):
        return {
            "line": span.start_line,
            "endLine": span.end_line,
            "reason": "a marker block, read by a generator",
        }
    reason = _no_touch_reason(span.text)
    if reason:
        return {"line": span.start_line, "endLine": span.end_line, "reason": reason}
    decls.insert(
        0,
        Decl(
            qualified_name=package_name,
            name=package_name,
            kind="package",
            signature=f"package {package_name}",
            visibility="public",
            start_line=package_line,
            end_line=package_line,
            doc_start_line=span.start_line,
            docs=span.text,
            depth=0,
        ),
    )
    return None


# ---------------------------------------------------------------- the diff


def changed_ranges(
    root: str, base: str, path: str
) -> tuple[list[tuple[int, int]], bool, list[tuple[int, int]]]:
    """Changed on-disk ranges, a deletion flag, and changed ranges on the old side.

    The diff is against the working tree rather than HEAD: comments live in the state a reviewer will
    read, and the sweep is meant to run on a clean tree anyway, so the two coincide.
    """
    out = git(root, "diff", "-U0", base, "--", path, check=False)
    ranges: list[tuple[int, int]] = []
    deleted_ranges: list[tuple[int, int]] = []
    deletions = False
    for line in out.splitlines():
        if not line.startswith("@@"):
            continue
        header = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if not header:
            continue
        old_start = int(header.group(1))
        old_count = int(header.group(2) or 1)
        start, count = int(header.group(3)), int(header.group(4) or 1)
        if count == 0:
            # A pure deletion has no line on the new side, but the judge still needs to know a
            # comment may have vanished here. Include both surviving neighbours: Git records the
            # insertion point before the following line, while the declaration that lost its doc
            # comment starts on that following line.
            deletions = True
            ranges.append((max(1, start), max(1, start + 1)))
            deleted_ranges.append((old_start, old_start + old_count - 1))
            continue
        if old_count == 0:
            pass  # pure insertion, nothing deleted
        elif old_count > count:
            deletions = True
            deleted_ranges.append((old_start, old_start + old_count - 1))
        ranges.append((start, start + count - 1))
    return ranges, deletions, deleted_ranges


def overlaps(ranges: list[tuple[int, int]], lo: int, hi: int) -> int:
    return sum(max(0, min(hi, b) - max(lo, a) + 1) for a, b in ranges)


# ---------------------------------------------------------------- targets


@dataclass
class FileReport:
    path: str
    is_test: bool
    is_new: bool
    # The language that claimed this file. The orchestrator batches on it, because a batch has to be
    # one language: the authoring skills disagree about the first sentence, and the comment-only
    # oracle is a different program per language.
    language: str = ""
    has_deletions: bool = False
    degraded: str = ""
    changed_lines: int = 0
    changed_comment_lines: int = 0
    targets: list[dict] = field(default_factory=list)
    commits: list[dict] = field(default_factory=list)
    skipped_comments: list[dict] = field(default_factory=list)

    @property
    def cost(self) -> float:
        code = self.changed_lines - self.changed_comment_lines
        return round(self.changed_comment_lines + 0.3 * code, 1)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="surrogateescape") as handle:
        return handle.read()


def _no_touch_reason(text: str) -> str:
    for pattern, reason in NO_TOUCH:
        if pattern.search(text):
            return reason
    return ""


def _package_line(src: str) -> int:
    for i, line in enumerate(src.splitlines(), 1):
        if line.strip().startswith("package "):
            return i
    return 0


def _suppress_lines(src: str) -> set[int]:
    """Lines adjacent to a @SuppressWarnings, whose comment is the justification for it."""
    hits: set[int] = set()
    for i, line in enumerate(src.splitlines(), 1):
        if "@SuppressWarnings" in line:
            hits.update({i - 1, i, i + 1})
    return hits


def _classify(decl: Decl, base_decl: Decl | None, is_new_file: bool, body_changed: bool) -> str:
    # Undocumented is tested first, and deliberately: without it every member of a new file would come
    # back as "new", which tells the sweeper nothing about whether there is a comment to compare.
    if not decl.docs:
        return "undocumented"
    if is_new_file or base_decl is None:
        return "new"
    if decl.docs != base_decl.docs:
        return "rewritten"
    return "code-only" if body_changed else "unchanged"


def merge_comment_blocks(src: str, spans: list[Span]) -> list[Span]:
    """Fold a run of `//` lines into the one comment a human would edit.

    The lexer is right to report three spans for three slashed lines -- that is what the grammar says
    -- but a target list built from them asks the sweeper to rewrite a paragraph one line at a time.
    Only comments that own their line merge: a trailing `// note` belongs to the statement it sits on.
    """
    lines = src.splitlines()

    def owns_its_line(span: Span) -> bool:
        return lines[span.start_line - 1].lstrip().startswith("//")

    merged: list[Span] = []
    for span in spans:
        prev = merged[-1] if merged else None
        if (
            prev is not None
            and prev.kind == "line"
            and span.kind == "line"
            and span.start_line == prev.end_line + 1
            and owns_its_line(prev)
            and owns_its_line(span)
        ):
            merged[-1] = Span(
                "line", prev.start, span.end, prev.start_line, span.end_line, src[prev.start : span.end]
            )
        else:
            merged.append(span)
    return merged


def _comment_anchor(span: Span, spans: list[Span]) -> int:
    """Position in the comment-free character stream immediately before `span`.

    The comment-only oracle guarantees that this position is stable while the sweeper rewrites,
    grows, or deletes earlier comments. Line numbers and opening words do not have that property.
    """
    removed = sum(previous.end - previous.start for previous in spans if previous.end <= span.start)
    return span.start - removed


def _comments_by_anchor(src: str, lang: Language) -> dict[int, Span]:
    spans = merge_comment_blocks(src, lang.scan(src))
    return {_comment_anchor(span, spans): span for span in spans}


def _decl_key(decl: Decl) -> str:
    return f"{decl.qualified_name}|{decl.signature}"


def _strip_java_annotations(text: str) -> str:
    """Remove annotations, including balanced argument lists, from a parameter declaration."""
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] != "@":
            out.append(text[i])
            i += 1
            continue
        i += 1
        while i < len(text) and (text[i].isalnum() or text[i] in "_.$"):
            i += 1
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "(":
            continue
        depth = 0
        quote = ""
        escaped = False
        while i < len(text):
            char = text[i]
            i += 1
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""
                continue
            if char in "\"'":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
    return "".join(out)


def _split_parameters(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depths = {"<": 0, "(": 0, "[": 0, "{": 0}
    pairs = {">": "<", ")": "(", "]": "[", "}": "{"}
    for index, char in enumerate(text):
        if char in depths:
            depths[char] += 1
        elif char in pairs:
            opener = pairs[char]
            depths[opener] = max(0, depths[opener] - 1)
        elif char == "," and not any(depths.values()):
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return [part for part in parts if part.strip()]


def _java_parameter_type(parameter: str) -> str:
    cleaned = _strip_java_annotations(parameter)
    cleaned = re.sub(r"\bfinal\b", " ", cleaned)
    match = re.search(r"\b[A-Za-z_$][\w$]*\s*((?:\[\s*\]\s*)*)$", cleaned)
    if match:
        cleaned = cleaned[: match.start()] + match.group(1)
    return re.sub(r"\s+", "", cleaned)


def _callable_key(decl: Decl) -> str | None:
    """Java overload identity that ignores parameter names but preserves parameter types."""
    if decl.kind not in {"method", "constructor"}:
        return None
    matches = list(re.finditer(rf"\b{re.escape(decl.name)}\s*\(", decl.signature))
    if not matches:
        return None
    open_paren = decl.signature.find("(", matches[-1].start())
    depth = 0
    close_paren = -1
    for index in range(open_paren, len(decl.signature)):
        if decl.signature[index] == "(":
            depth += 1
        elif decl.signature[index] == ")":
            depth -= 1
            if depth == 0:
                close_paren = index
                break
    if close_paren < 0:
        return None
    parameters = _split_parameters(decl.signature[open_paren + 1 : close_paren])
    types = ",".join(_java_parameter_type(parameter) for parameter in parameters)
    return f"{decl.qualified_name}|params:{types}"


def _decl_index(decls: list[Decl]) -> dict[str, Decl]:
    """Index exact declarations and unambiguous name-insensitive callable signatures."""
    result = {_decl_key(decl): decl for decl in decls}
    by_name: dict[str, list[Decl]] = {}
    by_callable: dict[str, list[Decl]] = {}
    for decl in decls:
        by_name.setdefault(decl.qualified_name, []).append(decl)
        callable_key = _callable_key(decl)
        if callable_key:
            by_callable.setdefault(callable_key, []).append(decl)
    for key, matches in by_callable.items():
        if len(matches) == 1:
            result[key] = matches[0]
    for name, matches in by_name.items():
        if len(matches) == 1:
            result[name] = matches[0]
    return result


def attach_positional_docs(decls: list[Decl], spans: list[Span], src: str) -> None:
    """Fill in the doc comments the mapper did not report, from the source itself.

    `sb map` reports no `docs` for a Go struct field (aeroxy/ast-bro#47), so a documented field
    arrives looking undocumented. In a Kubernetes API package that is not an edge case: every CRD
    field description is a struct field comment, so the whole package classifies as `undocumented`
    and the sweeper is invited to write comments that already exist.

    The comment is in the source, ending on the line before the declaration — the rule
    `Language.docs_by_position` already relies on. Marker lines stay in the text: they are part of
    the same comment group, and the sweeper has to see them to know they must not be detached.

    Applies to both sides of a comparison or neither, or a fixed current version measured against an
    unfixed base makes every declaration look rewritten.
    """
    by_end = {span.end_line: span for span in merge_comment_blocks(src, spans)}
    for decl in decls:
        if decl.docs:
            continue
        span = by_end.get(decl.start_line - 1)
        if span is None:
            continue
        if _all_markers(span.text):
            continue
        decl.docs = span.text
        decl.doc_start_line = span.start_line


def build_file_report(
    root: str,
    base: str,
    path: str,
    base_exists: bool,
    commits: list[dict],
    lang: Language,
    whole_file: bool = False,
) -> FileReport:
    abs_path = os.path.join(root, path)
    report = FileReport(
        path=path,
        is_test=lang.is_test(path),
        is_new=not base_exists,
        language=lang.name,
    )

    src = _read(abs_path)

    if whole_file:
        # Path-scoped survey: there is no diff to intersect, so the changed range is the file. Every
        # declaration and every inline comment then falls out of the same arithmetic the diff-scoped
        # run uses, which is the point — one definition of a target, two ways of choosing the lines.
        line_count = len(src.splitlines())
        ranges: list[tuple[int, int]] = [(1, line_count)] if line_count else []
        report.has_deletions = False
    else:
        ranges, report.has_deletions, deleted_ranges = changed_ranges(root, base, path)
    if whole_file:
        deleted_ranges: list[tuple[int, int]] = []
    if not ranges:
        return report
    report.changed_lines = sum(b - a + 1 for a, b in ranges)
    try:
        spans = lang.scan(src)
    except (ParseError, Unverifiable) as exc:
        report.degraded = str(exc)
        return report

    comment_lines = {ln for s in spans for ln in range(s.start_line, s.end_line + 1)}
    report.changed_comment_lines = sum(
        1 for a, b in ranges for ln in range(a, b + 1) if ln in comment_lines
    )

    try:
        decls = flatten(sb_map(abs_path), src)
        package_skip = attach_package_doc(decls, spans, src, path, lang)
        if lang.docs_by_position:
            attach_positional_docs(decls, spans, src)
    except Failed as exc:
        report.degraded = str(exc)
        return report

    base_by_name: dict[str, Decl] = {}
    base_src = ""
    base_spans: list[Span] = []
    base_decls: list[Decl] = []
    if base_exists:
        try:
            base_src = git(root, "show", f"{base}:{path}")
            with tempfile.TemporaryDirectory() as tmp:
                mirror = os.path.join(tmp, os.path.basename(path))
                Path(mirror).write_text(base_src, encoding="utf-8", errors="surrogateescape")
                base_decls = flatten(sb_map(mirror), base_src)
                base_spans = lang.scan(base_src)
                attach_package_doc(base_decls, base_spans, base_src, path, lang)
                if lang.docs_by_position:
                    attach_positional_docs(base_decls, base_spans, base_src)
                base_by_name = _decl_index(base_decls)
        except (Failed, ParseError, Unverifiable):
            base_by_name = {}

    # --- doc targets -------------------------------------------------------------------------
    overload_counts: dict[str, int] = {}
    for decl in decls:
        overload_index = overload_counts.get(decl.qualified_name, 0)
        overload_counts[decl.qualified_name] = overload_index + 1
        lo = min(decl.doc_start_line, decl.start_line)
        touched = overlaps(ranges, lo, decl.end_line)
        if not touched:
            continue
        base_decl = (
            base_by_name.get(_decl_key(decl))
            or base_by_name.get(_callable_key(decl) or "")
            or base_by_name.get(decl.qualified_name)
        )
        # Under whole_file every range overlaps, so the diff-derived question "did the body change"
        # has no answer and must not be asked: left to the overlap test it would answer yes for every
        # declaration in the file and class every documented one as `code-only`, inventing a staleness
        # signal out of the mode itself.
        body_changed = False if whole_file else overlaps(ranges, decl.start_line, decl.end_line) > 0
        target_class = _classify(decl, base_decl, report.is_new, body_changed)
        if target_class == "unchanged" and not whole_file:
            # Diff-scoped: the branch touched neither this comment nor this body, so there is nothing
            # for §7b to compare and no reason to spend a sweeper on it. Path-scoped is the opposite
            # case — "unchanged" is what the caller asked to look at, and it is where a comment that
            # has quietly stopped matching its code has been sitting undisturbed.
            continue
        report.targets.append(
            {
                "id": f"{path}#{_decl_key(decl)}",
                "kind": "doc",
                "declKind": decl.kind,
                "qualifiedName": decl.qualified_name,
                "signature": decl.signature,
                "overloadIndex": overload_index,
                "callableKey": _callable_key(decl),
                "visibility": decl.visibility,
                # A container is a type whose own comment may be untouched; the branch changed
                # something inside it. Say so, or the sweeper rewrites class comments for nothing.
                "container": bool(decl.kind in {"class", "interface", "enum", "record", "annotation"}),
                "class": target_class,
                "hasDoc": bool(decl.docs),
                "docStartLine": decl.doc_start_line,
                "startLine": decl.start_line,
                "endLine": decl.end_line,
                "changedLines": touched,
            }
        )

    # --- inline targets ----------------------------------------------------------------------
    header_end = _package_line(src)
    suppress = _suppress_lines(src)
    doc_lines = {ln for s in spans if s.kind == "doc" for ln in range(s.start_line, s.end_line + 1)}
    if package_skip:
        report.skipped_comments.append(
            {"line": package_skip["line"], "reason": package_skip["reason"]}
        )
        doc_lines.update(range(package_skip["line"], package_skip["endLine"] + 1))

    merged = merge_comment_blocks(src, spans)
    current_anchors = {_comment_anchor(span, merged): span for span in merged}
    if lang.docs_by_position:
        # A Go doc comment is an ordinary comment group that happens to end on the line before a
        # declaration. Claim those lines here so the inline pass below skips them; the declaration
        # pass has already collected the same comment as that declaration's doc target.
        decl_starts = {d.start_line for d in decls}
        src_lines = src.splitlines()
        for span in merged:
            following = span.end_line  # 0-based index of the line after the span
            if span.end_line + 1 in decl_starts or (
                # `sb map` reports the members of a grouped declaration but not the group, so the
                # comment above `const (` matches no declaration line. Anchoring the pattern at
                # column 0 keeps a function-local `var (` out: that one really is an inline comment.
                following < len(src_lines) and _GROUP_DECL.match(src_lines[following])
            ):
                doc_lines.update(range(span.start_line, span.end_line + 1))

    for span in merged:
        if span.kind == "doc":
            continue
        if not overlaps(ranges, span.start_line, span.end_line):
            continue
        if span.start_line in doc_lines:
            continue
        if span.start_line <= header_end:
            report.skipped_comments.append(
                {"line": span.start_line, "reason": "license header before the package declaration"}
            )
            continue
        if span.start_line in suppress:
            report.skipped_comments.append(
                {"line": span.start_line, "reason": "justifies a @SuppressWarnings"}
            )
            continue
        if _all_markers(span.text):
            report.skipped_comments.append(
                {"line": span.start_line, "reason": "a marker block, read by a generator"}
            )
            continue
        reason = _no_touch_reason(span.text)
        if reason:
            report.skipped_comments.append({"line": span.start_line, "reason": reason})
            continue

        enclosing = _innermost(decls, span.start_line)
        report.targets.append(
            {
                "id": f'{path}#{enclosing}@{_comment_anchor(span, merged)}:"{_head_words(span)}"',
                "kind": "inline",
                "enclosing": enclosing,
                "commentKind": span.kind,
                "startLine": span.start_line,
                "endLine": span.end_line,
                "text": span.text,
                "codeAnchor": _comment_anchor(span, merged),
            }
        )

    # A deleted inline comment has no current span to discover. Reconstruct only comments that
    # overlap an old-side deletion hunk and whose stable code anchor disappeared from the current
    # file. Doc comments are handled by the declaration pass above.
    if deleted_ranges and base_src and base_spans:
        base_merged = merge_comment_blocks(base_src, base_spans)
        base_doc_lines = {
            line
            for span in base_merged
            if span.kind == "doc"
            for line in range(span.start_line, span.end_line + 1)
        }
        if lang.docs_by_position:
            base_starts = {decl.start_line for decl in base_decls}
            base_lines = base_src.splitlines()
            for span in base_merged:
                following = span.end_line
                if span.end_line + 1 in base_starts or (
                    following < len(base_lines) and _GROUP_DECL.match(base_lines[following])
                ):
                    base_doc_lines.update(range(span.start_line, span.end_line + 1))

        for span in base_merged:
            anchor = _comment_anchor(span, base_merged)
            if span.kind == "doc" or span.start_line in base_doc_lines:
                continue
            if not overlaps(deleted_ranges, span.start_line, span.end_line):
                continue
            if anchor in current_anchors or _all_markers(span.text) or _no_touch_reason(span.text):
                continue
            enclosing = _innermost(base_decls, span.start_line)
            report.targets.append(
                {
                    "id": f'{path}#{enclosing}@{anchor}:"{_head_words(span)}"',
                    "kind": "inline",
                    "enclosing": enclosing,
                    "commentKind": span.kind,
                    "startLine": span.start_line,
                    "endLine": span.end_line,
                    "text": span.text,
                    "codeAnchor": anchor,
                    "deleted": True,
                }
            )

    report.targets.sort(key=_rank)
    report.commits = commits
    return report


def _head_words(span: Span, count: int = 6) -> str:
    body = re.sub(r"^\s*(//+|/\*+)|\*+/\s*$", " ", span.text)
    body = re.sub(r"^\s*\*", " ", body, flags=re.M)
    words = body.split()
    return " ".join(words[:count])


def _innermost(decls: list[Decl], line: int) -> str:
    best: Decl | None = None
    for decl in decls:
        if decl.start_line <= line <= decl.end_line and (best is None or decl.depth > best.depth):
            best = decl
    return best.qualified_name if best else "<file>"


def _rank(target: dict) -> tuple:
    if target["kind"] == "inline":
        # An inline comment carries no visibility, and its worst failure -- surviving a change to the
        # code under it -- is not visible from the metadata. Sort it after the doc targets of the
        # same file rather than inventing a rank for it.
        return (5, 5, 0)
    return (
        _VISIBILITY_RANK.get(target["visibility"], 3),
        _CLASS_RANK.get(target["class"], 4),
        -target["changedLines"],
    )


# ---------------------------------------------------------------- commands


def _source_files(
    root: str, base: str, only: list[str] | None
) -> tuple[list[tuple[str, bool, Language]], list[dict]]:
    """Return (path, existed-at-base, language) for each candidate, plus the files deliberately left out."""
    raw = git(root, "diff", "--name-status", "-M", "-C", base, "--")
    excluded: list[dict] = []
    picked: list[tuple[str, bool, Language]] = []
    for line in raw.splitlines():
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if status.startswith("D"):
            continue
        lang = language_for(path)
        if lang is None:
            excluded.append(
                {"path": path, "reason": f"no scanner for this suffix ({SUPPORTED}); english-developer-style owns this text"}
            )
            continue
        if only and path not in only:
            continue
        if _is_generated(root, path):
            excluded.append({"path": path, "reason": "generated; the next regeneration overwrites it"})
            continue
        picked.append((path, not status.startswith("A"), lang))
    return picked, excluded


def _files_under(
    root: str, base: str, pathspecs: list[str]
) -> tuple[list[tuple[str, bool, Language]], list[dict]]:
    """The same tuple as _source_files, for every tracked file matching `pathspecs`.

    This is the path-scoped survey: the caller has named a subtree and asked for its comments to be
    reviewed whether or not the branch touched them. It exists because a diff-scoped sweep can never
    reach a comment nobody has edited, and a comment nobody has edited is exactly where a stale one
    survives.

    The volume ceiling that the diff provided is gone, so the pathspec is the only thing bounding the
    run and it is required. `cmd_survey` reports the count it selected for the same reason.
    """
    listed = git(root, "ls-files", "--", *pathspecs).splitlines()
    at_base = set(git(root, "ls-tree", "-r", "--name-only", base).splitlines())

    excluded: list[dict] = []
    picked: list[tuple[str, bool, Language]] = []
    for path in listed:
        lang = language_for(path)
        if lang is None:
            excluded.append(
                {"path": path, "reason": f"no scanner for this suffix ({SUPPORTED}); english-developer-style owns this text"}
            )
            continue
        if _is_generated(root, path):
            excluded.append({"path": path, "reason": "generated; the next regeneration overwrites it"})
            continue
        picked.append((path, path in at_base, lang))
    return picked, excluded


def _content_hash(root: str, path: str) -> str | None:
    """sha1 of a file as it stands on disk, or None when it is not there."""
    try:
        return hashlib.sha1(Path(os.path.join(root, path)).read_bytes()).hexdigest()
    except OSError:
        return None


def _read_ledger(path: str | None) -> dict[str, dict]:
    if not path:
        return {}
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    entries = payload.get("entries")
    return entries if isinstance(entries, dict) else {}


def cmd_survey(args: argparse.Namespace) -> int:
    root = os.path.abspath(args.root)
    base = git(root, "merge-base", "HEAD", args.base).strip()
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()

    paths = getattr(args, "paths", None)
    mode = "path" if paths else "diff"
    if paths and args.files:
        raise Failed("--files restricts the branch diff and --paths replaces it; pass one, not both")
    if paths:
        files, excluded = _files_under(root, base, paths)
    else:
        files, excluded = _source_files(root, base, args.files)
    selected = len(files)

    # A file the ledger has seen at exactly these bytes is finished. Skipping it here rather than in the
    # workflow keeps one definition of "already swept", and keeps it out of the token budget entirely.
    ledger = _read_ledger(args.ledger)
    resumed: list[dict] = []
    if ledger:
        keep: list[tuple[str, bool, Language]] = []
        for path, base_exists, lang in files:
            entry = ledger.get(path)
            if (
                entry
                and entry.get("sha1") == _content_hash(root, path)
                and entry.get("mode") == mode
                and entry.get("base") == base
            ):
                resumed.append({"path": path, "wave": entry.get("wave")})
            else:
                keep.append((path, base_exists, lang))
        files = keep

    reports: list[FileReport] = []
    for path, base_exists, lang in files:
        log = git(root, "log", "--format=%H %s", f"{base}..HEAD", "--", path).splitlines()
        commits = [{"sha": ln.split(" ", 1)[0], "subject": ln.split(" ", 1)[1]} for ln in log if " " in ln]
        reports.append(
            build_file_report(root, base, path, base_exists, commits, lang, whole_file=bool(paths))
        )

    payload = {
        "base": base,
        "branch": branch,
        "root": root,
        # The mode is in the payload because it changes what the numbers below mean: under "path" a
        # target is a comment somebody asked to have read, not one the branch changed, and every
        # ledger, report and commit message downstream should say which of the two it was.
        "mode": mode,
        "pathspecs": paths or [],
        "selectedFiles": selected,
        "files": [
            {
                "path": r.path,
                "language": r.language,
                "isTest": r.is_test,
                "isNew": r.is_new,
                "hasDeletions": r.has_deletions,
                "degraded": r.degraded,
                "changedLines": r.changed_lines,
                "changedCommentLines": r.changed_comment_lines,
                "cost": r.cost,
                "commits": r.commits,
                "targets": r.targets,
                "skippedComments": r.skipped_comments,
            }
            for r in reports
        ],
        "excluded": excluded,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = {
        "ok": True,
        "base": base,
        "branch": branch,
        "mode": mode,
        "pathspecs": paths or [],
        # Under --paths nothing else bounds the run, so the agent reading this summary is the last
        # place a surprising number can be noticed before a fan-out spends on it.
        "selectedFiles": selected,
        "targetsFile": os.path.abspath(args.out),
        "files": [
            {
                "path": r.path,
                "language": r.language,
                "cost": r.cost,
                "targets": len(r.targets),
                "docTargets": sum(1 for t in r.targets if t["kind"] == "doc"),
                "inlineTargets": sum(1 for t in r.targets if t["kind"] == "inline"),
                "rewritten": sum(1 for t in r.targets if t.get("class") == "rewritten"),
                "undocumented": sum(1 for t in r.targets if t.get("class") == "undocumented"),
                "degraded": bool(r.degraded),
            }
            for r in reports
            if r.targets or r.degraded
        ],
        "excluded": [f"{e['path']} — {e['reason']}" for e in excluded],
        "resumed": resumed,
    }
    json.dump(summary, sys.stdout, indent=2)
    print()
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    """Mark files finished, so the next survey skips them while their bytes stay put."""
    root = os.path.abspath(args.root)
    path = Path(args.ledger)
    payload: dict = {"version": 1, "entries": {}}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(existing.get("entries"), dict):
                payload = existing
        except (OSError, json.JSONDecodeError):
            pass

    written, missing = [], []
    base = git(root, "merge-base", "HEAD", args.base).strip()
    for rel in args.files:
        sha1 = _content_hash(root, rel)
        if sha1 is None:
            missing.append(rel)
            continue
        payload["entries"][rel] = {
            "sha1": sha1,
            "wave": args.wave,
            "outcome": args.outcome,
            "mode": args.mode,
            "base": base,
        }
        written.append(rel)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    json.dump(
        {"ledger": str(path), "recorded": len(written), "missing": missing, "total": len(payload["entries"])},
        sys.stdout,
        indent=2,
    )
    print()
    return 0


def decls_of(src: str, mapped: dict, path: str) -> list[Decl]:
    """The file's declarations, with the doc comments the mapper does not report filled in.

    Every path that compares two revisions has to go through this rather than through `flatten`
    directly. `attach_positional_docs` says it applies to both sides of a comparison or neither, and
    the way to get that wrong is to call it in one command and not the next: the survey then reports
    a documented Go struct field while `pairs` hands the judge an empty before and after, so a
    rewritten CRD description reads as untouched.
    """
    decls = flatten(mapped, src)
    lang = language_for(path)
    if lang:
        try:
            spans = lang.scan(src)
            attach_package_doc(decls, spans, src, path, lang)
        except (ParseError, Unverifiable):
            spans = []
    if lang and lang.docs_by_position:
        try:
            attach_positional_docs(decls, spans, src)
        except (ParseError, Unverifiable):
            pass  # an unlexable revision keeps whatever the mapper reported
    return decls


def _decls_at(root: str, ref: str, path: str) -> tuple[dict[str, Decl], str]:
    """Load a file's declarations as of a git ref. Returns ({} , '') when the file did not exist then."""
    try:
        src = git(root, "show", f"{ref}:{path}")
    except Failed:
        return {}, ""
    with tempfile.TemporaryDirectory() as tmp:
        mirror = os.path.join(tmp, os.path.basename(path))
        Path(mirror).write_text(src, encoding="utf-8", errors="surrogateescape")
        try:
            return _decl_index(decls_of(src, sb_map(mirror), path)), src
        except Failed:
            return {}, src


def cmd_pairs(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    root, base = payload["root"], payload["base"]
    entry = next((f for f in payload["files"] if f["path"] == args.file), None)
    if entry is None:
        print(json.dumps({"file": args.file, "error": "not in the target list"}), file=sys.stderr)
        return 2

    abs_path = os.path.join(root, args.file)
    src = _read(abs_path)
    after_decls = _decl_index(decls_of(src, sb_map(abs_path), args.file))

    before_decls = {} if entry["isNew"] else _decls_at(root, base, args.file)[0]
    # Two baselines, because they answer different questions. `before` is the merge base, which is what
    # the net-delta rule needs: it measures the branch's comments as a reviewer will meet them. `preSweep`
    # is the tree the sweeper started from, which is the only way to tell a fact the branch author dropped
    # from one the sweeper just dropped. With one baseline the sweeper's own regressions hide inside the
    # branch's, which is exactly what a judge is there to separate.
    pre_decls, pre_src = _decls_at(root, args.pre_sweep_ref, args.file)
    lang = language_for(args.file)
    after_comments = _comments_by_anchor(src, lang) if lang else {}
    pre_comments = _comments_by_anchor(pre_src, lang) if lang and pre_src else {}

    out = []
    for target in entry["targets"]:
        if target["kind"] == "inline":
            anchor = target.get("codeAnchor")
            pre_span = pre_comments.get(anchor)
            after_span = after_comments.get(anchor)
            pre_text = pre_span.text if pre_span else None
            after_text = after_span.text if after_span else None
            before_text = target["text"] if target.get("deleted") else None
            out.append(
                {
                    **target,
                    "before": before_text,
                    "preSweep": pre_text,
                    "after": after_text,
                    "beforeChars": len(before_text) if before_text else 0,
                    "preSweepChars": len(pre_text) if pre_text else 0,
                    "afterChars": len(after_text) if after_text else 0,
                    "addedBySweep": pre_text is None and after_text is not None,
                    "touchedBySweep": pre_text != after_text,
                    "note": "inline comments are judged under §7b step 6; deleted targets also carry base text",
                }
            )
            continue

        qname = target["qualifiedName"]
        key = f"{qname}|{target.get('signature', '')}"
        callable_key = target.get("callableKey") or ""
        before = before_decls.get(key) or before_decls.get(callable_key) or before_decls.get(qname)
        pre = pre_decls.get(key) or pre_decls.get(callable_key) or pre_decls.get(qname)
        after = after_decls.get(key) or after_decls.get(callable_key) or after_decls.get(qname)
        record = {
            **target,
            "before": before.docs if before else None,
            "preSweep": pre.docs if pre else None,
            "after": after.docs if after else None,
            "beforeChars": len(before.docs) if before else 0,
            "preSweepChars": len(pre.docs) if pre else 0,
            "afterChars": len(after.docs) if after else 0,
            "touchedBySweep": bool(pre and after and pre.docs != after.docs),
        }
        if args.with_body and after:
            record["body"] = body_of(src, after)
        out.append(record)

    json.dump(
        {
            "file": args.file,
            "base": base,
            "preSweepRef": args.pre_sweep_ref,
            "isNew": entry["isNew"],
            "hasDeletions": entry["hasDeletions"],
            "commits": entry["commits"],
            "skippedComments": entry["skippedComments"],
            "targets": out,
        },
        sys.stdout,
        indent=2,
    )
    print()
    return 0


def cmd_touched(args: argparse.Namespace) -> int:
    root = os.path.abspath(args.root)
    ranges, _, _ = changed_ranges(root, args.ref, args.file)
    lines = sorted({ln for a, b in ranges for ln in range(a, b + 1)})
    json.dump({"file": args.file, "ref": args.ref, "lines": lines}, sys.stdout)
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("survey", help="build the target list for the branch")
    p.add_argument("--root", required=True)
    p.add_argument("--base", default="main", help="branch to take the merge base against")
    p.add_argument("--files", nargs="*", help="restrict the survey to these paths")
    p.add_argument(
        "--paths",
        nargs="+",
        metavar="PATHSPEC",
        help="survey every tracked file under these pathspecs instead of the branch diff, and take "
        "every comment in them as a target. The pathspec is the only bound on the run, so name a "
        "subtree you are prepared to review: 'api/v1', not '.'",
    )
    p.add_argument("--out", required=True, help="where to write targets.json")
    p.add_argument(
        "--ledger",
        help="skip files this ledger records as finished and still byte-identical (see `ledger`)",
    )
    p.set_defaults(func=cmd_survey)

    p = sub.add_parser("ledger", help="record files as finished for a later resume")
    p.add_argument("--root", required=True)
    p.add_argument("--ledger", required=True, help="path to ledger.json; created when absent")
    p.add_argument("--mode", choices=["diff", "path"], required=True, help="survey mode being recorded")
    p.add_argument("--base", required=True, help="survey base ref being recorded")
    p.add_argument("--files", nargs="+", required=True, help="repository-relative paths")
    p.add_argument("--wave", type=int, default=0, help="which wave finished them, for the report")
    p.add_argument("--outcome", default="approved", choices=["approved", "unchanged"])
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("pairs", help="before/after material for one file")
    p.add_argument("--targets", required=True, help="path to targets.json")
    p.add_argument("--file", required=True)
    p.add_argument(
        "--pre-sweep-ref",
        default="HEAD",
        help="the tree the sweep started from; separates the sweeper's edits from the branch author's",
    )
    p.add_argument("--with-body", action="store_true", help="include each member's source")
    p.set_defaults(func=cmd_pairs)

    p = sub.add_parser("touched", help="lines that differ between a ref and the working tree")
    p.add_argument("--root", required=True)
    p.add_argument("--ref", required=True)
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_touched)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Failed as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
