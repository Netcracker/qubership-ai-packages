No test turns escape processing off. `git grep setEscapeProcessing` over the tests finds nothing, so a `Statement` that ignores `setEscapeProcessing(false)` and translates JDBC escapes anyway passes the whole suite.

With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState `42601`. The new `StatementTest` cases check this through `execute`, `executeUpdate` with generated keys, and `addBatch`. They also check that the same paths translate the syntax by default, as a control. A further case checks that `setEscapeProcessing(true)` after `false` translates again. Another checks that, with `preferQueryMode=extendedCacheEverything`, a `Statement` with escape processing off does not reuse the translated query that another `Statement` cached for the same SQL.

Each path reaches the parser through its own code, as the table shows. The default cases cover the same paths as the `{d}` insert in `StatementTest.escapeProcessing` and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, so both are removed. The batch half gained nothing from the `reWriteBatchedInserts` and binary-mode parameters: `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half stays.

Only test files change, so the new tests pin behavior the driver already has. Each row below was checked by breaking that one site in the production code.

| Site | Guarded by |
| --- | --- |
| `CachedQueryCreateAction.create` | the default cases (translation on); the off cases and the cache case (translation off) |
| The flag that `executeCachedSql` passes on | off `execute` and off `executeUpdate with generated keys` |
| The `addBatch` call site in `PgStatement` | off `addBatch` |
| The flag that `createQueryKey` passes to `QueryWithReturningColumnsKey` | off `executeUpdate with generated keys` |
| The `equals` and `hashCode` of `BaseQueryKey` | the cache case |
| The argument of `setEscapeProcessing` | the turn-back-on case |

PreparedStatement and CallableStatement are not covered: their cache keys always escape, and JDBC specifies that `setEscapeProcessing` has no effect on a prepared statement. #1242 (closed) duplicated existing tests of the same parser path and never reached the escape-off path.
