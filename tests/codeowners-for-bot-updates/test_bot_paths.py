"""Tests for the codeowners-for-bot-updates script, bot_paths.py.

They cover the parts that decide what the generated CODEOWNERS block says:
how a path is matched, which pattern stands for it, which files of a bot PR
count as the bot's, and how a rerun replaces the block. The Matcher tests run
git; nothing here calls GitHub.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (REPO_ROOT / "agent-packages/codeowners-for-bot-updates/.apm/skills"
          / "codeowners-for-bot-updates/scripts/bot_paths.py")

_spec = importlib.util.spec_from_file_location("bot_paths", SCRIPT)
assert _spec is not None and _spec.loader is not None
bot_paths = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bot_paths)

TREE = [
    ".github/workflows/build.yaml",
    ".github/workflows/nested/reusable.yaml",
    "docs/CODEOWNERS",
    "docs/guide/intro.md",
    "go.mod",
    "tools/go.mod",
]


class MatcherTest(unittest.TestCase):
    matcher = bot_paths.Matcher()

    def test_a_file_name_matches_every_copy_in_the_tree(self):
        self.assertEqual({"go.mod", "tools/go.mod"}, self.matcher.match("go.mod", TREE))

    def test_a_directory_pattern_matches_nested_files(self):
        self.assertEqual({".github/workflows/build.yaml", ".github/workflows/nested/reusable.yaml"},
                         self.matcher.match("/.github/workflows/", TREE))

    def test_a_slash_star_pattern_matches_direct_children_only(self):
        self.assertEqual({"docs/CODEOWNERS"}, self.matcher.match("/docs/*", TREE),
                         "GitHub's /docs/* skips docs/guide/intro.md, where gitignore matches it")


class LastMatchTest(unittest.TestCase):
    def test_an_ownerless_line_after_the_star_line_wins(self):
        rules = bot_paths.parse_codeowners("* @owner\ngo.mod\n")
        got = bot_paths.last_match(rules, bot_paths.Matcher(), ["tools/go.mod", "README.md"])
        self.assertEqual({"tools/go.mod": (2, "go.mod", []), "README.md": (1, "*", ["@owner"])}, got)


class ProposedPatternTest(unittest.TestCase):
    def test_patterns(self):
        for path, want in [
            ("apps/ui/package.json", "package.json"),
            ("apps/x/docker/Dockerfile.native-micro", "*Dockerfile*"),
            ("build-logic/jvm/build.gradle.kts", "*.gradle.kts"),
            (".github/workflows/build.yaml", "/.github/workflows/"),
            (".claude/skills/x/SKILL.md", "/.claude/skills/"),
            ("tools/deploy/values.yaml", "/tools/deploy/values.yaml"),
        ]:
            with self.subTest(path):
                self.assertEqual(want, bot_paths.proposed_pattern(path), "proposed_pattern(%r)" % path)


class IgnorePathRegexTest(unittest.TestCase):
    def test_paths(self):
        for pattern, path, want in [
            ("apps/agent/plugins/*/build.gradle.kts", "apps/agent/plugins/brave/build.gradle.kts", True),
            ("apps/agent/plugins/*/build.gradle.kts", "apps/agent/plugins/a/b/build.gradle.kts", False),
            ("**/node_modules/**", "apps/ui/node_modules/x/package.json", True),
            ("**/node_modules/**", "node_modules/x/package.json", True),
            ("vendor/", "third_party/vendor/go.mod", True),
        ]:
            with self.subTest(pattern=pattern, path=path):
                regex = bot_paths.ignore_path_regex(pattern)
                got = bool(regex.match(path) if regex.pattern.endswith("$") else regex.search(path))
                self.assertEqual(want, got, "ignorePaths %r against %r" % (pattern, path))


def pr(commits, files, **fields):
    nodes = [{"commit": {"oid": oid, "parents": {"totalCount": parents},
                         "author": {"name": name, "user": None}}}
             for oid, name, parents in commits]
    return dict({"number": 1, "commits": {"totalCount": len(nodes), "nodes": nodes},
                 "files": {"totalCount": len(files), "nodes": [{"path": f} for f in files]}},
                **fields)


class BotFilesTest(unittest.TestCase):
    BOTS = {"renovate[bot]"}

    def test_a_pr_with_only_bot_commits_gives_every_file(self):
        p = pr([("a1", "renovate[bot]", 1), ("m1", "Someone", 2)], ["go.mod", "go.sum"])
        with mock.patch.object(bot_paths, "gh_json") as gh:
            self.assertEqual((["go.mod", "go.sum"], False), bot_paths.bot_files("o/r", p, self.BOTS),
                             "a merge commit by someone else changes nothing of its own")
            gh.assert_not_called()

    def test_a_file_only_a_person_changed_is_left_out(self):
        p = pr([("a1", "renovate[bot]", 1), ("b2", "Someone", 1)], ["go.mod", "handler.go"])
        files_of = {"a1": ["go.mod"], "b2": ["go.mod", "handler.go"]}
        with mock.patch.object(bot_paths, "gh_json",
                               side_effect=lambda args: {"f": files_of[args[1].rsplit("/", 1)[1]]}):
            self.assertEqual((["go.mod"], True), bot_paths.bot_files("o/r", p, self.BOTS))


class ClassifyTest(unittest.TestCase):
    def test_kinds(self):
        for name, fields, want in [
            ("renovate automerge setting, merged by a person",
             {"state": "MERGED", "body": "🚦 **Automerge**: Enabled.", "autoMergeRequest": None,
              "mergedBy": {"__typename": "User"}}, "auto"),
            ("github auto-merge", {"state": "MERGED", "body": "", "autoMergeRequest": {"enabledAt": "x"},
                                   "mergedBy": {"__typename": "User"}}, "auto"),
            ("merged by a bot", {"state": "MERGED", "body": "", "autoMergeRequest": None,
                                 "mergedBy": {"__typename": "Bot"}}, "auto"),
            ("merged by a person", {"state": "MERGED", "body": "🚦 **Automerge**: Disabled by config.",
                                    "autoMergeRequest": None, "mergedBy": {"__typename": "User"}},
             "manual"),
            ("open without automerge", {"state": "OPEN", "body": "", "autoMergeRequest": None,
                                        "mergedBy": None}, "open-manual"),
        ]:
            with self.subTest(name):
                self.assertEqual(want, bot_paths.classify(fields))


class VerdictTest(unittest.TestCase):
    IGNORED = [bot_paths.ignore_path_regex("apps/plugins/*/build.gradle.kts")]

    def test_verdicts(self):
        for path, automerged, want in [
            ("go.mod", True, ("ownerless", "automerged")),
            ("go.mod", False, ("ownerless", "merged by hand")),
            ("tools/go.mod", True, ("keep", "--keep")),
            ("apps/plugins/a/build.gradle.kts", True, ("ignored", "in Renovate ignorePaths")),
            ("libs/query/api.go", True, ("keep", "source code")),
            ("libs/query/ui.go", True, ("ownerless", "automerged")),
        ]:
            with self.subTest(path=path, automerged=automerged):
                got = bot_paths.verdict_of(path, automerged, keep={"tools/go.mod"},
                                           ownerless_source={"libs/query/ui.go"},
                                           ignore_res=self.IGNORED)
                self.assertEqual(want, got, "verdict_of(%r, automerged=%s)" % (path, automerged))


class PatternSortTest(unittest.TestCase):
    def test_a_leading_slash_or_star_does_not_decide_the_order(self):
        patterns = ["yarn.lock", "*Dockerfile*", "/.github/workflows/", "go.mod", "*.gradle", "Chart.yaml"]
        self.assertEqual(["/.github/workflows/", "*.gradle", "Chart.yaml", "*Dockerfile*", "go.mod",
                          "yarn.lock"], sorted(patterns, key=bot_paths.pattern_sort_key))


class ReplaceBlockTest(unittest.TestCase):
    def test_a_begin_marker_without_an_end_marker_is_refused(self):
        text = "* @owner\n" + bot_paths.BLOCK_BEGIN + "\ngo.mod\n/docs/ @writers\n"
        with self.assertRaises(ValueError):
            bot_paths.replace_block(text, ["go.mod"])

    def test_a_rerun_with_the_same_patterns_changes_nothing(self):
        once = bot_paths.replace_block("* @owner\n", ["go.mod"])
        self.assertEqual(once, bot_paths.replace_block(once, ["go.mod"]))

    def test_a_file_without_markers_gets_the_block_appended(self):
        got = bot_paths.replace_block("* @owner\n", ["go.mod"])
        self.assertEqual("\n".join(["* @owner", "", bot_paths.BLOCK_BEGIN, bot_paths.BLOCK_COMMENT,
                                    "go.mod", bot_paths.BLOCK_END]) + "\n", got)

    def test_a_rerun_moves_the_block_to_the_end_with_new_patterns(self):
        old = bot_paths.replace_block("* @owner\n", ["go.mod"])
        old = old.replace(bot_paths.BLOCK_END, bot_paths.BLOCK_END + "\n/docs/ @writers")
        got = bot_paths.replace_block(old, ["pom.xml"])
        self.assertEqual("\n".join(["* @owner", "", "/docs/ @writers", "", bot_paths.BLOCK_BEGIN,
                                    bot_paths.BLOCK_COMMENT, "pom.xml", bot_paths.BLOCK_END]) + "\n", got)


if __name__ == "__main__":
    unittest.main()
