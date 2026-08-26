#!/usr/bin/env python3
"""Create language-homogeneous, cost-bounded work units from a sweep survey."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def estimate_target_cost(target: dict[str, Any]) -> int:
    """Estimate prompt effort from prose size and changed source lines."""
    text = str(target.get("text") or "")
    changed_lines = max(0, int(target.get("changedLines") or 0))
    return 32 + math.ceil(len(text) / 4) + changed_lines * 4


def split_file(file_entry: dict[str, Any], max_targets: int, max_cost: int) -> list[dict[str, Any]]:
    """Split one file into ordered target slices without dropping an oversized target."""
    chunks: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_cost = 0

    def flush() -> None:
        nonlocal current, current_cost
        if not current:
            return
        chunks.append(
            {
                "path": file_entry["path"],
                "language": file_entry["language"],
                "targets": current,
                "estimatedCost": current_cost,
                "oversized": current_cost > max_cost,
            }
        )
        current = []
        current_cost = 0

    for target in file_entry.get("targets", []):
        cost = estimate_target_cost(target)
        if current and (len(current) >= max_targets or current_cost + cost > max_cost):
            flush()
        current.append(target)
        current_cost += cost
        if cost > max_cost:
            flush()
    flush()
    return chunks


def create_batches(
    payload: dict[str, Any], max_files: int, max_targets: int, max_cost: int
) -> dict[str, Any]:
    """Return deterministic batches sorted by language and source path."""
    if min(max_files, max_targets, max_cost) < 1:
        raise ValueError("batch limits must be positive integers")

    by_language: dict[str, list[dict[str, Any]]] = {}
    selected_files = [entry for entry in payload.get("files", []) if entry.get("targets")]
    for entry in sorted(selected_files, key=lambda item: (item.get("language", ""), item["path"])):
        language = str(entry.get("language") or "")
        if not language:
            raise ValueError(f"survey entry {entry['path']!r} has no language")
        by_language.setdefault(language, []).extend(split_file(entry, max_targets, max_cost))

    batches: list[dict[str, Any]] = []
    counters: dict[str, int] = {}

    def append_batch(language: str, items: list[dict[str, Any]], serial_group: str | None = None) -> None:
        counters[language] = counters.get(language, 0) + 1
        batches.append(
            {
                "id": f"{language}-{counters[language]:03d}",
                "language": language,
                "files": [item["path"] for item in items],
                "items": items,
                "targetCount": sum(len(item["targets"]) for item in items),
                "estimatedCost": sum(item["estimatedCost"] for item in items),
                "oversized": any(item["oversized"] for item in items),
                "serialGroup": serial_group,
            }
        )

    for language in sorted(by_language):
        chunks = by_language[language]
        counts: dict[str, int] = {}
        for chunk in chunks:
            counts[chunk["path"]] = counts.get(chunk["path"], 0) + 1

        pending: list[dict[str, Any]] = []

        def flush_pending(batch_language: str) -> None:
            nonlocal pending
            if pending:
                append_batch(batch_language, pending)
                pending = []

        for chunk in chunks:
            if counts[chunk["path"]] > 1:
                flush_pending(language)
                append_batch(language, [chunk], serial_group=chunk["path"])
                continue

            pending_targets = sum(len(item["targets"]) for item in pending)
            pending_cost = sum(item["estimatedCost"] for item in pending)
            would_overflow = (
                len(pending) >= max_files
                or pending_targets + len(chunk["targets"]) > max_targets
                or pending_cost + chunk["estimatedCost"] > max_cost
            )
            if pending and would_overflow:
                flush_pending(language)
            pending.append(chunk)
        flush_pending(language)

    return {
        "version": 1,
        "limits": {
            "maxFiles": max_files,
            "maxTargets": max_targets,
            "maxCost": max_cost,
        },
        "summary": {
            "files": len(selected_files),
            "targets": sum(len(entry.get("targets", [])) for entry in selected_files),
            "batches": len(batches),
            "oversizedBatches": sum(1 for batch in batches if batch["oversized"]),
        },
        "batches": batches,
    }


def command_create(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    report = create_batches(payload, args.max_files, args.max_targets, args.max_cost)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="create batches from targets.json")
    create.add_argument("--targets", required=True, help="survey JSON from sweep_targets.py")
    create.add_argument("--out", required=True, help="destination for batches.json")
    create.add_argument("--max-files", type=int, default=5)
    create.add_argument("--max-targets", type=int, default=20)
    create.add_argument("--max-cost", type=int, default=1200)
    create.set_defaults(func=command_create)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
