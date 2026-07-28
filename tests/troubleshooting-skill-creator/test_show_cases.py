import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "agent-packages/troubleshooting-skill-creator/.apm/skills/"
    / "troubleshooting-skill-creator/scripts/show_cases.py"
)

CATALOG = """\
# Widget troubleshooting

## API

### Connection refused

**Symptoms:**

* `connection [refused]`

**Root cause:**

The configured endpoint is unavailable.

### Background

This section is not a case.

### Request timeout

**Symptoms:**

* The request timed out.

**Root cause:**

The upstream did not respond.
"""

DUPLICATE_TITLE_CATALOG = """\
# Widget troubleshooting

## API

### Connection refused

**Symptoms:**

* The API connection is refused.

**Root cause:**

The API is unavailable.

## Database

### Connection refused

**Symptoms:**

* The database connection is refused.

**Root cause:**

The database is unavailable.
"""


class ShowCasesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.catalog = Path(self.temp_dir.name) / "troubleshooting.md"
        self.catalog.write_text(CATALOG, encoding="utf-8")

    def run_script(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_prints_only_case_titles_and_symptoms(self):
        result = self.run_script(str(self.catalog))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "### Connection refused\n\n"
            "**Symptoms:**\n\n"
            "* `connection [refused]`\n\n"
            "### Request timeout\n\n"
            "**Symptoms:**\n\n"
            "* The request timed out.\n\n",
        )

    def test_prints_complete_section_by_title(self):
        result = self.run_script(str(self.catalog), "Connection refused")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "### Connection refused\n\n"
            "**Symptoms:**\n\n"
            "* `connection [refused]`\n\n"
            "**Root cause:**\n\n"
            "The configured endpoint is unavailable.\n\n",
        )

    def test_rejects_duplicate_section_titles(self):
        self.catalog.write_text(DUPLICATE_TITLE_CATALOG, encoding="utf-8")

        result = self.run_script(str(self.catalog))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "duplicate section title: Connection refused\n")


if __name__ == "__main__":
    unittest.main()
