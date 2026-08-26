---
name: doc-comment-sweep
description: >-
  Use when asked to tidy, polish, review, audit, or comprehensively improve Java or Go doc comments, Javadoc, GoDoc, or
  inline comments changed on a branch before a pull request, or every comment under a bounded path. Not for editing one
  comment already shown in the request; use the matching language authoring skill for that.
---

# Sweep changed comments

Keep the writer and reviewer in independent contexts. The judge is the control that catches facts a fluent rewrite
drops, so the root agent must never write a batch and then judge that batch itself.

The workflow defaults to leaving an inspected patch in the working tree. Commit only when the user explicitly requests
`commit` mode.

## Prerequisites

Require all of the following before editing:

- a Git repository with a clean working tree;
- Python 3.9 or later;
- `git`;
- `sb` from ast-bro 3.0 or later on `PATH`.

Run `python3 --version`, `git --version`, `sb --version`, and the script tests before the survey. If a dependency is
missing, stop and give the user its installation command. Never install software without approval.

Resolve `<skill-directory>` to the directory containing this `SKILL.md`. Run bundled scripts by absolute path so the
commands work after APM deploys this skill to either `.claude/skills/` or `.agents/skills/`.

## Inputs

Infer these values from the request and repository, using the defaults when absent:

| Input | Default | Meaning |
| --- | --- | --- |
| `base` | repository default branch | Branch used to compute the merge base. |
| `mode` | `patch` | `patch` leaves edits for review; `commit` creates one `docs:` commit per completed wave. |
| `files` | all diff-selected files | Explicit repository-relative file allowlist. |
| `paths` | none | Audit every tracked Java or Go file under bounded pathspecs instead of using the branch diff. |
| `maxFiles` | `5` | Maximum distinct files in a batch. |
| `maxTargets` | `20` | Maximum comment targets in a batch. |
| `maxCost` | `1200` | Estimated prompt cost limit used by `make_batches.py`. |
| `batchesPerWave` | `3` | Maximum concurrently active batches, capped by harness capacity. |
| `maxRounds` | `2` | Maximum sweeper/judge rounds for one batch. |
| `gate` | none | Repository-specific formatter, generator, build, and test commands supplied or discovered for edited files. |

`files` and `paths` are mutually exclusive. Reject `paths: ["."]` unless the user explicitly confirms that repository-
wide audit scope after seeing the selected-file count.

## Agent selection

Use the following fallback order separately for each batch:

1. Invoke the package's `doc-comment-sweeper` and `doc-comment-judge` named agents.
1. If named agents are unavailable, invoke two generic isolated subagents with the corresponding agent file as their
   complete role contract.
1. If the harness cannot provide two isolated contexts, stop after survey and batching. Report that an independent
   judge is unavailable and give the exact commands and artifacts needed to continue in another session.

Never substitute a review in the root context for step 3. Specialist agents are leaf workers and must not delegate.

## Phase 1: Establish state

1. Resolve the repository root with `git rev-parse --show-toplevel`.
1. Refuse a dirty working tree. Do not stash, reset, or overwrite existing work.
1. Record `HEAD` as `preSweepRef` and compute the merge base against `base`.
1. Create an artifact directory under the path returned by `git rev-parse --git-path doc-comment-sweep`. Keep
   `targets.json`, `batches.json`, per-batch agent results, and `ledger.json` there so the working tree stays clean.
1. Run every `test_*.py` in `<skill-directory>/scripts` with `PYTHONDONTWRITEBYTECODE=1`. Stop if any test fails.

## Phase 2: Survey and batch

Run the survey in one of these forms:

```bash
python3 <skill-directory>/scripts/sweep_targets.py survey \
  --root <root> --base <base> --out <artifacts>/targets.json --ledger <artifacts>/ledger.json
```

```bash
python3 <skill-directory>/scripts/sweep_targets.py survey \
  --root <root> --base <base> --out <artifacts>/targets.json --ledger <artifacts>/ledger.json \
  --paths <bounded-paths>
```

Add `--files <files>` only for an explicit file allowlist. Show the user `selectedFiles`, target count, excluded files,
and degraded files before a path-scoped run starts editing.

Create batches:

```bash
python3 <skill-directory>/scripts/make_batches.py create \
  --targets <artifacts>/targets.json --out <artifacts>/batches.json \
  --max-files <maxFiles> --max-targets <maxTargets> --max-cost <maxCost>
```

