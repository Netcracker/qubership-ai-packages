#!/usr/bin/env python3
"""Find pull requests that a later issue or pull request blames for a defect.

Reads a gitcrawl SQLite mirror. A candidate is a pair (blamer, culprit): the
blamer is an issue or pull request created after the culprit pull request was
merged, and its title, body, or a comment names the culprit next to a word such
as "regression", "introduced", "after", or "broke". When the blamer is an issue,
the pull requests that close it ("Fixes #N") are recorded as the fix.

The output is a JSON Lines file of candidates with the text window around each
reference; a model then decides which candidates really blame the culprit.

Usage: find_missed_defects.py --repo pgjdbc/pgjdbc --out candidates.jsonl [--db PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3

DEFAULT_DB = os.path.expanduser("~/Library/Application Support/gitcrawl/gitcrawl.db")
BLAME_WORDS = re.compile(
    r"regress|introduc|since|after|broke|break|caused|due to|because of|revert|started|no longer|used to",
    re.I,
)
CLOSES = re.compile(r"\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)
WINDOW = 250
# A quoted mail reply carries the sender's address, which the output must not repeat.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def references(text: str, owner_repo: str) -> list[tuple[int, str]]:
    """Return (number, window) for each #N or full URL reference in text."""
    pattern = re.compile(
        r"(?<![\w/])#(\d{2,5})\b|github\.com/" + re.escape(owner_repo) + r"/(?:pull|issues)/(\d{2,5})",
        re.I,
    )
    out = []
    for m in pattern.finditer(text):
        lo, hi = max(0, m.start() - WINDOW), m.end() + WINDOW
        out.append((int(m[1] or m[2]), text[lo:hi]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--db", default=DEFAULT_DB)
    args = ap.parse_args()
    db = sqlite3.connect(args.db)
    row = db.execute("select id from repositories where full_name = ?", (args.repo,)).fetchone()
    if row is None:
        raise SystemExit(f"{args.repo} is not in the gitcrawl mirror {args.db}; run gitcrawl sync {args.repo} first")
    (repo_id,) = row
    threads = {
        n: dict(number=n, kind=k, title=t, body=b or "", author=a, created=c, merged=m, state=s)
        for n, k, t, b, a, c, m, s in db.execute(
            """select number, kind, title, body, author_login, created_at_gh, merged_at_gh, state
               from threads where repo_id = ?""",
            (repo_id,),
        )
    }
    comments: dict[int, list[str]] = {}
    for n, body in db.execute(
        """select t.number, c.body from comments c join threads t on t.id = c.thread_id
           where t.repo_id = ? and c.comment_type = 'issue_comment' and not c.is_bot""",
        (repo_id,),
    ):
        comments.setdefault(n, []).append(body)
    # issue number -> pull requests that close it
    fixed_by: dict[int, list[int]] = {}
    for t in threads.values():
        if t["kind"] == "pull_request":
            for m in CLOSES.finditer(t["title"] + "\n" + t["body"]):
                fixed_by.setdefault(int(m[1]), []).append(t["number"])

    seen = set()
    with open(args.out, "w") as out:
        for t in threads.values():
            if (t["author"] or "").endswith("[bot]") or (t["author"] or "").startswith("renovate"):
                continue
            texts = [("title+body", t["title"] + "\n" + t["body"])] + [("comment", c) for c in comments.get(t["number"], [])]
            for where, text in texts:
                for ref, window in references(text, args.repo):
                    culprit = threads.get(ref)
                    if (
                        culprit is None
                        or ref == t["number"]
                        or culprit["kind"] != "pull_request"
                        or not culprit["merged"]
                        or t["created"] <= culprit["merged"]
                        or not BLAME_WORDS.search(window)
                    ):
                        continue
                    key = (t["number"], ref)
                    if key in seen:
                        continue
                    seen.add(key)
                    fixes = [t["number"]] if t["kind"] == "pull_request" else fixed_by.get(t["number"], [])
                    out.write(json.dumps(dict(
                        repo=args.repo, blamer=t["number"], blamer_kind=t["kind"], blamer_title=t["title"],
                        blamer_created=t["created"], culprit=ref, culprit_title=culprit["title"],
                        culprit_merged=culprit["merged"], fix_prs=fixes, where=where,
                        window=EMAIL.sub("<email>", window),
                    )) + "\n")
    print(f"{len(seen)} candidates written to {args.out}")


if __name__ == "__main__":
    main()
