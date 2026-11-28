"""teeth.py against a throwaway suite, driven through its command line: the verdict it gives a revert, the runs it
refuses to read, and the bytes it puts back."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "cross-review", ".apm", "skills",
                      "cross-review", "scripts", "teeth.py")

# A suite of named tests, each failing "always", "never", or "when-broken" (when app.txt holds the word broken). It
# copies the app.txt it read to seen.bin, writes a JUnit report, and exits 1 when a test failed, or with the exit code
# rules.json forces.
SUITE = """
import json, os
rules = json.load(open("rules.json"))
app = open("app.txt", "rb").read()
open("seen.bin", "wb").write(app)
broken = b"broken" in app
cases = []
for name, when in rules["tests"].items():
    fails = when == "always" or (when == "when-broken" and broken)
    cases.append('<testcase name="%s">%s</testcase>' % (name, "<failure/>" if fails else ""))
os.makedirs("reports", exist_ok=True)
open("reports/TEST-suite.xml", "w").write("<testsuite>%s</testsuite>" % "".join(cases))
raise SystemExit(rules.get("exit", 1 if any("failure" in c for c in cases) else 0))
"""


class TeethTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.write("suite.py", SUITE.encode())

    def write(self, name, data):
        with open(os.path.join(self.dir, name), "wb") as f:
            f.write(data)

    def read(self, name):
        with open(os.path.join(self.dir, name), "rb") as f:
            return f.read()

    def teeth(self, rules, expect=None, find="fixed", replace="broken", edits=None):
        """Run teeth.py with one revert of app.txt, by default "fixed" to "broken"; return (exit code, stdout)."""
        self.write("rules.json", json.dumps(rules).encode())
        revert = {"id": "F-001", "edits": edits or [{"file": "app.txt", "find": find, "replace": replace}]}
        if expect:
            revert["expect"] = expect
        config = {"command": [sys.executable, "suite.py"], "results_glob": "reports/TEST-*.xml", "reverts": [revert]}
        self.write("teeth.json", json.dumps(config).encode())
        proc = subprocess.run([sys.executable, os.path.abspath(SCRIPT), "--config", "teeth.json"], cwd=self.dir,
                              capture_output=True, encoding="utf-8")
        return proc.returncode, proc.stdout

    def test_a_revert_puts_back_the_original_bytes_of_a_crlf_file(self):
        self.write("app.txt", b"fixed\r\nsecond\r\n")
        code, out = self.teeth({"tests": {"regression": "when-broken"}}, expect=["regression"])
        self.assertEqual((0, "teeth"), (code, out.splitlines()[-1].split()[0]), out)
        self.assertEqual(b"fixed\r\nsecond\r\n", self.read("app.txt"))

    def test_a_revert_that_stops_at_an_unmatched_edit_puts_back_the_original_bytes(self):
        self.write("app.txt", b"fixed\r\nsecond\r\n")
        code, out = self.teeth({"tests": {"regression": "when-broken"}},
                               edits=[{"file": "app.txt", "find": "fixed", "replace": "broken"},
                                      {"file": "app.txt", "find": "absent", "replace": "x"}])
        self.assertEqual((1, "PATCH"), (code, out.splitlines()[-1].split()[0]), out)
        self.assertEqual(b"fixed\r\nsecond\r\n", self.read("app.txt"))

    def test_a_line_break_in_an_edit_stands_for_whichever_ending_the_file_has(self):
        # (case, app.txt, find, replace, app.txt the suite reads during the revert)
        cases = [
            ("lf find, crlf file", b"keep\r\nfixed\r\nline\r\n", "fixed\nline", "broken\nline",
             b"keep\r\nbroken\r\nline\r\n"),
            ("lf find, lf file with a stray crlf line", b"stray\r\nfixed\nline\n", "fixed\nline", "broken\nline",
             b"stray\r\nbroken\nline\n"),
            ("lf find spanning mixed endings", b"fixed\r\nline\nend\n", "fixed\nline\nend", "broken\nline\nend",
             b"broken\r\nline\nend\n"),
            ("crlf written in replace", b"fixed\r\nline\r\n", "fixed\nline", "broken\r\nline",
             b"broken\r\nline\r\n"),
            ("replace adds a line to a single-line find", b"fixed\r\nline\r\n", "fixed", "broken\nextra",
             b"broken\r\nextra\r\nline\r\n"),
            ("replace adds a line to an unterminated last line", b"line\r\nfixed", "fixed", "broken\nextra",
             b"line\r\nbroken\r\nextra"),
        ]
        for case, original, find, replace, reverted in cases:
            with self.subTest(case):
                self.write("app.txt", original)
                code, out = self.teeth({"tests": {"regression": "when-broken"}}, expect=["regression"],
                                       find=find, replace=replace)
                self.assertEqual((0, "teeth"), (code, out.splitlines()[-1].split()[0]), out)
                self.assertEqual(reverted, self.read("seen.bin"), "app.txt during the revert")
                self.assertEqual(original, self.read("app.txt"), "app.txt after the restore")

    def test_an_expected_test_that_already_fails_with_the_fix_in_place_is_partial(self):
        self.write("app.txt", b"fixed\n")
        code, out = self.teeth({"tests": {"regression": "always", "unrelated": "when-broken"}},
                               expect=["regression"])
        self.assertEqual((1, "PARTIAL"), (code, out.splitlines()[-1].split()[0]), out)
        self.assertIn("regression already fails with the fix in place", out)

    def test_a_failing_exit_with_no_failed_test_gives_the_baseline_no_result(self):
        self.write("app.txt", b"fixed\n")
        code, out = self.teeth({"tests": {"regression": "when-broken"}, "exit": 3})
        self.assertEqual(2, code, out)
        self.assertIn("baseline: NO RESULT — exit 3, no failed test in the reports", out)

    def test_a_failing_exit_with_a_failed_test_gives_the_baseline_that_failure(self):
        self.write("app.txt", b"fixed\n")
        code, out = self.teeth({"tests": {"flaky": "always", "regression": "when-broken"}}, expect=["regression"])
        self.assertEqual(0, code, out)
        self.assertIn("baseline: 1 already failing, discounted from every verdict: ['flaky']", out)


if __name__ == "__main__":
    unittest.main()