Each batch is one language. When a large file appears in multiple batches, `serialGroup` contains its path: run those
batches in order and never concurrently. An `oversized` batch contains one target whose estimated cost exceeds the
limit; show it to the user before dispatching it.

Use `javadoc-authoring` for Java and `godoc-authoring` for Go. Never load both language skills into one worker.

## Phase 3: Sweep a batch

Give the sweeper only its batch plus:

- repository root, merge base, `preSweepRef`, and artifact paths;
- the matching authoring skill and `english-developer-style`;
- the repository-specific gate relevant to its files;
- the exact oracle command;
- previous judge findings on retry rounds.

For each file, the worker can materialize its before/pre-sweep/after pairs with:

```bash
python3 <skill-directory>/scripts/sweep_targets.py pairs \
  --targets <artifacts>/targets.json --file <path> --pre-sweep-ref <preSweepRef> --with-body
```

The sweeper may edit only comments associated with the batch's target IDs. It may read other files to verify facts. It
must leave machine-readable comments, licenses, issue references, URLs, TODO/FIXME markers, suppression directives,
and generated files unchanged.

The sweeper returns structured data with `edited`, `unchanged`, `grown`, `commentOnlyOk`, `notes`, and
`artifactMissing`. Persist the result before starting the judge.

## Phase 4: Deterministic oracle

Run the language-specific oracle against every file the batch could have edited:

```bash
python3 <skill-directory>/scripts/strip_java_comments.py verify \
  --root <root> --ref <preSweepRef> --files <java-files>
```

```bash
python3 <skill-directory>/scripts/strip_go_comments.py verify \
  --root <root> --ref <preSweepRef> --files <go-files>
```

Any `fail`, `new`, `missing`, `outside-root`, `unverifiable`, `blocked`, or parse error is a blocker. Under
`preSweepRef`, `new` means the sweeper created a source file. Do not ask the judge to excuse it. Have the sweeper undo
only the accidental code edit, rerun the oracle, and stop the batch if it still fails.

## Phase 5: Independent judge

Start the judge only after persisting the sweeper result and oracle output. Do not pass the sweeper's reasoning; pass
the artifact paths so the judge reconstructs evidence from Git and the working tree.

The judge must:

1. Build a fact ledger from `before` before evaluating `after`.
1. Identify lost facts, invented claims, stale identifiers, narration, and growth without a new fact.
1. Run the oracle independently.
1. Return `verdict`, `factLedger`, `findings`, `staleIdentifiers`, `codeUnchanged`, and `artifactMissing`.

`approve` means no blocker or major finding remains. Persist the result. If the verdict is `revise` and the round
budget remains, send only the findings and evidence back to the sweeper, then repeat the oracle and judge phases. Mark
the batch `stuck` after `maxRounds`; never describe it as approved.

## Phase 6: Gate and land a wave

After all non-overlapping batches in a wave converge:

1. Run each language oracle over every edited file in the wave.
1. Run repository format checks without allowing them to rewrite source automatically.
1. Run required generators when comments feed generated documentation, then inspect all generated diffs.
1. Run the repository-specific build and test commands from `gate`.
1. Compare failures with the recorded baseline and treat every new failure as a gate failure.

On failure, halt later waves and report all deferred batches. On success, update the ledger:

```bash
python3 <skill-directory>/scripts/sweep_targets.py ledger \
  --root <root> --ledger <artifacts>/ledger.json --wave <wave> \
  --mode <diff-or-path> --base <base> --outcome approved --files <approved-files>
```

In `commit` mode, stage only approved comment and required generated-documentation changes. Review the staged diff and
create a Conventional Commit such as `docs: improve changed API comments`. In `patch` mode, leave the approved patch
unstaged unless the user asked otherwise.

## Final report

Return a self-contained report with:

- rollback commit and artifact directory;
- selected, excluded, degraded, resumed, edited, unchanged, stuck, and deferred files;
- batch language, target count, estimated cost, rounds, and judge verdict;
- comment-only oracle results and repository gate commands;
- every grown comment and the new fact that paid for it;
- unresolved minor findings and files needing manual review;
- commits created, or the exact working-tree state in patch mode.

Do not claim full coverage from assigned file counts alone. Report the target counts the judge actually reviewed.
