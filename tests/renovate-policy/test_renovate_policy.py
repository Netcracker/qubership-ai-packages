import json
import re
import unittest
from pathlib import Path, PurePosixPath

import yaml


ROOT = Path(__file__).parents[2]

# A dependency pinned to the commit of a release tag, with the tag in a comment after one or more spaces. The tag is
# v1.2.3, 1.2.3, or <name>-v1.2.3, the forms Renovate's apm manager looks up as a version.
RELEASE_PIN = re.compile(r"[^\s#@]+#[0-9a-f]{40}\s+#\s*(?:\S+[-_]v|v?)\d+\.\d+\.\d+")

# Packages with no release yet, each still on an unmerged feat/agent-packages branch
# (Netcracker/qubership-core-lib-go#109, Netcracker/qubership-core-lib-go-fiber-server-utils#86,
# Netcracker/qubership-core-base-images#184). Once a repository releases its package, pin the commit of the release tag
# with the tag in a comment, and remove the entry.
UNRELEASED_DEPENDENCIES = {
    "Netcracker/qubership-core-lib-go/logging/agent-packages/logging-go-usage",
    "Netcracker/qubership-core-lib-go/memlimit/agent-packages/memlimit-go-usage",
    "Netcracker/qubership-core-lib-go/context-propagation/agent-packages/context-propagation-go-usage",
    "Netcracker/qubership-core-lib-go/security/agent-packages/security-go-usage",
    "Netcracker/qubership-core-lib-go-fiber-server-utils/agent-packages/fiber-server-utils-go-usage",
    "Netcracker/qubership-core-base-images/agent-packages/qubership-dockerfile-usage",
}


class RenovatePolicyTest(unittest.TestCase):
    maxDiff = None
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

    def test_a_dependency_on_another_repository_pins_a_sha_with_a_release_tag_comment(self):
        # Renovate's apm manager updates the SHA and the tag of such a pin together, and tests/marketplace_roundtrip.sh
        # rejects a ref that is not a SHA. The test checks the form only: Renovate gives a SHA that is not the commit of
        # its tag a digest update.
        unpinned, unreleased = [], set()
        for manifest in sorted((ROOT / "agent-packages").glob("*/apm.yml")):
            text = manifest.read_text()
            package = yaml.safe_load(text)
            for section in ("dependencies", "devDependencies"):
                for dependency in (package.get(section) or {}).get("apm") or []:
                    if dependency.startswith("../"):
                        continue
                    # YAML drops the comment, so the entry is read from the line that holds the dependency.
                    line = re.search(rf"^\s*-\s+({re.escape(dependency)}.*?)\s*$", text, re.MULTILINE)
                    self.assertIsNotNone(line, f"{manifest.relative_to(ROOT)}: no line holds {dependency}")
                    path = dependency.partition("#")[0]
                    if RELEASE_PIN.fullmatch(line[1]):
                        continue
                    if path in UNRELEASED_DEPENDENCIES:
                        unreleased.add(path)
                    else:
                        unpinned.append(f"{manifest.relative_to(ROOT)}: {line[1]}")
        self.assertEqual(
            {"not pinned as #<sha> # <tag>": [], "listed in UNRELEASED_DEPENDENCIES but released or gone": []},
            {
                "not pinned as #<sha> # <tag>": unpinned,
                "listed in UNRELEASED_DEPENDENCIES but released or gone": sorted(UNRELEASED_DEPENDENCIES - unreleased),
            },
        )

    def test_only_a_sha_with_a_release_tag_comment_is_a_release_pin(self):
        dependency = "Netcracker/qubership-workflow-hub/agent-packages/qubership-workflow-hub-usage"
        sha = "e6afd0a6bcc4f24d73e3e4d5fb9a31ada009e3f1"
        cases = {
            # The line Renovate's apm manager writes on an update, with one space before the comment.
            f"{dependency}#{sha} # v2.8.3": True,
            f"{dependency}#{sha}  # v2.8.2": True,
            f"{dependency}#{sha}  # 2.8.2": True,
            f"{dependency}#{sha}  # qubership-workflow-hub-usage-v1.0.0": True,
            # The line the shared preset's regex manager writes on an update.
            f"{dependency}#v2.8.3": False,
            f"{dependency}#{sha}  # main": False,
            f"{dependency}#{sha}": False,
            f"{dependency}#{sha[:39]}  # v2.8.2": False,
            f"{dependency}@v2.8.2": False,
            dependency: False,
        }
        for entry, expected in cases.items():
            with self.subTest(entry=entry):
                self.assertEqual(expected, bool(RELEASE_PIN.fullmatch(entry)))

    def test_the_preset_regex_manager_is_off_for_package_manifests_only(self):
        # The shared apm preset's regex manager writes #<new tag> over #<sha>  # <tag> and drops the SHA. The root
        # apm.yml keeps the manager, because only its marketplace regexes update the marketplace entries there.
        config = json.loads((ROOT / "renovate.json").read_text())
        globs = [
            glob
            for rule in config["packageRules"]
            if rule.get("matchManagers") == ["custom.regex"] and rule.get("enabled") is False
            for glob in rule.get("matchFileNames", [])
        ]
        manifests = [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "agent-packages").glob("*/apm.yml"))]
        turned_off = {
            manifest: any(PurePosixPath(manifest).full_match(glob) for glob in globs)
            for manifest in [*manifests, "apm.yml"]
        }
        self.assertEqual({**dict.fromkeys(manifests, True), "apm.yml": False}, turned_off)


if __name__ == "__main__":
    unittest.main()
