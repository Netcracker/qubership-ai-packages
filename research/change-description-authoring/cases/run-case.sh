#!/usr/bin/env sh
# Runs one case of change-description-authoring as a consumer of the skill
# would: the skill and english-developer-style are copied out of this checkout
# into a temporary directory, and claude runs there in safe mode with only the
# Read tool, so no installed copy of either skill, no user CLAUDE.md or rule,
# and none of this repository's AGENTS.md files reach the session.
#
# The session reads the copied skill files, then answers the case's prompt.md.
# With --baseline it reads english-developer-style alone, which shows what a
# check catches when the skill under test is absent.
#
# Run from the repository root:
#   research/change-description-authoring/cases/run-case.sh [--baseline] <case directory> <model> <out name> [<rev>]
# <model> is a claude --model alias (haiku, opus). With <rev>, the skills are
# taken from that commit; without it, from the working copy. The output goes to
# <case directory>/<model>/ (<case directory>/<model>/baseline/ with
# --baseline), only after the session succeeds:
#   <out name>.md      the session's final message, which is the drafted text
#   <out name>.run.txt the session's cost, tokens, turns, duration, and effort
#   skill-tree         the tree id of the skill that ran, see scripts/skill-tree.sh
# Set EFFORT to pass --effort (the committed Haiku results ran at high).
set -eu

baseline=
if [ "${1:-}" = --baseline ]; then baseline=1; shift; fi
usage='usage: run-case.sh [--baseline] <case directory> <model> <out name> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
name=${3:?$usage}
skill=agent-packages/change-description-authoring/.apm/skills/change-description-authoring
style=agent-packages/english-us-developer-style/.apm/skills/english-developer-style

work=$(mktemp -d)
mkdir "$work/skills" "$work/out" "$work/session"
copy() {
  # $1 is the skill directory; it lands under $work/skills/<its basename>.
  if [ -n "${rev:-}" ]; then
    git archive "$rev" "$1" | tar -x -C "$work/skills" --strip-components=4
  else
    git ls-files -z --cached --others --exclude-standard -- "$1" | xargs -0 tar -c | tar -x -C "$work/skills" --strip-components=4
  fi
}
rev=${4:-}
copy "$style"
if [ -z "$baseline" ]; then
  copy "$skill"
  if [ -n "$rev" ]; then
    scripts/skill-tree.sh "$skill" "$rev" > "$work/out/skill-tree"
  else
    scripts/skill-tree.sh "$skill" > "$work/out/skill-tree"
  fi
fi

{
  echo 'Before you write anything, read each of these files in full with the Read tool, and follow them:'
  echo
  if [ -z "$baseline" ]; then
    echo "- $work/skills/change-description-authoring/SKILL.md"
    for f in "$work"/skills/change-description-authoring/references/*.md; do echo "- $f"; done
  fi
  echo "- $work/skills/english-developer-style/SKILL.md"
  echo
  echo 'There is no repository checkout and no network: everything you know about the change is below. Your final'
  echo 'message is the deliverable: give the requested text only, with no preamble and no notes about your process.'
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
if [ -n "$baseline" ]; then dest=$dest/baseline; fi
mkdir -p "$dest"
cp "$work/out/"* "$dest/"
rm -rf "$work"
echo "$dest/$name.md"
