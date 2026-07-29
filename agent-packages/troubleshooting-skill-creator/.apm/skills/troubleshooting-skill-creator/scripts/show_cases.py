#!/usr/bin/env python3
"""Print the symptom catalog or one troubleshooting section."""

import sys

with open(sys.argv[1], encoding="utf-8") as catalog:
    lines = catalog.read().splitlines()

section_titles = set()
duplicate_titles = set()
for line in lines:
    if line.startswith("### "):
        title = line[4:]
        if title in section_titles:
            duplicate_titles.add(title)
        section_titles.add(title)

if duplicate_titles:
    raise SystemExit("duplicate section title: " + ", ".join(sorted(duplicate_titles)))

if len(sys.argv) == 2:
    for index, line in enumerate(lines):
        if line == "**Symptoms:**":
            end = lines.index("**Root cause:**", index)
            print("\n".join(lines[index - 2 : end]))
else:
    start = lines.index("### " + sys.argv[2])
    end = start + 1
    while end < len(lines) and not lines[end].startswith(("## ", "### ")):
        end += 1
    print("\n".join(lines[start:end]))
