I reviewed `6e453aa..HEAD` (six commits by Dave Cramer) using the final-review form. The most serious problem is that **the timeout does not work with default settings**: a connection that gets no answer to the SSL request still hangs, which is the exact case the PR exists to fix. No test was added, so nothing caught this.

Inputs I used: the task statement (the PR description), the six commit messages, the full diff, and the output of `comment-drift.py 6e453aa HEAD`. That output tagged `PGProperty` and `BaseDataSource.setConnectTimeout` as code-changed with comments unchanged, `getName` as comment-changed, the two new data-source accessors as comment-added, and `enableSSL` as code-changed with no comment. The diff adds no tests, so there are no test class comments. I loaded `test-authoring` and `english-developer-style`. No doc-comment skill was in the provided set, so I used the javadoc of neighbouring members as the reference.

## Item 1: comments consistent with the code and with each other

- **`PGProperty.java:675-677` (the `SSL_RESPONSE_TIMEOUT` javadoc).** "there are reports of the server not responding due to a failover without a timeout here, the client can wait forever" is a run-on sentence. It reads as "a failover without a timeout", not "without a timeout here, the client waits forever". The comment also leaves out three facts the code has:
  - the unit (milliseconds) and the default (5000);
  - commit 574b763 made the effective value the lesser of this setting and `socketTimeout`;
  - `0` means wait forever.

  Sibling javadoc in the same enum, such as `ADAPTIVE_FETCH`, states its default. (Substantive.)
- **`docs/documentation/head/connect.md:330-332`.** Same omissions: nothing about the cap by `socketTimeout`, the default of 5000, or what 0 means. The neighbouring entries put a blank line before a tab-indented paragraph. This entry uses four spaces and no blank line. (Missing facts: substantive. Formatting: taste.)
- **`README.md:121`.** The row gives no unit. Its neighbours `connectTimeout` and `socketTimeout` are in seconds, so "5000" next to them reads as seconds. The row also ends with about 170 trailing spaces. (Unit: substantive. Trailing spaces: taste.)
- **`ConnectionFactoryImpl.java:538-540`.** "We could do something tricky here to not set it in that case but this is pretty readable" describes the author's choice, not the code. The comment also says the smaller timeout is used, which is false when `sslResponseTimeout=0` (see Item 3). (Taste for the wording; the false claim is part of the Item 3 finding.)
- **`BaseDataSource.java:357-371`.** Each accessor's javadoc opens with an empty line and has no summary sentence. "SSL ResponseTimeout" is spelled differently from the property name. The siblings use `@return connect timeout`. (Taste.)
- `PGProperty.getName()` (tagged comment-changed) and `BaseDataSource.setConnectTimeout` (tagged code-changed): I checked both and neither comment is affected. The tags come from the parser misplacing the members next to the inserted text.

## Item 2: claimed cases covered

The task statement and commit messages claim these cases. None has a test.

| Claimed case | Test |
|---|---|
| A server that doesn't answer the SSL request no longer hangs the client (PR description) | none |
| The timeout is configurable through `sslResponseTimeout` (27deb41) | `PGPropertyTest.testGetSetAllProperties` and `testDataSourceProperties` cover the getter, setter and default generically; nothing covers the effect |
| The lesser of the current socket timeout and `sslResponseTimeout` is used (574b763) | none |
| The timeout is set "temporarily", i.e. the original timeout is restored after the read (PR description) | none |
| Sort order of the new constant (7f63448) | `PGPropertyTest.testSortOrder` (existing) |

**The headline case is in fact broken at the defaults.** `enableSSL` calls `pgStream.getSocket().setSoTimeout(sslTimeout)` directly (`ConnectionFactoryImpl.java:545`). That skips `PGStream.setNetworkTimeout` (`PGStream.java:743-746`), which is what sets `pgInput.setTimeoutRequested(true)`.

- With the default `socketTimeout=0`, `timeoutRequested` stays false.
- When the read times out, `VisibleBufferedInputStream.readMore` (`:165-171`) catches the `SocketTimeoutException` and, because `timeoutRequested` is false, does not rethrow it. It returns true having read 0 bytes.
- `ensureBytes` (`:126-133`) then loops and blocks for another 5 s, and keeps doing so.

