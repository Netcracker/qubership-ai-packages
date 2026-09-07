# final-review

An APM package that runs a **fixed checklist over a finished change in a fresh subagent**, before the commit is
final. The agent that wrote a change cannot see what it left out; a second agent with a clean context and a form that
demands an answer to every item can, and the form is short enough that the items are answered rather than skipped.

## What it checks

1. Comments consistent with the code and with each other: the doc comment above changed code that nobody edited,
   the first sentence of an added or changed comment, the list a comment carries, the sibling that delegates with a
   fixed argument, history narration.
2. Every case the task statement, the commit message, and the test class comments claim, covered by a named test,
   including the test that separates the chosen design from its alternative.
3. Boundaries, invalid partitions, the empty value, and the negative control that stays green on the base commit.
   Then the level: a test that runs in every job, beside the existing tests of the unit, that skips with a reason
   where the test policy treats a prerequisite as optional and fails where CI promises it.
4. Names and comments that refer by position or ordinal where a content name exists.
5. Assertions that hide the operands, messages that repeat the name, case ids that are indexes.
6. Whether the evidence that the tests can fail is stated.
7. The siblings of the change: other callers of the helper the fix touched, other builders of the same literal,
   found with `git grep` (or `sb callers` where that code-search command is installed), each judged for the same defect.

Every finding is labelled substantive, taste, or churn; only the first is a request, and churn is deleted before the
report goes out.

## Contents

- `.apm/instructions/final-review.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`: run the skill in a fresh subagent when a coding task is written and before the commit is final.
- `.apm/skills/final-review/SKILL.md`: the form.
- `.apm/skills/final-review/scripts/comment-drift.py`: lists, per changed member, whether its code or its doc comment
  moved, so that the comments nobody edited above changed code are on the reviewer's list. Java, Kotlin, Groovy, and
  Scala; line-based and approximate.

## Pairs with

- [`test-authoring`](../test-authoring/) owns what a test establishes and how its failure reads; items 2, 3, and 5
  cite it.
- [`javadoc-authoring`](../javadoc-authoring/) and its siblings own what a comment says; item 1 cites them.
- The developer-style skill of the repository's language owns wording; the review labels wording findings taste
  unless a sentence can be read wrongly.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/final-review
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/final-review@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.3.0`.

Then run `apm install` and `apm compile`.
