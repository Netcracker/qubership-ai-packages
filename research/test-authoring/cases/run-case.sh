#!/usr/bin/env sh
# Runs one case of test-authoring on any repository, as a consumer of the skill
# would: the skill is copied out of this checkout, the repository is fetched at
# the case's base commit into a temporary directory, the case's change is
# committed on top of it, and claude runs there in safe mode, so no installed
# copy of the skill, no user CLAUDE.md or rule, and none of this repository's
# AGENTS.md files reach the session. Safe mode drops the repository's own
# instructions too, so the script appends its CLAUDE.md, or its AGENTS.md where
# it has no CLAUDE.md, to the system prompt, followed by the case's
# instructions.md where the case has one.
#
# A case directory holds:
#   repo              the URL to fetch from
#   base              the full sha of the commit the change applies to
#   change.patch      the change the session finds as the last commit: the
#                     production change alone for a case written from scratch,
#                     or with the submitted tests for a rewrite
#   change-message.txt  the message of that commit
#   production-paths  one git pathspec per line: the production code, which the
#                     session must not change and which is reverted to base for
#                     the run on the base
#   build.sh          runs the tests the session may have changed; called with
#                     the repository directory, prints what ran and what failed
#   prompt.md         the task, with <skill> replaced by the path of the skill copy
#   instructions.md   optional: lines added to the repository's instructions
#
# After the session, the script runs build.sh on the fix and then on the base,
# whatever the session ran itself.
#
# Run from the repository root:
#   research/test-authoring/cases/run-case.sh <case directory> <model> [<rev>]
# With <rev>, the skill is taken from that commit; without it, from the working
# copy. The output goes to <case directory>/<model>/, and only after the
# session succeeds:
#   <file>            every file the session changed, under its own name, so
#                     that the commit of the next run shows how the result moved
#   changed-files.txt one line per changed file: production or other, the git
#                     status letter, and the path; production is compared with
#                     the commit the session started from (expected empty),
#                     everything else with base
#   result-note.md    the session's final message
#   result-build.txt  the output of build.sh on the fix and on the base
#   run.txt           the session's cost, turns, and duration
#   skill-tree        the tree id of the skill that ran, see scripts/skill-tree.sh
set -eu

usage='usage: run-case.sh <case directory> <model> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
skill=agent-packages/test-authoring/.apm/skills/test-authoring
base=$(cat "$case_dir/base")

work=$(mktemp -d)
mkdir "$work/skill" "$work/out"
if [ $# -ge 3 ]; then
  git archive "$3" "$skill" | tar -x -C "$work/skill" --strip-components=5
  scripts/skill-tree.sh "$skill" "$3" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$skill" | xargs -0 tar -c | tar -x -C "$work/skill" --strip-components=5
  scripts/skill-tree.sh "$skill" > "$work/out/skill-tree"
fi

repo=$work/repo
git init -q "$repo"
git -C "$repo" fetch -q --depth 2 "$(cat "$case_dir/repo")" "$base"
git -C "$repo" checkout -q FETCH_HEAD
git -C "$repo" apply --index "$case_dir/change.patch"
git -C "$repo" -c user.name='Case Author' -c user.email='case@example.invalid' \
  commit -q -F "$case_dir/change-message.txt"

: > "$work/instructions.md"
for f in CLAUDE.md AGENTS.md; do
  if [ -f "$repo/$f" ]; then cat "$repo/$f" >> "$work/instructions.md"; break; fi
done
if [ -f "$case_dir/instructions.md" ]; then
  printf '\n' >> "$work/instructions.md"
  cat "$case_dir/instructions.md" >> "$work/instructions.md"
fi

sed "s|<skill>|$work/skill|g" "$case_dir/prompt.md" > "$work/prompt.txt"
(cd "$repo" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --append-system-prompt-file "$work/instructions.md" --output-format json \
    --permission-mode bypassPermissions --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

python3 - "$work/session.json" "$work/out" <<'EOF'
import json, sys
session, out = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
open(f'{out}/result-note.md', 'w').write(d['result'].rstrip('\n') + '\n')
open(f'{out}/run.txt', 'w').write(
    f"cost_usd: {d['total_cost_usd']:.2f}\nturns: {d['num_turns']}\n"
    f"duration_s: {d['duration_ms'] // 1000}\n")
EOF

# One pathspec per line; a pathspec has no spaces in these repositories.
production=$(grep -v '^[[:space:]]*$' "$case_dir/production-paths")
excluded=$(for p in $production; do printf ':!%s ' "$p"; done)
git -C "$repo" add -A -N
{
  # $production and $excluded are split on purpose: one pathspec each.
  # shellcheck disable=SC2086
  git -C "$repo" diff --name-status HEAD -- $production | sed 's/^/production /'
  # shellcheck disable=SC2086
  git -C "$repo" diff --name-status "$base" -- . $excluded | sed 's/^/other /'
} > "$work/out/changed-files.txt"
while read -r _ status file; do
  [ "$status" = D ] && continue
  name=$(basename "$file")
  [ -e "$work/out/$name" ] && { echo "two changed files are named $name" >&2; exit 1; }
  cp "$repo/$file" "$work/out/$name"
done < "$work/out/changed-files.txt"

build() {
  status=0
  out=$(sh "$case_dir/build.sh" "$repo" 2>&1) || status=$?
  { echo "on the $1 (build.sh exited with $status):"; printf '%s\n' "$out" | sed 's/^/  /'; } >> "$work/out/result-build.txt"
}
build fix
# shellcheck disable=SC2086
git -C "$repo" checkout -q "$base" -- $production
build base
# shellcheck disable=SC2086
git -C "$repo" checkout -q HEAD -- $production

rm -rf "${case_dir:?}/$model"
mkdir -p "$case_dir/$model"
cp "$work/out/"* "$case_dir/$model/"
echo "$work"
