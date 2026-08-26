#!/usr/bin/env python3
"""Behavioral tests for language-safe, bounded sweep batching."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("make_batches.py")


def target(name: str, text: str = "brief", changed_lines: int = 1) -> dict:
    return {
        "id": name,
        "kind": "doc",
        "text": text,
        "changedLines": changed_lines,
    }


def run_batcher(payload: dict, *args: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "targets.json"
        output = Path(tmp) / "batches.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "create",
                "--targets",
                str(source),
                "--out",
                str(output),
                *args,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if process.returncode != 0:
            raise AssertionError(process.stderr or process.stdout)
        return json.loads(output.read_text(encoding="utf-8"))


def main() -> None:
    payload = {
        "files": [
            {
                "path": "go/api/a.go",
                "language": "go",
                "targets": [target("a1"), target("a2"), target("a3")],
            },
            {
                "path": "go/api/b.go",
                "language": "go",
                "targets": [target("b1")],
            },
            {
                "path": "java/A.java",
                "language": "java",
                "targets": [target("j1")],
            },
        ]
    }
    report = run_batcher(
        payload,
        "--max-files",
        "2",
        "--max-targets",
        "2",
        "--max-cost",
        "1000",
    )
    batches = report["batches"]

    assert report["summary"]["files"] == 3
    assert report["summary"]["targets"] == 5
    assert all(len({item["language"] for item in batch["items"]}) == 1 for batch in batches)
    assert all(batch["targetCount"] <= 2 for batch in batches)

    a_batches = [batch for batch in batches if "go/api/a.go" in batch["files"]]
    assert len(a_batches) == 2
    assert [batch["targetCount"] for batch in a_batches] == [2, 1]
    assert {batch["serialGroup"] for batch in a_batches} == {"go/api/a.go"}

    java_batches = [batch for batch in batches if batch["language"] == "java"]
    assert len(java_batches) == 1
    assert java_batches[0]["files"] == ["java/A.java"]

    expensive = {
        "files": [
            {
                "path": "go/api/huge.go",
                "language": "go",
                "targets": [target("huge", text="x" * 400, changed_lines=80)],
            }
        ]
    }
    expensive_report = run_batcher(expensive, "--max-cost", "50")
    assert len(expensive_report["batches"]) == 1
    assert expensive_report["batches"][0]["oversized"] is True

    print("all cases pass")


if __name__ == "__main__":
    main()
