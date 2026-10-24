# Final review: `6e453aa..HEAD` (sslResponseTimeout)

I ran the drift script against `6e453aa` and `HEAD`. Its parse is approximate. It tagged `PGProperty.getName() @811` as `comment-changed`, but the hunk is really the Javadoc of the new `SSL_RESPONSE_TIMEOUT` constant, and I read it as that. No earlier report of this form exists. The repository has no `AGENTS.md` or `CLAUDE.md`. Following test-authoring §0, I propose adding a stack line: `Tests: JUnit 4 engine, JUnit 4 assertions` (that is what `PGPropertyTest` imports). I edited no file.

## Item 1: Comments consistent with the code and with each other

- **`PGProperty.java:675-677`, the `SSL_RESPONSE_TIMEOUT` Javadoc.**
  - The first sentence is a run-on: "…there are reports of the server not responding due to a failover without a timeout here, the client can wait forever." A reader can take "without a timeout" as describing the failover. The sentence also tells the history instead of saying what the property is.
  - "This timeout will be set before the request and reset after" is not true on the timeout path. When `receiveChar()` throws `SocketTimeoutException`, `setSoTimeout(currentTimeout)` at `ConnectionFactoryImpl.java:554` never runs. The stream does get closed by `tryConnect`'s catch, so this is harmless, but the sentence still misstates it.
  - The comment does not say that the value is capped by `socketTimeout`, or what `0` means.
- **`ConnectionFactoryImpl.java:538-540`**: "We could do something tricky here to not set it in that case but this is pretty readable" talks about the writing of the code rather than the code. It also fails to mention the case it gets wrong (`sslResponseTimeout=0`, see item 3).
- **`BaseDataSource.java:357-372`**: the getter and setter comments open with an empty first sentence, and the getter's `@return SSL ResponseTimeout` has a misplaced space. The neighbors (`getConnectTimeout`) use the same thin form, so this is taste.
- **The docs disagree with the code and with each other:**
  - `README.md:121` gives the default as `5000` with no unit. Every neighboring timeout in that table (`connectTimeout`, `socketTimeout`, `loginTimeout`) is in seconds, so a reader will take this as 5000 s.
  - `connect.md:330-332` says milliseconds but gives no default.
  - Neither page says the value is capped by `socketTimeout` or what `0` does. The cap is the behavior commit 574b763 introduced.

## Item 2: Claimed cases covered

| Claimed case (source) | Test |
| --- | --- |
| A server that never answers the SSLRequest fails after the timeout instead of hanging (PR description) | none |
| The timeout is reset after the response (PGProperty Javadoc) | none |
| The lesser of `socketTimeout` and `sslResponseTimeout` is used (commit 574b763) | none |
| The property is configurable and exposed on DataSource (commit 27deb41) | `PGPropertyTest.testDataSourceProperties` and `testGetSetAllProperties` cover it generically, as an open-set test |
| Sort order of the enum (commit 7f63448) | `PGPropertyTest.testSortOrder` |

The change carries no behavioral test at all.

No command lines are added. Every hunk is claimed by a commit message, except the trailing whitespace added to the README row (about 170 spaces at `README.md:121`), which is noise.

## Item 3: Boundaries, partitions, and the negative control

- **No boundaries are tested.** Nothing exercises `0`, a negative value, a value equal to `socketTimeout`, or the controls `sslmode=disable` or `allow`, where no request is sent and no timeout is applied.
- **`sslResponseTimeout=0` with `socketTimeout>0` disables the read limit during the SSL response.**
  - With `0`, the guard `currentTimeout > 0 && currentTimeout < sslTimeout` is false, so `setSoTimeout(0)` runs. A socket that previously had `socketTimeout=10` now waits forever for the SSL byte.
  - So this change makes that configuration hang where the base commit failed after 10 s.
  - A negative value makes `Socket.setSoTimeout` throw `IllegalArgumentException`. That escapes as an unchecked exception rather than as a `PSQLException` naming the property.
- **Other limits on the same work:**
  - `socketTimeout` (seconds, set by `PGProperty.SOCKET_TIMEOUT`, applied at `ConnectionFactoryImpl.java:114`): it caps the new setting. Raising `sslResponseTimeout` above it has no effect, and no doc says so.
  - `loginTimeout` (seconds, `Driver.java:705`, which abandons the whole connect): with `loginTimeout=2`, any `sslResponseTimeout` above 2000 never fires. No doc says so.
  - `connectTimeout` ends only the TCP connect, not this work, so it does not count.
  - Nothing derives one limit from another, and no test sets either value past the other.
- **Pre-existing state, and the mechanism this replaces:**
  - The new default of 5000 ms reaches every existing user with `sslmode=prefer` (the default), `require`, or `verify-*`.
  - Fault 1, a peer that never answers: before, the connect hung until `socketTimeout`, `loginTimeout`, or forever. Now it fails after 5 s with a bare `SocketTimeoutException: Read timed out` that names neither the SSLRequest nor the property, and the code moves to the next host.
  - Fault 2, a slow but healthy server (under load, or a high-latency link) that answers the SSLRequest after more than 5 s: this used to connect and now fails.
  - No sentence in the change accepts that behavior change or justifies the 5 s default.

