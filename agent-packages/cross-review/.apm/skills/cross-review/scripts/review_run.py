#!/usr/bin/env python3
"""Bookkeeping for a cross-review run.

Every step that can be done without a model lives here: snapshotting the tree, extracting Codex
findings, pairing findings across reviewers, applying decisions to the ledger, and reporting.
The skill drives this script; agents only supply judgment.

Each subcommand does its step whole, so no step can be left half-applied.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"
POINTER_NAME = "cross-review-current"
SEVERITY_ORDER = {"minor": 0, "major": 1, "blocker": 2}
LINE_SLACK = 5
FIX_SHAPES = ("removes_cause", "adds_case", "narrows", "moves")
DEFER_ORIGINS = ("preexisting", "beyond_task", "prose")
PROSE_CATEGORIES = ("docs", "style")

# Codex reports P0-P3; the ledger and the blocking rule work in three levels.
CODEX_PRIORITY_TO_SEVERITY = {0: "blocker", 1: "blocker", 2: "major", 3: "minor"}

# git's own hash for the empty tree, and the left edge of a change whose first commit is a root
# commit.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

SANDBOX_SIGNATURES = (
    "Operation not permitted",
    "failed to initialize in-process app-server client",
    "sandbox",
)


# --------------------------------------------------------------------------- shell


def run(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None,
        check: bool = True) -> str:
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        env={**os.environ, **(env or {})},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        die("command failed: %s\n%s" % (" ".join(cmd), proc.stderr.decode("utf-8", "replace")))
    return proc.stdout.decode("utf-8", "replace")


def die(msg: str) -> NoReturn:
    sys.stderr.write("review_run: %s\n" % msg)
    raise SystemExit(2)


# --------------------------------------------------------------------------- schema


def load_schema(name: str) -> Dict[str, Any]:
    return json.loads((SCHEMA_DIR / ("%s.schema.json" % name)).read_text("utf-8"))


def validate(instance: Any, schema: Dict[str, Any], path: str = "$") -> List[str]:
    """Check the JSON Schema subset the bundled schemas use.

    Supports type, enum, required, properties, additionalProperties: false, items, minimum,
    maximum, minItems, and maxLength. Anything else in a schema is ignored rather than rejected,
    so an unsupported keyword never turns into a false failure.
    """
    errors: List[str] = []
    types = schema.get("type")
    if types is not None:
        allowed = types if isinstance(types, list) else [types]
        if not _type_matches(instance, allowed):
            errors.append("%s: expected %s, got %s" % (path, "/".join(allowed), _kind(instance)))
            return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: %r is not one of %s" % (path, instance, schema["enum"]))

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("%s: missing required property %r" % (path, key))
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append("%s: unexpected property %r" % (path, key))
        for key, sub in props.items():
            if key in instance:
                errors.extend(validate(instance[key], sub, "%s.%s" % (path, key)))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append("%s: needs at least %d item(s)" % (path, schema["minItems"]))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, "%s[%d]" % (path, i)))

    if isinstance(instance, str) and "maxLength" in schema and len(instance) > schema["maxLength"]:
        errors.append("%s: longer than %d characters" % (path, schema["maxLength"]))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("%s: below minimum %s" % (path, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("%s: above maximum %s" % (path, schema["maximum"]))

    return errors


def _type_matches(value: Any, allowed: List[str]) -> bool:
    for t in allowed:
        if t == "null" and value is None:
            return True
        if t == "boolean" and isinstance(value, bool):
            return True
        if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if t == "string" and isinstance(value, str):
            return True
        if t == "array" and isinstance(value, list):
            return True
        if t == "object" and isinstance(value, dict):
            return True
    return False


def _kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


# --------------------------------------------------------------------------- run dir


def pointer_path(repo: Path) -> Path:
    """Where a checkout records its active run.

    `--git-dir`, not `--git-common-dir`: linked worktrees share the common dir, so a pointer
    written there would let a review in one worktree hijack a review in another. Either way the
    file sits outside the working tree, so it cannot land in the diff under review.
    """
    out = run(["git", "rev-parse", "--git-dir"], cwd=repo).strip()
    p = Path(out)
    return (p if p.is_absolute() else (repo / p).resolve()) / POINTER_NAME


def resolve_dir(explicit: Optional[str], repo: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).resolve()
    root = repo_root(Path(repo).resolve() if repo else Path.cwd())
    ptr = pointer_path(root)
    if not ptr.exists():
        die("no active run: %s is missing. Run `init` first." % ptr)
    d = Path(ptr.read_text("utf-8").strip())
    if not (d / "state.json").exists():
        die("pointer at %s names %s, which has no state.json" % (ptr, d))
    return d


def repo_root(start: Path) -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"], cwd=start).strip())


def read_state(d: Path) -> Dict[str, Any]:
    return json.loads((d / "state.json").read_text("utf-8"))


def write_state(d: Path, state: Dict[str, Any]) -> None:
    tmp = d / "state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", "utf-8")
    tmp.replace(d / "state.json")


def round_dir(d: Path, n: int) -> Path:
    return d / "rounds" / str(n)


# --------------------------------------------------------------------------- tree state


def dirty_digest(repo: Path) -> str:
    """Return a digest that changes whenever HEAD, the index, or a non-ignored file changes.

    The status record of a file names its HEAD and index blobs but not its working-tree content,
    so a second edit to a file that is already modified leaves the record unchanged. The content
    of every file that differs from the index, and of every untracked file, is therefore hashed
    too. Every other file matches HEAD and the index, which the HEAD oid and the status record
    cover. A file marked assume-unchanged or skip-worktree is invisible to git, and to this digest.
    """
    h = hashlib.sha256()
    h.update(run(["git", "rev-parse", "HEAD"], cwd=repo).encode("utf-8"))
    h.update(run(["git", "status", "--porcelain=v2", "-z", "-uall"], cwd=repo).encode("utf-8"))
    changed = run(["git", "ls-files", "-z", "--modified", "--others", "--exclude-standard"], cwd=repo)
    for rel in sorted(set(filter(None, changed.split("\0")))):
        path = repo / rel
        h.update(b"\0" + rel.encode("utf-8") + b"\0")
        if path.is_symlink():
            h.update(b"link:" + os.readlink(path).encode("utf-8"))
        elif path.is_file():
            h.update(b"file:" + hashlib.sha256(path.read_bytes()).digest())
        else:
            h.update(b"absent")
    return "sha256:" + h.hexdigest()[:32]


def file_digest(path: Path) -> Optional[str]:
    """Return the digest of a file's bytes, or None when there is no such file."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def snapshot_ref(run_id: str, n: int) -> str:
    return "refs/cross-review/%s/r%d" % (run_id, n)


def worktree_tree(repo: Path, index: Path) -> str:
    """Write the working tree, untracked files included, as a tree object, through a scratch index."""
    if index.exists():
        index.unlink()
    env = {"GIT_INDEX_FILE": str(index)}
    run(["git", "read-tree", "HEAD"], cwd=repo, env=env)
    run(["git", "add", "-A"], cwd=repo, env=env)
    return run(["git", "write-tree"], cwd=repo, env=env).strip()


