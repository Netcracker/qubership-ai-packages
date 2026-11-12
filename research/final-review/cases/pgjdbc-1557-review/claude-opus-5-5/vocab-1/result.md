# Final review of `8495127..HEAD`, the isValid() network-timeout change

The change puts the socket read timeout (`setNetworkTimeout`) around the probe in `PgConnection.isValid(int)` (`pgjdbc/src/main/java/org/postgresql/jdbc/PgConnection.java:1381-1399`) and restores the old value in a `finally` block. The diff touches only that one file. The merge commit `dd4d98f` brings in no other hunks.

Inputs I used:
- **Diff and commit messages:** `1f01e87` says "Ensure isValid() will not last more than timeout seconds even if the underlying socket is broken (issue #1556)". `198701f` and `0e1f482` follow it.
- **Task statement:** the PR description, which says the change was "never tested".
- **Drift script:** it reports `PgConnection.isValid(int) @1373: code-changed, no-comment`.

There is no earlier report of this form.

## Item 1: comments consistent with the code and with each other

**None.** `isValid` has no doc comment beyond `@Override`, and the change adds no comment, so no comment can contradict the code and the change coins no terms.

One uncommented expression would puzzle a reader: the probe sets the statement timeout (`setQueryTimeout(timeout)`) and the socket timeout (`timeout * 1000`) to the same value, and nothing says why both are needed or which one should fire first. That is a real defect rather than a missing comment, so it is filed under item 3 (F3).

Taste: `savedNetworkTimeOut` spells "TimeOut", while the rest of the code uses `NetworkTimeout`.

## Item 2: claimed cases covered

There is no test class comment, so the claims come from the commit messages and the PR description:

