# Case: write the tests NullAway#1834 owes, from its production change

A regression case for `test-authoring`, the counterpart of [`nullaway-1834-rewrite`](../nullaway-1834-rewrite/README.md)
with no tests to start from. The input is the production change of
[uber/NullAway#1834](https://github.com/uber/NullAway/pull/1834) on its base `09fdea5a`, with the commit message of the
pull request and without its tests: commit `614efcf2`, tagged `test-authoring/nullaway-1834-no-tests` in
[vlsi/NullAway](https://github.com/vlsi/NullAway). The clone is two commits deep, so the submitted tests are not in the
history the session can read.

The rewrite case shows whether the skill repairs a form it is handed. This one shows which form the skill produces on
its own, and whether it finds the cases the change owes.

## What it exercises

- **The cases the change owes** (§3, §4). The commit message names the behaviors: a type variable whose bound admits
  null fails a `? extends Object` requirement, a `@Nullable` written on the use is compared as written, a declaration in
  unannotated code admits null, `Box<S>` with `S extends @Nullable T` fails `? extends T`, `Box<T>` fails
  `? extends @NonNull T`, `Box<T>` and `Box<S extends T>` stay assignable to `Box<? extends T>`, and a captured type
  argument is taken as written, so it meets a requirement that names a type variable.
- **A case and its controls in one check, and one case that expects a diagnostic per test** (§7), as in the rewrite
  case.
- **A helper that takes a value, not pieces of syntax** (§7), as in the rewrite case.
- **A new test takes the shape of its neighbors** (§9). `WildcardTests.java` writes each source as one text block
  passed to `makeHelper().addSourceLines(...)`.

## Files

| File | What it is |
| --- | --- |
| `tag` | The tag in `vlsi/NullAway` the session starts from. |
| `prompt.md` | The task given to the session, with `<skill>` replaced by the path of the skill copy. |
| `<model>/result.diff` | What the session changed in the production code (expected empty), then the tests relative to `09fdea5a`. |
| `<model>/result-note.md` | The session's closing message to the author of the pull request. |
| `<model>/skill-tree` | The tree id of the skill that produced the result. |
| `<model>/result-build.txt` | For the fix and for the base: the tests that ran and the ones that failed, or the build's exit status where it failed before any test ran. |
| `<model>/run.txt` | The session's cost in dollars, its turns and duration, and whether it ran the tests itself. |

## How to run

As in [`nullaway-1834-rewrite`](../nullaway-1834-rewrite/README.md#how-to-run), with this directory as the case:

```bash
research/test-authoring/cases/run-nullaway-case.sh \
  research/test-authoring/cases/nullaway-1834-from-scratch <model> <rev>
```

## Checks

Read `result.diff` and `result-note.md` against all of them.

1. **The defect is caught** (§3). One test expects an `incompatible types` diagnostic on passing a `Box<T>` with
   `<T extends @Nullable Object>` to a `Box<? extends Object>` in `@NullMarked` code. The existing tests in
   `WildcardTests.java` write the marker both ways, with the two types and as `incompatible types` alone, so either
   passes.
2. **Each behavior the commit message names has a case** (§4): the seven listed under *What it exercises*. Each case
   that expects no diagnostic, such as `Box<S extends T>` into `Box<? extends T>`, counts.
3. **Each case that expects a diagnostic stands with its controls** (§7). The nearest input that differs in the one
   annotation or bound deciding the diagnostic sits in the same source: `<T>` beside `<T extends @Nullable Object>`,
   `Box<? extends @Nullable Object>` beside `Box<? extends Object>`.
4. **One case that expects a diagnostic per test** (§7), and at most one input whose outcome the fix moves, which check
   8 shows. The harness stops at the first mismatch.
5. **No source is assembled from pieces** (§7). Each source is one text block, in the form of the tests around it
   (§9).
6. **The name states the rule** (§7). No ordinal, no line number, and no `And` or `But` joining the outcomes of two
   inputs. An `And` inside the condition of one rule passes.
7. **The production code is unchanged.** The session proposes the stack line (§0) in its closing message and does not
   edit `AGENTS.md`.
8. **The tests pass on the fix, and the defect's test fails on the base** (§5). Read `result-build.txt`: no failure on
   the fix, and on the base a failure for the test of check 1.

Checks 4 to 7 are partly countable. A result that passes has one marker at most per test. The markers may stop at
`incompatible types`, so the script is given no diagnostic to look for; read which declaration each marker sits on:

```bash
python3 research/test-authoring/cases/check-nullaway-case.py \
  research/test-authoring/cases/nullaway-1834-from-scratch/claude-opus-5-5
```
