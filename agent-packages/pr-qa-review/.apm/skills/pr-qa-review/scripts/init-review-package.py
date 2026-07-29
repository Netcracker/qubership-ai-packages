#!/usr/bin/env python3
"""Create a new durable artifact package for pr-qa-review."""

import argparse
import json
import re
import sys
from pathlib import Path


OID_PATTERN = re.compile(r"^[0-9a-fA-F]{40,64}$")


def complete_oid(value):
    if not OID_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError("expected a complete 40-64 character hexadecimal OID")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_directory", type=Path)
    parser.add_argument("--base-oid", required=True, type=complete_oid)
    parser.add_argument("--head-oid", required=True, type=complete_oid)
    args = parser.parse_args()

    root = args.artifact_directory.resolve()
    if root.exists():
        print(f"review package already exists: {root}")
        return 1

    root.mkdir(parents=True)
    (root / "checks").mkdir()
    (root / "screenshots").mkdir()
    (root / "report.md").write_text("# QA Review\n", encoding="utf-8")
    state = {
        "schema_version": 1,
        "review_status": "blocked",
        "workflow_state": "DISCOVER",
        "capability_discovery": [],
        "target": {
            "initial_base_oid": args.base_oid,
            "initial_head_oid": args.head_oid,
            "final_head_oid": args.head_oid,
            "status": "preliminary",
        },
        "permissions": [],
        "actions": [],
        "coverage": [],
        "checks": [],
    }
    (root / "review-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"review package created: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
