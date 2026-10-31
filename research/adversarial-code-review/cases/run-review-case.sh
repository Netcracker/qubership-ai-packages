#!/usr/bin/env sh
# Runs one review case of adversarial-code-review, as a consumer of the skill
# would: the skill is copied out of this checkout, the repository is fetched at
# the case's head commit into a temporary directory, and claude runs there in
# safe mode, so no installed copy of a skill, no user CLAUDE.md or rule, and none of
# this repository's AGENTS.md files reach the session. Safe mode drops the
# repository's own instructions too, so the script appends its CLAUDE.md, or
# its AGENTS.md where it has no CLAUDE.md, to the system prompt.
#
# A case directory holds:
#   repo        the URL to fetch from, or the path of a git bundle relative to
#               the case directory
#   base        the full sha of the commit the change starts from
#   head        the full sha of the last commit of the change
#   prompt.md   the task; <skills> is replaced by the directory of the skill
#               copy, <base> by the base sha, and <head> by the head sha
#
# Run from the repository root:
#   research/adversarial-code-review/cases/run-review-case.sh <case directory> <model> <label> [<rev>]
# With <rev>, the skill is taken from that commit; without it, from the
# working copy. The output goes to <case directory>/<model>/<label>/, and only
# after the session succeeds:
#   result.md     the session's final message, the report
#   run.txt       the session's cost, turns, duration, and tokens per model
#   skill-tree    the tree id of the skill that ran, see scripts/skill-tree.sh
set -eu

usage='usage: run-review-case.sh <case directory> <model> <label> [<rev>]'
case_dir=${1:?$usage}
case_dir=$(cd "${case_dir%/}" && pwd)
model=${2:?$usage}
label=${3:?$usage}
base=$(cat "$case_dir/base")
head=$(cat "$case_dir/head")

work=$(mktemp -d)
mkdir "$work/skills" "$work/out"
name=adversarial-code-review
skill=agent-packages/$name/.apm/skills/$name
if [ $# -ge 4 ]; then
  git archive "$4" "$skill" | tar -x -C "$work/skills" --strip-components=4
  printf '%s %s\n' "$(scripts/skill-tree.sh "$skill" "$4")" "$name" > "$work/out/skill-tree"
else
  git ls-files -z --cached --others --exclude-standard -- "$skill" | xargs -0 tar -c |
    tar -x -C "$work/skills" --strip-components=4
  printf '%s %s\n' "$(scripts/skill-tree.sh "$skill")" "$name" > "$work/out/skill-tree"
fi
# A pipeline's status is its last command's, so a failed git archive shows
# only as a missing copy.
[ -f "$work/skills/$name/SKILL.md" ] || { echo "no $skill at ${4:-the working copy}" >&2; exit 1; }

repo=$work/repo
git init -q "$repo"
src=$(cat "$case_dir/repo")
[ -f "$case_dir/$src" ] && src=$case_dir/$src
git -C "$repo" fetch -q --depth 10 "$src" "$head"
git -C "$repo" checkout -q FETCH_HEAD
git -C "$repo" cat-file -e "$base^{commit}"

: > "$work/instructions.md"
for f in CLAUDE.md AGENTS.md; do
  if [ -f "$repo/$f" ]; then cat "$repo/$f" >> "$work/instructions.md"; break; fi
done

sed -e "s|<skills>|$work/skills|g" -e "s|<base>|$base|g" -e "s|<head>|$head|g" "$case_dir/prompt.md" > "$work/prompt.txt"
(cd "$repo" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --append-system-prompt-file "$work/instructions.md" --output-format json \
    --permission-mode bypassPermissions --no-session-persistence < "$work/prompt.txt") > "$work/session.json"

python3 - "$work/session.json" "$work/out" <<'PY'
import json, sys
session, out = sys.argv[1:]
d = json.load(open(session))
if d['is_error']:
    sys.exit(f"session failed: {d['result']}")
open(f'{out}/result.md', 'w').write(d['result'].rstrip('\n') + '\n')
lines = [f"cost_usd: {d['total_cost_usd']:.2f}", f"turns: {d['num_turns']}",
         f"duration_s: {d['duration_ms'] // 1000}"]
for m, u in d['modelUsage'].items():
    lines.append(f"{m}: cost_usd {u['costUSD']:.2f}, input {u['inputTokens']}, output {u['outputTokens']}, "
                 f"cache_read {u['cacheReadInputTokens']}, cache_write {u['cacheCreationInputTokens']}")
open(f'{out}/run.txt', 'w').write('\n'.join(lines) + '\n')
PY

rm -rf "${case_dir:?}/$model/$label"
mkdir -p "$case_dir/$model/$label"
cp "$work/out/"* "$case_dir/$model/$label/"
echo "$work"
