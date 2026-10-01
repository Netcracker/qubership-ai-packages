#!/usr/bin/env sh
# Runs the NullAway test classes that differ from the case's base, in the
# repository given as the first argument, and prints how many tests ran and
# which failed, or the exit status of a build that failed before any test ran.
# Called by run-case.sh on the fix and on the base.
set -eu

repo=${1:?usage: build.sh <repository directory>}
base=$(cat "$(dirname "$0")/base")

# The test classes the session changed, as Gradle --tests filters.
classes=$(git -C "$repo" diff --name-only "$base" -- 'nullaway/src/test/java/*.java' |
  sed 's|^nullaway/src/test/java/||; s|\.java$||; s|/|.|g')
if [ -z "$classes" ]; then
  echo "no test class changed"
  exit 0
fi
filters=$(for c in $classes; do printf -- '--tests %s ' "$c"; done)

# Reports of an earlier build, the writer's or the fix's, must not be read as
# this one's.
results=$repo/nullaway/build/test-results/test
rm -rf "$results"
log=$(mktemp)
status=0
# $filters is split on purpose: one --tests argument per class.
# shellcheck disable=SC2086
(cd "$repo" && ./gradlew :nullaway:test --rerun --quiet $filters > "$log" 2>&1) || status=$?
# shellcheck disable=SC2086
python3 - "$results" "$log" "$status" $classes <<'EOF'
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
    errors = [line.rstrip() for line in open(log) if 'error:' in line or 'FAILURE' in line]
    print(f'no test report was written, and the build exited with {status}' + ''.join(f'\n  {e}' for e in errors[:10]))
elif status != 0 and not failed:
    print(f'{ran} tests ran and none failed, but the build exited with {status}; see {log}')
else:
    print(f'{ran} tests ran, {len(failed)} failed' + ''.join(f'\n  {t}' for t in failed))
EOF
