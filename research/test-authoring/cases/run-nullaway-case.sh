#!/usr/bin/env sh
# Runs one NullAway case of test-authoring as a consumer of the skill would:
# the skill is copied out of this checkout, NullAway is cloned at the case's
# tag into a temporary directory, and claude runs there in safe mode, so no
# installed copy of the skill, no user CLAUDE.md or rule, and none of this
# repository's AGENTS.md files reach the session. Safe mode drops the clone's
# own CLAUDE.md too, so the script appends it to the system prompt, where a
# consumer's session would have loaded it. In NullAway that file is a symlink
# to AGENTS.md and imports nothing.
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
(cd "$work/nullaway" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --append-system-prompt-file CLAUDE.md \
    --permission-mode bypassPermissions --no-session-persistence < "$work/prompt.txt") > "$work/out/result-note.md"

git -C "$work/nullaway" add -A -N
{
  git -C "$work/nullaway" diff HEAD -- nullaway/src/main CHANGELOG.md
  git -C "$work/nullaway" diff "$base" -- . ':!nullaway/src/main' ':!CHANGELOG.md'
} > "$work/out/result.diff"

mkdir -p "$case_dir/$model"
cp "$work/out/"* "$case_dir/$model/"
echo "$work"
