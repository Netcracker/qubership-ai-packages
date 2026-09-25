#!/usr/bin/env bash
# Probes for references/java/jetcheck.md. Needs a JDK 21 and Maven 3.9 on the PATH. The contract with ../run.sh is
# in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the Surefire -Dtest filter: one or more test classes under src/test/java/m.
cases() {
  cat <<'CASES'
falsified       PropertyTest
seeded          SeededTest
rechecking      RecheckTest
value-tostring  ValueToStringTest
assert-inside   AssertInPropertyTest
scenarios       ScenarioTest
min-value       MinValueTest
CASES
}

# Keep Surefire's report of each failing test. Drop its closing summary, which repeats every message, and Maven's
# closing lines, which name the Surefire version and point at the report directory. jetCheck prints the stack trace
# of a property that threw into its own message, where Surefire cannot trim it: keep only the frames of the tests.
# A test that took under a millisecond reports "0 s", which ../normalize.py, looking for a decimal point, leaves
# alone.
normalize() {
  local id=$1
  awk '
    /^\[ERROR\] Failed to execute goal / { tail = 1 }
    tail && /^\[ERROR\]/ { next }
    /^\[ERROR\] (Errors|Failures): $/ { skip = 1; next }
    /^\[ERROR\] Tests run: [0-9]+, Failures: [0-9]+, Errors: [0-9]+, Skipped: [0-9]+$/ { skip = 0 }
    !skip
  ' | sed -E \
    -e 's/Time elapsed: [0-9.]+ s/Time elapsed: <duration>/' \
    -e '/^	+at (java|jdk|sun|org\.junit|org\.opentest4j|org\.apache\.maven|org\.jetbrains\.jetCheck)\./d' \
    -e '/^	+\.\.\. [0-9]+ more$/d' |
  if [ "$id" = falsified ]; then
    # The unseeded case: the seed is new on every run, and with it the blob and the length of the shrinking.
    sed -E \
      -e 's/rechecking\("[^"]*"\)/rechecking("<blob>")/' \
      -e 's/recheckingIteration\(-?[0-9]+L, [0-9]+\)/recheckingIteration(<seed>L, <size>)/g' \
      -e 's/withSeed\(-?[0-9]+L\)/withSeed(<seed>L)/g' \
      -e 's/failed on iteration [0-9]+ /failed on iteration <n> /' \
      -e 's/^Shrunk in [0-9]+ stages?, by trying [0-9]+ examples?$/Shrunk in <n> stages, by trying <n> examples/'
  else
    cat
  fi
}

# Surefire prints only what failed. The per-test verdicts, including the tests that passed, and what the tests
# printed come from its report files, in execution order.
results() {
  uv run --quiet --python 3.12 --no-project python - target/surefire-reports <<'PY'
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

reports = Path(sys.argv[1])
print("results:")
for report in sorted(reports.glob("TEST-*.xml")):
    for case in ET.parse(report).getroot().iter("testcase"):
        verdict = "passed"
        for kind in ("failure", "error", "skipped"):
            node = case.find(kind)
            if node is not None:
                verdict = kind + (f" {node.get('type')}" if node.get("type") else "")
        print(f"  {case.get('classname')}.{case.get('name')}: {verdict}")
for output in sorted(reports.glob("*-output.txt")):
    if not output.read_text().strip():
        continue
    print(f"output of {output.name.removesuffix('-output.txt')}:")
    sys.stdout.write("".join(f"  {line}" for line in output.read_text().splitlines(keepends=True)))
PY
}

run_case() {
  local id=$1 tests
  tests=$(cases | awk -v id="$id" '$1 == id { print $2 }')
  [ -n "$tests" ] || { echo "unknown case: $id" >&2; exit 2; }
  rm -rf target/surefire-reports
  local rc=0 output
  output=$(mvn -q -B --no-transfer-progress test -Dtest="$tests" -Dsurefire.failIfNoSpecifiedTests=true 2>&1) || rc=$?
  { [ -z "$output" ] || printf '%s\n' "$output"; results; } | normalize "$id"
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
