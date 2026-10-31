### Extending `StatementTest.testSetFetchSize`

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

The two tests don't overlap. `testSetFetchSize` extends `BaseTest4` and needs a running database, and it checks only that a positive value round-trips through `getFetchSize()`. It has no case for a negative value. `PgStatementFetchSizeTest` constructs the statement over a stub connection, so it runs without a database. I would keep it for that reason.

If you want the negative case in `StatementTest` as well, I will add it there too. Do you want both, or only the new class?

### Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

This is a behavior change, and an application that passes a negative value will now get a `PSQLException` with SQLState `22023`. I still think the exception is right, for two reasons:

- The JDBC specification for `Statement.setFetchSize` says it "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- `0` is the JDBC value for "no hint", and in pgjdbc it fetches every row at once. An application that wants everything can call `setFetchSize(0)`.

For usage in the wild, I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql`. It returned 4 hits, all in test code of other projects. Code search doesn't cover private code, so this shows the pattern is rare in public code and says nothing about private code.

Do you want a changelog entry that tells users to replace `setFetchSize(-1)` with `setFetchSize(0)`? I will add one.

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement extends PgStatement` and does not override `setFetchSize`. `PgCallableStatement extends PgPreparedStatement`, also without an override, so the check applies to all three classes and I made no further change.
