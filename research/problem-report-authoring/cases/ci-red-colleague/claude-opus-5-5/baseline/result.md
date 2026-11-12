Hi Dana, `main` has been red since `4f2a9c1` ("Batch export: skip empty partitions"). Will you fix forward or revert? #1311 and #1314 are blocked in the merge queue behind it.

`OrderExportTest.exportsEmptyBatch()` fails in https://ci.internal.example/ledger-service/runs/88412 (trace trimmed, the rest is JUnit internals):

```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

It's not flaky: I re-ran the job twice (runs 88415 and 88419), and both failed the same way. The last green run, 88407, was on the parent `e01b77d`. Locally, `./gradlew :export:test --tests OrderExportTest` fails the same way on `4f2a9c1` and passes on `e01b77d` (JDK 21.0.5, Gradle 8.10.2, macOS 15.1).

My guess, not checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the header-only file the test counts.
