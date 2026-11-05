"""review_run.py against a throwaway git repository, driven through its command line: the digest that fences a
reviewer's reading, the ledger ids a round may reuse, how findings are paired, and the verdict a run ends on."""
import json
import os
import shutil
import subprocess
import sys
import signal
import tempfile
import time
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "cross-review", ".apm", "skills",
                      "cross-review", "scripts", "review_run.py")

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

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

    def start_run(self, max_rounds, legs="claude"):
        self.run_dir = self.emitted("init", "--scope", "uncommitted", "--legs", legs,
                                    "--max-rounds", str(max_rounds))["review_dir"]

    def round_file(self, n, name):
        return os.path.join(self.run_dir, "rounds", str(n), name)

    def review(self, findings, digest_start=None, digest_end=None):
        """Open the next round and file a claude report on it, read from the round's own target."""
        n = self.emitted("snapshot")["round"]
        self.file_report(n, findings, digest_start, digest_end)
        self.run_script("merge-prep")
        return n

    def file_report(self, n, findings, digest_start=None, digest_end=None):
        """Write round n's claude report against the round's own target."""
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


    # ------------------------------------------------------------------ pairing

    def test_one_reviewers_nearby_findings_with_one_title_stay_two_items(self):
        self.start_run(max_rounds=1)
        n = self.review([{**finding("c1", 10, "Missing null check"), "why": "request.user is null when anonymous"},
                         {**finding("c2", 13, "Missing null check"), "why": "request.address is null when absent"}])
        self.run_script("merge-auto")
        self.assertEqual(["request.user is null when anonymous", "request.address is null when absent"],
                         [i["why"] for i in self.items(n)])

    def test_one_reviewers_findings_at_one_line_with_one_title_stay_two_items(self):
        self.start_run(max_rounds=1)
        n = self.review([{**finding("c1", 10, "Missing null check"), "why": "request.user is null when anonymous"},
                         {**finding("c2", 10, "Missing null check"), "why": "request.user is null after logout"}])
        self.run_script("merge-auto")
        self.assertEqual(["request.user is null when anonymous", "request.user is null after logout"],
                         [i["why"] for i in self.items(n)])

    def test_a_finding_repeated_word_for_word_is_dropped(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check"), finding("c2", 10, "Missing null check")])
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            prep = json.load(f)
        self.assertEqual(([["c1"]], ["c2"]), ([[m["local_id"] for m in g["members"]] for g in prep["candidate_groups"]],
                                             [x["local_id"] for x in prep["dropped"]]))

    def test_a_report_repeating_a_local_id_degrades_the_round(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Missing null check"), finding("c1", 30, "Unclosed stream")])
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            self.assertEqual(["claude"], json.load(f)["degraded"])

    def test_codex_and_claude_findings_at_one_line_pair_into_one_item_both_reviewers_raised(self):
        self.start_run(max_rounds=1, legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        with open(os.path.join(FIXTURES, "codex-0.163.0-review.jsonl"), encoding="utf-8") as f:
            stream = f.read().replace("{repo}", os.path.realpath(self.repo))
        with open(self.round_file(n, "codex.jsonl"), "w", encoding="utf-8") as f:
            f.write(stream)
        extracted = self.emitted("codex-extract")
        self.assertEqual(("ok", 1, "01a172dc-65a3-7e43-a400-94e49a4993ca"),
                         (extracted["status"], extracted["findings"], extracted["session_id"]))
        self.file_report(n, [finding("c1", 10, "request.user may be null")])
        self.run_script("merge-prep")
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            groups = json.load(f)["candidate_groups"]
        self.assertEqual([["codex", "claude"]], [[m["reviewer"] for m in g["members"]] for g in groups])
        self.run_script("merge-apply", "--decisions", self.merger_output(n, groups))
        self.assertEqual([("both", True)], [(i["agreement"], i["blocking"]) for i in self.items(n)])

    def test_codex_extract_quotes_codex_stderr_when_the_stream_holds_no_review(self):
        self.start_run(max_rounds=1, legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        with open(self.round_file(n, "codex.stderr"), "w", encoding="utf-8") as f:
            f.write("bash: timeout: command not found\n")
        extracted = self.emitted("codex-extract")
        self.assertEqual("failed", extracted["status"])
        self.assertIn("timeout: command not found", extracted["note"])

    def test_codex_cmd_bounds_codex_with_python_rather_than_coreutils_timeout(self):
        self.start_run(max_rounds=1, legs="codex,claude")
        self.run_script("snapshot")
        command = self.run_script("codex-cmd").stdout
        wrapper, rest = command.split(" 1800 ", 1)
        self.assertEqual(("python3 -c", "codex exec "), (wrapper[:len("python3 -c")], rest[:len("codex exec ")]))
        started = time.monotonic()
        proc = subprocess.run(wrapper + " 1 sleep 30", shell=True, capture_output=True)
        self.assertEqual(-signal.SIGALRM, proc.returncode, "exit of the wrapper around sleep 30 with a 1 s deadline")
        self.assertLess(time.monotonic() - started, 10, "seconds until the wrapper ended sleep 30")

    def merger_output(self, n, groups):
        """Write a merger output that keeps merge-prep's groups as they are, and return its path."""
        path = self.round_file(n, "merger-output.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"groups": [{"key": g["key"], "members": [{"reviewer": m["reviewer"], "local_id": m["local_id"]}
                                                                for m in g["members"]],
                                   "primary": {"reviewer": g["members"][0]["reviewer"],
                                               "local_id": g["members"][0]["local_id"]},
                                   "prior_id": None, "contradicts": None} for g in groups],
                       "dropped": []}, f)
        return path

    # ------------------------------------------------------------------ run lifecycle

    def test_init_refuses_while_the_pointer_names_an_active_run(self):
        self.start_run(max_rounds=1)
        proc = self.run_script("init", "--scope", "uncommitted", check=False)
        self.assertNotEqual(0, proc.returncode, "init exit code")
        self.assertIn("pass --force to replace it", proc.stderr)

    def test_init_with_force_replaces_an_active_run(self):
        self.start_run(max_rounds=1)
        first = self.run_dir
        self.run_dir = self.emitted("init", "--scope", "uncommitted", "--force")["review_dir"]
        self.assertNotEqual(first, self.run_dir, "run directory of the replacing run")
        self.assertEqual(self.run_dir, self.emitted("status")["review_dir"])

    def test_init_starts_a_new_run_once_the_previous_one_stopped(self):
        self.start_run(max_rounds=1)
        self.run_script("stop", "--reason", "done")
        self.run_script("init", "--scope", "uncommitted")

    def snapshot_refs(self):
        return subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/cross-review/"], cwd=self.repo,
                              check=True, capture_output=True, encoding="utf-8").stdout.split()

    def test_a_clean_report_deletes_every_snapshot_ref_of_the_run(self):
        self.start_run(max_rounds=2)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "rejected", "rationale": "r", "evidence": "e"}])
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.assertEqual(2, len(self.snapshot_refs()), "snapshot refs before report")
        self.assertEqual(("clean", []), self.report())
        self.assertEqual([], self.snapshot_refs())
        self.assertEqual(("clean", []), self.report())

    def test_an_unfinished_report_keeps_only_the_last_rounds_snapshot_ref(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "rejected", "rationale": "r", "evidence": "e"}])
        self.review([])
        self.assertEqual("incomplete", self.report()[0])
        self.assertEqual([r for r in self.snapshot_refs() if r.endswith("/r2")], self.snapshot_refs())
        self.assertEqual(1, len(self.snapshot_refs()), "snapshot refs left")

    # ------------------------------------------------------------------ verdict

    def test_rebuilding_a_decided_merge_makes_the_run_incomplete_until_its_decisions_are_applied(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.file_report(n, [finding("c1", 10, "Missing null check")])
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("round 1 was merged, but its decisions were not applied", notes[0])
        self.decide(n, [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}])
        self.assertEqual(("clean", []), self.report())

    def test_redoing_a_decided_round_matches_against_the_ledger_from_before_it(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}])
        self.file_report(n, [finding("c1", 10, "Missing null check")])
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        self.assertEqual([("F-001", "new")], [(i["id"], i["state"]) for i in self.items(n)])
        applied = self.decide(n, [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}])
        self.assertEqual((False, None), (applied["stop"], applied["stop_reason"]))

    def test_merging_a_decided_round_again_keeps_its_ids(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}])
        self.run_script("merge-auto")
        self.assertEqual([("F-001", "new")], [(i["id"], i["state"]) for i in self.items(n)])

    def test_a_decided_round_that_a_later_round_followed_cannot_be_redone(self):
        self.start_run(max_rounds=3)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.review([])
        proc = self.run_script("merge-prep", "1", check=False)
        self.assertNotEqual(0, proc.returncode, "merge-prep 1 exit code")
        self.assertIn("round 1 is not the last round (round 2 is)", proc.stderr)

    def test_a_report_edited_after_merge_prep_makes_the_run_incomplete(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.file_report(n, [finding("c1", 10, "Missing null check")])
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("claude.findings.json is not the file merge-prep read in round 1", notes[0])

    def test_a_merged_file_edited_after_ledger_apply_makes_the_run_incomplete(self):
        self.start_run(max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        with open(self.round_file(n, "merged.json"), "a", encoding="utf-8") as f:
            f.write("\n")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("merged.json is not the file ledger-apply read in round 1", notes[0])

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
