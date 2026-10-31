You are the author of pgjdbc/pgjdbc pull request "Reject a negative fetch size in PgStatement.setFetchSize". The
change makes `setFetchSize(int rows)` throw `PSQLException` with SQLState `22023` (`INVALID_PARAMETER_VALUE`) when
`rows < 0`; before it, a negative value was stored and later sent to the server as the row limit of an `Execute`
message, where the backend treats any value below 1 as "no limit". The change adds `PgStatementFetchSizeTest`, which
runs without a database by constructing the statement over a stub connection.

A maintainer left one review comment on the pull request (not on a line):

> Thanks, a few things. The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather
> extend that one than add a new class. Throwing here could break applications that call `setFetchSize(-1)` to mean
> "fetch everything", which the old code silently allowed. And should `PgPreparedStatement` get the same check, or
> does it inherit it?

What you know, checked against the code:

- `StatementTest.testSetFetchSize` exists. It needs a running database (it extends `BaseTest4`), and it checks only
  that a positive value round-trips through `getFetchSize()`. It has no case for a negative value.
- The JDBC specification of `Statement.setFetchSize` says: "throws SQLException if a database access error occurs,
  this method is called on a closed Statement or the condition rows >= 0 is not satisfied." The fetch size `0` is the
  JDBC value for "no hint", and it fetches every row at once in pgjdbc.
- You searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql`: 4 hits, all in test code of
  other projects.
- `PgPreparedStatement extends PgStatement` and does not override `setFetchSize`, so the check applies to it too.
  `PgCallableStatement extends PgPreparedStatement`, also without an override.

Your positions: keep the new test class, because it runs without a database, and add the negative case to
`StatementTest.testSetFetchSize` only if the maintainer wants both; keep the exception, since the specification
requires it and `0` is the documented way to fetch everything; the inheritance question is answered by the code.

Write your reply, posted as a comment on the pull request directly under the maintainer's comment.
