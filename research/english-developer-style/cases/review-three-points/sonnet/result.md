## The test duplicates `StatementTest.testSetFetchSize`

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

`StatementTest.testSetFetchSize` has no negative case. It checks only that a positive value round-trips through `getFetchSize()`, so the two tests don't overlap. It also extends `BaseTest4`, so it needs a running database. `PgStatementFetchSizeTest` builds the statement over a stub connection, which lets the check run without one.

I'd keep the new class. Do you want the negative case added to `StatementTest.testSetFetchSize` as well, or only in the new class? I can add it either way.

## Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

That's right. The old code stored the negative value and sent it as the row limit of the `Execute` message, and the backend treats any value below 1 as no limit. So `-1` did fetch everything, and such a caller will now get a `PSQLException` with SQLState `22023`.

I'd still keep the exception, for two reasons:

- The `Statement.setFetchSize` specification says it "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- `0` is the JDBC value for "no hint", and pgjdbc fetches every row at once for it. A caller who wants everything has a documented value to use.

I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql` and found 4 hits, all in test code of other projects. That covers public code only, so it says nothing about private applications. I can add a release note saying that `setFetchSize` now rejects negative values and that `0` replaces `-1`. Should I?

## `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement extends PgStatement` and doesn't override `setFetchSize`. `PgCallableStatement extends PgPreparedStatement`, also without an override, so it gets the check too.
