I reviewed `6e453aa..HEAD` (six commits by Dave Cramer). The main problem: with default settings the new timeout never takes effect, because the driver's read buffer silently retries timed-out reads. There are also no tests.

# Final review: `6e453aa..HEAD`, "set a timeout to get the return from requesting SSL upgrade"

**Inputs.** I read the diff whole, the PR description, and the six commit messages. There is no earlier report and the change adds no test class. `comment-drift.py` reported:
- `PGProperty`: code-changed, comment-unchanged. This is the enum header and is not affected.
- `PGProperty.getName()`: comment-changed. This is a misparse; the comment it found is the new one on the `SSL_RESPONSE_TIMEOUT` constant.
- `ConnectionFactoryImpl.enableSSL(...)`: code-changed, no-comment.
- `BaseDataSource.getSslResponseTimeout()` and `setSslResponseTimeout(int)`: comment-added.
- `BaseDataSource.setConnectTimeout(int)`: code-changed, comment-unchanged. This is a misparse, and that method is unchanged.

## Item 1: comments consistent with the code and with each other

**1a. `PGProperty.java:676-677`, a run-on sentence a reader has to parse twice (Substantive, `english-developer-style` §4).** The sentence reads: "After requesting an upgrade to SSL from the server there are reports of the server not responding due to a failover without a timeout here, the client can wait forever." It is two sentences joined by a comma. The phrase "without a timeout here" can attach to "failover" or to "the client can wait forever". The second sentence, "This timeout will be set before the request and reset after", leaves four things out:
- the unit;
- that `socketTimeout` caps it, when that is smaller;
- what `0` does;
- that "reset" means "restored to the previous value".

It also tells the history of the change ("there are reports") instead of stating the contract. Request: "Time, in milliseconds, to wait for the server's reply to an SSLRequest. If `socketTimeout` is set and smaller, it is used instead. The previous socket timeout is restored after the reply arrives." Also say what `0` means once item 3b is decided.

**1b. `ConnectionFactoryImpl.java:538-540`, the inline comment restates the code and misstates its condition (Substantive).** "If the current timeout is less than sslTimeout then use the smaller timeout" leaves out `currentTimeout > 0`. That condition is the one a reader needs explained: `0` means "no timeout", so it must not count as smaller. The rest of the comment ("We could do something tricky here to not set it in that case but this is pretty readable") is the author weighing options, which a reader of the code does not need. Request: replace both with "A socket timeout of 0 means none; otherwise keep whichever limit is shorter." Writing it as `Math.min`, as `V3ReplicationProtocol.configureSocketTimeout` already does, would make the comment unnecessary.

**1c. `ConnectionFactoryImpl.java:545` and `:554`, uncommented expressions a reader would misread (Substantive).** These lines call `pgStream.getSocket().setSoTimeout(...)` directly, bypassing `PGStream.setNetworkTimeout`, which every other read timeout in connection setup goes through (`tryConnect` lines 113-115 and 172-174). A competent reader would take the two calls as equivalent. They are not, and item 3a shows the result. Request: call `pgStream.setNetworkTimeout(...)` / `getNetworkTimeout()`. If the direct call is meant, the comment must say why.

**1d. `BaseDataSource.java:357-372`, Javadoc (Taste).** "@return SSL ResponseTimeout" has an internal capital, and neither the getter nor the setter states the unit. Unlike every other timeout here, which is in seconds, this one is in milliseconds, so the unit matters more than usual. The sibling `getConnectTimeout` Javadoc is just as short, so this is taste. Request: "@return SSL response timeout, in milliseconds".

No comment narrates the change with "now", "no longer" or "used to". Terms: "SSL upgrade" matches the base code's own word ("Upgraded to encrypted connection", `ConnectionFactoryImpl` ALLOW path). No coinages.

## Item 2: claimed cases covered

No test was added or changed. I answered this item from the PR description and the commit messages.

| Claimed case | Test |
| --- | --- |
| A server that never answers the SSLRequest makes the connection fail instead of hanging (PR description) | none |
| The timeout is temporary: the previous socket timeout is restored after the reply (PR: "sets the timeout temporarily") | none |
| The timeout is configurable through `sslResponseTimeout`, URL or DataSource (commit `27deb41`) | none |
| The smaller of `socketTimeout` and `sslResponseTimeout` is used (commit `574b763`) | none |

