### Extending `StatementTest.testSetFetchSize`

> The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would rather extend that one than add a new class.

`StatementTest.testSetFetchSize` checks only that a positive value round-trips through `getFetchSize()`. It has no negative case, so `PgStatementFetchSizeTest` doesn't duplicate it. `testSetFetchSize` extends `BaseTest4`, so it needs a running database. `PgStatementFetchSizeTest` builds the statement over a stub connection and runs without one. I'd keep the new class. If you want the negative case in `testSetFetchSize` as well, I'll add it there too.

### Applications that call `setFetchSize(-1)`

> Throwing here could break applications that call `setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed.

You're right that the old code accepted `-1`, and that the backend treated it as no limit, so such a call did fetch every row. A caller that passes `-1` now gets a `PSQLException` with SQLState `22023`.

I'd still keep the exception, for two reasons:

- The `Statement.setFetchSize` specification says it "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- `0` is the JDBC value for "no hint", and pgjdbc fetches every row at once for it. Callers can switch from `-1` to `0` with no change in behavior.

I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql`. It returned 4 hits, all in test code of other projects. That covers public code only, so it says nothing about private applications.

Do you want the behavior change called out in the changelog, or should it wait for a release where you accept breaking changes?

### `PgPreparedStatement`

> And should `PgPreparedStatement` get the same check, or does it inherit it?

It inherits the check. `PgPreparedStatement` extends `PgStatement` and doesn't override `setFetchSize`. `PgCallableStatement` extends `PgPreparedStatement` and doesn't override it either, so all three classes reject a negative value.
