Hi Dana, `main` on `ledger-service` has been red since your `4f2a9c1` ("Batch export: skip empty partitions"), and #1311 and #1314 are blocked behind it in the merge queue. Will you fix forward or revert?

`OrderExportTest.exportsEmptyBatch()` fails in https://ci.internal.example/ledger-service/runs/88412:

```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

It isn't flaky: re-runs 88415 and 88419 fail the same way. Locally, `./gradlew :export:test --tests OrderExportTest` fails on `4f2a9c1` and passes on its parent `e01b77d`, where the last green CI run (88407) was.

My guess, which I haven't checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` returns before it writes the header-only file the test counts.
