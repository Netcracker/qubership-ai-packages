# Case: pgjdbc#4374, outcome lines and a changelog entry

The input is the description of [pgjdbc/pgjdbc#4374](https://github.com/pgjdbc/pgjdbc/pull/4374): a `{fn name}`
escape without an argument list was rewritten into a different statement, and now fails with one of two new errors,
both SQLState `42601`. The task is the commit message and the `CHANGELOG.md` entry. The case tests the changelog
entry and the outcome slot that #113 added, which carries the text and the code where the outcome emits them.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Changelog entry), §3, §5 (identifiers)
- `english-developer-style`: `SKILL.md` §5 (a quoted diagnostic is a literal), §7 (an identifier you do not have is
  not invented)

## Checks

1. **Outcome lines carry the text and the code** (`outcome_lines_4374`). The commit body has a `User-visible:`
   paragraph, and each of the two messages appears on a line of it with `42601`.
2. **Nothing invented** (`nothing_invented_4374`). No issue or pull request number other than #4374 and #4363, and no
   SQLState other than `42601`. No issue was filed for this defect.
3. **The changelog entry** (`changelog_entry_4374`). A bullet that starts with `fix:` (after `**Breaking:**` where the
   writer marks one) carries `[PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)`, the old symptom as a literal
   (`select ow`, `column "ow" does not exist`, or `{fn now}`), and the new error text or its SQLState. Question for the
   reader: does the entry say that a statement that ran only by accident now fails?

## Running it

As in [the cases README](../README.md). `controls/invented-and-thin-entry.md` is `opus/result.md` as committed before
2026-10-28 (see the git history) with `Fixes #4375` added to the commit and the changelog entry cut to its first clause.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome lines (1) | Nothing invented (2) | Changelog entry (3) | Ran by accident now fails (3, read) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | yes |
| Haiku r1 | passes | passes | passes | yes |
| Haiku r2 | passes | passes | passes | only by implication |
| Opus baseline | fails: no `User-visible:` | passes | passes | only by implication |
| Haiku baseline | fails: no `User-visible:` | passes | passes | no |
| `controls/invented-and-thin-entry.md` | passes | fails: `#4375` | fails | no |

Both Opus runs state the dependency on #4363 in the commit message; neither Haiku run does.
