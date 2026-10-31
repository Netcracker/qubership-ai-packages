The review is complete. Nothing was changed or committed, and I did not build or run the tests.

## Review of `8495127..HEAD` (issue #1556, `isValid()` timeout)

**Scope read:** the diff is one file, `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java` (16 insertions, 10 deletions in `isValid(int)`). Five commits, and the net diff is the whole change. I read the surrounding `setNetworkTimeout`/`getNetworkTimeout`, `PGStream`, `ConnectionFactoryImpl`, `QueryExecutorImpl`, `IsValidTest` and `AutoRollbackTestSuite`.

**Skills and inputs:** `final-review` in full. `test-authoring` and `english-developer-style` were loaded from the provided skills directory. The doc-comment skill (`javadoc-authoring`) and `change-description-authoring` are named by the skills but are not in that directory, so Items 1 and 2 used the English style skill and the file's own comments. The task statement is the PR description you quoted.

**Drift script** (`comment-drift.py 8495127… HEAD`) reported one entry: `PgConnection.isValid(int) @1373: code-changed, no-comment`.

### Previous report
None. This is the first review of this change.

### Item 1: comments consistent with the code and with each other
none. `isValid` has no doc comment in this file; it inherits the `java.sql.Connection` contract. The one comment in the method (`// "current transaction aborted", assume the connection is up and running`) is still true. No comment narrates the change.

### Item 2: claimed cases covered
Claims come from the commit subject `Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken`, the PR title, and commit `0e1f482` ("manages … get/setNetworkTimeout() in isValid()", i.e. the prior timeout is restored).
- Broken socket, call returns within `timeout` seconds: **no test** (finding F5).
- Prior network timeout is restored after the call: **no test** (part of F5).
- Commit `198701f` ("Add a try/catch to succeed tests") touches only `PgConnection.java`, so no test changes exist in the range.
- Hunk-to-claim: the only hunk is the claimed change. No commands in the diff.

### Item 3: boundaries, partitions, negative control
- Boundary: `timeout * 1000` is `int` arithmetic. For `timeout >= 2147484` it overflows to a negative value, `setNetworkTimeout` throws `PSQLException` ("must be … >= 0"), and the outer catch returns `false` on a healthy connection (F2). Base code accepted that value. No test at this boundary.
- Partition `timeout == 0`: SO_TIMEOUT becomes 0 (infinite), replacing a user-configured `socketTimeout` (F3).
- Negative control: existing `IsValidTest` and `AutoRollbackTestSuite` cover healthy and closed connections with `isValid(0)` and `isValid(4)`. Neither reaches the new path with a stalled socket.
- Limits on the same work: `socketTimeout` (set in `ConnectionFactoryImpl.java:96-99`) is overwritten for the call (F3). The statement query timeout `checkConnectionQuery.setQueryTimeout(timeout)` is set to the same value and does not unblock the caller's blocked read, so it does not bound the call. SO_TIMEOUT bounds each read, not the whole call (F4).
- Level (3a): observing a stalled socket needs a socket that stops answering, so it is a medium-level test beside `IsValidTest`. An in-process test cannot observe it.

### Item 4: names by content, not by position
none. No new names or cases.

### Item 5: the failure report
none. No assertions were added.

### Item 6: what the writer says it verified
The PR states "never tested". There is no red run on the base commit and no mutation verdict. Stated as the writer's own statement; I did not run the suite (F5).

### Item 7: siblings of the change
- `setNetworkTimeout(Executor, int)` has no other callers in `src/main`; the only new calls are the two in `isValid`.
- The house idiom for a temporary socket timeout is at the `PGStream` layer: `PGStream.hasMessagePending` (`PGStream.java:132-139`) and `QueryExecutorImpl.setSocketTimeout` (`QueryExecutorImpl.java:769`). Those bypass the JDBC-level `SecurityManager` check and `checkClosed()`. The change uses the public method instead, which causes F1.
- The replication branch and the `createStatement` branch both sit inside the new timeout, so both are covered.
- Not checked: `cancel()` on a broken socket is a possible twin path with the same symptom (`QueryExecutorBase.java:174`). It is outside this change.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Under a `SecurityManager` without `SQLPermission("setNetworkTimeout")`, `isValid` now throws `SecurityException` (a `RuntimeException`), which escapes the `catch (SQLException)`. The restore in `finally` also throws. Base `isValid` never checked this permission. | substantive | `PgConnection.java:1382-1398`; check at `PgConnection.java:1570-1580` | Set the socket timeout at the layer the house idiom uses: `queryExecutor.setNetworkTimeout(...)` and `getNetworkTimeout()`, as `PGStream.hasMessagePending` does. Or state the permission requirement. |
| F2 | `timeout * 1000` overflows `int` for `timeout >= 2147484`. The call then throws inside the try and returns `false` on a healthy connection. Base accepted this value. | substantive | `PgConnection.java:1384` | Compute in `long` and clamp to `Integer.MAX_VALUE`, or reject with a stated message. Add a boundary case at `2147483` and `2147484`. |
| F3 | `socketTimeout` is replaced for the call. For `isValid(0)` SO_TIMEOUT becomes 0 (infinite), so a user-configured `socketTimeout` no longer bounds the call. For `isValid(n)` with a longer `n` it lengthens the bound. | substantive | `PgConnection.java:1384`; `ConnectionFactoryImpl.java:96-99` | State the precedence in the change, and for `timeout == 0` keep the configured value rather than 0. Add a control with `socketTimeout` set. |
| F4 | The title and commit subject ("will not last more than timeout seconds") state a whole-call guarantee. SO_TIMEOUT bounds each read. A peer that dribbles bytes can extend the call, and a blocked write is not bounded. The broken-socket case with no bytes is bounded only as a per-read effect. | substantive | commit `1f01e87` subject; `PgConnection.java:1384` | Rewrite the claim to the per-read behavior, or add a deadline that bounds the whole call. |
| F5 | No test and no red run for the claimed cases: broken socket returns within `timeout`, prior timeout is restored. The PR states "never tested". | substantive | Test beside `jdbc4/IsValidTest.java`; no file in the diff | A medium test with a server that accepts and never answers: `isValid(1)` returns `false` in bounded time, and `getNetworkTimeout()` is unchanged after the call. Run it on base (hangs or red) and on head (green), and state both results. |

### Not findings
- Item 1: no comment to re-read.
- Item 4 and Item 5: no names or assertions were added.

### What this review did not check
- The test suite was not run and no build was performed.
- `javadoc-authoring` and `change-description-authoring` were not available, so the doc-comment and commit-message rules were not applied.
- The `cancel()` twin path and the `socketTimeout` precedence against the JDBC spec wording were not checked against an external source.
