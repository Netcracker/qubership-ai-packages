Hi Dana, `main` has been red since your `4f2a9c1` ("Batch export: skip empty partitions"). Are you going to fix forward or revert it?

`OrderExportTest > exportsEmptyBatch()` fails in CI run 88412 (https://ci.internal.example/ledger-service/runs/88412). The last green run, 88407, was on the parent `e01b77d`.

```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

It isn't flaky: reruns 88415 and 88419 failed the same way. Locally, `./gradlew :export:test --tests OrderExportTest` fails on `4f2a9c1` and passes on `e01b77d`.

My guess, which I haven't checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the header-only file that the test counts.

#1311 and #1314 are stuck in the merge queue behind the red `main`.
