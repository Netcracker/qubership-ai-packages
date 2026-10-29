# Final review: `8495127..HEAD`, isValid() bounded by its timeout (#1556)

The change has one real fix and four problems. It edits only `PgConnection.isValid(int)`. It adds no test, and the PR description says it was "never tested". Three of the problems change behavior for callers that work today: `isValid(0)` can now hang forever, `isValid` can now throw `SecurityException`, and large timeouts now make a healthy connection report invalid.

Inputs:
- **Diff:** read in full. It is one file, `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java`, with 16 lines added and 10 removed, spread over 5 commits.
- **Task statement:** the PR description you gave me.
- **Commit messages:** the first one claims "Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)". The later ones are a checkstyle fix, a merge, "Add a try/catch to succeed tests", and "Manages simply and properly get/setNetworkTimeout()".
- **Test class comments:** none, because no test was added.
- **Previous report:** none.
- **Drift script:** `PgConnection.isValid(int) @1373: code-changed, no-comment`.
- **Skills:** `test-authoring` and `english-developer-style` were loaded. The repository has no `AGENTS.md` or `CLAUDE.md`. Following test-authoring §0, I propose adding this line to the repository's instructions: `Tests: JUnit 4 engine, JUnit 4 Assert assertions`, which is what `IsValidTest` and its neighbors use. I did not edit any file.

## Item 1: comments consistent with the code and with each other

None. `isValid(int)` has no doc comment of its own; it inherits the contract of `java.sql.Connection`. The one comment inside it, `// "current transaction aborted", assume the connection is up and running` at line 1401, is still true of the `catch` it sits in. No comment describes the change in passing ("now", "no longer").

## Item 2: claimed cases covered

| Claimed case | Source | Test |
| --- | --- | --- |
| `isValid(timeout)` returns within `timeout` seconds when the socket is broken or the peer has stopped answering | Commit 1f01e87, PR title | **None.** No test was added. The existing `IsValidTest` cases (`testIsValid`, `testTransactionState`, `testIsValidRemoteClose`) all call `isValid(0)` and do not cover a silent peer. |
| Same claim for the replication branch (`IDENTIFY_SYSTEM`, which has no query timeout, so the network timeout is its only bound) | Implied: the change wraps both branches | **None.** `ReplicationConnectionTest` lines 44 and 65 call `isValid(3)` only on a healthy or closed connection. |
| The network timeout the caller set before `isValid` is restored afterwards | Commit 0e1f482 ("properly get/setNetworkTimeout()"), and the `finally` block at line 1398 | **None.** No test sets a network timeout, calls `isValid`, and then checks `getNetworkTimeout()`. If the `finally` block were deleted, every existing test would stay green. |

## Item 3: boundaries, partitions, and the negative control

- **No test of the defect or its control.** There is no test that reproduces the broken-socket case. There is also no control test showing a responsive connection still returns `true` with the caller's network timeout unchanged.
- **`timeout = 0`, the boundary the existing tests all use** (`PgConnection.java:1384`). JDBC defines `0` as "no timeout". `setNetworkTimeout(null, 0)` turns the socket read timeout off entirely. A connection opened with `socketTimeout=5`, whose `isValid(0)` used to give up after 5 s on a dead peer, now waits forever until the finally block restores the old value. That means this change makes the defect worse for exactly the input every pool that calls `isValid(0)` passes. The minimum fix is to skip `setNetworkTimeout` when `timeout == 0`. A fuller fix also keeps the shorter of the two limits when the caller's own timeout is non-zero.
- **Upper boundary: `timeout * 1000` overflows** (line 1384). For `timeout > 2147483`, the product is negative. `setNetworkTimeout` then throws `INVALID_PARAMETER_VALUE`, the outer `catch` swallows it, and `isValid` returns `false` for a healthy connection. Nothing tests `Integer.MAX_VALUE` or the value just past 2147483. The fix is to clamp the value, or compute it with `TimeUnit.SECONDS.toMillis` and saturate.
- **Two limits on the same work share one value.** The query timeout (line 1393, `setQueryTimeout(timeout)`) and the socket read timeout (line 1384) both bound the same `executeUpdate`, both count from about the same start, and both equal `timeout`.
  - **Query timeout fires first:** a cancel request goes out and the connection survives with a "canceling statement" error.
  - **Socket timeout fires first:** `QueryExecutorImpl` (lines 334, 513, 2427) calls `abort()`, which closes the socket. The connection is gone for good.
  - Which one wins is a race at the defaults. A server that is slow but healthy can now lose its connection to `isValid`. The fix is to derive one limit from the other: either the socket limit is the query timeout plus a margin, so it only catches a peer that does not answer the cancel, or the query timeout is dropped and the socket limit is documented as the only bound.
- **The caller's existing setting is the pre-existing state the change meets.** Two cases are missing: a `socketTimeout` larger than `timeout`, and one smaller. Both need a check that `isValid` restores the value afterwards.

## Item 3a: level, placement, and the environment

