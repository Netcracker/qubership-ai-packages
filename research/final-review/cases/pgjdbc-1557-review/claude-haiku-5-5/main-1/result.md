**Final review: `8495127..HEAD` (issue #1556, `isValid()` timeout)**

The change touches one method, `PgConnection.isValid(int)`, and adds no tests. It has five substantive findings: a regression for large timeouts, a security-manager failure, a masked cause in the log, an overstated claim, and no test or red run. Nothing was built or run.

**Setup.** I loaded `test-authoring` and `english-developer-style` from the skills directory. The form also asks for the Java doc-comment skill (`javadoc-authoring`), which is not in that directory, so I did not load it. Item 1 was checked against the form and the Javadoc section of `english-developer-style`. The drift script reported one member: `PgConnection.isValid(int) @1373: code-changed, no-comment`.

**Item 1: comments consistent with the code and with each other.** None. `isValid(int)` has no doc comment, so there is nothing to drift. The retained `// "current transaction aborted"` comment is still true. The change adds no comment that narrates the change. The PR's "will not last more than timeout seconds" is a claim, not a comment; it is covered under finding 4.

**Item 2: claimed cases covered.** Substantive finding. The PR and commit `1f01e87` claim these cases:
- a broken or stalled socket makes `isValid(n)` return within `n` seconds;
- a healthy connection still returns `true`;
- a user-set network timeout is restored afterwards (commit `0e1f482`);
- `isValid(0)` applies no limit.

None has a test. The diff touches only `PgConnection.java`, and `IsValidTest.testIsValid` covers only `isValid(0)` on a closed connection. The restore is the design point the PR names, so the test that fails if it is replaced by "no restore" is the one owed.

**Item 3: boundaries, partitions, negative control.** Substantive. The boundary `timeout * 1000` is not tested, and it overflows `int` (finding 1). `isValid(0)` is the no-limit case, and it is untested except on a dead connection. The negative control, a healthy connection that returns `true` with the same timeout, is absent. Pre-existing state: none; the change persists nothing.

**Item 3a: level and environment.** Substantive. The behavior is a blocked socket read, so no in-process test can observe it. The smallest level that can observe it is a medium test: a peer that completes startup and then stops answering. It belongs in `src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, beside `testIsValid` and on its `BaseTest4` fixture. Nothing is skipped and no CI job is at issue, since there is no test yet.

**Item 4: names by content.** None. The one new identifier is `savedNetworkTimeOut`, which is not positional.

**Item 5: the failure report.** None. The diff adds no assertions.

**Item 6: what the writer verified.** Substantive. Neither a red run on `8495127` nor a mutation verdict is stated. The PR says the change was "never tested".

**Item 7: siblings.**
- `isValid(int)` is the only implementation (grep over `src/main/java`).
- The only callers of the public `PgConnection.setNetworkTimeout` are the two in `isValid`.
- `PGStream.java:132-139` (`hasBufferedInput`) uses the same save-and-restore pattern, but on the stream directly. Findings 2 and 3 do not apply there: it has no permission check, and it has no closed-connection check on restore.
- The replication branch shares the same `try`, so findings 1 to 3 apply to it too.

**Findings, sorted.**

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. `timeout * 1000` overflows `int` above 2147483. `isValid(2147484)` on a healthy connection now returns `false`. The base computed `seconds * 1000L` (`PgStatement.java:535`) and returned `true`. | Substantive | `PgConnection.java:1384` | Compute in `long`, then clamp to `Integer.MAX_VALUE` or reject. Add a boundary test at 2147483 and 2147484. |
| 2. `setNetworkTimeout` checks `SQLPermission("setNetworkTimeout")` and can throw `SecurityException`. The `catch (SQLException)` does not catch it, so under a security manager without that grant `isValid` now throws. The base needed no permission. | Substantive | `PgConnection.java:1384`, `1398`, `1570-1576` | Call `queryExecutor.setNetworkTimeout` directly, as `PGStream` does, rather than the public method. |
| 3. When a read times out, the executor calls `abort()` (`QueryExecutorImpl.java:514`, `2428`), which sets `closed` (`QueryExecutorBase.java:125-131`). The `finally` restore then hits `checkClosed()` and throws "This connection has been closed.", which replaces the I/O cause in the FINE log. | Substantive | `PgConnection.java:1398` | Restore through `queryExecutor` without the closed check, or skip the restore when `isClosed()`. |
| 4. "Will not last more than timeout seconds" is false as written. `setSoTimeout` bounds each blocking read, not the whole call, so a peer that trickles bytes can run past the limit. It also does not bound writes. | Substantive | PR title; commit `1f01e87` | Reword to a per-read bound, or enforce an overall deadline, and say which case is not covered. |
| 5. No test covers the claimed cases (item 2). The behavior needs a medium test with a stalled peer, placed in `IsValidTest`. | Substantive | `src/test/java/org/postgresql/test/jdbc4/IsValidTest.java` | Add a stalled-peer test named for the outcome, e.g. `isValidReturnsFalseWithinTheTimeoutWhenTheServerStops`, and one named `isValidRestoresTheNetworkTimeout`. |
| 6. No red run on the base commit and no mutation verdict. The PR says "never tested". | Substantive | PR description | Provide the red run on `8495127` for the stalled-peer test. |
| 7. `savedNetworkTimeOut` spells `TimeOut`, but the methods it saves are `getNetworkTimeout` and `setNetworkTimeout`. | Taste | `PgConnection.java:1382` | `savedNetworkTimeout`. Expect it to be declined without discussion. |

**Not checked.** I did not build or run the suite, and I did not verify findings 1 to 3 by running them; they rest on reading the code and arithmetic. The `javadoc-authoring` skill was not available, so the Javadoc part of Item 1 is judged by the English style skill and the form alone.
