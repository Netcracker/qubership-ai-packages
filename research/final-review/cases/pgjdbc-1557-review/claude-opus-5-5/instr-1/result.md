# Final review: `8495127..HEAD`: bound `isValid()` by its timeout (#1556)

The change is a single hunk in `PgConnection.isValid(int)` (`pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1373-1408`). It reads the connection's network timeout, sets it to `timeout * 1000` around the check query, and restores the saved value in `finally`. No test files changed. The pull request description says the change was "never tested". No previous report exists.

I ran the drift script once. Its output was `PgConnection.isValid(int) @1373: code-changed, no-comment`.

## Item 1: comments consistent with the code and with each other

None. `isValid` has no doc comment, only `@Override`. The one comment inside the method ("current transaction aborted", assume the connection is up and running, at `:1402`) is still true. The `IN_FAILED_SQL_TRANSACTION` exception now passes through the inner `finally`, which restores the timeout on a live connection, and is then caught as before. No comment narrates the change.

## Item 2: claimed cases covered

Claimed cases, from the PR title, the description, and commit `1f01e87`:

| Claimed case | Test |
| --- | --- |
| `isValid(timeout)` returns within `timeout` seconds when the socket is broken or stalled (#1556) | **none** |
| (implied) on a healthy connection, the network timeout is the same after `isValid` as before | **none** |
| (implied) the replication branch (`IDENTIFY_SYSTEM`) is now bounded too | **none**. `ReplicationConnectionTest:44,65` calls `isValid(3)` only on healthy connections |

The existing tests only exercise healthy and closed connections. `IsValidTest` uses `isValid(0)` everywhere, and `AutoRollbackTestSuite` uses `isValid(4)`. None of them would fail if the hunk were reverted. The change contains no command lines.

Reading the other way, every hunk belongs to the title's sentence. The commit messages of `198701f` ("Add a try/catch to succeed tests") and `0e1f482` describe intermediate states that the final tree no longer has. The squashed message should describe only the final shape.

## Item 3: boundaries, partitions, and the negative control

**Input `timeout`:**
- **Overflow.** `timeout * 1000` overflows `int` for `timeout > 2147483` (`:1384`). The result is negative, so `setNetworkTimeout` throws "Network timeout must be a value greater than or equal to 0" (`:1573`). That exception is caught at `:1400`, and `isValid` returns **false on a healthy connection**. Before the change, any non-negative value worked. **Substantive.**
- **`timeout == 0`.** JDBC defines 0 as "no timeout". The change calls `setNetworkTimeout(null, 0)`, which **removes** a `socketTimeout` the user configured for the duration of the check. Before the change, `isValid(0)` on a stalled socket was bounded by `socketTimeout`. Now it blocks forever, so this partition gets worse. Every existing test uses this value. **Substantive.**
- **Narrowing.** A positive `timeout` larger than the configured `socketTimeout` likewise widens the bound the user set. The network timeout should never be raised above the saved one: use `min(saved, timeout*1000)`, treating 0 as infinite.

**Pre-existing state (the user's `socketTimeout` / `setNetworkTimeout` value).** The change replaces it during the check. No test starts from a connection that has a non-default network timeout and checks it after `isValid`.

**Mechanism replaced (unbounded wait → socket read timeout):**
- **Stalled-socket fault.**
  - Old: the query-timeout cancel fires after `timeout` s, but the cancel goes over a new socket and cannot unblock a read on a dead peer. The method blocks until TCP gives up (minutes to hours, or forever) and prints nothing.
  - New: `SocketTimeoutException` → `QueryExecutorImpl` `abort()` (`QueryExecutorImpl.java:334-335`) → the `finally` calls `setNetworkTimeout` → `checkClosed()` throws "This connection has been closed".
  - That exception replaces the I/O exception, so the FINE log at `:1405` records the close, **not the timeout that caused it**. The new path therefore prints less about the cause. **Substantive.**
- **Healthy-but-slow server.** This is the fault the old query-timeout path handled. Old: the cancel request is sent, the query is cancelled, `isValid` returns false, and the connection survives. New: `setQueryTimeout(timeout)` and the network timeout fire at the **same** value, and whichever wins decides the outcome. If the socket timeout fires first, the connection is **aborted**, so a pool calling `isValid(1)` against a loaded server now destroys connections. No sentence accepts this. **Substantive.**

**Limits on the same work:**
- `socketTimeout` (user setting) and `setQueryTimeout(timeout)` (`:1393`) both bound the check. The change sets the network timeout equal to the query timeout instead of deriving one from the other.
- `SO_TIMEOUT` bounds **each read**, not the whole exchange. A response read in several reads can take up to N × `timeout`, and writes are not bounded at all. So the title's "will not last more than timeout seconds" is a per-read bound. Either the title or the code should be adjusted. **Substantive.**

## Item 3a: level, placement, and the environment

There is no test at any level. The overflow and restore partitions can be observed with the regular test server through the public API:
- `con.isValid(Integer.MAX_VALUE)` should return true.
- `con.setNetworkTimeout(null, 5000); con.isValid(0); assertEquals(5000, con.getNetworkTimeout())`.

Both belong in `IsValidTest` (`pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`), next to the existing cases, sharing `BaseTest4`'s `con`.

The stalled-socket case needs a fault across the network boundary. The repository has a `ServerSocket`-based fixture in `LoginTimeoutTest` that could be extended into a stalling proxy. That test is owed and does not exist.

On the test stack: the repository's instructions name none. Proposed line: `Tests: JUnit 4 engine, JUnit 4 assertions (org.junit.Assert)`. I have not written it anywhere.

## Item 4: names by content, not by position

None. The only new name is `savedNetworkTimeOut`. Its spelling (`TimeOut`) differs from `getNetworkTimeout` and from `soTimeout` in `PGStream.java:132`, but that is taste and does not misdirect a reader.

## Item 5: the failure report

There are no new assertions. The existing `IsValidTest` assertions the change relies on include `assertTrue(con.isValid(0))` and `assertFalse(con.isValid(0))` with no message (`IsValidTest.java:34,38`). If those fail, the report says only `expected true but was false`. That is outside this diff, so I note it without filing it.

## Item 6: what the writer says it verified

There is no evidence. The description states the change was "never tested". There is no red run on the base commit and no mutation verdict. Commit `198701f` says a try/catch was added "to succeed tests", which shows a suite was run at some point but not that any test can fail on the defect.

## Item 7: siblings of the change

- **`setNetworkTimeout`** (`:1570`), the helper the change now relies on, has two side effects that `isValid` did not have before:
  - It calls `checkClosed()`.
  - It calls `SecurityManager.checkPermission(SQLPermission("setNetworkTimeout"))` (`:1578-1581`). Under a security manager without that permission, `isValid` now throws an unchecked `SecurityException`, which the `catch (SQLException)` does not catch. `isValid` needs no permission per JDBC.

  The request is to call `queryExecutor.setNetworkTimeout` / `getNetworkTimeout` directly, as `PGStream.hasMessagePending` does (`PGStream.java:132-139`). **Substantive.**
- **`PGStream.hasMessagePending`** (`PGStream.java:132`) is the existing sibling that saves and restores `SO_TIMEOUT`. It is consistent with this pattern and does not have the defect.
- **Callers of `isValid`:** none in `pgjdbc/src/main`. Pools are the callers.
- **Docs:** `README.md:138` and `docs/documentation/head/connect.md:289` describe `socketTimeout`. The change makes `isValid` override it, and no line says so. Nothing lists the change in `CHANGELOG.md`.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `timeout * 1000` overflows for `timeout > 2147483`, so `isValid` returns false on a healthy connection | Substantive | `PgConnection.java:1384` | Compute in `long` and clamp, e.g. `(int) Math.min(Integer.MAX_VALUE, timeout * 1000L)`, plus a test with `isValid(Integer.MAX_VALUE)` |
| `isValid(0)` and large timeouts replace the user's `socketTimeout` with a longer one (0 = infinite), so `isValid(0)` can now hang where it did not | Substantive | `PgConnection.java:1382-1384` | Only lower the timeout: keep the saved value when `timeout == 0` or when the saved value is smaller and non-zero. Add a test that checks `getNetworkTimeout()` is unchanged after `isValid` |
| Socket timeout equal to query timeout races the cancel; on a slow but healthy server the connection is aborted instead of cancelled | Substantive | `PgConnection.java:1384,1393` | Derive the network timeout from the query timeout with a margin, or say in the description that aborting is accepted |
| After a socket timeout, `checkClosed()` in `finally` replaces the `SocketTimeoutException`, so the FINE log loses the cause | Substantive | `PgConnection.java:1397-1399,1405` | Restore the timeout only when `!isClosed()`, or catch it and add it as suppressed, so the original exception is logged |
| `setNetworkTimeout` makes `isValid` need `SQLPermission("setNetworkTimeout")`; a `SecurityException` escapes `isValid` | Substantive | `PgConnection.java:1382,1384,1398` | Call `queryExecutor.get/setNetworkTimeout` directly, as `PGStream.hasMessagePending` does |
| `SO_TIMEOUT` bounds each read, not the whole call; the title's "not last more than timeout seconds" is not what the code guarantees | Substantive | `PgConnection.java:1384` | Reword the title or description to a per-read bound, or add an overall deadline |
| No test for the stalled-socket case, the timeout restore, the overflow boundary, or the replication branch under a fault | Substantive | `IsValidTest.java` | Restore and overflow tests in `IsValidTest`; a stalled-socket test using a stalling proxy (`LoginTimeoutTest`'s `ServerSocket` fixture as a base) |
| No red run or other evidence that a test fails on the base commit | Substantive | (PR description) | State the red run once the tests exist |
| Intermediate commit messages ("to succeed tests") describe states the final tree no longer has | Taste | commits `198701f`, `0e1f482` | Squash with one message describing the final shape |
| `socketTimeout` docs do not mention that `isValid` overrides it | Taste | `README.md:138`, `docs/documentation/head/connect.md:289` | One sentence, if the override is kept |

I did not build the project or run any suite, did not check the change against the JDBC specification text beyond what is cited above, and did not do a style-only pass over the prose.
