"""Shows that each fix's regression test fails when that fix is reverted.

A test written beside its fix can pass without checking anything, so every fix owes a run where the
fix is undone and the test is watched failing. This runs that check from a JSON file rather than a
throwaway script, and it refuses to turn a build that never ran into a verdict.

Usage:
    python3 teeth.py --config teeth.json [--only F-016] [--baseline-only]
    python3 teeth.py --dir <review_dir>/teeth --only F-013 --only F-017
    python3 teeth.py --dir <review_dir>/teeth --all

In directory mode each revert is its own file, `<id>.json`, holding the same object the `reverts`
list holds, with the run's `command` and `results_glob` in a `_config.json` beside them. One file per
revert is what makes a revert outlive the round that wrote it: a later round rewrites the code an
earlier fix landed, and `--all` then re-runs every tooth the run has accumulated to show which
earlier fixes still have one. A revert whose `find` text no longer occurs reports
`PATCH DID NOT APPLY` rather than passing quietly, which is the signal that the fix under it was
rewritten and its tooth needs re-cutting.

**The baseline runs once per call and is never carried between calls.** Every verdict below is a
subtraction from it, so it has to describe the suite as it behaves right now. What a cache key could
cover — the commit, the diff, the untracked files — is only the part of the input that lives in the
repository. A suite that talks to a database, a container, a clock, or anything else outside the
checkout can change its answer with the tree byte-identical, and no key computed from git can see
that. So the cheap path is one call per round with every revert in it, which pays for one baseline
and keeps it honest, rather than many calls sharing a stale one.

The config names one command, one glob for the reports it writes, and the reverts to try:

    {
      "command": ["./gradlew", ":nullaway:test",
                  "--tests", "com.uber.nullaway.JSpecifyUnrecognizedAnnotationLocationTest",
                  "-x", "installGitHooks"],
      "results_glob": "nullaway/build/test-results/test/TEST-*.xml",
      "reverts": [
        {"id": "F-016",
         "expect": ["recordComponentIsReportedOnce"],
         "edits": [{"file": "nullaway/src/main/java/com/uber/nullaway/Check.java",
                    "find": "COMPACT_RECORD_CONSTRUCTOR",
                    "replace": "ANNOTATION"}]},
        {"id": "all fixes at once",
         "restore_from": "origin/master",
         "paths": ["nullaway/src/main/java/com/uber/nullaway/Check.java"]}
      ]
    }

An `edits` revert rewrites text in place and requires `find` to occur exactly once. Edits compose:
each one matches the file as the edits before it left it, so a revert may take several edits to one
file, and an edit may follow a `restore_from` on the same path. A `restore_from` revert takes each
path back to the state it has in that git ref, which is the whole fix undone and needs no patch
text.

Three rules keep a stale answer from reading as a real one, and they are the reason to run this
rather than a hand-written loop:

* the command's exit status is read, so a revert that fails to compile is reported as such;
* every report file is required to be newer than the run that should have written it, so the
  previous run's XML can never be mistaken for this one's;
* Gradle is invoked with --no-watch-fs, because its file-system watching drops change events under
  load and then skips the compile task as up-to-date, which yields a green run over unmodified code;
* and with --rerun, because a revert restores the tree to a state the build has already seen, so an
  up-to-date or cached test task writes no report at all and the run has nothing to read. --rerun
  forces only the tasks named on the command line, so compilation stays incremental.
"""

import argparse
import glob
import json
import pathlib
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

GRADLE_FRESHNESS_ARGS = ["--no-watch-fs", "--console=plain", "--rerun"]


def read_reports(results_glob, newer_than):
    """Returns the failed test names from report files written after `newer_than`, or None."""
    fresh = [
        pathlib.Path(f) for f in glob.glob(results_glob) if pathlib.Path(f).stat().st_mtime > newer_than
    ]
    if not fresh:
        return None
    failed = set()
    for f in fresh:
        try:
            root = ET.fromstring(f.read_text())
        except ET.ParseError:
            continue
        for case in root.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                failed.add(case.get("name"))
    return failed


def run_once(config):
    """Runs the configured command and returns (failed test names or None, note)."""
    command = list(config["command"])
    if any("gradlew" in part for part in command):
        command += [a for a in GRADLE_FRESHNESS_ARGS if a not in command]
    stamp = time.time()
    time.sleep(1.05)  # report mtimes have to land strictly after the stamp
    proc = subprocess.run(command, capture_output=True, text=True)
    failed = read_reports(config["results_glob"], stamp)
    if failed is None:
        note = "\n".join(
            line
            for line in (proc.stdout + proc.stderr).splitlines()
            if re.search(r"error:|FAILURE:|Execution failed|Compilation failed", line)
        )
        return None, f"exit {proc.returncode}, no report written\n{note[:800]}"
    return failed, ""


