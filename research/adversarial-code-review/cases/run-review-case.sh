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
#   skills      optional: the names of the skills to copy, one per line;
#               adversarial-code-review when the file is absent
#
# Run from the repository root:
#   research/adversarial-code-review/cases/run-review-case.sh <case directory> <model> <label> [<rev>]
# With <rev>, the skill is taken from that commit; without it, from the
# working copy. The output goes to <case directory>/<model>/<label>/, and only
# after the session succeeds:
#   result.md     the session's final message, the report
#   run.txt       the session's cost, turns, duration, and tokens per model
#   tools.txt     every tool call the session made, one per line
#   access.txt    the tool calls to read first: a web tool, gh, curl, wget,
#                 a git fetch, pull, clone, or remote, a cd or pushd, or a
#                 path outside the clone and the skill copy. It is a pointer
#                 into tools.txt, not a verdict: a path is resolved against
#                 the clone, so an empty file does not show a clean run
#   skill-tree    the tree id of each skill that ran, see scripts/skill-tree.sh
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
names=adversarial-code-review
[ -f "$case_dir/skills" ] && names=$(cat "$case_dir/skills")
for name in $names; do
  skill=agent-packages/$name/.apm/skills/$name
  if [ $# -ge 4 ]; then
    git archive "$4" "$skill" | tar -x -C "$work/skills" --strip-components=4
    printf '%s %s\n' "$(scripts/skill-tree.sh "$skill" "$4")" "$name" >> "$work/out/skill-tree"
  else
    git ls-files -z --cached --others --exclude-standard -- "$skill" | xargs -0 tar -c |
      tar -x -C "$work/skills" --strip-components=4
    printf '%s %s\n' "$(scripts/skill-tree.sh "$skill")" "$name" >> "$work/out/skill-tree"
  fi
  # A pipeline's status is its last command's, so a failed git archive shows
  # only as a missing copy.
  [ -f "$work/skills/$name/SKILL.md" ] || { echo "no $skill at ${4:-the working copy}" >&2; exit 1; }
done

repo=$work/repo
git init -q "$repo"
src=$(cat "$case_dir/repo")
[ -f "$case_dir/$src" ] && src=$case_dir/$src
# Fetch deeper until base..HEAD is the whole change: base is reachable, and
# no commit of the range sits on the shallow boundary, which a merge from the
# main branch can leave on the first-parent chain after the other parent has
# reached base. Nothing newer than head is ever fetched. --deepen does not
# work for a fetch by sha from a URL, so each try fetches again with twice
# the depth.
depth=10
while :; do
  git -C "$repo" fetch -q --depth "$depth" "$src" "$head"
  if git -C "$repo" merge-base --is-ancestor "$base" FETCH_HEAD 2>/dev/null &&
    ! git -C "$repo" rev-list "$base"..FETCH_HEAD | grep -qxFf "$repo/.git/shallow" 2>/dev/null; then
    break
  fi
  [ "$depth" -lt 640 ] || { echo "base $base is not within $depth commits of head $head" >&2; exit 1; }
  depth=$((depth * 2))
done
git -C "$repo" checkout -q FETCH_HEAD

: > "$work/instructions.md"
for f in CLAUDE.md AGENTS.md; do
  if [ -f "$repo/$f" ]; then cat "$repo/$f" >> "$work/instructions.md"; break; fi
done

sed -e "s|<skills>|$work/skills|g" -e "s|<base>|$base|g" -e "s|<head>|$head|g" "$case_dir/prompt.md" > "$work/prompt.txt"
(cd "$repo" &&
  claude -p --safe-mode --settings '{"language":"English"}' --model "$model" \
    --append-system-prompt-file "$work/instructions.md" --output-format stream-json --verbose \
    --permission-mode bypassPermissions --no-session-persistence < "$work/prompt.txt") > "$work/session.jsonl"

python3 - "$work/session.jsonl" "$work/out" "$repo" "$work/skills" <<'PY'
import json, os, re, sys
session, out, *inside = sys.argv[1:]
inside = [os.path.realpath(p) for p in inside]
NETWORK = re.compile(r"\b(gh|curl|wget)\b|\bgit\b[^|;&]*\b(fetch|pull|clone|remote|ls-remote)\b")
PATH = re.compile(r"(?<![\w./])(/[^\s'\"`;|&)]+|~[^\s'\"`;|&)]*|\.\.(?:/[^\s'\"`;|&)]*)?)")
# After a cd, every relative path in the command means something else.
CHDIR = re.compile(r"(?:^|[;&|(]|\bthen|\bdo)\s*(cd|pushd)\b")

def outside(path):
    # A relative path is taken from the clone, where the session starts.
    real = os.path.realpath(os.path.join(inside[0], os.path.expanduser(path)))
    return not any(real == p or real.startswith(p + os.sep) for p in inside) and not real.startswith('/dev/')

calls, access, d = [], [], None
for line in open(session):
    e = json.loads(line)
    if e['type'] == 'result':
        d = e
    elif e['type'] == 'assistant':
        for c in e['message']['content']:
            if c['type'] != 'tool_use':
                continue
            name, args = c['name'], c['input']
            text = args.get('command') or args.get('file_path') or args.get('path') or args.get('url') \
                or args.get('query') or json.dumps(args)
            call = f"{name}: {' '.join(str(text).split())}"
            calls.append(call)
            paths = [args[k] for k in ('file_path', 'path', 'notebook_path') if isinstance(args.get(k), str)]
            if name == 'Bash':
                paths += PATH.findall(args.get('command', ''))
            command = args.get('command', '') if name == 'Bash' else ''
            if name in ('WebFetch', 'WebSearch') or NETWORK.search(command) or CHDIR.search(command) \
                    or any(outside(p) for p in paths):
                access.append(call)
open(f'{out}/tools.txt', 'w').write(''.join(c + '\n' for c in calls))
open(f'{out}/access.txt', 'w').write(''.join(c + '\n' for c in access))
if access:
    print(f"{len(access)} tool calls to check first; see access.txt", file=sys.stderr)
if d is None:
    sys.exit("session ended without a result")
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
