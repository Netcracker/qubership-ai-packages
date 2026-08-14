#!/usr/bin/env python3
"""Fail if any skill's frontmatter `description` is too long.

Claude reads a skill's `description` to decide whether to invoke it, and
truncates it at 1024 characters. A silently clipped description drops the
very trigger phrases that make a skill fire, so we cap every SKILL.md a
little under that hard limit and fail the build before a clipped one ships.

Length is measured in Unicode code points (so an em-dash counts as one),
which matches how the limit is applied. Leading and trailing whitespace is
stripped first, including the newline a clipped block scalar ends with.

The frontmatter goes through a real YAML parse, because the `description`
values in these files use every scalar style: plain, single- and
double-quoted, and folded or literal block scalars (`>`, `>-`, `|`, `|-`).
An earlier version pattern-matched the single-line styles instead, captured
the literal `>-` of a block scalar as the value, and reported the five
longest descriptions in the repository as 2 characters each.

Run via the Makefile, which supplies PyYAML through uv:

    make check-descriptions

PyYAML is pinned in requirements.txt. Nothing needs a global install, but
the script does need an interpreter that can import it, so a bare
`python3 scripts/check-skill-descriptions.py` works only where PyYAML
already exists.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit(
        "error: PyYAML is missing. Run `make check-descriptions`, which supplies "
        "it through uv, or install the pins in requirements.txt."
    )

LIMIT = 1020
ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = ROOT / "agent-packages"

# Matches the YAML frontmatter block at the top of a Markdown file. Finding the
# block is Markdown structure, not YAML, so it stays a pattern match; what the
# block contains is then parsed.
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class DescriptionError(Exception):
    """The frontmatter parses to something this check cannot measure."""


def iter_skill_files() -> list[Path]:
    """Every SKILL.md under agent-packages, including hidden dot-directories."""
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(PACKAGES_DIR):
        if "SKILL.md" in filenames:
            found.append(Path(dirpath) / "SKILL.md")
    return sorted(found)


def read_description(path: Path) -> str | None:
    """Return the `description` value from a SKILL.md frontmatter, or None.

    None means the file has no frontmatter, or none with a `description`.
    A frontmatter that will not parse, or whose `description` is not text,
    raises DescriptionError rather than being measured as something else.
    """
    text = path.read_text(encoding="utf-8")
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match is None:
        return None
    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as error:
        raise DescriptionError(f"the frontmatter is not valid YAML: {error}") from error
    if frontmatter is None:
        return None
    if not isinstance(frontmatter, dict):
        raise DescriptionError("the frontmatter is not a YAML mapping")
    if "description" not in frontmatter:
        return None
    description = frontmatter["description"]
    if not isinstance(description, str):
        raise DescriptionError(
            f"`description` holds {type(description).__name__}, not text"
        )
    return description.strip()


def main() -> int:
    skill_files = iter_skill_files()
    if not skill_files:
        print(f"error: no SKILL.md found under {PACKAGES_DIR}", file=sys.stderr)
        return 1

    violations: list[tuple[Path, int]] = []
    for path in skill_files:
        try:
            description = read_description(path)
        except DescriptionError as error:
            print(
                f"error: cannot measure the `description` in "
                f"{path.relative_to(ROOT)}: {error}",
                file=sys.stderr,
            )
            return 1
        if description is None:
            print(
                f"error: {path.relative_to(ROOT)} has no frontmatter `description`",
                file=sys.stderr,
            )
            return 1
        length = len(description)
        if length > LIMIT:
            violations.append((path, length))

    if violations:
        print(
            f"error: {len(violations)} skill description(s) exceed {LIMIT} characters:",
            file=sys.stderr,
        )
        for path, length in violations:
            print(
                f"  {length} chars ({length - LIMIT} over): {path.relative_to(ROOT)}",
                file=sys.stderr,
            )
        return 1

    print(f"ok: all {len(skill_files)} skill descriptions are within {LIMIT} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
