# Final review: `sslResponseTimeout` (6e453aa..HEAD)

**The task statement says:** a cloud failover can leave the client waiting forever for the server's answer to an SSL upgrade request. The fix sets a socket timeout for that read only and puts the old timeout back afterwards. The commit messages add three claims: the timeout is a property you can configure (URL and DataSource), its default is 5000 ms, and the code uses whichever is smaller, this timeout or the current `socketTimeout`.

**Drift script output:** `PGProperty` (code-changed, comment-unchanged), `PGProperty.getName()` (comment-changed), `ConnectionFactoryImpl.enableSSL` (code-changed, no-comment), `BaseDataSource.getSslResponseTimeout`/`setSslResponseTimeout` (comment-added), `BaseDataSource.setConnectTimeout` (code-changed, comment-unchanged). The `getName()` and `setConnectTimeout` entries are wrong attributions. They are really the new `SSL_RESPONSE_TIMEOUT` javadoc and the new setter next to `setConnectTimeout`, and I reviewed them as such.

Skills loaded: `test-authoring` and `english-developer-style`. The `javadoc-authoring` skill was not in the provided set, so the doc-comment checks below use the form's own wording.

## Item 1: comments consistent with the code and with each other

- **`PGProperty.java:675-678` (`SSL_RESPONSE_TIMEOUT` javadoc).**
  - The first sentence does not say what the property is. It tells the history ("there are reports of…").
  - It is also one run-on sentence: "…due to a failover without a timeout here, the client can wait forever". You can read it as saying the failover has no timeout.
  - "This timeout will be set before the request and reset after" leaves out the rule the code adds: a nonzero `socketTimeout` smaller than this value wins (`ConnectionFactoryImpl.java:539-543`).
  - It leaves out what `0` does. The code passes `0` to `setSoTimeout`, which disables the timeout and also overrides any `socketTimeout`. It also leaves out the unit, which the description string does give.
- **`docs/documentation/head/connect.md:330-332`.**
  - It does not mention the `socketTimeout` minimum, the 5000 default, or what `0` means. The neighbouring entries (`connectTimeout`, `socketTimeout`) state the unit, what zero means, and (for `cancelSignalTimeout`) the default.
  - It writes in the first person ("we wait"). It has no blank line after the bullet, and it indents with spaces where its neighbours use a tab. That may render differently from the other entries.
- **`README.md:121`.**
  - "Socket timeout waiting for a response…" gives no unit. Every neighbouring row is in seconds (`connectTimeout` 10, `socketTimeout` 0). So a reader seeing a default of `5000` here may assume seconds.
  - The line ends in a long run of trailing spaces.
- **`ConnectionFactoryImpl.java:539-541`, inline comment.** "We could do something tricky here to not set it in that case but this is pretty readable" talks about the change itself, not about the code. The first half of the comment is accurate.
- **`BaseDataSource.java:357-373`.** Each javadoc opens with an empty line before `@return` / `@param`, and the text reads "SSL ResponseTimeout". The neighbouring `getConnectTimeout` doesn't have the empty line (taste).

## Item 2: claimed cases covered

| Claimed case | Test |
|---|---|
| Read of the SSLRequest response times out when the server doesn't answer (the PR's main claim) | **none** |
| Previous socket timeout is restored after the response arrives | **none** |
| A smaller nonzero `socketTimeout` takes priority over `sslResponseTimeout` (commit 574b763) | **none** |
| `socketTimeout = 0` → `sslResponseTimeout` applies | **none** |
| Property can be set through the URL / `Properties` | **none** specific; the generic loops in `PGPropertyTest` iterate every property |
| DataSource getter/setter exist and round-trip | `PGPropertyTest` (bean-descriptor check over all properties, lines ~140-150) |
| Sort order (commit 7f63448) | `PGPropertyTest.testSortOrder` |

None of the behaviour the change claims has a test. Only the registration checks that run over every property cover it.

## Item 3: boundaries, partitions, and the negative control

- **No tests**, so there are no boundaries and no negative control. The missing control is a server that does answer the SSLRequest; the connection should succeed and keep its `socketTimeout`.
- **`sslResponseTimeout = 0` (boundary).** With `socketTimeout > 0`, the guard `currentTimeout < sslTimeout` is false, so `setSoTimeout(0)` runs. This makes the read wait forever and ignores the user's `socketTimeout`. That is the opposite of the "use the lesser" rule.
- **Negative `sslResponseTimeout` (invalid partition).** `Socket.setSoTimeout` throws `IllegalArgumentException`. `openConnectionImpl` catches only `ConnectException`, `IOException` and `SQLException`, so a raw `RuntimeException` escapes `connect()`. There is no validation and no test.
- **Other limits on this read** (a single read inside the connection attempt):
  - `socketTimeout` (documented, seconds): handled by taking the minimum.
  - `loginTimeout` (documented, seconds, default 0, `Driver.java:705`): bounds the whole connect from the same start. At a nonzero `loginTimeout` below 5 s, the login timeout fires first and hides this one's report. At the default 0 that doesn't happen. A note in the docs would cover it.
  - `connectTimeout` covers only the TCP connect, so it isn't the same limit.