class Stale(Exception):
    """A revert whose text no longer matches the code, usually because a later fix rewrote it."""


def apply_revert(revert, repo):
    """Applies one revert and returns the original contents keyed by path."""
    saved = {}
    for path in revert.get("paths", []) + [e["file"] for e in revert.get("edits", [])]:
        p = pathlib.Path(path)
        saved.setdefault(path, p.read_text())
    try:
        if "restore_from" in revert:
            for path in revert["paths"]:
                old = subprocess.run(
                    ["git", "-C", repo, "show", f"{revert['restore_from']}:{path}"],
                    capture_output=True,
                    text=True,
                )
                if old.returncode != 0:
                    raise SystemExit(
                        f"{revert['id']}: git show failed for {path}: {old.stderr.strip()}"
                    )
                pathlib.Path(path).write_text(old.stdout)
        for edit in revert.get("edits", []):
            # Read what is on disk rather than the saved copy, so that a second edit to one file
            # sees the first one, and so that an edit after a restore_from applies to the restored
            # text.
            target = pathlib.Path(edit["file"])
            text = target.read_text()
            hits = text.count(edit["find"])
            if hits != 1:
                raise Stale(
                    f"{revert['id']}: 'find' matches {hits} times in {edit['file']}, want 1"
                )
            target.write_text(text.replace(edit["find"], edit["replace"], 1))
    except BaseException:
        # A half-applied revert leaves the tree modified, and every later verdict would describe
        # code nobody wrote. SystemExit is not an Exception, so catch wider.
        for path, text in saved.items():
            pathlib.Path(path).write_text(text)
        raise
    return saved


def verdict_for(revert, failed, baseline):
    """Names what the run established for one revert."""
    new_failures = sorted(failed - baseline)
    expected = revert.get("expect")
    if not new_failures:
        return "NO TEETH", "nothing failed that passes with the fix in place"
    if not expected:
        return "teeth", f"newly failing: {', '.join(new_failures)}"
    missing = [t for t in expected if t not in failed]
    if not missing:
        return "teeth", f"newly failing: {', '.join(new_failures)}"
    return "PARTIAL", f"expected but still green: {', '.join(missing)}; newly failing: {', '.join(new_failures)}"


def load_directory(dirpath):
    """Reads one revert per file, with the shared test command from _config.json beside them."""
    d = pathlib.Path(dirpath)
    shared_file = d / "_config.json"
    if not shared_file.exists():
        raise SystemExit(f"{dirpath}: no _config.json naming the command and results_glob")
    shared = json.loads(shared_file.read_text())
    reverts = []
    for f in sorted(d.glob("*.json")):
        if f.name.startswith("_") or f.name.startswith("."):
            continue
        item = json.loads(f.read_text())
        item.setdefault("id", f.stem)
        reverts.append(item)
    return {"command": shared["command"], "results_glob": shared["results_glob"], "reverts": reverts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="one JSON file with command, results_glob and reverts")
    parser.add_argument("--dir", help="directory holding one revert per file, plus _config.json")
    parser.add_argument("--only", action="append", default=[], help="run only these revert ids")
    parser.add_argument("--all", action="store_true", help="run every revert in the directory")
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    if not args.config and not args.dir:
        raise SystemExit("pass --config <file> or --dir <directory>")
    if args.dir and not (args.only or args.all or args.baseline_only):
        raise SystemExit("--dir needs --only <id>, repeatable, or --all")
    config = load_directory(args.dir) if args.dir else json.loads(pathlib.Path(args.config).read_text())

    print("baseline: running the suite with every fix in place", flush=True)
    baseline, note = run_once(config)
    if baseline is None:
        print(f"baseline: NO RESULT — {note}")
        return 2
    if baseline:
        print(f"baseline: {len(baseline)} already failing, discounted from every verdict: {sorted(baseline)}")
    else:
        print("baseline: green")
    if args.baseline_only:
        return 0

    results = []
    for revert in config["reverts"]:
        if args.only and not args.all and revert["id"] not in args.only:
            continue
        try:
            saved = apply_revert(revert, args.repo)
        except Stale as exc:
            results.append((revert["id"], "PATCH DID NOT APPLY", str(exc)))
            print(f"{results[-1][0]}: {results[-1][1]} — {results[-1][2]}", flush=True)
            continue
        try:
            failed, note = run_once(config)
        finally:
            for path, text in saved.items():
                pathlib.Path(path).write_text(text)
        if failed is None:
            results.append((revert["id"], "NO RESULT", note))
        else:
            results.append((revert["id"],) + verdict_for(revert, failed, baseline))
        print(f"{results[-1][0]}: {results[-1][1]} — {results[-1][2]}", flush=True)

    print("\nrestored the tree; summary:")
    for rid, verdict, detail in results:
        print(f"  {verdict:<9} {rid}")
    return 0 if all(v == "teeth" for _, v, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
