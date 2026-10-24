# Final review of `8495127..HEAD`: `isValid()` bounded by `timeout` (issue #1556)

The change touches one file, `PgConnection.isValid(int)` (`pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1373`). It adds no tests and no comments. The drift script reports one member: `PgConnection.isValid(int) @1373: code-changed, no-comment`. The branch's net diff is the last commit's shape; the three commits before it are intermediate attempts (`1f01e87`, `11b1f3f`, `198701f`). No previous report exists. I loaded `test-authoring` and `english-developer-style`. No Javadoc skill was in the provided set, and none was needed, because no doc comment changed.

### Item 1: comments consistent with the code and with each other
None. `isValid` has no doc comment of its own; it is `@Override` and inherits the JDBC one. The only comment in the body, `// "current transaction aborted", assume the connection is up and running` (line 1402), was not changed and is still true. The `/*not used*/` comment on the `executor` parameter of `setNetworkTimeout` (line 1570) still holds, since `isValid` passes `null`. No comment narrates the change.

### Item 2: claimed cases covered
The PR description and the commit `1f01e87` claim these cases:
- **(a)** `isValid(timeout)` returns within `timeout` seconds when the underlying socket is broken. **No test.**
- **(b)** The caller's network timeout is restored afterwards. This comes from the subject of `0e1f482`: "properly get/setNetworkTimeout()". **No test.**
- **(c)** Commit `198701f` is titled "to succeed tests", which implies an existing test failed at an intermediate commit. Neither the PR nor the commits say which test failed or why. That commit's catch was later removed in `0e1f482`, so the current version has no evidence that the failure is gone.

The PR itself says "never tested". Every hunk belongs to the claim; no hunk is unclaimed. The change contains no commands to run.

### Item 3: boundaries, partitions, and the negative control
- **`timeout == 0` is a regression.** `setNetworkTimeout(null, 0 * 1000)` sets `SO_TIMEOUT` to infinite for the duration of the check, which removes the user's `socketTimeout`.
  - **Before:** `isValid(0)` on a broken socket was bounded by `socketTimeout`, if the user had set one.
  - **Now:** it blocks with no bound.
  - All existing `isValid` tests call `isValid(0)` (`IsValidTest.java:34,38,47,55,62,84,100`), so they run exactly this path. None of them breaks the socket.
- **Overflow of `timeout * 1000`** (line 1384). For `timeout > 2_147_483`, the multiplication overflows `int`:
  - If the result is negative, `setNetworkTimeout` throws `INVALID_PARAMETER_VALUE`. That exception is caught, and a healthy connection reports `false`.
  - If the result wraps to another positive value, the timeout is unrelated to the one requested.
  - Before the change, any non-negative `timeout` worked.
- **Behavior under a `SecurityManager`.** `PgConnection.setNetworkTimeout` checks `SQLPermission("setNetworkTimeout")` (line 1580) and throws `SecurityException`, which is unchecked. `isValid` does not catch it. Under a security manager that lacks this permission, `isValid` now throws where it used to return a result. No test or sentence covers this.
- **Two limits on the same wait, set equal.** The query timeout (`setQueryTimeout(timeout)`, line 1393) and the per-read socket timeout (`timeout * 1000`) now have the same value.
  - **Query timeout fires first:** it sends a cancel over a separate connection. The server answers with an error and the connection stays usable.
  - **Socket timeout fires first:** `QueryExecutorImpl` catches the `IOException` and calls `abort()` (`QueryExecutorImpl.java:334-338`), which closes the connection.
  - The query timer starts before the send. Its cancel then needs a new TCP connection and a round trip before the server's error arrives, and the socket read times out at about the same moment. So on a server that is alive but slow, the socket timeout usually wins.
  - **Result:** `isValid` on a slow server now destroys the pooled connection, where before the check was only cancelled. The change does not say this is accepted.
  - **Request:** derive one limit from the other, for example a socket timeout of `timeout` plus a margin above the cancel's own timing, or drop the query timeout. Alternatively, state that closing the connection is intended.
- **Comparing the old and new mechanisms on the broken-socket fault:**
  - **Old behavior:** hangs until `socketTimeout`, or until the OS gives up on TCP, which can take minutes.
  - **New behavior:** each blocking read is bounded by `timeout`.
  - **Writes are still unbounded:** `SO_TIMEOUT` does not apply to them, so a send into a full buffer on a dead peer still blocks. `processResults` (and the several messages that `IDENTIFY_SYSTEM` returns) may also read more than once, so each read gets the full `timeout`. The claim "will not last more than timeout seconds" therefore holds only per read, and only for reads.
  - **Error output is quieter:** after `abort()`, the `finally` block at line 1398 calls `setNetworkTimeout`. Its `checkClosed()` throws "This connection has been closed", and that exception replaces the original I/O exception. The `FINE` log at line 1405 now records the closed-connection error, not the `SocketTimeoutException` that caused it.
