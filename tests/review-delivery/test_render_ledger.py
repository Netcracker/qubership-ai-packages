"""render-ledger.py on small review.json files: the order of findings and of their groups, held findings with and
without open code findings, findings the change did not make, the fields of a previous finding, and the exit status
for a file it cannot render."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "review-delivery", ".apm", "skills",
                      "review-delivery", "scripts", "render-ledger.py")


def finding(fid, severity, cls=None, gate="none", **extra):
    """Return a finding whose title is its id, so the ledger's order can be read from the headings."""
    data = {"id": fid, "title": f"title {fid}", "kind": "defect", "severity": severity, "confidence": "high",
            "axis": "tests", "class": cls, "gate": gate, "location": None, "problem": "p",
            "proposed_solution": "s"}
    data.update(extra)
    return data


def older(fid, severity, disposition, **extra):
    return finding(fid, severity, origin="preexisting", disposition=disposition, **extra)


def stacked(fid, severity, **extra):
    return finding(fid, severity, origin="stack",
                   introduced_by={"commit": "c1", "request": "https://example.test/pr/0"}, **extra)


def review(findings, **extra):
    data = {"schema_version": 1, "target": {"platform": "github", "url": "https://example.test/pr/1"},
            "revision": {"base": "b", "head": "h"}, "result": "request_changes", "findings": findings}
    data.update(extra)
    return data


class RenderLedgerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def run_script(self, data):
        src = os.path.join(self.dir, "review.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return subprocess.run([sys.executable, SCRIPT, src], capture_output=True, text=True)

    def ledger(self, data):
        result = self.run_script(data)
        self.assertEqual(0, result.returncode, result.stderr)
        with open(os.path.join(self.dir, "ledger.md"), encoding="utf-8") as fh:
            return fh.read()

    def headings(self, data, prefix):
        return [line for line in self.ledger(data).splitlines() if line.startswith(prefix)]

    def test_findings_of_one_severity_are_ordered_by_the_number_in_their_id(self):
        data = review([finding("F10", "minor"), finding("F2", "minor"), finding("F1", "major")])
        self.assertEqual(["### F1 major: title F1 (tests)", "### F2 minor: title F2 (tests)",
                          "### F10 minor: title F10 (tests)"], self.headings(data, "### "))

    def test_groups_are_ordered_by_their_highest_severity_with_unclassed_findings_as_a_group(self):
        data = review([finding("F1", "major"), finding("F2", "nit", cls="C1"), finding("F3", "minor", cls="C2")],
                      classes=[{"id": "C1", "title": "nits"}, {"id": "C2", "title": "minors"}])
        self.assertEqual(["## Findings without a class", "## Class C2: minors", "## Class C1: nits"],
                         self.headings(data, "## "))

    def test_a_branch_request_is_held_while_a_code_finding_is_open(self):
        data = review([finding("F1", "minor"), finding("F2", "nit", gate="code_settled")])
        self.assertEqual(["## Findings without a class", "## Held until the code is settled"],
                         self.headings(data, "## "))

    def test_a_branch_request_is_not_held_when_only_nits_remain(self):
        data = review([finding("F1", "nit"), finding("F2", "nit", gate="code_settled")])
        self.assertEqual(["## Findings without a class"], self.headings(data, "## "))

    def test_an_unaccepted_fix_continued_as_a_nit_does_not_hold_a_branch_request(self):
        data = review([finding("F1", "nit"), finding("F2", "nit", gate="code_settled")], previous_findings=[{
            "thread_url": "https://example.test/t/1", "status": "fix_not_accepted", "reason": "still there.",
            "finding_id": "F1"}])
        self.assertEqual(["## Findings without a class", "## Previous findings"], self.headings(data, "## "))

    def test_an_unaccepted_fix_without_a_finding_holds_a_branch_request(self):
        data = review([finding("F2", "nit", gate="code_settled")], previous_findings=[{
            "thread_url": "https://example.test/t/1", "status": "fix_not_accepted", "reason": "still there."}])
        self.assertEqual(["## Held until the code is settled", "## Previous findings"], self.headings(data, "## "))

    def test_an_unaccepted_fix_naming_a_finding_not_in_the_file_holds_a_branch_request(self):
        data = review([finding("F2", "nit", gate="code_settled")], previous_findings=[{
            "thread_url": "https://example.test/t/1", "status": "fix_not_accepted", "reason": "still there.",
            "finding_id": "F9"}])
        self.assertEqual(["## Held until the code is settled", "## Previous findings"], self.headings(data, "## "))

    def test_a_previous_finding_keeps_its_replies_and_follow_up(self):
        data = review([], result="approve", previous_findings=[{
            "thread_url": "https://example.test/t/1", "status": "scope_deferred", "reason": "moved to a follow-up.",
            "reply_urls": ["https://example.test/r/1"], "follow_up_url": "https://example.test/issue/9"}])
        self.assertIn("- https://example.test/t/1: scope_deferred; moved to a follow-up. "
                      "Replies: https://example.test/r/1. Follow-up: https://example.test/issue/9.",
                      self.ledger(data).splitlines())

    def test_the_result_line_counts_only_the_findings_the_change_makes(self):
        data = review([finding("F1", "minor"), older("F2", "major", "follow_up"), stacked("F3", "major"),
                       older("F4", "major", "extend_scope")], result="approve")
        self.assertIn("Result: APPROVE (0 major, 1 minor, 0 nit)", self.ledger(data))

    def test_findings_the_change_did_not_make_get_their_own_sections(self):
        data = review([finding("F1", "minor"), older("F2", "major", "follow_up"), stacked("F3", "major"),
                       older("F4", "minor", "extend_scope"),
                       older("F5", "nit", "extend_scope", follow_up_url="https://example.test/issues/9")])
        self.assertEqual(["## Findings without a class", "### F1 minor: title F1 (tests)",
                          "### F4 minor, pre-existing: title F4 (tests)", "## Older than this change",
                          "### F2 major, pre-existing: title F2 (tests)",
                          "### F5 nit, pre-existing: title F5 (tests)", "## Made by other requests",
                          "### F3 major: title F3 (tests)"],
                         [line for line in self.ledger(data).splitlines() if line.startswith("##")])

    def test_an_older_defect_left_to_a_follow_up_does_not_hold_a_branch_request(self):
        data = review([older("F1", "major", "follow_up"), stacked("F2", "major"),
                       finding("F3", "nit", gate="code_settled")])
        self.assertNotIn("## Held until the code is settled", self.ledger(data))

    def test_an_older_defect_proposed_for_this_change_holds_a_branch_request(self):
        data = review([older("F1", "minor", "extend_scope"), finding("F2", "nit", gate="code_settled")])
        self.assertIn("## Held until the code is settled", self.ledger(data))

    def test_a_branch_request_the_change_did_not_make_is_rendered_once(self):
        data = review([finding("F1", "minor"), stacked("F2", "nit", gate="code_settled")])
        self.assertEqual(1, self.ledger(data).count("### F2 "))

    def test_an_older_defect_shows_its_commit_and_follow_up(self):
        text = self.ledger(review([older("F1", "minor", "follow_up", introduced_by={"commit": "abc", "request": None},
                                         follow_up_url="https://example.test/issues/9")]))
        self.assertIn("- Introduced by: abc\n- Disposition: follow_up\n- Follow-up: https://example.test/issues/9\n",
                      text)

    def test_a_stack_finding_without_its_request_exits_with_status_2_and_names_it(self):
        result = self.run_script(review([finding("F1", "minor", origin="stack", introduced_by={"commit": "c"})]))
        self.assertEqual(2, result.returncode)
        self.assertIn("findings[0].introduced_by.request", result.stderr)

    def test_an_older_defect_without_a_disposition_exits_with_status_2_and_names_it(self):
        result = self.run_script(review([finding("F1", "minor", origin="preexisting")]))
        self.assertEqual(2, result.returncode)
        self.assertIn("findings[0].disposition", result.stderr)

    def test_a_missing_top_level_field_exits_with_status_2_and_names_it(self):
        data = review([])
        del data["revision"]
        result = self.run_script(data)
        self.assertEqual((2, "render-ledger: missing top-level field 'revision'\n"),
                         (result.returncode, result.stderr))

    def test_a_missing_nested_field_exits_with_status_2_and_names_it(self):
        broken = finding("F1", "major")
        broken["evidence"] = [{"text": "t"}]
        result = self.run_script(review([broken]))
        self.assertEqual((2, "render-ledger: missing field 'basis'\n"), (result.returncode, result.stderr))


if __name__ == "__main__":
    unittest.main()
