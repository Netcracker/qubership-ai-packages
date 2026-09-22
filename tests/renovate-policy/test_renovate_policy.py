import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


class RenovatePolicyTest(unittest.TestCase):
    def test_release_age_comes_from_the_org_config(self):
        # The inherited org config sets the release-age delay and its exemptions (Netcracker packages, APM git-refs
        # through the apm preset). A repository rule would override them for every dependency it matches.
        config = json.loads((ROOT / "renovate.json").read_text())

        release_age_rules = [rule for rule in config["packageRules"] if "minimumReleaseAge" in rule]
        self.assertEqual(release_age_rules, [])

    def test_python_ci_tools_skip_the_weekly_schedule(self):
        config = json.loads((ROOT / "renovate.json").read_text())

        schedules = {
            rule.get("groupName"): rule["schedule"]
            for rule in config["packageRules"]
            if "schedule" in rule
        }
        self.assertEqual(schedules, {"python ci tools": ["at any time"]})

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
        self.assertIn("- renovate.json", marketplace)
        self.assertIn("|renovate\\.json|", marketplace)


if __name__ == "__main__":
    unittest.main()
