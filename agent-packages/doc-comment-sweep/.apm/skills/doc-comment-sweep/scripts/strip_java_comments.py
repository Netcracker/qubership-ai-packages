#!/usr/bin/env python3
"""Prove that an edit changed comments and nothing else.

The sweep lets a model rewrite comments in place, so the one thing that must not rest on the model's
word is whether it also touched code. This script answers that from the source text: it lexes Java
well enough to know a comment from a slash inside a string literal, removes the comments, and compares
what is left.

Three subcommands:

  strip     print the normalized form of one file, for eyeballing what the comparison actually sees
  classify  report every comment span and the per-line comment map, for the target inventory
  verify    compare each file against a git ref and exit non-zero when code moved

The comparison ignores indentation and horizontal spacing but not the distribution of code across
lines. Deleting a comment -- whole-line, trailing, or one that spanned lines mid-expression -- leaves
the normalized form untouched, which it must, because deleting is a legitimate edit. Rewrapping a
statement over two lines does not, which it also must.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from bisect import bisect_right
from dataclasses import dataclass
from typing import Callable

# Java resolves unicode escapes before it lexes, so // opens a comment and " opens a
# string. A lexer working on the raw text cannot see either. Rather than half-implement the rule and
# hand back a confident wrong answer, refuse the file: a false "the code is untouched" is worse than
# no answer at all. Matches an even-length backslash run followed by u+ and the hex for " ' * / \.
_PRE_LEX_ESCAPE = re.compile(r"(?<!\\)(?:\\\\)*\\u+00(?:22|27|2[aAfF]|5[cC])")

_WS_RUN = re.compile(r"[ \t\f\r]+")


class ParseError(Exception):
    """The file is not lexable Java: an unterminated literal or comment."""


class Unverifiable(Exception):
    """The file uses a construct this lexer refuses to reason about."""


@dataclass(frozen=True)
class Span:
    kind: str  # 'line' | 'block' | 'doc'
    start: int  # byte-agnostic character offsets into the source
    end: int
    start_line: int
    end_line: int
    text: str


def _line_starts(src: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(src):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _line_of(starts: list[int], offset: int) -> int:
    return bisect_right(starts, offset)


def _opens_text_block(src: str, i: int) -> bool:
    """A text block opener is three quotes, then optional spaces, then a line terminator (JLS 3.10.6).

    Without this test, four consecutive quotes lex as a text block that runs to the end of the file,
    when they are in fact two empty strings.
    """
    if not src.startswith('"""', i):
        return False
    j = i + 3
    while j < len(src) and src[j] in " \t\f":
        j += 1
    return j < len(src) and src[j] in "\r\n"


def scan(src: str) -> list[Span]:
    """Return every comment span in source order.

    Raises ParseError on an unterminated literal or block comment, and Unverifiable on a pre-lex
    unicode escape.
    """
    if _PRE_LEX_ESCAPE.search(src):
        raise Unverifiable(
            "the file contains a unicode escape that could encode a quote, a slash, or a backslash; "
            "Java resolves those before lexing, so this lexer cannot see the real token stream"
        )

    starts = _line_starts(src)
    spans: list[Span] = []
    i, n = 0, len(src)

    while i < n:
        ch = src[i]

        if ch == "/" and i + 1 < n:
            nxt = src[i + 1]
            if nxt == "/":
                end = src.find("\n", i)
                if end == -1:
                    end = n  # a trailing comment with no final newline is still a comment
                spans.append(Span("line", i, end, _line_of(starts, i), _line_of(starts, end - 1), src[i:end]))
                i = end
                continue
            if nxt == "*":
                # Block comments do not nest: the first */ closes, however many /* precede it.
                end = src.find("*/", i + 2)
                if end == -1:
                    raise ParseError(f"unterminated block comment at line {_line_of(starts, i)}")
                end += 2
                # /**/ is an empty block comment, not a doc comment with an empty body.
                kind = "doc" if src.startswith("/**", i) and not src.startswith("/**/", i) else "block"
                spans.append(Span(kind, i, end, _line_of(starts, i), _line_of(starts, end - 1), src[i:end]))
                i = end
                continue

        if _opens_text_block(src, i):
            j = i + 3
            while True:
                if j >= n:
                    raise ParseError(f"unterminated text block opened at line {_line_of(starts, i)}")
                if src[j] == "\\":
                    j += 2
                    continue
                if src.startswith('"""', j):
                    j += 3
                    break
                j += 1
            i = j
            continue

        if ch in "\"'":
            j = i + 1
            while True:
                if j >= n:
                    raise ParseError(f"unterminated literal at line {_line_of(starts, i)}")
                d = src[j]
                if d == "\\":
                    # One rule covers \\ \" \' \n and \uXXXX alike.
                    j += 2
                    continue
                if d == "\n":
                    raise ParseError(f"newline inside a literal at line {_line_of(starts, i)}")
                if d == ch:
                    j += 1
                    break
                j += 1
            i = j
            continue

        i += 1

    return spans


