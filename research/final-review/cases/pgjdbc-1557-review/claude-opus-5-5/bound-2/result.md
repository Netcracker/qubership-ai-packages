I've read the skill, the diff and the code around it. Now I'm writing up the review form.

# Final review: `8495127..HEAD` (PgConnection.isValid network timeout, #1556)

**Inputs.** The diff is one hunk in `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1381-1400`. The merge commit `dd4d98f` adds nothing else to the range. The task statement is the PR description you quoted, plus the commit message of `1f01e87`: "Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)". The drift script reported one member: `PgConnection.isValid(int) @1373: code-changed, no-comment`. There is no earlier report of this form. I loaded `test-authoring`. Its output was cut off in my terminal, so I cite it by the sections I saw. I did not see the text of `english-developer-style`, and no finding depends on wording style.

## Item 1: comments consistent with the code and with each other
None. `isValid(int)` has no doc comment of its own. The only comment in the method, `// "current transaction aborted", assume the connection is up and running`, still describes its branch correctly. No comment talks about the change itself.

## Item 2: claimed cases covered
The change claims these cases:
- **(a)** `isValid(timeout)` returns within about `timeout` seconds when the socket is broken, meaning the peer stops answering without a reset.
- **(b)** The same bound applies to replication connections. `IDENTIFY_SYSTEM` had no timeout before; it now has one through the network timeout.
- **(c)** The connection's own network timeout is restored afterwards. This is what commit `0e1f482` says: "Manages … properly get/setNetworkTimeout()".

| Claimed case | Test |
|---|---|
| (a) bounded on a broken socket | **none** |
| (b) replication connection bounded | **none**. `ReplicationConnectionTest` lines 44 and 65 only call `isValid(3)` on healthy or closed connections. |
| (c) network timeout restored | **none**. No test reads `getNetworkTimeout()` after `isValid`. |

The PR description itself says "never tested". The commit "Add a try/catch to succeed tests" claims a change that the final diff only shows as the `try/finally`. It is not a separate hunk. No commands are documented. Every hunk is claimed.

## Item 3: boundaries, partitions, and the negative control
- **`timeout = 0` is a regression.** The JDBC contract says 0 means "no timeout". The code calls `setNetworkTimeout(null, 0)`, which sets `SO_TIMEOUT=0`, an infinite read. That removes any `socketTimeout` the user configured for the duration of the call. Before the change, `isValid(0)` on a dead peer was bounded by the user's `socketTimeout`. Now it blocks forever. That is the hang #1556 reports, now reached through the most common argument: every existing `IsValidTest` case passes `0`.
- **Upper boundary overflow.** `timeout * 1000` overflows `int` once `timeout > 2_147_483` (about 24.8 days). `setNetworkTimeout` then throws "Network timeout must be a value greater than or equal to 0". The outer `catch (SQLException)` swallows it, so `isValid` returns **false for a healthy connection**. No test covers this.
- **Limits on the same work.**
  - `SO_TIMEOUT` bounds each blocking *read*, not the whole call. Writes are not bounded at all. So the claim "will not last more than timeout seconds" holds per read: several reads, or a write blocked on a full send buffer, can exceed it.
  - The query timeout, `checkConnectionQuery.setQueryTimeout(timeout)`, is set to the same value as the socket timeout. When the socket timeout fires first, `QueryExecutorImpl` hits an `IOException`, calls `abort()`, and closes the connection. Before, a merely slow server led to a cancel and a usable connection; now that connection may be destroyed. No sentence in the change accepts this.
  - If the user's `socketTimeout` is smaller than `timeout`, the call raises it for the duration. The parameter is explicit, so this is defensible, but nothing states it.
- **Negative control.** There is no test of a healthy connection showing that `getNetworkTimeout()` is unchanged after `isValid`, for both `socketTimeout=0` and a nonzero value.
- **New failure mode under a SecurityManager.** `setNetworkTimeout` calls `checkPermission(SQL_PERMISSION_NETWORK_TIMEOUT)` (`PgConnection.java:1578-1581`). The `SecurityException` it throws is not an `SQLException`, so it escapes `isValid` unhandled. Code that held no `setNetworkTimeout` permission could call `isValid` before this change and now gets an exception.
- **Exception in the `finally` replaces a success.** If restoring the timeout throws, for example a `SocketException` from `setSoTimeout`, the outer catch turns a successful check into `false`. This is minor.

