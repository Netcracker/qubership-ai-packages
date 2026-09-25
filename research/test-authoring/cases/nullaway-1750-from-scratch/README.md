# Case: write the tests NullAway#1750 owes, from its production change

A regression case for `test-authoring` on a fix that removes a false positive. The NullAway#1834 cases fix a missed
report, so the case they are named for expects a diagnostic. Here the case the change moves expects none, and its
nearest control is the input that expects one. The input is the production change of
[uber/NullAway#1750](https://github.com/uber/NullAway/pull/1750), merged as `f1ab72aa8b`, on its parent `bbceff5dd`,
without the changes the pull request made to `FrameworkTests.java`.

Before the fix, `SpringHandler` treated a Spring `@Value` field as possibly uninitialized whenever its SpEL expression
`#{...}` contained the token `null`. A field such as `@Value("#{someBean != null ? someBean.value : 'default'}")` drew
`@NonNull field '...' not initialized` although `null` there is only an operand of a comparison. The fix removes
`== null`, `!= null`, `null ==`, and `null !=` from the expression before it looks for `null` again, so
`#{someBean != null ? null : 'default'}` is still reported.

## What it exercises

- **A case and its controls are not independent** (§7), in the form the sub-bullet names for a fix that removes a false
  report: the case is silent, and its controls expect reports. Error Prone's `CompilationTestHelper` stops at the first
  mismatch, so a test holds one case: at most one input whose outcome the change moves, and no input that expects a
  report other than the case and its controls.
- **Drift costs most in a case that expects nothing** (§7). The silent field establishes the rule only while a field
  that differs in where `null` sits fires on the same source.
- **Two partitions the change moves are two tests** (§7). `null` to the right of the operator and `null` to the left
  are separate alternatives of the new pattern, and the commit message names both (`comparisons with null on either
  side`). The pull request's own `springValueSpelNullComparisonLeftSide` puts two moved inputs in one source, and on the
  base the second is hidden behind the first.
- **A new test uses the helpers the file already has, and a copied setup moves into one** (§7 *A short setup is
  repeated*, §9). On the base, the `Value` annotation stub is written out inside `springValueFieldTest`. A new test
  needs the same stub, and the pull request moved it into `addSpringValueAnnotationStub`, which `springValueFieldTest`
  now calls with its expectations unchanged. The stub is fixed text no expectation depends on, so the helper is
  infrastructure (§9).
- **The twin that already holds a case** (§9). `springValueFieldTest` is the existing test of the rule, and its markers
  are cases of their own, not controls of the new silent case. The new case is a test of its own, and the twin keeps its
  name and its expectations.
- **A helper that takes a value, not pieces of syntax** (§7). A helper that splices a SpEL expression and a marker into
  a class fails.
- **The stack line** (§0). NullAway's `AGENTS.md` has none, so the session proposes one and edits no instructions file.

## Files

| File | What it is |
| --- | --- |
| `repo`, `base` | `https://github.com/uber/NullAway.git` and `bbceff5dd398b268ed1cb588910d2a5f0519aa28`, the parent of the merge. |
| `change.patch` | The diff of `nullaway/src/main` between `bbceff5dd` and `f1ab72aa8b`: `SpringHandler.java` alone. |
| `change-message.txt` | The squash-merge message of `f1ab72aa8b` without its `New tests` and `Unit tests` sections and the `Tests` bullets of the CodeRabbit summary, which name the tests the session is asked to write and contradict a commit that adds none. |
| `production-paths` | `nullaway/src/main`. The pull request does not touch `CHANGELOG.md`. |
| `build.sh` | Runs every test class under `nullaway/src/test/java` that differs from `base`, with `./gradlew :nullaway:test --rerun --quiet`, and prints how many tests ran and which failed. |
| `prompt.md` | The task given to the session, with `<skill>` replaced by the path of the skill copy; the same text as `nullaway-1834-from-scratch`. |
| `<model>/` | The output of `run-case.sh`: the changed files under their own names, `changed-files.txt`, `result-note.md`, `result-build.txt`, `run.txt`, `skill-tree`. |

The infrastructure was checked without a model on 2026-09-25: the pull request's own tests applied on top of the case
commit give `73 tests ran, 0 failed` on the fix (59 s with a warm Gradle cache), and on the base
`73 tests ran, 2 failed`, `springValueSpelWithNullInConditional` and `springValueSpelNullComparisonLeftSide` (15 s).

## How to run

From the repository root:

```bash
research/test-authoring/cases/run-case.sh research/test-authoring/cases/nullaway-1750-from-scratch <model> [<rev>]
```

## Checks

Read the changed files against `base` (`git diff <base>` in the session's clone, or the file beside `changed-files.txt`
against its version at `base`) and `result-note.md` against all of them.

1. **The false positive is caught** (§1, §3). One test holds a field whose SpEL expression mentions `null` only as the
   right operand of `!=` or `==`, such as `#{someBean != null ? someBean.value : 'default'}`, with no marker on it, and
   that test fails on the base.
2. **The silent case stands with its reporting control in one source** (§7). The nearest input that differs in where
   `null` sits, `null` as a possible value of the same expression such as `#{someBean != null ? null : 'default'}`,
   carries `// BUG: Diagnostic contains:` in the same `addSourceLines` source. A control in a second source of the same
   test is partial, since the two sources can drift apart. A control in a separate test with its own copy of the class
   fails this check.
3. **Each partition the change moves has a case** (§4): `null` on the right of the operator (check 1) and `null` on the
   left (`#{null != someBean ? ...}`). Varying `==` against `!=` is not required; a case for each passes. A case read
   off the pattern rather than the specification, such as `someBean!=null` for the `\s*`, passes too, and the grade
   notes it (§4).
4. **One case per test** (§7). Count the silent fields that mention `null` in a comparison in each test the session
   added or changed: at most one. Two moved inputs in one test, as in the pull request's
   `springValueSpelNullComparisonLeftSide`, fail. Every marker in the test is a control of that case, such as `null` in
   the then branch or in the else branch of the same expression; a marker of another case, such as the existing markers
   of `springValueFieldTest`, fails.
5. **The `Value` stub is written once** (§9). The new tests and `springValueFieldTest` reach it through one helper, and
   `springValueFieldTest` keeps its expectations. A second verbatim copy of the stub fails, and so does a new helper
   while the old copy stays inline in `springValueFieldTest`. A result with no new test fails this check too.
6. **No source is assembled from pieces** (§7). Each test source is one text block in the form of its neighbors (§9).
   No helper takes a SpEL expression together with a field name, a marker, or another piece of syntax and splices them
   into a class.
7. **The name states the rule** (§7). No ordinal, no issue number, and no `And` or `But` joining the outcomes of two
   inputs; `Unless` or `OnlyWhen` stating the condition of one rule passes. A test that now holds the new case keeps no
   name that states only an older rule, such as `springValueFieldTest`; where the rule has a test per partition, the
   name also states the partition, such as the side of the operator `null` is on.
8. **The production code is unchanged.** `changed-files.txt` has no `production` line. The session proposes the stack
   line (§0) in its closing message, with the text of the line, for `AGENTS.md` or `CLAUDE.md`, and edits neither.
9. **Green on the fix, red on the base for each moved case** (§1). Read `result-build.txt`: no failure on the fix, and
   on the base a failure for every test that holds a silent field with `null` in a comparison and for no other test: at
   least two, one with `null` on the right and one with `null` on the left. `springValueFieldTest` passes on both.
