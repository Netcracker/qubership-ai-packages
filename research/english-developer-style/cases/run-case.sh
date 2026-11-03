#!/usr/bin/env sh
# Runs one case of english-developer-style as a consumer of the skill would:
# the skill is copied out of this checkout into a temporary directory, and
# claude runs there in safe mode with only the Read tool, so no installed copy
# of the skill, no user CLAUDE.md or rule, and none of this repository's
# AGENTS.md files reach the session.
#
# Run from the repository root:
#   research/english-developer-style/cases/run-case.sh <case directory> <model> <out name> [<rev>]
# <model> is a claude --model alias (opus, sonnet, haiku). With <rev>, the skill
# is taken from that commit and the output goes to <case directory>/<model>/baseline/;
# without it, the skill comes from the working copy and the output goes to
# <case directory>/<model>/. Only after the session succeeds, it writes:
#   <out name>.md      the session's final message, which is the drafted text
#   <out name>.run.txt the session's cost, tokens, turns, duration, and effort
#   skill-tree         the tree id of the skill that ran, see scripts/skill-tree.sh
# Set EFFORT to pass --effort.
set -eu

usage='usage: run-case.sh <case directory> <model> <out name> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
name=${3:?$usage}
rev=${4:-}
style=agent-packages/english-us-developer-style/.apm/skills/english-developer-style

work=$(mktemp -d)
mkdir "$work/skills" "$work/out" "$work/session"
if [ -n "$rev" ]; then
  git archive "$rev" "$style" | tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$style" "$rev" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$style" | xargs -0 tar -c |
    tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$style" > "$work/out/skill-tree"
fi

{
  echo 'Before you write anything, read this file in full with the Read tool, and follow it:'
  echo
  echo "- $work/skills/english-developer-style/SKILL.md"
  echo
  echo 'There is no repository checkout and no network: everything you know is below. Your final message is the'
  echo 'deliverable: give the requested text only, with no preamble and no notes about your process.'
  echo
  cat "$case_dir/prompt.md"
} > "$work/prompt.txt"

effort=
if [ -n "${EFFORT:-}" ]; then effort="--effort $EFFORT"; fi
# $effort is split on purpose: empty, or the flag and its value.
# shellcheck disable=SC2086
(cd "$work/session" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" $effort \
    --tools Read --output-format json --permission-mode bypassPermissions \
    --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

python3 - "$work/session.json" "$work/out" "$name" "${EFFORT:-}" <<'EOF'
import json, sys
session, out, name, effort = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
open(f'{out}/{name}.md', 'w').write(d['result'].rstrip('\n') + '\n')
usage = d['usage']
tokens = sum(usage.get(k, 0) for k in
             ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'))
open(f'{out}/{name}.run.txt', 'w').write(
    f"cost_usd: {d['total_cost_usd']:.4f}\ntokens: {tokens}\nturns: {d['num_turns']}\n"
    f"duration_s: {d['duration_ms'] // 1000}\neffort: {effort or 'default'}\n")
EOF

dest=$case_dir/$model
if [ -n "$rev" ]; then dest=$dest/baseline; fi
mkdir -p "$dest"
cp "$work/out/"* "$dest/"
rm -rf "$work"
echo "$dest/$name.md"
