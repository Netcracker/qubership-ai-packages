#!/usr/bin/env python3
"""Measure how often a skill's description makes Claude Code load the skill.

Each query runs through `claude -p` in a scratch project that holds the candidate skill and every other skill in
`agent-packages/`, so the candidate competes with the descriptions a consumer of this marketplace has installed.
`--setting-sources project` keeps the caller's own CLAUDE.md, hooks, and skills out of the run. A query counts as
triggered when the session calls the Skill tool with the candidate's name at any point before it ends.

skill-creator's run_eval.py answers a different question in this repository: it registers the description as a
command rather than a skill, and it scores a run as not triggered as soon as the first tool call is anything else,
such as loading test-authoring first.

Usage, from the repository root:

    python3 research/blackbox-test-design/trigger/run_trigger_eval.py \
        research/blackbox-test-design/trigger/eval-set.json out.json [--description FILE] [--runs 3] [--model sonnet]

Without --description, the description in the candidate's SKILL.md is used. Each run costs one short session, so a
pass over the 89 queries at three runs each is about 270 sessions.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SKILL = "blackbox-test-design"
DISALLOWED = "Write,Edit,NotebookEdit,Bash,WebFetch,WebSearch,Agent,Task"


def with_description(skill_md: str, description: str) -> str:
    """Return skill_md with its frontmatter description replaced by a one-line JSON string."""
    _, frontmatter, body = skill_md.split("---\n", 2)
    out, in_description = [], False
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            out.append("description: " + json.dumps(description))
            in_description = True
        elif in_description and (line.startswith(" ") or not line):
            continue
        else:
            in_description = False
            out.append(line)
    return "---\n" + "\n".join(out) + "\n---\n" + body


def skills_invoked(stream_lines) -> tuple[list[str], bool, str | None]:
    """Return the skill names passed to the Skill tool, in order, from claude's stream-json output; whether the
    session reached a verdict: it called the candidate, or it ended with a result event that is not an error; and the
    model id the session reported at start.

    Reading stops at the first call to the candidate or at the result event. A session that crashed, timed out, or hit
    a rate limit reaches no verdict, and its run is left out of the rates rather than counted as not triggered.
    """
    names, decided, model = [], False, None
    for line in stream_lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            model = event.get("model")
        elif event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use" and block["name"] == "Skill":
                    names.append(block["input"].get("skill", ""))
            if SKILL in names:
                decided = True
                break
        elif event.get("type") == "result":
            decided = not event.get("is_error", False)
            break
    return names, decided, model


def score(evals: list[dict], runs: dict[int, list[bool]]) -> dict:
    """Summarize per-query trigger rates; a query passes when its majority matches should_trigger.

    runs holds only the runs that reached a verdict; a query with none is reported and fails.
    """
    rows, hit, miss, false_hit, true_miss = [], 0.0, 0.0, 0.0, 0.0
    for i, item in enumerate(evals):
        if not runs[i]:
            rows.append({**item, "rate": None, "pass": False})
            continue
        rate = sum(runs[i]) / len(runs[i])
        if item["should_trigger"]:
            hit, miss = hit + rate, miss + 1 - rate
        else:
            false_hit, true_miss = false_hit + rate, true_miss + 1 - rate
        rows.append({**item, "rate": rate, "pass": (rate >= 0.5) == item["should_trigger"]})
    return {
        "recall": hit / (hit + miss) if hit + miss else None,
        "false_positive_rate": false_hit / (false_hit + true_miss) if false_hit + true_miss else None,
        "passed": sum(r["pass"] for r in rows),
        "total": len(rows),
        "rows": rows,
    }


def current_description() -> str:
    """Return the description in the candidate's SKILL.md, folded to one line."""
    skill_md = (REPO / "agent-packages" / SKILL / ".apm/skills" / SKILL / "SKILL.md").read_text()
    return yaml.safe_load(skill_md.split("---\n", 2)[1])["description"].strip()


def make_project(description: str | None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="trigger-eval-"))
    for skill_md in sorted(REPO.glob("agent-packages/*/.apm/skills/*/SKILL.md")):
        name = skill_md.parent.name
        text = skill_md.read_text()
        if name == SKILL and description is not None:
            text = with_description(text, description)
        target = root / ".claude/skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def claude_command(query: str, model: str | None) -> list[str]:
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose", "--setting-sources", "project",
           "--strict-mcp-config", "--no-session-persistence", "--max-turns", "4", "--disallowedTools", DISALLOWED]
    return cmd + ["--model", model] if model else cmd


def run_query(cmd: list[str], root: Path, timeout: float) -> tuple[list[str], bool, str | None]:
    """Run one session and read its verdict; a session still running after timeout seconds is killed."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(cmd, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    timer = threading.Timer(timeout, proc.kill)
    timer.start()
    try:
        return skills_invoked(proc.stdout)
    finally:
        timer.cancel()
        if proc.poll() is None:
            proc.kill()
        proc.wait()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_set")
    ap.add_argument("out")
    ap.add_argument("--description", help="file with a candidate description; default: the one in SKILL.md")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--model")
    ap.add_argument("--timeout", type=int, default=240)
    args = ap.parse_args()

    evals = json.loads(Path(args.eval_set).read_text())
    description = Path(args.description).read_text().strip() if args.description else None
    measured = description or current_description()
    root = make_project(description)
    runs: dict[int, list[bool]] = {i: [] for i in range(len(evals))}
    others: dict[int, set[str]] = {i: set() for i in range(len(evals))}
    failed = 0
    models: set[str] = set()
    try:
        with ThreadPoolExecutor(args.workers) as pool:
            futures = {pool.submit(run_query, claude_command(evals[i]["query"], args.model), root, args.timeout): i
                       for i in range(len(evals)) for _ in range(args.runs)}
            for future in as_completed(futures):
                i = futures[future]
                names, decided, model = future.result()
                if model:
                    models.add(model)
                if not decided:
                    failed += 1
                    continue
                runs[i].append(SKILL in names)
                others[i].update(n for n in names if n != SKILL)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    result = score(evals, runs)
    for i, row in enumerate(result["rows"]):
        row["other_skills"] = sorted(others[i])
    result = {"model": ", ".join(sorted(models)) or None, "model_requested": args.model or "default", "runs": args.runs,
              "failed_runs": failed, "description": measured, **result}
    Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(f"recall={result['recall']:.3f} false_positive_rate={result['false_positive_rate']:.3f} "
          f"passed={result['passed']}/{result['total']} failed_runs={failed}")
    for row in result["rows"]:
        if not row["pass"]:
            rate = "no verdict" if row["rate"] is None else f"{row['rate']:.2f}"
            print(f"  FAIL should_trigger={row['should_trigger']} rate={rate}: {row['query'][:100]}")


if __name__ == "__main__":
    main()
