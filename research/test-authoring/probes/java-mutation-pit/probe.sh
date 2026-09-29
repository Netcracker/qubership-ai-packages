#!/usr/bin/env bash
# Probes for the PIT row of references/mutation-tools.md. Needs Maven and a JDK 17 or later; the contract with
# ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the Maven arguments after the goals. targetClasses defaults to the groupId, probe.*, which covers
# both classes.
cases() {
  cat <<'CASES'
verdicts          -DtimestampedReports=false
target-classes    -DtargetClasses=probe.Other
history           -DhistoryInputFile=target/history.bin -DhistoryOutputFile=target/history.bin
CASES
}

# PIT prints its log and summary to stdout past Maven's -q. The log lines before the per-mutator summary, the
# timings section, and the slowest-test lines carry durations and spinner characters that normalize.py does not
# recognize, and the advertisement names a URL that may change without a change in behavior, so they are dropped. The CSV report is printed after the summary, one mutant per line, sorted so that
# the order in which PIT ran the mutants does not matter.
summary() {
  sed -E -n '/^- Mutators$/,$p' | sed -E \
    -e '/^- Timings$/,/^> Largest test /d' \
    -e '/^Enhanced functionality available at /d'
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  rm -rf target/pit-reports target/history.bin
  local rc=0
  if [ "$id" = history ]; then
    # The run fails before it mutates anything; keep only the reason, not Maven's stack trace and JVM details.
    # shellcheck disable=SC2086 # the case's arguments are split on purpose
    mvn -B -ntp test-compile org.pitest:pitest-maven:mutationCoverage $args >target/history.log 2>&1 || rc=$?
    grep -E 'History has been enabled|arcmutate_history' target/history.log | sed -E 's/^\[ERROR\] //'
  else
    # shellcheck disable=SC2086 # the case's arguments are split on purpose
    mvn -q -B -ntp test-compile org.pitest:pitest-maven:mutationCoverage $args 2>&1 | summary || rc=${PIPESTATUS[0]}
    echo "--- target/pit-reports/mutations.csv, sorted"
    sort target/pit-reports/mutations.csv
  fi
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
