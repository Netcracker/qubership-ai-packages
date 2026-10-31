## Final review: `6e453aae..HEAD` (SSL response timeout)

Nothing was changed and nothing was committed. I did not build or run tests. The drift script ran (exit 0). Its six flags include two parser artifacts, noted under Item 1.

Loaded: `final-review`, `test-authoring` and `english-developer-style`, all from the skills folder. `javadoc-authoring` is not in that folder, so the Javadoc rules were applied from the form and the developer-style skill alone. There is no previous report, so there is no open-findings table.

**The main result: the fix does not bound the wait in the default configuration.** This comes from reading the code, not from a run.

---

### Item 1: comments consistent with the code and with each other

- `ConnectionFactoryImpl.enableSSL` (`code-changed, no-comment`): the inline comment at lines 538–540 says "if the current timeout is less than sslTimeout then use the smaller timeout". The guard at line 541 also requires `currentTimeout > 0`. Read literally, the comment makes an unset socket timeout (0) the smaller value, which is the infinite wait. Finding S2.
- `SSL_RESPONSE_TIMEOUT` (`comment-added`): the first sentence is a cause ("After requesting an upgrade … there are reports … without a timeout here, the client can wait forever"). It does not state what the property does; that is in the second sentence. Finding S3. "Reset after" is true only on success, but `tryConnect`'s `catch (Exception)` closes the stream on failure, so the stale timeout is harmless.
- `BaseDataSource.getSslResponseTimeout` / `setSslResponseTimeout` (`comment-added`): see taste T3.
- `PGProperty` class comment (`code-changed, comment-unchanged`): still true. The new property has a datasource setter.
- Drift artifacts: `PGProperty.getName()` `comment-changed` and `BaseDataSource.setConnectTimeout` `code-changed` are parser artifacts. The diff's only `PGProperty` hunk is `@@ -674,0 +675,9`, and the `BaseDataSource` hunk starts after `setConnectTimeout`'s closing brace.
- Cross-file: the README row's "Socket timeout" and the missing unit conflict with the neighbouring rows and with `PGProperty` (finding S6). The `connect.md` entry does not state the `socketTimeout` cap or the zero case (finding S4).

### Item 2: claimed cases covered

Every case the description, commit messages and code comments claim, with its test:

- C1. Timeout set before the SSL request and reset after: no test.
- C2. A hang becomes a bounded wait under the default settings: no test. S1 shows this claim is false for the default settings.
- C3. Effective wait is the lesser of `socketTimeout` and `sslResponseTimeout` (commit 574b763): no test.
- C4. Property name, default 5000, milliseconds: no test.
- C5. `BaseDataSource` accessors: no test.

No command lines or quoted error texts were added.

Hunks no sentence claims: the README row carries 168 trailing spaces after its closing `|` (finding S7). The neighbouring rows have none.

### Item 3: boundaries, partitions and the negative control

Partitions the change claims, none tested:

- `sslResponseTimeout` unset, 0, negative, or a small positive value.
- `socketTimeout` unset, smaller than, or larger than `sslResponseTimeout`.
- `sslmode` `disable` or `allow` as the negative control: no SSL request is sent, so nothing should change.

Negative values: `Socket.setSoTimeout` throws `IllegalArgumentException`. That is neither `IOException` nor `SQLException`, so it escapes the connect path unwrapped (finding S5). The neighbouring `SOCKET_TIMEOUT` is guarded with `> 0` at line 113.

Limits on the same work:

- `loginTimeout` (`Driver.java:287–296`) runs the whole connect in a thread joined with that timeout. A `loginTimeout` shorter than `sslResponseTimeout` fires first, and the docs do not say so. At the defaults `loginTimeout` is 0, so the inner limit fires first. Covered by S4.
- `connectTimeout` covers only the socket connect, which precedes the request. It does not enclose the request.
- `socketTimeout` is handled by the lesser-of logic.
- Multi-host: each host attempt waits up to `sslResponseTimeout`, so N hanging hosts take about N × 5 s.

How each version fails, on two faults:

| Fault | Old code | New code as written, `socketTimeout` unset | New code, `socketTimeout` set |
| --- | --- | --- | --- |
| Silent server | Never fails, prints nothing | Never fails, prints nothing (S1) | About 5 s per host, then "The connection attempt failed." with a `SocketTimeoutException` cause |

With `sslmode=prefer`, the timeout does not downgrade to plaintext. The `SQLException`-only fallback at `ConnectionFactoryImpl:236` does not catch it. The change should state this.

**The S1 mechanism, from reading the code:**

1. `tryConnect` calls `setNetworkTimeout` only when `socketTimeout > 0` (line 113). That method is the only caller of `VisibleBufferedInputStream.setTimeoutRequested`. So with `socketTimeout` unset, `timeoutRequested` is false.
2. `enableSSL` sets the timeout with `pgStream.getSocket().setSoTimeout(...)`, which bypasses `PGStream.setNetworkTimeout`.
3. `receiveChar` → `read()` → `ensureBytes` → `readMore`. In `readMore`, a `SocketTimeoutException` with `timeoutRequested == false` is swallowed (`VisibleBufferedInputStream.java:165–172`). `readMore` returns true with zero bytes, and the `ensureBytes` loop reads again.
4. The read therefore re-arms every `sslResponseTimeout` and never returns while the server stays silent. This is the same hang the change is meant to fix.

