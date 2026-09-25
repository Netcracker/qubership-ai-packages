#!/usr/bin/env bash
# Probes for references/java/junit4.md, junit4-assert.md, and hamcrest.md. The contract with ../run.sh is in
# ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# Needs a JDK 21 or later on PATH or in JAVA_HOME; ./mvnw fetches the Maven release that
# .mvn/wrapper/maven-wrapper.properties pins. The runner scrubs the environment (no CI, no colors, fixed width)
# before calling this script.
set -euo pipefail
cd "$(dirname "$0")"

# case id, the runner, then its arguments. `surefire` runs the tests through Maven, which since Surefire 3.6 runs
# JUnit 4 on the JUnit Platform's Vintage engine; `junitcore` runs them through JUnit 4's own runner, the one a build
# on JUnit 4 without the Platform uses; `compile` compiles a test source that calls forms the libraries lack.
cases() {
  cat <<'CASES'
report              surefire  ReportTest
assert-forms        surefire  AssertFormsTest
hamcrest            surefire  HamcrestTest
grouping            surefire  GroupingTest
grouping-junitcore  junitcore probe.GroupingTest
parameterized       surefire  Parameterized*Test
errors              surefire  ErrorsTest
order               surefire  OrderTest
mixed-engines       surefire  Mixed*Test
mixed-junitcore     junitcore probe.MixedEnginesTest probe.MixedIgnoredTest probe.MixedDisabledTest
missing-call        compile   MissingCallTest
CASES
}

mvnw() {
  ./mvnw -B --no-transfer-progress "$@"
}

# Strip JUnitCore's version banner and the durations that ../normalize.py does not recognize (Surefire's "0 s" has no
# fraction, JUnitCore's "Time: 0.008" no unit). normalize.py handles paths, the other durations, and the index javac
# gives a lambda's synthetic method.
normalize() {
  sed -E \
    -e 's/Time elapsed: [0-9.]+ s/Time elapsed: <duration>/' \
    -e 's/^JUnit version [0-9.]+$/JUnit version <version>/' \
    -e 's/^Time: [0-9.,]+$/Time: <duration>/'
}

# The part of Maven's output that belongs to Surefire: from the T E S T S banner to the totals line of the
# results, which is the one "Tests run:" line without " -- in <class>".
surefire_console() {
  awk '/T E S T S/ { on = 1 } on { print } on && /Tests run: [0-9]+, Failures:/ && !/ -- in / { exit }'
}

# The test cases of the XML reports, one line each, with the failure or skip under them: what a CI server that
# reads the XML shows. Times and the test suite's properties are dropped.
xml_digest() {
  local report
  for report in target/surefire-reports/TEST-*.xml; do
    [ -e "$report" ] || continue
    echo "--- ${report#target/surefire-reports/}"
    grep -E '^ *<(testcase|failure|skipped)' "$report" \
      | sed -E -e 's/ time="[^"]*"//' -e 's/(<failure[^>]*>).*/\1/'
  done
}

run_surefire() {
  local tests=$1 rc=0
  rm -rf target/surefire-reports
  mvnw test -Dtest="$tests" -Dsurefire.failIfNoSpecifiedTests=false > target/probe.log 2>&1 || rc=$?
  surefire_console < target/probe.log
  echo "=== Surefire XML report"
  xml_digest
  # The plain-text report of the mixed class shows which engine's half a report file keeps.
  case $tests in
    Mixed*)
      echo "=== Surefire text report"
      cat target/surefire-reports/probe.MixedEnginesTest.txt ;;
  esac
  return $rc
}

run_junitcore() {
  mvnw --quiet test-compile dependency:build-classpath \
    -Dmdep.outputFile=target/classpath.txt -Dmdep.includeScope=test
  local java=java
  if [ -n "${JAVA_HOME:-}" ]; then java=$JAVA_HOME/bin/java; fi
  # JUnitCore prints the whole stack; keep the frames of the probe's own classes, which are what the claims cite.
  "$java" -cp "target/test-classes:target/classes:$(cat target/classpath.txt)" org.junit.runner.JUnitCore "$@" 2>&1 \
    | grep -vE '^[[:space:]]+(at (java|jdk|org\.junit|org\.hamcrest|sun)\.|\.\.\. [0-9]+ more)'
  return "${PIPESTATUS[0]}"
}

# Only the compiler's verdict on each line; the candidate overloads it lists under a line vary between JDKs.
run_compile() {
  local rc=0
  mvnw test-compile -Dprobe.testExclude=none > target/probe.log 2>&1 || rc=$?
  awk '/COMPILATION ERROR/ { on = 1 } on { print } on && /^\[INFO\] [0-9]+ errors?/ { exit }' target/probe.log \
    | grep -E 'COMPILATION ERROR|\.java:\[|^\[INFO\] [0-9]+ error'
  return $rc
}

run_case() {
  local id=$1 line runner args
  line=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$line" ] || { echo "unknown case: $id" >&2; exit 2; }
  read -r runner args <<< "$line"
  mkdir -p target
  local rc=0
  # shellcheck disable=SC2086 # the class list is several arguments
  case $runner in
    surefire) run_surefire $args ;;
    junitcore) run_junitcore $args ;;
    compile) run_compile ;;
  esac > target/case.out 2>&1 || rc=$?
  normalize < target/case.out
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