@dataclass(frozen=True)
class Normalized:
    lines: list[str]  # comment-free code lines, whitespace-collapsed, blanks dropped
    source_lines: list[int]  # source line each entry came from, same length as `lines`


def normalize(src: str, scanner: Callable[[str], list[Span]] = scan) -> Normalized:
    """Strip comments and reduce what is left to the form the comparison uses.

    A comment becomes a single space, never a newline. That is the whole reason deleting a multi-line
    comment does not register as a code change: with the comment replaced by a space, the code around
    it already sits on one line, exactly as it does once the comment is gone.

    Everything past the comment spans is language-independent, so `scanner` lets another language
    reuse this function with its own lexer. It has to stay one function across languages: two copies
    would let two sweeps be held to two different definitions of "the code moved".
    """
    spans = scanner(src)
    out: list[str] = []
    src_idx: list[int] = []

    cursor = 0
    for span in spans:
        for k in range(cursor, span.start):
            out.append(src[k])
            src_idx.append(k)
        out.append(" ")
        src_idx.append(span.start)
        cursor = span.end
    for k in range(cursor, len(src)):
        out.append(src[k])
        src_idx.append(k)

    starts = _line_starts(src)
    lines: list[str] = []
    source_lines: list[int] = []

    begin = 0
    for pos in range(len(out) + 1):
        if pos == len(out) or out[pos] == "\n":
            raw = "".join(out[begin:pos])
            collapsed = _WS_RUN.sub(" ", raw).strip()
            if collapsed:
                offset = begin
                while offset < pos and out[offset] in " \t\f\r":
                    offset += 1
                lines.append(collapsed)
                source_lines.append(_line_of(starts, src_idx[offset]))
            begin = pos + 1

    return Normalized(lines, source_lines)


@dataclass(frozen=True)
class Diff:
    line: int  # source line in the after-version
    before: str
    after: str


def first_difference(
    before: str, after: str, scanner: Callable[[str], list[Span]] = scan
) -> Diff | None:
    a, b = normalize(before, scanner), normalize(after, scanner)
    for i in range(max(len(a.lines), len(b.lines))):
        old = a.lines[i] if i < len(a.lines) else "<end of file>"
        new = b.lines[i] if i < len(b.lines) else "<end of file>"
        if old != new:
            return Diff(b.source_lines[i] if i < len(b.source_lines) else 0, old, new)
    return None


def resolve_under_root(root: str, path: str) -> str:
    """The repository-relative form of `path`, for a caller that may have passed an absolute one.

    `git show <ref>:<path>` only understands a repository-relative path, so an absolute one used to
    come back as FileNotFoundError and be reported as "new" — indistinguishable from a file the
    branch genuinely adds. A gate agent that mixes the two forms then gets contradictory verdicts for
    the same file, which is how one real run stalled.

    Raises ValueError when the path is not under root at all; the caller reports that rather than
    guessing.
    """
    if not os.path.isabs(path):
        return path
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    if rel.startswith(os.pardir + os.sep) or rel == os.pardir:
        raise ValueError(f"{path} is not under {root}")
    return rel


def _git_show(root: str, ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", root, "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise FileNotFoundError(f"{path} does not exist at {ref}")
    return proc.stdout


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="surrogateescape") as handle:
        return handle.read()


