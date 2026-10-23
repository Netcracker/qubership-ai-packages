# Final review: `8495127..HEAD`, "Ensure isValid() will not last more than timeout seconds"

I loaded `final-review`, `test-authoring` and `english-developer-style` from the given skills directory. There is no copy of `javadoc-authoring` there, so where a comment rule matters I checked against the JDK's `Connection.isValid` contract instead. No previous report exists, so there is no table of earlier findings.

**The change.** It modifies one file, `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java`, in `isValid(int)` at lines 1373–1409. Before the probe it saves `getNetworkTimeout()`, sets `setNetworkTimeout(null, timeout * 1000)`, runs the probe, and puts the saved value back in an inner `finally`. The intermediate commits 198701f ("Add a try/catch to succeed tests") and 11b1f3f are undone or folded in by 0e1f482. No test file changed.

**Drift script output:** `PgConnection.isValid(int) @1373: code-changed, no-comment`.

### Item 1: comments consistent with the code and with each other
None. `isValid` has no doc comment of its own and inherits the JDK's `Connection.isValid`. The only comment in the body is `// "current transaction aborted", assume the connection is up and running`, which is still true: the `finally` block resets the timeout before the `catch` runs, so the early `return true` keeps its meaning. No comment narrates the change. I also checked the other comments in the file that mention the network timeout; there are none near `setNetworkTimeout`/`getNetworkTimeout` (lines 1570–1600).

### Item 2: claimed cases covered
I took the claimed cases from the PR description and the commit message of 1f01e87 ("Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)"). The PR also says it was "never tested".

