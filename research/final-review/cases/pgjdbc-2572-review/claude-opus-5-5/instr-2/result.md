# Final review: `6e453aa..HEAD`, the SSL upgrade response timeout

The change has no test of its own, and two of its inputs behave wrongly:

- **Setting `sslResponseTimeout=0` removes the `socketTimeout` bound.** The SSL reply wait then has no limit at all, which brings back the hang the PR is meant to fix.
- **A negative value escapes as an unchecked exception.** It is not reported as a connection failure.

The same unbounded wait also exists on the GSS encryption request and in the TLS handshake that follows. The new code and docs also leave out how the setting interacts with `socketTimeout` and what `0` means.

Inputs: I read the diff whole, used the quoted PR description as the task statement, read the six commit messages (subjects only, no bodies), and ran `comment-drift.py 6e453aa HEAD`. There was no previous report. I loaded `test-authoring` and `english-developer-style` from the given directory. The doc-comment skill for Java (`javadoc-authoring`) is not in that directory, so I did not load it and none of its rules are cited.

## Item 1: comments consistent with the code and with each other

What the drift script reported:
- **`PGProperty` @25 (code changed, comment unchanged).** The enum's class comment is still true.
- **`PGProperty.getName()` @811 (comment changed) and `BaseDataSource.setConnectTimeout(int)` @353 (code changed).** The diff touches neither member, so these are parse errors caused by the line shift.
- **`enableSSL` @522.** It has no doc comment. Its new inline comment is covered below.

Findings:
- **The `SSL_RESPONSE_TIMEOUT` doc comment reads wrongly** (`PGProperty.java:675-676`). "…not responding due to a failover without a timeout here, the client can wait forever" is a run-on sentence. A reader parses it as "a failover without a timeout". It also does not say what the property is: there is no unit, no default, no cap at `socketTimeout`, and no meaning for `0`. "Reset after" is only true when `receiveChar` returns; when it throws, the stream is closed instead. That is harmless, but the sentence promises more than the code does. **Substantive.**
- **The inline comment at `ConnectionFactoryImpl.java:538-540` is accurate about the minimum rule.** The clause "We could do something tricky…" carries no information (`english-developer-style`). **Taste.**
- **The user-facing docs are silent on two facts the code decides** (`connect.md:330-332` and `README.md:121`):
  - The value is capped by `socketTimeout` when that is smaller.
  - `0` does not mean "disabled" the way it does for the neighbouring `socketTimeout` and `connectTimeout` entries. In this code `0` means wait forever and override `socketTimeout`.

  These docs also give the timeout in milliseconds, while every neighbouring timeout is in seconds. That difference is stated, but a reader skimming the table will assume seconds. **Substantive** for the missing cap and the meaning of `0`; the unit choice itself is **taste**.
- **The `BaseDataSource` getter and setter Javadoc start with an empty line** (`BaseDataSource.java:357-370`). Their sibling `getConnectTimeout` does not. "SSL ResponseTimeout" is mis-cased. **Taste.**
- No comment narrates the change (no "now", "no longer" or "used to").

## Item 2: claimed cases covered

Claimed cases:

| Claimed case | Test |
| --- | --- |
| A server that does not answer the SSLRequest makes the connection fail within the timeout instead of hanging (task statement) | **none** |
| The timeout is set only temporarily and then restored, so `socketTimeout` holds after the upgrade (task statement: "sets the timeout temporarily") | **none** |
| The lesser of the current socket timeout and `sslResponseTimeout` is used (commit 574b763) | **none** |
| `sslResponseTimeout` is a configurable property with a data-source getter and setter (commit 27deb41) | Existing `PGPropertyTest.testDataSourceProperties`, `testGetSetAllProperties` and `testEnumConstantNaming` pick up the new constant |
| Sort order of the property (commit 7f63448) | Existing `PGPropertyTest.testSortOrder` |

The change tells no one to run a command, so there are no commands to check.

Every hunk belongs to a claim. The code and `PGProperty` hunks belong to the task statement and to 27deb41. The README, `connect.md` and `BaseDataSource` hunks belong to 27deb41 and 574b763. The spacing commits only touch these same hunks.

**Substantive:** none of the behaviour claims has a test.

## Item 3: boundaries, partitions, and the negative control

**Partitions of `sslResponseTimeout` (`ConnectionFactoryImpl.java:535-545`):**
- **`0`:** Suppose `socketTimeout=30`, so `currentTimeout` is 30000. The condition `currentTimeout < 0` is false, so `setSoTimeout(0)` runs, and the SSL reply wait is unbounded even though the user set `socketTimeout`. On the base commit, `socketTimeout` bounded this read. **Substantive.** Either treat `<= 0` as "keep the current timeout", or reject it.
- **Negative:** `Socket.setSoTimeout(-1)` throws `IllegalArgumentException`. In `openConnectionImpl` the handlers at `:308`, `:322` and `:333` catch only `ConnectException`, `IOException` and `SQLException`. The exception therefore escapes `connect` unwrapped, and the next host is not tried. **Substantive.**
- **Equal to, or just above, `socketTimeout` in milliseconds:** there is no test.

**Negative control:** there is none.
- With `sslmode=disable` or `allow`, `enableSSL` returns before the new code. A test with those modes should stay green.
- Default `sslmode` is `prefer`, so the 5 s default reaches every connection that does not set `sslmode`. A server that used to answer in more than 5 s now fails. The PR description does not mention this. **Substantive:** state it in the description, or add a test that pins the default.