def make_snapshot(repo: Path, run_id: str, n: int, review_dir: Path) -> Tuple[str, str]:
    """Commit the current tree without touching the real index or working tree."""
    head = run(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    tree = worktree_tree(repo, review_dir / "snap.index")
    snap = run(
        ["git", "commit-tree", tree, "-p", head, "-m", "cross-review snapshot r%d" % n],
        cwd=repo,
    ).strip()
    # Without a ref the snapshot is unreachable and gc may drop it mid-run.
    run(["git", "update-ref", snapshot_ref(run_id, n), snap], cwd=repo)
    return head, snap


# --------------------------------------------------------------------------- symbols

DECL_PATTERNS = [
    re.compile(r"^\s*(?:public|private|protected|internal|static|final|abstract|synchronized|native|default|open|suspend|override|fun|def|func|class|interface|enum|record|struct|impl|trait|type|const|var|let|async)\b.*?(\w+)\s*(?:\(|\{|=|:|$)"),
    re.compile(r"^\s*(\w+)\s*[:=]\s*(?:async\s+)?(?:function|\()"),
]
TYPE_PATTERN = re.compile(r"^\s*(?:public|private|protected|internal|final|abstract|sealed|open|static)?\s*(?:class|interface|enum|record|struct|trait|impl|object)\s+(\w+)")


def guess_symbol(repo: Path, rel_path: str, line: Optional[int]) -> Optional[str]:
    """Name the declaration enclosing a line, so the ledger survives later line shifts."""
    if not line or line < 1:
        return None
    f = repo / rel_path
    try:
        lines = f.read_text("utf-8", "replace").splitlines()
    except OSError:
        return None
    if line > len(lines):
        return None

    member = None
    for i in range(min(line, len(lines)) - 1, -1, -1):
        text = lines[i]
        if not text.strip() or text.lstrip().startswith(("*", "//", "#")):
            continue
        if member is None:
            for pat in DECL_PATTERNS:
                m = pat.match(text)
                if m and not TYPE_PATTERN.match(text):
                    member = m.group(1)
                    break
        m = TYPE_PATTERN.match(text)
        if m:
            return "%s#%s" % (m.group(1), member) if member else m.group(1)
    return member


# --------------------------------------------------------------------------- commands


def cmd_init(args: argparse.Namespace) -> None:
    repo = repo_root(Path(args.repo).resolve() if args.repo else Path.cwd())
    active = active_run(pointer_path(repo))
    if active and not args.force:
        die("%s is a run still %s at round %d; every command finds its run through the pointer, so a new "
            "run would take it over. Read it with `status`, end it with `stop`, or pass --force to replace it."
            % active)
    kind, base, commit, doc = parse_scope(args.scope)
    # Before the run directory exists: a scope git cannot resolve should leave nothing behind.
    base_oid = scope_base_oid(repo, kind, base, commit)
    doc_path, doc_label = (None, None) if doc is None else document_scope(repo, doc)
    task_text = None
    if args.task:
        try:
            task_text = Path(args.task).read_text("utf-8")
        except OSError as exc:
            die("cannot read the task statement %s: %s" % (args.task, exc))
        if not task_text.strip():
            die("the task statement %s is empty" % args.task)
    run_id = hashlib.sha1(("%s|%f" % (repo, time.time())).encode()).hexdigest()[:6]
    tmp = Path(os.environ.get("TMPDIR", "/tmp"))
    d = (tmp / "claude-review" / ("%s-%s" % (repo.name, run_id))).resolve()
    (d / "rounds").mkdir(parents=True, exist_ok=True)
    # A copy, so an edit to the original mid-run cannot change what later rounds are told the change is for.
    task_path = None
    if task_text is not None:
        task_path = d / "task.md"
        task_path.write_text(task_text, "utf-8")

    state = {
        "schema_version": 1,
        "run_id": run_id,
        "repo_root": str(repo),
        "review_dir": str(d),
        "scope": {"kind": kind, "base": base, "commit": commit, "base_oid": base_oid,
                  "file": doc_path, "label": doc_label},
        "task": str(task_path) if task_path else None,
        "legs": [leg.strip() for leg in args.legs.split(",") if leg.strip()],
        "round": 0,
        "max_rounds": args.max_rounds,
        "status": "initialized",
        "codex": {"parent_session_id": None, "rollout_path": None, "rounds": {}},
        "agents": [],
        "rounds": [],
        "ledger": [],
        "families": {},
        "stop_reason": None,
    }
    write_state(d, state)
    ptr = pointer_path(repo)
    ptr.write_text(str(d) + "\n", "utf-8")
    emit({"review_dir": str(d), "run_id": run_id, "pointer": str(ptr),
          "reviewer_name": "rvw-%s-claude" % run_id,
          "task": str(task_path) if task_path else None,
          "next": "review_run.py snapshot"})


def active_run(ptr: Path) -> Optional[Tuple[str, str, int]]:
    """Name the run the pointer holds, if that run has not stopped or converged."""
    try:
        d = Path(ptr.read_text("utf-8").strip())
        state = read_state(d)
        status, n = state["status"], state["round"]
    except (OSError, ValueError, KeyError, TypeError):
        return None  # no run, or one too damaged to resume: nothing to take over
    if status in ("stopped", "converged"):
        return None
    return str(d), status, n


def scope_base_oid(repo: Path, kind: str, base: Optional[str], commit: Optional[str]) -> str:
    """Pin the left edge of the change, once, at init.

    Every later round reviews the range from this commit to that round's snapshot, so the range
    grows as fixes land. Without it each round restates the original argument: a `commit:` run
    re-reviews that one commit forever and never sees a fix, and an `uncommitted` run goes empty
    the moment the fixes are committed.
    """
    if kind == "commit":
        sha = run(["git", "rev-parse", "--verify", "--quiet", "%s^{commit}" % commit],
                  cwd=repo, check=False).strip()
        if not sha:
            die("no such commit: %s" % commit)
        parent = run(["git", "rev-parse", "--verify", "--quiet", "%s^" % sha],
                     cwd=repo, check=False).strip()
        return parent or EMPTY_TREE
    if kind == "base":
        merge_base = run(["git", "merge-base", base, "HEAD"], cwd=repo, check=False).strip()
        if not merge_base:
            die("no merge base between %s and HEAD; is %s a branch in this checkout?" % (base, base))
        return merge_base
    return run(["git", "rev-parse", "HEAD"], cwd=repo).strip()


def parse_scope(spec: str) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    if spec == "uncommitted":
        return "uncommitted", None, None, None
    if spec.startswith("base:"):
        return "base", spec[len("base:"):], None, None
    if spec.startswith("commit:"):
        return "commit", None, spec[len("commit:"):], None
    if spec.startswith("file:"):
        return "file", None, None, spec[len("file:"):]
    die("scope must be uncommitted, base:<branch>, commit:<sha>, or file:<path>; got %r" % spec)


def document_scope(repo: Path, spec: str) -> Tuple[str, str]:
    """Resolve the document a `file:` run reviews, and the path its findings are anchored at.

    The document may live outside the repository, as a plan written in plan mode does. Its
    findings are then anchored at the bare file name, since the schema takes no absolute path.
    """
    path = Path(spec).expanduser().resolve()
    if not path.is_file():
        die("no such file: %s" % spec)
    try:
        label = str(path.relative_to(repo.resolve()))
    except ValueError:
        label = path.name
    return str(path), label


def is_document(state: Dict[str, Any]) -> bool:
    return state["scope"]["kind"] == "file"


def snapshot_document(state: Dict[str, Any], rd: Path) -> Path:
    """Copy the document into the round, so that both reviewers read the same text and its line numbers."""
    src = Path(state["scope"]["file"])
    try:
        text = src.read_text("utf-8")
    except OSError as exc:
        die("cannot read the document %s: %s" % (src, exc))
    if not text.strip():
        die("the document %s is empty" % src)
    dst = rd / "document" / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return dst


def document_diff(label: str, old: Path, new: Path) -> str:
    return "".join(difflib.unified_diff(
        old.read_text("utf-8").splitlines(keepends=True),
        new.read_text("utf-8").splitlines(keepends=True),
        "a/" + label, "b/" + label))


# Each format's headings, and the delimiters of the blocks whose lines are code rather than headings. A Markdown
# fence closes on a run of its own character at least as long; an AsciiDoc block closes on the line that opened it.
MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
MARKDOWN_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
ASCIIDOC_HEADING = re.compile(r"^={1,6}\s+(\S.*?)\s*$")
ASCIIDOC_BLOCK = re.compile(r"^(-{4,}|\.{4,}|\+{4,}|/{4,}|`{3,})\s*$")


def document_heading(doc: Path, line: Optional[int]) -> Optional[str]:
    """Name the heading above a line: the document's analogue of an enclosing declaration.

    Markdown `#` headings and AsciiDoc `=` headings count, except inside a fenced code block, a
    listing, a literal, a passthrough, or a comment block, where such a line is code. Other formats,
    reStructuredText and plain text among them, get None.
    """
    if not line or line < 1:
        return None
    suffix = doc.suffix.lower()
    asciidoc = suffix in (".adoc", ".asciidoc")
    if asciidoc:
        heading_re, block_re = ASCIIDOC_HEADING, ASCIIDOC_BLOCK
    elif suffix in (".md", ".markdown"):
        heading_re, block_re = MARKDOWN_HEADING, MARKDOWN_FENCE
    else:
        return None
    try:
        lines = doc.read_text("utf-8", "replace").splitlines()
    except OSError:
        return None
    heading, block = None, None
    for text in lines[:line]:
        m = block_re.match(text)
        if m:
            opener = m.group(1)
            if block is None:
                block = opener
            elif opener == block if asciidoc else opener[0] == block[0] and len(opener) >= len(block):
                block = None
            continue
        if block is None:
            m = heading_re.match(text)
            if m:
                heading = m.group(1)
    return heading

def cmd_snapshot(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    repo = Path(state["repo_root"])
    n = state["round"] + 1
    if n > state["max_rounds"]:
        die("round %d exceeds max_rounds %d; stop or raise the limit" % (n, state["max_rounds"]))

    rd = round_dir(d, n)
    rd.mkdir(parents=True, exist_ok=True)
    head, snap = make_snapshot(repo, state["run_id"], n, d)
    target = {"head_oid": head, "snapshot_oid": snap, "snapshot_ref": snapshot_ref(state["run_id"], n),
              "snapshot_tree": run(["git", "rev-parse", "%s^{tree}" % snap], cwd=repo).strip(),
              "dirty_digest": dirty_digest(repo),
              "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    doc = snapshot_document(state, rd) if is_document(state) else None
    if doc:
        target["document"] = str(doc)
        target["document_label"] = state["scope"]["label"]
    (rd / "target.json").write_text(json.dumps(target, indent=2) + "\n", "utf-8")
    (rd / "scope.txt").write_text(scope_flags(state) + "\n", "utf-8")

    prev_snap = None
    if n > 1:
        prev = json.loads((round_dir(d, n - 1) / "target.json").read_text("utf-8"))
        prev_snap = prev["snapshot_oid"]
        if doc:
            patch = document_diff(state["scope"]["label"], Path(prev["document"]), doc)
        else:
            patch = run(["git", "diff", "%s..%s" % (prev_snap, snap)], cwd=repo)
        (rd / "fixes.patch").write_text(patch, "utf-8")

    prompt = (document_prompt(state, n, doc, rd / "fixes.patch" if n > 1 else None) if doc
              else codex_prompt(state, n, snap, prev_snap))
    (rd / "codex-prompt.txt").write_text(prompt, "utf-8")

    state["round"] = n
    state["status"] = "reviewing"
    state["target"] = target
    state["rounds"].append({"n": n, "target": target, "degraded": [],
                            "blocking_in": None, "blocking_out": None})
    write_state(d, state)
    emit({"round": n, "review_dir": str(d), "target": target,
          "reviewer_name": "rvw-%s-claude" % state["run_id"],
          "next": "review_run.py codex-cmd %d" % n})


def scope_flags(state: Dict[str, Any]) -> str:
    s = state["scope"]
    if s["kind"] == "uncommitted":
        return "--uncommitted"
    if s["kind"] == "base":
        return "--base %s" % s["base"]
    if s["kind"] == "file":
        return "file:%s" % s["label"]
    return "--commit %s" % s["commit"]


def scope_sentence(state: Dict[str, Any], n: int, snap: Optional[str] = None,
                   prev_snap: Optional[str] = None) -> List[str]:
    """Describe the scope in prose, for the rounds that cannot pass a scope flag.

    What a later round states is a *range*, not the argument `init` was given. Its right edge is
    this round's snapshot commit, which puts the fixes made since the last round inside the scope
    rather than beyond it. Restating the argument instead is what made a `commit:` run re-review
    the same commit every round and never look at a single fix.
    """
    s = state["scope"]
    base_oid = s.get("base_oid")
    if not base_oid or not snap:
        # A run started before the range was pinned. Say what the argument said.
        if s["kind"] == "uncommitted":
            return ["Review the staged, unstaged, and untracked changes in the working tree."]
        if s["kind"] == "base":
            return ["Review the changes this branch introduces relative to `%s` (`git diff %s...HEAD`), "
                    "together with any uncommitted changes in the working tree." % (s["base"], s["base"])]
        return ["Review the changes introduced by commit `%s` (`git show %s`)."
                % (s["commit"], s["commit"])]

    origin = {
        "uncommitted": "the working-tree changes this run started from",
        "base": "the changes this branch introduces relative to `%s`" % s["base"],
        "commit": "commit `%s`" % s["commit"],
    }[s["kind"]]
    out = [
        "Review the change as it stands now: `git diff %s %s`. The right-hand side is a commit "
        "holding the current working tree, uncommitted and untracked files included."
        % (base_oid, snap),
        "",
        "That range is %s **plus every fix applied since**. Review the code inside the range as it "
        "reads now — not the commit or the diff this run started from, which no longer describes "
        "the code." % origin,
    ]
    if prev_snap:
        out += [
            "",
            "The fixes made since round %d are `git diff %s %s`. Check those first: a fix that "
            "introduces a defect, or that does not do what its rationale claims, is what this "
            "round exists to catch. Then re-check the rest of the range."
            % (n - 1, prev_snap, snap),
        ]
    return out


TASK_PROMPT_LIMIT = 6000


def task_statement(state: Dict[str, Any]) -> Optional[str]:
    """The task statement `init --task` copied into the run, cut to what a prompt can carry."""
    path = state.get("task")
    if not path:
        return None
    try:
        text = Path(path).read_text("utf-8").strip()
    except OSError:
        return None
    if len(text) > TASK_PROMPT_LIMIT:
        text = text[:TASK_PROMPT_LIMIT] + "\n[... cut at %d characters; the full text is %s]" % (TASK_PROMPT_LIMIT, path)
    return text


def codex_prompt(state: Dict[str, Any], n: int, snap: Optional[str] = None,
                 prev_snap: Optional[str] = None) -> str:
    """Rebuild the reviewer's memory from the ledger.

    `codex exec review` rejects `--base`, `--uncommitted`, and `--commit` alongside a custom
    prompt: they are alternative ways to say what to review. Every round therefore states its
    scope in the prompt text, round 1 included, so the adversarial instruction and the review
    questions reach Codex from the first round. Later rounds add the ledger.

    What the prompt names is the range ending at this round's snapshot, never the original scope
    argument: see scope_sentence().
    """
    if n == 1:
        out = ["Review this change. Report prioritized, actionable findings.", ""]
        base_oid = state["scope"].get("base_oid")
        if base_oid and snap:
            out.append("The change is `git diff %s %s`. The right-hand side is a commit holding the "
                       "current working tree, uncommitted and untracked files included." % (base_oid, snap))
        else:
            out += scope_sentence(state, n, snap, prev_snap)
    else:
        out = ["Re-review round %d of this change. Report prioritized, actionable findings." % n, ""]
        out += scope_sentence(state, n, snap, prev_snap)
    out.append("")
    out += ledger_lines(state, "code")
    task = task_statement(state)
    if task:
        out.append("The change is meant to do what this task statement asks. Check that it solves this problem, "
                   "all of it, and not an adjacent one. For a bug fix, check that something in the diff or its tests "
                   "shows the cause is proven and gone, not only the symptom made rarer.")
        out.append("")
        out.append("--- task statement ---")
        out.append(task)
        out.append("--- end task statement ---")
        out.append("")
    out.append("Focus on defects this diff introduces. Report pre-existing problems separately and "
               "mark them as such.")
    out.append("")
    out.append("Review adversarially. For each behavior the diff changes, try to build the input, "
               "the state, or the sequence that breaks it rather than reading for plausibility. "
               "Then attack your own finding: name the check, the type, or the invariant that would "
               "make it impossible, and drop the finding if you find one. Report what survives, "
               "with the assumption it rests on.")
    out.append("")
    out.append("Answer these for the diff as a whole, and file a finding for each that applies: Does it add "
               "behavior a caller reading the name, the signature, and the docs would not predict? Is the change "
               "at the right abstraction layer, or does it patch a symptom where the component that owns the "
               "invariant should change? Does it add quadratic or worse complexity in the size of an input, and "
               "is that size bounded? Does it break a persisted format, a wire protocol, an API shape, or a "
               "configuration key that existing readers depend on? Where it adds an exception to, narrows, or takes "
               "precedence over a statement in a file it does not change (a rule of a specification or a decision "
               "record, a documented default, a doc comment), does that statement, read on its own, still state "
               "the old behavior? Is text the diff moves or copies from another file still true, and does a claim "
               "about what another open pull request or branch does hold at its current head?")
    out.append("")
    out.append("Where a hunk repairs a defect by raising a limit or timeout, adding a retry, ignoring an "
               "exception, sleeping, disabling a test, or moving work into another process, check that "
               "something in the diff or its tests shows the cause is gone rather than the symptom rarer.")
    return "\n".join(out) + "\n"


def ledger_lines(state: Dict[str, Any], subject: str) -> List[str]:
    """Tell a reviewer what the earlier rounds decided, so it checks the fixes and does not refile the rejections."""
    fixed = [e for e in state["ledger"] if e["status"] == "fixed"]
    rejected = [e for e in state["ledger"] if e["status"] == "rejected"]
    deferred = [e for e in state["ledger"] if e["status"] == "deferred"]
    out: List[str] = []
    if fixed:
        out.append("Addressed since your last pass. These are claims, not verified facts: check each "
                   "against the %s, and watch for defects the fix itself introduced." % subject)
        for e in fixed:
            out.append("- [%s] %s - %s" % (e["id"], e["title"], e["decision"]["rationale"]))
        out.append("")
    if rejected:
        out.append("Rejected with evidence. Do not refile these unless you can refute the evidence.")
        for e in rejected:
            out.append("- [%s] %s - rejected because %s Evidence: %s"
                       % (e["id"], e["title"], e["decision"]["rationale"], e["decision"]["evidence"]))
        out.append("")
    if deferred:
        out.append("Deferred as out of scope for this change: "
                   + ", ".join("[%s] %s" % (e["id"], e["title"]) for e in deferred))
        out.append("")
    case_families = {k: v for k, v in state.get("families", {}).items()
                     if any(f["shape"] == "adds_case" for f in v["fixes"])}
    if case_families:
        out.append("Properties an earlier fix handled by adding a case, with the findings that reported "
                   "them. The next failure is usually an input next to the ones those fixes handled: "
                   "one level deeper, through a wrapper or a generic call, through a subtype, or two "
                   "handled shapes combined. Try those, not the handled inputs.")
        for name, fam in case_families.items():
            out.append("- %s (%s)" % (name, ", ".join(sorted({m["id"] for m in fam["members"]}))))
        out.append("")
    return out


DOCUMENT_PROMPT_LIMIT = 60000


def document_prompt(state: Dict[str, Any], n: int, doc: Path, fixes_patch: Optional[Path]) -> str:
    """Build the Codex prompt for a `file:` run, which reviews a document rather than a diff.

    The prompt carries the document with line numbers, so that Codex anchors its findings on the
    same lines the Claude reviewer reads in the round's copy.
    """
    label = state["scope"]["label"]
    if n == 1:
        out = ["Review this document. Report prioritized, actionable findings.", ""]
    else:
        out = ["Re-review round %d of this document. Report prioritized, actionable findings." % n, ""]
    out.append("The document is `%s`, a plan or a design written before the code it describes. Anchor every "
               "finding at the file `%s` and at the line numbers below, and quote the lines it is about."
               % (label, label))
    out.append("")
    out.append("The working directory is the repository the document is about. Read the code there to check "
               "every claim the document makes about it: a plan built on a misread API is wrong in every step "
               "that follows.")
    out.append("")
    if fixes_patch:
        out.append("The edits made since round %d are the diff below. Check them first: an edit that introduces "
                   "a defect, or that does not do what its rationale claims, is what this round exists to catch. "
                   "Then re-check the rest of the document." % (n - 1))
        out.append("")
        out.append("--- edits since round %d ---" % (n - 1))
        out.append(fixes_patch.read_text("utf-8").rstrip("\n"))
        out.append("--- end edits ---")
        out.append("")
    out += ledger_lines(state, "document and the code")
    task = task_statement(state)
    if task:
        out.append("The document plans the change this task statement asks for. Check that following the plan "
                   "solves this problem, all of it, and not an adjacent one. For a bug fix, check that the plan "
                   "names the cause and removes it, rather than making the symptom rarer.")
        out.append("")
        out.append("--- task statement ---")
        out.append(task)
        out.append("--- end task statement ---")
        out.append("")
    out.append("Review adversarially. For each step, look for the input or the state that makes it fail once it "
               "is implemented as written, rather than reading the step for plausibility. Then attack your own "
               "finding: name the code, the check, or the later step that already handles the case, and drop "
               "the finding if you find one. Report what survives, with the assumption it rests on.")
    out.append("")
    out.append("Answer these for the document as a whole, and file a finding for each that applies:")
    out.append("- Is every claim about existing code true: the method exists, the call returns what the plan "
               "says, the callers are the ones the plan lists? Does a claim about another open pull request or "
               "branch hold at its current head, and is text copied from another file still true?")
    out.append("- Can each step be implemented as written, without a second design pass? Does it name the file, "
               "the type, or the function it changes?")
    out.append("- Which cases does the plan leave out? Take the set from something enumerable, such as an enum, "
               "a switch, the options of a configuration, or a list in a specification, and name the members "
               "the plan skips.")
    out.append("- Does the plan change the component that owns the invariant, or patch a symptom in one caller?")
    out.append("- Does it break a persisted format, a wire protocol, an API shape, or a configuration key that "
               "existing readers depend on, without saying how those readers are handled?")
    out.append("- Does each behavior the plan promises get a test, and would that test fail without the change?")
    out.append("- Does a step depend on a later one, or add work the task does not need?")
    out.append("- Where the document takes precedence over, narrows, or adds an exception to a rule of another "
               "specification or decision record, does it amend that rule, in the same change where the file can "
               "change? A follow-up settles it only where the file cannot change in this change.")
    out.append("")
    out.append("Mark problems in existing code that the plan neither causes nor has to change as pre-existing.")
    out.append("")
    text = doc.read_text("utf-8")
    if len(text) > DOCUMENT_PROMPT_LIMIT:
        out.append("The document is too long to reproduce here. Read it at `%s`; its line numbers are the ones "
                   "to anchor at." % doc)
    else:
        out.append("--- document %s ---" % label)
        out += ["%5d  %s" % (i, line) for i, line in enumerate(text.splitlines(), start=1)]
        out.append("--- end document ---")
    return "\n".join(out) + "\n"


def cmd_codex_cmd(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = args.round or state["round"]
    rd = round_dir(d, n)
    prompt = rd / "codex-prompt.txt"
    with_prompt = prompt.exists() and prompt.stat().st_size > 0

    if args.resume:
        # Adjudication only. A resumed session tries to start the review tool and the default
        # sandbox refuses it the in-process app-server it needs, so the agent falls back to a
        # hand-written review: this form yields prose, not findings.
        sid = state["codex"].get("parent_session_id")
        if not sid:
            die("no codex session recorded yet; run a review round before resuming")
        cmd = (CODEX_DEADLINE + "codex exec -C %s resume %s --json --output-schema %s -o %s -"
               % (sh(state["repo_root"]), sh(sid),
                  sh(str(SCHEMA_DIR / "adjudication.schema.json")),
                  sh(str(rd / "codex-adj.md"))))
        cmd += " < %s > %s 2> %s" % (sh(args.prompt or str(rd / "codex-adj-prompt.txt")),
                                     sh(str(rd / "codex-adj.jsonl")),
                                     sh(str(rd / "codex-adj.stderr")))
        sys.stdout.write(cmd + "\n")
        return

    # A scope flag and a custom prompt are mutually exclusive in `codex exec review`, so a round
    # that carries the ledger states its scope in the prompt instead. See codex_prompt().
    selector = "-" if with_prompt else scope_flags(state)
    cmd = (CODEX_DEADLINE + "codex exec -C %s --json review %s --title %s -o %s"
           % (sh(state["repo_root"]), selector,
              sh("cross-review r%d (%s)" % (n, state["run_id"])),
              sh(str(rd / "codex.last.md"))))
    if with_prompt:
        cmd += " < %s" % sh(str(prompt))
    cmd += " > %s 2> %s" % (sh(str(rd / "codex.jsonl")), sh(str(rd / "codex.stderr")))
    sys.stdout.write(cmd + "\n")


# Ends a hung Codex after 30 minutes. SIGALRM outlives exec and kills codex; Python is already a
# requirement, where coreutils' `timeout` is missing from a stock macOS.
CODEX_DEADLINE = ("python3 -c 'import os, signal, sys; signal.alarm(int(sys.argv[1])); "
                  "os.execvp(sys.argv[2], sys.argv[2:])' 1800 ")


def sh(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def cmd_codex_extract(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    repo = Path(state["repo_root"])
    n = args.round or state["round"]
    rd = round_dir(d, n)
    target = json.loads((rd / "target.json").read_text("utf-8"))

    jsonl = rd / "codex.jsonl"
    stderr_text = (rd / "codex.stderr").read_text("utf-8", "replace") if (rd / "codex.stderr").exists() else ""
    session_id, review_output = scan_codex_stream(jsonl)

    source = "stdout"
    if review_output is None and session_id:
        rollout = find_rollout(session_id)
        if rollout:
            _, review_output = scan_codex_stream(rollout)
            source = "rollout:%s" % rollout
            state["codex"]["rollout_path"] = str(rollout)

    status = "ok"
    note = ""
    prose = rd / "codex.last.md"
    prose_text = prose.read_text("utf-8", "replace") if prose.exists() else ""
    if review_output is None:
        status = "failed"
        hit = next((s for s in SANDBOX_SIGNATURES if s in stderr_text), None)
        if hit:
            note = "codex reported a sandbox problem (%s)" % hit
        elif prose_text.strip():
            # The structured event and the -o file are two artifacts, and only one is missing here:
            # codex finished the review and wrote it as prose. Calling that a failed round throws
            # away a review that ran.
            note = ("no structured review event, but codex wrote a finished review to %s "
                    "(%d bytes). Read it before you call this round degraded."
                    % (prose, len(prose_text)))
        else:
            note = "no exited_review_mode event in stdout or the rollout file"
            if stderr_text.strip():
                note += "; %s ends with: %s" % (rd / "codex.stderr", stderr_text.strip()[-400:])

    document = ((target["document_label"], Path(target["document"]), Path(state["scope"]["file"]))
                if target.get("document") else None)
    report = build_codex_report(review_output, repo, n, target, dirty_digest(repo), status, document)
    out = rd / "codex.findings.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8")

    if session_id:
        state["codex"]["parent_session_id"] = session_id
    state["codex"]["rounds"][str(n)] = {
        "session_id": session_id, "status": status,
        "findings": len(report["findings"]), "source": source,
    }
    write_state(d, state)
    emit({"status": status, "note": note, "session_id": session_id, "source": source,
          "findings": len(report["findings"]), "file": str(out),
          "report_md": str(prose) if prose_text.strip() else None})


def scan_codex_stream(path: Path) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Pull the parent session id and the last review payload out of a JSONL stream."""
    session_id = None
    review_output = None
    if not path.exists():
        return None, None
    for line in path.read_text("utf-8", "replace").splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        if session_id is None:
            rec_type = rec.get("type")
            if rec_type == "session_meta" or payload.get("type") == "session_meta":
                session_id = payload.get("session_id") or rec.get("session_id")
            elif rec_type == "thread.started":
                # codex-cli 0.145.0 opens its stdout stream with `thread.started`
                # and never emits `session_meta` there, so this is the only place
                # the id appears. It matches the rollout file's `session_meta`
                # id, which is what `find_rollout` globs for. Without it the
                # rollout fallback below cannot run, and a review whose
                # `review_output` reaches only the rollout reads as a failure.
                session_id = rec.get("thread_id") or rec.get("id")
        found = payload.get("review_output") or rec.get("review_output")
        if not found:
            # codex-cli records a finished review as an `item_completed` event whose
            # `ExitedReviewMode` item carries the payload one level down.
            for holder in (payload.get("item"), rec.get("item")):
                if isinstance(holder, dict) and holder.get("review_output"):
                    found = holder["review_output"]
        if found:
            review_output = found
    return session_id, review_output


def find_rollout(session_id: str) -> Optional[Path]:
    base = Path.home() / ".codex" / "sessions"
    if not base.exists():
        return None
    matches = sorted(base.glob("*/*/*/rollout-*%s*.jsonl" % session_id))
    return matches[-1] if matches else None


def build_codex_report(review_output: Optional[Dict[str, Any]], repo: Path, n: int,
                       target: Dict[str, Any], digest_end: str, status: str,
                       document: Optional[Tuple[str, Path, Path]] = None) -> Dict[str, Any]:
    """Turn Codex's review payload into a reviewer report.

    For a `file:` run, ``document`` holds the document's label, the round's copy, and the original.
    """
    findings = []
    verdict = "inconclusive"
    explanation = ""
    if review_output:
        explanation = review_output.get("overall_explanation", "") or ""
        verdict = "revise" if "incorrect" in (review_output.get("overall_correctness") or "") else "approve"
        for i, f in enumerate(review_output.get("findings") or [], start=1):
            loc = f.get("code_location") or {}
            rng = loc.get("line_range") or {}
            abs_path = loc.get("absolute_file_path") or ""
            rel = relativize(abs_path, repo)
            start = rng.get("start")
            # Codex may anchor at the label the prompt gave, at the round's copy, or at the original.
            on_document = document is not None and bool(rel) and (
                rel == document[0] or Path(abs_path).resolve() in (document[1].resolve(), document[2].resolve()))
            if on_document:
                rel = document[0]
            symbol = (document_heading(document[1], start) if on_document
                      else guess_symbol(repo, rel, start) if rel else None)
            findings.append({
                "local_id": "codex-r%d-%d" % (n, i),
                "prior_id": None,
                "severity": CODEX_PRIORITY_TO_SEVERITY.get(f.get("priority"), "major"),
                "confidence": float(f.get("confidence_score") or 0.5),
                "category": "correctness",
                "title": re.sub(r"^\[P\d\]\s*", "", f.get("title") or "").strip(),
                "why": f.get("body") or "",
                "evidence": "%s:%s-%s" % (rel, start, rng.get("end")) if rel else "",
                "depends_on_premise": None,
                "suggestion": f.get("body") or "",
                "anchor": {
                    "path": rel,
                    "symbol": symbol,
                    "start_line": start,
                    "end_line": rng.get("end"),
                },
                "introduced_by_diff": True,
            })
    if not findings and status == "ok":
        verdict = "approve"
    return {
        "status": status,
        "reviewer": "codex",
        "round": n,
        "target": {
            "head_oid": target["head_oid"],
            "snapshot_oid": target["snapshot_oid"],
            "dirty_digest_start": target["dirty_digest"],
            "dirty_digest_end": digest_end,
        },
        "verdict": verdict,
        "findings": findings,
        "preexisting": [],
        "checked_without_findings": explanation[:600],
    }


def relativize(abs_path: str, repo: Path) -> str:
    if not abs_path:
        return ""
    try:
        return str(Path(abs_path).resolve().relative_to(repo.resolve()))
    except ValueError:
        return abs_path


def cmd_digest(args: argparse.Namespace) -> None:
    repo = repo_root(Path(args.repo).resolve() if args.repo else Path.cwd())
    sys.stdout.write(dirty_digest(repo) + "\n")


def cmd_validate(args: argparse.Namespace) -> None:
    schema = load_schema(args.kind)
    try:
        instance = json.loads(Path(args.file).read_text("utf-8"))
    except (OSError, ValueError) as exc:
        emit({"valid": False, "errors": ["cannot read %s: %s" % (args.file, exc)]})
        raise SystemExit(1)
    errors = validate(instance, schema)
    emit({"valid": not errors, "errors": errors})
    if errors:
        raise SystemExit(1)


# --------------------------------------------------------------------------- merging


def cmd_merge_prep(args: argparse.Namespace) -> None:
    """Do the mechanical half of the merge: validate, fence, collapse, and pair by anchor."""
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = args.round or state["round"]
    rd = round_dir(d, n)
    target = json.loads((rd / "target.json").read_text("utf-8"))
    schema = load_schema("finding")
    rewind_round(state, n)

    legs: Dict[str, Dict[str, Any]] = {}
    degraded: List[str] = []
    stale = False
    declared = state.get("legs") or ["codex", "claude"]
    for leg in declared:
        f = rd / ("%s.findings.json" % leg)
        if not f.exists():
            degraded.append(leg)
            continue
        try:
            report = json.loads(f.read_text("utf-8"))
        except ValueError as exc:
            degraded.append(leg)
            sys.stderr.write("review_run: %s report is not valid JSON: %s\n" % (leg, exc))
            continue
        errors = validate(report, schema)
        if errors:
            degraded.append(leg)
            sys.stderr.write("review_run: %s report fails the schema:\n  %s\n" % (leg, "\n  ".join(errors)))
            continue
        ids = [x["local_id"] for x in report["findings"]]
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            degraded.append(leg)
            sys.stderr.write("review_run: %s report gives more than one finding the local_id %s; every finding "
                             "needs its own. Fix %s and rerun merge-prep.\n" % (leg, ", ".join(repeated), f))
            continue
        if report["status"] != "ok" or report["round"] != n:
            degraded.append(leg)
            continue
        t = report["target"]
        # A start that differs from the snapshot means the tree moved before the reviewer began.
        if t["dirty_digest_start"] != t["dirty_digest_end"] or t["dirty_digest_start"] != target["dirty_digest"]:
            stale = True
        if t["snapshot_oid"] != target["snapshot_oid"]:
            stale = True
        legs[leg] = report

    raw: List[Dict[str, Any]] = []
    for leg, report in legs.items():
        for f in report["findings"]:
            raw.append({**f, "reviewer": leg})

    groups, dropped = pair_findings(raw, state["scope"]["label"] if is_document(state) else None)
    ledger_hits = assign_ledger_matches(groups, state["ledger"])

    payload = {
        "round": n,
        "target": {"head_oid": target["head_oid"], "snapshot_oid": target["snapshot_oid"], "stale": stale},
        "legs": {leg: legs[leg]["status"] if leg in legs else "missing" for leg in declared},
        "degraded": degraded,
        "candidate_groups": [
            {"key": g["key"], "reason": g["reason"],
             "ledger_match": ledger_hits[g["key"]],
             "members": g["members"]}
            for g in groups
        ],
        "dropped": dropped,
        "ledger": [{"id": e["id"], "title": e["title"], "status": e["status"],
                    "anchor": e["anchor"], "decision": e["decision"]} for e in state["ledger"]],
    }
    out = rd / "merge-input.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", "utf-8")

    entry = next(r for r in state["rounds"] if r["n"] == n)
    entry["degraded"] = degraded
    # Everything a later step derived from the previous merge-input.json describes other findings.
    entry.update({"reports": {leg: file_digest(rd / ("%s.findings.json" % leg)) for leg in declared},
                  "blocking_in": None, "blocking_out": None, "merge_input": None, "merged": None})
    if n == state["round"]:
        state["status"], state["stop_reason"] = "reviewing", None
    write_state(d, state)
    emit({"file": str(out), "raw": len(raw), "candidate_groups": len(groups),
          "dropped": len(dropped), "degraded": degraded, "stale": stale,
          "next": "spawn the merger with %s" % out})


def pair_findings(raw: List[Dict[str, Any]],
                  document: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Group findings of different reviewers that mechanically refer to the same place.

    ``document`` is the label of the document a `file:` run reviews, whose findings same_place pairs
    by a stricter rule.

    Same path plus either the same symbol or overlapping line ranges. Two findings of one reviewer
    never share a group: a reviewer that filed two findings made two claims, and a group yields one
    item, so grouping them here would drop the second claim's reasoning before the merger saw it, and
    a single-reviewer run has no merger at all. Only a word-for-word repeat is dropped. Semantic
    matches that share no anchor are left for the merger, which is the half that needs a model.
    """
    groups: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    for f in raw:
        twin = next((g for g in groups for m in g["members"]
                     if m["reviewer"] == f["reviewer"] and same_claim(m, f)), None)
        if twin:
            dropped.append({"reviewer": f["reviewer"], "local_id": f["local_id"], "duplicate_of": twin["key"],
                            "reason": "repeats another finding of the same reviewer word for word"})
            continue
        home = next((g for g in groups
                     if all(m["reviewer"] != f["reviewer"] for m in g["members"])
                     and any(same_place(f, m, document) for m in g["members"])), None)
        if home:
            home["members"].append(f)
            home["reason"] = "same anchor"
        else:
            groups.append({"key": "g%d" % (len(groups) + 1), "reason": "single", "members": [f]})
    return groups, dropped


def same_claim(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Decide whether two findings say the same thing, every field but their ids alike."""
    def claim(f: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in f.items() if k not in ("local_id", "prior_id")}
    return claim(a) == claim(b)


def same_place(a: Dict[str, Any], b: Dict[str, Any], document: Optional[str] = None) -> bool:
    """Decide whether two findings certainly point at the same code.

    Line overlap decides whenever both sides carry lines. A shared symbol is not enough on its
    own: two unrelated defects twenty lines apart in one long method share a symbol, and merging
    them here would hide one of them from the merger, which cannot split what it never saw as
    separate. The symbol only breaks the tie when one side has no lines to compare.

    Findings on ``document``, the document a `file:` run reviews, pair only when their line ranges
    overlap with no slack, and, where both name a heading, the headings are equal. A line of prose is
    a whole paragraph, so five lines apart is usually another claim or another section. A side with no
    heading, such as a Codex finding on a format document_heading cannot read, is paired on its lines.
    """
    aa, ba = a["anchor"], b["anchor"]
    if not aa["path"] or aa["path"] != ba["path"]:
        return False
    if document is not None and aa["path"] == document:
        if aa["symbol"] and ba["symbol"] and aa["symbol"] != ba["symbol"]:
            return False
        return overlaps(aa, ba, slack=0)
    if aa.get("start_line") is not None and ba.get("start_line") is not None:
        return overlaps(aa, ba)
    return bool(aa["symbol"] and ba["symbol"] and aa["symbol"] == ba["symbol"])


def overlaps(a: Dict[str, Any], b: Dict[str, Any], slack: int = LINE_SLACK) -> bool:
    a1, a2 = a.get("start_line"), a.get("end_line")
    b1, b2 = b.get("start_line"), b.get("end_line")
    if a1 is None or b1 is None:
        return False
    a2 = a2 if a2 is not None else a1
    b2 = b2 if b2 is not None else b1
    return a1 - slack <= b2 and b1 - slack <= a2


def normalized(f: Dict[str, Any]) -> str:
    return re.sub(r"\W+", " ", (f["title"] or "").lower()).strip()


LEDGER_MATCH_THRESHOLD = 50


def assign_ledger_matches(groups: List[Dict[str, Any]],
                          ledger: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """Propose at most one group per ledger entry, the one that matches it best.

    Two groups proposed for one entry would reach the ledger as one item, and the decision on one
    would close the other. The first group in report order wins a tie.
    """
    proposed = {g["key"]: match_ledger(g, ledger) for g in groups}
    winner: Dict[str, Tuple[float, str]] = {}
    for g in groups:
        fid, score = proposed[g["key"]]
        if fid and (fid not in winner or score > winner[fid][0]):
            winner[fid] = (score, g["key"])
    return {key: fid if fid and winner[fid][1] == key else None for key, (fid, _) in proposed.items()}


def match_ledger(group: Dict[str, Any], ledger: List[Dict[str, Any]]) -> Tuple[Optional[str], float]:
    """Find the ledger entry a group restates, scoring every candidate and taking the best.

    A shared symbol alone cannot carry a match: two distinct defects in one long method share it,
    and mismatching them here would attach one finding's rejection evidence to a different
    finding. Wording is the durable signal, since line numbers shift with every round of fixes.
    A reviewer's own prior_id wins over any score, unless the ledger has no such entry.
    """
    ids = {e["id"] for e in ledger}
    for f in group["members"]:
        if f.get("prior_id") in ids:
            return f["prior_id"], float("inf")

    best_id, best_score = None, 0.0
    for e in ledger:
        for f in group["members"]:
            a = f["anchor"]
            if e["anchor"]["path"] != a["path"]:
                continue
            score = 60.0 * title_similarity(e["title"], f["title"])
            if overlaps(e["anchor"], a):
                score += 40
            if e["anchor"]["symbol"] and a["symbol"] and e["anchor"]["symbol"] == a["symbol"]:
                score += 20
            if score > best_score:
                best_id, best_score = e["id"], score
    return (best_id, best_score) if best_score >= LEDGER_MATCH_THRESHOLD else (None, 0.0)


def title_similarity(a: str, b: str) -> float:
    ta, tb = set(normalized({"title": a}).split()), set(normalized({"title": b}).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / float(len(ta | tb))


def cmd_merge_apply(args: argparse.Namespace) -> None:
    """Turn the merger's grouping decisions into merged.json.

    The merger decides only what belongs together. Ids, severities, agreement, and the blocking
    flag are computed here, so a merger that miscounts cannot corrupt the ledger, and a merger
    that loses a finding is caught rather than believed.
    """
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = args.round or state["round"]
    prep = json.loads((round_dir(d, n) / "merge-input.json").read_text("utf-8"))
    merge_with(d, state, n, prep, json.loads(Path(args.decisions).read_text("utf-8")), args.decisions)


def cmd_merge_auto(args: argparse.Namespace) -> None:
    """Assemble merged.json without a merger, for a run with a single reviewer.

    One reviewer cannot agree with or contradict itself, so the only judgment a merger would add is
    absent by construction. The mechanical pairing and the ledger match still apply.
    """
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = args.round or state["round"]
    prep = json.loads((round_dir(d, n) / "merge-input.json").read_text("utf-8"))
    decisions = {
        "groups": [
            {"key": g["key"],
             "members": [{"reviewer": m["reviewer"], "local_id": m["local_id"]} for m in g["members"]],
             "primary": {"reviewer": g["members"][0]["reviewer"],
                         "local_id": g["members"][0]["local_id"]},
             "prior_id": g["ledger_match"], "contradicts": None}
            for g in prep["candidate_groups"]
        ],
        "dropped": [],
    }
    merge_with(d, state, n, prep, decisions, None)


def merge_with(d: Path, state: Dict[str, Any], n: int, prep: Dict[str, Any],
               decisions: Dict[str, Any], source: Optional[str]) -> None:
    rd = round_dir(d, n)
    rewind_round(state, n)

    by_key = {}
    for g in prep["candidate_groups"]:
        for m in g["members"]:
            if (m["reviewer"], m["local_id"]) in by_key:
                die("%s lists %s/%s more than once, so a decision on it cannot say which finding it means. "
                    "Rerun merge-prep %d." % (rd / "merge-input.json", m["reviewer"], m["local_id"], n))
            by_key[(m["reviewer"], m["local_id"])] = m
    check_decisions(decisions, set(by_key), {e["id"] for e in state["ledger"]}, source)

    items: List[Dict[str, Any]] = []
    dropped = list(prep["dropped"])
    group_ids: Dict[str, str] = {}
    contradicts: Dict[str, Optional[str]] = {}
    next_id = max([int(e["id"].split("-")[1]) for e in state["ledger"]] or [0])
    for g in decisions["groups"]:
        members = [by_key[(m["reviewer"], m["local_id"])] for m in g["members"]]
        primary = by_key[(g["primary"]["reviewer"], g["primary"]["local_id"])]
        if g.get("prior_id"):
            fid = g["prior_id"]
        else:
            next_id += 1
            fid = "F-%03d" % next_id
        item = assemble_item(fid, g, members, primary, state["ledger"])
        items.append(item)
        group_ids[g["key"]] = item["id"]
        contradicts[item["id"]] = g.get("contradicts")
    for m in decisions.get("dropped", []):
        dropped.append({"reviewer": m["reviewer"], "local_id": m["local_id"],
                        "duplicate_of": m.get("duplicate_of", ""), "reason": m.get("reason", "")})
    expected = set(by_key)

    resolve_contradictions(items, group_ids, contradicts)

    merged = {
        "round": n,
        "target": prep["target"],
        "items": items,
        "dropped": dropped,
        "stats": {
            "raw": len(expected) + len(prep["dropped"]),
            "merged": len(items),
            "blocking": sum(1 for i in items if i["blocking"]),
            "degraded": prep["degraded"],
        },
    }
    errors = validate(merged, load_schema("merged"))
    if errors:
        die("assembled merged.json fails its own schema:\n  " + "\n  ".join(errors))
    out = rd / "merged.json"
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", "utf-8")

    entry = next(r for r in state["rounds"] if r["n"] == n)
    entry["blocking_in"] = merged["stats"]["blocking"]
    entry["stale"] = prep["target"]["stale"]
    # Decisions applied to an earlier merged.json do not cover this one.
    entry.update({"merge_input": file_digest(rd / "merge-input.json"), "merged": None, "blocking_out": None})
    if n == state["round"]:
        state["stop_reason"] = None
    state["status"] = "awaiting_fixes"
    write_state(d, state)
    same_site = {i["id"]: ids for i in items if (ids := same_site_fixes(state, i, n))}
    emit({"file": str(out), "items": len(items), "blocking": merged["stats"]["blocking"],
          "degraded": prep["degraded"], "stale": prep["target"]["stale"],
          "same_site": same_site, "families": family_summary(state),
          "next": "read %s, decide each item, then run ledger-apply" % out})


def check_decisions(decisions: Any, findings: set, ledger_ids: set, source: Optional[str]) -> None:
    """Refuse a grouping that merged.json cannot represent faithfully, listing every violation.

    The merger is a model, and the orchestrator reads only merged.json, so a grouping that hides or
    misattributes a finding has to fail here. A primary outside its group gives one defect
    another's text; a reused prior_id makes one decision close two defects; a contradicts or a
    duplicate_of that names no group points the reader at nothing. source is the decisions file,
    or None when merge-auto built the decisions, and then a violation is a defect of this script.
    """
    errors: List[str] = []
    placed: Dict[Tuple[str, str], str] = {}

    def place(ref: Any, where: str) -> Optional[Tuple[str, str]]:
        if not isinstance(ref, dict) or not ref.get("reviewer") or not ref.get("local_id"):
            errors.append("%s holds %r, which is not a {reviewer, local_id} reference" % (where, ref))
            return None
        key = (ref["reviewer"], ref["local_id"])
        if key not in findings:
            errors.append("%s names %s/%s, which is not in merge-input.json" % ((where,) + key))
        elif key in placed:
            errors.append("%s places %s/%s, which %s already placed" % ((where,) + key + (placed[key],)))
        else:
            placed[key] = where
        return key

    groups = decisions.get("groups") if isinstance(decisions, dict) else None
    dropped = decisions.get("dropped", []) if isinstance(decisions, dict) else None
    if not isinstance(groups, list) or not isinstance(dropped, list) \
            or not all(isinstance(x, dict) for x in groups + dropped):
        errors.append("the decisions need a groups list of objects, and dropped, where present, a list "
                      "of objects")
        groups, dropped = [], []
    keys = [g.get("key") for g in groups]
    claimed: Dict[str, str] = {}
    for i, g in enumerate(groups):
        key = g.get("key")
        members = g.get("members") or []
        if isinstance(key, str) and key:
            where = "group %r" % key
            if keys.count(key) > 1:
                errors.append("%s: the key is used by %d groups" % (where, keys.count(key)))
        else:
            where = "groups[%d]" % i
            errors.append("%s has no key; every group needs a unique one" % where)
        own = [place(m, where) for m in members]
        primary = g.get("primary")
        primary_key = (primary.get("reviewer"), primary.get("local_id")) if isinstance(primary, dict) else None
        if not own:
            errors.append("%s has no members" % where)
        elif primary_key not in own:
            errors.append("%s names primary %r, which is not one of its own members" % (where, primary))
        prior_id = g.get("prior_id")
        if prior_id is not None:
            if prior_id not in ledger_ids:
                errors.append("%s names prior_id %s, which is not in the ledger (%s); use null for a "
                              "finding the ledger has not seen"
                              % (where, prior_id, ", ".join(sorted(ledger_ids)) or "empty"))
            elif prior_id in claimed:
                errors.append("%s names prior_id %s, which %s already took; one ledger entry takes one "
                              "group, so keep it on the group that restates it and use null on the "
                              "other, or merge the two groups if they are one defect"
                              % (where, prior_id, claimed[prior_id]))
            else:
                claimed[prior_id] = where
        other = g.get("contradicts")
        if other is not None and (other == key or other not in keys):
            errors.append("%s contradicts %r, which is not another group's key" % (where, other))
    for i, m in enumerate(dropped):
        place(m, "dropped[%d]" % i)
        dup = m.get("duplicate_of")
        if dup and dup not in keys:
            errors.append("dropped[%d] is a duplicate_of %r, which is not a group's key" % (i, dup))
    missing = sorted(findings - set(placed))
    if missing:
        errors.append("%d finding(s) are in no group and not dropped: %s"
                      % (len(missing), ", ".join("%s/%s" % k for k in missing)))
    if not errors:
        return
    listing = "\n  - ".join(errors)
    if source is None:
        die("merge-auto built decisions that fail %d check(s), so merged.json was not written. This is "
            "a defect in review_run.py; report it with the round's merge-input.json:\n  - %s"
            % (len(errors), listing))
    die("%s fails %d check(s), so merged.json was not written:\n  - %s\n"
        "Fix them in that file and rerun merge-apply with it." % (source, len(errors), listing))


def same_site_fixes(state: Dict[str, Any], item: Dict[str, Any], n: int) -> List[str]:
    """Return the ids fixed in an earlier round at the same path and symbol as ``item``, and its own id
    where an earlier round fixed it, whatever symbol the new finding names.

    Such an item may get wrong the same property an earlier fix handled, which is how a run that adds
    one case per round looks from inside a single round; ledger-apply makes the decision say whether it
    does. The answer comes from ``fix_log``, so a later refile, rejection, or decision of this round
    does not remove a fix that is still in the code.
    """
    anchor = item["anchor"]
    ids = [f["id"] for f in fix_log(state)
           if f["kind"] == "fixed" and f["round"] < n
           and (f["id"] == item["id"]
                or (anchor["symbol"] and f["path"] == anchor["path"] and same_symbol(f["symbol"], anchor["symbol"])))]
    return list(dict.fromkeys(ids))


def fix_log(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the run's record of fixed decisions and deferrals with a follow-up, one entry per decision.

    The ledger keeps only each item's latest decision; this keeps every one, with the round, shape,
    family, follow-up, and anchor it had. Entries are only appended, except that redoing a round puts the
    log back as it was before that round (rewind_round), and the one field written later is ``family``,
    set when a later decision lists the fix in ``same_property``. A run started before the log existed
    gets one built from its ledger and its families' fixes."""
    if "fix_log" not in state:
        log = [log_entry(e, e["decision"], e["decision"]["round"]) for e in state["ledger"]
               if e["decision"]["kind"] == "fixed"
               or (e["decision"]["kind"] == "deferred" and e["decision"].get("follow_up"))]
        by_id = {e["id"]: e for e in state["ledger"]}
        for name, fam in state.get("families", {}).items():
            for f in fam["fixes"]:
                if f["id"] in by_id and not any(x["id"] == f["id"] and x["round"] == f["round"] for x in log):
                    log.append(log_entry(by_id[f["id"]], {"kind": "fixed", "fix_shape": f["shape"],
                                                          "family": name}, f["round"]))
        state["fix_log"] = log
    return state["fix_log"]


def log_entry(item: Dict[str, Any], dec: Dict[str, Any], n: int) -> Dict[str, Any]:
    """Return the fix_log record of decision ``dec`` on ``item`` in round ``n``."""
    return {"id": item["id"], "round": n, "kind": dec["kind"], "fix_shape": dec.get("fix_shape"),
            "family": dec.get("family"), "follow_up": dec.get("follow_up"),
            "path": item["anchor"]["path"], "symbol": item["anchor"]["symbol"]}


def outstanding_follow_ups(state: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return each (id, follow-up) the log records once, leaving out those a later fix resolved by
    removing the cause: a fix of the same item, or of another member of the follow-up's family."""
    out: List[Tuple[str, str]] = []
    for f in fix_log(state):
        if not f["follow_up"] or (f["id"], f["follow_up"]) in out:
            continue
        if any(g["kind"] == "fixed" and g["fix_shape"] == "removes_cause" and g["round"] > f["round"]
               and (g["id"] == f["id"] or (f["family"] and g["family"] == f["family"]))
               for g in fix_log(state)):
            continue
        out.append((f["id"], f["follow_up"]))
    return out


def same_symbol(a: Optional[str], b: Optional[str]) -> bool:
    """Tell whether two anchor symbols name one declaration, where one reviewer qualified it and the other
    did not (``Parser#parse`` and ``parse``)."""
    if not a or not b:
        return False
    short, long_ = sorted((a, b), key=len)
    return a == b or long_.endswith(("#" + short, "." + short))


def family_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return each family's members and fixes, with ``recurring`` set where a case-adding fix was followed
    by a new member in a later round."""
    out = {}
    for name, fam in state.get("families", {}).items():
        out[name] = dict(fam, recurring=is_recurring(fam))
    return out


def is_recurring(fam: Dict[str, Any]) -> bool:
    """Tell whether a family produced a member in a round after one of its fixes added a case.

    Once that happens, another case is the fix the next round will refile on a neighboring input.
    """
    case_rounds = [f["round"] for f in fam["fixes"] if f["shape"] == "adds_case"]
    return bool(case_rounds) and max(m["round"] for m in fam["members"]) > min(case_rounds)


def assemble_item(fid: str, group: Dict[str, Any], members: List[Dict[str, Any]],
                  primary: Dict[str, Any], ledger: List[Dict[str, Any]]) -> Dict[str, Any]:
    reviewers = sorted({m["reviewer"] for m in members})
    agreement = "both" if len(reviewers) > 1 else reviewers[0]
    severity = max((m["severity"] for m in members), key=lambda s: SEVERITY_ORDER[s])
    confidence = max(m["confidence"] for m in members)

    prior_entry = next((e for e in ledger if e["id"] == fid), None)
    state_name = "new"
    prior = None
    if prior_entry:
        prior = {"status": prior_entry["status"], "round": prior_entry["decision"]["round"],
                 "rationale": prior_entry["decision"]["rationale"],
                 "evidence": prior_entry["decision"]["evidence"]}
        state_name = {"rejected": "reraised_after_rejection", "fixed": "regression"}.get(
            prior_entry["status"], "repeat")

    return {
        "id": fid,
        "state": state_name,
        "severity": severity,
        "confidence": confidence,
        "category": primary["category"],
        "agreement": agreement,
        "blocking": severity != "minor" and (confidence >= 0.6 or agreement == "both"),
        "sources": [{"reviewer": m["reviewer"], "local_id": m["local_id"],
                     "severity": m["severity"], "confidence": m["confidence"]} for m in members],
        "contradiction": None,
        "prior": prior,
        "title": primary["title"],
        "why": primary["why"],
        "evidence": "\n".join(dict.fromkeys(m["evidence"] for m in members if m["evidence"])),
        "depends_on_premise": next((m["depends_on_premise"] for m in members
                                    if m["depends_on_premise"]), None),
        "suggestion": primary["suggestion"],
        "anchor": primary["anchor"],
    }


def resolve_contradictions(items: List[Dict[str, Any]], group_ids: Dict[str, str],
                           contradicts: Dict[str, Optional[str]]) -> None:
    """Translate group-level contradiction pairs into item ids, in both directions.

    A contradiction is symmetric: one of the pair is wrong. Marking only the side that declared it
    would leave the other looking unopposed, which is the side the main session might act on first.
    """
    by_id = {i["id"]: i for i in items}
    for fid, other_key in contradicts.items():
        other_id = group_ids.get(other_key or "")
        if not other_id or other_id == fid:
            continue
        by_id[fid]["contradiction"] = other_id
        if by_id[other_id]["contradiction"] is None:
            by_id[other_id]["contradiction"] = fid


# --------------------------------------------------------------------------- ledger


def cmd_ledger_apply(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = args.round or state["round"]
    rd = round_dir(d, n)
    merged = json.loads((rd / "merged.json").read_text("utf-8"))
    report = json.loads(Path(args.fix_report).read_text("utf-8"))

    by_id = {i["id"]: i for i in merged["items"]}
    if len(by_id) != len(merged["items"]):
        dupes = sorted({i["id"] for i in merged["items"] if sum(j["id"] == i["id"] for j in merged["items"]) > 1})
        die("%s gives more than one item the id %s, and one decision would close all of them. "
            "Rebuild it: run merge-apply %d --decisions %s, or merge-auto %d for a single-reviewer "
            "run, and give each prior_id to one group only."
            % (rd / "merged.json", ", ".join(dupes), n, rd / "merger-output.json", n))
    decisions = {dec["id"]: dec for dec in report.get("decisions", [])}
    rewind_round(state, n)

    undecided = [i["id"] for i in merged["items"] if i["blocking"] and i["id"] not in decisions]
    if undecided and not args.allow_partial:
        die("no decision for blocking item(s): %s. Decide them, or pass --allow-partial."
            % ", ".join(undecided))

    for fid, dec in decisions.items():
        if fid not in by_id:
            die("decision names %s, which is not in round %d" % (fid, n))
        for field in ("kind", "rationale", "evidence"):
            if not dec.get(field):
                die("decision for %s is missing %s. A rejection without evidence will be refiled "
                    "next round." % (fid, field))
        if dec["kind"] not in ("fixed", "rejected", "deferred"):
            die("decision for %s has kind %r; expected fixed, rejected, or deferred"
                % (fid, dec["kind"]))
        check_family(state, by_id[fid], dec, n)
        upsert_ledger(state["ledger"], by_id[fid], dec, n)

    # Appended only now, so every decision of the round was checked against the log as it stood before it.
    fix_log(state).extend(log_entry(by_id[fid], dec, n) for fid, dec in decisions.items()
                          if dec["kind"] == "fixed" or (dec["kind"] == "deferred" and dec.get("follow_up")))

    for item in merged["items"]:
        if item["id"] not in decisions:
            upsert_ledger(state["ledger"], item, None, n)

    entry = next(r for r in state["rounds"] if r["n"] == n)
    entry["blocking_out"] = sum(
        1 for i in merged["items"]
        if i["blocking"] and decisions.get(i["id"], {}).get("kind") not in ("fixed", "rejected", "deferred")
    )
    entry["fix_report"] = str(Path(args.fix_report).resolve())
    entry["merged"] = file_digest(rd / "merged.json")
    state["status"] = "reviewed"

    # should_stop records this round's blocking ids, which the next round compares against, so it
    # has to run before the state is written rather than after.
    stop, reason = should_stop(state, merged, n)
    if stop:
        state["status"] = "converged" if reason == "no blocking findings" else "stopped"
        state["stop_reason"] = reason
    write_state(d, state)

    emit({"round": n, "ledger": len(state["ledger"]),
          "open_blocking": entry["blocking_out"], "stop": stop, "stop_reason": reason,
          "recurring_families": [k for k, v in family_summary(state).items() if v["recurring"]],
          "next": "review_run.py report" if stop else "review_run.py snapshot"})


def rewind_round(state: Dict[str, Any], n: int) -> None:
    """Put the ledger, the fix log, and the families back as they were before round n's decisions,
    recording them the first time.

    A redone round is matched and decided against what the round before it left: otherwise its own
    first decisions turn a finding into a regression of itself, and its blocking ids into a repeat.
    Only the last round can be redone, since a later round's entries would go with it.
    """
    entry = next(r for r in state["rounds"] if r["n"] == n)
    if "ledger_before" not in entry:
        entry["ledger_before"] = copy.deepcopy(state["ledger"])
        entry["last_blocking_before"] = state.get("_last_blocking_ids")
        entry["fix_log_before"] = copy.deepcopy(fix_log(state))
        entry["families_before"] = copy.deepcopy(state.get("families", {}))
        return
    if n != state["round"]:
        die("round %d is not the last round (round %d is), so it cannot be redone; fix what it missed "
            "in the last round instead." % (n, state["round"]))
    state["ledger"] = copy.deepcopy(entry["ledger_before"])
    state["_last_blocking_ids"] = entry["last_blocking_before"]
    if "fix_log_before" in entry:
        state["fix_log"] = copy.deepcopy(entry["fix_log_before"])
        state["families"] = copy.deepcopy(entry["families_before"])
    else:
        # Recorded by a version that kept no fix log: drop what round n added instead.
        state["fix_log"] = [f for f in fix_log(state) if f["round"] < n]
        for fam in state.get("families", {}).values():
            fam["members"] = [m for m in fam["members"] if m["round"] < n]
            fam["fixes"] = [f for f in fam["fixes"] if f["round"] < n]
        state["families"] = {k: v for k, v in state.get("families", {}).items() if v["members"]}


def check_family(state: Dict[str, Any], item: Dict[str, Any], dec: Dict[str, Any], n: int) -> None:
    """Validate the fields a decision carries about its fix and family, and record it in its family.

    A rejected item asserts nothing about a property, so only the type of its same_property is checked.
    A fixed item
    names the shape of its fix. An item at the site of earlier fixes lists, in
    ``same_property``, those that get the same property wrong, and names that property as its
    ``family``; the listed fixes join the family, so the case a round-1 fix added counts against a
    round-2 one, and the unlisted ones keep their own. An item is never unrelated to its own earlier
    fix. A family whose earlier fix added a case takes no further case: the decision computes the
    property, or takes the decisions that depend on it out of the change and names the follow-up that
    will compute it. A blocking item is deferred only where the
    change did not introduce it, and then with a follow-up, except a docs or style item deferred as
    prose, which §7 closes.
    """
    fid = item["id"]
    shape = dec.get("fix_shape")
    if dec["kind"] == "fixed" and shape not in FIX_SHAPES:
        die("decision for %s is fixed but its fix_shape is %r; expected one of %s"
            % (fid, shape, ", ".join(FIX_SHAPES)))
    shared = dec.get("same_property")
    if shared is not None and not isinstance(shared, list):
        die("%s has same_property of type %s; expected a list of ids." % (fid, type(shared).__name__))
    if dec["kind"] == "rejected":
        return
    earlier = same_site_fixes(state, item, n)
    if earlier and not isinstance(shared, list):
        die("%s is at the site of %s, fixed in an earlier round. List in same_property those that get "
            "the same property wrong, and name it in family; [] where none does."
            % (fid, ", ".join(earlier)))
    shared = shared or []
    stray = [i for i in shared if i not in earlier]
    if stray:
        die("%s lists %s in same_property, which is not an earlier fix at its site (%s)."
            % (fid, ", ".join(stray), ", ".join(earlier) or "none"))
    if fid in earlier and fid not in shared:
        die("%s was itself fixed in an earlier round, so it gets that fix's property wrong again: list "
            "%s in same_property and name the property in family." % (fid, fid))
    if shared and not dec.get("family"):
        die("%s lists %s in same_property without a family: name the property they share."
            % (fid, ", ".join(shared)))
    if dec["kind"] == "deferred" and item["blocking"]:
        if dec.get("origin") == "prose" and item["category"] not in PROSE_CATEGORIES:
            die("%s is a %s finding; origin prose is for a docs or style preference."
                % (fid, item["category"]))
        if dec.get("origin") not in DEFER_ORIGINS:
            die("%s is blocking and deferred with origin %r. Defer only a defect the change did not "
                "introduce (origin: preexisting or beyond_task) or a docs or style preference "
                "(origin: prose); narrow the change for a defect it introduced, and record that as "
                "fixed with fix_shape narrows." % (fid, dec.get("origin")))
        if dec.get("origin") != "prose" and not dec.get("follow_up"):
            die("%s is blocking and deferred without a follow_up: name the draft issue or the "
                "change that will fix it." % fid)
    family = dec.get("family")
    if not family:
        return
    fam = state.setdefault("families", {}).setdefault(family, {"members": [], "fixes": []})
    listed = [f for f in fix_log(state) if f["id"] in shared and f["kind"] == "fixed" and f["round"] < n]
    for f in listed:
        if f["family"] and f["family"] != family:
            die("%s names family %r, but %s, which it lists in same_property, is in family %r. Reuse "
                "that sentence." % (fid, family, f["id"], f["family"]))
    for f in listed:
        f["family"] = family
        add_to_family(fam, f["id"], f["round"], f["fix_shape"])
    add_to_family(fam, fid, n, None)
    if dec["kind"] != "fixed":
        return
    case_fixes = [f for f in fam["fixes"] if f["shape"] == "adds_case" and f["round"] < n]
    if shape == "adds_case" and case_fixes:
        die("%s adds a case to family %r, whose fix %s already added one in round %d, and the family "
            "came back. Compute the property where it is owned (removes_cause), or take the decisions "
            "that depend on it out of the change (narrows) and name the follow_up that computes it."
            % (fid, family, case_fixes[0]["id"], case_fixes[0]["round"]))
    if shape == "narrows" and not dec.get("follow_up"):
        die("%s narrows the change for family %r without a follow_up: name the draft issue or the "
            "change that will compute the property." % (fid, family))
    add_to_family(fam, fid, n, shape)


def add_to_family(fam: Dict[str, Any], fid: str, n: int, shape: Optional[str]) -> None:
    """Record ``fid`` as a member of ``fam`` in round ``n`` and, where ``shape`` is given, its fix; a
    pair already recorded is left alone."""
    if not any(m["id"] == fid and m["round"] == n for m in fam["members"]):
        fam["members"].append({"id": fid, "round": n})
    if shape and not any(f["id"] == fid and f["round"] == n for f in fam["fixes"]):
        fam["fixes"].append({"id": fid, "round": n, "shape": shape})


def upsert_ledger(ledger: List[Dict[str, Any]], item: Dict[str, Any],
                  dec: Optional[Dict[str, Any]], n: int) -> None:
    existing = next((e for e in ledger if e["id"] == item["id"]), None)
    if existing is None:
        existing = {
            "id": item["id"], "title": item["title"], "category": item["category"],
            "severity": item["severity"], "anchor": item["anchor"],
            "first_round": n, "last_seen_round": n, "sources": [],
            "status": "open",
            "decision": {"round": n, "kind": "open", "rationale": "", "evidence": ""},
            "reraised_rounds": [],
        }
        ledger.append(existing)
    existing["last_seen_round"] = n
    existing["severity"] = item["severity"]
    existing["sources"] = sorted({s["reviewer"] for s in item["sources"]})
    if item["state"] == "reraised_after_rejection" and n not in existing["reraised_rounds"]:
        existing["reraised_rounds"].append(n)
    if item["state"] == "regression":
        existing["status"] = "regressed"
    if dec:
        existing["status"] = dec["kind"]
        existing["decision"] = {"round": n, "kind": dec["kind"],
                                "rationale": dec["rationale"], "evidence": dec["evidence"]}
        for field in ("fix_shape", "family", "origin", "follow_up"):
            if dec.get(field):
                existing["decision"][field] = dec[field]
        if isinstance(dec.get("same_property"), list):
            existing["decision"]["same_property"] = dec["same_property"]


def should_stop(state: Dict[str, Any], merged: Dict[str, Any], n: int) -> Tuple[bool, Optional[str]]:
    if merged["stats"]["degraded"]:
        return False, None  # a degraded round can never be the one that declares the review clean
    if merged["stats"]["blocking"] == 0 and not merged["target"]["stale"]:
        return True, "no blocking findings"
    if n >= state["max_rounds"]:
        return True, "reached max_rounds (%d)" % state["max_rounds"]
    open_ids = {i["id"] for i in merged["items"] if i["blocking"]}
    prev = state.get("_last_blocking_ids")
    state["_last_blocking_ids"] = sorted(open_ids)
    if prev is not None and set(prev) == open_ids and open_ids:
        return True, "two consecutive rounds raised the same blocking findings"
    if all(i["state"] == "reraised_after_rejection" for i in merged["items"] if i["blocking"]) and open_ids:
        return True, "every blocking finding is a refile of one already rejected with evidence"
    return False, None


# --------------------------------------------------------------------------- status, report


def cmd_status(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    n = state["round"]
    rd = round_dir(d, n) if n else None

    def has(name: str) -> bool:
        return bool(rd and (rd / name).exists())

    if state["status"] in ("stopped", "converged"):
        nxt = "review_run.py report"
    elif n == 0:
        nxt = "review_run.py snapshot"
    elif not has("codex.findings.json") or not has("claude.findings.json"):
        missing = [f for f in ("codex.findings.json", "claude.findings.json") if not has(f)]
        nxt = "waiting on %s; run codex-extract once codex exits" % ", ".join(missing)
    elif not has("merge-input.json"):
        nxt = "review_run.py merge-prep %d" % n
    elif not has("merged.json"):
        nxt = "spawn the merger on %s, then review_run.py merge-apply %d --decisions <file>" % (rd / "merge-input.json", n)
    elif state["status"] == "awaiting_fixes":
        nxt = "fix what you accept, then review_run.py ledger-apply %d --fix-report <file>" % n
    else:
        nxt = "review_run.py snapshot"

    summary = {
        "review_dir": str(d), "run_id": state["run_id"], "repo_root": state["repo_root"],
        "scope": scope_flags(state), "round": n, "max_rounds": state["max_rounds"],
        "status": state["status"], "reviewer_name": "rvw-%s-claude" % state["run_id"],
        "agents": state["agents"],
        "ledger_open": [e["id"] for e in state["ledger"] if e["status"] in ("open", "regressed")],
        "stop_reason": state["stop_reason"], "next": nxt,
    }
    (d / "RESUME.md").write_text(
        "# Resume this review\n\nRun directory: `%s`\nRound: %d of %d\nStatus: %s\n\nNext step:\n\n```bash\n%s\n```\n"
        % (d, n, state["max_rounds"], state["status"], nxt), "utf-8")
    emit(summary)


def cmd_register_agent(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    state["agents"] = [a for a in state["agents"] if a["role"] != args.role]
    state["agents"].append({"role": args.role, "name": args.name, "agent_id": args.agent_id,
                            "persistent": args.persistent, "last_round": state["round"]})
    write_state(d, state)
    emit({"agents": state["agents"]})


def cmd_report(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    lines = ["# Cross-review report", "",
             "Repository: `%s`" % state["repo_root"],
             "Scope: `%s`" % scope_flags(state),
             "Rounds: %d of %d" % (state["round"], state["max_rounds"])]

    base_oid = state["scope"].get("base_oid")
    if is_document(state) and state.get("target"):
        lines.append("Document reviewed in the last round: `%s`, a copy of `%s`."
                     % (state["target"]["document"], state["scope"]["file"]))
    elif base_oid and state.get("target"):
        lines.append("Range reviewed in the last round: `git diff %s %s` - the scope plus every fix "
                     "applied during the run." % (base_oid, state["target"]["snapshot_oid"]))
    lines.append("")

    degraded = sorted({leg for r in state["rounds"] for leg in r["degraded"]})
    if degraded:
        lines += ["> A reviewer failed to report in at least one round (%s). "
                  "Coverage is incomplete, so this run cannot be called clean." % ", ".join(degraded), ""]

    for status, heading in (("fixed", "Fixed"), ("rejected", "Rejected"),
                            ("deferred", "Deferred"), ("regressed", "Regressed"), ("open", "Open")):
        group = [e for e in state["ledger"] if e["status"] == status]
        if not group:
            continue
        lines += ["## %s" % heading, ""]
        for e in group:
            anchor = e["anchor"]["path"]
            if e["anchor"]["symbol"]:
                anchor += " (`%s`)" % e["anchor"]["symbol"]
            lines += ["### %s - %s [%s]" % (e["id"], e["title"], e["severity"]),
                      "- Location: %s" % anchor,
                      "- Reported by: %s" % ", ".join(e["sources"] or ["-"]),
                      "- Resolution: %s" % (e["decision"]["rationale"] or "not decided"),
                      "- Evidence: %s" % (e["decision"]["evidence"] or "-")]
            if e["reraised_rounds"]:
                lines.append("- Refiled after rejection in round(s): %s"
                             % ", ".join(str(r) for r in e["reraised_rounds"]))
            lines.append("")

    families = family_summary(state)
    if families:
        lines += ["## Families", ""]
        for name, fam in families.items():
            lines.append("- %s%s: members %s; fixes %s" % (
                name, " (recurring)" if fam["recurring"] else "",
                ", ".join("%s (round %d)" % (m["id"], m["round"]) for m in fam["members"]),
                ", ".join("%s %s" % (f["id"], f["shape"]) for f in fam["fixes"]) or "none"))
        lines.append("")

    follow_ups = outstanding_follow_ups(state)
    if follow_ups:
        lines += ["## Follow-ups to file", ""]
        lines += ["- %s: %s" % pair for pair in follow_ups]
        lines.append("")

    open_blocking = [e for e in state["ledger"] if e["status"] in ("open", "regressed")]
    # With no open item, the run is clean only if its last round reviewed the code it ends on: that
    # round finished, its reviewers read a still tree, and the tree has not changed since.
    unconfirmed = last_round_gap(d, state)
    if open_blocking or degraded:
        verdict = "items remaining"
    elif unconfirmed:
        verdict = "incomplete"
        lines += ["> No round reviewed the final code: %s" % unconfirmed, ""]
    else:
        verdict = "clean"
    lines += ["## Verdict: %s" % verdict, ""]
    if state["stop_reason"]:
        lines += ["Stopped because %s." % state["stop_reason"], ""]

    out = d / "report.md"
    out.write_text("\n".join(lines), "utf-8")
    emit({"file": str(out), "verdict": verdict, "degraded": degraded,
          "deleted_refs": drop_snapshot_refs(state, keep_last=verdict != "clean")})


def drop_snapshot_refs(state: Dict[str, Any], keep_last: bool) -> List[str]:
    """Delete the run's snapshot refs, keeping the last round's while the run may go on.

    A snapshot holds every untracked file that is not ignored, so a ref left behind keeps a stray
    secret in the object store and lists it in `git log --all`. Only the next round needs a ref: it
    diffs against the last snapshot. The verdict reads the tree oid the round recorded, not the ref.
    """
    repo = Path(state["repo_root"])
    refs = run(["git", "for-each-ref", "--format=%(refname)", "refs/cross-review/%s/" % state["run_id"]],
               cwd=repo).split()
    if keep_last and state["rounds"]:
        refs = [r for r in refs if r != snapshot_ref(state["run_id"], state["rounds"][-1]["n"])]
    for ref in refs:
        run(["git", "update-ref", "-d", ref], cwd=repo)
    return refs


def last_round_gap(d: Path, state: Dict[str, Any]) -> Optional[str]:
    """Say why the last round does not cover the code the run ends on, or return None if it does."""
    another = ("Run `snapshot` for another round; if the run has used all %d rounds, raise max_rounds "
               "in %s first." % (state["max_rounds"], d / "state.json"))
    if not state["rounds"]:
        return "no round was run. Run `snapshot` to start round 1."
    last = state["rounds"][-1]
    n = last["n"]
    merged_path = round_dir(d, n) / "merged.json"
    if last.get("blocking_in") is None or not merged_path.exists():
        return ("round %d was not merged. Finish it: run merge-prep %d, then merge-apply %d --decisions "
                "<file> (or merge-auto %d for a single-reviewer run), then ledger-apply %d."
                % (n, n, n, n, n))
    # A round merged by an older version of this script has no stale key; merged.json has the flag.
    stale = last.get("stale")
    if stale is None:
        stale = json.loads(merged_path.read_text("utf-8"))["target"]["stale"]
    if last.get("blocking_out") is None:
        return ("round %d was merged, but its decisions were not applied. Run ledger-apply %d "
                "--fix-report <file>." % (n, n))
    # Each step recorded the digest of the file it read; a file edited after that step makes every
    # later result describe findings nobody decided.
    rd = round_dir(d, n)
    redo = "Redo the round from that step: merge-prep %d, then merge-apply or merge-auto, then ledger-apply %d." % (n, n)
    links = [(rd / ("%s.findings.json" % leg), (last.get("reports") or {}).get(leg, ""), "merge-prep")
             for leg in state.get("legs") or ["codex", "claude"]]
    links += [(rd / "merge-input.json", last.get("merge_input"), "the merge"),
              (merged_path, last.get("merged"), "ledger-apply")]
    for path, recorded, step in links:
        if file_digest(path) != recorded:
            return "%s is not the file %s read in round %d. %s" % (path, step, n, redo)
    if stale:
        return "the tree changed while round %d was being reviewed. %s" % (n, another)
    # A document outside the repository is invisible to the tree comparison below.
    if is_document(state):
        original = Path(state["scope"]["file"])
        if file_digest(original) != file_digest(Path(last["target"]["document"])):
            return ("%s changed after round %d copied it, and no round reviewed the edit. %s"
                    % (original, n, another))
    # Compared by content, so committing the reviewed changes keeps the run clean, and any edit
    # after the snapshot, a fix included, does not.
    snap = last["target"]["snapshot_oid"]
    reviewed = last["target"].get("snapshot_tree") or run(
        ["git", "rev-parse", "%s^{tree}" % snap], cwd=Path(state["repo_root"])).strip()
    if worktree_tree(Path(state["repo_root"]), d / "report.index") != reviewed:
        return ("the code changed after round %d took its snapshot, and no round reviewed the change; "
                "`git diff %s` shows the tracked part of it. %s" % (n, snap, another))
    return None


def cmd_stop(args: argparse.Namespace) -> None:
    d = resolve_dir(args.dir, args.repo)
    state = read_state(d)
    state["status"] = "stopped"
    state["stop_reason"] = args.reason
    write_state(d, state)
    emit({"status": "stopped", "stop_reason": args.reason})


def emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- cli


def main() -> None:
    p = argparse.ArgumentParser(prog="review_run.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", help="run directory; defaults to the one the git-dir pointer names")
    p.add_argument("--repo", help="repository path; defaults to the working directory")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create the run directory and claim it in the git dir")
    s.add_argument("--scope", required=True, help="uncommitted, base:<branch>, commit:<sha>, or file:<path>")
    s.add_argument("--max-rounds", type=int, default=6)
    s.add_argument("--task", help="file holding the task statement: the issue, the request, or the prompt the change "
                                  "answers; both reviewers are told what the change is for")
    s.add_argument("--legs", default="codex,claude",
                   help="reviewers this run expects; a missing declared leg degrades the round")
    s.add_argument("--force", action="store_true", help="replace a run the pointer names that has not ended")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("snapshot", help="open the next round: pin the tree and write its prompt")
    s.set_defaults(func=cmd_snapshot)

    s = sub.add_parser("codex-cmd", help="print the codex command for a round")
    s.add_argument("round", nargs="?", type=int)
    s.add_argument("--resume", action="store_true",
                   help="print the adjudication command instead: resume the session to argue one "
                        "rejected finding. It returns prose, not findings, because the review tool "
                        "cannot start from inside a turn under the default sandbox")
    s.add_argument("--prompt", help="prompt file for --resume")
    s.set_defaults(func=cmd_codex_cmd)

    s = sub.add_parser("codex-extract", help="turn the codex stream into a reviewer report")
    s.add_argument("round", nargs="?", type=int)
    s.set_defaults(func=cmd_codex_extract)

    s = sub.add_parser("merge-prep", help="validate both reports and pair findings by anchor")
    s.add_argument("round", nargs="?", type=int)
    s.set_defaults(func=cmd_merge_prep)

    s = sub.add_parser("merge-apply", help="assemble merged.json from the merger's grouping")
    s.add_argument("round", nargs="?", type=int)
    s.add_argument("--decisions", required=True, help="the merger's grouping output")
    s.set_defaults(func=cmd_merge_apply)

    s = sub.add_parser("merge-auto", help="assemble merged.json with no merger, for a single-leg run")
    s.add_argument("round", nargs="?", type=int)
    s.set_defaults(func=cmd_merge_auto)

    s = sub.add_parser("ledger-apply", help="record what was fixed, rejected, or deferred")
    s.add_argument("round", nargs="?", type=int)
    s.add_argument("--fix-report", required=True)
    s.add_argument("--allow-partial", action="store_true",
                   help="accept a round where some blocking items have no decision")
    s.set_defaults(func=cmd_ledger_apply)

    s = sub.add_parser("register-agent", help="record a subagent so a later round can reach it")
    s.add_argument("--role", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--agent-id", required=True)
    s.add_argument("--persistent", action="store_true")
    s.set_defaults(func=cmd_register_agent)

    s = sub.add_parser("digest", help="print the digest a reviewer records before and after reading")
    s.set_defaults(func=cmd_digest)

    s = sub.add_parser("validate", help="check a file against a bundled schema")
    s.add_argument("file")
    s.add_argument("--kind", required=True, choices=["finding", "merged"])
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("status", help="print where the run stands and the next command")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("stop", help="end the run and record why")
    s.add_argument("--reason", required=True)
    s.set_defaults(func=cmd_stop)

    s = sub.add_parser("report", help="write the final report and delete the snapshot refs no later round needs")
    s.set_defaults(func=cmd_report)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
