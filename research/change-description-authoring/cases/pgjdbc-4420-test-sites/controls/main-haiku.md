## Why

No test turned escape processing off. `git grep setEscapeProcessing` over the tests finds nothing, so a `Statement` that ignored `setEscapeProcessing(false)` and translated JDBC escapes anyway passed the whole suite.

## What

With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState 42601.

The diff adds four test methods to `StatementTest`. The first two are parameterized over three ways to run a statement: `execute`, `executeUpdate` with generated keys, and `addBatch`. Each path hands the flag to the parser in its own way: `addBatch` has its own call site in `PgStatement`, and generated keys use `QueryWithReturningColumnsKey` rather than `BaseQueryKey`. Each path runs once with escape processing off and once with the default, so the default case shows the same statement translated.

The other two tests check that `setEscapeProcessing(true)` after `false` translates again, and that with `preferQueryMode=extendedCacheEverything` a `Statement` with escape processing off does not reuse the translated query that another `Statement` cached for the same SQL.

The diff also removes two existing checks: the `{d}` insert in `StatementTest.escapeProcessing`, and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`. The new default cases cover the same paths, so no coverage is lost. The batch half gains nothing from the `reWriteBatchedInserts` and binary-mode parameters of `BatchExecuteTest`: `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half stays.

## Verification

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.test.jdbc2.StatementTest' --tests 'org.postgresql.test.jdbc2.BatchExecuteTest'
```

The command needs a running PostgreSQL server, such as the one in `docker/postgres-server/docker-compose.yml`. A passing run shows the new cases and the remaining batch test pass against that server. CI runs the full test suite on every pull request.

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

`PreparedStatement` and `CallableStatement` are not covered. Their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement. #1242 (closed) duplicated existing tests of the same parser path and did not reach this branch.
