## Final review: `8495127..HEAD` (PgConnection.isValid)

Round 1, so there is no previous report. The change touches one file and one member, `PgConnection.isValid(int)`. The drift script reports `PgConnection.isValid(int) @1373: code-changed, no-comment`. The task statement is the PR description ("Ensure isValid() will not last more than timeout seconds"), and the commit message of 1f01e87 makes the same claim. No test file changed.

Skills: I loaded `test-authoring` and `english-developer-style`. The doc-comment skill (`javadoc-authoring`) was not among the three skills provided, so I did not load it and applied its rules by reading only.

## Item 1: comments consistent with the code and with each other

none. `isValid(int)` has no doc comment, and the change adds none (drift: `no-comment`). The existing comment at `PgConnection.java:1402` ("current transaction aborted") still describes its branch correctly. No comment narrates the change.

## Item 2: claimed cases covered

Claimed cases: (a) a broken socket with `timeout > 0` makes `isValid` return false within about `timeout` seconds; (b) the socket's network timeout is restored afterwards. Tests covering them: none. The change touches no test. `IsValidTest.java` and `ReplicationConnectionTest.java` exercise only healthy connections. The PR says "never tested". See F1.

## Item 3: boundaries, partitions, and the negative control

- **Overflow.** `timeout * 1000` at `PgConnection.java:1384` is `int` arithmetic. For `timeout = 2147484`, the product is -2147483296. `setNetworkTimeout` rejects it, the outer `catch` swallows the exception, and a healthy connection returns `false`. The base code did not have this: it passed `timeout` to `checkConnectionQuery.setQueryTimeout`, which uses `seconds * 1000L` (`PgStatement.java:535`). See F2.
- **`timeout = 0`.** `setNetworkTimeout(null, 0)` sets `SO_TIMEOUT` to 0, which means infinite. That replaces the `socketTimeout` property that `ConnectionFactoryImpl.java:98-99` applies. Before the change, `isValid(0)` on a dead socket returned `false` after `socketTimeout` seconds. Now it blocks indefinitely. There is no control for this (`socketTimeout` set, `timeout` 0). See F3.
- **Failure path.** On an I/O error the query executor calls `abort()` (`QueryExecutorImpl.java:514`), so the connection is closed. Then the `finally` at `:1398` calls `checkClosed()` and throws "This connection has been closed". That exception replaces the socket exception, and the FINE log at `:1405` records the wrong cause. See F5.
- **Negative control.** None. There is no healthy-socket control for the new path, and no `timeout > 0` versus `timeout = 0` pair.
- **Pre-existing state.** Not applicable; no persisted state is involved.

## Item 3a: level, placement, and the environment

The changed behavior is a socket read against a silent peer. The smallest test that observes it is medium: a local `ServerSocket` that answers the startup and then never replies. It belongs beside `IsValidTest` in `test/jdbc4`. The test needs a timeout guard so that the base-commit run fails on the symptom instead of hanging. No such test exists at any level (F1).

## Item 4: names by content, not by position

none. The only new identifier is `savedNetworkTimeOut`, which is a casing issue, not a positional reference (F7).

## Item 5: the failure report

none. The change adds no assertion. Any test written for F1 should use `assertFalse` with a message that names the timeout and the socket state.

## Item 6: what the writer says it verified

Not stated. There is no red run on `8495127` and no mutation verdict, and the PR says the change was never tested. This is covered by F1 and is not counted twice.

## Item 7: siblings of the change

- **`isValid(int)`.** `PgConnection` is the only main-source implementation. Callers are tests only: `ReplicationConnectionTest.java:44,65`, `AutoRollbackTestSuite.java:227,314,317`, `IsValidTest.java:34-100`. None of them exercises a broken socket.
- **`setNetworkTimeout` / `getNetworkTimeout`.** `isValid` is the only caller in `PgConnection`. `PGStream.java:132-139` uses the stream-level method for its own purpose and restores in a `finally`, as the change does.
- **`int * 1000` on a timeout.** I read every `* 1000` hit in `pgjdbc/src/main`. Four sites are `int`: the new one at `PgConnection.java:1384` (F2), and three pre-existing ones at `ConnectionFactoryImpl.java:89` (connect timeout), `:99` (`socketTimeout`), and `MultiHostChooser.java:36`. The same overflow applies to the three pre-existing sites, and it is not in this change. See F6.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F2 | `timeout * 1000` overflows for `timeout >= 2147484`, so a healthy connection reports invalid | substantive | `PgConnection.java:1384` | Compute `timeout * 1000L`, clamp to `Integer.MAX_VALUE`, and add cases at 2147483 and 2147484. |
| F3 | `isValid(0)` sets `SO_TIMEOUT` to 0 and so drops the `socketTimeout` bound on a dead socket | substantive | `PgConnection.java:1384`; `ConnectionFactoryImpl.java:98-99` | For `timeout == 0`, leave the socket timeout alone, or name the change in the PR and test it against a `socketTimeout` control. |
| F1 | No test for the claimed behavior (broken socket returns false in bounded time; timeout restored), and no healthy control | substantive | new test beside `IsValidTest.java`; `PgConnection.java:1373-1406` | Add a medium test: a local `ServerSocket` that answers startup and then goes silent. Assert `isValid(1)` is false and `getNetworkTimeout()` is unchanged. Add a healthy control. Guard against hanging, and show the red run on `8495127`. |
| F4 | The title claim is stronger than the mechanism: `SO_TIMEOUT` bounds each read, not the whole call, and does not bound writes | substantive | `PgConnection.java:1373`; PR title | Narrow the claim to "each socket read waits at most `timeout` seconds", or add an overall deadline. Say in the description that blocked writes are not bounded. |
| F5 | The `finally` replaces the socket exception with "This connection has been closed", so the FINE log names the wrong cause | substantive | `PgConnection.java:1397-1405` | Keep the first exception, for example by attaching the restore failure with `addSuppressed` or by logging the original before restoring. |
| F6 | The same `int * 1000` overflow exists in pre-existing code | substantive (follow-up) | `ConnectionFactoryImpl.java:89`, `:99`; `MultiHostChooser.java:36` | Name it as a follow-up in the PR description, or fix it in this change. |
| F7 | `savedNetworkTimeOut` casing differs from `NetworkTimeout` in the methods it pairs with and from the file's `Timeout` spelling | taste (I prefer `savedNetworkTimeout`; expect it declined) | `PgConnection.java:1382, 1398` | Rename to `savedNetworkTimeout`. |

## Not checked

I did not build or run the suite, per the instructions. The JDK behavior the findings rely on (`SO_TIMEOUT` scope, exception replacement in `finally`, int overflow) comes from reading the code and the `SO_TIMEOUT` documentation, not from a run. The doc-comment skill was not loaded, and the drift script's parse is approximate, so I checked its one member against the full diff.
