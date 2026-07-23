import copy
import json
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = PACKAGE_ROOT / ".apm/skills/pr-qa-review/scripts/validate-review-package.py"
OID_A = "1" * 40
OID_B = "2" * 40


def png(width=1280, height=720):
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", width, height) + b"\x08\x06\x00\x00\x00"


def valid_state():
    return {
        "schema_version": 1,
        "review_status": "complete",
        "capability_discovery": [
            {"source": "repository-native", "status": "inspected", "evidence": "package scripts"},
            {"source": "harness-tools", "status": "inspected", "evidence": "browser adapter metadata"},
            {"source": "local-executables", "status": "inspected", "evidence": "executable presence"},
            {"source": "local-runtimes", "status": "inspected", "evidence": "configured context names"},
        ],
        "target": {
            "initial_base_oid": OID_A,
            "initial_head_oid": OID_B,
            "final_head_oid": OID_B,
            "status": "current",
        },
        "permissions": [
            {
                "id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "target": "http://review.local",
                "access_mode": "read-only",
                "status": "approved",
                "decision_source": "user",
                "decision_evidence": "User approved browser access for this URL.",
                "allowed_actions": ["navigate", "inspect-console", "inspect-network", "capture-screenshot"],
            }
        ],
        "actions": [
            {
                "id": "open-entry",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "target": "http://review.local",
                "access_mode": "read-only",
                "action": "navigate",
            }
        ],
        "coverage": [
            {
                "id": "web-ui",
                "required": True,
                "status": "complete",
                "impact": "none",
                "evidence_profile": "web-ui",
                "required_slots": [
                    "entry-wide",
                    "changed-wide",
                    "entry-narrow",
                    "changed-narrow",
                    "console",
                    "network",
                    "accessibility",
                    "keyboard",
                ],
            }
        ],
        "checks": [
            {
                "id": "entry-wide",
                "coverage_id": "web-ui",
                "slot": "entry-wide",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["screenshots/entry-wide.png"],
            },
            {
                "id": "changed-wide",
                "coverage_id": "web-ui",
                "slot": "changed-wide",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["screenshots/changed-wide.png"],
            },
            {
                "id": "entry-narrow",
                "coverage_id": "web-ui",
                "slot": "entry-narrow",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["screenshots/entry-narrow.png"],
            },
            {
                "id": "changed-narrow",
                "coverage_id": "web-ui",
                "slot": "changed-narrow",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["screenshots/changed-narrow.png"],
            },
            {
                "id": "console",
                "coverage_id": "web-ui",
                "slot": "console",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["checks/console.txt"],
            },
            {
                "id": "network",
                "coverage_id": "web-ui",
                "slot": "network",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["checks/network.txt"],
            },
            {
                "id": "accessibility",
                "coverage_id": "web-ui",
                "slot": "accessibility",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["checks/accessibility.txt"],
            },
            {
                "id": "keyboard",
                "coverage_id": "web-ui",
                "slot": "keyboard",
                "required": True,
                "status": "satisfied",
                "permission_id": "browser-read",
                "implementation": "chrome-devtools-mcp",
                "owner": "root",
                "owner_can_invoke": True,
                "artifacts": ["checks/keyboard.txt"],
            },
        ],
    }


