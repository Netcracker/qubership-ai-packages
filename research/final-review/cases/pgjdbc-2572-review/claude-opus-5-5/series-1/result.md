# Final review: `6e453aa..HEAD` (sslResponseTimeout)

The main finding is that the timeout never fires with the default settings. With `socketTimeout=0`, the read loop swallows the `SocketTimeoutException` and retries every 5 s, so a server that stops answering the SSL request still hangs the client forever. The change also has no tests at all.

Inputs used: the PR description as the task statement, six commit messages, the diff of five files, and the output of `comment-drift.py`. There was no previous report.

## Item 1: comments consistent with the code and with each other

From the drift output:
- `PGProperty @25` and `PGProperty.getName() @811` are parse artifacts; the only real change is the new constant.
- `BaseDataSource.setConnectTimeout(int) @353` is an artifact too; its body did not change.
- `enableSSL` has `code-changed, no-comment`.

Findings:
- **`PGProperty.java:675-678`, the Javadoc of `SSL_RESPONSE_TIMEOUT`.** The sentence "there are reports of the server not responding due to a failover without a timeout here, the client can wait forever" is a run-on. It reads as if the failover happens "without a timeout". The comment also narrates the history instead of saying what the property does. It does not give the unit (ms), the default (5000), that the smaller of this and `socketTimeout` is used, or what 0 means. "Reset after" is also not true on the timeout path, where the stream is closed instead. Substantive.
- **`ConnectionFactoryImpl.java:539-541`.** The comment says "use the smaller timeout". The code does not do that when `sslResponseTimeout=0`: it sets 0, which means wait forever, even when `socketTimeout` is set (see item 3). The second half, "We could do something tricky here…", tells the reader nothing about the code. Substantive for the first half, taste for the second.
- **`BaseDataSource.java:357-371`.** Both new doc comments start with an empty line, followed by `@return SSL ResponseTimeout` and `@param … ssl response timeout`. The sibling comments start directly with `@return connect timeout`. Taste.
- **Docs disagree on units, and the docs omit the default.**
  - The README row reads `Integer | 5000` with no unit. The rows right above it (`connectTimeout`, `socketTimeout`) are in seconds, so "5000" reads as 5000 seconds.
  - `connect.md:330-332` gives no default.
  - Substantive: a reader can get the unit wrong.

## Item 2: claimed cases covered

Claimed cases:
1. The SSL request no longer hangs when the server does not reply. No test.
2. The timeout is temporary and is restored after the reply ("sets the timeout temporarily"). No test.
3. The smaller of `socketTimeout` and `sslResponseTimeout` is used (commit 574b763). No test.
4. The property is configurable through the URL, `Properties`, and the DataSource (commit 27deb41). This is covered only generically, by `PGPropertyTest.testGetSetAllProperties`, `testDataSourceProperties`, and `testSortOrder`, which go over every property.

Case 1 is not just untested: it does not hold with the default `socketTimeout=0` (item 3).

Commands written by the change: none. Hunks not claimed by any sentence: none. The whitespace fixes are covered by the commits "fix spacing" and "restore spacing".

## Item 3: boundaries, partitions, and the negative control

- **Default configuration, `socketTimeout=0`: the timeout never fires** (`ConnectionFactoryImpl.java:545`).
  - The change calls `pgStream.getSocket().setSoTimeout(...)` directly. It skips `PGStream.setNetworkTimeout`, which also calls `pgInput.setTimeoutRequested(ms != 0)` (`PGStream.java:743-746`).
  - With `timeoutRequested == false`, `VisibleBufferedInputStream.readMore` catches the `SocketTimeoutException` and returns `true` with nothing read (lines 165-177).
  - `ensureBytes` then loops into another blocking read (lines 127-131).
  - So `receiveChar()` wakes every 5 s and blocks again, forever. This is exactly the hang the PR describes.
  - The timeout only works when `socketTimeout > 0`. In that case it only shortens an existing `socketTimeout` larger than 5 s down to 5 s.
  - Substantive. Request: use `pgStream.getNetworkTimeout()`/`setNetworkTimeout()`, and add a test against a peer that accepts the TCP connection but never answers the SSLRequest, with `socketTimeout=0`.
- **Boundary `sslResponseTimeout=0`.**
  - With `socketTimeout=10` (10 000 ms), the condition `currentTimeout < sslTimeout` is false, so `setSoTimeout(0)` runs and the SSL response wait has no limit.
  - The value 0 cancels the user's own `socketTimeout`.
  - Substantive. Request: decide what 0 means (probably "do not override"), write it in the docs, and test it.
- **Invalid partition: a negative value.**
  - `Socket.setSoTimeout(-1)` throws `IllegalArgumentException`.
  - That is neither the `IOException` nor the `SQLException` that `openConnectionImpl` (lines 308-347) handles, so it escapes the per-host fallback.
  - A non-integer value is handled: `getInt` raises `PSQLException` "must be an integer".
  - Substantive. Request: validate the value or treat it like 0, and add a test.
