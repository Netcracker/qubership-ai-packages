#!/usr/bin/env python3
"""Extract one reviewer's root review comments from a gitcrawl mirror.

A finding is a root inline review comment (not a reply) that the reviewer left on
a pull request someone else wrote. Each finding gets a review round: the rank of
its commit among the commits the reviewer commented on, in the order of the first
comment on each. A commit GitHub no longer has (a force-push dropped it) is
recorded as null, and its round is told apart from other dropped commits by
the review the comment belongs to.

Writes findings.jsonl (one finding per line) and, with --batch-dir, the same
findings split into batches of about --batch-size for labeling with
prompts/prompt-label-findings.md; a pull request is never split across batches.

Usage: extract_findings.py --reviewer vlsi --repo pgjdbc/pgjdbc --repo uber/NullAway \
         --out findings.jsonl [--min-findings 5 --batch-dir batches] [--db PATH]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sqlite3

DEFAULT_DB = os.path.expanduser("~/Library/Application Support/gitcrawl/gitcrawl.db")


def root_fields(raw: dict) -> dict | None:
    """Return the fields of a root comment, or None for a reply."""
    if "_graphql" in raw:
        g = raw["_graphql"]
        if g["replyTo"] is not None:
            return None
        return dict(
            commit=g["originalCommit"]["oid"] if g["originalCommit"] else None,
            created=g["createdAt"], path=g["path"], line=g["originalLine"],
            hunk=g["diffHunk"], body=g["body"], url=g["url"], db_id=g["fullDatabaseId"],
            review=g["pullRequestReview"]["fullDatabaseId"] if g["pullRequestReview"] else None,
        )
    if "in_reply_to_id" in raw:  # REST omits the key on a root comment
        return None
    return dict(
        commit=raw["original_commit_id"], created=raw["created_at"], path=raw["path"],
        line=raw["original_line"], hunk=raw["diff_hunk"], body=raw["body"], url=raw["html_url"],
        db_id=str(raw["id"]), review=str(raw["pull_request_review_id"]),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--repo", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--max-lines", type=int, default=20000, help="skip pull requests larger than this")
    ap.add_argument("--batch-dir")
    ap.add_argument("--batch-size", type=int, default=110)
    ap.add_argument("--min-findings", type=int, default=5, help="batch only pull requests with this many findings")
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    marks = ",".join("?" * len(args.repo))
    rows = db.execute(
        f"""select r.full_name, t.number, t.title, t.author_login, t.state, t.merged_at_gh is not null,
                   d.additions + d.deletions, c.raw_json
            from comments c join threads t on t.id = c.thread_id join repositories r on r.id = t.repo_id
            left join pull_request_details d on d.thread_id = t.id
            where c.author_login = ? and c.comment_type = 'pull_review_comment' and t.kind = 'pull_request'
              and coalesce(t.author_login, '') <> ? and r.full_name in ({marks})""",
        (args.reviewer, args.reviewer, *args.repo),
    ).fetchall()

    by_pr: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
    for repo, number, title, author, state, merged, lines, raw in rows:
        f = root_fields(json.loads(raw))
        if f is None or lines is None or lines > args.max_lines:
            continue
        f.update(repo=repo, pr=number, title=title, author=author, state=state, merged=bool(merged), pr_lines=lines)
        by_pr[(repo, number)].append(f)

    findings = []
    for fs in by_pr.values():
        fs.sort(key=lambda f: f["created"])
        # A dropped commit is told apart from another dropped one by its review.
        key = [f["commit"] or f"dropped:{f['review']}" for f in fs]
        order: list[str] = []
        for k in key:
            if k not in order:
                order.append(k)
        for f, k in zip(fs, key):
            f["round"] = order.index(k) + 1
        findings += fs
    findings.sort(key=lambda f: (f["repo"], f["pr"], f["created"]))
    with open(args.out, "w") as out:
        for i, f in enumerate(findings):
            f["id"] = f"F{i:04d}"
            out.write(json.dumps(f) + "\n")
    print(f"{len(findings)} findings in {len(by_pr)} pull requests written to {args.out}")

    if args.batch_dir:
        os.makedirs(args.batch_dir, exist_ok=True)
        batches: list[list[dict]] = [[]]
        for key in sorted(by_pr):
            group = [f for f in findings if (f["repo"], f["pr"]) == key]
            if len(group) < args.min_findings:
                continue
            if batches[-1] and len(batches[-1]) + len(group) > args.batch_size:
                batches.append([])
            batches[-1] += group
        for n, batch in enumerate(batches):
            with open(os.path.join(args.batch_dir, f"batch_{n}.jsonl"), "w") as out:
                for f in batch:
                    hunk_tail = "\n".join((f["hunk"] or "").splitlines()[-12:])
                    out.write(json.dumps(dict(id=f["id"], url=f["url"], repo=f["repo"], pr=f["pr"], pr_title=f["title"],
                                              path=f["path"], diff_hunk_tail=hunk_tail, comment=f["body"])) + "\n")
        print(f"{sum(map(len, batches))} findings in {len(batches)} batches written to {args.batch_dir}")


if __name__ == "__main__":
    main()
