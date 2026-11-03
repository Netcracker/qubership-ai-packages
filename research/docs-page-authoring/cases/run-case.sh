#!/usr/bin/env sh
# Runs one case of docs-page-authoring as a consumer of the skill would: the
# skill and english-developer-style are copied out of this checkout into a
# temporary directory, and claude runs there in safe mode with only the Read
# tool, so no installed copy of either skill, no user CLAUDE.md or rule, and
# none of this repository's AGENTS.md files reach the session.
#
# Run from the repository root:
#   research/docs-page-authoring/cases/run-case.sh <case directory> <model> <out name> [<rev>]
# <model> is a claude --model alias (opus, sonnet, haiku). With <rev>,
# docs-page-authoring is taken from that commit and the output goes to
# <case directory>/<model>/baseline/; without it, the skill comes from the
# working copy and the output goes to <case directory>/<model>/.
# english-developer-style always comes from the working copy. The prompt is
# the case's prompt.md with the line <page> replaced by cases/page.md. Only
# after the session succeeds, it writes:
#   <out name>.md      the session's final message, which is the drafted entry
#   <out name>.run.txt the session's cost, tokens, turns, and duration
#   skill-tree         the tree id of docs-page-authoring, see scripts/skill-tree.sh
set -eu

usage='usage: run-case.sh <case directory> <model> <out name> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
name=${3:?$usage}
rev=${4:-}
docs=agent-packages/docs-page-authoring/.apm/skills/docs-page-authoring
style=agent-packages/english-us-developer-style/.apm/skills/english-developer-style

work=$(mktemp -d)
mkdir "$work/skills" "$work/out" "$work/session"
if [ -n "$rev" ]; then
  git archive "$rev" "$docs" | tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$docs" "$rev" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$docs" | xargs -0 tar -c |
    tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$docs" > "$work/out/skill-tree"
fi
git ls-files -z --cached --others --exclude-standard -- "$style" | xargs -0 tar -c |
  tar -x -C "$work/skills" --strip-components=4

{
  echo 'Before you write anything, read these files in full with the Read tool, and follow them:'
  echo
  echo "- $work/skills/docs-page-authoring/SKILL.md"
  echo "- $work/skills/english-developer-style/SKILL.md"
  echo
  echo 'There is no repository checkout and no network: everything you know is below. Your final message is the'
  echo 'deliverable: give the requested text only, with no preamble and no notes about your process.'
  echo
  python3 -c 'import sys; print(open(sys.argv[1]).read().replace("<page>", open(sys.argv[2]).read().rstrip("\n")), end="")' \
    "$case_dir/prompt.md" "$case_dir/../page.md"
} > "$work/prompt.txt"

(cd "$work/session" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --tools Read --output-format json --permission-mode bypassPermissions \
    --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

python3 - "$work/session.json" "$work/out" "$name" <<'PY'
import json, sys
session, out, name = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
if d['num_turns'] <= 1:
    sys.exit(f"session ended after {d['num_turns']} turn without reading the skills: {d['result'][:200]}")
open(f'{out}/{name}.md', 'w').write(d['result'].rstrip('\n') + '\n')
usage = d['usage']
tokens = sum(usage.get(k, 0) for k in
             ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'))
open(f'{out}/{name}.run.txt', 'w').write(
    f"cost_usd: {d['total_cost_usd']:.4f}\ntokens: {tokens}\nturns: {d['num_turns']}\n"
    f"duration_s: {d['duration_ms'] // 1000}\n")
PY

dest=$case_dir/$model
if [ -n "$rev" ]; then dest=$dest/baseline; fi
mkdir -p "$dest"
cp "$work/out/"* "$dest/"
rm -rf "$work"
echo "$dest/$name.md"