def cmd_strip(args: argparse.Namespace) -> int:
    print("\n".join(normalize(_read(args.file)).lines))
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    src = _read(args.file)
    try:
        spans = scan(src)
    except Unverifiable as exc:
        json.dump({"file": args.file, "status": "unverifiable", "reason": str(exc)}, sys.stdout, indent=2)
        print()
        return 3
    except ParseError as exc:
        json.dump({"file": args.file, "status": "unparseable", "reason": str(exc)}, sys.stdout, indent=2)
        print()
        return 2

    comment_lines: dict[int, str] = {}
    for span in spans:
        for line in range(span.start_line, span.end_line + 1):
            # A line holding both code and a comment counts as a comment line for cost purposes; the
            # span list is what the inventory uses when it needs the exact extent.
            comment_lines[line] = span.kind

    payload = {
        "file": args.file,
        "status": "ok",
        "lineCount": src.count("\n") + (0 if src.endswith("\n") else 1),
        "commentLines": {str(k): v for k, v in sorted(comment_lines.items())},
        "spans": [
            {
                "kind": s.kind,
                "startLine": s.start_line,
                "endLine": s.end_line,
                "startOffset": s.start,
                "endOffset": s.end,
                "text": s.text,
            }
            for s in spans
        ],
    }
    json.dump(payload, sys.stdout, indent=2)
    print()
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    results = []
    worst = 0
    for path in args.files:
        entry: dict[str, object] = {"file": path}
        try:
            rel = resolve_under_root(args.root, path)
        except ValueError as exc:
            entry.update(status="outside-root", reason=str(exc))
            worst = max(worst, 2)
            results.append(entry)
            continue
        entry["file"] = rel

        # "new" has to mean "the branch adds this file", nothing else. A path that is not on disk is
        # a caller mistake — a typo, a stale list — and reporting it as new would let a gate pass on
        # a file nobody verified.
        if not os.path.exists(os.path.join(args.root, rel)):
            entry.update(status="missing", reason="no such file under the root")
            worst = max(worst, 2)
            results.append(entry)
            continue

        try:
            before = _git_show(args.root, args.ref, rel)
        except FileNotFoundError:
            entry["status"] = "new"
            results.append(entry)
            continue

        after = _read(os.path.join(args.root, rel))
        try:
            diff = first_difference(before, after)
        except Unverifiable as exc:
            entry.update(status="unverifiable", reason=str(exc))
            worst = max(worst, 3)
            results.append(entry)
            continue
        except ParseError as exc:
            entry.update(status="unparseable", reason=str(exc))
            worst = max(worst, 2)
            results.append(entry)
            continue

        if diff is None:
            entry["status"] = "pass"
        else:
            entry.update(
                status="fail",
                line=diff.line,
                expected=diff.before,
                found=diff.after,
            )
            worst = max(worst, 1)
        results.append(entry)

    verdict = {0: "pass", 1: "fail", 2: "unparseable", 3: "unverifiable"}[worst]
    json.dump({"verdict": verdict, "ref": args.ref, "files": results}, sys.stdout, indent=2)
    print()

    if worst == 1:
        bad = [r for r in results if r["status"] == "fail"][0]
        print(
            f"\ncode changed: {bad['file']}:{bad['line']}\n"
            f"  at {args.ref}: {bad['expected']}\n"
            f"  on disk:      {bad['found']}",
            file=sys.stderr,
        )
    return worst


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_strip = sub.add_parser("strip", help="print the normalized comment-free form of a file")
    p_strip.add_argument("file")
    p_strip.set_defaults(func=cmd_strip)

    p_classify = sub.add_parser("classify", help="report comment spans and the per-line comment map")
    p_classify.add_argument("--file", required=True)
    p_classify.set_defaults(func=cmd_classify)

    p_verify = sub.add_parser("verify", help="compare files on disk against a git ref")
    p_verify.add_argument("--root", required=True, help="repository root")
    p_verify.add_argument("--ref", required=True, help="the commit the sweep started from")
    p_verify.add_argument("--files", nargs="+", required=True, help="repository-relative paths")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ParseError, Unverifiable) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
