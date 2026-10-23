Review of `8495127..HEAD` (`PgConnection.isValid(int)`, one file, +16/−10)

The change has three substantive defects and no tests. On a connection with a configured socket timeout, `isValid(0)` can now block with no limit, where before that timeout bounded it. Under a SecurityManager, `isValid` can now throw `SecurityException`. A large timeout overflows when converted to milliseconds. The description says the change was "never tested", and the branch adds no test.

Inputs used: the PR description as the task statement, and the five commit messages. The drift script reported one member, `PgConnection.isValid(int) @1373: code-changed, no-comment`. There was no earlier report of this form.

### Item 1: comments consistent with the code and with each other
**None.** `isValid(int)` has no doc comment (it is `@Override`), and the change neither adds nor edits a comment. The only comment in the method, `// "current transaction aborted", assume the connection is up and running` (line 1402), is still true. No comment describes the change in passing ("now", "no longer"). The `setNetworkTimeout`/`getNetworkTimeout` pair it now calls has no comments to drift.

### Item 2: claimed cases covered
Claimed cases:
- **(a) From the PR title and commit 1f01e87:** `isValid()` returns within `timeout` seconds "even if the underlying socket is broken".
- **(b) From commit 0e1f482:** the network timeout in effect before the call is restored afterwards.
- **(c) From commit 198701f:** the existing tests still pass.

| Claimed case | Test |
|---|---|
| (a) Returns within `timeout` on a broken or unresponsive socket | **None.** No test in `IsValidTest` makes the peer stop answering. |
| (a′) The replication branch (`IDENTIFY_SYSTEM`, which has no `setQueryTimeout`) is now bounded too | **None.** `ReplicationConnectionTest:44,65` only checks a healthy and a closed connection. |
| (b) The earlier network timeout survives `isValid` | **None.** No test calls `setNetworkTimeout(x)`, then `isValid`, then checks `getNetworkTimeout() == x`. |
| (c) Existing behavior | `IsValidTest.testIsValid`, `testTransactionState`, `testIsValidRemoteClose`. These exist, but the writer says they were not run. |

All three claimed behaviors are findings: none has a test.

### Item 3: boundaries, partitions, and the negative control
- **`timeout` upper boundary (substantive).** `timeout * 1000` at `PgConnection.java:1384` is `int` arithmetic.
  - From `timeout = 2147484` (`Integer.MAX_VALUE / 1000 + 1`) the product goes negative. `setNetworkTimeout` then throws `INVALID_PARAMETER_VALUE`, the `catch` swallows it, and `isValid` returns `false` on a healthy connection.
  - Larger values wrap round to arbitrary positive millisecond values.
  - The base commit had no such limit.
  - Request: clamp with `(int) Math.min(TimeUnit.SECONDS.toMillis(timeout), Integer.MAX_VALUE)`, and add tests at 2147483 and 2147484.
- **`timeout = 0` combined with a socket timeout already set (substantive).**
  - `isValid(0)` now calls `setNetworkTimeout(null, 0)`, which means an infinite socket timeout.
  - On a connection opened with `socketTimeout=30`, or after `setNetworkTimeout(null, 30000)`, the check used to be bounded by that 30 s. Now it can block forever on the very broken socket the PR is about.
  - The same happens for any `timeout * 1000` larger than the existing timeout: the change widens a stricter bound that the user set.
  - Request: use the smaller of the two non-zero values, and keep the existing one when `timeout == 0`. Add a test for `isValid(0)` with a network timeout already set.
- **Negative control.** None is present. The test that should stay green on the base commit is "a healthy connection returns `true` and leaves `getNetworkTimeout()` unchanged". No such test exists.
- **Slow but healthy server (substantive, an unstated change in behavior).**
  - The statement's query timeout (`setQueryTimeout(timeout)`, line 1393) and the new socket timeout now expire at the same moment.
  - Before, a slow server led to a cancel, an error, `false`, and the connection stayed usable.
  - Now the socket read can time out first. The resulting `SocketTimeoutException` is an `IOException`, so `QueryExecutorImpl.java:334-335` calls `abort()` and closes the connection. `isValid` now has the side effect of closing a connection that is merely slow.
  - That may be acceptable for pools, which discard the connection anyway. Even so, the description should state it, or the socket timeout should be set slightly longer than the query timeout so the cancel can win.
- **State left behind.** Not applicable: nothing is persisted.

