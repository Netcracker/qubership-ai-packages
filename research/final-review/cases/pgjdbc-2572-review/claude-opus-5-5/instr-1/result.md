# Final review: `6e453aa..HEAD` (sslResponseTimeout)

**How the review was run.** I loaded `test-authoring` and `english-developer-style` from the given directory. The Java doc-comment skill (`javadoc-authoring`) is not in that directory, so I judged doc comments against the developer-style §7 "Javadoc" module and the sibling comments in the same files. There is no previous report for this change. I ran the drift script, and its output is used under item 1.

## Item 1: comments consistent with the code and with each other

Drift script output:
- `PGProperty @25 code-changed, comment-unchanged`: the enum comment ("All connection parameters…") is still true.
- `PGProperty.getName() @811 comment-changed` and `BaseDataSource.setConnectTimeout(int) @353 code-changed`: neither member changed in the diff. The parser tagged them only because lines around them moved.
- `BaseDataSource.getSslResponseTimeout()` / `setSslResponseTimeout(int)` (`comment-added`): these follow the shape of their siblings (`@return connect timeout` / `@see`). There is no finding on them.

Findings:
- **`PGProperty.java:675-678`, the `SSL_RESPONSE_TIMEOUT` comment.**
  - It reads: "After requesting an upgrade to SSL … there are reports of the server not responding due to a failover without a timeout here, the client can wait forever." This is a run-on sentence, and it parses as "a failover without a timeout". It never says what the property is.
  - It omits the facts a user needs: the unit (milliseconds), that a smaller `socketTimeout` overrides it, and what `0` does.
  - Sibling entries such as `SOCKET_TIMEOUT` (`:580-586`) open with "The timeout value used for…" and end with the unit and the meaning of zero.
  - The closing "will be set before the request and reset after" is true only when `receiveChar` returns. That is harmless, because the stream is closed on failure, but the sentence states it unconditionally.
- **`connect.md:330-332` and `README.md:121`.** Both say the property is the time "we wait", but the code waits for the lesser of this value and `socketTimeout` (`ConnectionFactoryImpl.java:541`). A user who sets `sslResponseTimeout=30000` with `socketTimeout=10` gets 10 s and has no sentence telling them so. `connect.md` also omits the default (5000), which the README states.
- **`ConnectionFactoryImpl.java:537-539`.** "We could do something tricky here to not set it in that case but this is pretty readable" narrates the author's deliberation rather than the code (style §7, "Comments age"). Its first sentence also skips the `sslTimeout == 0` case (see item 3).

## Item 2: claimed cases covered

| Claimed case (PR description / commit messages) | Test |
| --- | --- |
| A timeout fires when the server does not answer the SSLRequest | **none** |
| The timeout is set temporarily and restored afterwards | **none** |
| The timeout is configurable (`sslResponseTimeout`, default 5000) | `PGPropertyTest.testGetSetAllProperties` and `testDriverGetPropertyInfo` check this generically; nothing checks the effect of the value |
| The lesser of the current socket timeout and `sslResponseTimeout` is used (commit 574b763) | **none** |
| DataSource getter and setter | `PGPropertyTest.testDataSourceProperties` (generic) |
| Sort order (commit 7f63448) | `PGPropertyTest.testSortOrder` |

- No command lines are documented in the change.
- Every hunk belongs to a claim. The one exception is the run of trailing spaces on `README.md:121` (`git diff --check` flags it); it is inside a claimed hunk, so it is not a separate finding.

## Item 3: boundaries, partitions, and the negative control

There are no tests, so every partition below has no evidence. The code shows these:

