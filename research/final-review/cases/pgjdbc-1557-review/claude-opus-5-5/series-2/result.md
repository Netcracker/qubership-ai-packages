I've finished reading the diff, the drift output, the callers and `IsValidTest`; the report follows.

# Final review: `8495127..HEAD` (pgjdbc #1556, `isValid()` bounded by timeout)

I had the PR description and the commit messages. The only changed file is `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java`, in `isValid(int)` (lines 1373–1408). The drift script lists one member: `PgConnection.isValid(int) @1373: code-changed, no-comment`.

## Item 1: comments consistent with the code and with each other
None. `isValid` has no doc comment of its own; it inherits the one on `@Override`. The only inline comment ("current transaction aborted…", line 1402) is still true, because the restore in `finally` runs before the `catch` branch. No comment describes the change itself.

## Item 2: claimed cases covered
Claims, from commit 1f01e87 and the PR description:
- **"isValid() will not last more than timeout seconds even if the underlying socket is broken."** No test covers this. All of `IsValidTest` calls `isValid(0)`. Neither `testIsValid` nor `testIsValidRemoteClose` exercises a positive timeout against a peer that stops answering, and `testIsValidRemoteClose` uses `pg_terminate_backend`, which gets an answer (the socket closes) rather than silence. The PR itself says "never tested". **Substantive.**
- **The save/restore of the network timeout** (commit 0e1f482, "properly get/setNetworkTimeout()"). No test checks that `getNetworkTimeout()` after `isValid(n)` equals its value before. **Substantive.**
- **The replication branch** (`IDENTIFY_SYSTEM`). Before this change it had no query timeout, so the network timeout is its only bound. `ReplicationConnectionTest` calls `isValid(3)` only on healthy connections. That leaves the replication branch with no broken-peer test, same as above.

Every hunk belongs to the claim above. The intermediate commits (198701f "Add a try/catch to succeed tests", the merge, the checkstyle fix) leave no net hunk of their own.

## Item 3: boundaries, partitions, and the negative control
- **`timeout = 0` erases the user's `socketTimeout` (`PgConnection.java:1384`).** In JDBC, `isValid(0)` means "no limit". `setNetworkTimeout(null, 0)` sets `SO_TIMEOUT` to infinite. Take a connection opened with `socketTimeout=30`: before the change, `isValid(0)` on a dead peer failed after 30 s; now it blocks forever. This is the opposite of what the PR intends, and on exactly the call every existing test makes. **Substantive.** Requested: when `timeout == 0`, keep the existing timeout.
- **A larger `timeout` relaxes a smaller `socketTimeout`.** With `socketTimeout=2` and `isValid(10)`, the read bound goes from 2 s to 10 s. **Substantive.** Requested: use the smaller of the two non-zero values.
- **`timeout * 1000` overflows (`:1384`).** For `timeout > 2147483` the product is negative. `setNetworkTimeout` then throws "Network timeout must be a value greater than or equal to 0." That exception is caught and logged at FINE, so `isValid` returns `false` on a healthy connection. Nothing tests the boundary at `Integer.MAX_VALUE / 1000` or the value just past it. **Substantive.**
- **Two limits on the same work fire at the same moment.** `setQueryTimeout(timeout)` (`:1393`) and the network timeout both expire after `timeout` seconds, counted from nearly the same start.
  - If the cancel wins, the server answers with an error and the connection survives.
  - If `SO_TIMEOUT` wins, the I/O error goes through `QueryExecutorImpl`'s IOException path (`abort()`, lines 335 and 514), so the connection is closed.

  On a slow but healthy server, which of these happens depends on timing. **Substantive.** Requested: derive one limit from the other, for example a network timeout of the query timeout plus a margin, or drop `setQueryTimeout`.
- **Negative control.** The existing healthy-connection tests (`testIsValid`, `testTransactionState`) serve as the control that passes on the base commit. Together with the missing broken-peer test, they would form the pair; only the control exists.

