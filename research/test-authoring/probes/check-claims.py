"""Check every claims.tsv under probes/ against the golden files and against the reference it cites.

A row is broken when its pattern is not (or, for ``absent``, is) in the probe's golden file, or when its quote is no
longer in the reference file. Exit 1 lists every broken row; the notes that begin with ``contradicts:`` or
``refines:`` are printed as a summary either way. The ledger format is in README.md.
"""

import re
import sys
from pathlib import Path

PROBES = Path(__file__).resolve().parent
SKILL = PROBES.parents[2] / "agent-packages/test-authoring/.apm/skills/test-authoring"
COLUMNS = ["id", "probe", "check", "pattern", "reference", "quote", "note"]


def unescape(pattern: str) -> str:
    return pattern.encode().decode("unicode_escape")


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def check_row(eco: Path, row: dict[str, str]) -> list[str]:
    problems = []
    golden = eco / "expected" / f"{row['probe']}.txt"
    if not golden.exists():
        return [f"no golden file {golden.relative_to(PROBES)}"]
    output = golden.read_text()
    kind, pattern = row["check"], row["pattern"]
    if kind == "contains":
        found = unescape(pattern) in output
    elif kind in ("regex", "absent"):
        found = re.search(pattern, output) is not None
    else:
        return [f"unknown check kind {kind!r}"]
    if kind == "absent" and found:
        problems.append(f"{golden.name} contains /{pattern}/, which the claim says is absent")
    elif kind != "absent" and not found:
        problems.append(f"{golden.name} lacks {pattern!r}")
    reference = SKILL / row["reference"]
    if not reference.exists():
        problems.append(f"no reference file {row['reference']}")
    elif squash(row["quote"]) not in squash(reference.read_text()):
        problems.append(f"{row['reference']} no longer contains the quote {row['quote']!r}")
    return problems


def main() -> int:
    broken = 0
    notes = []
    cited = set()
    ledgers = sorted(PROBES.glob("*/claims.tsv"))
    if not ledgers:
        print("no claims.tsv under", PROBES)
        return 1
    for ledger in ledgers:
        eco = ledger.parent
        lines = ledger.read_text().splitlines()
        if lines[0].split("\t") != COLUMNS:
            print(f"{ledger.relative_to(PROBES)}: header must be {COLUMNS}")
            return 1
        ids = set()
        for number, line in enumerate(lines[1:], start=2):
            cells = line.split("\t")
            if len(cells) != len(COLUMNS):
                print(f"{ledger.relative_to(PROBES)}:{number}: {len(cells)} columns, expected {len(COLUMNS)}")
                broken += 1
                continue
            row = dict(zip(COLUMNS, cells))
            if row["id"] in ids:
                print(f"{ledger.relative_to(PROBES)}:{number}: duplicate id {row['id']}")
                broken += 1
            ids.add(row["id"])
            cited.add(eco / "expected" / f"{row['probe']}.txt")
            for problem in check_row(eco, row):
                print(f"{eco.name}/{row['id']}: {problem}")
                broken += 1
            if row["note"].startswith(("contradicts:", "refines:")):
                notes.append(f"{eco.name}/{row['id']} ({row['reference']}): {row['note']}")
        print(f"{eco.name}: {len(ids)} claims checked")
    for golden in sorted(PROBES.glob("*/expected/*.txt")):
        if golden not in cited:
            print(f"note: {golden.relative_to(PROBES)} is cited by no claim")
    if notes:
        print("\nMeasurements that contradict or refine the reference:")
        for note in notes:
            print(f"  {note}")
    if broken:
        print(f"\n{broken} broken claim(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