The fix is to call `pgStream.setNetworkTimeout(...)` at lines 545 and 554 instead of `getSocket().setSoTimeout(...)`. `enableSSL` already declares `IOException`.

### Item 3a: level, placement and environment

The behavior crosses a socket, so no in-process test covers it. The smallest level is medium: a loopback `ServerSocket` that accepts and never answers the 8-byte request. It needs no PostgreSQL server. The natural place is beside `SocketTimeoutTest` and `ConnectTimeoutTest` in `org.postgresql.test.jdbc2`. No test exists (finding S8).

### Item 4: names by content

None. The new identifiers (`sslTimeout`, `currentTimeout`) name their content.

### Item 5: the failure report

None. The change adds no assertions.

### Item 6: what the writer says it verified

No red run on the base commit, no test, and no run of the default configuration is stated anywhere in the range. S1 is the defect a red run on the default settings would have shown.

### Item 7: siblings

- GSS encryption request (`ConnectionFactoryImpl.java:462–470`): same request-response shape, same unbounded `receiveChar()`, reached for `gssEncMode` prefer or require before the SSL step (line 162). The description does not claim it and does not name it as follow-up (finding S9). The S1 fix applies there too.
- The `PGStream.setNetworkTimeout` helper is bypassed (S1).
- Property lists: `git grep` finds `socketTimeout` in the README and `connect.md`, and both list the new property. No prose counts the set's size.

---

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| S1 | With `socketTimeout` unset (the default), the SSL response read never ends. The timeout is set on the raw socket, so `timeoutRequested` stays false and `readMore` swallows the timeout, looping forever. | Substantive (blocker) | `ConnectionFactoryImpl.java:545, 553, 554`; `VisibleBufferedInputStream.java:165–172` | Use `pgStream.setNetworkTimeout(sslTimeout)` and `pgStream.setNetworkTimeout(currentTimeout)`. Run: default settings, silent server, `sslmode=require`; the connect must fail in about 5 s. This run was not done. |
| S2 | The inline comment omits the `currentTimeout > 0` guard, so a reader takes an unset socket timeout as the smaller value. | Substantive | `ConnectionFactoryImpl.java:538–541` | State the guard: "if a socket timeout is set and is less than sslTimeout, use it." |
| S3 | The `SSL_RESPONSE_TIMEOUT` doc's first sentence is a cause, not a statement of what the property does. | Substantive | `PGProperty.java:675–677` | Open with what the property bounds, e.g. "Bounds the wait for the server's answer to the SSL request." Keep the failover reason after it. |
| S4 | `connect.md` omits three things: the wait is the lesser of `socketTimeout` and this value; zero means no timeout; and `loginTimeout` can end the wait earlier. | Substantive | `docs/documentation/head/connect.md:330–332` | Add the three conditions in the sentence each one limits. |
| S5 | A negative value reaches `Socket.setSoTimeout`, which throws `IllegalArgumentException`, escaping the connect path unwrapped. | Substantive | `ConnectionFactoryImpl.java:535, 545` | Guard with `> 0` like `socketTimeout`, or reject with a `PSQLException`. Run with `-1`. |
| S6 | The README row has no unit, and its neighbours are in seconds (`connectTimeout` 10, `socketTimeout` 0). "Socket timeout" also invites confusion with `socketTimeout`. | Substantive | `README.md:121` | Write "in milliseconds" and drop "Socket". |
| S7 | 168 trailing spaces after the row's closing `\|`. No sentence claims them. | Substantive (Item 2 rule) | `README.md:121` | Remove the trailing whitespace. |
| S8 | No test covers any claim (C1–C5). A medium test is owed. | Substantive | new test beside `pgjdbc/src/test/java/org/postgresql/test/jdbc2/SocketTimeoutTest.java` | A loopback `ServerSocket` test with: (a) default `socketTimeout`, silent server, expect failure in about 5 s; (b) `socketTimeout=1`, expect about 1 s; (c) `sslmode=disable` as the control, no request sent. |
| S9 | The GSS encryption request has the same unbounded wait and is not named. | Substantive | `ConnectionFactoryImpl.java:462–470` | Fix it with the same change, or name it as follow-up in the description. |
| T1 | The second comment sentence ("We could do something tricky … pretty readable") narrates a rejected alternative and gives an opinion. | Taste | `ConnectionFactoryImpl.java:540` | Drop it. |
| T2 | The `connect.md` entry is indented with four spaces and has no blank line after the bullet, so the description runs into the `= int` line. Neighbours use a tab and a blank line. | Taste | `connect.md:330–332` | Match the neighbours. |
| T3 | Accessor docs: the getter's "SSL ResponseTimeout" is a fragment; there are extra blank Javadoc lines; `set(properties,sslResponseTimeout)` has no space after the comma, which a checkstyle `WhitespaceAfter` rule would flag (not run). | Taste | `BaseDataSource.java:357–374` | Match the neighbouring accessors. |

**Not checked:** I did not build or run the code or the tests, so S1 and S5 rest on reading the code. I did not check the `javadoc-authoring` rules, which are not in the skills folder.
