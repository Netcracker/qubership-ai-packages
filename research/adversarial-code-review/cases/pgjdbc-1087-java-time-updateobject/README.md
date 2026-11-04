# Case: review pgjdbc/pgjdbc#1087 at d6d7e45f, a parameterized test whose values and failures are hard to reproduce

A review case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#1087][pr] at `d6d7e45f`, eleven commits on top
of `0d51370b`. The change teaches `PgResultSet.updateObject` to accept `LocalDate`, `LocalTime`, `LocalDateTime`, and
`OffsetDateTime`, and adds the parameterized test `UpdateObject310Test`. The gold comes from the inline comments a
maintainer left on this commit in January 2018, a manual review written before agents reviewed code. The author replied
in the thread or changed the code near each comment the checks below are built from; on the one about keeping the stack
trace, the reply says the author did not see how to do it.

The code base is the pgjdbc of early 2018: JDBC 4.2 code sits behind `//#if mvn.project.property.postgresql.jdbc.spec`
preprocessor comments, and the tests use JUnit 4. This is older than the pgjdbc the model usually knows. A finding that
names today's API or test helpers instead of the code at `d6d7e45f` is not a pass.

The prompt names neither the pull request nor its author. The pull request was rebased in 2021 and later closed without
a merge; the checks only ask about the test at this commit.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/1087

## What it exercises

The first paragraph of area *Verification and documentation*: tests that would catch an incorrect implementation, read
here as tests whose input is the same on every run and whose failure tells the reader what went wrong.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **Test values come from the clock.** Pass: a finding that `UpdateObject310Test.data()`
   (`pgjdbc/src/test/java/org/postgresql/test/jdbc42/UpdateObject310Test.java:41-44`) builds its parameters with
   `LocalDateTime.now()`, `OffsetDateTime.now()`, `LocalDate.now()`, and `LocalTime.now()`, so each run tests different
   values and a failure on one value cannot be reproduced; the fix is fixed literal values. Partial: the report asks for
   fixed or boundary values (a DST transition, midnight, dates before 1970) but does not say that `now()` makes the
   runs differ. Fail: neither.
   `grep -niE 'now\(|nondetermin|reproduc|clock|fixed value' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/1087#discussion_r164277172))
2. **The `fail` message names no exception.** Pass: a finding that `testWrongClass` ends the `try` block with
   `fail("should have thrown an Exception")` (line 117), which names neither the expected exception or SQLState
   (`PSQLState.DATATYPE_MISMATCH`) nor the column and value under test, so a failure of one parameterized case says
   little. Partial: the report says `testWrongClass` should state what it expects, without pointing at the `fail` call.
   Fail: neither.
   `grep -niE 'fail\(|should have thrown|testWrongClass' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/1087#discussion_r164277249))
3. **The caught exception is lost.** Pass: a finding that the `catch (PSQLException e)` block (lines 118-119) checks
   only `e.getSQLState()` with `assertEquals` and no message, so when the SQLState differs the `AssertionError` carries
   neither the message nor the stack trace of `e`; the fix keeps `e`, for example as the cause or in the assertion
   message. Partial: the report asks for an assertion message in `testWrongClass` but does not say the original
   exception is dropped. Fail: neither.
   `grep -niE 'stack ?trace|getSQLState|PSQLException|cause' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/1087#discussion_r164277266))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, the first paragraph
  (tests that would catch an incorrect implementation)
- `adversarial-code-review`: `SKILL.md` §Finding model and §Finding content, for a test defect reported as
  `non-blocking`

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `0d51370b68cd26ccfa92b0bae4a66da1015cf9ee` (the parent of the pull request's first commit), and `d6d7e45f13cd5f11300758de4646fa6011aa4324` (the reviewed commit, the eleventh of the pull request). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-1087-java-time-updateobject <model> <label> <rev>
```