So with default settings, a server that never answers the SSL request still hangs the client indefinitely; the only change is that the socket now wakes every 5 s. The timeout only takes effect when `socketTimeout > 0`, and then that existing setting would already have stopped the hang. (Substantive.)

The fix is to call `pgStream.setNetworkTimeout(sslTimeout)` before the read and `pgStream.setNetworkTimeout(currentTimeout)` after it. I checked by reading the code, not by running it.

## Item 3: boundaries, partitions, and the negative control

- **`sslResponseTimeout=0` while `socketTimeout>0`** (`ConnectionFactoryImpl.java:541-545`). The check `currentTimeout < sslTimeout` is false when `sslTimeout` is 0, so `setSoTimeout(0)` runs. That turns off the user's `socketTimeout` for the SSL read, and on the base commit that read was bounded by `socketTimeout`. This is a regression, and no case covers it. (Substantive.)
- **Negative `sslResponseTimeout`.** `Socket.setSoTimeout` throws `IllegalArgumentException`. None of the catch blocks in `openConnectionImpl` handles it (they catch `SQLException`, `ConnectException`, `IOException`), so the caller gets an unchecked exception instead of a `PSQLException`. Nothing validates the value and no case covers it. (Substantive.)
- **Boundary partitions with no case:** `sslResponseTimeout` below, equal to, and above `socketTimeout*1000`; `socketTimeout` unset (the default, and the broken one). The negative control is also missing: `sslmode=disable` or `allow` never sends the request, and a server that answers within the timeout should connect normally. (Substantive.)
- **Other limits on the same work (connection establishment):**
  - **`loginTimeout`**, read in `Driver.java:704-714` (seconds, default 0, otherwise `DriverManager.getLoginTimeout()`). It bounds the whole connect from the same start. If it is set below 5 s, `loginTimeout` fires before the SSL timeout. That is acceptable, but neither the docs nor a test states which one the user sees.
  - At the defaults (`loginTimeout=0`), the new limit is the only one, and per Item 2 it doesn't fire.
  - **`socketTimeout`**: the code handles this one with the minimum, except for the 0 case above.
  - **`connectTimeout`** bounds only the TCP connect, a separate operation, so it doesn't count here.

  The request is a case with `sslResponseTimeout` just past `loginTimeout*1000` that asserts which limit fires, and a statement in the docs. (Substantive.)
