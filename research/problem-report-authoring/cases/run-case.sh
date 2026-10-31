#!/usr/bin/env sh
# Runs one case of problem-report-authoring as a consumer of the skill would:
# the skill and english-developer-style are copied out of this checkout into a
# temporary directory, and claude runs there in safe mode with only the Read
# and Write tools, so no installed copy of either skill, no user CLAUDE.md or
# rule, and none of this repository's AGENTS.md files reach the session.
#
# Run from the repository root:
#   research/problem-report-authoring/cases/run-case.sh <case directory> <model> <out name> [<rev>]
# <model> is a model ID such as claude-opus-5-5, and names the output
# directory. With <rev>, problem-report-authoring is taken from that commit and
# the output goes to <case directory>/<model>/baseline/; without it, the skill
# comes from the working copy and the output goes to <case directory>/<model>/.
# english-developer-style always comes from the working copy. Only after the
# session succeeds, it writes:
#   <out name>.md      the report or message the session drafted
#   <out name>-note.md the hand-over note to the person filing
#   <out name>.run.txt the session's cost, tokens, turns, and duration
#   skill-tree         the tree id of problem-report-authoring, see scripts/skill-tree.sh
set -eu

usage='usage: run-case.sh <case directory> <model> <out name> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
name=${3:?$usage}
rev=${4:-}
skill=agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring
style=agent-packages/english-us-developer-style/.apm/skills/english-developer-style

work=$(mktemp -d)
mkdir "$work/skills" "$work/out" "$work/session"
if [ -n "$rev" ]; then
  git archive "$rev" "$skill" | tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$skill" "$rev" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$skill" | xargs -0 tar -c |
    tar -x -C "$work/skills" --strip-components=4
  scripts/skill-tree.sh "$skill" > "$work/out/skill-tree"
fi
git ls-files -z --cached --others --exclude-standard -- "$style" | xargs -0 tar -c |
  tar -x -C "$work/skills" --strip-components=4
cp "$case_dir/prompt.md" "$work/prompt.md"

cat > "$work/prompt.txt" <<EOF
Read the skill at $work/skills/problem-report-authoring/SKILL.md in full, open its reference files under the
references/ directory next to it where the skill says to, and follow it. Read
$work/skills/english-developer-style/SKILL.md in full too, and follow it for the wording. Your input is
$work/prompt.md. There is no repository checkout and no network: everything you know is in the input. Do not file or
send anything. Write the report or message to $work/out/draft.md and the hand-over note to the person filing to
$work/out/draft-note.md. Write only those two files.
EOF

(cd "$work/session" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --tools Read,Write --output-format json --permission-mode bypassPermissions \
    --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

python3 - "$work/session.json" "$work/out" "$name" <<'PY'
import json, os, sys
session, out, name = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
for f in ('draft.md', 'draft-note.md'):
    if not os.path.exists(f'{out}/{f}'):
        sys.exit(f"session wrote no {f}: {d['result'][:200]}")
for src, dst in (('draft.md', f'{name}.md'), ('draft-note.md', f'{name}-note.md')):
    text = open(f'{out}/{src}').read().replace(f'{out}/', '')
    open(f'{out}/{dst}', 'w').write(text.rstrip('\n') + '\n')
    os.remove(f'{out}/{src}')
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