- **Negative control is missing.** There is no test that a server that answers `S`/`N` connects as before, and none that `socketTimeout` is back to its old value after `enableSSL`.
- **Other limits on the same work.**
  - `loginTimeout` (Driver thread, default 0) ends the whole connect. When it is below 5 s it fires first, which is fine.
  - `connectTimeout` covers only `connect()`.
  - `socketTimeout` is handled through the minimum, once the `setNetworkTimeout` issue above is fixed.
  - The TLS handshake after an `S` reply (`MakeSSL.convert`) runs with the timeout already restored. A server that answers `S` and then stalls in the handshake still hangs with `socketTimeout=0`. The PR does not say whether the reported hang is before or after the `S`. Substantive: name this as out of scope, or cover it.
- **Values users already pass.** This is a new key, and nothing else reads it.
- **Fault comparison.**
  - Old code, silent peer: blocks without limit and prints nothing (with `socketTimeout=0`).
  - New code, `socketTimeout=0`: identical (see above).
  - New code, `socketTimeout=s > 5`: fails after 5 s with `PSQLException` "The connection attempt failed." caused by a `SocketTimeoutException`, then moves to the next host if there is one.
  - With `sslmode=prefer` (the default), there is no fallback to a non-SSL connection: the fallback only triggers on an `INVALID_AUTHORIZATION_SPECIFICATION` `SQLException`.
  - The PR has no sentence about either behavior. Folded into the first finding of this item.

## Item 3a: level, placement, and the environment

There is no test at any level. The behavior can be observed in one process: open a `ServerSocket` on loopback that accepts and never writes, then connect with `sslmode=prefer` and assert that the connection fails within a bounded time. No database is needed.

The natural place is beside the existing connection-factory and SSL tests, for example `ConnectTimeoutTest` or the `jdbc4`/`ssl` test packages. Substantive.

## Item 4: names by content, not by position

None. Checked the new identifiers (`SSL_RESPONSE_TIMEOUT`, `sslResponseTimeout`, `sslTimeout`, `currentTimeout`) and the comments; none of them refers to anything by position.

## Item 5: the failure report

None in the change, because it adds no assertions. The existing generic `testSortOrder` uses `assertTrue` with a message that already prints both names.

## Item 6: what the writer says it verified

Neither the commits nor the PR description state a red run on the base commit, a mutation verdict, or any manual reproduction of the hang. test-authoring §1 requires this evidence for a regression fix. Given item 3, a reproduction with `socketTimeout=0` would have shown that the change does not work.

## Item 7: siblings of the change

- **`enableGSSEncrypted`, `ConnectionFactoryImpl.java:462-468`.** It sends `GSSENCRequest` and blocks in `pgStream.receiveChar()` with no timeout. That is the same symptom on the same "upgrade request" handshake, and it applies whenever `gssEncMode` is `prefer` or `require`. Substantive: cover it in this change, or name it as follow-up in the description.
- **Other callers of `getSocket().setSoTimeout`.** There are none in the main code. Every other place goes through `PGStream.setNetworkTimeout`, which is why that is the call to use here.
- **Sets the new property joins.**
  - `PGProperty`: placed in sorted order, enforced by `testSortOrder`.
  - `BaseDataSource` getter and setter: present.
  - README table: present.
  - `connect.md`: present, but the entry lacks the blank line and tab indentation the neighboring entries use (taste).
  - No prose counts the timeout properties.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Timeout never fires with the default `socketTimeout=0`; the read loop retries every 5 s forever | Substantive | `ConnectionFactoryImpl.java:545,554` | Use `pgStream.getNetworkTimeout()`/`setNetworkTimeout()`; add a test with a silent loopback peer and `socketTimeout=0` |
| `sslResponseTimeout=0` disables the limit and overrides a set `socketTimeout` | Substantive | `ConnectionFactoryImpl.java:539-545` | Define 0 (for example "do not override"), document it, and test it |
| A negative value throws `IllegalArgumentException` that escapes per-host handling | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value or clamp it; add a test |
| No tests for the timeout, the restore, the minimum rule, or the negative control | Substantive | change as a whole | In-process tests beside the existing connect-timeout tests |
| No red-run evidence | Substantive | PR description | State the reproduction and the red run on the base commit |
| GSS encryption request has the same unbounded `receiveChar()` | Substantive | `ConnectionFactoryImpl.java:468` | Fix it in this change, or name it as follow-up |
| A hang in the TLS handshake after an `S` reply is not covered and not mentioned | Substantive | `ConnectionFactoryImpl.java:554,580` | Say whether it is out of scope, or bound it too |
| `SSL_RESPONSE_TIMEOUT` Javadoc is a run-on with history narration; it lacks unit, default, min rule, and meaning of 0 | Substantive | `PGProperty.java:675-678` | Rewrite it to state what the property does |
| Comment "use the smaller timeout" is false for 0 | Substantive | `ConnectionFactoryImpl.java:539-541` | Align it with the fixed code; drop the "tricky" sentence |
| README row has no unit next to seconds-based siblings; `connect.md` has no default; README line has trailing whitespace | Substantive (unit), taste (whitespace) | `README.md:121`, `connect.md:330-332` | Write "milliseconds" and the default of 5000 in both places |
| DataSource doc comments start with an empty line; `set(properties,sslResponseTimeout)` has no space after the comma | Taste | `BaseDataSource.java:357-372` | Match the sibling accessors |

I did not build the project or run any tests. I made no edits and no commits, and I did not do a prose-style pass beyond the sentences that read wrongly.
