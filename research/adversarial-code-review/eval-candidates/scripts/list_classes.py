#!/usr/bin/env python3
"""Print the eval-case candidates of each class as Markdown tables.

Reads data/snapshots.json from build_snapshots.py and data/missed-defects.jsonl
from the missed-defect judge. The thresholds are the ones README.md describes.

Usage: list_classes.py [--data DIR] [--top 12]
"""
from __future__ import annotations

import argparse
import json
import os


def table(title: str, rows: list[dict], top: int) -> None:
    print(f"### {title}\n")
    print("| Snapshot | Diff lines | Gold | Accepted | Substantive | Reviewed | Rare categories |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for s in rows[:top]:
        print(f'| {s["repo"]}#{s["pr"]} round {s["round"]} (`{s["commit"][:8]}`) | {s["diff_lines"]} | '
              f'{len(s["gold"])} | {s["accepted"]} | {s["substantive"]} | {s["reviewed_year"]} | '
              f'{", ".join(s["rare_categories"]) or "-"} |')
    print()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    snaps = json.load(open(os.path.join(args.data, "snapshots.json")))
    table("Small diff, many findings", sorted(
        [s for s in snaps if s["diff_lines"] <= 400 and len(s["gold"]) >= 4],
        key=lambda s: -len(s["gold"]) / max(s["diff_lines"], 20)), args.top)
    table("New findings after the author's rework", sorted(
        [s for s in snaps if s["round"] >= 2 and len(s["gold"]) >= 4], key=lambda s: -len(s["gold"])), args.top)
    table("Medium pull request, many findings", sorted(
        [s for s in snaps if 400 < s["diff_lines"] <= 5000 and len(s["gold"]) >= 5], key=lambda s: -len(s["gold"])), args.top)
    table("Manual reviews, before 2025", sorted(
        [s for s in snaps if s["reviewed_year"] < 2025 and len(s["gold"]) >= 3], key=lambda s: -len(s["gold"])), args.top)

    missed = [json.loads(line) for line in open(os.path.join(args.data, "missed-defects.jsonl"))]
    missed = [m for m in missed if m["verdict"] == "introduced" and m["reviewable"]]
    print("### Missed defects\n")
    print("| Culprit | Reported in | Fixed by | Kind | Defect |")
    print("| --- | --- | --- | --- | --- |")
    for m in sorted(missed, key=lambda m: m["culprit_merged"], reverse=True)[:args.top]:
        # An override can make a culprit introduced while every blamer stays likely.
        b = next((b for b in m["blamers"] if b["verdict"] == "introduced"), m["blamers"][0])
        fixes = ", ".join(f"#{n}" for n in b["fix_prs"]) or "-"
        print(f'| {m["repo"]}#{m["culprit"]} | #{b["number"]} | {fixes} | {b["defect_kind"]} | {b["defect"]} |')


if __name__ == "__main__":
    main()
