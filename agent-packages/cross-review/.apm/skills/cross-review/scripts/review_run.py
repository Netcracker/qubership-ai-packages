#!/usr/bin/env python3
"""Bookkeeping for a cross-review run.

Every step that can be done without a model lives here: snapshotting the tree, extracting Codex
findings, pairing findings across reviewers, applying decisions to the ledger, and reporting.
The skill drives this script; agents only supply judgment.

Each subcommand does its step whole, so no step can be left half-applied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"
POINTER_NAME = "cross-review-current"
SEVERITY_ORDER = {"minor": 0, "major": 1, "blocker": 2}
LINE_SLACK = 5

# Codex reports P0-P3; the ledger and the blocking rule work in three levels.
CODEX_PRIORITY_TO_SEVERITY = {0: "blocker", 1: "blocker", 2: "major", 3: "minor"}

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
    out = run(["git", "status", "--porcelain=v2", "-z", "-uall"], cwd=repo)
    return "sha256:" + hashlib.sha256(out.encode("utf-8")).hexdigest()[:32]


def make_snapshot(repo: Path, run_id: str, n: int, review_dir: Path) -> Tuple[str, str]:
    """Commit the current tree without touching the real index or working tree."""
    head = run(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    index = review_dir / "snap.index"
    if index.exists():
        index.unlink()
    env = {"GIT_INDEX_FILE": str(index)}
    run(["git", "read-tree", "HEAD"], cwd=repo, env=env)
    run(["git", "add", "-A"], cwd=repo, env=env)
    tree = run(["git", "write-tree"], cwd=repo, env=env).strip()
    snap = run(
        ["git", "commit-tree", tree, "-p", head, "-m", "cross-review snapshot r%d" % n],
        cwd=repo,
    ).strip()
    # Without a ref the snapshot is unreachable and gc may drop it mid-run.
    run(["git", "update-ref", "refs/cross-review/%s/r%d" % (run_id, n), snap], cwd=repo)
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
    kind, base, commit = parse_scope(args.scope)
    run_id = hashlib.sha1(("%s|%f" % (repo, time.time())).encode()).hexdigest()[:6]
    tmp = Path(os.environ.get("TMPDIR", "/tmp"))
    d = (tmp / "claude-review" / ("%s-%s" % (repo.name, run_id))).resolve()
    (d / "rounds").mkdir(parents=True, exist_ok=True)

    state = {
        "schema_version": 1,
        "run_id": run_id,
        "repo_root": str(repo),
        "review_dir": str(d),
        "scope": {"kind": kind, "base": base, "commit": commit},
        "legs": [leg.strip() for leg in args.legs.split(",") if leg.strip()],
        "round": 0,
        "max_rounds": args.max_rounds,
        "status": "initialized",
        "codex": {"parent_session_id": None, "rollout_path": None, "rounds": {}},
        "agents": [],
        "rounds": [],
        "ledger": [],
        "stop_reason": None,
    }
    write_state(d, state)
    ptr = pointer_path(repo)
    ptr.write_text(str(d) + "\n", "utf-8")
    emit({"review_dir": str(d), "run_id": run_id, "pointer": str(ptr),
          "reviewer_name": "rvw-%s-claude" % run_id,
          "next": "review_run.py snapshot"})


def parse_scope(spec: str) -> Tuple[str, Optional[str], Optional[str]]:
    if spec == "uncommitted":
        return "uncommitted", None, None
    if spec.startswith("base:"):
        return "base", spec[len("base:"):], None
    if spec.startswith("commit:"):
        return "commit", None, spec[len("commit:"):]
    die("scope must be uncommitted, base:<branch>, or commit:<sha>; got %r" % spec)


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
    target = {"head_oid": head, "snapshot_oid": snap, "dirty_digest": dirty_digest(repo),
              "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    (rd / "target.json").write_text(json.dumps(target, indent=2) + "\n", "utf-8")
    (rd / "scope.txt").write_text(scope_flags(state) + "\n", "utf-8")

    if n > 1:
        prev = json.loads((round_dir(d, n - 1) / "target.json").read_text("utf-8"))
        patch = run(["git", "diff", "%s..%s" % (prev["snapshot_oid"], snap)], cwd=repo)
        (rd / "fixes.patch").write_text(patch, "utf-8")

    (rd / "codex-prompt.txt").write_text(codex_prompt(state, n), "utf-8")

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
    return "--commit %s" % s["commit"]


def scope_sentence(state: Dict[str, Any]) -> str:
    """Describe the scope in prose, for the rounds that cannot pass a scope flag."""
    s = state["scope"]
    if s["kind"] == "uncommitted":
        return "Review the staged, unstaged, and untracked changes in the working tree."
    if s["kind"] == "base":
        return ("Review the changes this branch introduces relative to `%s` "
                "(`git diff %s...HEAD`), together with any uncommitted changes in the working tree."
                % (s["base"], s["base"]))
    return "Review the changes introduced by commit `%s` (`git show %s`)." % (s["commit"], s["commit"])


def codex_prompt(state: Dict[str, Any], n: int) -> str:
    """Rebuild the reviewer's memory from the ledger.

    Round 1 carries nothing, so it runs under a scope flag and Codex's own review prompt. Later
    rounds need the ledger, and `codex exec review` rejects `--base`, `--uncommitted`, and
    `--commit` alongside a custom prompt — they are alternative ways to say what to review. So the
    scope moves into the prompt text from round 2 on, and so does everything else this prompt says,
    including the adversarial instruction round 1 has no way to carry.
    """
    if n == 1:
        return ""
    fixed = [e for e in state["ledger"] if e["status"] == "fixed"]
    rejected = [e for e in state["ledger"] if e["status"] == "rejected"]
    deferred = [e for e in state["ledger"] if e["status"] == "deferred"]

    out = ["Re-review round %d of this change. Report prioritized, actionable findings." % n,
           "", scope_sentence(state), ""]
    if fixed:
        out.append("Addressed since your last pass. These are claims, not verified facts: check each "
                   "against the code, and watch for defects the fix itself introduced.")
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
    out.append("Focus on defects this diff introduces. Report pre-existing problems separately and "
               "mark them as such.")
    out.append("")
    out.append("Review adversarially. For each behavior the diff changes, try to build the input, "
               "the state, or the sequence that breaks it rather than reading for plausibility. "
               "Then attack your own finding: name the check, the type, or the invariant that would "
               "make it impossible, and drop the finding if you find one. Report what survives, "
               "with the assumption it rests on.")
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
        cmd = ("timeout 1800 codex exec -C %s resume %s --json --output-schema %s -o %s -"
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
    cmd = ("timeout 1800 codex exec -C %s --json review %s --title %s -o %s"
           % (sh(state["repo_root"]), selector,
              sh("cross-review r%d (%s)" % (n, state["run_id"])),
              sh(str(rd / "codex.last.md"))))
    if with_prompt:
        cmd += " < %s" % sh(str(prompt))
    cmd += " > %s 2> %s" % (sh(str(rd / "codex.jsonl")), sh(str(rd / "codex.stderr")))
    sys.stdout.write(cmd + "\n")


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
    if review_output is None:
        status = "failed"
        hit = next((s for s in SANDBOX_SIGNATURES if s in stderr_text), None)
        note = ("codex reported a sandbox problem (%s)" % hit) if hit else \
               "no exited_review_mode event in stdout or the rollout file"

    report = build_codex_report(review_output, repo, n, target, dirty_digest(repo), status)
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
          "findings": len(report["findings"]), "file": str(out)})


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
                       target: Dict[str, Any], digest_end: str, status: str) -> Dict[str, Any]:
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
                    "symbol": guess_symbol(repo, rel, start) if rel else None,
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
        if report["status"] != "ok" or report["round"] != n:
            degraded.append(leg)
            continue
        t = report["target"]
        if t["dirty_digest_start"] != t["dirty_digest_end"]:
            stale = True
        if t["snapshot_oid"] != target["snapshot_oid"]:
            stale = True
        legs[leg] = report

    raw: List[Dict[str, Any]] = []
    for leg, report in legs.items():
        for f in report["findings"]:
            raw.append({**f, "reviewer": leg})

    groups, dropped = pair_findings(raw)
    ledger_hits = {g["key"]: match_ledger(g, state["ledger"]) for g in groups}

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
    write_state(d, state)
    emit({"file": str(out), "raw": len(raw), "candidate_groups": len(groups),
          "dropped": len(dropped), "degraded": degraded, "stale": stale,
          "next": "spawn the merger with %s" % out})


def pair_findings(raw: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Group findings that mechanically refer to the same place.

    Same path plus either the same symbol or overlapping line ranges. Semantic matches that share
    no anchor are left for the merger, which is the half that needs a model.
    """
    groups: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    for f in raw:
        placed = False
        for g in groups:
            if any(same_place(f, m) for m in g["members"]):
                if any(m["reviewer"] == f["reviewer"] and normalized(m) == normalized(f)
                       for m in g["members"]):
                    dropped.append({"reviewer": f["reviewer"], "local_id": f["local_id"],
                                    "duplicate_of": g["key"],
                                    "reason": "identical title and anchor within one reviewer"})
                else:
                    g["members"].append(f)
                    g["reason"] = "same anchor"
                placed = True
                break
        if not placed:
            groups.append({"key": "g%d" % (len(groups) + 1), "reason": "single", "members": [f]})
    return groups, dropped