## Item 3a: level, placement, and the environment
Case (c) and both boundaries can be observed with a live connection alone, with no fault injection:
- read `getNetworkTimeout()` before and after `isValid(n)`;
- call `isValid(Integer.MAX_VALUE)` and assert `true`.

These belong in `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java` beside `testIsValid`, sharing the `BaseTest4` fixture. Case (a) needs a peer that stops answering, such as a proxy or a socket that never replies. That only works across the process boundary, and no such test exists.

## Item 4: names by content, not by position
None. The new local `savedNetworkTimeOut` is named by what it holds (the capital `O` is a taste point at most and not reported). The change adds no ordinals.

## Item 5: the failure report
None in the change, because it adds no tests. The existing `IsValidTest.testIsValid` uses bare `assertTrue(con.isValid(0))` with no message, which reports only `expected true`. That predates the change, so I note it without requesting anything.

## Item 6: what the writer says it verified
Nothing. The description says "never tested". There is no red run on the base commit and no mutation verdict.

## Item 7: siblings of the change
- Callers of `setNetworkTimeout`/`getNetworkTimeout` in `pgjdbc/src/main`:
  - `PGStream.hasMessagePending` (`PGStream.java:132-139`) uses the same save → set → restore pattern with `1` ms and never passes `0`, so the zero-means-infinite defect does not apply there.
  - `QueryExecutorBase:90-95` only delegates.
- Other validation paths that can hang on a dead peer outside `isValid` are out of scope. Pools that call `isValid(0)` are exactly the callers the timeout-0 regression reaches.
- Within `isValid`, the replication path now goes through `createStatement()` with the network timeout. Its `Statement` is still not closed when `execute` throws (it was not before either), so it leaks on exactly the failure path this change targets. This is not a regression.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| `isValid(0)` sets `SO_TIMEOUT=0` and removes the user's `socketTimeout`, so a dead peer can now hang forever | Substantive | `PgConnection.java:1384` | When `timeout == 0`, keep the existing network timeout. Add a test that `getNetworkTimeout()` is unchanged by `isValid(0)` with a nonzero `socketTimeout`. |
| `timeout * 1000` overflows for `timeout > 2_147_483`, so a healthy connection returns `false` | Substantive | `PgConnection.java:1384` | Clamp or use `long` arithmetic. Add a test that `isValid(Integer.MAX_VALUE)` is `true`. |
| `SecurityException` from `setNetworkTimeout`'s permission check now escapes `isValid` | Substantive | `PgConnection.java:1384`, `1578-1581` | Catch it and fall back to the query timeout alone, or state the new permission requirement. |
| No test for any claimed case: broken socket bounded, replication bounded, timeout restored | Substantive | `IsValidTest.java` | Add the restore and boundary tests in `IsValidTest`, plus a broken-peer test that stops answering. Show a red run on the base commit for the broken-peer test. |
| No evidence the change was run at all | Substantive | PR description | A run of the broken-peer scenario with its duration, before and after. |
| `SO_TIMEOUT` bounds each read, not writes or the whole call, so the claim "not more than timeout seconds" is stronger than the code | Substantive | `PgConnection.java:1384`, commit `1f01e87` | Narrow the claim, or bound the whole call with a deadline. |
| Socket timeout equals query timeout, so a slow but live server may get its connection aborted instead of cancelled | Taste | `PgConnection.java:1384`, `1393` | Set the network timeout slightly above the query timeout so the cancel path wins. |
| A failure while restoring in `finally` turns a successful check into `false` | Taste | `PgConnection.java:1398` | Restore inside its own try and log on failure. |

Not checked: I did not build the project or run any test suite, and I did not confirm the broken-socket behavior by running it. Item 3's statements about `abort()` and `SO_TIMEOUT` come from reading the code. I did not do a pass over the prose for style alone.
