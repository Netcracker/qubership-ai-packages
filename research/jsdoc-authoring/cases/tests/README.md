# Case: a new test class, `jsdoc-authoring`

The input is a new test file (TypeScript, Vitest) with four tests: two ordinary ones whose names state what they check,
a regression test with a descriptive name (`counts only the value in evictedBytes`, issue #57: a wrong total, nothing
thrown), and a guard test (`has a handler for every event`) whose fix is an edit outside the code under test, adding a
handler and listing the event in `HANDLED`. The task says nothing about which test deserves a comment. The case is the
negative control for the regression-test exception in §1 and the Use slot of the test genre: before 1.3.0 both read as
owed on every test.

## Skill parts

- `SKILL.md`: §1 (the regression-test exception), §2 (sizing), §4 (Test file), §7 (When to write nothing), §8 (the
  checklist items that restate those)
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

1. **The ordinary tests get no comment.**
2. **No defect history on the regression test.** No `used to` sentence and no issue number; its name states the rule. A
   line on the construction (the key is longer than the value, so a counted key changes the total) is allowed (§3).
3. **The guard test names the edit that turns it green.** A comment that sends the reader to the dispatcher or to
   `HANDLED`.
4. **No file comment** restating the test names.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on `a51171b`
(`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`. Check 1 and check 4 passed in every run of
both arms.

| Arm | No history (2) | Guard names the fix (3) |
| --- | --- | --- |
| Baseline | 4 of 4 fail | 0 of 4 pass: no comment |
| 1.3.0 draft | 4 of 4 fail | 0 of 4 pass: no comment |
| 1.3.0 | Opus r1, r2 and Sonnet r1 pass; Sonnet r2 fails: the defect sentence, inline beside the key-length line | Opus r2 and Sonnet r1 pass; Opus r1 fails: no comment anywhere; Sonnet r2 fails: no comment on it |

A first draft of 1.3.0 said only that a test whose name states its rule needs no comment; its runs are the *1.3.0 draft*
row and are not committed. 1.3.0 ties the no-comment case to a failure fixed in the code under test, and sends the
defect and the issue number to the commit that adds the test. Across the five skills, a defect sentence remains in 2 of
20 runs (baseline 20 of 20), and the guard test names its fix in 16 of 20 (baseline 12 of 20). A run of the same rules
before a final-review pass, which moved one sentence, named it in 19 of 20, so the guard result varies from run to run.