- **`sslResponseTimeout=0`.** The check `currentTimeout > 0 && currentTimeout < sslTimeout` is false, so `setSoTimeout(0)` runs and the read waits forever. This also discards a configured `socketTimeout`. A user who sets 0 to switch the feature off, with `socketTimeout=10`, waits longer than on the base commit. **Substantive.**
- **A negative value.** `Socket.setSoTimeout(-1)` throws `IllegalArgumentException`. That is an unchecked exception that escapes `openConnectionImpl`, which catches only `IOException` and `SQLException` (`:308-335`), instead of a `PSQLException` with `INVALID_PARAMETER_VALUE`. It is neither validated nor documented. **Substantive.**
- **A non-integer value.** `getInt` turns it into a `PSQLException` (`PGProperty.java:915`). That handling is fine, but no test covers it.
- **Pre-existing state (users' current settings).**
  - Users on `socketTimeout=0` (the default) move from "wait forever" to 5 s.
  - Users with `socketTimeout > 5` move from their `socketTimeout` to 5 s. On those users' configurations, a slow server (for example postmaster under fork pressure) that answers the SSLRequest after 5 s now fails with "The connection attempt failed." caused by `SocketTimeoutException`.
  - The PR does not state this default behavior change. There is also no CHANGELOG entry under `[Unreleased]`. **Substantive.**
- **Other limits on the same work:**
  - `socketTimeout` (`ConnectionFactoryImpl.java:112-114`) bounds the same read. The `min` in the code derives one limit from the other, but no document says so (item 1).
  - `loginTimeout` (`Driver.java:705`, default 0) encloses the whole connect. A `loginTimeout` below 5 s fires first, which is expected for an enclosing limit, so this is not a finding.
  - `connectTimeout` bounds only the TCP connect, so it does not count.
- **Negative control.** A case where the server answers within the timeout and the socket's timeout is restored to the `socketTimeout` value is absent.

## Item 3a: level, placement, and the environment

The behavior can be observed without a PostgreSQL server. `LoginTimeoutTest.TimeoutHelper` (`LoginTimeoutTest.java:88-130`) already provides a local `ServerSocket` that accepts a connection and never replies, which is exactly the "server never answers the SSLRequest" fault. The request is for tests beside `LoginTimeoutTest` (or in `SocketTimeoutTest`) that share that fixture:
- `sslmode=require` with `sslResponseTimeout=500` fails within a bound, with a `SocketTimeoutException` cause.
- `socketTimeout` smaller than `sslResponseTimeout` wins.
- `sslResponseTimeout=0` (the boundary above).

No test needs an optional service, so the skip rules do not apply.

## Item 4: names by content, not by position

none. I checked the new identifiers, comments, and documentation entries; none refers to anything by position.

## Item 5: the failure report

none. There are no new assertions. The existing `testSortOrder` boolean assertion predates this change.

## Item 6: what the writer says it verified

Neither the PR description nor the commits state a red run, a manual reproduction of the hang, or a mutation result. There is no evidence that the timeout ever fired.

## Item 7: siblings of the change

- **`enableGSSEncrypted`, `ConnectionFactoryImpl.java:465-470`.** It sends the same kind of request packet and calls `pgStream.receiveChar()` with no temporary timeout. With `gssEncMode=prefer|require` (the default is `allow`, `PGProperty.java:240-242`), the same host-swap hang applies. **Substantive**: either fix it here or name it as follow-up.
- **`MakeSSL.convert`, after `'S'` (`:578`).** The TLS handshake runs at `currentTimeout`, which is 0 by default. A peer that vanishes after answering `S` still hangs. The description's scenario ("changing the host underneath") reaches this too. Name it as follow-up, or state why it is out of scope.
- **The set of connection properties.** `PGProperty`, `BaseDataSource`, the README table, and `connect.md` all list the new member. No sentence counts the properties. The CHANGELOG has no entry, as noted under item 3.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `sslResponseTimeout=0` sets an infinite read timeout and discards `socketTimeout` | Substantive | `ConnectionFactoryImpl.java:541-545` | Treat `<= 0` as "use the current timeout" (or reject it), document the meaning, and add a test |
| A negative value throws an unchecked `IllegalArgumentException` from `setSoTimeout` | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value and raise a `PSQLException` (`INVALID_PARAMETER_VALUE`); add a test |
| No test covers the timeout firing, the restore, or the "lesser of" rule | Substantive | none (no test files) | Tests next to `LoginTimeoutTest`, reusing `TimeoutHelper` (item 3a), plus the negative control |
| Default behavior change (wait forever, or `socketTimeout` above 5 s, becomes 5 s) is not stated; no CHANGELOG entry | Substantive | PR description, `CHANGELOG.md` | Say so in the description and add an `[Unreleased]` entry |
| Docs omit that a smaller `socketTimeout` caps the value, what 0 means, and (in `connect.md`) the default | Substantive | `connect.md:330`, `README.md:121`, `PGProperty.java:675` | State the cap, the meaning of 0, and the default |
| The `SSL_RESPONSE_TIMEOUT` Javadoc is a run-on sentence that misparses and never says what the property is | Substantive | `PGProperty.java:675-678` | A first sentence in the shape of `SOCKET_TIMEOUT`, giving the unit and the zero value |
| The GSS encryption request has the same unbounded `receiveChar` | Substantive | `ConnectionFactoryImpl.java:470` | Apply the same timeout, or name it as follow-up |
| The TLS handshake after `'S'` is still unbounded | Substantive | `ConnectionFactoryImpl.java:578` | Name it as follow-up, or state why it is out of scope |
| The code comment narrates the author's deliberation ("We could do something tricky…") | Taste | `ConnectionFactoryImpl.java:537-539` | Remove the second sentence |
| Milliseconds, while sibling timeouts use seconds | Taste | `PGProperty.java:681` | Consider seconds for consistency |
| `connect.md` entry is indented with spaces and has no blank line, unlike its tab-indented siblings | Taste | `connect.md:330-332` | Match the sibling formatting |

This review did not build the project or run the test suite. It did not check runtime behavior, did not check the checkstyle result for `set(properties,sslResponseTimeout)`, and did no style-only pass over the prose.