| Claimed case | Test |
| --- | --- |
| `isValid(timeout)` returns within about `timeout` seconds when the socket is broken (#1556) | **none** |
| The `replicationConnection` (`IDENTIFY_SYSTEM`) branch is bounded the same way | **none** |
| The saved network timeout is restored after `isValid`, on both the true and the false outcome | **none** |
| `198701f`: "Add a try/catch to succeed tests" (a restore failure must not throw) | **none**; `0e1f482` later removed that try/catch |

- **F1 (substantive):** the change adds no test, and the PR says it was never tested. The existing `IsValidTest` (`pgjdbc/src/test/java/org/postgresql/test/jdbc4/IsValidTest.java`) only calls `isValid(0)` on a healthy or closed connection, so it never reaches the new behaviour.
  - **Request:** add tests to `IsValidTest`:
    - A connection whose peer stops answering returns `false` from `isValid(1)` within a bounded time. A proxy that stops forwarding works, or a backend stopped with `pg_terminate_backend`/`SIGSTOP`.
    - `getNetworkTimeout()` is unchanged after `isValid(n)` on both outcomes.

No hunk changes anything outside what the PR claims.

## Item 3: boundaries, partitions, and the negative control

**F2 (substantive): `isValid(0)` now turns off any network timeout the user had set.** JDBC defines `timeout == 0` as "no timeout", so the code calls `setNetworkTimeout(null, 0)`, which means an infinite socket timeout.
- **Before the change:** a user who had called `setNetworkTimeout(5000)` against broken sockets kept that 5 s bound inside `isValid(0)`.
- **After the change:** `isValid(0)` can block forever on exactly the broken socket that issue #1556 describes. This is the pre-existing state the change runs into, and no test or sentence in the change covers it.
- **Request:** when `timeout == 0`, leave the saved network timeout as it is. More generally, apply the new value only where it is tighter than the saved one (saved is 0 or larger). Add a test that sets a network timeout, calls `isValid(0)`, and checks it stays bounded.

**F3 (substantive): the two limits are equal, so the inner one does not reliably fire first.** The statement timeout (`setQueryTimeout(timeout)`) and the socket timeout (`timeout * 1000`) both fire at `timeout`.
- On a server that is alive but slow, the socket read can time out before the cancel timer does. An `IOException` in `QueryExecutorImpl` calls `abort()` (for example `QueryExecutorImpl.java:334-335`), which closes a healthy connection. Before the change, the cancel produced an ordinary error and the connection stayed usable.
- Neither the commit message nor the PR accepts this.
- **Request:** derive one limit from the other. For example, give the socket timeout a margin above the query timeout, so the cancel path fires first and the socket timeout only catches a dead peer.

**F4 (substantive): a large timeout now makes a live connection report as invalid.** `timeout * 1000` overflows `int` for `timeout > 2147483` seconds.
- The negative value makes `setNetworkTimeout` throw `INVALID_PARAMETER_VALUE` (`PgConnection.java:1572-1574`). The outer `catch` swallows it, so `isValid` returns `false` for a connection that is fine.
- Before the change, any `timeout >= 0` worked.
- The value just outside this boundary has no test.
- **Request:** clamp the multiplication (for example `Math.min(timeout, Integer.MAX_VALUE / 1000) * 1000`) and add a test with `Integer.MAX_VALUE`.

**F5 (substantive): on a broken socket the log loses the real cause.** After an I/O error, `abort()` has closed the connection. The `finally` restore then calls `setNetworkTimeout`, whose `checkClosed()` throws "This connection has been closed". That exception replaces the original I/O error, so the `LOGGER.log(Level.FINE, …)` at `:1404` records the closed-connection exception instead of the I/O error. The new code fails on the same fault but tells the user less.
- **Request:** restore only when `!isClosed()`, or catch the restore's exception and add it as suppressed to the original one.

On the overall bound: `SO_TIMEOUT` limits each read separately, not the whole call. A server that sends bytes slowly, or a blocked write, can still push `isValid` past `timeout`. That is weaker than "will not last more than timeout seconds". I file it as taste, because the probe exchanges one small message.

## Item 3a: level, placement, and the environment

- **F6 (substantive): `isValid` now throws `SecurityException` under a security manager.** `setNetworkTimeout` calls `securityManager.checkPermission(SQL_PERMISSION_NETWORK_TIMEOUT)` (`:1578-1581`).
  - With a security manager that lacks `SQLPermission("setNetworkTimeout")`, `isValid` throws that exception. It is unchecked, so the `catch (SQLException)` does not catch it.
  - Before the change, `isValid` needed no permission. Pools commonly call `isValid` inside sandboxed applications.
  - **Request:** call `queryExecutor.setNetworkTimeout/getNetworkTimeout` directly, the way `PGStream.hasMessagePending` does (`PGStream.java:132-139`). That way no permission check is involved, and the `checkClosed()` problem in F5 goes away too.
- **Test level:** a broken socket only shows up across the network, so a test that needs a server is right here. The finding is that no such test exists (F1).

## Item 4: names by content, not by position

**None.** The change adds no comments, case ids, or messages that refer to anything by position or ordinal.

## Item 5: the failure report

**None.** The change adds no assertions. The tests requested in F1 should use `assertEquals` on the restored timeout, and put the elapsed time in the message of the duration assertion.

## Item 6: what the writer says it verified

**No evidence of verification.** The PR says outright that the change was "never tested". There is no red run against the base commit and no mutation verdict.

## Item 7: siblings of the change

- **The same probe elsewhere:** `isValid` is the only place that runs the `checkConnectionQuery`/`IDENTIFY_SYSTEM` probe.
- **The pattern this change relies on:** the save, set, and restore of the socket timeout also appears in `PGStream.hasMessagePending` (`PGStream.java:132-139`).
  - That sibling uses the stream-level setter, which has no permission check and no `checkClosed`.
  - It restores in `finally`, and its timeout is fixed at 1 ms, so F2 and F4 don't apply to it.
  - It is the model F6 asks this change to follow.
- **Other callers:** `git grep -n 'setNetworkTimeout('` finds no other caller in `main` that needs the same fix.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| F1: no test that `isValid` is bounded on a broken socket, or that the timeout is restored | Substantive | `IsValidTest.java` | 2 |
| F2: `isValid(0)` replaces a user-set network timeout with infinity | Substantive | `PgConnection.java:1384` | 3 |
| F3: equal query and socket timeouts race, and a socket timeout aborts a live connection | Substantive | `PgConnection.java:1384,1392` | 3 |
| F4: `timeout * 1000` overflows, so a live connection returns `false` | Substantive | `PgConnection.java:1384` | 3 |
| F5: the restore in `finally` hides the original I/O error in the log | Substantive | `PgConnection.java:1398` | 3 |
| `SO_TIMEOUT` bounds each read, not the whole `isValid` call | Taste | `PgConnection.java:1384` | 3 |
| F6: `isValid` now throws `SecurityException` without `setNetworkTimeout` permission | Substantive | `PgConnection.java:1382,1384` | 3a |
| `savedNetworkTimeOut` spells "TimeOut" | Taste | `PgConnection.java:1382` | 1 |

I did not build the project or run any tests, as instructed. F3 and F5 are based on reading `QueryExecutorImpl`'s `abort()` path, not on a run.
