#!/usr/bin/env bash
# Probes for the mutmut row of references/mutation-tools.md. Needs uv; the contract with ../run.sh is in
# ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
set -euo pipefail
cd "$(dirname "$0")"
probe=$PWD

# verdicts  one run over src/, then every mutant's status
# rerun     the same run, then a second one after is_positive changed, which re-tests only that function
cases() {
  printf '%s\n' verdicts rerun
}

# mutmut redraws a progress line with a spinner many times a second, so the number of lines depends on the speed of
# the machine. Keep the first and the last counter line of the mutation run, without the spinner: the first shows
# how many mutants already had a result when the run began, the last the totals. The legend of the counters is
# mutmut's: killed, no tests, timeout, suspicious, survived, skipped, caught by type check.
counters() {
  tr '\r' '\n' | sed -E 's/[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏] /\n/g' | grep -E '^[0-9]+/[0-9]+  ' | sed -n '1p;$p' | uniq
}

mutmut() {
  uv run --quiet --managed-python --frozen --project "$probe" mutmut "$@"
}

run_case() {
  local id=$1 work rc=0
  case $id in verdicts|rerun) ;; *) echo "unknown case: $id" >&2; exit 2 ;; esac
  # The interpreter is the uv-managed CPython that .python-version pins, never one found on the host.
  uv sync --quiet --managed-python --frozen
  # mutmut writes its mutants/ directory next to the sources, so each case works on a copy.
  work=$(mktemp -d)
  cp -R src tests pyproject.toml "$work/"
  (
    cd "$work"
    if [ "$id" = rerun ]; then
      mutmut run >/dev/null 2>&1 || true
      sed -i.orig 's/return n > 0/return 0 < n/' src/numbers_probe/numbers.py
      echo "--- is_positive changed, the rest did not"
    fi
    mutmut run 2>&1 | counters || rc=${PIPESTATUS[0]}
    echo "--- mutmut results --all true"
    mutmut results --all true 2>&1
    echo "exit code: $rc"
  )
  rm -rf "$work"
}

case ${1:-} in
  list) cases ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