- **A test is possible without a hung database.** `LoginTimeoutTest` already uses an in-process `ServerSocket` peer that accepts and never answers. The analogous test needs either a small TCP relay between the driver and the test server that stops forwarding after login, or a fake backend that completes the startup handshake and then goes silent. The test then asserts that `isValid(1)` returns `false` within the timeout plus a stated margin.
- **The restore check needs only the ordinary test server.** Call `setNetworkTimeout(null, 5000)`, then `isValid(1)`, then `assertEquals(5000, con.getNetworkTimeout())`.
- **Placement:** both tests belong in `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, beside the existing `isValid` tests and sharing their `BaseTest4` fixture.
- **Security manager:** nothing needs to be skipped for an optional prerequisite. The security-manager case is covered by the regression test requested in Item 7.

## Item 4: names by content, not by position

None. The only name the change adds is the local `savedNetworkTimeOut` (line 1382), which names its content. Its capital `O` does not match the method it stores (`getNetworkTimeout`). That is a style nit and not a finding.

## Item 5: the failure report

None in the change, since it adds no assertions. One note for the tests it owes: the existing `testIsValid` uses bare `assertTrue(con.isValid(0))` with no message. New tests should follow `testIsValidRemoteClose`, which passes a message, and should use `assertEquals` for the restored timeout.

## Item 6: what the writer says it verified

None stated. The PR says "never tested". There is no run that fails on the base commit and no mutation result. Commit 198701f, "Add a try/catch to succeed tests", suggests the existing suite was made to pass without the new behavior being observed.

## Item 7: siblings of the change

The change now relies on `PgConnection.getNetworkTimeout()` and `PgConnection.setNetworkTimeout(Executor, int)`. In main code, `isValid` is their only caller (`git grep -n 'setNetworkTimeout\|getNetworkTimeout'`). `PGStream.hasMessagePending` (`PGStream.java:132-139`) uses the same save-and-restore pattern one layer down, through `PGStream.setNetworkTimeout`. It does not go through `PgConnection`, so the security check and the `checkClosed()` problem below do not apply to it. Three problems come from what the `PgConnection` methods do, and they are new in `isValid`:

1. **`SecurityException` escapes `isValid`** (lines 1384 and 1398, through `setNetworkTimeout` at line 1580). Under a `SecurityManager` that does not grant `SQLPermission("setNetworkTimeout")`, `isValid` now throws an unchecked `SecurityException`. Before this change it needed no permission, and the `catch (SQLException e)` does not catch it. The fix is to call `queryExecutor.setNetworkTimeout` and `getNetworkTimeout` directly, as `PGStream` does. That skips both the permission check and `checkClosed()`.
2. **The original error is replaced in the log** (line 1398). When the socket times out, `abort()` closes the connection. The `finally` block then calls `setNetworkTimeout`, whose `checkClosed()` throws "This connection has been closed". That exception replaces the timeout exception, so the FINE log at line 1405 records the wrong cause. Calling the executor directly (point 1) fixes this too.
3. **A failed restore makes a good check report `false`.** If restoring the timeout fails after a successful check, `return true` is overridden and `isValid` returns `false` for a connection that answered. The connection is also left with the `isValid` timeout as its socket timeout.

No other main-code site validates a connection (`git grep -n 'isValid(\|IDENTIFY_SYSTEM' -- pgjdbc/src/main`), so the fix has no other site to carry.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `isValid(0)` turns off any socket timeout the caller configured, so it can hang forever where it was bounded before | Substantive | `PgConnection.java:1384` | Leave the network timeout unchanged when `timeout == 0`; otherwise keep the shorter of the caller's value and `timeout`. Test with `socketTimeout` set and `isValid(0)`. |
| Under a `SecurityManager` without `setNetworkTimeout` permission, `isValid` now throws `SecurityException` | Substantive | `PgConnection.java:1384, 1398` (check at 1580) | Use `queryExecutor.set/getNetworkTimeout` directly. |
| After a socket timeout, the `finally` block's `checkClosed()` exception replaces the timeout in the log; a failed restore turns `true` into `false` | Substantive | `PgConnection.java:1398` | Restore through `queryExecutor`; do not let a restore failure override the result or hide the original exception. |
| `timeout * 1000` overflows for `timeout > 2147483`, so a healthy connection reports invalid | Substantive | `PgConnection.java:1384` | Saturate the conversion; test `Integer.MAX_VALUE` and 2147484. |
| Query timeout and socket timeout are the same value on the same work; when the socket wins, it destroys a slow but healthy connection | Substantive | `PgConnection.java:1384, 1393` | Derive one from the other (socket limit = query timeout + margin) or document the pair. |
| The headline claim (bounded by `timeout` on a silent peer) has no test, for either branch | Substantive | `IsValidTest.java` (absent) | Add a test with a silent peer (relay or fake backend, as in `LoginTimeoutTest`) asserting `false` within the bound; add the replication case to `ReplicationConnectionTest`. |
| Restoring the caller's network timeout is untested; deleting the `finally` block keeps every test green | Substantive | `IsValidTest.java` (absent) | `setNetworkTimeout(null, 5000)`, `isValid(1)`, `assertEquals(5000, con.getNetworkTimeout())`. |
| No evidence the tests can fail (no failing run on the base commit, no mutation result) | Substantive | PR description | State the failing run on the base commit for the new tests. |

I did not build the project or run its tests. I did not check the behavior of the real server or of `java.net.Socket` beyond the driver code I read. I did not review the prose for style.
