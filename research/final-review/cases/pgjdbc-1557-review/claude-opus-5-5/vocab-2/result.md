I've filled in the final-review form for this change below. One change is required before merge: the patch loses the user's `socketTimeout` limit, so `isValid(0)` on a dead socket now hangs forever instead of failing after `socketTimeout`. The PR says it was "never tested", and it adds no tests. I didn't change any files.

# Final review: `8495127..HEAD` (pgjdbc #1556, `PgConnection.isValid(int)`)

**Inputs.** The diff touches one file, `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java`: `isValid(int)` now saves the network timeout, sets it to `timeout * 1000`, runs the probe, and restores the saved value in `finally`. The merge commit adds nothing else to the diff. The drift script reports `PgConnection.isValid(int) @1373: code-changed, no-comment`. There is no previous report. I loaded `test-authoring` and `english-developer-style`. No doc-comment skill was in the provided set, but the change adds no comments.

### Item 1: comments consistent with the code and with each other

- **No comments to check against the code.** `isValid` has no doc comment (only `@Override`). The change adds no comments and introduces no new terms.
- **The new network timeout has no comment.** The added `setNetworkTimeout(null, timeout * 1000)` at `PgConnection.java:1384`, next to the existing `setQueryTimeout(timeout)` at `:1393`, looks redundant to a competent reader: why set two timeouts with the same value?
  - **Request:** a comment that answers why the query timeout alone does not bound the call. The cancel request goes over a separate connection and cannot unblock a read on a socket that no longer answers. The comment should also say what the `finally` restores and why.
  - Label: substantive.

### Item 2: claimed cases covered

The PR description and the commit messages claim three cases.

- **(a) `isValid(n)` returns within about `n` seconds when the socket is broken** (`1f01e87`, PR title). No test covers this. It is the purpose of the change. Substantive.
- **(b) The network timeout is restored after `isValid`** (`0e1f482`, "Manages simply and properly get/setNetworkTimeout()"). No test covers this. Substantive.
- **(c) "Add a try/catch to succeed tests"** (`198701f`). This message says tests failed at some point, but no test file changed and the message doesn't say which test failed or why the try/catch is correct. Substantive.
  - **Request:** a sentence in the description naming that test and its failure, or the commit squashed away.

Reading the other way: every hunk serves the claim, and the merge adds no unrelated changes. The change adds no commands.

### Item 3: boundaries, partitions, and the negative control

The timeout input is in seconds. Its boundaries are 0 (no limit, per JDBC), small positive values, and large values.

**Integer overflow at large timeouts** (`PgConnection.java:1384`).
- `timeout * 1000` overflows for any `timeout > 2147483`, including `Integer.MAX_VALUE`, which some pools pass as "no limit."
- The negative value makes `setNetworkTimeout` throw `INVALID_PARAMETER_VALUE` (`:1572-1575`). The outer `catch` logs it at FINE, and `isValid` returns `false` on a healthy connection. In the base code, these values worked.
- **Request:** compute the value in `long` and clamp it to `Integer.MAX_VALUE`, plus tests at `2147483`, `2147484` and `Integer.MAX_VALUE`.
- Label: substantive.

**The change replaces the limit users already set with `socketTimeout`** (`ConnectionFactoryImpl.java:97-99`, `PGProperty.SOCKET_TIMEOUT`).
- The new code overrides the user's read timeout and does not combine it with `timeout`.
- **With `socketTimeout=5` and `isValid(0)`:** the network timeout becomes 0, which means no limit. On a broken socket, the base code failed after 5 s; the new code blocks forever. This is a regression in exactly the scenario the PR targets.
- **With `socketTimeout=5` and `isValid(30)`:** the call now fails after 30 s instead of 5 s.
- **Request:** use `timeout == 0 ? saved : (saved == 0 ? timeout*1000 : min(saved, timeout*1000))`, plus a test for each case: `socketTimeout` below the `isValid` timeout, and `isValid(0)` with `socketTimeout` set.
- Label: substantive.

