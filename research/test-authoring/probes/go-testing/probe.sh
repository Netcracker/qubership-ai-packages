#!/usr/bin/env bash
# Probes for references/go/testing.md and references/go/testify.md. Needs the Go toolchain that go.mod names. The
# contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# Every case is one package under this module; -count=1 keeps go test from replaying a cached result.
set -euo pipefail
cd "$(dirname "$0")"
# The toolchain line of go.mod is a minimum, so a newer go on PATH would run the cases itself. GOTOOLCHAIN pins the
# exact release, which go downloads when the one on PATH differs.
GOTOOLCHAIN=$(sed -nE 's/^toolchain (go[0-9.]+)$/\1/p' go.mod)
export GOTOOLCHAIN

# case id, then the go test arguments.
cases() {
  cat <<'CASES'
report          ./report
keep-going      ./keepgoing
subtests        ./subtests
cmp-diff        ./cmpdiff
shuffle-seed    -shuffle=1 -v ./shuffle
shuffle-on      -shuffle=on ./shuffle
shuffle-on-v    -shuffle=on -v -run=^TestA$ ./shuffle
shuffle-on-fail -shuffle=on ./report
shuffle-replay  -shuffle=on -v ./shuffle
parallel        ./parallel
race            -race ./race
testify-forms   ./testifyforms
testify-order   ./testifyorder
testify-group   ./testifygrouping
missing-call    ./missingcall
CASES
}

# Strip what changes between runs and between releases without a change in behavior. ../normalize.py handles
# paths and durations for every ecosystem.
#  - go-cmp prints a random mix of spaces and non-breaking spaces so that nobody parses its output; both become
#    a space.
#  - the seed -shuffle=on picks is the clock; a seed given on the command line is short and stays.
#  - line numbers inside the standard library move with every Go release.
normalize() {
  sed -E \
    -e $'s/\xc2\xa0/ /g' \
    -e 's/^-test\.shuffle [0-9]{6,}$/-test.shuffle <seed>/' \
    -e 's/(testing\.go):[0-9]+:/\1:<line>:/'
}

# The race report names goroutine ids, addresses, and runtime frames, and which of the two writes comes first is
# up to the scheduler. Keep the lines that report the race and its location, once each.
race_summary() {
  sed -E \
    -e 's/^(Read|Write|Previous read|Previous write) at 0x[0-9a-f]+ by goroutine [0-9]+:$/<access> at <address> by goroutine <n>:/' \
    -e 's/ \+0x[0-9a-f]+$//' \
    | grep -E '^WARNING: DATA RACE$|^<access> at|/race/m_test\.go:|race detected during execution of test|^(FAIL|ok)' \
    | sed -E 's/^ +//' | sort -u
}

# Replaying a shuffled run: run once with -shuffle=on, read the seed it prints, rerun with that seed, and report
# whether the order of the tests is the same. The seed and the order change from run to run, and the verdict stays.
shuffle_replay() {
  local first second seed
  first=$(go test -count=1 "$@" 2>&1 || true)
  seed=$(printf '%s\n' "$first" | sed -n -E 's/^-test\.shuffle ([0-9]+)$/\1/p')
  [ -n "$seed" ] || { printf '%s\n' "$first"; echo "no -test.shuffle line in the first run"; return 1; }
  second=$(go test -count=1 "${@/-shuffle=on/-shuffle=$seed}" 2>&1 || true)
  if [ "$(printf '%s\n' "$first" | grep '^=== RUN')" = "$(printf '%s\n' "$second" | grep '^=== RUN')" ]; then
    echo "-shuffle=<seed> with the printed seed ran the tests in the same order"
  else
    echo "-shuffle=<seed> with the printed seed ran the tests in a different order"
  fi
  printf '%s\n' "$second" | grep -m1 '^-test.shuffle' | normalize
}

run_case() {
  local id=$1 line args=()
  line=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$line" ] || { echo "unknown case: $id" >&2; exit 2; }
  read -r -a args <<<"$line"
  # A toolchain or module download prints "go: downloading ..." on stderr; do it before the case runs.
  export GOFLAGS=
  go mod download >/dev/null 2>&1
  local rc=0
  case $id in
    shuffle-replay) shuffle_replay "${args[@]}" || rc=$? ;;
    race) go test -count=1 "${args[@]}" 2>&1 | race_summary | normalize || rc=${PIPESTATUS[0]} ;;
    *) go test -count=1 "${args[@]}" 2>&1 | normalize || rc=${PIPESTATUS[0]} ;;
  esac
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
