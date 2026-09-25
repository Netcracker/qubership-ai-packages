#!/usr/bin/env bash
# Probes for references/java/junit5.md, junit5-assertions.md, assertj.md, and truth.md. Needs a JDK (21 or later)
# and Maven on PATH. The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# Most cases are `mvn test` runs, because Surefire's console is what a Maven user reads. The names-* cases run JUnit's
# console launcher instead: Surefire prints a parameterized case as `method(int)[1]` and never shows a display name,
# so the display names the reference describes are measured where JUnit prints them.
set -euo pipefail
cd "$(dirname "$0")"

logging=-Djava.util.logging.config.file=src/logging/config.properties

# case id, runner, then the runner's arguments. Every case builds into build/<case id>, so a case that compiles
# other sources or with other flags never reuses another case's classes. A case that runs several classes sets
# surefire.runOrder=alphabetical: the default runs them in directory listing order, which differs between macOS and
# Linux. The random-order cases must not set it, since Surefire then overrides the method orderer they configure;
# random-order-surefire sets it to show that.
cases() {
  cat <<CASES
report               surefire -Dtest=probe.ReportTest
assert-forms         surefire -Dtest=probe.AssertFormsTest
grouping             surefire -Dtest=probe.GroupingTest
throws               surefire -Dtest=probe.ThrowsTest
parameterized        surefire -Dtest=probe.Parameterized* -Dsurefire.runOrder=alphabetical
assertj              surefire -Dtest=probe.AssertjTest
truth                surefire -Dtest=probe.TruthTest
random-order         surefire -Dtest=probe.ShuffledTest -Dprobe.testResources=src/random-order
random-order-logged  surefire -Dtest=probe.ShuffledTest -Dprobe.testResources=src/random-order -DargLine=$logging
random-order-seed    surefire -Dtest=probe.RandomOrderTest -Dprobe.testResources=src/random-order -DargLine=$logging -Djunit.jupiter.execution.order.random.seed=42
random-order-surefire surefire -Dtest=probe.RandomOrderTest -Dprobe.testResources=src/random-order -DargLine=$logging -Djunit.jupiter.execution.order.random.seed=42 -Dsurefire.runOrder=alphabetical
missing-call         surefire -Dprobe.testSources=src/missing-call/java
names                launcher --select-class=probe.ReportTest --select-class=probe.ParameterizedCasesTest --select-class=probe.ParameterizedFieldsTest --select-class=probe.ParameterizedConstructorTest
names-no-parameters  launcher -Dmaven.compiler.parameters=false --select-class=probe.ParameterizedCasesTest --select-class=probe.ParameterizedFieldsTest --select-class=probe.ParameterizedConstructorTest
names-property       launcher -Dprobe.testResources=src/displayname-default --select-class=probe.ParameterizedCasesTest
CASES
}

mvn_quiet=(mvn -q -B --no-transfer-progress)

# Strip what changes between machines and between releases without a change in behavior. A stack frame outside the
# probe package carries a line number of JUnit, AssertJ, Surefire, or the JDK: a run of them becomes one
# "<framework frames>" line, and the probe's own frames, which the claims are about, stay. Maven's closing advice
# after "Failed to execute goal" names plugin versions and help links and says nothing about the tests. JDK 24 and
# later warn when Byte Buddy, which AssertJ loads, calls sun.misc.Unsafe; JDK 21 does not. The seed, the durations
# ../normalize.py leaves (the launcher's `100 ms`, Surefire's `0 s` for a fast test), and the counts of frames AssertJ
# and Truth elide, and the index javac gives a lambda's synthetic method, which differs between JDKs, are this
# ecosystem's to replace; ../normalize.py handles paths and decimal durations.
normalize() {
  sed -E \
    -e 's/(lambda\$[A-Za-z0-9_]+)\$[0-9]+/\1$<n>/g' \
    -e '/^\[ERROR\] Failed to execute goal /,$d' \
    -e '/^WARNING: (A terminally deprecated method in sun\.misc\.Unsafe|sun\.misc\.Unsafe::|Please consider reporting)/d' \
    -e 's/(default seed: )[0-9]+/\1<seed>/' \
    -e 's/\.\.\.\([0-9]+ remaining lines not displayed/...(<n> remaining lines not displayed/' \
    -e 's/Testing framework: [0-9]+ frames collapsed/Testing framework: <n> frames collapsed/' \
    -e 's/^(Test run finished after )[0-9]+ ms$/\1<duration>/' \
    -e 's/(Time elapsed: )[0-9]+ s /\1<duration> /g' |
    awk '
      /^[ \t]+(at )?[A-Za-z0-9_$.\/]+\.[A-Za-z0-9_$<>]+\([^)]*\)$/ {
        if ($0 ~ /^[ \t]+(at )?probe\./) { print; collapsed = 0; next }
        if (!collapsed) { match($0, /^[ \t]+(at )?/); print substr($0, 1, RLENGTH) "<framework frames>"; collapsed = 1 }
        next
      }
      /^[ \t]+\.\.\. [0-9]+ more$/ { sub(/[0-9]+/, "<n>"); print; collapsed = 0; next }
      { print; collapsed = 0 }
    '
}

run_case() {
  local id=$1 line runner
  line=$(cases | awk -v id="$id" '$1 == id')
  [ -n "$line" ] || { echo "unknown case: $id" >&2; exit 2; }
  runner=$(awk '{ print $2 }' <<<"$line")
  local args=() mvn_args=() launcher_args=()
  read -r -a args <<<"$(awk '{ $1 = ""; $2 = ""; sub(/^ +/, ""); print }' <<<"$line")"
  for arg in "${args[@]}"; do
    case $arg in
      --*) launcher_args+=("$arg") ;;
      *) mvn_args+=("$arg") ;;
    esac
  done
  local rc=0
  case $runner in
    surefire)
      "${mvn_quiet[@]}" test -Dprobe.case="$id" ${mvn_args[@]+"${mvn_args[@]}"} 2>&1 | normalize || rc=${PIPESTATUS[0]}
      ;;
    launcher)
      # Compiling is the probe's own step, not the case: its output would only name Maven.
      "${mvn_quiet[@]}" test-compile dependency:build-classpath -Dprobe.case="$id" \
        -Dmdep.outputFile="build/$id/classpath.txt" -Dmdep.includeScope=test ${mvn_args[@]+"${mvn_args[@]}"} >&2
      java -cp "build/$id/test-classes:$(cat "build/$id/classpath.txt")" org.junit.platform.console.ConsoleLauncher \
        execute --disable-banner --disable-ansi-colors --details=tree ${launcher_args[@]+"${launcher_args[@]}"} 2>&1 |
        normalize || rc=${PIPESTATUS[0]}
      ;;
  esac
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
