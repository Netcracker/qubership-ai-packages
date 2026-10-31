Thanks for the review. I'll take your three points in order.

### The new test class

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

Both tests cover `setFetchSize`, but `StatementTest.testSetFetchSize` has no case for a negative value. It checks only that a positive value round-trips through `getFetchSize()`. It also extends `BaseTest4`, so it runs only when a database is available. `PgStatementFetchSizeTest` constructs the statement over a stub connection, so the negative case runs in a build without a server. That's why I'd like to keep the new class.

Do you want the negative case in `StatementTest.testSetFetchSize` as well? If so, I'll add it there too.

### Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

You're right that the old code allowed it and that it worked. The driver stored `-1` and sent it as the row limit of the `Execute` message. The backend treats any value below 1 as no limit, so the query returned every row.

I'd still keep the exception, because the JDBC specification of `Statement.setFetchSize` requires it: "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."

The documented way to fetch everything is `setFetchSize(0)`. In JDBC, `0` means "no hint", and in pgjdbc it fetches every row at once. An application that passes `-1` today can pass `0` and get all rows in one batch.

To estimate the impact, I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql`. It returned 4 hits, all in test code of other projects. If you'd like, I can add a changelog entry that names the new `PSQLException` (SQLState `22023`) and gives `0` as the replacement.

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits it. `PgPreparedStatement extends PgStatement` and does not override `setFetchSize`. `PgCallableStatement extends PgPreparedStatement` and does not override it either. So the check applies to all three classes.
