#!/usr/bin/env bash
# Probes for the gremlins row of references/mutation-tools.md. Needs go and git; the contract with ../run.sh is in
# ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# gremlins is pinned in go.mod as a tool dependency, which Renovate's gomod manager bumps.
set -euo pipefail
cd "$(dirname "$0")"
# The go line of go.mod is a minimum, so a newer go on PATH would run the cases itself. GOTOOLCHAIN pins the
# exact release, which go downloads when the one on PATH differs.
GOTOOLCHAIN=go$(sed -nE 's/^go ([0-9.]+)$/\1/p' go.mod)
export GOTOOLCHAIN

# case id, then the arguments to gremlins unleash. --workers 1 runs the mutants one at a time, in source order.
# The diff case runs in a git repository whose HEAD has IsPositive as n >= 0, with the working tree at n > 0.
cases() {
  cat <<'CASES'
verdicts          --workers 1
path              --workers 1 ./other
diff              --workers 1 --diff HEAD
CASES
}

# gremlins spells the total duration out in words ("1 second 210 milliseconds"), which ../normalize.py does not
# recognize.
normalize() {
  sed -E 's/completed in .*/completed in <duration>/'
}

# On a cold module cache go prints a "go: downloading" line per module, which would land in the case's output.
# Download the modules and build the tool first, and show the output only if that fails.
warm_up() {
  local out
  out=$(go mod download 2>&1 && go tool -n gremlins 2>&1) || { printf '%s\n' "$out" >&2; exit 2; }
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local work rc=0
  warm_up
  work=$(mktemp -d)
  cp -R go.mod go.sum ./*.go other "$work/"
  (
    cd "$work"
    if [ "$id" = diff ]; then
      sed -i.orig 's/return n > 0/return n >= 0/' numbers.go && rm numbers.go.orig
      git init --quiet
      git add .
      git -c user.name=probe -c user.email=probe@example.com commit --quiet --message base
      sed -i.orig 's/return n >= 0/return n > 0/' numbers.go && rm numbers.go.orig
    fi
    # shellcheck disable=SC2086 # the case's arguments are split on purpose
    go tool gremlins unleash $args 2>&1 | normalize || rc=${PIPESTATUS[0]}
    echo "exit code: $rc"
  )
  rm -rf "$work"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
