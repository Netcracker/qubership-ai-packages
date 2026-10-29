# Final review: `6e453aa..HEAD` (SSL response timeout)

The task statement was taken from the PR description you gave me. I loaded `test-authoring` and `english-developer-style`. The repository has no `javadoc-authoring` skill, so comments were checked against the code only. This is the first round of review, so there is no earlier report to compare against.

**Bottom line:** in the default configuration the change does not fix the hang. Fixing that and adding a test with a silent server is the main request.

## Item 1: comments consistent with the code and with each other

Drift script output:
- `PGProperty @25` is tagged code-changed, comment-unchanged. This comes from inserting a constant into the enum, and the enum comment is still true.
- `PGProperty.getName()` (comment-changed) and `BaseDataSource.setConnectTimeout(int)` (code-changed) are parse artifacts. Neither member's text changed.
- `enableSSL` is tagged code-changed, no-comment.
- The two new data-source accessors are tagged comment-added.

Findings:
- **`PGProperty.java:675-678`, the comment on `SSL_RESPONSE_TIMEOUT`.**
  - The first sentence runs two clauses together: "…due to a failover without a timeout here, the client can wait forever." A reader can take "without a timeout" as describing the failover. It needs a full stop after "failover".
  - The comment explains why the setting exists but not what it is. It gives no unit (milliseconds, unlike the seconds used by `socketTimeout` and `connectTimeout`) and no default. It does not say that the smaller of this value and `socketTimeout` applies, and it does not say what 0 does.
  - "This timeout will be set before the request and reset after" is not true of the code in the default configuration (see Item 2).
- **`docs/documentation/head/connect.md:330`.** The entry omits the default of 5000 and the rule that the smaller of this value and `socketTimeout` applies. It also does not say what 0 means. A user comparing it with `socketTimeout` (seconds) will set the wrong order of magnitude.
- **`ConnectionFactoryImpl.java:539-541`.** "if the current timeout is less than sslTimeout then use the smaller timeout" leaves out the `currentTimeout > 0` guard: 0 means no timeout, so it is not "less". The comment also talks about the change itself ("We could do something tricky here…").
- **`BaseDataSource.java:357-372`.** The new accessor comments have an empty first line before the block tags, and "SSL ResponseTimeout" is a garbled name. Their siblings (`getConnectTimeout`) put the tags on the first line. Taste.

## Item 2: claimed cases covered

| Claimed case (source) | Test |
|---|---|
| A server that never answers the SSLRequest no longer hangs the client (PR description) | **none** |
| The timeout is set temporarily and restored after the response (PR description, `PGProperty` comment) | **none** |
| `sslResponseTimeout` is configurable, default 5000 ms (commit 27deb41) | Getter and setter only, through the generic `PGPropertyTest.testDataSourceProperties` and `testGetSetAllProperties`. The default and its effect on a connection are untested. |
| The smaller of `socketTimeout` and `sslResponseTimeout` is used (commit 574b763) | **none** |
| Property order (commit 7f63448) | `PGPropertyTest.testSortOrder` (an existing test) |

**Substantive: the main claimed case is false in the default configuration.**
- `enableSSL` calls `pgStream.getSocket().setSoTimeout(...)` directly instead of `PGStream.setNetworkTimeout` (`PGStream.java:743-746`). `setNetworkTimeout` also calls `pgInput.setTimeoutRequested(milliseconds != 0)`.
- With the default `socketTimeout=0`, `timeoutRequested` stays false. In that state `VisibleBufferedInputStream.readMore` (`:165-177`) swallows the `SocketTimeoutException` and returns true with 0 bytes read.
- `ensureBytes` (`:126-133`) then loops back into `read`. So `receiveChar()` at `ConnectionFactoryImpl.java:553` retries every 5 s forever, which is the hang the PR sets out to remove.
- When `socketTimeout > 0`, the read was already bounded before this change. The only effect then is to shorten it to 5 s when `socketTimeout > 5`.
- The request: use `pgStream.getNetworkTimeout()` and `pgStream.setNetworkTimeout(...)` for both setting and restoring the timeout, and add the test described in Item 3a. That test would have failed against this code.

## Item 3: boundaries, partitions, and the negative control

None of these are tested:
- **`sslResponseTimeout=0`.** `setSoTimeout(0)` means wait forever. Because the guard is `currentTimeout < sslTimeout`, 0 also overrides a positive `socketTimeout`. So setting 0 removes the protection the user configured through `socketTimeout`, and the docs don't say what 0 does.
- **Negative value.** `Socket.setSoTimeout` throws `IllegalArgumentException`. That exception is unchecked, so it escapes the `IOException` and `SQLException` handlers in `openConnectionImpl` and skips the move to the next host. It should be validated, or caught as an invalid parameter, and tested.
- **`socketTimeout` both below and above `sslResponseTimeout`** (the rule that the smaller applies): no test either way.
- **Negative controls:**
  - With `sslmode=disable` or `allow`, nothing changes.
  - A server that answers 'S' or 'N' quickly still connects.
  - With `socketTimeout=0`, the stream's timeout is back to 0 after the SSL response, so later reads are not cut off at 5 s. There is no test for this, and the bypass described in Item 2 means the restore also leaves `timeoutRequested` out of step with the socket.
