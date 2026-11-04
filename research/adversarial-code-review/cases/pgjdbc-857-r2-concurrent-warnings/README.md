# Case: review pgjdbc/pgjdbc#857 at e93883c6, warnings read and cleared while the statement still runs

A review case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#857][pr] at `e93883c6`, three commits on top of
`9f722014`. The change makes `Statement.getWarnings()` and `ResultSet.getWarnings()` return warnings as soon as the
backend sends them, and lets another thread read and clear them while the query runs, through a new class
`PGSQLWarningWrapper`. The gold comes from the inline comments a maintainer left on the third commit in July 2017, a
manual review written before agents reviewed code. The author replied in the thread or changed the code near each of the
four.

This is the second review round. The findings of the first round are not given to the model, and an earlier finding that
the model reports again is not counted against the run.

The code base is the pgjdbc of 2017: Java 6 to 8, JUnit 4, anonymous `Callable` classes instead of lambdas. This is
older than the pgjdbc the model usually knows. A finding that names today's API instead of the code at `e93883c6` is not
a pass.

The prompt names neither the pull request nor its author.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/857

## What it exercises

- Area *Correctness and data integrity*: the concurrency path of a producer thread (the result handler) and a consumer
  thread (`getWarnings` and `clearWarnings`) sharing one warning chain.
- Area *Compatibility and evolution*, bullet *Contracts*: a new public class in a package users import.
- Area *Verification and documentation*: tests that would catch an incorrect implementation and do not depend on timing.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **A cleared result set gets its old warnings back.** Pass: a finding that `CursorResultHandler.handleWarning` in
   `pgjdbc/src/main/java/org/postgresql/jdbc/PgResultSet.java:1776-1779` sets `PgResultSet.this.warnings =
   this.getWarning()`, the head of the handler's own chain, which `ResultHandlerBase` keeps from the first warning on.
   After a consumer calls `ResultSet.clearWarnings()` (line 2555), the next warning puts the whole old chain back, so
   the consumer processes the warnings it already cleared a second time. Partial: the report names a race on
   `PgResultSet.warnings` (not `volatile`, line 108) or on the handler, without the old chain coming back after a
   clear. Fail: neither.
   `grep -niE 'handleWarning|getWarning\(\)|clearWarnings|PgResultSet' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/857#discussion_r129515812))
2. **The wrapper becomes public API.** Pass: a finding that `PGSQLWarningWrapper`
   (`pgjdbc/src/main/java/org/postgresql/util/PGSQLWarningWrapper.java:16`) is a `public class` in
   `org.postgresql.util`, the package that holds `PSQLException` and other classes users import, so the driver would
   have to keep it compatible; the fix is an internal package or a Javadoc note that it is not for users. Partial: the
   report raises only its name (the `PSQL` prefix of `PSQLWarning` and `PSQLState`). Fail: neither.
   `grep -niE 'PGSQLWarningWrapper|public API|org\.postgresql\.util|internal' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/857#discussion_r129516359))
3. **The concurrency test checks only the count and the last warning.** Pass: a finding that
   `testConcurrentWarningReadAndClear` in `pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java:491-513`
   counts warnings and asserts only that the last one is `"Warning " + iterations`, so it should assert each warning's
   message in order; a duplicated or skipped warning then fails at the warning where it happens. Partial: the report
   calls the test weak or names its 2-second timeout as the only failure signal, without asking for an assertion per
   warning. Fail: neither.
   `grep -niE 'testConcurrentWarningReadAndClear|each warning|lastProcessed|Warning %' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/857#discussion_r129514907))
4. **The early-warning test depends on timing.** Pass: a finding that `testWarningsAreAvailableAsap` (lines 425-456)
   reads the warnings from a task scheduled 1000 ms after the start while the function runs `pg_sleep(2)`, so on a slow
   machine the check can run before the notices arrive or after the statement ends; the fix holds the statement
   deterministically, for example with a row lock taken by a second connection or a latch. Partial: the report names
   the sleep or the scheduled read but treats it only as slow, not as a source of flaky results. Fail: neither.
   `grep -niE 'testWarningsAreAvailableAsap|pg_sleep|1000|flak|timing|row lock' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/857#discussion_r129517623))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity* (races, state transitions)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, bullet *Contracts*
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, the first paragraph

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `9f72201458d1ce0837e9525d947dcea2828b9475` (the parent of the pull request's first commit), and `e93883c6f074ce24c2646ee875db8bf2ce070718` (the reviewed commit, the third of the pull request). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-857-r2-concurrent-warnings <model> <label> <rev>
```
