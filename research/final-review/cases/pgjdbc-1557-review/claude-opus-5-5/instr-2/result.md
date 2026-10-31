I reviewed `8495127..HEAD` with the final-review form. The only file the change touches is `PgConnection.isValid(int)`. It adds no tests, and the description says the fix "was never tested". The new code doesn't keep isValid() within `timeout` seconds, and it adds three regressions that the old code didn't have (findings 1–3 below).

## Item 1: comments consistent with the code and with each other

None. The drift script reports a single member, `PgConnection.isValid(int) @1373: code-changed, no-comment`. The method has `@Override` and no Javadoc. Its one inline comment, "current transaction aborted", assume the connection is up and running (`PgConnection.java:1401`), is still true: a `25P02` error from the query passes through the inner `finally` and returns `true`. No comment describes the change as a change ("now", "no longer").

## Item 2: claimed cases covered

Claimed cases (from the PR description and the `1f01e877` commit message "Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)"):

| Claimed case | Test |
| --- | --- |
| A broken or unresponsive socket: isValid returns within `timeout` seconds | none |
| The replication path (`IDENTIFY_SYSTEM`, which had no query timeout before) is bounded too | none |
| The network timeout the caller set is restored after isValid (the purpose of the `finally`) | none |

The `IsValidTest` tests only call `isValid(0)`. Under the new code that sets the network timeout to 0, which means no timeout, so none of them exercise the bound.

The claim itself is also false as a description of the mechanism. `setNetworkTimeout` sets `SO_TIMEOUT`, which limits each blocking read, not the whole call. The empty-query round trip reads several messages (ParseComplete or BindComplete, then CommandComplete or EmptyQueryResponse, then ReadyForQuery). If a peer stalls before each message, the wait can approach a full `timeout` per message. Writes are not bounded by `SO_TIMEOUT` at all. That counts as a finding by itself: either the title should say "per read", or there should be a deadline over the whole call.

Every hunk belongs to that one claim. The merge commit `dd4d98f` brings nothing from master into the diff against the base.

**Commands in the changed files:** none.

## Item 3: boundaries, partitions, and the negative control

No tests exist, so every partition is missing. Partitions the code itself creates:

- **`timeout == 0`** (`PgConnection.java:1384`). JDBC says 0 means no timeout, so the code sets `SO_TIMEOUT` to 0 (infinite). This replaces any `socketTimeout` the user configured (`ConnectionFactoryImpl.java:97-99`) for the duration of the call. Before the change, `isValid(0)` on a dead socket gave up after `socketTimeout`. Now it blocks forever. This is the opposite of what the change is for. **Substantive.**
- **`timeout` larger than the existing network timeout.** The same happens with `isValid(30)` when `socketTimeout=5`: the limit goes from 5 s to 30 s. The user's limit encloses this work and is now raised instead of respected. The request is to derive one limit from the other: use the smaller of the two, ignoring zeros. **Substantive.**
- **`timeout > 2147483`.** `timeout * 1000` overflows to a negative number. `setNetworkTimeout` throws `INVALID_PARAMETER_VALUE`, the outer `catch` logs it, and isValid returns `false` for a healthy connection. Before the change this value worked. The request is a guard or `long` arithmetic that caps at `Integer.MAX_VALUE`. **Substantive.**
- **A `SecurityManager` without `SQLPermission("setNetworkTimeout")`.** The public `setNetworkTimeout` checks that permission (`PgConnection.java:1578-1581`). It throws `SecurityException`, an unchecked exception that the `catch (SQLException)` does not catch, so it escapes isValid. Before the change, isValid needed no permission. `QueryExecutorImpl` already does this save/set/restore by calling the stream directly (`setSocketTimeout`, around line 762). The request is to call `queryExecutor.setNetworkTimeout`/`getNetworkTimeout` directly. **Substantive.**
- **Fault comparison, old mechanism vs new:**
  - **Server slow but alive.** Before, the cancel timer from `setQueryTimeout(timeout)` fired, the query was cancelled, isValid returned `false`, and the connection stayed usable. Now the read timeout is the same length as the cancel timer and races it. If the read timeout wins, the `IOException` path calls `abort()` (`QueryExecutorImpl.java:335`, `:2428`) and closes the connection as a side effect of isValid. **Substantive** (no sentence accepts this). The request is a run that shows which one fires first, or a socket timeout set slightly above the query timeout.
  - **Dead socket after an abort.** The `setNetworkTimeout` in the inner `finally` calls `checkClosed()` and throws "This connection has been closed". That exception replaces the original I/O error, so the FINE log entry at `:1404` no longer shows the cause. It prints less than before. **Substantive.**
