## Final review: `8495127..HEAD`

**Change reviewed:** 5 commits, one file, `pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java`. `isValid(int)` now sets the socket timeout to `timeout * 1000` ms, runs the check, and restores the old value in a `finally`. No test file changed.

**Inputs:** I read the full diff. The task statement is the PR text you quoted. Commit `1f01e87` claims "Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)". No previous report was handed over, so there is no §4 table. The drift script ran and reported one member: `PgConnection.isValid(int) @1373: code-changed, no-comment`. I loaded `test-authoring` and `english-developer-style` and cite them below. Findings are from reading the code; nothing was built or run.

### Item 1: comments consistent with the code and with each other
none. `isValid` has no doc comment, so there is nothing to check against the new body. The one comment in the method, `// "current transaction aborted", assume the connection is up and running`, sits in the `catch` and is unchanged and still true. No comment narrates the change.

### Item 2: claimed cases covered
Claims come from the task statement and commit `1f01e87`.
- **A. `isValid(timeout)` returns within `timeout` seconds on a broken socket.** No test. See F5.
- **B. The caller's network timeout is restored after the call.** No test.
- **C. `isValid(0)` still means no limit.** No test targets the socket. The existing `IsValidTest.testIsValid` calls `isValid(0)` only on a live and on a closed connection.

### Item 3: boundaries, partitions, and the negative control
- **Values varied:** only `0`, in the existing tests. Missing boundary: any `timeout` above 2147483. The `timeout * 1000` at PgConnection.java:1384 is `int` arithmetic and wraps. For `Integer.MAX_VALUE` it yields `-1000`. `setNetworkTimeout` then throws "must be a value greater than or equal to 0", the outer `catch (SQLException)` at 1400 returns `false`, and a live connection reports invalid. Base returns `true`. See F1.
- **Negative control missing:** `isValid(1)` on a live connection stays green on base, and no test in the diff asserts it.
- **Limits on the same work**, each with where it is set:
  - **A.** Socket `SO_TIMEOUT` = `timeout` s, set at PgConnection.java:1384. It bounds each read, not the call, and does not bound writes.
  - **B.** Query timeout = `timeout` s on `checkConnectionQuery`, set at PgConnection.java:1393. Its timer sends a cancel.
  - **C.** `cancelSignalTimeout`, default `"10"` s (PGProperty.java:282), bounds the cancel's own socket (QueryExecutorBase.java:173–174). PgStatement.java:74 documents that `execute` waits for the cancel to finish.
  - **A and B** start together with the same value. At the defaults neither fires strictly first, and the cancel in C can extend the call by about 10 s past `timeout`. So the claim "will not last more than timeout seconds" is not guaranteed by the code. See F4.
- **Requested cases:** a stalled peer asserting the bound, with the socket timeout restored afterwards. Also a case with `cancelSignalTimeout` set past `timeout`, since that setting is a boundary of B.

### Item 3a: level, placement, and environment
- The overflow and control cases need a live connection, which every class in `test/jdbc4` gets from `BaseTest4`. Add them to `IsValidTest.java` beside `testIsValid`, sharing `con` (test-authoring §9).
- The stalled-peer case needs a socket whose peer stops replying after startup. That is a medium test (test-authoring §3). If the repository has a fake backend, it fits there. I did not search for one.

### Item 4: names by content, not by position
none. The new identifier `savedNetworkTimeOut` has no ordinal.

### Item 5: the failure report
none in the change, which adds no assertions. The requested cases assert a boolean returned by `isValid`, which test-authoring §7 allows. Give them a message that names the timeout value.

### Item 6: what the writer says it verified
Not stated. The PR says "never tested", and no red run on the base commit or mutation verdict appears. I did not run the suite to supply it.

### Item 7: siblings of the change
- `isValid(` has no other implementation in the repository.
- `setNetworkTimeout(` has one other main-source caller, `PGStream.hasBytesAvailable` (PGStream.java:132–139). It sets a 1 ms poll and restores in a `finally`. Its stream-level setter has no `checkClosed()` and no permission check, so F2 and F3 do not reach it, and the overflow does not reach it.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. `timeout * 1000` overflows for `timeout` > 2147483, so `isValid(Integer.MAX_VALUE)` returns `false` on a live connection (base: `true`). | substantive | PgConnection.java:1384 | Compute in `long` and clamp to `Integer.MAX_VALUE`, keeping `0` as `0`. Add the overflow case and the `isValid(1)` control to `IsValidTest`. |
| F2. Under a SecurityManager without `SQLPermission("setNetworkTimeout")`, `isValid` throws `SecurityException`, which the `catch (SQLException)` does not catch. Base never reaches that check. | substantive | PgConnection.java:1384 and 1398; permission check at 1578–1580 | Route the internal calls through `queryExecutor`, which has no permission check, or document the permission requirement and test it. |
| F3. After a socket failure, `abort()` has set `closed`, so the restore at 1398 throws "This connection has been closed." That exception replaces the I/O cause the FINE log at 1402 should carry. The `false` result is unchanged. | substantive | PgConnection.java:1398 | Restore only when `!isClosed()`, as QueryExecutorImpl.java:772 already does. |
| F4. The claim "will not last more than timeout seconds" is not guaranteed. A and B are both `timeout` from the same start. The cancel in C can run up to about 10 s more at the defaults. A bounds reads only, not writes. From reading the code, not a run. | substantive | PgConnection.java:1384, 1393; PGProperty.java:282 | Add the stalled-peer case that asserts the bound. Then derive one limit from the other, or document the pair. |
| F5. No test covers claims A, B, or C from Item 2. | substantive | `IsValidTest.java` (no line; the change adds no test) | Add the cases in Item 3 and 3a: stalled peer with the bound and restore; overflow; `isValid(1)` control. |

### What the review did not check
I did not build, run the suite, or run a stalled-peer or overflow case, so F1 to F4 rest on reading the code. The JDBC `Connection.isValid` contract text is not in the repository, so I took the contract from the method's own behavior. I did not do a prose pass; the change adds no prose beyond the unchanged `catch` comment.
