import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    REPO_ROOT
    / "agent-packages/troubleshooting-skill-creator/.apm/skills/"
    / "troubleshooting-skill-creator"
)
PACKAGE_MANIFEST = REPO_ROOT / "agent-packages/troubleshooting-skill-creator/apm.yml"


class TroubleshootingSkillTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.creator = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.template = (SKILL_ROOT / "references/package-template.md").read_text(
            encoding="utf-8"
        )
        cls.package_manifest = PACKAGE_MANIFEST.read_text(encoding="utf-8")

    def test_package_manifests_omit_optional_author_metadata(self):
        self.assertNotIn("\nauthor:", f"\n{self.package_manifest}")
        self.assertNotIn("\nauthor:", f"\n{self.template}")

    def test_generated_descriptions_include_all_product_names(self):
        self.assertIn("- `<product-names>`", self.template)
        self.assertIn(
            "`OpenTelemetry Collector (OTel Collector, OTEC, Telemetry Collector)`",
            self.template,
        )
        self.assertIn(
            "description: Use when assessing or diagnosing a support ticket involving "
            "<product-names> or its components (<components>)",
            self.template,
        )
        self.assertIn(
            "description: Diagnose installation, configuration, and runtime failures "
            "involving <product-names> or its components (<components>) from a support "
            "ticket, pasted problem description, or attached evidence",
            self.template,
        )

    def test_creator_collects_and_checks_aliases(self):
        self.assertIn(
            "canonical product name and every evidence-backed alias", self.creator
        )
        self.assertIn(
            "description names the canonical product, every evidence-backed alias, and its components",
            self.creator,
        )


if __name__ == "__main__":
    unittest.main()
