import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL = PACKAGE_ROOT / ".apm/skills/pr-qa-review/SKILL.md"
RUNTIME = PACKAGE_ROOT / ".apm/skills/pr-qa-review/references/runtime-and-environment.md"
UI = PACKAGE_ROOT / ".apm/skills/pr-qa-review/references/ui-and-user-surfaces.md"


class SkillStateMachineContractTest(unittest.TestCase):
    def test_first_permission_gate_cannot_include_mutation_budgets(self):
        text = SKILL.read_text(encoding="utf-8")
        access_gate = text.split("## State 2: AWAIT_ACCESS_PERMISSION", 1)[1].split(
            "## State 3: INSPECT_APPROVED_RUNTIME", 1
        )[0]
        access_gate = " ".join(access_gate.split())

        self.assertIn("The first review-access permission question MUST NOT include", access_gate)
        self.assertIn("deployment, recovery, rollback, cleanup, or other runtime mutation budget", access_gate)
        self.assertIn("name every concrete selected implementation", access_gate)

    def test_action_budget_requires_completed_runtime_inventory(self):
        text = SKILL.read_text(encoding="utf-8")
        runtime_gate = text.split("## State 3: INSPECT_APPROVED_RUNTIME", 1)[1].split(
            "## State 4: READY", 1
        )[0]

        self.assertIn("Only after the approved inventory is recorded", runtime_gate)
        self.assertIn("existing local developer runtime first", runtime_gate)

    def test_passive_discovery_stops_before_static_review(self):
        text = SKILL.read_text(encoding="utf-8")
        discover = text.split("## State 1: DISCOVER", 1)[1].split(
            "## State 2: AWAIT_ACCESS_PERMISSION", 1
        )[0]
        discover = " ".join(discover.split())

        self.assertIn("STOP passive discovery", discover)
        self.assertIn("Do not perform defect analysis", discover)
        self.assertIn("Static review is an evidence check", discover)
        self.assertIn("MUST NOT read patch hunks", discover)
        self.assertIn("name-status and diff statistics", discover)
        self.assertIn("MUST inventory each relevant local runtime class", discover)
        self.assertIn("Docker contexts, kube-contexts, and kind, minikube, or k3d names", discover)
        self.assertIn("Do not stop after finding the first runtime candidate", discover)
        self.assertIn("--gate discovery", discover)
        self.assertIn("MUST NOT ask the first permission question", discover)
        self.assertIn("Never render a credential-bearing configuration file", discover)
        self.assertIn("names and non-secret metadata", discover)
        self.assertIn("Do not invoke a runtime CLI", discover)
        self.assertIn("capability discovery source", discover)

    def test_domain_references_are_deferred_until_after_permission(self):
        text = SKILL.read_text(encoding="utf-8")
        routing = text.split("## Reference routing", 1)[1].split(
            "## Red flags", 1
        )[0]

        self.assertIn("During `DISCOVER`, read only", routing)
        self.assertIn("After the applicable permission gate", routing)

    def test_permission_contract_is_capability_first_and_product_agnostic(self):
        text = SKILL.read_text(encoding="utf-8")
        access_gate = text.split("## State 2: AWAIT_ACCESS_PERMISSION", 1)[1].split(
            "## State 3: INSPECT_APPROVED_RUNTIME", 1
        )[0]
        access_gate = " ".join(access_gate.split())

        self.assertIn("required capability", access_gate)
        self.assertIn("concrete selected implementation and approved fallback", access_gate)
        self.assertNotIn("Chrome MCP", access_gate)
        self.assertNotIn("Firefox MCP", access_gate)
        self.assertNotIn("repository Playwright", access_gate)

        ui = UI.read_text(encoding="utf-8")
        self.assertIn("no browser or automation product is universally required", ui)
        self.assertNotIn("Playwright", ui)

    def test_missing_capability_can_offer_a_separately_approved_installation(self):
        runtime = RUNTIME.read_text(encoding="utf-8")
        install_gap = runtime.split("## Capability gap", 1)[1].split(
            "## Approved runtime inspection", 1
        )[0]

        self.assertIn("no viable available implementation", install_gap)
        self.assertIn("propose an optional installation plan", install_gap)
        self.assertIn("source and version", install_gap)
        self.assertIn("network access and filesystem writes", install_gap)
        self.assertIn("cleanup or uninstall", install_gap)
        self.assertIn("explicit user approval", install_gap)
        self.assertIn("does not authorize executing", install_gap)
        self.assertIn("Do not invent an installation command", install_gap)

    def test_unrestricted_leaf_cannot_own_sensitive_executable_checks(self):
        text = SKILL.read_text(encoding="utf-8")
        ready = text.split("## State 4: READY", 1)[1].split(
            "## State 5: EXECUTE", 1
        )[0]
        ready = " ".join(ready.split())

        self.assertIn("preserves and enforces the leaf tool boundary", ready)
        self.assertIn("inherited or unrestricted tool surface", ready)
        self.assertIn("keep the check in the main thread", ready)
        self.assertIn("shell, network, browser, scanner, runtime, deployment, or mutation", ready)
        self.assertIn("bounded static reasoning", ready)


if __name__ == "__main__":
    unittest.main()