class ReviewPackageValidatorTest(unittest.TestCase):
    def run_validator(self, mutate=None, omit=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = copy.deepcopy(valid_state())
            if mutate:
                mutate(state)

            (root / "checks").mkdir()
            (root / "screenshots").mkdir()
            artifacts = {
                "screenshots/entry-wide.png": png(),
                "screenshots/changed-wide.png": png(),
                "screenshots/entry-narrow.png": png(390, 844),
                "screenshots/changed-narrow.png": png(390, 844),
                "checks/console.txt": b"no console errors\n",
                "checks/network.txt": b"all requests completed\n",
                "checks/accessibility.txt": b"names and roles inspected\n",
                "checks/keyboard.txt": b"keyboard path completed\n",
            }
            for relative, content in artifacts.items():
                if relative not in omit:
                    (root / relative).write_bytes(content)
            (root / "review-state.json").write_text(json.dumps(state), encoding="utf-8")
            if "report.md" not in omit:
                (root / "report.md").write_text("# QA review\n", encoding="utf-8")

            return subprocess.run(
                ["python3", str(VALIDATOR), str(root)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_complete_package(self):
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("review package valid", result.stdout)

    def test_rejects_unresolved_permission(self):
        result = self.run_validator(lambda state: state["permissions"][0].update(status="unresolved"))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unresolved permission", result.stdout)

    def test_rejects_permission_without_user_decision_evidence(self):
        def mutate(state):
            state["permissions"][0].pop("decision_evidence")

        result = self.run_validator(mutate)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("lacks user decision evidence", result.stdout)

    def test_rejects_complete_review_without_required_coverage(self):
        def mutate(state):
            state["coverage"] = []
            state["checks"] = []

        result = self.run_validator(mutate)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("no required coverage", result.stdout)

    def test_rejects_missing_screenshot(self):
        result = self.run_validator(omit={"screenshots/entry-wide.png"})
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing artifact", result.stdout)

    def test_rejects_missing_report(self):
        result = self.run_validator(omit={"report.md"})
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing report", result.stdout)

    def test_rejects_tmp_artifact(self):
        def mutate(state):
            state["checks"][0]["artifacts"] = ["/tmp/entry-wide.png"]

        result = self.run_validator(mutate)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must be relative", result.stdout)

    def test_rejects_open_required_check(self):
        result = self.run_validator(lambda state: state["checks"][0].update(status="running"))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("non-terminal required check", result.stdout)

    def test_rejects_action_outside_permission_budget(self):
        result = self.run_validator(lambda state: state["actions"][0].update(action="delete-secret"))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("outside permission budget", result.stdout)

    def test_rejects_owner_without_selected_implementation(self):
        result = self.run_validator(lambda state: state["checks"][0].update(owner_can_invoke=False))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot invoke implementation", result.stdout)

    def run_discovery_validator(self, mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = valid_state()
            state["review_status"] = "blocked"
            state["workflow_state"] = "AWAIT_ACCESS_PERMISSION"
            state["target"]["status"] = "preliminary"
            state["permissions"][0].update(
                status="unresolved",
                decision_source=None,
                decision_evidence=None,
            )
            state["actions"] = []
            for row in state["coverage"]:
                row.update(status="blocked", impact="Permission unresolved.")
            for check in state["checks"]:
                check.update(status="planned", artifacts=[])
            if mutate:
                mutate(state)

            (root / "checks").mkdir()
            (root / "screenshots").mkdir()
            (root / "review-state.json").write_text(json.dumps(state), encoding="utf-8")
            (root / "report.md").write_text("# QA review\n", encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--gate", "discovery", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_complete_discovery_ledger(self):
        result = self.run_discovery_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("discovery gate valid", result.stdout)

    def test_discovery_gate_rejects_missing_slot_check(self):
        result = self.run_discovery_validator(lambda state: state["checks"].pop())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing required slot", result.stdout)

    def test_discovery_gate_rejects_check_without_candidate_permission(self):
        result = self.run_discovery_validator(lambda state: state["checks"][0].update(permission_id="missing"))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("has no candidate permission", result.stdout)

    def test_discovery_gate_rejects_missing_capability_source(self):
        result = self.run_discovery_validator(lambda state: state["capability_discovery"].pop())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing capability discovery source", result.stdout)

    def test_discovery_gate_rejects_incomplete_web_ui_profile(self):
        def mutate(state):
            state["coverage"][0]["required_slots"].remove("keyboard")
            state["checks"] = [check for check in state["checks"] if check["slot"] != "keyboard"]

        result = self.run_discovery_validator(mutate)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("web-ui profile is missing required slot", result.stdout)


if __name__ == "__main__":
    unittest.main()
