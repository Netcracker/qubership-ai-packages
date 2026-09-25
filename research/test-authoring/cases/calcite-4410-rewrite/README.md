# Case: rewrite the copied fixture chains of Calcite#4410

A regression case for `test-authoring`. The input is [apache/calcite#4410](https://github.com/apache/calcite/pull/4410)
as the reviewer saw it, commit `93e698ac`, applied to `cf91ec8f36`, the parent of the merged squash `252d6aa7d4e9`. The
change makes `SqlValidatorImpl` expand a common column of `JOIN ... USING` and `NATURAL JOIN` when identifier expansion
is on, matching names case-insensitively where the validator does. It adds two tests to `SqlValidatorTest`, each with
four `sql("…")…ok()` calls. Every call repeats the same fixture chain of four `with…` calls, and no call expects an
error.

The reviewer, Julian Hyde, asked for a helper method "so that each test becomes ~2 lines", for cases where the column
differs in case between the two tables or appears twice in one table, and for negative tests ([the comment][review]).
The merged version answers with a cartesian product of table and column names, formatted into SQL with `String.format`
and run in a loop inside one `@Test`. Grade against the skill, not against the merged diff.

[review]: https://github.com/apache/calcite/pull/4410#discussion_r2144186613

The production code of `93e698ac` and of the merged commit behave alike: the merge moved the methods into the `Expander`
class and replaced `Util.matches` with `SqlNameMatcher`. The merged tests pass on the production code of this case.

## What it exercises

This is the first case whose unit takes one input per call. NullAway's harness compiles one source and checks many
markers; Calcite's `SqlValidatorFixture` validates one statement per `ok()` or `fails()` call, and a failure names the
query in its message.

- **One behavior per test** (§7, *One behavior per test*). Each `sql(…).ok()` is an act; a second call on another input
  is a second scenario. The submitted tests hold four acts each.
- **Cases that share a setup write it once** (§7, *Cases that share a setup write it once*, with the sub-bullets *A
  helper leaves the reader the whole input* and *The form follows the assertions*). The shared part is the fixture
  chain, not the SQL. A helper that returns the configured fixture and takes the query whole passes; a helper or a loop
  that builds the query from table and column names with `String.format` fails. Cases that pass and cases that fail
  assert differently, so they are separate tests or two parameterized tables.
- **A loop over a table of literal cases in one test** (§7 and §9, *A new test takes the shape of its neighbors*). The
  neighbors of `SqlValidatorTest` put several `sql()` calls in one test, and the skill wins over that shape.
- **Which inputs** (§4). The change touches how a column name is matched, so the partitions are the case of the selected
  column, of the `USING` column, and of each table's column, under a case-sensitive and a case-insensitive matcher, for
  `USING` and for `NATURAL`. The negative partitions are the reviewer's request.
- **Red on the base** (§1, §5). Each test of a partition the change moves fails on `cf91ec8f36`.
- **The stack line is proposed** (§0). Calcite has no `AGENTS.md` or `CLAUDE.md`; the session proposes the line and
  creates no file.

## Files

| File | What it is |
| --- | --- |
| `repo`, `base` | `apache/calcite` and `cf91ec8f36e1f7cf9656e2f794d8f78a2b43d88c`, the parent of the merged squash. |
| `change.patch` | `git diff 12e7d621 93e698ac`: the production change and the two tests the reviewer saw. It applies to `base` cleanly. |
| `change-message.txt` | The subject of the pull request's first commit. |
| `production-paths` | `core/src/main`. |
| `build.sh` | Runs `SqlValidatorTest` and every other test class under `core/src/test/java` that differs from `base`, and prints the count and the failed tests. |
| `prompt.md` | The task, with `<skill>` replaced by the path of the skill copy. |
| `<model>/…` | The outputs `run-case.sh` writes; its header lists them. |

`build.sh` needs a JDK that Gradle 8.7 runs on; JDK 21 was used. A warm run of `SqlValidatorTest` (547 tests) takes
about 20 seconds; the first run in a fresh checkout compiles `core` and takes about 2.5 minutes.

## How to run

From the repository root:

```bash
research/test-authoring/cases/run-case.sh research/test-authoring/cases/calcite-4410-rewrite <model> [<rev>]
```

## Behaviors on the base

A run of one input per test showed which inputs the change moves, with emp and dept of the default mock catalog, whose
column is `DEPTNO`:

| Input | Case-sensitive | On the base | On the fix |
| --- | --- | --- | --- |
| `select DEPTNO from emp join dept using (DEPTNO)` | no | passes | passes |
| `select deptno from emp join dept using (deptno)` | no | `AssertionError` | passes |
| `select DEPTNO from emp join dept using (deptno)` | no | `Column 'DEPTNO' is ambiguous` | passes |
| `select deptno from emp join dept using (DEPTNO)` | no | `Column 'deptno' is ambiguous` | passes |
| `select DEPTNO from emp natural join dept` | yes | `Column 'DEPTNO' is ambiguous` | passes |
| `select deptno from emp natural join dept` | no | `Column 'deptno' is ambiguous` | passes |
| `select DEPTNO from emp natural join dept` | no | `Column 'DEPTNO' is ambiguous` | passes |

`NATURAL JOIN` failed on the base under a case-sensitive matcher too: the change adds the expansion of a natural join's
common column, not only case-insensitive matching.

## Checks

Read the changed files against `base` (`git diff <base>` in the session's clone, or the file beside `changed-files.txt`
against its version at `base`) and `result-note.md` against all of them.

1. **Every submitted input survives with its expectation** (§4). The 8 queries of the submitted tests, each with its
   case-sensitivity setting, are each validated by some test of the result and still expected to pass. A missing input
   fails, except where the closing message shows it is the same query as one that stays: under a case-sensitive matcher
   the default casing upper-cases `deptno`, so the two case-sensitive `NATURAL JOIN` queries are one (§4, a redundant
   case). No other drop passes: an input that passes on the base is a control, not a redundant case, and the
   case-insensitive `NATURAL JOIN` with `DEPTNO` is a partition of its own (the table above).
2. **The partitions the change moves have a case each** (§4): a `USING` column spelled in another case than the table
   column; a selected column spelled in another case than the `USING` column; a `NATURAL JOIN` common column under a
   case-sensitive matcher; and one under a case-insensitive matcher in another case. A case where the two tables spell
   the column differently (a custom catalog, or derived tables with quoted aliases) passes this check with credit; it is
   not required, because the session was not told about the reviewer's question.
3. **At least one negative case with the error position** (§4, and the reviewer's request). Under a case-sensitive
   matcher, a name that differs from the column only in case is rejected, written with `^…^` around the offending
   identifier and `fails("…")` with the part of the message the behavior defines (`Column '…' not found`). A negative
   case written as `ok()`, or with no position marker, fails.
4. **One act per test, or one runner case per act** (§7). No test calls `sql(…)` twice on unrelated inputs, and no test
   loops over inputs inside one `@Test`. A `@ParameterizedTest` whose rows are literal queries with named cases, or a
   `@TestFactory` of dynamic tests, passes. A test that holds a case and its control as two `sql()` calls fails: each
   call is its own act.
5. **The shared setup is written once, and the query is written whole** (§7, §9). The fixture chain appears once, in a
   helper or a fixture field, and each test passes its full SQL text to it. No `String.format`, `formatted`, or
   concatenation builds a query from table or column names, and no `Sets.cartesianProduct` appears. Repeating the
   four-call chain in every test fails.
6. **Passing and failing cases take different forms** (§7, *The form follows the assertions*). No row field or flag
   selects between `ok()` and `fails()`.
7. **Names state the scenario and the outcome** (§7). No ordinal, no `CaseSensitive` on a test of case-insensitive
   matching, and no `And` joining the outcomes of two inputs. Calcite's `test` prefix passes.
8. **The production code is unchanged**, and no `AGENTS.md` or `CLAUDE.md` is created. The closing message proposes a
   stack line (§0), such as JUnit 5 with Hamcrest and Calcite's fixtures.
9. **Red on the base, green on the fix** (§1). Read `result-build.txt`: no failure on the fix, and on the base a failure
   for every test of an input the table above marks as moved. Tests of a control, such as the all-uppercase `USING` case
   or a negative case, may pass on the base.
10. **The closing message names what moved and why.** It passes where it gives, for each move, the section of the skill
    behind it (`§7`, `§9`, or the rule's words), and says that the tests no longer take the neighbors' shape of several
    `sql()` calls in one test (§9). A message that names what moved but neither of those is partial.