Every claimed case is a finding (Substantive). Request:
- A test with an in-process `ServerSocket` that accepts the connection and never replies. With `sslmode=require`, it asserts the connection fails within about `sslResponseTimeout`, and it must also run with `socketTimeout` unset (see 3a).
- A test with `socketTimeout=1` and `sslResponseTimeout=60000`, asserting it fails after about 1 s.
- A test that replies `N` with `sslmode=prefer` and checks the socket timeout afterwards equals `socketTimeout`.
- A `BaseDataSource` round trip, which `PGPropertyTest` may already cover generically.

Unclaimed hunks: none. The README row has about 170 trailing spaces, which is formatting only.

## Item 3: boundaries, partitions, and the negative control

**3a. The timeout never fires in the default configuration (Substantive; this is the main finding).** With `socketTimeout` unset (default `0`), `PGStream.setNetworkTimeout` is never called. So `VisibleBufferedInputStream.timeoutRequested` stays `false`. `enableSSL` sets `SO_TIMEOUT=5000` on the raw socket, then calls `receiveChar()` → `pgInput.read()` → `ensureBytes(1)` → `readMore`. In `readMore` (`VisibleBufferedInputStream.java:165-172`), the `SocketTimeoutException` is caught and dropped because `timeoutRequested` is false, and the method returns `true` with `read = 0`. `ensureBytes` then loops and reads again.

The result: a server that never replies still hangs the client forever, now in 5-second slices. That is the exact scenario the PR claims to fix. The timeout only fires when `socketTimeout > 0`, and then the user already had a bound before this change.

Comparing the two mechanisms on that fault:
- **Before the change:** blocks forever with the default settings. With `socketTimeout=s`, it fails after `s` with "The connection attempt failed." caused by `SocketTimeoutException`.
- **After the change:** still blocks forever with the default settings. With `socketTimeout` set, it fails after `min(s, sslResponseTimeout)` with the same message.

Request: set the timeout through `pgStream.setNetworkTimeout(sslTimeout)` and restore it with `setNetworkTimeout(currentTimeout)`. That method also sets `timeoutRequested`. Then run the never-reply fault with the default settings and report how long it takes and what it prints.

**3b. Boundary `sslResponseTimeout=0` cancels an existing `socketTimeout` (Substantive).** With `socketTimeout=10` (10000 ms) and `sslResponseTimeout=0`, the guard `currentTimeout < sslTimeout` is `10000 < 0`, which is false. So `setSoTimeout(0)` removes the user's 10 s bound for the duration of the SSL reply, which is worse than before the change. The docs do not say what `0` means. Request: decide that `0` means "no SSL-specific limit" and keep `currentTimeout` in that case, document it, and test that boundary.

**3c. Invalid partition: a negative value (Substantive).** `sslResponseTimeout=-1` makes `Socket.setSoTimeout` throw `IllegalArgumentException`. That exception escapes `tryConnect` (which rethrows anything) and is neither an `IOException` nor an `SQLException`, so the caller gets an unchecked exception with no `PSQLException` wrapping and no attempt on the next host. Request: reject or ignore a negative value with a message that names the property (as `receiveBufferSize` does), and test it.

**3d. Other limits on the same work:**
- **`socketTimeout`** (documented, seconds, default 0): it caps `sslResponseTimeout`, because the smaller value wins. Raising `sslResponseTimeout` above it has no effect, and neither `connect.md:330` nor `README.md:121` says so (Substantive). Request: add one sentence saying the smaller of the two applies.
- **`loginTimeout`** (documented, seconds, default 0): it bounds the whole connection attempt and fires first whenever it is shorter. That is correct nesting, so it is not a finding.
- **`connectTimeout`** (default 10 s): it bounds only the TCP connect, which is earlier work, so it does not count.
- **The TLS handshake in `MakeSSL.convert` after an `S` reply** (Taste): it runs with the restored timeout, which is infinite by default. A failover during the handshake still hangs. The property name limits the scope to the reply, so whether the PR's "hanging when asking for SSL upgrade" covers the handshake is a judgement call.

