"""Tests for the codeowners-for-bot-updates script, bot_paths.py.

They cover the parts that decide what the generated CODEOWNERS block says:
how a path is matched, which pattern stands for it, which files of a bot PR
count as the bot's, where a rerun puts the block, and which kept paths need
override lines in it. The Matcher tests run git; nothing here calls GitHub.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
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

    def test_a_slash_star_pattern_with_a_wildcard_directory_matches_direct_children_only(self):
        tree = ["apps/ui/config/package.json", "apps/ui/config/nested/package.json", "README.md"]
        self.assertEqual({"apps/ui/config/package.json"}, self.matcher.match("/apps/*/config/*", tree))

    def test_a_root_slash_star_pattern_matches_root_files_only(self):
        self.assertEqual({"go.mod"}, self.matcher.match("/*", TREE))

    def test_a_file_name_matches_case_sensitively(self):
        self.assertEqual({"docker/Dockerfile"},
                         self.matcher.match("Dockerfile", ["docker/Dockerfile", "docker/dockerfile"]))


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

    def test_a_file_whose_last_line_is_the_star_line_gets_the_block_after_it(self):
        got = bot_paths.replace_block("* @owner\n", ["go.mod"])
        self.assertEqual("\n".join(["* @owner", "", bot_paths.BLOCK_BEGIN, bot_paths.BLOCK_COMMENT,
                                    "go.mod", bot_paths.BLOCK_END]) + "\n", got)

    def test_the_block_goes_after_the_star_line_and_before_the_lines_that_follow_it(self):
        got = bot_paths.replace_block("/.github/ @admins\n* @owner\n/docs/ @writers\n", ["go.mod"])
        self.assertEqual("\n".join(["/.github/ @admins", "* @owner", "", bot_paths.BLOCK_BEGIN,
                                    bot_paths.BLOCK_COMMENT, "go.mod", bot_paths.BLOCK_END, "",
                                    "/docs/ @writers"]) + "\n", got)

    def test_a_rerun_moves_a_block_from_the_end_to_after_the_star_line(self):
        old = "\n".join(["* @owner", "/docs/ @writers", "", bot_paths.BLOCK_BEGIN, "go.mod",
                         bot_paths.BLOCK_END]) + "\n"
        got = bot_paths.replace_block(old, ["pom.xml"])
        self.assertEqual("\n".join(["* @owner", "", bot_paths.BLOCK_BEGIN, bot_paths.BLOCK_COMMENT,
                                    "pom.xml", bot_paths.BLOCK_END, "", "/docs/ @writers"]) + "\n", got)

    def test_the_block_goes_after_the_last_of_two_star_lines_and_a_rerun_changes_nothing(self):
        once = bot_paths.replace_block("* @a\n/docs/ @writers\n* @b\n# apps\n/apps/ @apps-team\n", ["go.mod"])
        self.assertEqual("\n".join(["* @a", "/docs/ @writers", "* @b", "", bot_paths.BLOCK_BEGIN,
                                    bot_paths.BLOCK_COMMENT, "go.mod", bot_paths.BLOCK_END, "", "# apps",
                                    "/apps/ @apps-team"]) + "\n", once)
        self.assertEqual(once, bot_paths.replace_block(once, ["go.mod"]), "rerun")

    def test_a_file_without_a_star_line_gets_the_block_at_the_end(self):
        got = bot_paths.replace_block("/docs/ @writers\n", ["go.mod"])
        self.assertEqual("\n".join(["/docs/ @writers", "", bot_paths.BLOCK_BEGIN, bot_paths.BLOCK_COMMENT,
                                    "go.mod", bot_paths.BLOCK_END]) + "\n", got)


class OverrideOwnersTest(unittest.TestCase):
    matcher = bot_paths.Matcher()

    def test_a_path_the_star_line_owns_gets_an_override_and_one_a_later_line_owns_does_not(self):
        text = "* @owner\n/apps/ui/ @ui-team\n"
        got = bot_paths.override_owners(text, self.matcher, ["apps/ui/package.json", "tools/package.json"])
        self.assertEqual({"tools/package.json": ["@owner"]}, got)

    def test_a_rerun_takes_the_owners_from_outside_the_old_block(self):
        text = "\n".join(["/apps/ui/ @web-team", "* @owner", bot_paths.BLOCK_BEGIN, "package.json",
                          "/apps/ui/package.json @ui-team", "/tools/package.json @ui-team",
                          bot_paths.BLOCK_END]) + "\n"
        got = bot_paths.override_owners(text, self.matcher, ["apps/ui/package.json", "tools/package.json"])
        self.assertEqual({"apps/ui/package.json": ["@owner"], "tools/package.json": ["@owner"]}, got,
                         "the override lines of the old block give @ui-team, which no line outside it does")

    def test_without_a_star_line_every_owned_path_gets_an_override(self):
        got = bot_paths.override_owners("/apps/ui/ @ui-team\n", self.matcher, ["apps/ui/package.json"])
        self.assertEqual({"apps/ui/package.json": ["@ui-team"]}, got)

    def test_no_paths_give_no_overrides(self):
        self.assertEqual({}, bot_paths.override_owners("* @owner\n", self.matcher, []))

    def test_a_path_whose_last_matching_line_has_no_owners_gets_no_override(self):
        got = bot_paths.override_owners("* @owner\n/vendor/\n", self.matcher, ["vendor/go.mod"])
        self.assertEqual({}, got)


class CheckVerdictsTest(unittest.TestCase):
    TEXT = "\n".join(["* @owner", bot_paths.BLOCK_BEGIN, "go.mod", bot_paths.BLOCK_END,
                      "/apps/ @apps-team"]) + "\n"

    @staticmethod
    def row(verdict):
        return {"verdict": verdict, "in_tree": True}

    def test_an_ownerless_path_a_line_after_the_block_owns_is_listed_apart_from_the_mismatches(self):
        rows = {"apps/go.mod": self.row("ownerless"), "README.md": self.row("ownerless"),
                "go.mod": self.row("ownerless")}
        current = {"apps/go.mod": (5, "/apps/", ["@apps-team"]), "README.md": (1, "*", ["@owner"]),
                   "go.mod": (3, "go.mod", [])}
        self.assertEqual((["README.md"], ["apps/go.mod"]),
                         bot_paths.check_verdicts(rows, current, self.TEXT))

    def test_without_a_block_an_owned_ownerless_path_is_a_mismatch(self):
        rows = {"apps/go.mod": self.row("ownerless")}
        current = {"apps/go.mod": (2, "/apps/", ["@apps-team"])}
        self.assertEqual((["apps/go.mod"], []),
                         bot_paths.check_verdicts(rows, current, "* @owner\n/apps/ @apps-team\n"))


class WriteTargetTest(unittest.TestCase):
    def test_a_symbolic_link_in_the_clone_is_refused(self):
        with tempfile.TemporaryDirectory() as clone:
            os.mkdir(os.path.join(clone, ".github"))
            os.symlink(os.path.join(clone, "elsewhere"), os.path.join(clone, ".github/CODEOWNERS"))
            with self.assertRaises(ValueError):
                bot_paths.write_target(None, clone, ".github/CODEOWNERS")

    def test_a_regular_file_in_the_clone_is_the_target(self):
        with tempfile.TemporaryDirectory() as clone:
            os.mkdir(os.path.join(clone, ".github"))
            Path(clone, ".github/CODEOWNERS").write_text("* @owner\n")
            self.assertEqual(os.path.join(clone, ".github/CODEOWNERS"),
                             bot_paths.write_target(None, clone, ".github/CODEOWNERS"))

    def test_a_file_named_by_codeowners_is_the_target_even_when_it_is_a_link(self):
        with tempfile.TemporaryDirectory() as d:
            link = os.path.join(d, "CODEOWNERS")
            os.symlink(os.path.join(d, "real"), link)
            self.assertEqual(link, bot_paths.write_target(link, None, ".github/CODEOWNERS"))


if __name__ == "__main__":
    unittest.main()
