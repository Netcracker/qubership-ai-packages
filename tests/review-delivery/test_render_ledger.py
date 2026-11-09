"""render-ledger.py on small review.json files: the order of findings and of their groups, held findings with and
without open code findings, the fields of a previous finding, and the exit status for a file it cannot render."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "review-delivery", ".apm", "skills",
                      "review-delivery", "scripts", "render-ledger.py")


def finding(fid, severity, cls=None, gate="none"):
    """Return a finding whose title is its id, so the ledger's order can be read from the headings."""
    return {"id": fid, "title": f"title {fid}", "kind": "defect", "severity": severity, "confidence": "high",
            "axis": "tests", "class": cls, "gate": gate, "location": None, "problem": "p",
            "proposed_solution": "s"}


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
        self.assertEqual(["### F1 [major] title F1 (tests)", "### F2 [minor] title F2 (tests)",
                          "### F10 [minor] title F10 (tests)"], self.headings(data, "### "))

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

    def test_a_previous_finding_keeps_its_replies_and_follow_up(self):
        data = review([], result="approve", previous_findings=[{
            "thread_url": "https://example.test/t/1", "status": "scope_deferred", "reason": "moved to a follow-up.",
            "reply_urls": ["https://example.test/r/1"], "follow_up_url": "https://example.test/issue/9"}])
        self.assertIn("- https://example.test/t/1: scope_deferred; moved to a follow-up. "
                      "Replies: https://example.test/r/1. Follow-up: https://example.test/issue/9.",
                      self.ledger(data).splitlines())

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
