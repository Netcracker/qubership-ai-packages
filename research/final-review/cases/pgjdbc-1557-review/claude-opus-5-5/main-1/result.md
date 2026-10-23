# Final review of `8495127..HEAD`: `isValid()` bounded by `timeout` (#1556)

The change wraps the validation query in `PgConnection.isValid(int)` (`pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1373`). It saves the network timeout, sets it to `timeout * 1000`, and restores it in a `finally` block. No test was added or changed.

**Inputs.** I had the diff, the five commit messages, and the PR description as the task statement. There was no previous report. The drift script output was `PgConnection.isValid(int) @1373: code-changed, no-comment`. I loaded `test-authoring` and `english-developer-style`. No `javadoc-authoring` copy was provided, and none was needed because no doc comment is involved.

## Item 1: comments consistent with the code and with each other
None. `isValid` has no doc comment, only `@Override`. The one comment in the touched region, `// "current transaction aborted", assume the connection is up and running`, is still true of the `IN_FAILED_SQL_TRANSACTION` branch. No comment narrates the change.

## Item 2: claimed cases covered
The cases claimed by the PR title and the commit `1f01e87` ("even if the underlying socket is broken"), and by the commit `0e1f482` ("get/setNetworkTimeout()"):

| Claimed case | Test |
|---|---|
| (a) `isValid(n)` returns within `n` seconds when the socket is broken (peer silent, no RST) | **none** |
| (b) The previous network timeout is restored after `isValid`, on both the success path and the failure path | **none**. No test calls `getNetworkTimeout()` after `isValid` |
| (c) The replication connection path (`IDENTIFY_SYSTEM`) under the new timeout | `ReplicationConnectionTest` calls `isValid(3)` on a healthy connection only. It does not exercise (a) or (b) |

The claim in (a) is also wider than the code delivers. `SO_TIMEOUT` (set through `setNetworkTimeout`, then `PGStream.setNetworkTimeout`, then `Socket.setSoTimeout`) bounds each blocking **read** separately. It does not bound the total time, and it does not bound a blocked **write** to a peer whose receive window is full. So "will not last more than timeout seconds" is not guaranteed. The PR description or commit message should state what the change actually bounds: reads, per read.

## Item 3: boundaries, partitions, and the negative control
- **`timeout == 0`.** JDBC defines this as "no timeout". The code now calls `setNetworkTimeout(null, 0)`, which **removes** any `socketTimeout` the user configured, for as long as `isValid(0)` runs. Before this change, a connection opened with `socketTimeout=10` could not hang in `isValid(0)` for more than about 10 s. Now it can hang indefinitely on exactly the broken socket that #1556 is about. This is a regression in the mode the issue targets. The existing tests use `isValid(0)` on a default connection where `socketTimeout` is 0, so they cannot see it.
- **Large `timeout`.** `timeout * 1000` overflows `int` once `timeout > 2_147_483`. A negative result makes `setNetworkTimeout` throw "Network timeout must be a value greater than or equal to 0". That exception is caught, so `isValid` returns `false` on a **healthy** connection. Some wrapped values come out positive and just wrong. No test covers this.
- **Control.** There is no test with a non-zero `socketTimeout` showing that the value is unchanged after `isValid`. There is also no test showing that a healthy connection stays valid and open when `timeout > 0`.
- **A new outcome the change introduced, with no test.** `setQueryTimeout(timeout)` and `SO_TIMEOUT = timeout*1000` now race at the same instant. If the socket timeout wins on a slow but alive server, `QueryExecutorImpl` calls `abort()` (`QueryExecutorImpl.java:334`, `:513`, `:2427`). The connection is then **closed**, whereas before it was only cancelled and reported invalid. This should either be stated as intended, or the network timeout should be set somewhat above the query timeout so that the server-side cancel gets the first chance.
- **SecurityManager setting.** `setNetworkTimeout` checks `SQLPermission("setNetworkTimeout")` (`PgConnection.java:1578-1581`). If a SecurityManager is installed without that permission, `isValid` now throws an uncaught `SecurityException`, where before it returned normally. Neither partition has a test.
- **Pre-existing state.** The pre-existing state here is the connection's configured `socketTimeout`. As covered above, it is overwritten when `timeout == 0` and is not verified as restored when `timeout > 0`.

