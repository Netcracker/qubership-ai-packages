No test turned escape processing off: `git grep setEscapeProcessing` over the tests finds nothing. So a `Statement` that ignored `setEscapeProcessing(false)` and translated JDBC escapes anyway passed the whole suite.

The new tests in `StatementTest` run a `{d '1900-01-01'}` insert three ways: through `execute`, through `executeUpdate` with generated keys, and through `addBatch`. With escape processing off, the server receives the escape as written and rejects it with SQLState 42601. With the default, the insert succeeds. Two more tests cover related cases:

- `setEscapeProcessing(true)` after `false` turns translation back on.
- With `preferQueryMode=extendedCacheEverything`, a `Statement` with escape processing off does not reuse the translated query that another `Statement` cached for the same SQL.

The default cases cover the same paths as two older tests, so I removed both. One is the `{d}` insert in `StatementTest.escapeProcessing`. The other is the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, and its `PreparedStatement` half stays. The `reWriteBatchedInserts` and binary-mode parameters of `BatchExecuteTest` added nothing to that batch half. `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary.

Each site that passes the flag on, and the tests that fail when that site ignores the flag:

| Site | Guarded by |
| --- | --- |
| `CachedQueryCreateAction.create` escapes only when the flag is on | the three default cases, the three "off" cases, and the cache test |
| `executeCachedSql` passes the flag | "off" `execute` and generated keys |
| `addBatch` passes the flag | "off" `addBatch` |
| `createQueryKey` passes the flag to `QueryWithReturningColumnsKey` | "off" generated keys |
| `BaseQueryKey.equals` and `hashCode` include `escapeProcessing` | the cache test |
| `setEscapeProcessing` stores its argument | the turn-back-on test |

`PreparedStatement` and `CallableStatement` are not covered. Their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement.
