# Final review of `8495127..HEAD`: Ensure isValid() will not last more than timeout seconds

The only change is to `PgConnection.isValid(int)` (`pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1373-1406`). It saves the network timeout, sets it to `timeout * 1000` for the duration of the check, and restores the saved value in a `finally`. No test file changes. The commit messages are subject lines only (`1f01e87`, `11b1f3f`, `198701f`, `0e1f482`, plus a merge commit that adds nothing to the net diff). The description says the change was "never tested".

Drift script output: `PgConnection.isValid(int) @1373: code-changed, no-comment`, and nothing else.

## Item 1: comments consistent with the code and with each other

None. `isValid` has no doc comment of its own; it inherits the `Connection.isValid` Javadoc, where `0` means no timeout. The only comment inside the method ("current transaction aborted", at `:1401`) is still true. No comment narrates the change. Finding 1 below breaks the inherited contract's meaning of `0`; that is filed under item 3 because it is a behavior defect, not a stale sentence.

## Item 2: claimed cases covered

Claimed cases, from the description and the subject of `1f01e87`:
- **isValid returns within `timeout` seconds when the socket is broken (no reply arrives).** No test exercises this. No test in `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java` makes the server stop answering. It has a connection closed by the client (`testIsValid`) and one killed by `pg_terminate_backend` (`testIsValidRemoteClose`). Both fail fast with or without this change, so neither can tell the fix from the base. This is a finding.
- **The network timeout is restored afterwards** (the subject of `0e1f482`). No test checks that `getNetworkTimeout()` after `isValid(n)` equals its value before. This is a finding.
- **The replication branch is covered too.** The new limit wraps `IDENTIFY_SYSTEM`, which has no query timeout. `ReplicationConnectionTest` (`:44`, `:65`) calls `isValid(3)` only on healthy or terminated connections, so it has the same gap.

No command lines are added. Reading the claims the other way: every hunk belongs to the subject line, and the merge commit adds nothing to the net diff.

## Item 3: boundaries, partitions, and the negative control

1. **`timeout == 0` (boundary).** The JDBC contract says `0` means no timeout is applied. The new code calls `setNetworkTimeout(null, 0)`, which reaches `PGStream.setNetworkTimeout` and then `Socket.setSoTimeout(0)`, which means wait forever.
   - Any `socketTimeout` the user configured is dropped for the duration of the call.
   - Example: a pool opens connections with `socketTimeout=10` and validates with `isValid(0)`, as all existing tests do. On a dead peer it used to fail after 10 s; it now blocks forever.
   - So the change makes the defect worse in the most common call form. It is reachable from existing user settings; the item's paragraph on pre-existing state applies.
2. **Large `timeout` (upper boundary, overflow).** `timeout * 1000` overflows `int` for `timeout > 2147483`.
   - `isValid(Integer.MAX_VALUE)` gives `-1000`, so `setNetworkTimeout` throws "Network timeout must be a value greater than or equal to 0."
   - The outer `catch` swallows that, so `isValid` returns `false` on a healthy connection.
   - Other values wrap to small positive numbers and give a much shorter timeout than requested.
   - Neither boundary is tested.
3. **Interaction with the other limits on the same work.**
   - The non-replication branch now has two limits on the same wait, both equal to `timeout`: `setQueryTimeout(timeout)` (a cancel request after `timeout` s) and the socket read timeout (also `timeout` s). They start at almost the same instant, so which one fires first is a race.
     - If the cancel wins, the server answers 57014, `isValid` returns `false`, and the connection stays open (the old behavior on a slow but alive server).
     - If the socket timeout wins, `QueryExecutorImpl.execute` catches the `IOException` (`QueryExecutorImpl.java:334-335`) and calls `abort()`, which closes the connection.
     - Slow but alive servers now get their connections closed, nondeterministically. No sentence in the change accepts this.
     - The limits should be derived from one another, for example the socket timeout set slightly above the query timeout, or the query timeout dropped where the socket timeout is set.
   - The user's existing `socketTimeout` is replaced, not combined.
     - With `socketTimeout=5` and `isValid(30)`, a dead peer now takes 30 s instead of 5 s.
     - That is within the contract, but it is the user's limit raised by the driver. Use `min(saved, timeout*1000)` when `saved > 0`.
4. **Failure output on the fault the change targets.** When the socket timeout fires, the connection is already aborted.
   - The `finally` then calls `setNetworkTimeout(...)`, whose `checkClosed()` (`:1571`) throws "This connection has been closed."
   - That exception replaces the `SocketTimeoutException` cause, so the FINE log at `:1404` records the wrong reason.
   - `isValid` still returns `false`, so this is output quality, not correctness.
   - The same masking happens for any I/O failure inside the block (`testIsValidRemoteClose`).
5. **Invalid partition: a SecurityManager without `SQLPermission("setNetworkTimeout")`.**
   - `setNetworkTimeout` calls `checkPermission` (`:1578-1581`). The resulting `SecurityException` is unchecked and not caught by `catch (SQLException e)`.
   - So `isValid` now throws on a deployment where it used to work.
   - The JDBC spec makes `setNetworkTimeout` permission-gated; `isValid` is not.
