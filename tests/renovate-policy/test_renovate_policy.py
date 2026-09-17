import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


class RenovatePolicyTest(unittest.TestCase):
    def test_non_apm_automerge_waits_one_day(self):
        config = json.loads((ROOT / "renovate.json").read_text())

        release_age_rules = [
            rule for rule in config["packageRules"] if "minimumReleaseAge" in rule
        ]
        self.assertEqual(
            release_age_rules,
            [
                {
                    "description": "Wait one day before automerging newly released dependencies.",
                    "matchDepTypes": ["!apm"],
                    "matchUpdateTypes": [
                        "minor",
                        "patch",
                        "pin",
                        "digest",
                        "pinDigest",
                    ],
                    "minimumReleaseAge": "1 day",
                }
            ],
        )

    def test_shared_automerge_keeps_apm_manual_and_validates_python_updates(self):
        config = json.loads((ROOT / "renovate.json").read_text())
        extends = config["extends"]

        self.assertIn("github>Netcracker/renovate-config:automerge", extends)
        self.assertLess(
            extends.index("github>Netcracker/renovate-config:automerge"),
            extends.index("github>Netcracker/renovate-config:apm"),
        )
        self.assertNotIn("platformAutomerge", config)
        self.assertFalse(any("automerge" in rule for rule in config["packageRules"]))

        marketplace = (ROOT / ".github/workflows/marketplace.yml").read_text()
        self.assertIn("- Makefile", marketplace)
        self.assertIn("|Makefile|", marketplace)


if __name__ == "__main__":
    unittest.main()
