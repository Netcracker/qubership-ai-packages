"""findings-csv.py on a one-finding dossier: a triage decision may be entered in findings.csv or in findings.jsonl
between two runs, and neither run may erase it."""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "deep-review", ".apm", "skills",
                      "deep-review", "scripts", "findings-csv.py")

README = """# Ревью
<!-- BEGIN generated:standalone -->
<!-- END generated:standalone -->
<!-- BEGIN generated:components -->
<!-- END generated:components -->
"""


class FindingsCsvTest(unittest.TestCase):
    def setUp(self):
        self.dossier = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dossier)
        for d in ("reports", "issues", "work"):
            os.mkdir(os.path.join(self.dossier, d))
        self.write("reports/security.md", '<a id="sec-01"></a>\n### SEC-01\n')
        self.write("README.md", README)
        self.write_finding(verdict="")
        self.assertEqual(0, self.script().returncode)

    def write(self, name, text):
        with open(os.path.join(self.dossier, name), "w", encoding="utf-8") as f:
            f.write(text)

    def write_finding(self, verdict, fid="SEC-01", merged=()):
        ids = [fid, *merged]
        finding = {"id": fid, "sources": [{"axis": "security", "id": i} for i in ids], "priority": "plan",
                   "severity": "HIGH", "confidence": "PLAUSIBLE", "title": "t", "verdict": verdict,
                   "rejection_reason": ""}
        self.write("findings.jsonl", json.dumps(finding) + "\n")

    def set_csv_verdict(self, verdict):
        path = os.path.join(self.dossier, "findings.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[0]["verdict"] = verdict
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    def jsonl_verdict(self):
        with open(os.path.join(self.dossier, "findings.jsonl"), encoding="utf-8") as f:
            return json.loads(f.readline())["verdict"]

    def csv_verdict(self):
        with open(os.path.join(self.dossier, "findings.csv"), encoding="utf-8") as f:
            return next(csv.DictReader(f))["verdict"]

    def script(self, *args):
        return subprocess.run([sys.executable, os.path.abspath(SCRIPT), self.dossier, *args], capture_output=True,
                              encoding="utf-8")

    def test_a_decision_entered_in_findings_jsonl_is_written_into_the_csv(self):
        self.write_finding(verdict="fix")
        done = self.script()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("fix", self.csv_verdict())

    def test_a_decision_entered_in_findings_jsonl_survives_an_import(self):
        self.write_finding(verdict="fix")
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("fix", self.jsonl_verdict())

    def test_a_decision_entered_in_the_csv_stops_a_build_until_imported(self):
        self.set_csv_verdict("backlog")
        self.assertEqual(1, self.script().returncode)
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("backlog", self.jsonl_verdict())

    def test_a_decision_cleared_in_the_csv_after_an_import_is_imported_too(self):
        self.set_csv_verdict("fix")
        self.assertEqual(0, self.script("--import-csv").returncode)
        self.set_csv_verdict("")
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("", self.jsonl_verdict())

    def test_a_decision_changed_twice_in_the_csv_is_not_a_conflict(self):
        self.set_csv_verdict("fix")
        self.assertEqual(0, self.script("--import-csv").returncode)
        self.set_csv_verdict("backlog")
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("backlog", self.jsonl_verdict())

    def test_a_finding_decided_differently_in_both_files_is_left_for_a_person(self):
        self.write_finding(verdict="reject")
        self.set_csv_verdict("fix")
        done = self.script("--import-csv")
        self.assertEqual(1, done.returncode)
        self.assertIn("SEC-01: findings.csv ('fix', ''), findings.jsonl ('reject', '')", done.stderr)
        self.assertEqual("reject", self.jsonl_verdict())

    def test_without_the_base_file_a_disagreement_is_not_resolved_in_either_direction(self):
        os.remove(os.path.join(self.dossier, "work", "findings-csv.base.json"))
        self.write_finding(verdict="fix")
        done = self.script()
        self.assertEqual(1, done.returncode)
        self.assertIn("findings-csv.base.json is missing", done.stderr)
        self.assertEqual("", self.csv_verdict())

    def test_a_csv_decision_on_a_finding_merged_into_another_line_lands_on_that_line(self):
        self.set_csv_verdict("fix")
        self.write_finding(verdict="", fid="SEC-02", merged=["SEC-01"])
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual("fix", self.jsonl_verdict())

    def test_a_csv_decision_on_a_finding_no_line_carries_is_reported(self):
        self.set_csv_verdict("fix")
        self.write_finding(verdict="", fid="SEC-02")
        done = self.script("--import-csv")
        self.assertEqual(1, done.returncode)
        self.assertIn("SEC-01: findings.csv ('fix', ''), findings.jsonl has no line with this id", done.stderr)

    def test_two_imports_without_the_base_file_record_a_base(self):
        os.remove(os.path.join(self.dossier, "work", "findings-csv.base.json"))
        self.assertEqual(0, self.script("--import-csv").returncode)
        done = self.script("--import-csv")
        self.assertEqual(0, done.returncode, done.stderr)

    def test_refuses_to_write_the_csv_through_a_symbolic_link(self):
        outside = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        os.remove(os.path.join(self.dossier, "findings.csv"))
        os.symlink(os.path.join(outside, "stolen.csv"), os.path.join(self.dossier, "findings.csv"))
        done = self.script()
        self.assertNotEqual(0, done.returncode)
        self.assertIn("is a symbolic link", done.stderr)
        self.assertEqual([], os.listdir(outside))


if __name__ == "__main__":
    unittest.main()
