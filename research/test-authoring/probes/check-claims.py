"""Check every claims.tsv under probes/ against the golden files and against the reference it cites.

A row is broken when its pattern is not (or, for ``absent``, is) in the probe's golden file, or when its quote is no
longer in the reference file. Exit 1 lists every broken row; the notes that begin with ``contradicts:`` or
``refines:`` are printed as a summary either way. The ledger format, and the ``# inherit:`` line that makes one
ecosystem's ledger apply to another's golden files, are in README.md.
"""

import re
import sys
from pathlib import Path

PROBES = Path(__file__).resolve().parent
SKILL = PROBES.parents[2] / "agent-packages/test-authoring/.apm/skills/test-authoring"
COLUMNS = ["id", "probe", "check", "pattern", "reference", "quote", "note"]
INHERIT = re.compile(r"# inherit: ([a-z0-9-]+)")


def unescape(pattern: str) -> str:
    return pattern.encode("latin-1", "backslashreplace").decode("unicode_escape")


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


def read_ledger(ledger: Path) -> tuple[str | None, list[tuple[str, int, list[str]]], list[str]]:
    """Return the ecosystem the ledger inherits from, its rows as (file, line number, cells), and its errors."""
    name = str(ledger.relative_to(PROBES))
    lines = ledger.read_text().splitlines()
    parent = None
    if lines and (directive := INHERIT.fullmatch(lines[0])):
        parent = directive.group(1)
        lines = lines[1:]
    if not lines or lines[0].split("\t") != COLUMNS:
        return parent, [], [f"{name}: header must be {COLUMNS}"]
    rows = [(name, number, line.split("\t")) for number, line in enumerate(lines[1:], start=3 if parent else 2)]
    return parent, rows, []


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
        parent, own, errors = read_ledger(ledger)
        inherited = []
        if parent is not None:
            parent_ledger = PROBES / parent / "claims.tsv"
            if not parent_ledger.exists():
                errors.append(f"{ledger.relative_to(PROBES)}: inherits from {parent}, which has no claims.tsv")
            else:
                grandparent, inherited, parent_errors = read_ledger(parent_ledger)
                errors += parent_errors
                if grandparent is not None:
                    errors.append(f"{parent_ledger.relative_to(PROBES)}: inherits in turn, which is not supported")
        if errors:
            print(*errors, sep="\n")
            return 1
        rows = {}
        for source, number, cells in own:
            if len(cells) != len(COLUMNS):
                print(f"{source}:{number}: {len(cells)} columns, expected {len(COLUMNS)}")
                broken += 1
                continue
            row = dict(zip(COLUMNS, cells))
            if row["id"] in rows:
                print(f"{source}:{number}: duplicate id {row['id']}")
                broken += 1
            rows[row["id"]] = row
            if row["note"].startswith(("contradicts:", "refines:")):
                notes.append(f"{eco.name}/{row['id']} ({row['reference']}): {row['note']}")
        # An inherited row runs against this ecosystem's golden files unless a row of its own replaces it. Its note is
        # printed under the ecosystem that owns the row.
        overridden = set(rows)
        for _, _, cells in inherited:
            if len(cells) == len(COLUMNS) and cells[0] not in overridden:
                rows[cells[0]] = dict(zip(COLUMNS, cells), inherited=parent)
        for row in rows.values():
            cited.add(eco / "expected" / f"{row['probe']}.txt")
            origin = f" (inherited from {row['inherited']})" if "inherited" in row else ""
            for problem in check_row(eco, row):
                print(f"{eco.name}/{row['id']}{origin}: {problem}")
                broken += 1
        summary = f"{eco.name}: {len(rows)} claims checked"
        if parent is not None:
            summary += f", {len(rows) - len(overridden)} inherited from {parent}"
        print(summary)
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