6. **Negative control.** Nothing shows that a healthy connection still returns `true` with a non-zero timeout and an unchanged `getNetworkTimeout()`. The existing tests use `isValid(0)` only, which is the case in point 1.

## Item 3a: level, placement, and the environment

There is no test. The defect lives across the socket boundary (a peer that stops answering), so an in-process unit test is not owed.

These cases are cheap to test beside the existing tests, in `IsValidTest`, which already extends `BaseTest4`:
- the overflow and `0` boundaries;
- the restored network timeout;
- the SecurityManager case.

The broken-socket case needs one of these:
- a proxy that stops forwarding (the repository has `StrangeProxyServer` in `pgjdbc/src/test/java/org/postgresql/test/util/`; worth checking whether it fits);
- `pg_sleep` with a lock that holds the server's reply.

The new test belongs in `IsValidTest`, not in a new class.

## Item 4: names by content, not by position

None. There are no new test names or messages. The new local `savedNetworkTimeOut` is named by its content. Its capitalization (`TimeOut` against `getNetworkTimeout`) is a taste point and is not filed.

## Item 5: the failure report

None in the change, since it has no assertions. The tests that will be added should use `assertEquals` for the restored timeout rather than `assertTrue(a == b)`, and should give `assertFalse(con.isValid(n))` a message naming the fault (`test-authoring`, assertion messages).

## Item 6: what the writer says it verified

None stated. The description says "never tested". There is no red run on the base commit for a hung peer and no measured duration for the new path.

## Item 7: siblings of the change

**Helpers touched: `getNetworkTimeout()` / `setNetworkTimeout(Executor, int)`.** I searched for every place that saves, changes, and restores the socket timeout:
- `PGStream.hasMessagePending` (`PGStream.java:132-139`) saves and restores in a `finally`, but calls `PGStream`, not `PgConnection`. It skips `checkClosed` and the SecurityManager, so finding 4 (masked cause) and finding 5 (permission) do not apply. That is a reason to call `queryExecutor.setNetworkTimeout` (or the stream) directly from `isValid`.
- `QueryExecutorImpl` (`:716`, `:773`) manages the timeout for COPY and goes to the socket directly. Same conclusion.

**Same symptom elsewhere.** The cancel-based `setQueryTimeout` cannot help on a dead peer anywhere in the driver, not only in `isValid`. Any statement with a query timeout and no `socketTimeout` hangs the same way. That is outside this issue's scope, but the description should name it as a follow-up or say why only `isValid` is fixed.

**Replication branch.** It is now bounded by the socket timeout only. It does not close `statement` on failure; that predates the change, and it is not filed.

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | `isValid(0)` sets `soTimeout=0` (forever), dropping a configured `socketTimeout`; a dead peer that used to fail after `socketTimeout` now hangs forever | Substantive | `PgConnection.java:1384` | Leave the network timeout alone when `timeout == 0`; add a test with `socketTimeout` set and `isValid(0)` |
| 2 | `timeout * 1000` overflows for `timeout > 2147483`; `isValid(Integer.MAX_VALUE)` returns `false` on a healthy connection | Substantive | `PgConnection.java:1384` | Clamp (e.g. `(int) Math.min((long) timeout * 1000, Integer.MAX_VALUE)`); test the upper boundary |
| 3 | Socket timeout and query timeout are equal and race; when the socket timeout wins, `abort()` closes a slow but alive connection | Substantive | `PgConnection.java:1384`, `:1392` | Derive one limit from the other (socket timeout above the query timeout, or one mechanism only); state the intended outcome |
| 4 | Existing `socketTimeout` is replaced rather than bounded; with `socketTimeout=5`, `isValid(30)` waits 30 s on a dead peer | Substantive | `PgConnection.java:1382-1384` | Use `min(saved, timeout*1000)` when `saved > 0` |
| 5 | `SecurityException` from the `setNetworkTimeout` permission check escapes `isValid`, which did not need the permission before | Substantive | `PgConnection.java:1384` (via `:1578-1581`) | Set the timeout on `queryExecutor` directly, bypassing the public permission-checked method |
| 6 | The restore in `finally` throws "connection has been closed" after an I/O abort and replaces the real cause in the log | Substantive | `PgConnection.java:1398` | Restore only when not closed, or restore through `queryExecutor` with failures suppressed |
| 7 | No test for the claimed case (hung peer returns `false` within `timeout`), for the timeout being restored, or for a healthy connection with a non-zero timeout (the control) | Substantive | `IsValidTest.java` | Add tests in `IsValidTest`, including a non-responding peer (proxy or lock-held query) with a measured upper bound on duration |
| 8 | No evidence that the change fixes the issue (description: "never tested") | Substantive | n/a | A run on a hung peer, on the base commit and on HEAD, with durations |
| 9 | Dead peers make every query timeout hang, not only `isValid`'s; the sibling is unnamed | Substantive | description | Name it as a follow-up, or say why it is out of scope |

This review did not build the project or run any test. It read the drift script's output but did not check it against a full Java parse, and it did not do a style pass over the prose.
