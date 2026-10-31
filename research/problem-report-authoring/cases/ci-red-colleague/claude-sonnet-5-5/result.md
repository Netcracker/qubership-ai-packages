Hi Dana, `main` in `ledger-service` has been red since your `4f2a9c1` ("Batch export: skip empty partitions"). Will you fix forward or revert?

`OrderExportTest > exportsEmptyBatch()` fails on it:

```text
org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
    at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

Run: https://ci.internal.example/ledger-service/runs/88412. The last green run was 88407, on the parent `e01b77d`.

What I checked:
- I re-ran the job twice (runs 88415 and 88419) and it failed the same way, so it isn't flaky.
- `./gradlew :export:test --tests OrderExportTest` fails locally on `4f2a9c1` and passes on `e01b77d` (JDK 21.0.5, Gradle 8.10.2, macOS 15.1).

My guess, not checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the header-only file that the test counts.

PRs #1311 and #1314 are blocked in the merge queue behind it. If you'd rather revert, tell me and I can do it.
