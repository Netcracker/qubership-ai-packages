#!/usr/bin/env sh
# Runs one NullAway case of test-authoring as a consumer of the skill would:
# the skill is copied out of this checkout, NullAway is cloned at the case's
# tag into a temporary directory, and claude runs there in safe mode, so no
# installed copy of the skill, no user CLAUDE.md or rule, and none of this
# repository's AGENTS.md files reach the session. Safe mode drops the clone's
# own CLAUDE.md too, so the script appends it to the system prompt, where a
# consumer's session would have loaded it, followed by the case's
# instructions.md where the case has one. NullAway's CLAUDE.md is a symlink
# to AGENTS.md and imports nothing.
#
# After the session, the script builds the test classes the session changed,
# on the fix and then on the base of the pull request, whatever the session
# ran itself.
#
# Run from the repository root:
#   research/test-authoring/cases/run-nullaway-case.sh <case directory> <model> [<rev>]
# With <rev>, the skill is taken from that commit; without it, from the
# working copy. The output goes to <case directory>/<model>/, and only after
# the session succeeds:
#   result.diff     what the session changed in production code (expected
#                   empty), then every test file relative to the base of
#                   uber/NullAway#1834
#   result-note.md  the session's final message
#   result-build.txt  for the fix and for the base, the tests that ran and
#                   the ones that failed, or the exit status of a build that
#                   failed before any test ran
#   run.txt         the session's cost, turns, and duration, and whether it
#                   ran the tests itself
#   skill-tree      the tree id of the skill that ran, see scripts/skill-tree.sh
set -eu

case_dir=${1:?usage: run-nullaway-case.sh <case directory> <model> [<rev>]}
case_dir=${case_dir%/}
model=${2:?usage: run-nullaway-case.sh <case directory> <model> [<rev>]}
skill=agent-packages/test-authoring/.apm/skills/test-authoring
base=09fdea5a232106714b68f3d9a275e9bdf227c2c5

work=$(mktemp -d)
mkdir "$work/skill" "$work/out"
if [ $# -ge 3 ]; then
  git archive "$3" "$skill" | tar -x -C "$work/skill" --strip-components=5
  scripts/skill-tree.sh "$skill" "$3" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$skill" | xargs -0 tar -c | tar -x -C "$work/skill" --strip-components=5
  scripts/skill-tree.sh "$skill" > "$work/out/skill-tree"
fi
git clone -q --depth 2 --branch "$(cat "$case_dir/tag")" https://github.com/vlsi/NullAway.git "$work/nullaway"

sed "s|<skill>|$work/skill|g" "$case_dir/prompt.md" > "$work/prompt.txt"
# A case may add lines to NullAway's instructions, as its maintainers would
# write them there; they reach the session with the rest of CLAUDE.md.
cat "$work/nullaway/CLAUDE.md" > "$work/instructions.md"
if [ -f "$case_dir/instructions.md" ]; then
  printf '\n' >> "$work/instructions.md"
  cat "$case_dir/instructions.md" >> "$work/instructions.md"
fi
(cd "$work/nullaway" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --append-system-prompt-file "$work/instructions.md" --output-format json \
    --permission-mode bypassPermissions --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

ran_tests=no
[ -d "$work/nullaway/nullaway/build/test-results" ] && ran_tests=yes
python3 - "$work/session.json" "$work/out" "$ran_tests" <<'EOF'
import json, sys
session, out, ran_tests = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
open(f'{out}/result-note.md', 'w').write(d['result'].rstrip('\n') + '\n')
open(f'{out}/run.txt', 'w').write(
    f"cost_usd: {d['total_cost_usd']:.2f}\nturns: {d['num_turns']}\n"
    f"duration_s: {d['duration_ms'] // 1000}\nwriter_ran_tests: {ran_tests}\n")
EOF

git -C "$work/nullaway" add -A -N
{
  git -C "$work/nullaway" diff HEAD -- nullaway/src/main CHANGELOG.md
  git -C "$work/nullaway" diff "$base" -- . ':!nullaway/src/main' ':!CHANGELOG.md'
} > "$work/out/result.diff"

# The test classes the session changed, as Gradle --tests filters.
classes=$(git -C "$work/nullaway" diff --name-only "$base" -- 'nullaway/src/test/java/*.java' |
  sed 's|^nullaway/src/test/java/||; s|\.java$||; s|/|.|g')
filters=$(for c in $classes; do printf -- '--tests %s ' "$c"; done)
build() {
  if [ -z "$classes" ]; then
    echo "on the $1: no test class changed" >> "$work/out/result-build.txt"
    return
  fi
  # Reports of an earlier build, the writer's or the fix's, must not be
  # read as this one's.
  results=$work/nullaway/nullaway/build/test-results/test
  rm -rf "$results"
  status=0
  # $filters is split on purpose: one --tests argument per class.
  # shellcheck disable=SC2086
  (cd "$work/nullaway" && ./gradlew :nullaway:test --rerun --quiet $filters > "$work/build-$1.log" 2>&1) || status=$?
  # shellcheck disable=SC2086
  python3 - "$results" "$work/build-$1.log" "$1" "$status" $classes <<'EOF' >> "$work/out/result-build.txt"
import glob, sys
import xml.etree.ElementTree as ET
results, log, label, status, classes = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5:]
ran, failed = 0, []
for c in classes:
    for f in glob.glob(f'{results}/TEST-{c}.xml'):
        for tc in ET.parse(f).getroot().iter('testcase'):
            ran += 1
            if tc.find('failure') is not None or tc.find('error') is not None:
                failed.append(f"{c.rsplit('.', 1)[1]}.{tc.get('name')}")
if ran == 0:
    errors = [line.rstrip() for line in open(log) if 'error:' in line or 'FAILURE' in line]
    print(f'on the {label}: no test report was written, and the build exited with {status}' + ''.join(f'\n  {e}' for e in errors[:10]))
elif status != 0 and not failed:
    print(f'on the {label}: {ran} tests ran and none failed, but the build exited with {status}; see the build log')
else:
    print(f'on the {label}: {ran} tests ran, {len(failed)} failed' + ''.join(f'\n  {t}' for t in failed))
EOF
}
build fix
git -C "$work/nullaway" checkout -q "$base" -- nullaway/src/main
build base
git -C "$work/nullaway" checkout -q HEAD -- nullaway/src/main

mkdir -p "$case_dir/$model"
cp "$work/out/"* "$case_dir/$model/"
echo "$work"