- **Missing negative control:** no test compares a healthy connection with a positive `timeout` against a broken one.
- **Pre-existing state:** a connection whose user `socketTimeout` is shorter than `timeout` is not tested either. In that case the user's timeout is raised during the check and must be restored afterwards.

### Item 3a: level, placement, and the environment
None of the behavior is tested at any level. Restoring the timeout is observable in one process against the existing test server: the test sets a network timeout, calls `isValid(n)`, and asserts `getNetworkTimeout()` afterwards. That test belongs beside `IsValidTest`, sharing `BaseTest4`. Bounding the time needs a peer that stops answering. A small local proxy, similar to the existing proxy/`ServerSocket` tests (`SocksProxyTest`, `LoginTimeoutTest`), could stop forwarding after the connection is established. That test also belongs in `IsValidTest`, not in a new class.

### Item 4: names by content, not by position
None. No new names, case ids, or messages refer to anything by position. The local variable name `savedNetworkTimeOut` uses different capitalization from `getNetworkTimeout`; that is wording only and is not filed.

### Item 5: the failure report
None in the change, which adds no assertions. The existing `IsValidTest.testIsValid` uses `assertTrue(con.isValid(0))` with no message. That predates the change and is not filed.

### Item 6: what the writer says it verified
The writer states no red run and no mutation verdict. The PR says "never tested". Commit `198701f` refers to failing tests but does not name them.

### Item 7: siblings of the change
- **`setNetworkTimeout`:** in main code, `isValid` is the only caller of `PgConnection.setNetworkTimeout`/`getNetworkTimeout` (`git grep`).
- **`PGStream.hasMessagePending`:** this sibling saves and restores the timeout through `PGStream.getNetworkTimeout()`/`setNetworkTimeout(int)` (`PGStream.java:132-139`). That stream-level setter skips both the security-manager check and `checkClosed()`. Switching `isValid` to `queryExecutor.setNetworkTimeout(...)` would remove the `SecurityException` finding and the masked-cause finding together.
- **Replication branch** (`IDENTIFY_SYSTEM`): it gets only the socket bound, with no query timeout. So the race between the two limits described in Item 3 does not apply there, but the multi-read caveat does.
- **Other paths with the same symptom:** `close()` (Terminate) and transaction commands can also block on a dead socket. The task concerns `isValid` only, so these are not filed. They could be named as follow-ups.

### Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| `isValid(0)` sets `SO_TIMEOUT` to infinite and drops the user's `socketTimeout`, so it can now hang where it used to be bounded | Substantive | `PgConnection.java:1384` | Leave the network timeout unchanged when `timeout == 0` (or use the smaller nonzero value), and add a test |
| `timeout * 1000` overflows `int` for `timeout > 2_147_483`, so a healthy connection reports `false` or gets an unrelated timeout | Substantive | `PgConnection.java:1384` | Compute in `long` and clamp to `Integer.MAX_VALUE` (or use `TimeUnit`), and add a boundary test |
| `isValid` now throws an uncaught `SecurityException` under a `SecurityManager` that lacks `SQLPermission("setNetworkTimeout")` | Substantive | `PgConnection.java:1384,1398` (check at 1580) | Call `queryExecutor.setNetworkTimeout` directly, as `PGStream.hasMessagePending` does |
| Query timeout and socket timeout are equal, so on a slow but alive server the socket timeout usually fires first and `abort()` closes the connection instead of cancelling the check | Substantive | `PgConnection.java:1384,1393`; `QueryExecutorImpl.java:334` | Derive one limit from the other, or state that closing the connection is intended |
| The bound covers each read only: writes are unbounded and a multi-message reply gets `timeout` per read, so the "not more than timeout seconds" claim does not hold as written | Substantive | `PgConnection.java:1384` | Narrow the claim in the description, or bound the whole check |
| After `abort()`, the `setNetworkTimeout` call in `finally` throws "connection closed" and that replaces the original I/O exception in the `FINE` log | Substantive | `PgConnection.java:1398,1405` | Restore the timeout without `checkClosed()`, or add the original exception as suppressed |
| No test for the broken-socket bound, for restoring the network timeout, or for a positive `timeout` against a healthy control | Substantive | `IsValidTest.java` | Add these tests to `IsValidTest` (a local proxy that stops forwarding, plus `getNetworkTimeout()` after `isValid(n)`) |
| No red run or other evidence; the test that commit `198701f` says was failing is not named | Substantive | PR description | Name that test and state the evidence |

I did not build the project or run its test suite, and I did not do a style-only pass over the prose; the last three commits' squash shape was read but not run.
