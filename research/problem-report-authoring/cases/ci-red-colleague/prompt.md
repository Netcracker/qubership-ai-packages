# Notes: main is red

Taken on 2026-10-30 at 14:10 UTC. I work on the payments team; the repository is our own `ledger-service`.

`main` has been red since commit `4f2a9c1` ("Batch export: skip empty partitions", by Dana Reyes, merged at 11:42
UTC). CI run: https://ci.internal.example/ledger-service/runs/88412. The last green run, 88407, was on its parent
`e01b77d`.

From the run log:

```text
OrderExportTest > exportsEmptyBatch() FAILED
    org.opentest4j.AssertionFailedError: expected: <1> but was: <0>
        at app//com.acme.ledger.export.OrderExportTest.exportsEmptyBatch(OrderExportTest.java:57)
```

The full trace is 40 lines; the rest is JUnit internals.

I re-ran the job twice (runs 88415 and 88419): the same failure both times. Locally,
`./gradlew :export:test --tests OrderExportTest` fails the same way on `4f2a9c1` and passes on `e01b77d`. JDK 21.0.5,
Gradle 8.10.2, macOS 15.1.

My guess, not checked: the commit's new `if (partitions.isEmpty()) return;` in `OrderExporter.export` skips writing the
header-only file the test counts.

Two pull requests in the merge queue, #1311 and #1314, are blocked behind the red `main`.

## The task

Write the Slack direct message to Dana asking whether they will fix forward or revert. Slack renders backticks and
triple-backtick blocks.