Pre-existing state: users who already pass `socketTimeout` are covered by the `min` rule, apart from 3b. The new default (5000 ms) applies to every existing connection that uses `sslmode` `prefer` or above, and the PR claims that change.

## Item 3a: level, placement, and the environment

There is no test at any level, which is a finding (Substantive). The behavior can be observed without a PostgreSQL server: a loopback `ServerSocket` that accepts and stays silent, driven through `DriverManager.getConnection` or `ConnectionFactoryImpl`. Request: put that test next to `pgjdbc/src/test/java/org/postgresql/test/jdbc2/SocketTimeoutTest.java` or `ConnectTimeoutTest`, reusing their fixture, and do not make it depend on the SSL server suite (`test/ssl/SslTest`), which needs a configured server.

## Item 4: names by content, not by position

None. I checked the new property name, the accessors, the comments and the doc entries; none refers to anything by position or ordinal.

## Item 5: the failure report

None, because the change has no assertions.

## Item 6: what the writer says it verified

Neither a failing run on the base commit nor a mutation verdict is stated in the commits or the PR description. Given 3a, such a run with the default settings would have shown the fix does not fire.

## Item 7: siblings of the change

- **`enableGSSEncrypted`** (`ConnectionFactoryImpl.java:463-466`) sends GSSENCRequest and blocks on `receiveChar()` with the same exposure, whenever `gssEncMode` is `prefer` or `require` (default `allow` returns early). The same defect applies, a finding (Substantive). Request: apply the same bounded wait, or name it as follow-up in the description.
- **Other direct `getSocket().setSoTimeout` callers** (`QueryExecutorImpl:778`, `V3ReplicationProtocol:124-133`, `PGStream.hasMessagePending:201`): these sit outside connection setup and are not reachable by this change's condition. They were not reviewed for the 3a defect.
- **Set membership:** the new property appears in the `PGProperty` enum, the README table, `connect.md`, and as a `BaseDataSource` getter/setter. The other timeout properties (`connectTimeout`, `socketTimeout`) appear only in those same places. Nothing still counts the timeouts by their old number.
- **Formatting of the `connect.md:330-332` entry** (Taste): it lacks the blank line and tab indent its neighbors use. It is also the only timeout there in milliseconds, so the unit is easy to miss.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Raw `setSoTimeout` bypasses `timeoutRequested`; with default settings the timeout is swallowed and the hang remains | Substantive | `ConnectionFactoryImpl.java:545` | 3 (3a), 1 (1c) |
| No test for any claimed case | Substantive | `ConnectionFactoryImpl.java:535-554` | 2, 3a |
| `sslResponseTimeout=0` removes an existing `socketTimeout` | Substantive | `ConnectionFactoryImpl.java:542` | 3 (3b) |
| A negative value escapes as an unwrapped `IllegalArgumentException` | Substantive | `ConnectionFactoryImpl.java:545` | 3 (3c) |
| Docs omit that `socketTimeout` caps the value, and what `0` means | Substantive | `connect.md:330`, `README.md:121` | 3 (3d) |
| Run-on Javadoc sentence, no unit, ambiguous "reset" | Substantive | `PGProperty.java:676-677` | 1 (1a) |
| Inline comment omits the `> 0` condition and narrates the author's choice | Substantive | `ConnectionFactoryImpl.java:538-540` | 1 (1b) |
| GSSENCRequest reply wait has the same unbounded hang | Substantive | `ConnectionFactoryImpl.java:463-466` | 7 |
| TLS handshake after `S` remains unbounded | Taste | `ConnectionFactoryImpl.java:578` | 3 (3d) |
| Accessor Javadoc lacks the unit, and its capitalization is off | Taste | `BaseDataSource.java:359,368` | 1 (1d) |
| `connect.md` entry formatting differs from its neighbors | Taste | `connect.md:330-332` | 7 |

The drift script misattributed the new enum-constant comment to `PGProperty.getName()`, so I read the `PGProperty` comments by hand instead.