## Item 3a: Level, placement, and the environment

- `enableSSL` is private. Its behavior can be observed in one process through `ConnectionFactoryImpl.openConnectionImpl` (or `DriverManager.getConnection`) against a local `ServerSocket` that accepts and never replies. That is a medium test on localhost and needs no PostgreSQL server.
- Three cases are owed:
  - the timeout fires within the configured bound;
  - with `socketTimeout` smaller, the smaller one fires;
  - the control with `sslmode=disable`, which sends no SSLRequest.
- None exists. The natural home is beside the existing SSL and connect tests in `pgjdbc/src/test/java/org/postgresql/test/jdbc2` (for example `ConnectTimeoutTest`).

## Item 4: Names by content, not by position

None. No new test names, case ids, or messages exist. The comments refer to things by name ("the current timeout", "sslTimeout").

## Item 5: The failure report

None. No assertions were added. The generic `PGPropertyTest` assertions that cover the new constant were not changed.

## Item 6: What the writer says it verified

Neither the commits nor the PR description state a red run on the base commit, a mutation verdict, or a manual reproduction of the hang (for example a socket that accepts and does not reply). The writer states no evidence of any kind.

## Item 7: Siblings of the change

- **`enableGSSEncrypted` (`ConnectionFactoryImpl.java:463-470`)** sends the matching GSSENCRequest and blocks in `pgStream.receiveChar()` with no timeout. A server that changes underneath the connection hangs there the same way when `gssEncMode` is `prefer` or `require`. The default (`allow`) skips it, which narrows the exposure but does not remove it. It needs fixing, or naming as follow-up in the description.
- **`MakeSSL.convert`**: the TLS handshake after an `'S'` reply runs with `currentTimeout`, so with `socketTimeout=0` it can still hang. The task statement names only the upgrade response, so this belongs as a follow-up sentence.
- **Other `getSoTimeout`/`setSoTimeout` users** (`QueryExecutorImpl.java:778`, `V3ReplicationProtocol.java:124`, `PGStream.java:201-210`): these are unrelated paths and the defect does not apply. They do use the save/restore idiom in `try/finally`, which the new code does not. The new code also calls `getSocket().setSoTimeout` directly instead of `PGStream.setNetworkTimeout`/`getNetworkTimeout` (`PGStream.java:744-749`), which taste prefers.
- **The set of properties:**
  - `README.md` and `connect.md` both list the new property.
  - `CHANGELOG.md` `[Unreleased]` does not, even though `CONTRIBUTING.md:243` ("Updating changelog") asks for an entry.
  - The DataSource getter and setter are present.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `sslResponseTimeout=0` overrides a positive `socketTimeout` and waits forever; a negative value throws `IllegalArgumentException` | Substantive | `ConnectionFactoryImpl.java:541-545` | Treat `0` as "use the current timeout" (or document `0` as disabled and still honor `socketTimeout`), reject negatives with a `PSQLException`, and test both |
| No test of the timeout, the `socketTimeout` cap, or the control | Substantive | (none) | A localhost `ServerSocket` that never replies, through `getConnection`: timeout fires; smaller `socketTimeout` wins; `sslmode=disable` control |
| No evidence the fix was seen to work (red run or reproduction) | Substantive | (PR) | State the reproduction and its result |
| The default changes behavior for every SSL user (a slow server now fails after 5 s), with no sentence accepting it; the timeout error does not name the SSLRequest or the property | Substantive | `PGProperty.java:681` | Justify the default in the description, or default to `0`/off; wrap the `SocketTimeoutException` in a message naming `sslResponseTimeout` |
| README row omits the unit; neighbors are in seconds, so 5000 reads as seconds | Substantive | `README.md:121` | Say "milliseconds" in the row; drop the trailing whitespace |
| Docs omit the default, the `socketTimeout` cap, the `loginTimeout` interaction, and the meaning of `0` | Substantive | `connect.md:330-332`, `PGProperty.java:675-677` | Add them; match the neighbors' tab-indented, blank-line format |
| Javadoc run-on sentence, and "reset after" is false on the timeout path | Substantive | `PGProperty.java:675-677` | State what the property bounds and its cap; drop the narrative or fix the claim |
| GSSENCRequest has the same unbounded read | Substantive | `ConnectionFactoryImpl.java:470` | Apply the same bound, or name it as follow-up in the description |
| No CHANGELOG entry | Substantive | `CHANGELOG.md:6` | Add one under `[Unreleased]` |
| Timeout restored outside `try/finally`; bypasses `PGStream.setNetworkTimeout` | Taste | `ConnectionFactoryImpl.java:536-554` | Use `get/setNetworkTimeout` with a `finally` |
| Comment explains the writer's choice rather than the code | Taste | `ConnectionFactoryImpl.java:538-540` | Rewrite as one sentence on why the smaller timeout wins |
| Empty first sentences, "SSL ResponseTimeout", missing space after the comma in `set(properties,…)` | Taste | `BaseDataSource.java:357-372` | Tidy to match the neighbors |

Not checked: I did not build the project or run the test suite, I did not reproduce the hang, and I did not do a wording pass over the prose for style alone.
