#!/usr/bin/env bash
# Runs one case of blackbox-test-design as a consumer of the skill would. The case's files are copied into a temporary
# directory, the skills are copied into its .claude/skills/, and claude runs there with --setting-sources project, so
# no user CLAUDE.md, rule, hook, or installed skill, and none of this repository's AGENTS.md files, reach the session.
# Both arms get test-authoring, the skill a consumer of this one also has; the with-skill arm adds blackbox-test-design
# and leaves it to the session to load it from its description.
#
# A case directory holds prompt.md (the task), files/ (copied into the working directory), and README.md (the checks).
# Where it also holds build.sh, that script is run with the working directory as its argument, to build an input the
# repository keeps only as source; the source itself stays out of the session.
#
# Run from the repository root:
#   research/blackbox-test-design/cases/run-case.sh <case directory> <with-skill|without-skill> <model>
# The output goes to <case directory>/results/<arm>-<model>/, and only after the session succeeds:
#   the files the session created or changed, and <name>.diff for each input file it changed
#   run.txt      the session's cost, turns, duration, and the skills it loaded
#   skill-tree   the tree id of blackbox-test-design (with-skill only), see scripts/skill-tree.sh
#   skill-tree-test-authoring  the tree id of test-authoring, which both arms have
set -euo pipefail

usage='usage: run-case.sh <case directory> <with-skill|without-skill> <model>'
case_dir=$(cd "${1:?$usage}" && pwd)
arm=${2:?$usage}
model=${3:?$usage}
case $arm in with-skill|without-skill) ;; *) echo "$usage" >&2; exit 2 ;; esac

copy_skill() {
  local dir=agent-packages/$1/.apm/skills/$1
  mkdir -p "$work/task/.claude/skills/$1"
  git ls-files -z --cached --others --exclude-standard -- "$dir" | xargs -0 tar -c | tar -x -C "$work/task/.claude/skills/$1" --strip-components=5
}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/task" "$work/inputs" "$work/out"
if [ -d "$case_dir/files" ]; then
  cp -R "$case_dir/files/." "$work/task/"
  cp -R "$case_dir/files/." "$work/inputs/"
fi
if [ -x "$case_dir/build.sh" ]; then
  "$case_dir/build.sh" "$work/task"
fi
copy_skill test-authoring
scripts/skill-tree.sh agent-packages/test-authoring/.apm/skills/test-authoring > "$work/out/skill-tree-test-authoring"
if [ "$arm" = with-skill ]; then
  copy_skill blackbox-test-design
  scripts/skill-tree.sh agent-packages/blackbox-test-design/.apm/skills/blackbox-test-design > "$work/out/skill-tree"
fi
git -C "$work/task" init -q
echo .claude/ >> "$work/task/.git/info/exclude"

(cd "$work/task" &&
  claude -p "$(cat "$case_dir/prompt.md")" --model "$model" --setting-sources project --strict-mcp-config \
    --no-session-persistence --permission-mode bypassPermissions --output-format stream-json --verbose \
    > "$work/transcript.jsonl")

python3 - "$work/transcript.jsonl" > "$work/out/run.txt" <<'EOF'
import json, sys
skills, result, model = [], {}, None
for line in open(sys.argv[1]):
    event = json.loads(line)
    if event["type"] == "system" and event.get("subtype") == "init":
        model = event["model"]
    elif event["type"] == "assistant":
        for block in event["message"]["content"]:
            if block["type"] == "tool_use" and block["name"] == "Skill":
                skills.append(block["input"]["skill"])
    elif event["type"] == "result":
        result = event
print(f"model: {model}")
print(f"cost_usd: {result['total_cost_usd']:.2f}")
print(f"turns: {result['num_turns']}")
print(f"duration_s: {result['duration_ms'] / 1000:.0f}")
print(f"skills_loaded: {', '.join(skills) or 'none'}")
EOF

git -C "$work/task" ls-files --others --exclude-from="$work/task/.git/info/exclude" | sort |
  while IFS= read -r f; do
    case $f in *.jar) continue ;; esac
    if [ -f "$work/inputs/$f" ]; then
      cmp -s "$work/inputs/$f" "$work/task/$f" || diff -u "$work/inputs/$f" "$work/task/$f" > "$work/out/${f//\//_}.diff" || true
    else
      mkdir -p "$work/out/$(dirname "$f")"
      cp "$work/task/$f" "$work/out/$f"
    fi
  done

dest=$case_dir/results/$arm-$model
rm -rf "$dest"
mkdir -p "$(dirname "$dest")"
cp -R "$work/out" "$dest"
echo "$dest"
cat "$dest/run.txt"
