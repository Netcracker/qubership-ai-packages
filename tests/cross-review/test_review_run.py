"""review_run.py against a throwaway git repository, driven through its command line: the digest that fences a
reviewer's reading, the ledger ids a round may reuse, and the verdict a run ends on."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "cross-review", ".apm", "skills",
                      "cross-review", "scripts", "review_run.py")

SOURCE = "".join("line %d\n" % i for i in range(1, 41))


class ReviewRunTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        # init places the run directory under TMPDIR; keep it inside the throwaway tree.
        self.env = {**os.environ, "TMPDIR": os.path.join(self.repo, ".git", "tmp")}
        self.git("init", "-q")
        self.git("config", "user.email", "t")
        self.git("config", "user.name", "t")
        self.write("app.py", SOURCE)
        self.git("add", "app.py")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as f:
            f.write(text)

    def run_script(self, *args, check=True):
        proc = subprocess.run([sys.executable, os.path.abspath(SCRIPT), "--repo", self.repo, *args],
                              cwd=self.repo, env=self.env, capture_output=True, encoding="utf-8")
        if check and proc.returncode != 0:
            self.fail("review_run.py %s exited %d:\n%s" % (" ".join(args), proc.returncode, proc.stderr))
        return proc

    def emitted(self, *args):
        return json.loads(self.run_script(*args).stdout)

    def digest(self):
        return self.run_script("digest").stdout.strip()

    def start_run(self, max_rounds):
        self.run_dir = self.emitted("init", "--scope", "uncommitted", "--legs", "claude",
                                    "--max-rounds", str(max_rounds))["review_dir"]

    def round_file(self, n, name):
        return os.path.join(self.run_dir, "rounds", str(n), name)

    def review(self, findings, digest_start=None, digest_end=None):
        """Open the next round and file a claude report on it, read from the round's own target."""
        n = self.emitted("snapshot")["round"]
        with open(self.round_file(n, "target.json"), encoding="utf-8") as f:
            target = json.load(f)
        report = {
            "status": "ok", "reviewer": "claude", "round": n,
            "target": {"head_oid": target["head_oid"], "snapshot_oid": target["snapshot_oid"],
                       "dirty_digest_start": digest_start or target["dirty_digest"],
                       "dirty_digest_end": digest_end or target["dirty_digest"]},
            "verdict": "revise" if findings else "approve",
            "findings": findings, "preexisting": [], "checked_without_findings": "app.py",
        }
        with open(self.round_file(n, "claude.findings.json"), "w", encoding="utf-8") as f:
            json.dump(report, f)
        self.run_script("merge-prep")
        return n

    def decide(self, n, decisions):
        path = self.round_file(n, "fix-report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"decisions": decisions}, f)
        return self.emitted("ledger-apply", "--fix-report", path)

    def merge_apply(self, n, groups):
        path = self.round_file(n, "merger-output.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"groups": groups, "dropped": []}, f)
        return self.run_script("merge-apply", "--decisions", path, check=False)

    def ledger_matches(self, n):
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            groups = json.load(f)["candidate_groups"]
        return [(g["members"][0]["local_id"], g["ledger_match"]) for g in groups]

    def report(self):
        """Run report and return its verdict with the explanation line, if the report has one."""
        out = self.emitted("report")
        with open(out["file"], encoding="utf-8") as f:
            notes = [line for line in f.read().splitlines() if line.startswith("> No round")]
        return out["verdict"], notes

    def items(self, n):
        with open(self.round_file(n, "merged.json"), encoding="utf-8") as f:
            return json.load(f)["items"]

    def ledger_with_one_deferred_finding(self):
        """Round 1 reports one blocking finding at app.py:10, and the run defers it as F-001."""
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check in parse")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "deferred", "rationale": "later", "evidence": "app.py:10"}])

    # ------------------------------------------------------------------ digest

    def test_digest_is_stable_while_the_tree_is_unchanged(self):
        self.write("app.py", SOURCE + "edit\n")
        self.assertEqual(self.digest(), self.digest())

    def test_editing_a_changed_file_again_changes_the_digest(self):
        for name, first in (("app.py", SOURCE + "first edit\n"), ("new.py", "first draft\n")):
            with self.subTest(name):
                self.write(name, first)
                before = self.digest()
                self.write(name, first.replace("first", "second"))
                self.assertNotEqual(before, self.digest(), "digest after a second edit of " + name)

    # ------------------------------------------------------------------ ledger ids

    def test_two_groups_naming_one_prior_id_are_refused(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load")])
        proc = self.merge_apply(n, [group("c1", "F-001"), group("c2", "F-001")])
        self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
        self.assertIn("names prior_id F-001, which group 'c1' already took", proc.stderr)
        self.assertFalse(os.path.exists(self.round_file(n, "merged.json")), "merged.json written")

    def test_a_prior_id_used_once_keeps_its_id_beside_a_new_finding(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load")])
        proc = self.merge_apply(n, [group("c1", "F-001"), group("c2", None)])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual([("c1", "F-001"), ("c2", "F-002")],
                         [(i["sources"][0]["local_id"], i["id"]) for i in self.items(n)])

    def test_a_prior_id_missing_from_the_ledger_is_refused(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 10, "Missing null check in parse")])
        proc = self.merge_apply(n, [group("c1", "F-099")])
        self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
        self.assertIn("names prior_id F-099, which is not in the ledger (F-001)", proc.stderr)

    def test_merge_prep_proposes_a_ledger_entry_only_to_the_group_that_matches_it_best(self):
        self.ledger_with_one_deferred_finding()
        # Both carry the title of F-001; only c2 also overlaps its lines at app.py:10.
        n = self.review([finding("c1", 18, "Missing null check in parse"),
                         finding("c2", 10, "Missing null check in parse")])
        self.assertEqual([("c1", None), ("c2", "F-001")], self.ledger_matches(n))

    def test_merge_prep_gives_a_tied_ledger_entry_to_the_first_group(self):
        self.ledger_with_one_deferred_finding()
        # Both carry the title of F-001, and neither overlaps its lines.
        n = self.review([finding("c1", 18, "Missing null check in parse"),
                         finding("c2", 30, "Missing null check in parse")])
        self.assertEqual([("c1", "F-001"), ("c2", None)], self.ledger_matches(n))

    def test_merge_prep_prefers_a_reviewer_prior_id_over_a_closer_match(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load", prior_id="F-001")])
        self.assertEqual([("c1", None), ("c2", "F-001")], self.ledger_matches(n))

    def test_merge_prep_ignores_a_reviewer_prior_id_the_ledger_lacks(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 30, "Unclosed file in load", prior_id="F-099")])
        self.assertEqual([("c1", None)], self.ledger_matches(n))

    def test_a_primary_from_another_group_is_refused(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load")])
        other = group("c2", None)
        other["primary"] = {"reviewer": "claude", "local_id": "c1"}
        proc = self.merge_apply(n, [group("c1", None), other])
        self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
        self.assertIn("group 'c2' names primary", proc.stderr)
        self.assertIn("which is not one of its own members", proc.stderr)

    def test_a_contradiction_naming_no_group_is_refused(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check in parse")])
        lone = group("c1", None)
        lone["contradicts"] = "g9"
        proc = self.merge_apply(n, [lone])
        self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
        self.assertIn("group 'c1' contradicts 'g9', which is not another group's key", proc.stderr)

    def test_merge_apply_refuses_a_grouping_that_misplaces_a_finding(self):
        c1, c2 = {"reviewer": "claude", "local_id": "c1"}, {"reviewer": "claude", "local_id": "c2"}
        ghost = {"reviewer": "claude", "local_id": "c9"}
        cases = [
            ("a group with no key", [{**group("c1", None), "key": None}, group("c2", None)], [],
             "groups[0] has no key"),
            ("a group with no members", [group("c1", None), group("c2", None),
                                         {"key": "g3", "members": [], "primary": c1, "prior_id": None,
                                          "contradicts": None}], [],
             "group 'g3' has no members"),
            ("a group that contradicts itself", [{**group("c1", None), "contradicts": "c1"}, group("c2", None)],
             [], "group 'c1' contradicts 'c1', which is not another group's key"),
            ("an unknown member", [group("c1", None), {**group("c2", None), "members": [c2, ghost]}], [],
             "group 'c2' names claude/c9, which is not in merge-input.json"),
            ("a finding in two groups", [group("c1", None), {**group("c2", None), "members": [c2, c1]}], [],
             "group 'c2' places claude/c1, which group 'c1' already placed"),
            ("a finding grouped and dropped", [group("c1", None), group("c2", None)],
             [{**c1, "duplicate_of": "c2", "reason": "same"}],
             "dropped[0] places claude/c1, which group 'c1' already placed"),
            ("a drop that names no group", [group("c1", None)], [{**c2, "duplicate_of": "g9", "reason": "same"}],
             "dropped[0] is a duplicate_of 'g9', which is not a group's key"),
        ]
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load")])
        for name, groups, dropped, expected in cases:
            with self.subTest(name):
                path = self.round_file(n, "merger-output.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"groups": groups, "dropped": dropped}, f)
                proc = self.run_script("merge-apply", "--decisions", path, check=False)
                self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
                self.assertIn(expected, proc.stderr)
                self.assertFalse(os.path.exists(self.round_file(n, "merged.json")), "merged.json written")

    def test_merge_apply_reports_every_violation_at_once(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load"),
                         finding("c3", 20, "Off-by-one in loop")])
        twin = group("c2", None)
        twin["key"] = "c1"
        proc = self.merge_apply(n, [group("c1", None), twin])
        self.assertNotEqual(0, proc.returncode, "merge-apply exit code")
        self.assertIn("fails 3 check(s)", proc.stderr)
        self.assertIn("1 finding(s) are in no group and not dropped: claude/c3", proc.stderr)

    def test_ledger_apply_refuses_a_merged_file_with_a_repeated_id(self):
        self.ledger_with_one_deferred_finding()
        n = self.review([finding("c1", 10, "Missing null check in parse"),
                         finding("c2", 30, "Unclosed file in load")])
        self.assertEqual(0, self.merge_apply(n, [group("c1", "F-001"), group("c2", None)]).returncode)
        path = self.round_file(n, "merged.json")
        with open(path, encoding="utf-8") as f:
            merged = json.load(f)
        merged["items"][1]["id"] = "F-001"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f)
        fix_report = self.round_file(n, "fix-report.json")
        with open(fix_report, "w", encoding="utf-8") as f:
            json.dump({"decisions": [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}]}, f)
        proc = self.run_script("ledger-apply", "--fix-report", fix_report, check=False)
        self.assertNotEqual(0, proc.returncode, "ledger-apply exit code")
        self.assertIn("more than one item the id F-001", proc.stderr)

    # ------------------------------------------------------------------ verdict

    def test_a_run_whose_last_round_read_a_moving_tree_is_incomplete(self):
        self.start_run(max_rounds=1)
        n = self.review([], digest_end="sha256:" + "0" * 32)
        self.run_script("merge-auto")
        self.assertEqual("reached max_rounds (1)", self.decide(n, [])["stop_reason"])
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("the tree changed while round 1 was being reviewed", notes[0])

    def test_a_round_whose_reviewer_started_after_the_tree_moved_is_stale(self):
        self.start_run(max_rounds=1)
        n = self.review([], digest_start="sha256:" + "0" * 32, digest_end="sha256:" + "0" * 32)
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            self.assertEqual(True, json.load(f)["target"]["stale"])

    def test_a_run_whose_last_round_was_not_merged_is_incomplete(self):
        self.start_run(max_rounds=1)
        self.review([])
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("round 1 was not merged", notes[0])

    def test_a_run_whose_last_round_decisions_were_not_applied_is_incomplete(self):
        self.start_run(max_rounds=1)
        self.review([finding("c1", 10, "Missing null check in parse")])
        self.run_script("merge-auto")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("round 1 was merged, but its decisions were not applied", notes[0])

    def test_a_run_whose_code_changed_after_its_last_round_is_incomplete(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.write("app.py", SOURCE + "edited after the review\n")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("the code changed after round 1 took its snapshot", notes[0])

    def test_a_run_that_gained_an_untracked_file_after_its_last_round_is_incomplete(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.write("added.py", "added after the review\n")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("the code changed after round 1 took its snapshot", notes[0])

    def test_editing_an_ignored_file_after_the_last_round_keeps_the_run_clean(self):
        self.write(".gitignore", "*.log\n")
        self.git("add", ".gitignore")
        self.git("commit", "-q", "-m", "ignore logs")
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.write("build.log", "written after the review\n")
        self.assertEqual(("clean", []), self.report())

    def test_committing_the_reviewed_changes_keeps_the_run_clean(self):
        self.write("app.py", SOURCE + "reviewed edit\n")
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.git("commit", "-q", "-am", "reviewed edit")
        self.assertEqual(("clean", []), self.report())

    def test_a_run_whose_last_round_read_a_still_tree_is_clean(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.assertEqual("no blocking findings", self.decide(n, [])["stop_reason"])
        self.assertEqual(("clean", []), self.report())

    def test_a_round_merged_without_a_stale_key_takes_the_flag_from_merged_json(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        state_path = os.path.join(self.run_dir, "state.json")
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
        del state["rounds"][0]["stale"]
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        self.assertEqual(("clean", []), self.report())


def finding(local_id, line, title, prior_id=None):
    return {"local_id": local_id, "prior_id": prior_id, "severity": "major", "confidence": 0.9,
            "category": "correctness", "title": title, "why": "why", "evidence": "app.py:%d" % line,
            "depends_on_premise": None, "suggestion": "fix it",
            "anchor": {"path": "app.py", "symbol": None, "start_line": line, "end_line": line},
            "introduced_by_diff": True}


def group(local_id, prior_id):
    member = {"reviewer": "claude", "local_id": local_id}
    return {"key": local_id, "members": [member], "primary": member, "prior_id": prior_id, "contradicts": None}


if __name__ == "__main__":
    unittest.main()
