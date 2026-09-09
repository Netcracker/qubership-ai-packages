# A/B trial: references split by role, against the one-file-per-language layout

Run on 2026-09-07 against pgjdbc at the base commit of
[PR #4405](https://github.com/pgjdbc/pgjdbc/pull/4405) with that PR's one-file fix applied and its test left out, the
same task as `ab-pr4405.md`. Two questions:

1. With the references split by the role a library plays (engine, assertion library, doubles, property-based,
   structural, mutation) and the §0 selection protocol in `SKILL.md`, which files does the model open, and does the
   split change the tests it writes on a JUnit 5 project with JUnit assertions?
2. On a project whose assertion library is AssertJ, does the old layout leak the JUnit form of a rule (`assertAll` as
   the way to group assertions), and does the split stop the leak?

## Setup

Eight headless `claude -p` sessions, one per cell, each in its own detached worktree at the same base commit, run
with `--setting-sources project` so that only the worktree's `.claude/` is loaded: `test-authoring` in the old or the
new layout, `javadoc-authoring` and `english-developer-style` as they were on the day, and the three trigger
paragraphs in `.claude/rules/`. The old layout is the package as committed on 2026-09-06 plus the maintainer's later
edit of `junit.md` on parameterized names, so the two arms differ only in the split and in §0. Every worktree carries
a `CLAUDE.md` line naming the stack, as the skill now expects.

Two projects. *Stock* is pgjdbc with the line `Tests: JUnit 5 engine, JUnit 5 assertions.` *AssertJ* is pgjdbc with
`assertj-core` added to the test dependencies, the neighboring unit test `V3ParameterListTests` rewritten to
`assertThat(...).isEqualTo(...)`, and the line `Tests: JUnit 5 engine, AssertJ assertions.`; the rest of the test
tree, `PreparedStatementTest` included, still uses JUnit assertions. The prompt is the one-shot prompt of
`ab-pr4405.md`: the problem, the diff, "write the tests this change needs, and commit", naming no skill and no test
class, with a PostgreSQL 16 on the default port. Models `opus` and `sonnet` as the CLI resolved them on the day. One
run per cell; nothing below has a variance estimate. Scripts, prompts, transcripts, and the metrics extractor are in
`claude-skills-research/experiments/20260907-test-authoring-refs-ab/`.

## Results

| Cell | Layout | Project | Model | Reference files opened | Unit test | Integration test | Red on base (of N) | Cost | Min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r01 | old | stock | Opus | none | 3 methods in `V3ParameterListTests` | new class, 3 tests | 4 of 7 | $4.05 | 7.8 |
| r02 | old | stock | Sonnet | none | 2 methods in `V3ParameterListTests` | new class, 1 `@ParameterizedTest(name = "{0}")` over a label column | 3 of 5 | $3.01 | 7.2 |
| r03 | new | stock | Opus | `junit5.md`, `junit5-assertions.md` | 3 methods in `V3ParameterListTests` | new class, 1 test with `assertAll` over value and warning | 3 of 5 | $5.77 | 11.0 |
| r04 | new | stock | Sonnet | none | 1 method asserting both settings | 1 method added to `PreparedStatementTest` | 2 of 8 | $1.88 | 6.3 |
| r05 | old | AssertJ | Opus | `junit.md` | 3 methods, AssertJ | new class, `@ParameterizedTest` over the setting, **AssertJ `assertThat` wrapped in JUnit `assertAll`**, both imports | 3 of 6 | $6.08 | 11.6 |
| r06 | old | AssertJ | Sonnet | none | 3 methods, AssertJ | 1 method added to `PreparedStatementTest`, JUnit assertions | 4 of 120 | $3.07 | 7.9 |
| r07 | new | AssertJ | Opus | `junit5.md` | 4 methods, AssertJ | new class, 2 tests through a helper, AssertJ `assertSoftly`, no JUnit import | 4 of 7 | $5.22 | 10.0 |
| r08 | new | AssertJ | Sonnet | none | 2 methods, AssertJ | 1 method added to `PreparedStatementTest`, JUnit assertions | 3 of 119 | $3.03 | 8.0 |

Every cell loaded `test-authoring` through the Skill tool without being told, compiled, passed with the fix, and went
red with the fix reverted; the reverts were run again here, outside the sessions. Every cell added its unit test to
`V3ParameterListTests` through the public `toString`, as in the earlier trial. Total cost $32.11.

**Question 2 is answered.** The leak exists and the split stops it. In r05, Opus on the AssertJ project under the
old layout opened `junit.md`, read the "Grouping assertions" section that names `assertAll`, and wrote the
integration test's two checks as AssertJ `assertThat` calls inside JUnit's `assertAll`, importing both libraries into
one file. In r07, the same model on the same project under the new layout wrote `assertSoftly` with no JUnit import.
It had opened only `junit5.md`, the engine file, which carries no grouping rule, and took `assertSoftly` from its own
knowledge; the file it did not open could no longer mislead it. The Sonnet cells on the AssertJ project (r06, r08)
show no leak under either layout, and no grouping at all: they wrote the integration test as one method in the
existing `PreparedStatementTest` and matched that file's JUnit assertions rather than the `CLAUDE.md` line, which
is the nearest-test rule of §0 and §9 winning over the stack line.

**Question 1 is answered for Opus and not for Sonnet.** Opus opened the reference files in both new-layout cells,
through `ls` of the directory and `cat` of the file (never the Read tool), and in r03 chose exactly the two files §0
names for the stock stack. The tests it then wrote follow them: `assertAll` for the two checks on one result, a
message on `assertTrue(rs.next())`, no `@ParameterizedTest` name pattern. Sonnet opened no reference file in any of
its four cells, under either layout, and its transcripts never mention the references; what it knows of the
mechanics comes from `SKILL.md` alone. Its tests show the difference: a `name = "{0}"` pattern over a label column
where `junit5.md` says to keep the default (r02, old layout, so the file it did not read would not have helped it
either), a bare `assertTrue(rs.next())` with no message (r04, r08), and one unit method asserting both settings
(r04), which is §7's one-behavior rule not followed.

## What the trial says about the layout

- The role split does what it was made for: a project on one assertion library no longer reads the grouping rule of
  another, because the file that carried both no longer exists. The two Opus cells on the AssertJ project are the
  before and after.
- §0's selection protocol works when the model reads it: r03 opened the engine file and the assertions file for the
  named stack and nothing else. It is read by Opus and, on these four runs, not acted on by Sonnet.
- The reference files are inert for Sonnet. Four runs, two layouts, two projects, zero files opened. The rules a
  reference carries (the default parameterized name, the message on a boolean assertion, `assertSoftly` for AssertJ)
  reach Sonnet only if `SKILL.md` or the trigger paragraph carries them, or if the instruction to open the file is
  imperative and placed where the model acts on it, which is the next thing to try: a sentence in the trigger
  paragraph of `.claude/rules/test-authoring.md`, or a first step in §0 that names the two files to open before the
  first assertion is written. This trial does not test that.
- A method added to an existing JUnit-assertions file was written with JUnit assertions in every Sonnet cell on the
  AssertJ project, against the `CLAUDE.md` line. That is not a defect: the two requirements conflict, both choices
  are defensible in a real project, and the stack line governs the new classes, where every cell used AssertJ.
- Cost and time did not move with the layout. The Opus cells cost $4 to $6 and the Sonnet cells $2 to $3 under both
  layouts; the new layout's Opus cells ran longer by two to three minutes, which is within what one run shows.

## Rerun: the four Sonnet cells with an imperative read in the trigger paragraph

After the eight cells above, one sentence went into the trigger paragraph (`.claude/rules/test-authoring.md` and the
package's instructions file) and into the first paragraph of §0: before writing the first assertion, read the two
files under `references/` for the project's test engine and its assertion library. The four Sonnet cells were rerun
with that sentence and nothing else changed; the old layout got the same sentence, though it has no §0 to point at.

| Cell | Layout | Project | Reference files opened | Unit test | Integration test | Red on base (of N) | Cost | Min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r09 | old | stock | `junit.md` | 1 method in `V3ParameterListTests` | new class beside it, 2 tests | 3 of 4 | $2.93 | 9.8 |
| r10 | new | stock | `junit5.md`, `junit5-assertions.md` | 3 methods in `V3ParameterListTests` | 1 method added to `PreparedStatementTest` | 4 of 120 | $2.55 | 9.6 |
| r11 | old | AssertJ | `junit.md` | 2 methods, AssertJ | 1 method added to `PreparedStatementTest`, JUnit assertions | 2 of 9 | $2.39 | 8.9 |
| r12 | new | AssertJ | `junit5.md`, `assertj.md` | 2 methods, AssertJ | 1 method added to `PreparedStatementTest`, **AssertJ** | 2 of 9 | $3.25 | 10.0 |

Every cell compiled, passed with the fix, and went red without it. Four of four opened reference files, against zero
of four without the sentence; the two new-layout cells opened exactly the two files §0 names for their stack, and r12
picked `assertj.md` for the AssertJ project without being told which file that was. In r12 the method added to the
JUnit-assertions `PreparedStatementTest` was written with AssertJ, the only Sonnet cell to follow the stack line
there; the other three kept the file's own style, which is the defensible reading of a conflict the project itself
created. No cell leaked `assertAll` in either layout, as before: Sonnet did not group assertions at all.

What the sentence did not change: a bare `assertTrue(rs.next())` with no message appears in three of the four cells
(§7's message rule, which is in `SKILL.md`, not in a reference), and r09 put its integration test in a new class
beside `V3ParameterListTests` rather than in the existing integration test class, which is §9 again. The sentence
buys the reference files a reader; the rules in the body still have to be followed on their own.
