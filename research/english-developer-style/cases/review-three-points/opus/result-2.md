### The new test class

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

Both tests call `setFetchSize`, but they test different things. `StatementTest.testSetFetchSize` extends `BaseTest4`, so it needs a running database, and it only checks that a positive value comes back from `getFetchSize()`. It has no negative case. `PgStatementFetchSizeTest` builds the statement over a stub connection, so it runs without a database. I'd like to keep it for that reason.

Do you want the negative case in `StatementTest.testSetFetchSize` as well? I'm happy to add it there too, or leave that test unchanged.

### Applications that pass `-1`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

You're right that this changes behavior: a caller that passes `-1` now gets a `PSQLException` where it used to get every row. I still think the exception is correct, for three reasons:

- The JDBC specification requires it. `Statement.setFetchSize` "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- `0` is the documented way to fetch everything. It is the JDBC value for "no hint", and pgjdbc fetches every row at once for it. Before this change, the driver sent `-1` as the row limit of the `Execute` message, and the backend treats any limit below 1 as no limit. So these callers only need to replace `-1` with `0`.
- I searched GitHub code for `setFetchSize(-1)` together with `org.postgresql` and found 4 hits. All of them are in test code of other projects.

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement` extends `PgStatement` and doesn't override `setFetchSize`. `PgCallableStatement` extends `PgPreparedStatement` and doesn't override it either, so the check applies to all three classes.