- **Negative control:** a healthy connection with a non-zero `socketTimeout`, where isValid returns `true` and `getNetworkTimeout()` afterwards equals the configured value. Absent.

## Item 3a: level, placement, and the environment

No test exists. The behavior crosses the network boundary (a read that blocks on a socket), so a fault-injecting test needs a server or a stalled socket. The in-process parts can still be tested at unit level: the overflow, the `timeout == 0` min-logic, and the timeout restore. The natural place is `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, which already has `BaseTest4` and the remote-close fixture. The stalled-socket case can be built like `testIsValidRemoteClose`, for example with a proxy that stops forwarding, or with `pg_sleep` on another session holding a lock. It should skip with `assume…` where the CI matrix doesn't provide that.

## Item 4: names by content, not by position

None. There are no new names or messages. The only new identifier, `savedNetworkTimeOut`, describes its content. The capital O differs from `getNetworkTimeout`, but that is taste and not reported.

## Item 5: the failure report

None. The change adds no assertions. The existing `assertTrue(con.isValid(0))` in `testIsValid` has no message, but that line is outside the diff.

## Item 6: what the writer says it verified

None stated. The PR description says the fix was "never tested". There is no red run on the base commit and no mutation verdict. Commit `198701f` ("Add a try/catch to succeed tests") suggests the suite was run to get it green, not to show that the fix can fail.

## Item 7: siblings of the change

Helpers the change now relies on: `PgConnection.setNetworkTimeout` and `getNetworkTimeout`. `git grep` finds no other callers in `src/main`. Other sites with the same save/set/restore pattern:

- **`PGStream.hasMessagePending` (`PGStream.java:132-140`).** Restores the timeout in `finally` and sets a fixed 1 ms. It doesn't have the 0, overflow or permission defects.
- **`QueryExecutorImpl.processNotifies(int)` (around `:700-765`).** Calls `setSocketTimeout` directly, so it bypasses the `SecurityManager` check. This is the model for finding 4.

The other path with the same symptom is the replication branch of isValid itself. It has no `setQueryTimeout` and depends on the network timeout alone, so on that path the `timeout == 0` regression makes isValid unbounded. That is covered by finding 1, not filed again. Other blocking calls a pool makes on a dead socket (`rollback`, `close`) are outside the task statement, but the description should name them as follow-up if #1556 covers them.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `isValid(0)` sets the network timeout to 0 (infinite) and overrides the user's `socketTimeout`, so a dead socket now blocks forever | Substantive | `PgConnection.java:1384` | Use the smaller of the two non-zero limits; leave the timeout unchanged when `timeout == 0` |
| 2 | A `timeout` larger than the configured `socketTimeout` raises the limit for the call | Substantive | `PgConnection.java:1384` | Same: derive the limit from the existing one |
| 3 | `timeout * 1000` overflows when `timeout > 2147483`, so a healthy connection reports invalid | Substantive | `PgConnection.java:1384` | Compute in `long` and cap at `Integer.MAX_VALUE` |
| 4 | The public `setNetworkTimeout` throws `SecurityException` under a SecurityManager, and it escapes isValid | Substantive | `PgConnection.java:1382-1398` | Call `queryExecutor.get/setNetworkTimeout` directly, as `QueryExecutorImpl` does |
| 5 | The title claims a bound on the whole call; `SO_TIMEOUT` bounds each read, and writes not at all | Substantive | `PgConnection.java:1384`, PR title | A deadline over the whole call, or a title that says "per read" |
| 6 | The read timeout equals the query timeout and races the cancel timer; a slow but live server can now get its connection aborted | Substantive | `PgConnection.java:1384`, `:1392` | A run showing which fires first, or a socket timeout set above the query timeout |
| 7 | When the connection was aborted, the `setNetworkTimeout` in `finally` throws and hides the original I/O error from the log | Substantive | `PgConnection.java:1397-1399` | Skip the restore when `isClosed()`, or log the original exception |
| 8 | No test covers any claimed case: broken socket, replication path, timeout restored, or the healthy-connection control | Substantive | `IsValidTest.java` | Tests in `IsValidTest` for each, including the 0, overflow and `socketTimeout` partitions, with a red run on the base |
| 9 | No evidence that any test can fail; the PR says "never tested" | Substantive | — | The red run on `8495127` |

Not checked: I did not build the project or run its tests. The fault timings above come from reading `SO_TIMEOUT`, `abort()` and the cancel timer, not from a run. Wording was not reviewed for style.