### Item 3a: level, placement, and the environment
- **No test at any level (substantive).**
  - Detecting an unresponsive peer cannot be done in one process without a socket, so a test needing a server is acceptable here. It belongs in `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, next to `testIsValidRemoteClose`, sharing `BaseTest4`.
  - `LoginTimeoutTest` already has a precedent: a `ServerSocket` that never answers.
  - The test for the restored timeout (2b) needs no special fixture.
- **SecurityManager (substantive).**
  - `isValid` now goes through the public `setNetworkTimeout`, which calls `securityManager.checkPermission(SQL_PERMISSION_NETWORK_TIMEOUT)` (lines 1578-1581).
  - The resulting `SecurityException` is unchecked and is not caught by `catch (SQLException e)`. Code running under a SecurityManager without `SQLPermission("setNetworkTimeout")` therefore gets an exception out of `isValid`, which used to need no permission.
  - Request: call `queryExecutor.setNetworkTimeout`/`getNetworkTimeout` directly (wrapping the `IOException`), as `PGStream.hasMessagePending` does internally.

### Item 4: names by content, not by position
**None.** The new local `savedNetworkTimeOut` is named by its content. Its spelling, `TimeOut`, is inconsistent with `getNetworkTimeout` and `soTimeout` in `PGStream`. That is taste, not reported as a finding.

### Item 5: the failure report
**None in the change**, since it adds no assertions. The neighboring tests it relies on use `assertTrue(con.isValid(0))` without a message (`IsValidTest:34`, `38`). That is outside this change, so it is not filed.

### Item 6: what the writer says it verified
**There is no evidence.** The PR description says outright "never tested". There is no run that fails on the base commit and no mutation result. Commit 198701f, "Add a try/catch to succeed tests", suggests tests were run at some point, but its try/catch was replaced in 0e1f482, and no result is reported for the final shape.

### Item 7: siblings of the change
- **`getNetworkTimeout(`/`setNetworkTimeout(` callers.** I ran `git grep` and found 4 production sites:
  - `PgConnection:1382,1384,1398`, which is this change.
  - `PGStream.hasMessagePending:132-139`, which already saves and restores `soTimeout` around a 1 ms peek. It is safe, because it always shortens and never widens.
  - The same defect does not apply to `PGStream`.
- **`isValid(` callers.** These are tests only: `IsValidTest`, `AutoRollbackTestSuite`, `ReplicationConnectionTest`. Pools call it from outside the repository.
- **Other operations that block without a bound on a broken socket.** Examples are `rollback` in pool cleanup and `close()` sending Terminate. They are outside the scope of the stated task, and I did not audit them. The description could name them as follow-up.

### Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| `isValid(0)` or a large `timeout` replaces a stricter network timeout the user set; `isValid(0)` can block forever | Substantive | `PgConnection.java:1384` | Use the smaller non-zero bound; keep the existing timeout when `timeout == 0`; add a test |
| `timeout * 1000` overflows `int` from 2147484 upward, so a healthy connection reports invalid | Substantive | `PgConnection.java:1384` | Clamp via `long`/`TimeUnit`; add tests at 2147483 and 2147484 |
| `SecurityException` from `setNetworkTimeout` now escapes `isValid` under a SecurityManager | Substantive | `PgConnection.java:1382,1384,1398` | Call `queryExecutor.get/setNetworkTimeout` directly |
| Socket timeout equal to the query timeout lets a slow but healthy connection be aborted instead of cancelled; not stated | Substantive | `PgConnection.java:1384,1393` | State it in the description, or give the socket timeout a margin over `setQueryTimeout` |
| No test for the claimed case: returns within `timeout` on an unresponsive peer (both regular and replication branches) | Substantive | `IsValidTest.java` | Add a test with a peer that stops answering, beside `testIsValidRemoteClose` |
| No test that the earlier network timeout is restored, and no healthy-connection control | Substantive | `IsValidTest.java` | `setNetworkTimeout(x)`, `isValid`, then `assertEquals(x, getNetworkTimeout())` |
| No evidence that any test was run, red or green | Substantive | PR description | Run the suite and add a test that fails on the base commit |
| Five-commit history includes a try/catch that a later commit replaced | Taste | commits 198701f, 0e1f482 | Squash into one commit whose message describes the final shape |

**Test stack (proposal only).** The repository's instructions don't name its test stack. I propose adding the line `Tests: JUnit 4 engine, JUnit 4 assertions`; I have not edited any file.

**Not checked.** I did not build the project or run any test, so none of the behaviors above was observed at runtime; they come from reading the code. I did not do a style pass on the prose.