- **Behaviour change at the defaults** (taste: the reporter's call). The default `sslmode=prefer` sends the SSL request, so the new 5000 ms default applies to every connection. Once the Item 2 fix lands, a server that takes more than 5 s to answer (a cold-starting serverless instance, a host under heavy load) will fail to connect where it used to succeed. The PR description should state that tradeoff, or the default should be reconsidered.

## Item 3a: level, placement, and the environment

There is no test at any level. The behaviour can be observed on the local machine without a PostgreSQL server. `LoginTimeoutTest.TimeoutHelper` (`LoginTimeoutTest.java:88-131`) already provides a `ServerSocket` that accepts a connection and never answers.

The request is a test beside `LoginTimeoutTest.testTimeoutOccurs`, sharing that helper. It should use `sslmode=require`, leave `socketTimeout` unset, set `sslResponseTimeout` to a few hundred ms and `loginTimeout` to a much larger value. It should assert that the connection fails with a `SocketTimeoutException` in the cause chain, well before `loginTimeout`. On HEAD that test would fail, which is the Item 2 defect. Companion cases: `socketTimeout` smaller than `sslResponseTimeout`; `sslResponseTimeout=0` with `socketTimeout` set. (Substantive.)

Note that the existing `testTimeoutOccurs` passes on both base and HEAD because `loginTimeout=5` ends the attempt, so it says nothing about this change.

## Item 4: names by content, not by position

None. No test names or case ids were added, and no comment refers to anything by position.

## Item 5: the failure report

None, because there are no new assertions. The test requested under Item 3a should assert the elapsed bound and the exception type with messages that print the measured values, not a bare `assertTrue`. The existing `testTimeoutOccurs` assertion has exactly that weakness, so it shouldn't be copied.

## Item 6: what the writer says it verified

Neither the PR description nor the commits show a red run on the base commit or a mutation verdict. No evidence is given that any test can fail. (Substantive.)

## Item 7: siblings of the change

- **`enableGSSEncrypted`** (`ConnectionFactoryImpl.java:463-469`) has the same pattern: it sends the GSSENC request and calls `pgStream.receiveChar()` with no timeout, reached with `gssEncMode=prefer|require`. The same hang applies. Fix it in this change or name it as follow-up. (Substantive.)
- **`MakeSSL.convert`** (the `'S'` branch, `ConnectionFactoryImpl.java:584`) runs the TLS handshake after the timeout has been restored, so a host that answers 'S' and then stops responding still hangs. The PR's own scenario, a host swapped underneath the connection, can occur at that point. Name it as follow-up or cover it. (Substantive.)
- **`V3ReplicationProtocol.java:133`** also calls `getSocket().setSoTimeout` directly. It predates this change and isn't on this path; I didn't examine it further.
- `git grep` finds no other reader of `SSL_RESPONSE_TIMEOUT`.
- **`CHANGELOG.md`** has an `[Unreleased] / Added` section, and this new public connection property has no entry there. (Substantive.)

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Timeout set on the raw socket, so `timeoutRequested` stays false; at default `socketTimeout=0` the timeout is swallowed and the read keeps blocking | Substantive | `ConnectionFactoryImpl.java:545,554` | Use `pgStream.setNetworkTimeout(...)` for both the set and the restore |
| `sslResponseTimeout=0` turns off an active `socketTimeout` during the SSL read | Substantive | `ConnectionFactoryImpl.java:541-545` | Treat 0 as "no extra limit" (keep `currentTimeout`) and document it |
| Negative value escapes as `IllegalArgumentException` | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value, or map it to a `PSQLException` |
| No test of the timeout, the minimum, the restore, or the controls | Substantive | (none) | Local-socket tests beside `LoginTimeoutTest.testTimeoutOccurs`, as described in Item 3a |
| Relation to `loginTimeout` neither tested nor documented | Substantive | `Driver.java:704`; docs | Add a case just past `loginTimeout`, and a sentence in the docs |
| No red run or mutation evidence | Substantive | PR | Show the new test failing on the base commit |
| GSSENC request read has the same unbounded wait | Substantive | `ConnectionFactoryImpl.java:463-469` | Fix here or name as follow-up |
| TLS handshake after 'S' is still unbounded | Substantive | `ConnectionFactoryImpl.java:584` | Name as follow-up or cover it |
| Javadoc run-on sentence; missing unit, default, minimum with `socketTimeout`, meaning of 0 | Substantive | `PGProperty.java:675-677` | Rewrite with those facts |
| `connect.md` entry missing default, cap, and 0 semantics | Substantive | `connect.md:330-332` | Add them |
| README row has no unit beside rows in seconds | Substantive | `README.md:121` | Say "milliseconds"; strip the trailing spaces |
| No CHANGELOG entry | Substantive | `CHANGELOG.md` | Add under `[Unreleased] / Added` |
| New 5 s default changes behaviour for every `sslmode=prefer` connection | Taste | `PGProperty.java:681` | State the tradeoff in the PR, or reconsider the default |
| Inline comment describes the author's choice, not the code | Taste | `ConnectionFactoryImpl.java:538-540` | State the rule ("use the smaller non-zero timeout") |
| Accessor javadoc has no summary sentence; "SSL ResponseTimeout" | Taste | `BaseDataSource.java:357-371` | Match the `connectTimeout` siblings |
| `connect.md` entry indented with spaces and no blank line, unlike its neighbours | Taste | `connect.md:330` | Match the neighbouring entries |

What this review did not check: I did not build the project or run any tests. The timeout-swallowing defect comes from reading `VisibleBufferedInputStream` and was not observed in a run. I did not do a style-only pass over the prose.
