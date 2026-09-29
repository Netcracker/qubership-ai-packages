#!/usr/bin/env bash
# Probes for the go-mutesting row of references/mutation-tools.md. Needs go and uv; the contract with ../run.sh is
# in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# go-mutesting (the maintained avito-tech fork) is pinned in go.mod as a tool dependency, which Renovate's gomod
# manager bumps. Its v2 tags lack a /v2 module path, so the pin is a pseudo-version of the tagged commit.
set -euo pipefail
cd "$(dirname "$0")"
# The go line of go.mod is a minimum, so a newer go on PATH would run the cases itself. GOTOOLCHAIN pins the
# exact release, which go downloads when the one on PATH differs.
GOTOOLCHAIN=go$(sed -nE 's/^go ([0-9.]+)$/\1/p' go.mod)
export GOTOOLCHAIN
probe=$PWD

cases() {
  printf '%s\n' verdicts
}

# The mutant files live in a fresh temp directory whose name ends in a random number; keep the file name, which
# carries the mutant's index.
normalize() {
  sed -E 's#"[^"]*/go-mutesting-[0-9]+/#"<tmp>/#'
}

# On a cold module cache go prints a "go: downloading" line per module, which would land in the case's output.
# Download the modules and build the tool first, and show the output only if that fails.
warm_up() {
  local out
  out=$(go mod download 2>&1 && go tool -n go-mutesting 2>&1) || { printf '%s\n' "$out" >&2; exit 2; }
}

run_case() {
  local id=$1 work rc=0
  [ "$id" = verdicts ] || { echo "unknown case: $id" >&2; exit 2; }
  # go-mutesting writes report.json into the working directory, so the case runs on a copy.
  warm_up
  work=$(mktemp -d)
  cp go.mod go.sum ./*.go "$work/"
  (
    cd "$work"
    go tool go-mutesting --exec-timeout=10 . 2>&1 | normalize || rc=${PIPESTATUS[0]}
    echo "--- report.json, one mutant per line"
    uv run --quiet --python 3.12 --no-project python "$probe/mutants.py" report.json
    echo "exit code: $rc"
  )
  rm -rf "$work"
}

case ${1:-} in
  list) cases ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
