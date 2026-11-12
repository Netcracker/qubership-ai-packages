Final review of `8495127fe0450f94923251f67ab8e2208319437f..HEAD`. The drift script reported one member, `PgConnection.isValid(int)` at `PgConnection.java:1373`, tagged `code-changed, no-comment`. The skills I loaded were `test-authoring` and `english-developer-style`. The `javadoc-authoring` skill that `final-review` names for Java was not among the provided copies, so I did not load it.

**Previous report:** none. This is the first review of this change.

### Item 1: comments consistent with the code and with each other

None. `isValid` has no doc comment in this file; its Javadoc is inherited from `java.sql.Connection`. The one inline comment in the method, `// "current transaction aborted", assume the connection is up and running` (line 1402 area), is still true: the server answered, so the connection is up. No comment narrates the change.

### Item 2: claimed cases covered

Claims come from the commit subject `Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)`, from `0e1f482` ("Manages simply and properly get/setNetworkTimeout() in isValid()"), and from the task statement. The claimed cases are:

- A silent or broken peer makes `isValid(n)` return `false` within about `n` seconds. **No test.**
- The network timeout is restored after the call, whatever the outcome. **No test.**
- `isValid(0)` leaves the network timeout unchanged. **No test.**

The natural home is the existing `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`, which currently has only `isValid(0)` cases.

Reverse direction: every hunk belongs to the isValid sentence. The diff touches only `PgConnection.java`, so there is no unclaimed hunk.

### Item 3: boundaries, partitions, and the negative control

- **Boundary defect.** `timeout * 1000` is an `int` multiplication at `PgConnection.java:1384`. `isValid` accepts any `timeout >= 0`, so `isValid(2147484)` gives `2147484000`, which overflows to a negative value. `setNetworkTimeout` rejects negatives (line 1572), so the `SQLException` is caught at line 1401 and `isValid` returns `false` on a healthy connection. The old code passed `timeout` straight to `setQueryTimeout`, and `PgStatement.java:535` uses `seconds * 1000L`, so the sibling path does not overflow.
- **Missing partitions.** No case at `0` (no limit), `1`, `Integer.MAX_VALUE`, or the overflow value. No control: a healthy connection with a positive timeout returns `true` and leaves the network timeout unchanged. The base commit passes that control.
- **Limits on the same work.** The statement's query timeout is set to the same `timeout` in seconds (line 1394). The query-timeout cancel is sent by the driver on a separate socket, and that socket uses `cancelSignalTimeout` (`PGProperty.java:282`, default 10). I did not verify whether that cancel runs off the calling thread. If it does, the caller's wait is bounded by the socket timeout alone.
- **Per-read bound, not per-call.** `SO_TIMEOUT` applies to each read. A peer that sends one byte every `timeout - ε` seconds keeps the read loop alive past `timeout`. A real server would end that loop through the cancel at the query timeout, but a path that delivers the cancel to the server cannot be assumed. The claim "will not last more than timeout seconds" is therefore stronger than the mechanism.
- **Negative control with a SecurityManager.** `setNetworkTimeout` checks `SQLPermission("setNetworkTimeout")` at line 1578 and throws `SecurityException`, which the `catch (SQLException e)` at line 1401 does not catch. Under a policy that lacks that permission, `isValid` now throws where it used to return a boolean. I read this from the code; I did not run it.

### Item 3a: level, placement, and the environment

The behavior needs a peer that accepts the connection and then stays silent, so the observing test is at the medium level, using a local socket. It belongs beside `IsValidTest` in the same fixture, not in a new class. Whether the existing CI matrix runs `IsValidTest` against a server that can be silenced was not checked.

### Item 4: names by content, not by position

None. `savedNetworkTimeOut` names its content.

### Item 5: the failure report

None. The change adds no assertions.

### Item 6: what the writer says it verified

Neither a red run on the base commit nor a mutation verdict is stated. The task statement itself says "never tested". Requested: a test that is red on `8495127`.

### Item 7: siblings of the change

- `getNetworkTimeout` and `setNetworkTimeout` have these callers in `pgjdbc/src/main`: `PgConnection.java` (1382, 1384, 1398, 1570, 1591), `QueryExecutorBase.java` (90–96), and `PGStream.java` (132–139, 588–593). The new `isValid` is the only new caller.
- `isValid` has one caller in `pgjdbc/src/main`, which is the method itself.
- The other `* 1000` sites (`ConnectionFactoryImpl.java:89, 99, 247`, `MultiHostChooser.java:36`, `Driver.java:669`) multiply bounded configuration values, so none of them has the overflow.
- Minor, not a finding: when a timeout closes the connection, the `finally` restore throws `This connection has been closed`, which replaces the original cause in the FINE log.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| `timeout * 1000` overflows for `timeout > 2147483`; `isValid` then returns `false` on a healthy connection | Substantive | `PgConnection.java:1384` | Use `timeout * 1000L` (the `setNetworkTimeout` argument stays `int`, so clamp or reject the overflow explicitly), and add the overflow value as a case with a control. |
| `isValid` now throws `SecurityException` under a SecurityManager without `SQLPermission("setNetworkTimeout")`, where it used to return a boolean | Substantive | `PgConnection.java:1578` via `:1384` and `:1399` | Bypass the permission check for the internal save and restore, or catch the `SecurityException` and return `false`; the behavior change must be stated in the description. |
| The bound is per read, so a peer that trickles bytes can keep `isValid` alive past `timeout` if the cancel cannot reach it | Substantive | `PgConnection.java:1384`, claim in commit `1f01e87` | Either add a whole-call deadline, or narrow the sentence to "a silent socket". |
| No test for any claimed case (timeout bound, restore, `isValid(0)`) | Substantive | `pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java` | Add a test beside `testIsValid` with a peer that stays silent after startup, asserting `false` within the bound and the restored network timeout; confirm it is red on `8495127`. |
| No red run or mutation verdict stated; the description says "never tested" | Substantive | PR description | State the red run, or hold the change until it is run. |
| `savedNetworkTimeOut` spelled `TimeOut` while the methods say `Timeout` | Taste | `PgConnection.java:1382` | Rename to `savedNetworkTimeout`; declined without discussion is acceptable. |

## What this review did not check

I did not build or run the suite, so the overflow, the SecurityManager behavior, and the trickle case are established by reading the code, not by a run. I did not verify whether the query-timeout cancel runs off the calling thread. `javadoc-authoring` was not loaded. The drift script parses only the one member it reported.
