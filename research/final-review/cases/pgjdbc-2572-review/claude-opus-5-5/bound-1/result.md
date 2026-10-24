I found **4 substantive problems and 2 matters of taste**. The most serious is that with default settings the change does nothing: the client still hangs forever. I ran the drift script, read the full diff, and loaded `test-authoring` and `english-developer-style`; I changed no files.

No previous report of this form exists, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other

Drift script output: `PGProperty` code-changed/comment-unchanged (the enum's class comment, still true); `PGProperty.getName()` comment-changed (a mis-parse: it is the new `SSL_RESPONSE_TIMEOUT` comment); `ConnectionFactoryImpl.enableSSL` code-changed, no-comment; `BaseDataSource.get/setSslResponseTimeout` comment-added; `BaseDataSource.setConnectTimeout(int)` code-changed/comment-unchanged (a mis-parse, the method is unchanged).

- **`PGProperty.java:675-678`**: the comment on `SSL_RESPONSE_TIMEOUT` is one run-on sentence: "…not responding due to a failover without a timeout here, the client can wait forever". A reader can take "without a timeout here" as part of the failover. It also says "set before the request and reset after", but leaves out the rule the code applies (`ConnectionFactoryImpl.java:539-543`): the smaller of `sslResponseTimeout` and the current socket timeout is used. It doesn't give the unit or what `0` means.
- **`README.md:121` and `connect.md:330-332`**: neither page says that `socketTimeout` caps this value when it is set. Neither says that `0` means "wait forever, ignoring `socketTimeout`", which is what the code does (see item 3). The README row says "Socket timeout" with no unit, while the row two lines above (`socketTimeout`) is in seconds. A reader could set `sslResponseTimeout=5` thinking it means 5 seconds; it means 5 ms.
- **`BaseDataSource.java:357-372`**: both doc comments start with an empty first sentence (a bare `@return` / `@param`). "SSL ResponseTimeout" is mis-spaced. They match their thinner neighbors, so this is taste.
- No comment narrates the change ("now", "no longer").

## Item 2: claimed cases covered

What the description and commits claim:

| Claimed case | Test |
| --- | --- |
| (a) A timeout bounds the wait for the reply to the SSL request when the server never answers | none |
| (b) The timeout is configurable as `sslResponseTimeout`, default 5000 | only the generic `PGPropertyTest.testGetSetAllProperties` and `testDataSourceProperties`, which check registration, not behavior |
| (c) The smaller of the current socket timeout and `sslResponseTimeout` is used | none |
| (d) The original timeout is restored after the reply | none |
| (e) Sort order fixed | `PGPropertyTest.testSortOrder` |

Hunks: every hunk is claimed by one of the commit subjects. No command lines are added.

**Case (a) is not met in the default configuration (substantive).** The code at `ConnectionFactoryImpl.java:545` calls `pgStream.getSocket().setSoTimeout(sslTimeout)` directly instead of `pgStream.setNetworkTimeout(...)`, which is what `PGStream.java:743-746` and `QueryExecutorImpl.setSocketTimeout` use. `setNetworkTimeout` also sets `VisibleBufferedInputStream.timeoutRequested`. When `socketTimeout=0` (the default), that flag is `false`. In that case `readMore` (`VisibleBufferedInputStream.java:165-172`) swallows the `SocketTimeoutException` and returns `true` with nothing read, and `ensureBytes` loops.

So with default settings, `receiveChar()` wakes every 5 s, swallows the timeout and blocks again, forever. That is the hang the change set out to fix. The timeout only fires when `socketTimeout` is set, and the existing code already bounded the read in that case. The new value only changes behavior when `socketTimeout` is longer than 5 s.

## Item 3: boundaries, partitions, and the negative control

No test varies any input. Partitions with no case:

| Partition | What the code does | Status |
| --- | --- | --- |
| `socketTimeout=0` (default) | hangs forever (item 2) | untested |
| `socketTimeout` < `sslResponseTimeout` | uses `socketTimeout` | untested |
| `socketTimeout` > `sslResponseTimeout` | the only case where the change has an effect | untested |
| `sslResponseTimeout=0` with `socketTimeout>0` | sets `SO_TIMEOUT=0`, wait unbounded | **regression from base**: the guard `currentTimeout < sslTimeout` is false when `sslTimeout` is 0; on the base commit `socketTimeout` bounded this read |
| Negative value | `setSoTimeout` throws `IllegalArgumentException` (unchecked); it passes through `tryConnect`'s rethrow uncaught by the host loop, which catches only `ConnectException`, `IOException` and `SQLException` | not validated or documented |
| Server replies quickly (`S`/`N`/`E`) | timeout restored afterwards | no control test |
| `sslmode=disable` / `allow` | returns before the change runs | correctly skipped; no control test |

**Restore on failure:** when `receiveChar` throws, the restore at `:554` is skipped. That is harmless, because the stream is closed by the `catch` in `tryConnect`.

**Old versus new failure, on the reported fault (the server accepts the connection and never answers the SSL request):**
- Old: blocks forever when `socketTimeout=0`; otherwise fails after `socketTimeout` with "The connection attempt failed." (or moves on to the next host).
- New: unchanged when `socketTimeout=0`. When `socketTimeout` is more than 5 s, it fails after 5 s with the same message and an `IOException` cause, then tries the next host. This part is an improvement.

**Other limits on the same work:**
- `socketTimeout` (`tryConnect`, seconds × 1000) bounds the same read. Raising `sslResponseTimeout` past it has no effect, by design (the smaller-of rule), but the docs don't say so (item 1).
- `loginTimeout` (in `Driver`) encloses the whole connection attempt. With a value under 5 s it fires first; that is fine for an enclosing limit.
- `connectTimeout` bounds only the TCP connect, so it doesn't count.
- The TLS handshake that follows (`MakeSSL.convert` → `startHandshake`) runs with the original timeout (`0` by default), so a host swap at that point still hangs (see item 7).

## Item 3a: level, placement, and the environment

There is no test at any level. The behavior can be observed without a PostgreSQL server: open a local `ServerSocket` that accepts the connection, reads the 8-byte SSL request and never replies. Then connect with `sslmode=require`, `sslResponseTimeout=500` and default `socketTimeout`, and assert that the connection fails with a `SocketTimeoutException` cause within a generous bound. That test is red on HEAD, which also confirms item 2.

The controls, in the same file:
- `socketTimeout=1` with `sslResponseTimeout=60000` (the smaller-of rule)
- `sslResponseTimeout=0` with `socketTimeout=1` (bounded, as on the base commit)

The test belongs beside the existing connection-factory tests rather than in `PGPropertyTest`.

## Item 4: names by content, not by position

None. I checked the new property name, getter and setter names, comments, and doc rows; none refers to anything by position.

## Item 5: the failure report

None. The change adds no assertions.

## Item 6: what the writer says it verified

There is no red run on the base commit, no mutation verdict, and no statement of any run against a hanging peer.

## Item 7: siblings of the change

- **`enableGSSEncrypted` (`ConnectionFactoryImpl.java:462-468`)**: the GSSENC request has the same send-then-`receiveChar()` pattern with no timeout. It runs before `enableSSL` when `gssEncMode` is `prefer` or `require`. The same host-swap hang applies. Fix it in this change or name it as follow-up in the description.
- **`MakeSSL.convert` → `startHandshake()`**: this runs right after the reply with the timeout restored to `currentTimeout`. The same hang can happen during the handshake. Name it as follow-up, or keep the bounded timeout through the handshake.
- **`pgStream.getSocket().getSoTimeout()`**: the other call sites are `PGStream.java:124`, which copies the value, and `QueryExecutorImpl.java:778`, which reads it but sets the timeout through `setNetworkTimeout`. That second site shows the idiom this change should follow.
- **Lists of properties**: `README.md`, `connect.md` and `PGProperty` all have the new member. `CHANGELOG.md` `[Unreleased]` has no entry for the new property (taste).

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | Timeout set on the raw socket bypasses `timeoutRequested`; with the default `socketTimeout=0` the timeout is swallowed and the client still hangs forever | Substantive | `ConnectionFactoryImpl.java:545,554` | Use `pgStream.setNetworkTimeout(sslTimeout)` and restore with `pgStream.setNetworkTimeout(currentTimeout)` |
| 2 | `sslResponseTimeout=0` with `socketTimeout>0` makes the wait unbounded, where the base commit bounded it; negative values throw an unchecked `IllegalArgumentException` | Substantive | `ConnectionFactoryImpl.java:539-545` | Treat `0` as "use `socketTimeout`" (or document it), and reject or ignore negative values |
| 3 | No test of any claimed case: a hanging peer, the smaller-of rule, the restore, or the controls | Substantive | none | Add the local-`ServerSocket` test and controls from item 3a; state the red run on HEAD and the base commit |
| 4 | Docs and Javadoc omit the smaller-of rule and what `0` means; the README gives no unit next to a seconds-based neighbor; the Javadoc's run-on sentence misreads | Substantive | `PGProperty.java:675-678`, `README.md:121`, `connect.md:330-332` | State the unit (ms), that `socketTimeout` caps it, and what `0` does; split the sentence |
| 5 | The GSSENC request and the TLS handshake have the same unbounded wait | Substantive | `ConnectionFactoryImpl.java:462-468`, `MakeSSL.java:41` | Fix in this change, or name as follow-up in the description |
| 6 | Empty first sentence in the getter/setter Javadoc, "SSL ResponseTimeout"; trailing whitespace on the README row; the `connect.md` entry is indented with spaces and has no blank line after `= int`, unlike its tab-indented neighbors | Taste | `BaseDataSource.java:357-372`, `README.md:121`, `connect.md:330` | Match the neighboring entries |

I did not build the project, run its test suite, or reproduce finding 1 on a live socket. That finding comes from reading the code: `VisibleBufferedInputStream.readMore` swallows the timeout and `ensureBytes` loops. I also did not do a style pass over the prose beyond sentences that read wrongly.
