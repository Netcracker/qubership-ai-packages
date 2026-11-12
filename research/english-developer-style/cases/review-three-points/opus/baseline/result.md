### Duplicate test

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

Both tests call `setFetchSize`, but they don't check the same thing. `StatementTest.testSetFetchSize` extends `BaseTest4`, so it needs a running database. It also only checks that a positive value round-trips through `getFetchSize()` and has no negative case. `PgStatementFetchSizeTest` builds the statement over a stub connection, so it runs without a server.

I'd like to keep the new class for that reason. Should I also add the negative case to `StatementTest.testSetFetchSize`, or is the new class enough?

### Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

You're right that the old code accepted it. The driver stored the negative value and sent it as the row limit of the `Execute` message. The backend treats any limit below 1 as "no limit", so those applications got every row, and after this change they get a `PSQLException` instead.

I still think the driver should throw, because the JDBC specification requires it. `Statement.setFetchSize` "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied." To fetch everything, JDBC uses `0`, which means "no hint". In pgjdbc, `0` fetches every row at once, so an affected application can switch from `-1` to `0` and get the same result.

I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql` and found 4 hits, all in other projects' test code. That search only covers public code. If it helps, I can add a changelog entry that names SQLState `22023` and says to use `setFetchSize(0)` instead.

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement` extends `PgStatement` and doesn't override `setFetchSize`. `PgCallableStatement` extends `PgPreparedStatement`, also without an override, so it inherits the check too.
