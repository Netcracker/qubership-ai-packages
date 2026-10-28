No test turned escape processing off, so a `Statement` that ignored `setEscapeProcessing(false)` passed the suite.

The new `StatementTest` cases check that, with escape processing off, `{d '1900-01-01'}` reaches the server as written and fails with 42601 through `execute`, `executeUpdate` with generated keys, and `addBatch`, each of which passes the flag to the parser separately. They also cover turning it back on and a translated query cached under `preferQueryMode=extendedCacheEverything`.

The default-mode `{d}` cases in `StatementTest.escapeProcessing` and the `Statement` half of `BatchExecuteTest.testBatchEscapeProcessing` are removed, since the new default cases cover the same paths. `PreparedStatement` is not covered: JDBC says the setting has no effect there. See #1242.