def same_place(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Decide whether two findings certainly point at the same code.

    Line overlap decides whenever both sides carry lines. A shared symbol is not enough on its
    own: two unrelated defects twenty lines apart in one long method share a symbol, and merging
    them here would hide one of them from the merger, which cannot split what it never saw as
    separate. The symbol only breaks the tie when one side has no lines to compare.
    """
    aa, ba = a["anchor"], b["anchor"]
    if not aa["path"] or aa["path"] != ba["path"]:
        return False
    if aa.get("start_line") is not None and ba.get("start_line") is not None:
        return overlaps(aa, ba)
    return bool(aa["symbol"] and ba["symbol"] and aa["symbol"] == ba["symbol"])


def overlaps(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    a1, a2 = a.get("start_line"), a.get("end_line")
    b1, b2 = b.get("start_line"), b.get("end_line")
    if a1 is None or b1 is None:
        return False
    a2 = a2 if a2 is not None else a1
    b2 = b2 if b2 is not None else b1
    return a1 - LINE_SLACK <= b2 and b1 - LINE_SLACK <= a2


def normalized(f: Dict[str, Any]) -> str:
    return re.sub(r"\W+", " ", (f["title"] or "").lower()).strip()


LEDGER_MATCH_THRESHOLD = 50


def match_ledger(group: Dict[str, Any], ledger: List[Dict[str, Any]]) -> Optional[str]:
    """Find the ledger entry a group restates, scoring every candidate and taking the best.

    A shared symbol alone cannot carry a match: two distinct defects in one long method share it,
    and mismatching them here would attach one finding's rejection evidence to a different
    finding. Wording is the durable signal, since line numbers shift with every round of fixes.
    """
    for f in group["members"]:
        if f.get("prior_id"):
            return f["prior_id"]

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
    return best_id if best_score >= LEDGER_MATCH_THRESHOLD else None


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
    merge_with(d, state, n, prep, json.loads(Path(args.decisions).read_text("utf-8")))


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
    merge_with(d, state, n, prep, decisions)


def merge_with(d: Path, state: Dict[str, Any], n: int, prep: Dict[str, Any],
               decisions: Dict[str, Any]) -> None:
    rd = round_dir(d, n)

    by_key = {}
    for g in prep["candidate_groups"]:
        for m in g["members"]:
            by_key[(m["reviewer"], m["local_id"])] = m
    expected = set(by_key)

    seen = set()
    items: List[Dict[str, Any]] = []
    dropped = list(prep["dropped"])
    group_ids: Dict[str, str] = {}
    contradicts: Dict[str, Optional[str]] = {}
    next_id = max([int(e["id"].split("-")[1]) for e in state["ledger"]] or [0])

    for g in decisions.get("groups", []):
        members = []
        for m in g.get("members", []):
            key = (m["reviewer"], m["local_id"])
            if key not in by_key:
                die("merger names an unknown finding: %s/%s" % key)
            if key in seen:
                die("merger placed %s/%s in more than one group" % key)
            seen.add(key)
            members.append(by_key[key])
        if not members:
            continue
        primary_key = (g["primary"]["reviewer"], g["primary"]["local_id"])
        primary = by_key.get(primary_key)
        if primary is None or primary_key not in seen:
            die("group %r names a primary that is not one of its members" % g.get("key"))

        prior_id = g.get("prior_id")
        if prior_id:
            fid = prior_id
        else:
            next_id += 1
            fid = "F-%03d" % next_id
        item = assemble_item(fid, g, members, primary, state["ledger"])
        items.append(item)
        if g.get("key"):
            group_ids[g["key"]] = item["id"]
            contradicts[item["id"]] = g.get("contradicts")

    for m in decisions.get("dropped", []):
        key = (m["reviewer"], m["local_id"])
        if key not in by_key:
            die("merger drops an unknown finding: %s/%s" % key)
        if key in seen:
            die("merger both grouped and dropped %s/%s" % key)
        seen.add(key)
        dropped.append({"reviewer": m["reviewer"], "local_id": m["local_id"],
                        "duplicate_of": m.get("duplicate_of", ""), "reason": m.get("reason", "")})

    missing = expected - seen
    if missing:
        die("merger lost %d finding(s): %s"
            % (len(missing), ", ".join("%s/%s" % k for k in sorted(missing))))

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
    state["status"] = "awaiting_fixes"
    write_state(d, state)
    emit({"file": str(out), "items": len(items), "blocking": merged["stats"]["blocking"],
          "degraded": prep["degraded"], "stale": prep["target"]["stale"],
          "next": "read %s, decide each item, then run ledger-apply" % out})


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
    decisions = {dec["id"]: dec for dec in report.get("decisions", [])}

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
        upsert_ledger(state["ledger"], by_id[fid], dec, n)

    for item in merged["items"]:
        if item["id"] not in decisions:
            upsert_ledger(state["ledger"], item, None, n)

    entry = next(r for r in state["rounds"] if r["n"] == n)
    entry["blocking_out"] = sum(
        1 for i in merged["items"]
        if i["blocking"] and decisions.get(i["id"], {}).get("kind") not in ("fixed", "rejected", "deferred")
    )
    entry["fix_report"] = str(Path(args.fix_report).resolve())
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
          "next": "review_run.py report" if stop else "review_run.py snapshot"})


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
             "Rounds: %d of %d" % (state["round"], state["max_rounds"]), ""]

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

    open_blocking = [e for e in state["ledger"] if e["status"] in ("open", "regressed")]
    verdict = "items remaining" if (open_blocking or degraded) else "clean"
    lines += ["## Verdict: %s" % verdict, ""]
    if state["stop_reason"]:
        lines += ["Stopped because %s." % state["stop_reason"], ""]

    out = d / "report.md"
    out.write_text("\n".join(lines), "utf-8")
    emit({"file": str(out), "verdict": verdict, "degraded": degraded})


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
    s.add_argument("--scope", required=True, help="uncommitted, base:<branch>, or commit:<sha>")
    s.add_argument("--max-rounds", type=int, default=6)
    s.add_argument("--legs", default="codex,claude",
                   help="reviewers this run expects; a missing declared leg degrades the round")
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

    s = sub.add_parser("validate", help="check a file against a bundled schema")
    s.add_argument("file")
    s.add_argument("--kind", required=True, choices=["finding", "merged"])
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("status", help="print where the run stands and the next command")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("stop", help="end the run and record why")
    s.add_argument("--reason", required=True)
    s.set_defaults(func=cmd_stop)

    s = sub.add_parser("report", help="write the final report")
    s.set_defaults(func=cmd_report)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