- **Unit mismatch.** `socketTimeout`, `connectTimeout`, `loginTimeout` and `cancelSignalTimeout` are all in seconds; this new property is in milliseconds. Users who set `sslResponseTimeout=10` by analogy get 10 ms. A reader's guess about the unit is what makes this substantive.
- **Not covered by the new timeout:** the TLS handshake after `'S'` (`MakeSSL.convert`) still runs at the restored timeout, which is 0 by default. The same failover during the handshake would still hang. See item 7.

## Item 3a: level, placement, and the environment

The behaviour can be seen in one process with no PostgreSQL server: a local `ServerSocket` that accepts and never writes. Connecting to it with `sslmode=require` and a small `sslResponseTimeout` should fail within that time. With `socketTimeout=1` and `sslResponseTimeout=60000` it should fail in about 1 s. No such test exists. It belongs in the existing connection/SSL tests, for example next to the `PGPropertyTest` fixture or an existing `ConnectionFactoryImpl`-level test. A new class isn't needed.

## Item 4: names by content, not by position

None. I checked the new identifiers, comments and doc entries; none refers to anything by position.

## Item 5: the failure report

None. The change adds no assertions. The existing `testSortOrder` message prints its operands.

## Item 6: what the writer says it verified

The commits and the PR description give no evidence: no red run on the base commit, and no reproduction of the hang.

## Item 7: siblings of the change

`receiveChar()` reads in `ConnectionFactoryImpl` (three call sites):

- **`:470` in `enableGSSEncrypted`.** Same pattern: request packet, then a blocking one-byte response, with no timeout. The default `gssEncMode=allow` returns before this read. But `prefer`/`require` reach it, and a failover there hangs the same way. **This applies:** fix it in this change or name it as follow-up.
- **`:553`.** The changed site.
- **`:644` in `doAuthentication`.** Covered by `socketTimeout`, which is reset at `:171-173`. This is a normal protocol read, so the defect doesn't apply.
- **`MakeSSL.convert` (TLS handshake).** Not a `receiveChar` caller, but it is the next blocking step of the same upgrade, and it runs with no timeout by default. Name it as follow-up.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| No test for the timeout firing, the restore, or the `socketTimeout` minimum | Substantive | `ConnectionFactoryImpl.java:535-554` | In-process test using a silent `ServerSocket`: timeout fires; smaller `socketTimeout` wins; a server that answers still connects (control) |
| `sslResponseTimeout=0` disables the read timeout and overrides `socketTimeout` | Substantive | `ConnectionFactoryImpl.java:542` | Treat `0` as "use the current timeout" (or document that it means infinite), and test it |
| Negative value escapes as `IllegalArgumentException` | Substantive | `ConnectionFactoryImpl.java:545` | Validate, or map to a `PSQLException`; add a test |
| Property javadoc: first sentence isn't a definition, run-on misreads, no `socketTimeout` minimum / `0` meaning / unit | Substantive | `PGProperty.java:675-678` | Rewrite: what it bounds, unit, default, the minimum with `socketTimeout`, `0` behaviour |
| README row gives no unit next to seconds-based rows; trailing whitespace | Substantive | `README.md:121` | Say "milliseconds"; trim the line |
| connect.md entry leaves out default, `0`, the `socketTimeout` minimum; formatting differs from neighbours | Substantive | `connect.md:330-332` | Add the facts; match the blank-line and tab layout |
| GSSENC request read has the same unbounded wait | Substantive | `ConnectionFactoryImpl.java:470` | Apply the same timeout, or name it as follow-up in the PR |
| TLS handshake after `'S'` has no timeout by default | Substantive | `ConnectionFactoryImpl.java:576` (`MakeSSL.convert`) | Name as follow-up, or keep the timeout through the handshake |
| Milliseconds while the sibling timeouts use seconds | Taste | `PGProperty.java:681` | Prefer seconds to match `socketTimeout`/`connectTimeout` |
| `loginTimeout` < 5 s hides this timeout's report | Taste | `connect.md:330` | Document the pair |
| Inline comment talks about the change ("something tricky… pretty readable") | Taste | `ConnectionFactoryImpl.java:539-541` | Keep only the first sentence |
| Empty first line in the getter/setter javadoc; "SSL ResponseTimeout" | Taste | `BaseDataSource.java:357-371` | Match `getConnectTimeout` |

I didn't build the project or run its test suite, and I didn't do a style-only pass over the prose.
