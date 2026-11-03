No test turns escape processing off: `git grep setEscapeProcessing` over the tests finds nothing. A `Statement` that ignores `setEscapeProcessing(false)` and translates JDBC escapes anyway passes the whole suite.

This change adds tests and touches no production code. With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState `42601`. The new cases in `StatementTest` check:

- `execute`, `executeUpdate` with generated keys, and `addBatch`, each with escape processing off and with the default as a control. Each path passes the flag to the parser by its own route, so each gets a case.
- `setEscapeProcessing(true)` after `setEscapeProcessing(false)` translates again.
- With `preferQueryMode=extendedCacheEverything`, a `Statement` with escape processing off does not reuse the translated query that another `Statement` cached for the same SQL.

The default cases cover the same paths as the `{d}` insert in `StatementTest.escapeProcessing` and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, so both are removed. The batch test's `reWriteBatchedInserts` and binary-mode parameters do not reach a `Statement` batch: `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half of that test stays.

The new tests pass on the code as it stands. The table pairs each production site with the cases that fail when that site alone is broken:

| Site | Guarded by |
| --- | --- |
| `CachedQueryCreateAction.create` always escapes | the three "off" cases and the cache test |
| `CachedQueryCreateAction.create` never escapes | the three default cases |
| `executeCachedSql` passes `true` instead of the flag | "off" `execute` and generated keys |
| `addBatch` call site in `PgStatement` passes `true` instead of the flag | "off" `addBatch` |
| `createQueryKey` passes `true` to `QueryWithReturningColumnsKey` | "off" generated keys |
| `BaseQueryKey` `equals` and `hashCode` ignore `escapeProcessing` | the cache test |
| `setEscapeProcessing` ignores its argument | the turn-back-on test |

`PreparedStatement` and `CallableStatement` are not covered, on purpose: their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement. #1242 (closed) duplicated existing tests of the same parser path and did not reach the `Statement` path this change covers.
