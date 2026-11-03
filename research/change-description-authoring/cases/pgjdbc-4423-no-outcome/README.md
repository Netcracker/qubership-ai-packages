# Case: pgjdbc#4423, a change no caller observes

The input is the diff of [pgjdbc/pgjdbc#4423](https://github.com/pgjdbc/pgjdbc/pull/4423), which stops the Gradle test
task from excluding `**/*Suite*` and renames the one test the mask hid, with the author's notes. Nothing in the driver
jar changes. The case is the negative control for the outcome slot and for the changelog entry: the commit has no
`User-visible:` or `Not changed:` lines, the description has no "User-visible changes" section, and the change gets no
changelog entry.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4 and its skip condition; Pull request description, slot 3; Changelog entry), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **No outcome slot** (`no_outcome_slot`). No `User-visible`, `Not changed:`, or `Breaking` anywhere. A
   `Not changed:` line that says nothing in the jar changes fails: the slot holds an outcome a reader would expect to
   change and that the change keeps, and nothing here is one.
2. **No changelog entry** (`no_changelog_entry`). No bullet in the changelog's shape, and the output says that the
   change needs no entry.

## Running it

As in [the cases README](../README.md). `controls/entry-for-a-test-change.md` is `haiku/result.md` as committed before
2026-10-28 (see the git history) with a `Changed` entry for the test in place of "No entry".

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | No outcome slot (1) | No changelog entry (2) |
| --- | --- | --- |
| Opus r1 | passes | passes |
| Opus r2 | fails: "Not changed: The driver jar has the same contents." | passes |
| Haiku r1, r2 | passes | passes |
| Opus baseline | passes | passes |
| Haiku baseline | passes | passes |
| `controls/entry-for-a-test-change.md` | passes | fails |

The baselines pass both checks: without the skill, neither model writes an outcome slot or an entry for this change.
The failing run is the one that adds a `Not changed:` line to the commit body.
