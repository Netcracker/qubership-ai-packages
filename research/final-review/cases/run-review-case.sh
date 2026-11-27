#!/usr/bin/env sh
# Runs one review case of final-review, as a consumer of the skills would: the
# skills are copied out of this checkout, the repository is fetched at the
# case's head commit into a temporary directory, and claude runs there in safe
# mode, so no installed copy of a skill, no user CLAUDE.md or rule, and none of
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
#               copies, <base> by the base sha, and <gh> by the directory of
#               the copy of gh/
# and, for a change whose branch has an open pull request:
#   gh/         what gh printed for the branch, one file per command, such as
#               pr-view.json for `gh pr view --json state,title,body,baseRefName`;
#               the session gets a copy outside the case directory
#   gh-stub     an empty file: put a gh on the session's PATH that answers
#               `gh pr view` from gh/pr-view.json, or with gh's `no pull
#               requests found` where the case has no such file, and fails
#               every other command, so that a prompt need not name the pull
#               request
#   branch      the name of a local branch to check the head out on, for gh's
#               messages; without it the head is checked out detached
#   pr-target   the branch the pull request merges into and its sha, as
#               `main <sha>`; the script fetches that commit where the head's
#               history lacks it and points refs/remotes/origin/<branch> at it
#   remote      an empty file: add the case's repository as the remote
#               `origin`, so that a fetch of the target reaches the bundle's
#               branches while refs/remotes/origin/<branch> stays at pr-target
# and, for a review of an uncommitted change:
#   worktree/   files copied over the checkout before the session starts, so
#               that they show as unstaged edits or untracked files
#
# Run from the repository root:
#   research/final-review/cases/run-review-case.sh <case directory> <model> <label> [<rev>]
# With <rev>, the skills are taken from that commit; without it, from the
# working copy. The output goes to <case directory>/<model>/<label>/, and only
# after the session succeeds; a label that already has results is replaced:
#   result.md     the session's final message, the report
#   run.txt       the session's cost, turns, duration, and tokens per model
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
# Each line: the package directory, then the skill directory inside it.
for entry in final-review:final-review test-authoring:test-authoring english-us-developer-style:english-developer-style \
  apm-authoring:apm-authoring; do
  name=${entry#*:}
  skill=agent-packages/${entry%%:*}/.apm/skills/$name
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
git -C "$repo" fetch -q --depth 10 "$src" "$head"
git -C "$repo" checkout -q FETCH_HEAD
if [ -f "$case_dir/branch" ]; then
  read -r branch_name < "$case_dir/branch" || true
  git -C "$repo" checkout -q -b "${branch_name:?$case_dir/branch is empty}"
fi
git -C "$repo" cat-file -e "$base^{commit}"
if [ -f "$case_dir/pr-target" ]; then
  # Read the pair whether or not the file ends in a newline, and say which file
  # is wrong rather than stopping on read's status under set -e.
  target_name='' target_sha=''
  read -r target_name target_sha < "$case_dir/pr-target" || true
  case $target_sha in
    *[!0-9a-f]* | '') bad=1 ;;
    *) [ ${#target_sha} -eq 40 ] && bad= || bad=1 ;;
  esac
  if [ -z "$target_name" ] || [ -n "$bad" ]; then
    echo "$case_dir/pr-target: expected '<branch> <40-character sha>' on one line" >&2
    exit 1
  fi
  if ! git -C "$repo" cat-file -e "$target_sha^{commit}" 2>/dev/null; then
    # The head's shallow history can lack a target that moved on its own.
    git -C "$repo" fetch -q --depth 10 "$src" "$target_sha" 2>/dev/null ||
      git -C "$repo" fetch -q "$src" '+refs/heads/*:refs/case-source/*' 2>/dev/null || true
    git -C "$repo" cat-file -e "$target_sha^{commit}" 2>/dev/null || {
      echo "$case_dir/pr-target: $target_sha is not in $src" >&2
      exit 1
    }
  fi
  git -C "$repo" update-ref "refs/remotes/origin/$target_name" "$target_sha"
fi
if [ -f "$case_dir/remote" ]; then git -C "$repo" remote add origin "$src"; fi
if [ -d "$case_dir/gh" ]; then cp -R "$case_dir/gh" "$work/gh"; fi
if [ -d "$case_dir/worktree" ]; then cp -R "$case_dir/worktree/." "$repo/"; fi
session_path=$PATH
if [ -f "$case_dir/gh-stub" ]; then
  mkdir "$work/bin"
  # The stub answers `gh pr view`, with or without --json and --jq, from the
  # saved output, and refuses every other command as a session with no network
  # would.
  cat > "$work/bin/gh" <<STUB
#!/usr/bin/env python3
import json, subprocess, sys
args = sys.argv[1:]
if args[:2] != ['pr', 'view']:
    sys.exit('gh: no network here; only gh pr view answers')
try:
    data = json.load(open('$work/gh/pr-view.json'))
except FileNotFoundError:
    branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True).stdout.strip()
    sys.exit('no pull requests found for branch "' + branch + '"')
fields = jq = None
for i, a in enumerate(args):
    if a == '--json' and i + 1 < len(args):
        fields = args[i + 1].split(',')
    elif a.startswith('--json='):
        fields = a.split('=', 1)[1].split(',')
    elif a in ('--jq', '-q') and i + 1 < len(args):
        jq = args[i + 1]
if fields is None:
    print('title:\t' + data['title'] + '\nstate:\t' + data['state'] + '\n--\n' + data['body'])
    sys.exit()
unknown = [f for f in fields if f not in data]
if unknown:
    sys.exit('gh: unknown JSON field: ' + ', '.join(unknown))
out = json.dumps({f: data[f] for f in fields})
if jq:
    sys.exit(subprocess.run(['jq', '-r', jq], input=out, text=True).returncode)
print(out)
STUB
  chmod +x "$work/bin/gh"
  session_path=$work/bin:$PATH
fi

: > "$work/instructions.md"
for f in CLAUDE.md AGENTS.md; do
  if [ -f "$repo/$f" ]; then cat "$repo/$f" >> "$work/instructions.md"; break; fi
done

sed -e "s|<skills>|$work/skills|g" -e "s|<base>|$base|g" -e "s|<gh>|$work/gh|g" \
  "$case_dir/prompt.md" > "$work/prompt.txt"
(cd "$repo" && PATH=$session_path &&
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
