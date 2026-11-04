#!/usr/bin/env python3
"""Group labeled findings into review snapshots, the unit of an eval case.

A snapshot is (pull request, commit the reviewer commented on). Its gold set is
the strong findings on that commit: kind defect, design, or test, severity not
nit, and detectable from the diff (labels from prompts/prompt-label-findings.md). For
each gold finding the script also records whether the pull request author
replied in its thread (author_replied), and whether the pull request's last
commit differs from the snapshot within 3 lines of it (code_changed). A finding
with either counts as accepted.

Commits are looked up in local clones (--clone owner/repo=PATH) and fetched by
sha when missing; a snapshot whose commit GitHub no longer serves is skipped.
The base of a snapshot is its merge base with the pull request's base commit
from the mirror, or with origin/HEAD when the mirror has none; a snapshot whose
base would be the commit itself is skipped and reported.

Labels are matched to findings by comment URL, which stays stable when a new
sync adds comments and shifts the F-numbers. A finding listed in --overrides
with "gold": false is kept, with the reason as "override", but is never gold;
that file records the labels a reader found wrong.

Writes --out-findings (findings with labels and acceptance, without comment
bodies or diff hunks, which stay in the mirror) and --out-snapshots.

Usage: build_snapshots.py --findings findings.jsonl --labels 'batches/*.out.jsonl' \
         --clone pgjdbc/pgjdbc=~/code/pgjdbc --clone uber/NullAway=~/code/nullaway \
         --out-findings data/findings.jsonl --out-snapshots data/snapshots.json \
         [--exclude pgjdbc/pgjdbc#2541 ...] [--overrides data/overrides.jsonl] [--db PATH]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sqlite3
import subprocess

DEFAULT_DB = os.path.expanduser("~/Library/Application Support/gitcrawl/gitcrawl.db")
RARE = {"concurrency", "security", "resource", "compatibility", "performance", "error-handling"}
NEAR = 3  # lines around the commented line that count as "changed near it"


def strong(f: dict) -> bool:
    if f.get("override"):
        return False
    lab = f["label"]
    return lab["kind"] in ("defect", "design", "test") and lab["severity"] != "nit" and lab["diff_detectable"]


class Clones:
    def __init__(self, specs: list[str]):
        self.dirs = {}
        for spec in specs:
            repo, path = spec.split("=", 1)
            self.dirs[repo] = os.path.expanduser(path)

    def git(self, repo: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", self.dirs[repo], *args], capture_output=True, text=True)

    def has(self, repo: str, sha: str | None) -> bool:
        if not sha:
            return False
        if self.git(repo, "cat-file", "-e", sha + "^{commit}").returncode == 0:
            return True
        return self.git(repo, "fetch", "-q", "origin", sha).returncode == 0

    def lines(self, repo: str, a: str, b: str) -> int:
        out = self.git(repo, "diff", "--numstat", a, b).stdout
        return sum(int(x) + int(y) for x, y, *_ in (l.split("\t") for l in out.splitlines()) if x != "-")

    def touched(self, repo: str, a: str, b: str, path: str, line: int | None) -> bool | None:
        if not line or not self.has(repo, b):
            return None
        out = self.git(repo, "diff", "-U0", a, b, "--", path).stdout
        for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))?", out, re.M):
            start, count = int(m[1]), int(m[2] or 1)
            if start - NEAR <= line <= start + max(count, 1) + NEAR:
                return True
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--labels", required=True, help="glob of labeled batch files")
    ap.add_argument("--clone", action="append", required=True)
    ap.add_argument("--out-findings", required=True)
    ap.add_argument("--out-snapshots", required=True)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--overrides", help="JSON Lines of corrections; a line with url and gold false removes a finding from gold")
    ap.add_argument("--exclude", action="append", default=[],
                    help="owner/repo#N of a pull request with no code to review, such as release notes")
    args = ap.parse_args()
    excluded = {(e.split("#")[0], int(e.split("#")[1])) for e in args.exclude}

    labels = {}
    for path in glob.glob(os.path.expanduser(args.labels)):
        for line in open(path):
            if line.strip():
                o = json.loads(line)
                o.pop("id", None)
                labels[o.pop("url")] = o
    findings = [dict(f, label=labels[f["url"]]) for f in map(json.loads, open(args.findings))
                if f["url"] in labels and (f["repo"], f["pr"]) not in excluded]

    if args.overrides:
        overrides = {o["url"]: o["reason"] for o in map(json.loads, open(args.overrides))
                     if "url" in o and o["gold"] is False}
        for f in findings:
            if f["url"] in overrides:
                f["override"] = overrides.pop(f["url"])
        if overrides:
            raise SystemExit(f"{args.overrides} names findings that are not labeled: {', '.join(overrides)}")

    db = sqlite3.connect(args.db)
    replies: dict[str, list[str]] = collections.defaultdict(list)
    for raw, login in db.execute("select raw_json, author_login from comments where comment_type = 'pull_review_comment'"):
        j = json.loads(raw)
        parent = j["_graphql"]["replyTo"]["fullDatabaseId"] if "_graphql" in j and j["_graphql"]["replyTo"] \
            else j.get("in_reply_to_id")  # absent on a root comment
        if parent:
            replies[str(parent)].append(login)
    heads, pr_bases = {}, {}
    for r, n, h, b in db.execute("select r.full_name, d.number, d.head_sha, d.base_sha "
                                 "from pull_request_details d join repositories r on r.id = d.repo_id"):
        heads[(r, n)], pr_bases[(r, n)] = h, b

    clones = Clones(args.clone)
    by_snapshot: dict[tuple, list[dict]] = collections.defaultdict(list)
    for f in findings:
        by_snapshot[(f["repo"], f["pr"], f["round"], f["commit"])].append(f)
    commit_of_round = {(r, p, n): c for r, p, n, c in by_snapshot}

    snapshots, no_base = [], []
    for (repo, pr, rnd, commit), group in sorted(by_snapshot.items()):
        if not clones.has(repo, commit):
            continue
        # The pull request's base branch tip, unlike today's default branch,
        # never contains the reviewed commit, even after a merge commit or a
        # fast-forward brought it in.
        target = pr_bases.get((repo, pr))
        if not clones.has(repo, target):
            target = "origin/HEAD"
        merge_base = clones.git(repo, "merge-base", target, commit)
        if merge_base.returncode != 0:
            raise SystemExit(f"git merge-base {target} {commit} failed in {clones.dirs[repo]}: "
                             f"{merge_base.stderr.strip()}; run git remote set-head origin --auto there")
        base = merge_base.stdout.strip()
        if base == commit:
            no_base.append(f"{repo}#{pr} round {rnd}")
            continue
        prev = commit_of_round.get((repo, pr, rnd - 1))
        head = heads.get((repo, pr))
        gold = [f for f in group if strong(f)]
        for f in gold:
            f["author_replied"] = any(login == f["author"] for login in replies.get(f["db_id"], []))
            f["code_changed"] = clones.touched(repo, commit, head, f["path"], f["line"]) if head else None
        snapshots.append(dict(
            repo=repo, pr=pr, title=group[0]["title"], round=rnd, commit=commit, base=base, prev_commit=prev,
            reviewed_year=int(group[0]["created"][:4]), diff_lines=clones.lines(repo, base, commit),
            findings=len(group), gold=[f["id"] for f in gold],
            accepted=sum(bool(f["author_replied"] or f["code_changed"]) for f in gold),
            defects=sum(f["label"]["kind"] == "defect" for f in gold),
            substantive=sum(f["label"]["severity"] == "substantive" for f in gold),
            rare_categories=sorted({f["label"]["category"] for f in gold} & RARE),
        ))

    with open(args.out_findings, "w") as out:
        for f in findings:
            f = {k: v for k, v in f.items() if k not in ("body", "hunk")}
            out.write(json.dumps(f) + "\n")
    with open(args.out_snapshots, "w") as out:
        json.dump(snapshots, out, indent=1)
    print(f"{len(findings)} labeled findings, {len(snapshots)} snapshots")
    if no_base:
        print(f"skipped {len(no_base)} snapshots whose commit is already in the base branch: {', '.join(no_base)}")


if __name__ == "__main__":
    main()
