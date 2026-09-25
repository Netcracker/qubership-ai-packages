#!/usr/bin/env bash
# Probes for the Stryker row of references/mutation-tools.md. Needs node and npm; .nvmrc names the Node release CI
# sets up. The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the arguments to stryker run. stryker.config.json mutates src/**/*.ts; --mutate overrides it. The
# scoped cases name numbers.ts, not other.ts: the vitest runner runs only the tests related to the mutated files, and
# with no test importing other.ts the dry run finds none and Stryker stops.
cases() {
  cat <<'CASES'
verdicts          stryker.config.json
mutate-file       stryker.config.json --mutate src/numbers.ts
mutate-lines      stryker.config.json --mutate src/numbers.ts:12-12
CASES
}

# Stryker's log lines carry a clock time and a process id and report durations of the dry run, so they are dropped;
# the clear-text report, which follows them, is kept. Colors are stripped in case the log ignores NO_COLOR.
report() {
  sed -E $'s/\x1b\\[[0-9;]*m//g' | grep -Ev '^[0-9]{2}:[0-9]{2}:[0-9]{2} \([0-9]+\) '
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  npm ci --silent --no-audit --no-fund >&2
  rm -rf reports
  local rc=0
  # shellcheck disable=SC2086 # the case's arguments are split on purpose
  npx --no-install stryker run $args 2>&1 | report || rc=${PIPESTATUS[0]}
  # The clear-text report lists only the survivors and the uncovered mutants; the JSON report has every status.
  if [ -f reports/mutation/mutation.json ]; then
    echo "--- reports/mutation/mutation.json, one mutant per line"
    node statuses.mjs reports/mutation/mutation.json
  fi
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
