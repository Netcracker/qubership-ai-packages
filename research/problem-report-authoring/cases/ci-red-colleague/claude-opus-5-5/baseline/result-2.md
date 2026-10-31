Hi Dana, `main` has been red since your `4f2a9c1` ("Batch export: skip empty partitions"), and #1311 and #1314 are blocked behind it in the merge queue. Will you fix forward or revert, and roughly when?

First red run: https://ci.internal.example/ledger-service/runs/88412 (the last green one, 88407, ran on the parent `e01b77d`). I trimmed the trace to the test frame. The rest is JUnit internals:

```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

It isn't a flake: I re-ran the job twice (88415 and 88419) and got the same failure. Locally, `./gradlew :export:test --tests OrderExportTest` fails the same way on `4f2a9c1` and passes on `e01b77d` (JDK 21.0.5, Gradle 8.10.2, macOS 15.1).

My guess, which I haven't checked: the new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the header-only file that the test counts.
