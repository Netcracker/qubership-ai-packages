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

PLAN = """# Plan

## Parse the header
Read the length prefix.

```bash
# not a heading
make check
```
Then validate it.

## Cache the result
Store it per connection.
"""


class ReviewRunTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        # init places the run directory under TMPDIR; keep it inside the throwaway tree.
        # The developer's own git config, such as a global core.hooksPath, must not reach the throwaway repo.
        self.env = {**os.environ, "TMPDIR": os.path.join(self.repo, ".git", "tmp"),
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q")
        self.git("config", "user.email", "t")
        self.git("config", "user.name", "t")
        self.write("app.py", SOURCE)
        self.git("add", "app.py")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True, capture_output=True)

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
        self.decide(n, [{"id": "F-001", "kind": "deferred", "rationale": "later", "evidence": "app.py:10",
                            "origin": "preexisting", "follow_up": "issue to fix parse"}])

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
            json.dump({"decisions": [self.fixed("F-001", "removes_cause")]}, f)
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
                              env=self.env, check=True, capture_output=True, encoding="utf-8").stdout.split()

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

    # ------------------------------------------------------------------ families

    def fixed(self, fid, shape, **fields):
        return dict({"id": fid, "kind": "fixed", "fix_shape": shape, "rationale": "r", "evidence": "e"}, **fields)

    def second_finding_at_a_case_fix(self):
        """Round 1 fixes F-001 in parse by adding a case; round 2 files F-002, a new finding in parse."""
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "adds_case", family="which requests act for a user")])
        n = self.review([finding("c2", 20, "Empty user read as absent", symbol="parse")])
        proc = self.merge_apply(n, [group("c2", None)])
        self.assertEqual(0, proc.returncode, proc.stderr)
        return n

    def ledger_apply_fails(self, n, decisions):
        path = self.round_file(n, "fix-report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"decisions": decisions}, f)
        proc = self.run_script("ledger-apply", "--fix-report", path, check=False)
        self.assertNotEqual(0, proc.returncode, "ledger-apply exit code")
        return proc.stderr

    def test_a_fixed_decision_without_a_fix_shape_is_refused(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        stderr = self.ledger_apply_fails(n, [{"id": "F-001", "kind": "fixed", "rationale": "r", "evidence": "e"}])
        self.assertIn("decision for F-001 is fixed but its fix_shape is None", stderr)

    def test_a_finding_at_an_earlier_fix_must_say_whether_it_shares_its_property(self):
        n = self.second_finding_at_a_case_fix()
        stderr = self.ledger_apply_fails(n, [self.fixed("F-002", "removes_cause")])
        self.assertIn("F-002 is at the site of F-001", stderr)

    def test_a_second_case_in_a_family_is_refused(self):
        n = self.second_finding_at_a_case_fix()
        stderr = self.ledger_apply_fails(n, [self.fixed("F-002", "adds_case", same_property=["F-001"],
                                                        family="which requests act for a user")])
        self.assertIn("F-002 adds a case to family 'which requests act for a user', whose fix F-001", stderr)

    def test_a_fix_that_removes_the_cause_is_accepted_in_a_family_that_came_back(self):
        n = self.second_finding_at_a_case_fix()
        applied = self.decide(n, [self.fixed("F-002", "removes_cause", same_property=["F-001"],
                                             family="which requests act for a user")])
        self.assertEqual(["which requests act for a user"], applied["recurring_families"])

    def test_a_blocking_deferral_without_a_follow_up_is_refused(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        stderr = self.ledger_apply_fails(n, [{"id": "F-001", "kind": "deferred", "rationale": "r", "evidence": "e",
                                              "origin": "preexisting"}])
        self.assertIn("F-001 is blocking and deferred without a follow_up", stderr)

    def test_the_report_lists_the_follow_up_of_a_narrowed_fix(self):
        self.start_run(max_rounds=1)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "narrows", family="which requests act for a user",
                                   follow_up="draft issue: compute the acting user in one place")])
        with open(self.emitted("report")["file"], encoding="utf-8") as f:
            self.assertIn("- F-001: draft issue: compute the acting user in one place", f.read())

    def test_redoing_a_round_replaces_its_fix_in_the_family(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "adds_case", family="which requests act for a user")])
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "removes_cause", family="which requests act for a user")])
        with open(os.path.join(self.run_dir, "state.json"), encoding="utf-8") as f:
            family = json.load(f)["families"]["which requests act for a user"]
        self.assertEqual([{"id": "F-001", "round": 1, "shape": "removes_cause"}], family["fixes"])

    def test_the_next_prompt_names_only_the_families_a_case_was_added_to(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse"),
                         finding("c2", 30, "File left open", symbol="load")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "adds_case", family="which requests act for a user"),
                        self.fixed("F-002", "removes_cause", family="which files are closed")])
        n = self.emitted("snapshot")["round"]
        with open(self.round_file(n, "codex-prompt.txt"), encoding="utf-8") as f:
            prompt = f.read()
        self.assertIn("- which requests act for a user (F-001)", prompt)
        self.assertNotIn("which files are closed", prompt)

    def test_a_rejected_refile_keeps_the_earlier_case_fix_in_force(self):
        self.start_run(max_rounds=4)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "adds_case", family="which requests act for a user")])
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        proc = self.merge_apply(n, [group("c1", "F-001")])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.decide(n, [{"id": "F-001", "kind": "rejected", "rationale": "r", "evidence": "e"}])
        n = self.review([finding("c3", 20, "Empty user read as absent", symbol="parse")])
        proc = self.merge_apply(n, [group("c3", None)])
        self.assertEqual(0, proc.returncode, proc.stderr)
        stderr = self.ledger_apply_fails(n, [self.fixed("F-002", "adds_case", same_property=["F-001"],
                                                        family="which requests act for a user")])
        self.assertIn("F-002 adds a case to family 'which requests act for a user', whose fix F-001", stderr)

    def test_redoing_a_round_recorded_without_a_fix_log_drops_its_fixes(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "adds_case", family="which requests act for a user")])
        state_file = os.path.join(self.run_dir, "state.json")
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
        for entry in state["rounds"]:
            del entry["fix_log_before"], entry["families_before"]
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f)
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "removes_cause", family="which requests act for a user")])
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
        self.assertEqual(([("F-001", "removes_cause")], [{"id": "F-001", "round": 1, "shape": "removes_cause"}]),
                         ([(e["id"], e["fix_shape"]) for e in state["fix_log"]],
                          state["families"]["which requests act for a user"]["fixes"]),
                         "(fix_log, the family's fixes) after the redo")

    def test_a_blocking_deferral_without_an_origin_is_refused(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        stderr = self.ledger_apply_fails(n, [{"id": "F-001", "kind": "deferred", "rationale": "r", "evidence": "e",
                                              "follow_up": "issue"}])
        self.assertIn("F-001 is blocking and deferred with origin None", stderr)

    def test_a_correctness_finding_is_not_deferred_as_prose(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        stderr = self.ledger_apply_fails(n, [{"id": "F-001", "kind": "deferred", "rationale": "r", "evidence": "e",
                                              "origin": "prose"}])
        self.assertIn("F-001 is a correctness finding; origin prose is for a docs or style preference", stderr)

    def test_narrowing_the_change_for_a_family_needs_a_follow_up(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        stderr = self.ledger_apply_fails(n, [self.fixed("F-001", "narrows", family="which requests act for a user")])
        self.assertIn("F-001 narrows the change for family 'which requests act for a user' without a follow_up",
                      stderr)

    def test_same_property_names_only_earlier_fixes_at_the_site(self):
        n = self.second_finding_at_a_case_fix()
        stderr = self.ledger_apply_fails(n, [self.fixed("F-002", "removes_cause", same_property=["F-009"],
                                                        family="which requests act for a user")])
        self.assertIn("F-002 lists F-009 in same_property, which is not an earlier fix at its site (F-001)", stderr)

    def test_a_listed_fix_keeps_the_family_it_is_in(self):
        n = self.second_finding_at_a_case_fix()
        stderr = self.ledger_apply_fails(n, [self.fixed("F-002", "removes_cause", same_property=["F-001"],
                                                        family="who acts")])
        self.assertIn("F-002 names family 'who acts', but F-001, which it lists in same_property, is in family "
                      "'which requests act for a user'", stderr)

    def test_a_later_fix_that_removes_the_cause_takes_the_follow_up_off_the_report(self):
        self.start_run(max_rounds=2)
        n = self.review([finding("c1", 10, "Query user ignored", symbol="parse")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "narrows", family="which requests act for a user",
                                   follow_up="draft issue: compute the acting user in one place")])
        n = self.review([finding("c2", 20, "Empty user read as absent", symbol="parse")])
        proc = self.merge_apply(n, [group("c2", None)])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.decide(n, [self.fixed("F-002", "removes_cause", same_property=["F-001"],
                                   family="which requests act for a user")])
        with open(self.emitted("report")["file"], encoding="utf-8") as f:
            self.assertNotIn("draft issue: compute the acting user in one place", f.read())

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
        self.decide(n, [self.fixed("F-001", "removes_cause")])
        self.assertEqual(("clean", []), self.report())

    def test_redoing_a_decided_round_matches_against_the_ledger_from_before_it(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "removes_cause")])
        self.file_report(n, [finding("c1", 10, "Missing null check")])
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        self.assertEqual([("F-001", "new")], [(i["id"], i["state"]) for i in self.items(n)])
        applied = self.decide(n, [self.fixed("F-001", "removes_cause")])
        self.assertEqual((False, None), (applied["stop"], applied["stop_reason"]))

    def test_merging_a_decided_round_again_keeps_its_ids(self):
        self.start_run(max_rounds=3)
        n = self.review([finding("c1", 10, "Missing null check")])
        self.run_script("merge-auto")
        self.decide(n, [self.fixed("F-001", "removes_cause")])
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

    # ------------------------------------------------------------------ documents

    def plan_in_repo(self, name="plan.md", text=PLAN):
        """Write text to docs/<name> in the repository and return its path."""
        os.makedirs(os.path.join(self.repo, "docs"), exist_ok=True)
        self.write("docs/" + name, text)
        return os.path.join(self.repo, "docs", name)

    def group_lines(self, n):
        """Return round n's candidate groups from merge-input.json as (reviewer, start line) lists."""
        with open(self.round_file(n, "merge-input.json"), encoding="utf-8") as f:
            groups = json.load(f)["candidate_groups"]
        return [[(m["reviewer"], m["anchor"]["start_line"]) for m in g["members"]] for g in groups]

    def plan_outside_repo(self):
        """Write PLAN to plan.md in a directory outside the repository and return its path."""
        outside = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside)
        path = os.path.join(outside, "plan.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(PLAN)
        return path

    def start_document_run(self, path, max_rounds=2, legs="claude"):
        self.run_dir = self.emitted("init", "--scope", "file:" + path, "--legs", legs,
                                    "--max-rounds", str(max_rounds))["review_dir"]

    def target(self, n):
        with open(self.round_file(n, "target.json"), encoding="utf-8") as f:
            return json.load(f)

    def codex_stream(self, n, locations):
        """Write round n's codex stream with one finding per (absolute path, line, title) in locations."""
        findings = [{"title": "[P1] " + title, "body": "body", "confidence_score": 0.9, "priority": 1,
                     "code_location": {"absolute_file_path": path, "line_range": {"start": line, "end": line}}}
                    for path, line, title in locations]
        records = [{"type": "session_meta", "payload": {"session_id": "s-1"}},
                   {"type": "event_msg", "payload": {"type": "item_completed", "item": {
                       "type": "ExitedReviewMode", "review_output": {
                           "findings": findings, "overall_correctness": "patch is incorrect",
                           "overall_explanation": "e"}}}}]
        with open(self.round_file(n, "codex.jsonl"), "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(r) + "\n" for r in records))

    def codex_anchors(self, n):
        with open(self.round_file(n, "codex.findings.json"), encoding="utf-8") as f:
            return [(x["anchor"]["path"], x["anchor"]["start_line"], x["anchor"]["symbol"])
                    for x in json.load(f)["findings"]]

    def plan_edited_after_round_one(self):
        """Round 1 fixes F-001 at line 10 of docs/plan.md, the plan's line 10 is rewritten, and round 2 opens."""
        self.start_document_run(self.plan_in_repo())
        n = self.review([finding("c1", 10, "Validation names no limit", symbol="Parse the header",
                                 path="docs/plan.md")])
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "fixed", "fix_shape": "removes_cause",
                         "rationale": "the step names the limit", "evidence": "docs/plan.md:10"}])
        self.write("docs/plan.md", PLAN.replace("Then validate it.", "Then check the length against the limit."))
        return self.emitted("snapshot")["round"]

    def test_init_refuses_a_file_scope_that_names_no_file(self):
        proc = self.run_script("init", "--scope", "file:" + os.path.join(self.repo, "missing.md"), check=False)
        self.assertNotEqual(0, proc.returncode, "init exit code")
        self.assertIn("no such file", proc.stderr)

    def test_snapshot_copies_a_document_inside_the_repository_into_the_round_under_its_repository_path(self):
        self.start_document_run(self.plan_in_repo())
        target = self.target(self.emitted("snapshot")["round"])
        with open(target["document"], encoding="utf-8") as f:
            copy = f.read()
        self.assertEqual(("docs/plan.md", os.path.join(self.run_dir, "rounds", "1", "document", "plan.md"), PLAN),
                         (target["document_label"], target["document"], copy))

    def test_a_document_outside_the_repository_is_labeled_by_its_file_name(self):
        self.start_document_run(self.plan_outside_repo())
        self.assertEqual("plan.md", self.target(self.emitted("snapshot")["round"])["document_label"])

    def test_a_codex_finding_on_the_document_is_anchored_at_its_label_under_the_nearest_heading(self):
        self.start_document_run(self.plan_in_repo(), legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        # Line 10 sits below a fenced "# not a heading" comment; line 13 is in the next section.
        original = os.path.join(os.path.realpath(self.repo), "docs", "plan.md")
        self.codex_stream(n, [(self.target(n)["document"], 10, "Validation names no limit"),
                              (original, 13, "Cache never expires")])
        self.run_script("codex-extract")
        self.assertEqual([("docs/plan.md", 10, "Parse the header"), ("docs/plan.md", 13, "Cache the result")],
                         self.codex_anchors(n))

    def test_findings_on_a_document_pair_only_when_their_lines_overlap(self):
        self.start_document_run(self.plan_in_repo(), legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        plan = os.path.join(os.path.realpath(self.repo), "docs", "plan.md")
        self.codex_stream(n, [(plan, 4, "Prefix width unstated"), (plan, 10, "Validation names no limit")])
        self.run_script("codex-extract")
        # Lines 8 and 10 are in one section and two lines apart, which pairs two findings in code.
        self.file_report(n, [finding("c1", 4, "Prefix width unstated", symbol="Parse the header", path="docs/plan.md"),
                             finding("c2", 8, "Check target unnamed", symbol="Parse the header", path="docs/plan.md")])
        self.run_script("merge-prep")
        self.assertEqual([[("codex", 4), ("claude", 4)], [("codex", 10)], [("claude", 8)]], self.group_lines(n))

    def test_a_codex_finding_in_the_section_of_an_earlier_fix_is_listed_at_its_site(self):
        self.start_document_run(self.plan_in_repo(), legs="codex")
        plan = os.path.join(os.path.realpath(self.repo), "docs", "plan.md")
        n = self.emitted("snapshot")["round"]
        self.codex_stream(n, [(plan, 10, "Validation names no limit")])
        self.run_script("codex-extract")
        self.run_script("merge-prep")
        self.run_script("merge-auto")
        self.decide(n, [{"id": "F-001", "kind": "fixed", "fix_shape": "adds_case", "rationale": "r",
                         "evidence": "docs/plan.md:10", "family": "which inputs the header check covers"}])
        n = self.emitted("snapshot")["round"]
        self.codex_stream(n, [(plan, 4, "Prefix width unstated"), (plan, 13, "Cache never expires")])
        self.run_script("codex-extract")
        self.run_script("merge-prep")
        self.assertEqual({"F-002": ["F-001"]}, self.emitted("merge-auto")["same_site"])

    def test_a_codex_finding_on_an_asciidoc_document_is_anchored_under_the_nearest_heading(self):
        adoc = ("= Plan\n\n== Parse the header\nRead the length prefix.\n\n----\n== not a heading\n----\n"
                "Then validate it.\n\n== Cache the result\nStore it per connection.\n")
        self.start_document_run(self.plan_in_repo("plan.adoc", adoc), legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        # Line 9 sits below a "== not a heading" line inside a listing block; line 12 is in the next section.
        self.codex_stream(n, [(self.target(n)["document"], 9, "Validation names no limit"),
                              (self.target(n)["document"], 12, "Cache never expires")])
        self.run_script("codex-extract")
        self.assertEqual([("docs/plan.adoc", 9, "Parse the header"), ("docs/plan.adoc", 12, "Cache the result")],
                         self.codex_anchors(n))

    def test_findings_on_a_document_with_no_heading_symbol_pair_on_exact_line_overlap(self):
        rst = "Plan\n====\n\nRead the length prefix.\n\nThen validate it.\n\nStore it per connection.\n"
        self.start_document_run(self.plan_in_repo("plan.rst", rst), legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        self.codex_stream(n, [(self.target(n)["document"], 4, "Prefix width unstated"),
                              (self.target(n)["document"], 8, "Cache never expires")])
        self.run_script("codex-extract")
        self.file_report(n, [finding("c1", 4, "Prefix width unstated", symbol="Plan", path="docs/plan.rst"),
                             finding("c2", 6, "Check target unnamed", symbol="Plan", path="docs/plan.rst")])
        self.run_script("merge-prep")
        self.assertEqual([[("codex", 4), ("claude", 4)], [("codex", 8)], [("claude", 6)]], self.group_lines(n))

    def test_markdown_findings_in_a_diff_scope_run_pair_on_nearby_lines_whatever_their_symbols(self):
        notes = self.plan_in_repo("notes.md")
        self.start_run(max_rounds=1, legs="codex,claude")
        n = self.emitted("snapshot")["round"]
        self.codex_stream(n, [(os.path.realpath(notes), 10, "Validation names no limit")])
        self.run_script("codex-extract")
        self.file_report(n, [finding("c1", 12, "Validation names no limit", symbol="Parse the header",
                                     path="docs/notes.md")])
        self.run_script("merge-prep")
        self.assertEqual([[("codex", 10), ("claude", 12)]], self.group_lines(n))

    def test_a_document_over_the_prompt_limit_is_named_in_the_prompt_rather_than_copied(self):
        self.start_document_run(self.plan_in_repo(text="# Plan\n" + "x" * 60001 + "\n"))
        n = self.emitted("snapshot")["round"]
        with open(self.round_file(n, "codex-prompt.txt"), encoding="utf-8") as f:
            prompt = f.read()
        self.assertEqual((True, False), ("Read it at `%s`" % self.target(n)["document"] in prompt, "x" * 100 in prompt),
                         "(prompt names the round's copy, prompt holds the text)")

    def test_snapshot_refuses_an_empty_document(self):
        self.start_document_run(self.plan_in_repo(text="\n"))
        proc = self.run_script("snapshot", check=False)
        self.assertNotEqual(0, proc.returncode, "snapshot exit code")
        self.assertIn("is empty", proc.stderr)

    def test_round_two_writes_the_edits_to_the_document_as_its_fixes_patch(self):
        n = self.plan_edited_after_round_one()
        with open(self.round_file(n, "fixes.patch"), encoding="utf-8") as f:
            changed = [line for line in f.read().splitlines()
                       if line[:1] in "+-" and not line.startswith(("+++", "---"))]
        self.assertEqual(["-Then validate it.", "+Then check the length against the limit."], changed)

    def test_the_round_two_codex_prompt_carries_the_edits_the_ledger_and_the_numbered_document(self):
        n = self.plan_edited_after_round_one()
        with open(self.round_file(n, "codex-prompt.txt"), encoding="utf-8") as f:
            prompt = f.read().splitlines()
        expected = ["--- edits since round 1 ---", "+Then check the length against the limit.",
                    "- [F-001] Validation names no limit - the step names the limit",
                    "   10  Then check the length against the limit."]
        self.assertEqual([], [line for line in expected if line not in prompt], "lines missing from the prompt")

    def test_a_document_edited_outside_the_repository_after_the_last_round_makes_the_run_incomplete(self):
        plan = self.plan_outside_repo()
        self.start_document_run(plan, max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        with open(plan, "a", encoding="utf-8") as f:
            f.write("An edit no round reviewed.\n")
        verdict, notes = self.report()
        self.assertEqual("incomplete", verdict)
        self.assertIn("plan.md changed after round 1 copied it", notes[0])

    def test_a_document_run_whose_document_is_unchanged_since_the_last_round_is_clean(self):
        self.start_document_run(self.plan_outside_repo(), max_rounds=1)
        n = self.review([])
        self.run_script("merge-auto")
        self.decide(n, [])
        self.assertEqual(("clean", []), self.report())


def finding(local_id, line, title, prior_id=None, symbol=None, path="app.py"):
    return {"local_id": local_id, "prior_id": prior_id, "severity": "major", "confidence": 0.9,
            "category": "correctness", "title": title, "why": "why", "evidence": "%s:%d" % (path, line),
            "depends_on_premise": None, "suggestion": "fix it",
            "anchor": {"path": path, "symbol": symbol, "start_line": line, "end_line": line},
            "introduced_by_diff": True}


def group(local_id, prior_id):
    member = {"reviewer": "claude", "local_id": local_id}
    return {"key": local_id, "members": [member], "primary": member, "prior_id": prior_id, "contradicts": None}


if __name__ == "__main__":
    unittest.main()