## Item 3a: level, placement, and the environment
- **Placement.** A new test belongs in `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, reusing `BaseTest4`'s `con`. None was added.
- **Level.** The bounded wait is observable without a real server: a socket peer that accepts the connection and never answers (a `ServerSocket` that does not reply, or a proxy that stops forwarding after startup). The request is a test against such a peer, asserting that `isValid(1)` returns `false` within about 1 s plus a margin. Nothing in the change skips a test.
- **SecurityManager regression.** `setNetworkTimeout` (`:1578–1581`) checks `SQLPermission("setNetworkTimeout")`. The resulting `SecurityException` is unchecked and escapes the `catch (SQLException)`. Under a SecurityManager that denies this permission, `isValid()` now throws where it used to return a result. **Substantive.** Requested: call `queryExecutor.setNetworkTimeout`/`getNetworkTimeout` directly, as `QueryExecutorImpl.processNotifies` does with its own save/restore of the socket timeout (lines 715–766).

## Item 4: names by content, not by position
None. The new local `savedNetworkTimeOut` names its content. Its casing ("TimeOut") differs from `getNetworkTimeout`; that is **taste**.

## Item 5: the failure report
None in the change, since it adds no assertions. A new timing test should assert the elapsed time with an equality or range assertion that prints the measured milliseconds, not with `assertTrue(elapsed < x)` alone (test-authoring, assertion choice).

## Item 6: what the writer says it verified
Nothing. The PR says "never tested", and there is no red run on the base commit and no mutation verdict. Commit 198701f, "Add a try/catch to succeed tests", suggests the existing suite failed at one point. That try/catch was later replaced by the outer `try` in 0e1f482, and no run of the final state is stated.

## Item 7: siblings of the change
- **`isValid` callers.** `git grep -n 'isValid('` finds 12 test call sites (`IsValidTest`, `AutoRollbackTestSuite`, `ReplicationConnectionTest`) and no production callers in the main sources. Every `IsValidTest` call passes `0`, so the `timeout = 0` finding above reaches all of them.
- **`processNotifies(int)`** (`QueryExecutorImpl.java:705–767`) is the sibling that already bounds a read by temporarily changing `SO_TIMEOUT`. It saves the old value, works on the socket directly with no permission check, and restores in `finally`. It is the pattern to reuse, not a site with the defect.
- **`setNetworkTimeout`/`getNetworkTimeout`** are now relied on by `isValid`. Their other callers are user code, and those are not affected.

## Findings

| Finding | Label | File:line | Request |
|---|---|---|---|
| `isValid(0)` sets `SO_TIMEOUT` to infinite and overrides `socketTimeout`, so it can now hang forever | Substantive | PgConnection.java:1384 | Keep the existing timeout when `timeout == 0`; otherwise use the smaller of the two non-zero values |
| `isValid(n)` raises a smaller user `socketTimeout` to `n` s | Substantive | PgConnection.java:1384 | Same: take the minimum |
| `timeout * 1000` overflows for `timeout > 2147483`, so a healthy connection is reported invalid | Substantive | PgConnection.java:1384 | Clamp or compute in `long`; test the boundary |
| Query timeout and network timeout expire together; the outcome (cancel vs. connection abort) depends on timing | Substantive | PgConnection.java:1384, 1393 | Derive one limit from the other |
| `SecurityException` from `setNetworkTimeout`'s permission check escapes `isValid` | Substantive | PgConnection.java:1384 (via 1578–1581) | Call `queryExecutor.set/getNetworkTimeout` directly |
| No test for the claimed case (dead peer, positive timeout, bounded duration) | Substantive | IsValidTest.java | Add a test in `IsValidTest` against a non-replying peer, asserting `false` and the elapsed time |
| No test that the network timeout is restored after `isValid` | Substantive | IsValidTest.java | Assert `getNetworkTimeout()` before and after |
| No broken-peer test for the replication branch | Substantive | ReplicationConnectionTest.java | Same test on the replication connection, or say in the description why it is not owed |
| `savedNetworkTimeOut` casing differs from the API's `NetworkTimeout` | Taste | PgConnection.java:1382 | Rename to `savedNetworkTimeout` |

I didn't build the project or run the test suite, and I did no style-only pass over the prose.