## Item 3a: level, placement, and the environment
No test exists at any level. (b) and the `timeout == 0` regression can both be observed in `IsValidTest` (`pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`), next to `testIsValid` and sharing the `BaseTest4` fixture: call `con.setNetworkTimeout(null, 5000)`, then `con.isValid(1)` and `con.isValid(0)`, then `assertEquals(5000, con.getNetworkTimeout())`. The overflow case can be checked the same way with `isValid(Integer.MAX_VALUE)`, asserting `true`.

(a) depends on a peer that stops answering, so it crosses the network boundary. A loopback proxy socket that stops forwarding would keep it in one process apart from the database, which CI already provides for this class. No skip is needed.

## Item 4: names by content, not by position
None. No test names, case ids or comments were added. The new local is spelled `savedNetworkTimeOut` while the API spells it `NetworkTimeout`. That is taste.

## Item 5: the failure report
None. No assertions were added. The existing `IsValidTest` uses `assertTrue(con.isValid(0))` with no message at line 34. That line is unchanged and outside this review's scope.

## Item 6: what the writer says it verified
None stated, and the PR says outright "never tested". There is no red run on the base commit and no mutation verdict (`test-authoring` §1). The commit `198701f`, "Add a try/catch to succeed tests", suggests the suite was run at some point. That is a consistency gate, not evidence that a new test can fail.

## Item 7: siblings of the change
- `setNetworkTimeout(` / `getNetworkTimeout(`: 3 call sites outside their definitions.
  - `PGStream.hasMessagePending` (`PGStream.java:132-139`) uses the same save, set and restore pattern. The defect does not apply there: it sets 1 ms, never 0, and restores in `finally`.
  - `NetworkTimeoutTest` tests the setter only.
  - `isValid` itself.
- `isValid(` callers: `IsValidTest` (6 calls, all with `timeout = 0`, and therefore all in the partition where the change *removes* the bound), `AutoRollbackTestSuite` (3, `timeout = 4`) and `ReplicationConnectionTest` (2, `timeout = 3`). I read all of them. None configures `socketTimeout`, so none reaches the regression in item 3.
- Other operations that block on a broken socket, such as `close()` sending a Terminate or `abort()`, are not covered by this change. They could be named as follow-up for #1556.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| `isValid(0)` sets `SO_TIMEOUT` to 0, so a configured `socketTimeout` stops bounding it and it can hang indefinitely on a broken socket | Substantive | `PgConnection.java:1384` | When `timeout == 0`, leave the network timeout as it is (skip the set and restore), and add a test with `socketTimeout` set |
| `timeout * 1000` overflows for `timeout > 2_147_483`, so a healthy connection reports invalid | Substantive | `PgConnection.java:1384` | Compute in `long` and clamp to `Integer.MAX_VALUE`, and add a test |
| No test that the network timeout is restored after `isValid` | Substantive | `IsValidTest.java` | Assert `getNetworkTimeout()` after `isValid(1)` and after `isValid(0)` |
| No test that a broken or silent socket makes `isValid(n)` return `false` within about `n` s | Substantive | `IsValidTest.java` | Add a test using a proxy that stops forwarding, or name it as follow-up in the PR |
| Title claims a total bound, but `SO_TIMEOUT` bounds each read and does not cover writes | Substantive | PR title / `1f01e87` message | Reword the claim, or bound the total, for example with a timer that aborts |
| A `SecurityManager` without `setNetworkTimeout` permission now makes `isValid` throw `SecurityException` | Substantive | `PgConnection.java:1384` | Call `queryExecutor.setNetworkTimeout` directly, bypassing the permission check for this internal use, or catch the exception and fall back |
| The socket timeout and the query timeout fire together, so a slow server now gets its connection aborted instead of cancelled | Substantive | `PgConnection.java:1384,1393` | State this as intended, or set the network timeout a margin above the query timeout |
| No red run or mutation evidence; the PR says "never tested" | Substantive | — | Run the new tests on the base commit and show them red |
| `savedNetworkTimeOut` uses `TimeOut` where the API spells `Timeout` | Taste | `PgConnection.java:1382` | Rename to `savedNetworkTimeout` |

I did not build or run the test suite, and I did not do a style-only pass over the prose.
