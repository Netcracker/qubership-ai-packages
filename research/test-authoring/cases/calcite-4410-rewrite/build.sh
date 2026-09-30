#!/usr/bin/env sh
# Runs SqlValidatorTest, and any other test class under core/src/test/java that
# differs from the case's base, in the calcite checkout given as the argument,
# and prints how many tests ran and which failed. Needs a JDK that Gradle 8.7
# runs on (17 or 21); the first run downloads Gradle and the dependencies.
set -eu
repo=${1:?usage: build.sh <calcite checkout>}
case_dir=$(cd "$(dirname "$0")" && pwd)
base=$(cat "$case_dir/base")

classes=$( { echo org.apache.calcite.test.SqlValidatorTest
  git -C "$repo" diff --name-only "$base" -- 'core/src/test/java/*Test.java' |
    sed 's|^core/src/test/java/||; s|\.java$||; s|/|.|g'; } | sort -u)
filters=$(for c in $classes; do printf -- '--tests %s ' "$c"; done)

# Reports of an earlier build, the writer's or the fix's, must not be read as
# this one's.
results=$repo/core/build/test-results/test
rm -rf "$results"
log=$(mktemp)
status=0
# $filters is split on purpose: one --tests argument per class.
# shellcheck disable=SC2086
(cd "$repo" && ./gradlew :core:test --rerun --quiet $filters > "$log" 2>&1) || status=$?

# shellcheck disable=SC2086
python3 - "$results" "$log" "$status" $classes <<'PY'
import glob, sys
import xml.etree.ElementTree as ET
results, log, status, classes = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
ran, failed = 0, []
for c in classes:
    for f in glob.glob(f'{results}/TEST-{c}.xml'):
        for tc in ET.parse(f).getroot().iter('testcase'):
            ran += 1
            if tc.find('failure') is not None or tc.find('error') is not None:
                failed.append(f"{c.rsplit('.', 1)[1]}.{tc.get('name')}")
if ran == 0:
    errors = [l.rstrip() for l in open(log) if 'error:' in l or 'FAILURE' in l or 'What went wrong' in l]
    print(f'no test report was written, and the build exited with {status}' + ''.join(f'\n  {e}' for e in errors[:10]))
elif status != 0 and not failed:
    print(f'{ran} tests ran and none failed, but the build exited with {status}; see {log}')
else:
    print(f'{ran} tests ran, {len(failed)} failed' + ''.join(f'\n  {t}' for t in failed))
PY
[ "$status" -eq 0 ]