| Claimed case | Test |
|---|---|
| `isValid(n)` returns within about n seconds when the peer stops answering but the socket stays open (#1556) | **none** |
| The connection's own network timeout is the same after `isValid` as before (the reason for the save/restore design) | **none**. No test calls `getNetworkTimeout()` after `isValid()`. Deleting the `finally` would not turn any test red. |
| The replication branch (`IDENTIFY_SYSTEM`) is bounded the same way | **none**. `ReplicationConnectionTest` calls `isValid(3)` only on a healthy connection. |

All three are **substantive**.

### Item 3: boundaries, partitions, and the negative control
- **`timeout * 1000` overflows** (line 1384). Any `timeout > 2147483` gives a negative number. For example, `isValid(Integer.MAX_VALUE)` gives −1000. `setNetworkTimeout` rejects negative values with `INVALID_PARAMETER_VALUE` (line 1573), the outer `catch` swallows that, and **`isValid` returns `false` for a healthy connection**. Before this change, any non-negative value worked. The fix is to clamp, for example `(int) Math.min((long) timeout * 1000, Integer.MAX_VALUE)`. The test owed is `isValid(Integer.MAX_VALUE)` returning true. **Substantive.**
- **`timeout == 0` removes an existing bound.** The spec treats 0 as "no timeout", and the change maps it to `setSoTimeout(0)`, which is infinite. If a connection was opened with `socketTimeout=5`, `isValid(0)` on a dead peer used to fail after 5 s. Now it blocks until TCP gives up, which is the very hang #1556 is about. The same thing happens whenever `timeout * 1000` is larger than the configured socket timeout, e.g. `socketTimeout=5` with `isValid(30)`: the check now waits 30 s instead of 5 s. Pre-existing state the change runs into: connections configured with `socketTimeout`. The request is to only ever lower the timeout: use `min` of the two non-zero values, and keep the saved value when `timeout == 0`. The tests owed are `isValid(0)` and `isValid(30)` on a connection opened with `socketTimeout`. **Substantive.**
- **Other limits on the same work.** These all bound the same `isValid` call, counted from the same start:
  - `setQueryTimeout(timeout)` (line 1393, non-replication branch only). A timer fires after `timeout` seconds and sends a CancelRequest over a new socket, bounded by `cancelSignalTimeout`. It fires at the same moment as the new `SO_TIMEOUT`, and its cancel to a dead host only ends the cancel attempt, not the probe. So in the hang case it is not a second working bound, and the two do not conflict.
  - The caller's own limit, e.g. a pool's validation timeout. It lies outside the repository; no evidence was given.
  - The user's `socketTimeout`, covered in the bullet above.
  
  Note also that `SO_TIMEOUT` limits each blocking read, not the whole call. The title's promise of "not more than timeout seconds" therefore holds only while the response arrives in one read, and nothing bounds a blocked write. The PR description should state this, or the code should measure a deadline. **Taste.**
- **Negative control:** none. No test checks that `isValid` still returns true for a healthy connection with a non-zero timeout and a pre-set network timeout. All existing `IsValidTest` cases use `isValid(0)`. **Substantive**, together with the missing cases above.

### Item 3a: level, placement, and the environment
Restoring the timeout can be observed with the existing `IsValidTest` fixture (`BaseTest4`, which needs the DB that CI already provides): `con.setNetworkTimeout(null, 5000); con.isValid(2); assertEquals(5000, con.getNetworkTimeout())`. The overflow and `timeout == 0` tests belong there too.

The hang case needs a peer that stops answering. It can stay in-process with the same DB if the test uses the `socketFactory` property (`PGProperty.SOCKET_FACTORY`, line 287) with a factory whose input stream can be frozen after startup. That avoids an external proxy that CI does not provide. Nothing was added, so there is nothing to place yet. **Substantive**, as part of Item 2.

### Item 4: names by content, not by position
None. The change adds one identifier, `savedNetworkTimeOut`, and no test names or messages. (`TimeOut` is cased differently from `getNetworkTimeout`, but I didn't raise it.)

### Item 5: the failure report
None. The change adds no assertions.

### Item 6: what the writer says it verified
The description says "never tested", and there is no red run and no mutation verdict. Commit 198701f's message ("Add a try/catch to succeed tests") says some suite failed at that point, but the failure isn't described, and 0e1f482 later removed that try/catch. **Substantive:** no evidence is stated.

### Item 7: siblings of the change
- **`setNetworkTimeout(Executor, int)`** (line 1570). Its only call sites in `src/main` are the two new ones in `isValid`. Using it brings in two side effects that apply here:
  - **SecurityManager check** (lines 1577–1581). Under a SecurityManager without `SQLPermission("setNetworkTimeout")`, `isValid` now throws an unchecked `SecurityException`. Pool code that expects only `SQLException` or a boolean will break. The fix is to call `queryExecutor.setNetworkTimeout`/`getNetworkTimeout` directly, since that is internal use and not the user's request. **Substantive.**
  - **`checkClosed()`** (line 1571). When the probe fails with an I/O error, `QueryExecutorImpl.execute` calls `abort()` (line 335). The restore in `finally` then throws "This connection has been closed", and that exception **replaces** the original. The `LOGGER.log(Level.FINE, …)` at line 1404 then records the closed-connection error instead of the socket timeout or I/O cause. The fix is to skip the restore when the connection is closed, or to catch and log the restore failure separately. **Substantive** (wrong diagnosis in the log).
- **`getNetworkTimeout()`** (line 1591). Only the new call site uses it, and the same SecurityManager-free fix applies.
- **The same save/lower/restore pattern** appears in `PGStream.hasMessagePending` (`PGStream.java:132–140`) and `QueryExecutorImpl.setSocketTimeout` (line 769). Both work on the stream or socket directly, without a security check or `checkClosed`, so neither has these defects. They are the model for the fix.
- **Other validation probes:** `git grep` finds no other `isValid` or `checkConnectionQuery` users in `src/main`, so the defect has no other site.

### Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| `timeout * 1000` overflows for `timeout > 2147483`, so `isValid` returns false on a healthy connection | Substantive | PgConnection.java:1384 | Clamp in `long`; test `isValid(Integer.MAX_VALUE)` |
| `isValid(0)`, or a timeout larger than `socketTimeout`, raises or removes the user's socket timeout during the check | Substantive | PgConnection.java:1384 | Only lower the timeout (min of non-zero values); test with `socketTimeout` set |
| `isValid` can throw `SecurityException` through the public `setNetworkTimeout` | Substantive | PgConnection.java:1382, 1384, 1398 | Use `queryExecutor.get/setNetworkTimeout` directly |
| The restore in `finally` throws on an aborted connection and hides the real cause in the log | Substantive | PgConnection.java:1398 | Skip the restore if closed, or catch and log it separately |
| No test for the bounded hang (#1556), for the restored network timeout, for the replication branch, or a non-zero-timeout healthy control | Substantive | IsValidTest.java (missing) | Add these to `IsValidTest`; freeze the stream through `socketFactory` for the hang case |
| No red run or mutation evidence; PR says "never tested" | Substantive | — | State the evidence that the new tests fail on 8495127 |
| `SO_TIMEOUT` bounds each read, not the whole call, and nothing bounds writes; the title promises a total bound | Taste | PgConnection.java:1384 | Qualify the claim in the description, or use a deadline |

I did not build the project or run any suite, did not check a SecurityManager run or a hung socket in practice, and did not review the prose for style.
