#!/usr/bin/env python3
"""Tests for build_snapshots.py on a pull request merged with a merge commit.

`make test` runs it.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "research", "adversarial-code-review",
                      "eval-candidates", "scripts", "build_snapshots.py")
URL = "https://github.com/o/r/pull/7#discussion_r1"


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True).stdout.strip()


class MergedPullRequestTest(unittest.TestCase):
    """Pull request 7 is reviewed at `reviewed` and merged into main with a merge commit.

    History: fork -> reviewed (the pull request), fork -> main_tip -> merge.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.repo = os.path.join(d, "repo")
        os.mkdir(self.repo)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")

        def commit(name: str, text: str) -> str:
            with open(os.path.join(self.repo, name), "w") as f:
                f.write(text)
            git(self.repo, "add", name)
            git(self.repo, "commit", "-q", "-m", name)
            return git(self.repo, "rev-parse", "HEAD")

        self.fork = commit("a.txt", "a\n")
        git(self.repo, "checkout", "-q", "-b", "pr")
        self.reviewed = commit("b.txt", "one\ntwo\nthree\n")
        git(self.repo, "checkout", "-q", "main")
        self.main_tip = commit("c.txt", "c\n")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "Merge pull request #7", "pr")
        git(self.repo, "update-ref", "refs/remotes/origin/main", "main")
        git(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

        self.findings = os.path.join(d, "findings.jsonl")
        with open(self.findings, "w") as f:
            f.write(json.dumps(dict(
                id="F0000", repo="o/r", pr=7, title="t", author="author", round=1, commit=self.reviewed,
                created="2024-01-01T00:00:00Z", path="b.txt", line=2, url=URL, db_id="1")) + "\n")
        self.labels = os.path.join(d, "labels.jsonl")
        with open(self.labels, "w") as f:
            f.write(json.dumps(dict(url=URL, kind="defect", severity="substantive", category="correctness",
                                    diff_detectable=True)) + "\n")
        self.db = os.path.join(d, "mirror.db")
        self.out = os.path.join(d, "out")
        os.mkdir(self.out)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def build(self, base_sha: str | None) -> tuple[list[dict], str]:
        db = sqlite3.connect(self.db)
        db.executescript("""
            create table repositories (id integer, full_name text);
            create table pull_request_details (repo_id integer, number integer, head_sha text, base_sha text);
            create table comments (raw_json text, author_login text, comment_type text);
        """)
        db.execute("insert into repositories values (1, 'o/r')")
        db.execute("insert into pull_request_details values (1, 7, ?, ?)", (self.reviewed, base_sha))
        db.commit()
        db.close()
        snapshots = os.path.join(self.out, "snapshots.json")
        run = subprocess.run(
            [sys.executable, SCRIPT, "--findings", self.findings, "--labels", self.labels,
             "--clone", f"o/r={self.repo}", "--out-findings", os.path.join(self.out, "findings.jsonl"),
             "--out-snapshots", snapshots, "--db", self.db],
            check=True, capture_output=True, text=True)
        with open(snapshots) as f:
            return json.load(f), run.stdout

    def test_snapshot_base_is_the_fork_point_when_the_mirror_has_the_base_commit(self) -> None:
        snapshots, _ = self.build(base_sha=self.main_tip)
        self.assertEqual([(self.fork, self.reviewed, 3)],
                         [(s["base"], s["commit"], s["diff_lines"]) for s in snapshots])

    def test_snapshot_is_skipped_when_its_commit_is_in_the_default_branch_and_the_mirror_has_no_base(self) -> None:
        snapshots, stdout = self.build(base_sha=None)
        self.assertEqual([], snapshots)
        self.assertIn("skipped 1 snapshots whose commit is already in the base branch: o/r#7 round 1", stdout)


if __name__ == "__main__":
    unittest.main()
