import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


class RenovatePolicyTest(unittest.TestCase):
    def test_release_age_and_schedule_come_from_the_shared_presets(self):
        # The inherited org config and the shared presets set the release-age delay, its exemptions (Netcracker
        # packages, APM git-refs through the apm preset), and the weekly schedule. A repository setting would
        # override them for every dependency it matches.
        config = json.loads((ROOT / "renovate.json").read_text())

        overrides = [
            (index, key)
            for index, scope in enumerate([config, *config["packageRules"]])
            for key in ("minimumReleaseAge", "schedule")
            if key in scope
        ]
        self.assertEqual(overrides, [])

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
