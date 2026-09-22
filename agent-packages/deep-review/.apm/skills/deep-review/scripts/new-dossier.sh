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

repo=$(cd "$repo" && pwd)
date=$(date +%Y-%m-%d)
name=$date${label:+-$label}
dossier="$repo/.review/$name"

if [ -e "$dossier" ]; then
  n=2
  while [ -e "$dossier-$n" ]; do n=$((n + 1)); done
  dossier="$dossier-$n"
fi

mkdir -p "$dossier/prompts" "$dossier/reports" "$dossier/work/history"
: >"$dossier/findings.jsonl"

# Keep dossiers out of the reviewed repository's history without touching its .gitignore.
if [ ! -e "$repo/.review/.gitignore" ]; then
  printf '*\n' >"$repo/.review/.gitignore"
fi

cat >"$dossier/README.md" <<EOF
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
| \`synthesis.md\` | workflow | deduplicated, ranked, cross-axis view |
| \`work/\` | agents | scratch space: reproductions, scanner output, benchmarks |

Rejection reasons used during triage: \`convention\`, \`guard-missed\`, \`out-of-scope\`, \`model-error\`,
\`accepted-debt\`. See the \`deep-review\` skill for what each one implies.
EOF

echo "$dossier"
