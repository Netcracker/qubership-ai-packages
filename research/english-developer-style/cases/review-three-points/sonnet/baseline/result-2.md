Thanks for the review. I took your points in order.

### The test duplicates `StatementTest.testSetFetchSize`

I'd like to keep `PgStatementFetchSizeTest`. `StatementTest.testSetFetchSize` has no negative case: it only checks that a positive value round-trips through `getFetchSize()`. It also extends `BaseTest4`, so it needs a running database. The new class constructs the statement over a stub connection and runs without one.

If you want both, I'll add the negative case to `StatementTest.testSetFetchSize` as well. Do you want that, or should the new class stand alone?

### Applications that call `setFetchSize(-1)`

You wrote: "Throwing here could break applications that call `setFetchSize(-1)` to mean 'fetch everything', which the old code silently allowed."

You're right that this is a behavior change. The old code stored the negative value and sent it as the row limit of the `Execute` message, and the backend treats any limit below 1 as no limit. So `-1` did fetch everything.

I'm keeping the exception for two reasons:

- The `Statement.setFetchSize` specification requires it: "throws SQLException if a database access error occurs, this method is called on a closed Statement or the condition rows >= 0 is not satisfied."
- `0` is the JDBC value for "no hint", and pgjdbc fetches every row at once for it. An application that wants everything can call `setFetchSize(0)`.

I searched GitHub code search for `setFetchSize(-1)` together with `org.postgresql` and found 4 hits, all in test code of other projects. Code search covers public repositories only, so it says nothing about private code.

### `PgPreparedStatement`

It inherits the check. `PgPreparedStatement extends PgStatement` and does not override `setFetchSize`. `PgCallableStatement extends PgPreparedStatement`, also without an override, so it gets the check too.
