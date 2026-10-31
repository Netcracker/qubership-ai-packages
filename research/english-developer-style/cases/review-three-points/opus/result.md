### The new test class

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

`StatementTest.testSetFetchSize` covers part of this: it checks that a positive value round-trips through `getFetchSize()`. It has no case for a negative value, though. It also extends `BaseTest4`, so it needs a running database. `PgStatementFetchSizeTest` builds the statement over a stub connection and runs without a database, so I'd like to keep it.

Should I keep only the new class, or also add the negative case to `testSetFetchSize`? I'm happy to do either.

### Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

That's right: an application that calls `setFetchSize(-1)` now gets a `PSQLException` where it used to get every row. Even so, I'd keep the exception, for three reasons:

- The JDBC specification requires it. `Statement.setFetchSize` "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- These applications already have a supported value. `0` is the JDBC value for "no hint", and pgjdbc fetches every row at once for it.
- Few callers rely on `-1`. I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql` and found 4 hits, all in other projects' test code.

I can add a changelog entry that points those callers to `setFetchSize(0)`. Would you like that in this PR?

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement extends PgStatement` and doesn't override `setFetchSize`. `PgCallableStatement extends PgPreparedStatement` and doesn't override it either, so the check applies to all three classes.
