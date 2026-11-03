No test turned escape processing off: `git grep setEscapeProcessing` over the tests found nothing. A `Statement` that ignored `setEscapeProcessing(false)` and translated JDBC escapes anyway passed the whole suite.

The new tests in `StatementTest` cover this case. With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState 42601. Each production site that carries the flag to the parser is guarded by these tests:

| Site | Guarded by |
| --- | --- |
| `CachedQueryCreateAction.create` | every case of `escapeSyntaxIsTranslatedByDefault` and `escapeSyntaxReachesTheServerAsWrittenWhenEscapeProcessingIsOff`, and `aCachedTranslatedQueryIsNotReusedWhenEscapeProcessingIsOff` |
| `executeCachedSql` | the "off" `execute` and `executeUpdate with generated keys` cases |
| `addBatch` | the "off" `addBatch` case |
| `createQueryKey`, for `QueryWithReturningColumnsKey` | the "off" `executeUpdate with generated keys` case |
| `BaseQueryKey.equals` and `hashCode` | `aCachedTranslatedQueryIsNotReusedWhenEscapeProcessingIsOff` |
| `setEscapeProcessing` | `escapeSyntaxIsTranslatedAgainWhenEscapeProcessingIsTurnedBackOn` |

I removed the `{d}` insert in `StatementTest.escapeProcessing` and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, because the default cases cover the same paths. The `reWriteBatchedInserts` and binary-mode parameters of `BatchExecuteTest` added no coverage to the batch half. `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half stays.

`PreparedStatement` and `CallableStatement` are not covered. Their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement. #1242, now closed, duplicated existing tests of the same parser path and never reached this branch.
