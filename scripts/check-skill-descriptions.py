#!/usr/bin/env python3
"""Fail if any skill's frontmatter `description` is too long.

Claude reads a skill's `description` to decide whether to invoke it, and
truncates it at 1024 characters. A silently clipped description drops the
very trigger phrases that make a skill fire, so we cap every SKILL.md a
little under that hard limit and fail the build before a clipped one ships.

Length is measured in Unicode code points (so an em-dash counts as one),
which matches how the limit is applied.

Run via the Makefile (`make check-descriptions`) or directly:

    python3 scripts/check-skill-descriptions.py

No third-party libraries required.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

LIMIT = 1020
ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = ROOT / "agent-packages"

# Matches the YAML frontmatter block at the top of a Markdown file.
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Matches the description value, including common YAML quoting styles:
#   description: unquoted text
#   description: 'single-quoted text'
#   description: "double-quoted text"
# Multi-line YAML block scalars (| or >) are not used in these files.
_DESC_RE = re.compile(
    r"^description:[ \t]*"
    r"(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|(.*?))\s*$",
    re.MULTILINE,
)


def iter_skill_files() -> list[Path]:
    """Every SKILL.md under agent-packages, including hidden dot-directories."""
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(PACKAGES_DIR):
        if "SKILL.md" in filenames:
            found.append(Path(dirpath) / "SKILL.md")
    return sorted(found)


def read_description(path: Path) -> str | None:
    """Return the `description` value from a SKILL.md frontmatter, or None."""
    text = path.read_text(encoding="utf-8")
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match is None:
        return None
    desc_match = _DESC_RE.search(fm_match.group(1))
    if desc_match is None:
        return None
    # Groups: 1 = single-quoted, 2 = double-quoted, 3 = unquoted
    value = desc_match.group(1) or desc_match.group(2) or desc_match.group(3) or ""
    return value.strip()


def main() -> int:
    skill_files = iter_skill_files()
    if not skill_files:
        print(f"error: no SKILL.md found under {PACKAGES_DIR}", file=sys.stderr)
        return 1

    violations: list[tuple[Path, int]] = []
    for path in skill_files:
        description = read_description(path)
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