- **Settings already in use:** none apply. The property is new, so no earlier configuration carries it.

## Item 3a: level, placement, and the environment

The behavior can be observed in one process without a PostgreSQL server. `LoginTimeoutTest` (`pgjdbc/src/test/java/org/postgresql/test/jdbc2/LoginTimeoutTest.java:97-138`) already has a helper that runs a `ServerSocket` which accepts connections and never replies. The requested test sits beside it and reuses that helper:
- Connect with `sslmode=require`, `sslResponseTimeout=200`, `socketTimeout=0`.
- Assert that the connection fails within a bound well below `loginTimeout`.
- Add the control cases listed in Item 3.

The change adds no test at all, so this is **substantive**.

## Item 4: names by content, not by position

None. The checked names are `SSL_RESPONSE_TIMEOUT`, `sslResponseTimeout`, `sslTimeout` and `currentTimeout`, plus the comments. None of them refers to anything by position or ordinal.

## Item 5: the failure report

None. The change adds no assertions. The generic `PGPropertyTest` assertions that now cover the property already print the property name.

## Item 6: what the writer says it verified

Neither the PR description nor the commits give any evidence: no failing run on the base commit, no reproduction of the hang, no mutation result.

## Item 7: siblings of the change

- **`enableGSSEncrypted`** (`ConnectionFactoryImpl.java:465-470`) sends GSSENCRequest and calls `receiveChar()` with the same unbounded wait. The same defect applies when `gssEncMode` is `prefer` or `require`. The default is `allow`, which never sends the request, so the default path is not affected. This should be fixed in this change or named as follow-up.
- **The TLS handshake after 'S'** (`MakeSSL.convert`, `:571`) runs after the timeout is restored. If the host changes underneath the connection, the client can hang there too. This is out of the literal scope but worth naming as follow-up.
- **Other direct `getSocket().setSoTimeout` callers** also bypass `timeoutRequested`:
  - `V3ReplicationProtocol.java:124-133`, which predates this change.
  - `QueryExecutorImpl.java:778` and its `setSocketTimeout` helper.

  I read only these two. Whether they suffer the same problem was not checked, so they are worth a look.
- **`receiveChar(` call sites:** there are 9, and I read the 3 in `ConnectionFactoryImpl`, because those are the ones reached during connection setup, before `socketTimeout` is applied at line 173.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The timeout bypasses `PGStream.setNetworkTimeout`, so the hang remains when `socketTimeout=0` (the default) | Substantive | `ConnectionFactoryImpl.java:536,545,554` | Use `getNetworkTimeout()` and `setNetworkTimeout()` to set and restore the timeout |
| No test for the hang being fixed, the restore, or the rule that the smaller timeout applies | Substantive | `LoginTimeoutTest.java:97-138` (where the test belongs) | Add an in-process silent-server test beside the existing helper, plus the control cases |
| `sslResponseTimeout=0` disables the configured `socketTimeout` during the SSL request, and this is undocumented | Substantive | `ConnectionFactoryImpl.java:542` | Define what 0 means (fall back to `socketTimeout`, or no timeout), document it, and test it |
| A negative value throws an unchecked `IllegalArgumentException` that skips host failover | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value or turn it into a `PSQLException`, and test it |
| The property comment has a run-on first sentence, no unit, no default, no 0 or smaller-timeout rule, and a "reset after" claim that is untrue | Substantive | `PGProperty.java:675-678` | Rewrite it to state what the property is, in ms, with default 5000, the smaller-timeout rule and the meaning of 0 |
| The docs entry omits the default, the smaller-timeout rule and the meaning of 0, and doesn't flag ms against the seconds used by sibling settings | Substantive | `connect.md:330-332` | Add these facts |
| GSSENCRequest has the same unbounded `receiveChar()` | Substantive | `ConnectionFactoryImpl.java:470` | Fix it in this change or name it as follow-up |
| The code comment omits the `> 0` guard and talks about the change itself | Taste | `ConnectionFactoryImpl.java:539-541` | Say that 0 means no socket timeout, and drop the "something tricky" sentence |
| The accessor comments have an empty first line and the name "SSL ResponseTimeout"; there's a missing space in `set(properties,sslResponseTimeout)`; the README row has trailing spaces | Taste | `BaseDataSource.java:357-372`, `README.md:121` | Match the sibling accessors and trim the row |
| No CHANGELOG entry under Unreleased | Taste | `CHANGELOG.md:6` | Add an entry under Added |

I did not build the project or run the test suite. The `VisibleBufferedInputStream` hang comes from reading the code, not from a run, and I did no prose-style pass beyond sentences that read wrongly.