**Replaced mechanism (an unbounded read becomes a bounded one), on a silent server:**
- **Old:** waits forever, unless `socketTimeout` or `loginTimeout` is set.
- **New:** about 5 s. The `SocketTimeoutException` is an `IOException`, so it is reported as "The connection attempt failed." with the cause attached, and the next host is tried.

So the new mechanism fails earlier and prints a cause. Note that because it is not a `SQLException`, the `prefer` fallback to non-SSL at `:237` is not tried. That is probably intended, but no sentence states it. **Taste.**

**Other limits on the same work:**
- **`socketTimeout`** (seconds, set at `:112-115`). It caps `sslResponseTimeout` by design. Raising `sslResponseTimeout` past it has no effect, which is undocumented (see Item 1).
- **`loginTimeout`** (seconds, encloses the whole connect). If it is below 5 s it fires first. Since it bounds the whole connect, that is expected.
- **`connectTimeout`** bounds only the TCP connect, which happens before this work, so it does not count here.
- **`MakeSSL.convert`, called after `'S'`,** runs the TLS handshake with the restored `currentTimeout`, which may be `0`. If the failover happens in the handshake instead, the hang is still unbounded. This is filed under Item 7.

**Pre-existing state:** the property is new, so there are no stored values to meet.

## Item 3a: level, placement, and the environment

There is no test at any level. The behaviour can be observed without a PostgreSQL server: a local `ServerSocket` that accepts the connection and never replies to the SSLRequest is enough.

**Request (substantive):** a test beside the existing connect tests that opens a connection to such a socket with `sslmode=require` and a short `sslResponseTimeout`. It should assert:
- the connection fails with a `SocketTimeoutException` cause,
- it fails within a bound,
- `socketTimeout` holds again after the upgrade when the socket does reply.

The property-registration cases sit correctly in `PGPropertyTest`.

## Item 4: names by content, not by position

None. I checked the new property name, the accessors, and the comment and doc text; none refers to anything by position or ordinal.

## Item 5: the failure report

None. The change adds no assertions. The existing `PGPropertyTest` assertions that now cover the property already carry messages naming the property.

## Item 6: what the writer says it verified

No evidence is stated. The commits and the PR description carry neither a red run on the base commit nor a mutation verdict, and no run against a silent server.

## Item 7: siblings of the change

Other places that do the same unbounded read during the connection setup:
- **`enableGSSEncrypted`** (`ConnectionFactoryImpl.java:463-469`). It sends `GSSENCRequest` and then calls `pgStream.receiveChar()` with no temporary timeout. A failover hang applies here identically when `gssEncMode` is `prefer` or `require`. **Substantive:** fix it in this change, or name it as a follow-up in the description.
- **The TLS handshake in `MakeSSL.convert`** (reached at `:572`). It runs with the restored timeout, which may be `0`. The same failover can hang there. **Substantive:** cover it, or name it as a follow-up.
- **The new code calls `pgStream.getSocket().getSoTimeout()` and `setSoTimeout(...)` directly.** `PGStream` already has `getNetworkTimeout()` and `setNetworkTimeout(int)` (`PGStream.java:200-210`, `:744`), which `hasMessagePending` uses for the same save-and-restore pattern. **Taste.**

New member of a set: `sslResponseTimeout` is listed in all three places the other properties are listed (`PGProperty`, the README table, and `connect.md`), next to `socketTimeout`. I found no prose that counts the timeout properties.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `sslResponseTimeout=0` overrides a set `socketTimeout` and makes the SSL reply wait unbounded | Substantive | `ConnectionFactoryImpl.java:535-545` | Treat `<= 0` as "keep the current timeout" (or reject it), document it, and test it |
| A negative value throws `IllegalArgumentException` out of `connect`, unwrapped, without trying the next host | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value, or map it to a `PSQLException` |
| No test of the timeout firing, of the timeout being restored afterwards, or of the cap at `socketTimeout` | Substantive | `ConnectionFactoryImpl.java:535-554` | Local silent `ServerSocket` test with `sslmode=require`, plus `sslmode=disable` as the control |
| The 5 s default now applies to every connection that does not set `sslmode` (default `prefer`); unstated | Substantive | `PGProperty.java:681` | One sentence in the description accepting it, or a different default |
| The docs omit the cap at `socketTimeout` and the meaning of `0` | Substantive | `connect.md:330-332`, `README.md:121` | State both, as the neighbouring timeout entries do |
| Run-on doc comment that reads as "a failover without a timeout"; no unit, default, or cap | Substantive | `PGProperty.java:675-676` | Rewrite to state what the property sets and its unit, default, and cap |
| `GSSENCRequest` response read has the same unbounded wait | Substantive | `ConnectionFactoryImpl.java:469` | Apply the same timeout, or name it as a follow-up in the description |
| The TLS handshake after `'S'` can still hang with `socketTimeout=0` | Substantive | `ConnectionFactoryImpl.java:572` | Cover it, or name it as a follow-up |
| No red-run or mutation evidence stated | Substantive | (PR description) | Show a run against a silent server on the base commit and on HEAD |
| Bypasses `PGStream.get/setNetworkTimeout` | Taste | `ConnectionFactoryImpl.java:536,545,554` | Use the `PGStream` methods |
| Milliseconds while the neighbouring timeouts use seconds; the inline "something tricky" clause; empty first Javadoc line and "SSL ResponseTimeout" casing; missing space in `set(properties,sslResponseTimeout)` | Taste | `PGProperty.java:681`, `ConnectionFactoryImpl.java:538-540`, `BaseDataSource.java:357-372` | As noted |

I did not build the project or run the test suite. `javadoc-authoring` was not available, so its rules were not applied, and I did not do a style-only pass over the prose.
