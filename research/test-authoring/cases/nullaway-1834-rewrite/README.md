# Case: rewrite the split positive and negative tests of NullAway#1834

A regression case for `test-authoring`. The input is [uber/NullAway#1834](https://github.com/uber/NullAway/pull/1834) as
submitted, commit `d55c1507`, tagged `test-authoring/nullaway-1834-split-pairs` in
[vlsi/NullAway](https://github.com/vlsi/NullAway). It adds 20 tests to `WildcardTests.java`: 9 expect a diagnostic, and
11 expect none. Each test carries its own copy of the class it compiles, and a case that expects no diagnostic is a
separate test from the case it controls. The reviewer asked for the two in one test, so that the reader does not process
the same setup twice ([the comment][review]), and the rules of version 1.1.0 on related cases started from that comment.

[review]: https://github.com/uber/NullAway/pull/1834#discussion_r4011039854

## What it exercises

- **A case and its controls in one check** (§7, the sub-bullet *A case and its controls are not independent*). Error
  Prone's `CompilationTestHelper` compiles one source and matches every `// BUG: Diagnostic contains:` marker. It stops
  at the first marker without a diagnostic and names it by line. A case that expects a diagnostic goes into one source
  with the nearest inputs that do not, and a second case that expects a diagnostic is a second test.
- **A helper that takes a value, not pieces of syntax** (§7, the sub-bullet *A helper leaves the reader the whole
  input*). An earlier draft of 1.1.0 led four of four Opus runs to assemble each source from a type parameter list, a
  statement, and a marker with `String.formatted`.
- **No case is lost when the tests collapse** (§4). The rewrite changes the form; each of the 20 inputs keeps its
  expectation.
- **The stack line is proposed, not written** (§0). NullAway has an `AGENTS.md`; the skill proposes the line that
  records the harness's stop-at-first behavior, and the session does not add it.

## Files

| File | What it is |
| --- | --- |
| `tag` | The tag in `vlsi/NullAway` the session starts from. |
| `prompt.md` | The task given to the session, with `<skill>` replaced by the path of the skill copy. |
| `<model>/result.diff` | What the session changed in the production code (expected empty), then the tests relative to the base of the pull request, `09fdea5a`. |
| `<model>/result-note.md` | The session's closing message to the author of the pull request. |
| `<model>/skill-tree` | The tree id of the skill that produced the result. |
| `<model>/result-build.txt` | The tests that fail on the fix and on the base, from the build the script runs after the session. |
| `<model>/run.txt` | The session's cost in dollars, its turns and duration, and whether it ran the tests itself. |

## How to run

From the repository root, with `<rev>` the commit that holds the skill under test, or no `<rev>` for the working copy:

```bash
research/test-authoring/cases/run-nullaway-case.sh \
  research/test-authoring/cases/nullaway-1834-rewrite <model> <rev>
```

The script copies the skill out of the checkout, clones NullAway at the tag into a temporary directory, runs
`claude -p --safe-mode` there with `prompt.md`, and writes the files above once the session succeeds. Safe mode keeps
every installed skill, every user rule, and every `CLAUDE.md` out of the session, including the installed copy of
`test-authoring` and this repository's `AGENTS.md`. It drops NullAway's own `CLAUDE.md` too, so the script appends that
file to the system prompt, where a consumer's session would have it.

The session may run the build, as a writer of tests would. Whatever it ran, the script then runs the test classes the
session changed, on the fix and on the base `09fdea5a`, and records the failures in `result-build.txt`. The script
prints the temporary directory, which holds the NullAway tree and the two build logs.

## Checks

Read `result.diff` and `result-note.md` against all of them.

1. **Every case survives with its expectation** (§4). The 9 diagnostics of the submitted tests are expected verbatim,
   and every one of the 11 inputs that expected no diagnostic is still compiled with no marker on it. Map each of the
   20 submitted inputs to a line of the result; a missing input fails, and so does an input whose type parameters or
   annotations changed.
2. **Each case that expects a diagnostic stands with its controls** (§7). A control is a nearest input that differs in
   the one annotation or bound that decides the diagnostic: `<T>` beside `<T extends @Nullable Object>`,
   `Box<? extends @Nullable Object>` beside `Box<? extends Object>`. It sits in the same source as the case it
   controls. An input that expects nothing and controls no case, such as a captured type argument, may stay a test of
   its own.
3. **One case that expects a diagnostic per test** (§7). The harness stops at the first mismatch, so two markers in one
   test fail, however closely the two rules are related.
4. **No source is assembled from pieces** (§7). No `String.formatted`, `String.format`, or concatenation builds a
   source, and no helper takes a type parameter list, a statement, or a marker. The source of each test is one text
   block the reader sees whole.
5. **The name states the rule** (§7). No ordinal, no line number, and no `And` joining two rules.
6. **The production code is unchanged, and so are the other tests.** The session proposes the stack line (§0) in its
   closing message and does not edit `AGENTS.md`.
7. **The closing message names what moved and why**, and the rule of the skill behind each move.
8. **The rewritten tests pass on the fix, and each test with a marker fails on the base** (§5). Read
   `result-build.txt`: no failure on the fix, and on the base a failure for every test that expects a diagnostic the
   fix added.

Checks 1 to 6 are partly countable. For the submitted tests the script prints 20 tests, 11 of them with no marker. The
two captured type arguments control no case that expects a diagnostic, so they may stay tests of their own; every other
input joins one of the 9 tests with a marker. A result that passes has at most 11 tests, at most 2 of them with no
marker, one marker at most per test, and prints `True` for every diagnostic:

```bash
python3 research/test-authoring/cases/check-nullaway-case.py \
  research/test-authoring/cases/nullaway-1834-rewrite/claude-opus-5-5 \
  'incompatible types: Box<T> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<@Nullable T> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<S> cannot be converted to Box<? extends Object>' \
  'incompatible types: Box<@Nullable T> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<S> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<T> cannot be converted to Box<? extends T>' \
  'incompatible types: Box<? extends T> cannot be converted to Box<? extends Object>' \
  'mismatched type parameter nullability'
```

The diagnostic `Box<T> cannot be converted to Box<? extends Object>` is expected twice in the submitted tests, once for
a bound written in `@NullMarked` code and once for a declaration in unannotated code; the script checks only that it
appears, so read the second one.
