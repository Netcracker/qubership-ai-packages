## Why

No test turned escape processing off: `git grep setEscapeProcessing` over the tests found nothing. A `Statement` that ignored `setEscapeProcessing(false)` and translated JDBC escapes anyway passed the whole suite.

## What

With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState 42601. The new tests in `StatementTest` check:

- the `execute`, `executeUpdate` with generated keys, and `addBatch` paths, with escape processing off and, as a control, with the default. Each path carries the flag to the parser in its own way: `addBatch` has its own call site in `PgStatement`, and generated keys use `QueryWithReturningColumnsKey` rather than `BaseQueryKey`;
- `setEscapeProcessing(true)` after `false` translates again;
- with `preferQueryMode=extendedCacheEverything`, a `Statement` with escape processing off does not reuse the translated query another `Statement` cached for the same SQL.

The default cases cover the same paths as the `{d}` insert in `StatementTest.escapeProcessing` and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, so I removed both. The batch half gained nothing from the `reWriteBatchedInserts` and binary-mode parameters of `BatchExecuteTest`: `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half stays.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.test.jdbc2.StatementTest' --tests 'org.postgresql.test.jdbc2.BatchExecuteTest'
```

I checked that each new test can fail by applying one mutant at a time to the production code:

| Mutant | Red |
| --- | --- |
| `CachedQueryCreateAction.create` always escapes | all three "off" cases and the cache test |
| `create` never escapes | all three default cases |
| `executeCachedSql` passes `true` instead of the flag | "off" `execute` and generated keys |
| `addBatch` passes `true` instead of the flag | "off" `addBatch` |
| `createQueryKey` passes `true` to `QueryWithReturningColumnsKey` | "off" generated keys |
| `BaseQueryKey.equals` and `hashCode` ignore `escapeProcessing` | the cache test |
| `setEscapeProcessing` ignores its argument | the turn-back-on test |

## Scope

`PreparedStatement` and `CallableStatement` are not covered: their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement. #1242 (closed) duplicated existing tests of the same parser path and did not reach this branch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
