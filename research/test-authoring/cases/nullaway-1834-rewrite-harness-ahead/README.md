# Case: rewrite NullAway#1834's tests where the maintainers accept a form ahead of the harness

A regression case for `test-authoring`. The input is the same as in `nullaway-1834-rewrite`:
[uber/NullAway#1834](https://github.com/uber/NullAway/pull/1834) as submitted, commit `d55c1507`, tagged
`test-authoring/nullaway-1834-split-pairs` in [vlsi/NullAway](https://github.com/vlsi/NullAway), with 20 tests in
`WildcardTests.java`: 9 expect a diagnostic, and 11 expect none. The difference is in NullAway's instructions. The case
adds `instructions.md` to them, a stack line that describes Error Prone's `CompilationTestHelper` as it is (it stops at
the first mismatched marker and names it by line number) and asks for tests written as if it reported every mismatch and
told each marker apart.

[google/error-prone#6117](https://github.com/google/error-prone/pull/6117) makes the helper report every mismatched
line. A reviewer of NullAway may prefer the tests of one rule in one source now, and accept a second run to see the next
mismatch until that change is released. The case checks that the skill follows such a line instead of splitting by the
harness's current behavior.

## What it exercises

- **A stack line that accepts a form ahead of the harness** (§0, and §7's bullet *Independent cases in one check hide
  each other*). The session reads the harness's behavior from the line, writes the tests as the line asks, and proposes
  no change to the harness.
- **A case and its controls in one check** (§7), as in `nullaway-1834-rewrite`.
- **A helper that takes a value, not pieces of syntax** (§7), as in `nullaway-1834-rewrite`.
- **No case is lost when the tests collapse** (§4).

## Files

The files are those of `nullaway-1834-rewrite`, plus `instructions.md`, which `run-nullaway-case.sh` appends to
NullAway's `CLAUDE.md` in the session's system prompt.

## How to run

From the repository root, with `<rev>` the commit that holds the skill under test, or no `<rev>` for the working copy:

```bash
research/test-authoring/cases/run-nullaway-case.sh \
  research/test-authoring/cases/nullaway-1834-rewrite-harness-ahead <model> <rev>
```

## Checks

Read the changed test files against the base and `result-note.md` against all of them, as in `nullaway-1834-rewrite`.

1. **Every case survives with its expectation** (§4), as check 1 of `nullaway-1834-rewrite` states it.
2. **Each case that expects a diagnostic stands with its controls** (§7), in the same source, as check 2 of
   `nullaway-1834-rewrite` states it.
3. **Several markers of one rule may share a test** (§7). A split of two markers of one rule into two tests, justified
   by the harness stopping at the first mismatch, fails. Tests of different rules may stay apart.
4. **No source is assembled from pieces** (§7), as check 4 of `nullaway-1834-rewrite` states it.
5. **The name states the rule, or what the cases of the test share** (§7). No ordinal, no line number, and no `And` or
   `But` joining the outcomes of two inputs.
6. **The production code, the other tests, and `AGENTS.md` are unchanged.** The closing message proposes no stack line,
   since one exists, and no change to Error Prone for reporting every mismatch.
7. **The closing message names what moved and why**, and cites the stack line for the grouping. The line reaches the
   session in the system prompt, not in `AGENTS.md` on disk, so a citation of NullAway's instructions without a file
   path passes.
8. **The rewritten tests pass on the fix, and each test with a marker fails on the base** (§5), as check 8 of
   `nullaway-1834-rewrite` states it.

The snippet of `nullaway-1834-rewrite` counts the tests, the tests with no marker, and the markers, and checks every
diagnostic:

```bash
python3 research/test-authoring/cases/check-nullaway-case.py \
  research/test-authoring/cases/nullaway-1834-rewrite-harness-ahead/claude-opus-5-5 \
  'incompatible types: Box<T> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<@Nullable T> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<S> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<@Nullable T> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<S> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<T> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<? extends T> cannot be converted to Box<? extends Object>' \
  'mismatched type parameter nullability'
```

Its limits of `nullaway-1834-rewrite`, one marker at most per test, do not apply here. Compare the number of tests with
the result of `nullaway-1834-rewrite` for the same model and skill: a result that passes has fewer tests, or says why
not.
