Hi Dana, `main` has been red since your `4f2a9c1` ("Batch export: skip empty partitions"): `OrderExportTest.exportsEmptyBatch()` fails. Will you fix forward, or should it be reverted? PRs #1311 and #1314 are blocked behind it in the merge queue.

Failing run: https://ci.internal.example/ledger-service/runs/88412
```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

Re-running didn't help: runs 88415 and 88419 failed the same way. The last green run, 88407, was on the parent `e01b77d`. Locally, `./gradlew :export:test --tests OrderExportTest` fails on `4f2a9c1` and passes on `e01b77d`.

My guess, which I haven't checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the header-only file the test counts.
