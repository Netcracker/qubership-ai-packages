"""Tests for scripts/check-skill-descriptions.py.

The check once measured only single-line YAML scalars. A `description: >-`
block scalar captured the literal `>-` as its value, so the five longest
descriptions in the repository measured 2 characters and the check reported
them as passing. It parses the frontmatter with PyYAML now, so the tests
below treat the reader as a black box: they assert the value a block scalar
folds to, and that an over-long one is reported.

Run them through `make test`, which supplies PyYAML via uv.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/check-skill-descriptions.py"

_spec = importlib.util.spec_from_file_location("check_skill_descriptions", SCRIPT)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def write_skill(directory: Path, frontmatter: str) -> Path:
    """Write a SKILL.md holding the given frontmatter and return its path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "SKILL.md"
    path.write_text(f"---\n{frontmatter}\n---\n\n# Skill\n", encoding="utf-8")
    return path


class ReadDescriptionTest(unittest.TestCase):
    """Every YAML scalar style a SKILL.md may use resolves to its real value."""

    def read(self, frontmatter: str) -> str | None:
        with TemporaryDirectory() as tmp:
            return checker.read_description(
                write_skill(Path(tmp), textwrap.dedent(frontmatter).strip("\n"))
            )

    def test_folded_block_scalar_joins_lines_with_spaces(self):
        self.assertEqual(
            self.read(
                """
                name: demo
                description: >-
                  Use when the branch is ready for review.
                  Covers doc comments and inline comments.
                """
            ),
            "Use when the branch is ready for review. "
            "Covers doc comments and inline comments.",
        )

    def test_folded_block_scalar_keeps_the_break_at_a_blank_line(self):
        self.assertEqual(
            self.read(
                """
                name: demo
                description: >
                  First paragraph.

                  Second paragraph.
                """
            ),
            "First paragraph.\nSecond paragraph.",
        )

    def test_literal_block_scalar_keeps_every_line_break(self):
        self.assertEqual(
            self.read(
                """
                name: demo
                description: |-
                  First line.
                  Second line.
                """
            ),
            "First line.\nSecond line.",
        )

    def test_block_scalar_header_is_not_the_value(self):
        # The regression: `>-` used to be captured and measured as the value.
        description = self.read(
            """
            name: demo
            description: >-
              Structure and content rules for doc comments.
            """
        )
        self.assertNotIn(">", description)
        self.assertEqual(description, "Structure and content rules for doc comments.")

    def test_plain_and_quoted_scalars_still_read_correctly(self):
        self.assertEqual(
            self.read("name: demo\ndescription: Plain value."), "Plain value."
        )
        self.assertEqual(
            self.read("name: demo\ndescription: 'It''s quoted.'"), "It's quoted."
        )
        self.assertEqual(
            self.read('name: demo\ndescription: "Say \\"hello\\"."'), 'Say "hello".'
        )

    def test_frontmatter_that_will_not_parse_is_an_error(self):
        with self.assertRaises(checker.DescriptionError):
            self.read("name: demo\ndescription: *undefined_anchor")

    def test_a_description_that_is_not_text_is_an_error(self):
        # PyYAML reads this as a list, which has a len() that means nothing here.
        with self.assertRaises(checker.DescriptionError):
            self.read("name: demo\ndescription:\n  - first\n  - second")

    def test_frontmatter_without_a_description_reads_as_none(self):
        self.assertIsNone(self.read("name: demo\nlicense: MIT"))


class CheckDescriptionsTest(unittest.TestCase):
    """`main()` measures folded descriptions and fails on an over-long one."""

    def run_check(self, frontmatter: str) -> tuple[int, str, str]:
        """Run main() over a package tree holding one SKILL.md."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root / "agent-packages/demo/.apm/skills/demo",
                textwrap.dedent(frontmatter).strip("\n"),
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            original_root, original_packages = checker.ROOT, checker.PACKAGES_DIR
            checker.ROOT, checker.PACKAGES_DIR = root, root / "agent-packages"
            try:
                with contextlib.ExitStack() as capture:
                    capture.enter_context(contextlib.redirect_stdout(stdout))
                    capture.enter_context(contextlib.redirect_stderr(stderr))
                    status = checker.main()
            finally:
                checker.ROOT, checker.PACKAGES_DIR = original_root, original_packages
        return status, stdout.getvalue(), stderr.getvalue()

    @staticmethod
    def folded_block(length: int) -> str:
        """A `>-` description that folds to exactly `length` characters."""
        words = []
        remaining = length
        # Nine-character words plus the fold's single space make ten per word.
        while remaining > 10:
            words.append("a" * 9)
            remaining -= 10
        words.append("a" * remaining)
        lines = "\n".join(f"  {word}" for word in words)
        return f"name: demo\ndescription: >-\n{lines}"

    def test_the_helper_folds_to_the_requested_length(self):
        for length in (11, 20, 999, checker.LIMIT, checker.LIMIT + 1):
            with self.subTest(length=length), TemporaryDirectory() as tmp:
                path = write_skill(Path(tmp), self.folded_block(length))
                self.assertEqual(len(checker.read_description(path)), length)

    def test_an_over_long_block_scalar_fails_the_check(self):
        over = checker.LIMIT + 25
        status, stdout, stderr = self.run_check(self.folded_block(over))
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn(f"{over} chars (25 over)", stderr)

    def test_a_block_scalar_at_the_limit_passes_the_check(self):
        status, stdout, stderr = self.run_check(self.folded_block(checker.LIMIT))
        self.assertEqual(status, 0, stderr)
        self.assertIn("ok: all 1 skill descriptions", stdout)

    def test_an_unmeasurable_description_fails_instead_of_passing(self):
        # A parse failure reports the file it came from, not a stack trace.
        status, stdout, stderr = self.run_check(
            "name: demo\ndescription: *undefined_anchor"
        )
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("cannot measure", stderr)
        self.assertIn("demo/.apm/skills/demo/SKILL.md", stderr)


if __name__ == "__main__":
    unittest.main()
