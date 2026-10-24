#!/usr/bin/env bash
# Create a review dossier under <repo>/.review/<date>/ and print its absolute path.
#
# Usage: new-dossier.sh <repo-path> [label]
#
# The dossier outlives the session on purpose: every stage reads and writes files here,
# so a stage can be re-run later without replaying a conversation.

set -euo pipefail

repo=${1:?usage: new-dossier.sh <repo-path> [label]}
label=${2:-}

# The label becomes a path segment, so it may not climb out of .review or hide the dossier.
case $label in
  '' | [A-Za-z0-9]*) ;;
  *) echo "new-dossier.sh: the label must start with a letter or a digit; got '$label'" >&2; exit 1 ;;
esac
case $label in
  *[!A-Za-z0-9._-]*) echo "new-dossier.sh: the label may hold letters, digits, '.', '_', and '-' only; got '$label'" >&2; exit 1 ;;
esac

repo=$(cd "$repo" && pwd -P)
date=$(date +%Y-%m-%d)
name=$date${label:+-$label}
root="$repo/.review"

# Everything under .review comes from the reviewed repository, which may point any of it somewhere else. Write only
# into directories this script creates itself, and refuse a symbolic link anywhere on the way.
if [ -L "$root" ]; then
  echo "new-dossier.sh: $root is a symbolic link; refusing to write the dossier through it" >&2
  exit 1
fi
if [ -e "$root" ] && [ ! -d "$root" ]; then
  echo "new-dossier.sh: $root exists and is not a directory" >&2
  exit 1
fi
mkdir -p "$root"

dossier="$root/$name"
n=1
# mkdir without -p fails on anything already there, a dangling symbolic link included, so a name is used only when
# this script created the directory.
until mkdir "$dossier" 2>/dev/null; do
  n=$((n + 1))
  dossier="$root/$name-$n"
  if [ "$n" -gt 99 ]; then
    echo "new-dossier.sh: no free dossier name under $root for $name" >&2
    exit 1
  fi
done
case $(cd "$dossier" && pwd -P) in
  "$repo"/.review/*) ;;
  *) echo "new-dossier.sh: $dossier resolves outside $repo" >&2; exit 1 ;;
esac

mkdir "$dossier/prompts" "$dossier/reports" "$dossier/work" "$dossier/work/history" "$dossier/issues" "$dossier/audit"
: >"$dossier/findings.jsonl"

# Keep dossiers out of the reviewed repository's history without touching its .gitignore. A .gitignore that is already
# there, or a symbolic link in its place, is left alone.
if [ ! -e "$root/.gitignore" ] && [ ! -L "$root/.gitignore" ]; then
  printf '*\n' >"$root/.gitignore"
fi

# README.md is left for the consolidator: it becomes the team's report, and a folder view renders it first.
cat >"$dossier/audit/dossier.md" <<EOF
# Review dossier — $name

| File | Written by | Contents |
| --- | --- | --- |
| \`00-profile.md\` | session, stage 1 | archetype, surface, consumers, stability commitments, technology inventory; for a system, the components table and their interactions |
| \`00-commands.md\` | session, stage 1 | build, test, and tooling commands that were executed and work; read-only for agents |
| \`work/commands-<axis>.md\` | agents | corrections to the above — one file per axis, never a shared append |
| \`work/raw-<axis>.jsonl\` | axis agent | findings exactly as raised, before verification |
| \`work/findings-<axis>.jsonl\` | verifier | the verified findings of one axis; the previous version moves to \`work/history/\` on a re-run |
| \`questions.md\` | session, stage 2 | focus questions with pre-filled answers; the user edits this in place |
| \`00-focus.md\` | session, stage 2 | resolved decisions only — every agent reads this |
| \`prompts/<axis>.md\` | workflow | distilled prompts for synthesis axes |
| \`reports/<axis>.md\` | workflow | one report per axis |
| \`findings.jsonl\` | workflow, then triage | normalized findings; triage adds \`verdict\` and \`rejection_reason\` |
| \`README.md\` | workflow | the team's report: what to fix, in which order; the entry point |
| \`issues/<NN>-<slug>.md\` | workflow | one card per problem, ready to copy into a tracker |
| \`findings.csv\` | \`scripts/findings-csv.py\` | every finding, for triage in a spreadsheet; \`--import-csv\` copies decisions back |
| \`audit/synthesis.md\` | workflow | how the run went: disagreements between axes, coverage, refutations |
| \`audit/dossier.md\` | \`new-dossier.sh\` | this map |
| \`work/completeness.md\` | workflow | what the review missed, and the first-reader check of \`README.md\` |
| \`work/\` | agents | scratch space: reproductions, scanner output, benchmarks |

Rejection reasons used during triage: \`convention\`, \`guard-missed\`, \`out-of-scope\`, \`model-error\`,
\`accepted-debt\`. See the \`deep-review\` skill for what each one implies.
EOF

echo "$dossier"
