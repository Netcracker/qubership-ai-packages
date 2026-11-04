"""check.py prints, for every case under research/change-description-authoring/cases/, what check-output.txt records.

A change to a regex in check.py can move a verdict on a result nobody re-read. This test fails on any such move, so a
reviewer reads the diff of check-output.txt instead of re-running every case by hand. On an intended change,
regenerate the file with `python3 tests/change-description-authoring-cases/test_check_output.py --regenerate` and
commit it with the change.
"""
import difflib
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CASES_DIR = os.path.join("research", "change-description-authoring", "cases")
CHECK = os.path.join(CASES_DIR, "check.py")
GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-output.txt")
HEADER = "=== "
REGENERATE = "python3 tests/change-description-authoring-cases/test_check_output.py --regenerate"


def case_names():
    """Returns the directories under cases/ that hold a README.md, as every case does and a __pycache__ does not."""
    return sorted(d for d in os.listdir(os.path.join(REPO_ROOT, CASES_DIR))
                  if os.path.isfile(os.path.join(REPO_ROOT, CASES_DIR, d, "README.md")))


def run_check(case):
    """Returns what check.py prints for the case, run from the repository root as the cases README says."""
    proc = subprocess.run([sys.executable, CHECK, os.path.join(CASES_DIR, case)], cwd=REPO_ROOT,
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise AssertionError(f"check.py {case} exited with {proc.returncode}:\n{proc.stderr}")
    return proc.stdout


def read_golden():
    """Returns {case: output} from check-output.txt, where each case's output follows a `=== <case>` line."""
    outputs = {}
    case = None
    with open(GOLDEN, encoding="utf-8") as f:
        for line in f:
            if line.startswith(HEADER):
                case = line[len(HEADER):].rstrip("\n")
                outputs[case] = ""
            else:
                outputs[case] += line
    return outputs


def regenerate():
    """Rewrites check-output.txt once every case has run, so a case that fails leaves the file as it was."""
    text = "".join(f"{HEADER}{case}\n{run_check(case)}" for case in case_names())
    with open(GOLDEN, "w", encoding="utf-8") as f:
        f.write(text)


class CheckOutputTest(unittest.TestCase):

    def test_every_case_directory_has_a_recorded_output(self):
        self.assertEqual(case_names(), sorted(read_golden()),
                         f"case directories against check-output.txt; regenerate with: {REGENERATE}")

    def test_each_case_prints_its_recorded_output(self):
        golden = read_golden()
        for case in case_names():
            with self.subTest(case=case):
                expected = golden.get(case, "")
                actual = run_check(case)
                if actual != expected:
                    diff = "".join(difflib.unified_diff(expected.splitlines(True), actual.splitlines(True),
                                                        "check-output.txt", f"check.py {case}"))
                    self.fail(f"check.py output moved; if the change is intended, regenerate with: {REGENERATE}\n"
                              f"{diff}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--regenerate"]:
        regenerate()
    else:
        unittest.main()