**Old and new mechanisms on the two faults.**
- **Broken socket (the fault in #1556):** the base code blocks in `read` until the OS gives up on the TCP connection; the query-timeout cancel cannot help. The new code fails after about `timeout` seconds per blocking read, with the caveat above. Socket writes are not bounded by the read timeout, but the probe is a few bytes, so that is acceptable. The PR states no duration or output from a run (see item 6).
- **Healthy but slow server:** the query-cancel timer and the socket read timeout fire at the same moment. If the read timeout wins, `QueryExecutorImpl` calls `abort()` (`QueryExecutorImpl.java:334-338`, `:588-591`) and the connection is closed. In the base code, only the query was cancelled and the connection survived. `isValid` returns `false` in both cases, so a pool reacts the same way.
  - **Request:** one sentence in the description that accepts this behavior.
  - Label: taste.

**Negative control.** All `IsValidTest` cases call `isValid(0)`, so the new path with a non-zero network timeout runs only incidentally in `AutoRollbackTestSuite` (`isValid(4)`) and `ReplicationConnectionTest` (`isValid(3)`). No control shows that a healthy connection with a user-set network timeout stays valid and keeps that timeout. That gap is covered by finding (b) in item 2.

### Item 3a: level, placement, and the environment

- **Request:** add the tests to `IsValidTest`, which already holds the `isValid` tests and extends `BaseTest4`, so they share its fixture.
- **Restore test (b) and overflow test:** each needs only the existing test server. For example: `con.setNetworkTimeout(null, 1234); con.isValid(2); assertEquals(1234, con.getNetworkTimeout())`.
- **Broken-socket test (a):** this behavior only exists across the network boundary, so it needs a medium-level test. Put a local TCP proxy between the driver and the server, stop it forwarding after the connection is established, and assert that `isValid(1)` returns `false` within a bound derived from the timeout.
- Label: substantive. This is the same finding as item 2 (a) and (b).

**Separate finding: security manager behavior.** `isValid` now calls the public `setNetworkTimeout`, which checks `SQLPermission("setNetworkTimeout")` (`PgConnection.java:1577-1580`).
- Under a security manager that lacks that permission, `isValid` throws an unchecked `SecurityException` that the `catch (SQLException)` does not catch. The base `isValid` needed no such permission.
- The `finally` also calls `checkClosed()`. After an I/O failure has aborted the connection, that throws "This connection has been closed." and replaces the real cause in the FINE log.
- **Request:** call `queryExecutor.getNetworkTimeout()` / `setNetworkTimeout()` directly, the way `PGStream.hasMessagePending` does at `PGStream.java:132-139`.
- Label: substantive.

### Item 4: names by content, not by position

None. I checked the added local `savedNetworkTimeOut` and the commit messages; nothing refers to anything by position. The capital `O` in `TimeOut` breaks the file's `NetworkTimeout` spelling (taste).

### Item 5: the failure report

None. The change adds no assertions or test cases.

### Item 6: what the writer says it verified

There is no evidence. The PR states it was "never tested", and it gives no failing run on the base commit, no run on a broken socket, and no mutation result.

### Item 7: siblings of the change

- **`isValid` implementations:** `git grep 'boolean isValid(int'` finds only this one, and both the replication probe and the regular probe sit inside the new wrapper.
- **`setNetworkTimeout`/`getNetworkTimeout` callers in main code:** the only other one is `PGStream.java:132-139`. It already saves, sets and restores the timeout at the stream level, so it does not have this defect; it is the model for the request in item 3a.
- **`setQueryTimeout` as the only bound on a network wait:** the only other uses are inside statement classes, where `socketTimeout` is the documented bound. None.

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| No comment says why a network timeout is set next to the query timeout, or what the `finally` restores | Substantive | `PgConnection.java:1382-1398` | 1 |
| No test that `isValid(n)` returns within the timeout on a broken socket | Substantive | `PgConnection.java:1373` | 2 |
| No test that the network timeout is restored after `isValid` | Substantive | `PgConnection.java:1398` | 2 |
| "Add a try/catch to succeed tests" names no test and no failure | Substantive | commit `198701f` | 2 |
| `timeout * 1000` overflows for `timeout > 2147483`; a healthy connection reports invalid | Substantive | `PgConnection.java:1384` | 3 |
| The user's `socketTimeout` is replaced; `isValid(0)` on a dead socket now hangs forever | Substantive | `PgConnection.java:1384` | 3 |
| On a slow server, the read timeout closes the connection where the old cancel kept it | Taste | `PgConnection.java:1384`, `QueryExecutorImpl.java:588` | 3 |
| Public `setNetworkTimeout` adds a `SQLPermission` check (uncaught `SecurityException`) and a `checkClosed()` that hides the cause | Substantive | `PgConnection.java:1382`, `:1398` | 3a |

The drift script parsed the file. I did not build the project or run any tests.
