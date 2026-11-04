# Case: review pgjdbc/pgjdbc#4443 at 0dec6811, a 25-line XA fix whose tests leave its own claims unchecked

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#4443][pr] at `0dec6811`, one commit on
top of `87474525`. The gold answer comes from the maintainer's inline comments on that commit: eight comments, of which
four are used here, and the author replied in the thread or changed the code near each of them. The review was written
in 2026, and reviews from 2025 on may have been written with an agent's help. An earlier review of a previous version of
the pull request, written as a review summary with no inline comments, is not given to the model; a problem from it that
is still present at `0dec6811` is a valid finding.

The change makes `PGXAConnection` report `XAER_RMFAIL` instead of `XAER_RMERR` when the backend dies during
`rollback()`, two-phase `commit()`, or `recover()`. The new helper `connectionIsGone` accepts an SQLSTATE of class 08 or
a closed connection. The production change is about 25 lines; the rest of the diff is four new tests in
`XADataSourceTest`. The commit message names two triggers, `57P01` from `pg_terminate_backend()` and `57P05` from
`idle_session_timeout`, and the `recover()` change. The tests exercise only the first trigger, do not reach `recover()`,
and one of them checks nothing the driver controls.

The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/4443

## What it exercises

- Area *Verification and documentation*: tests that would catch an incorrect implementation, and the claims of the
  commit message checked against the tests that exist.
- Area *Reliability, operability, and observability*: actionable logs, on a branch whose condition the change widened.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **A test that checks nothing the driver controls.** Pass: a finding about
   `committedBranchMustNotBeReportedAsRolledBack` (`XADataSourceTest.java` line 1443) that names at least one of: its
   row-count assertion at line 1459 checks the `COMMIT PREPARED` the test itself ran and cannot fail on any driver
   change; `assertNotEquals(XAException.XAER_RMERR, ...)` at line 1460 also passes on `XAER_NOTA` or any other wrong
   code; it runs that `COMMIT PREPARED` on `conn`, the XA connection's own session, under a comment that says the client
   never learns about it; it picks the gid with `preparedGids(dbConn).get(0)` instead of `gidOf(xid)`; or it duplicates
   `commitPreparedAfterBackendTerminationOfACommittedBranchMustReportRmfail` (line 1472), which tests the same scenario
   with the same `CustomXid(2)` and should replace it. Partial: the report says the new tests overlap without naming
   this test or a defect in it. Fail: neither.
   `grep -niE 'committedBranchMustNotBe|assertNotEquals|testxa1RowCount|get\(0\)|duplicat' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4443#discussion_r4347320709))
2. **No test for `57P05`.** Pass: a finding that the commit message and the `CHANGELOG.md` entry name `57P05`
   (`idle_session_timeout`) as a trigger, but every new test ends the session with `pg_terminate_backend()` (`57P01`,
   through `terminateBackendAndWait`), so the idle-timeout path has no test; the remedy is a test that sets
   `idle_session_timeout` between `prepare()` and `commit()`, on PostgreSQL 14 or later. Partial: the report says the
   tests cover only one way for the backend to die without naming `57P05` or `idle_session_timeout`. Fail: neither.
   `grep -niE '57P05|idle_session|idle session' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4443#discussion_r4347320725))
3. **The `recover()` change has no test.** Pass: a finding that `recover()` now reports `XAER_RMFAIL` when
   `connectionIsGone` holds (`PGXAConnection.java` lines 440-442), yet no new test calls `recover()` after the backend
   is terminated; the only `recover()` error test runs on a live connection and expects `XAER_RMERR`. Partial: the
   report notes untested branches of `connectionIsGone` without naming `recover()`. Fail: neither.
   `grep -niE 'recover' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4443#discussion_r4347320734))
4. **The debug line does not say why the connection counts as gone.** Pass: a finding that the debug messages in
   `rollback` (line 510) and `commitPrepared` (line 651) still read `connection failure (sql error code ...)`, which now
   also fires on `conn.isClosed()` for an SQLSTATE that is not a connection error, such as `57P01`, so the log does not
   tell which condition produced `XAER_RMFAIL`; the remedy is to log `conn.isClosed()` or the deciding condition.
   Partial: the report says the log message is stale or misleading after the change without naming what is missing.
   Fail: neither.
   `grep -niE 'debug|log|reconnection could be expected|isClosed' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4443#discussion_r4347320769))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch an
  incorrect implementation
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Reliability, operability, and observability*, actionable
  logs

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `874745258455be18708d91a24cc98a0ae5ae85a3` (the parent of the pull request's commit), and `0dec68112f22aefbf446278bc77a4ddb0741e3ea` (the commit the review was written on). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-4443-xa-rmfail-tests <model> <label> <rev>
```
