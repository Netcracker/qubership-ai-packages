# doc-comment-sweep

Sweep the Java and Go comments changed on a branch before opening a pull request. The package combines independent
writer and judge agents with deterministic Python tools that select targets, bound each batch, reconstruct comment
versions, and reject source-code changes.

The package is designed for Claude Code and Codex. APM deploys the same skill bundle to each harness and converts the
two agent definitions to their native formats.

## What is included

| Path | Purpose |
| --- | --- |
| `.apm/skills/doc-comment-sweep/SKILL.md` | Harness-neutral orchestration procedure and fallback rules. |
| `.apm/skills/doc-comment-sweep/scripts/sweep_targets.py` | Java and Go target survey, comment pairs, and resume ledger. |
| `.apm/skills/doc-comment-sweep/scripts/make_batches.py` | Language-safe batching bounded by files, targets, and estimated prompt cost. |
| `.apm/skills/doc-comment-sweep/scripts/strip_*_comments.py` | Comment-only oracles for Java and Go. |
| `.apm/agents/doc-comment-sweeper.agent.md` | Comment editor that may change only assigned targets. |
| `.apm/agents/doc-comment-judge.agent.md` | Read-only adversarial reviewer that reconstructs the old comment's facts first. |

The runtime scripts require only the Python standard library.

Three sibling packages arrive as APM dependencies and install alongside this one: `javadoc-authoring` and
`godoc-authoring` supply the rules a comment is written and graded against, and `english-us-developer-style` supplies
the prose rules. The sweeper and the judge both read the authoring skill by name, so the rubric has one definition and
a fix to it reaches both agents at once.

## Requirements

- APM 0.24.1 or later
- Python 3.9 or later
- Git
- [ast-bro](https://github.com/aeroxy/ast-bro) 3.0 or later, available on `PATH` as `sb`

Install ast-bro with one of its supported package managers:

```bash
python3 -m pip install ast-bro
# or
npm install -g @ast-bro/cli
# or
cargo install ast-bro
```

The agent checks prerequisites and asks before installing anything.

## Install

Register the marketplace and install the package for both supported harnesses:

```bash
apm marketplace add Netcracker/qubership-ai-packages
apm install doc-comment-sweep@qubership-ai-packages --target claude,codex
```

For a direct install from this repository:

```bash
apm install Netcracker/qubership-ai-packages/agent-packages/doc-comment-sweep --target claude,codex
```

## Usage

Start with patch mode and a small scope:

```text
Use doc-comment-sweep on backend/internal/recovery.go and backend/internal/cleanup.go.
Use patch mode, show the survey and batches before editing, and run the backend unit tests as the project gate.
```

For the branch diff:

```text
Use doc-comment-sweep for the Java and Go comments changed against main.
Leave the result as a patch and run the checks required for the edited modules.
```

For a path audit, name a bounded subtree:

```text
Use doc-comment-sweep in path mode for backend/api/v1.
Show the selected-file and target counts before editing anything.
```

Path mode audits every tracked Java or Go file under the path, including comments the branch did not touch. Avoid `.`
unless a repository-wide audit is intentional.

## Workflow

1. Refuse a dirty working tree and record the rollback commit.
2. Survey changed declarations and inline comments with `sb map --json`.
3. Partition targets by language, file count, target count, and estimated prompt cost.
4. Run the sweeper on one batch.
5. Prove the source is unchanged after stripping comments.
6. Run the judge in a separate context and build a fact ledger from the old comments.
7. Retry blocker and major findings up to two rounds.
8. Run repository-specific checks and return an evidence-backed report.

Large files can appear in multiple ordered batches. Those batches share a `serialGroup` and never run concurrently,
which avoids both context exhaustion and conflicting edits to one file.

## Safety boundaries

- The default mode leaves an inspected patch and does not commit.
- The workflow refuses a dirty tree instead of stashing or resetting user work.
- The sweeper can read the repository to verify facts but edits only assigned comments.
- The judge runs independently and never edits source files.
- Java and Go batches use different authoring rules and never share one worker context.
- Machine-readable comments, suppression directives, license headers, issue references, URLs, and generated files are
  excluded from rewriting.
- A comment-only oracle failure blocks the batch regardless of the judge's opinion.

If the harness cannot create an independent judge context, the workflow stops after survey and batching. It reports
the artifacts needed to continue in another session instead of letting the writer approve its own work.

## Test the package

Run the bundled script tests:

```bash
cd .apm/skills/doc-comment-sweep/scripts
for test_file in test_*.py; do PYTHONDONTWRITEBYTECODE=1 python3 "$test_file"; done
```

The survey test builds a temporary Java and Go repository and invokes the real `sb` CLI. The oracle tests exercise
comment-like text inside strings, multiline literals, malformed input, path validation, and end-to-end Git comparisons.
