import json
import subprocess
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = PACKAGE_ROOT / ".apm/skills/pr-qa-review/scripts/init-review-package.py"
OID_A = "a" * 40
OID_B = "b" * 40


class ReviewPackageInitializerTest(unittest.TestCase):
    def test_creates_durable_review_package_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "artifacts"
            command = [
                "python3",
                str(INITIALIZER),
                str(root),
                "--base-oid",
                OID_A,
                "--head-oid",
                OID_B,
            ]

            created = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            self.assertTrue((root / "checks").is_dir())
            self.assertTrue((root / "screenshots").is_dir())
            self.assertTrue((root / "report.md").is_file())
            state = json.loads((root / "review-state.json").read_text(encoding="utf-8"))
            self.assertEqual("blocked", state["review_status"])
            self.assertEqual("DISCOVER", state["workflow_state"])
            self.assertEqual([], state["capability_discovery"])
            self.assertEqual(OID_A, state["target"]["initial_base_oid"])
            self.assertEqual(OID_B, state["target"]["initial_head_oid"])

            (root / "report.md").write_text("user edit\n", encoding="utf-8")
            repeated = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(0, repeated.returncode)
            self.assertIn("already exists", repeated.stdout)
            self.assertEqual("user edit\n", (root / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
