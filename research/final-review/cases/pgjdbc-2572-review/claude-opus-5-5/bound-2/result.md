# Final review: `sslResponseTimeout` (6e453aa..HEAD)

The change has no new tests. The main defect is that `sslResponseTimeout=0` (and any negative value) is passed straight to `setSoTimeout`. With `socketTimeout` set, 0 turns off the read limit the user already had. A negative value throws an `IllegalArgumentException` instead of a connection error.

I had the task statement (the PR description) and the six commit messages. There was no previous report. I loaded `test-authoring` and `english-developer-style`. No `javadoc-authoring` copy was in the skills directory, so I checked the comments against the item questions alone.

The drift script reported:
- `PGProperty @25` and `PGProperty.getName() @811`: line shifts caused by the inserted constant.
- `BaseDataSource.setConnectTimeout(int)`: an artifact of the adjacent insertion.
- `enableSSL(...)`: real code change, no comment.
- `get/setSslResponseTimeout`: comments added.

## Item 1: comments consistent with the code and with each other

- **`PGProperty.java:675-677` (Javadoc of `SSL_RESPONSE_TIMEOUT`)** is one run-on sentence. A reader can take "due to a failover without a timeout here" as one phrase. The Javadoc also leaves out two things the code does:
  - the timeout is capped by the socket's current timeout (`ConnectionFactoryImpl.java:542`);
  - 0 means "no timeout" because `setSoTimeout(0)` means infinite.

  "set before the request and reset after" is accurate. The `<p>…</p>` wrapper around a single paragraph is noise.
- **`connect.md:330-332`** gives no default (5000), even though the README and `PGProperty` do. It doesn't say the value is capped by `socketTimeout`, or what 0 means. Every neighbouring entry has "The timeout is specified in seconds and a value of zero means that it is disabled". This entry is in milliseconds and doesn't say what zero means. A reader who sets `sslResponseTimeout=10000` with `socketTimeout=3` will think they get 10 s; they get 3 s. The entry also uses 4-space indentation with no blank line after `= int`, while every sibling uses a blank line and a tab, so it renders differently.
- **`README.md:121`**: the same missing cap and missing meaning of 0. The row also has about 170 trailing spaces.
- **`ConnectionFactoryImpl.java:539-541`**: the comment matches the code. "We could do something tricky here…" talks about the change rather than the code (taste).
- **`BaseDataSource.java:357-372`**: the `@return SSL ResponseTimeout` wording is odd, but it follows the sibling `@return connect timeout` style. No finding.
- No comment says `now`, `no longer` or `used to`.

## Item 2: claimed cases covered

Claimed cases, from the PR description and the commit messages:

| Claimed case | Test |
| --- | --- |
| (a) A server that does not answer the SSLRequest makes the connection fail after the timeout instead of hanging. | **none** |
| (b) The value is configurable via `sslResponseTimeout` (27deb41). | `PGPropertyTest.testGetSetAllProperties`, `testDataSourceProperties`, `testDriverGetPropertyInfo` cover it through registration. |
| (c) "use lesser of current socket timeout or sslresponse timeout" (574b763). | **none** |
| (d) The timeout is "set temporarily", so the previous socket timeout is restored afterwards. | **none** |
| (e) The sort order is fixed (7f63448). | `PGPropertyTest.testSortOrder` |

The design reason is the min-of-two rule in (c). A test that would fail if it were replaced by "always use sslResponseTimeout" needs `socketTimeout` below `sslResponseTimeout` and an assertion on the elapsed time or the exception. It doesn't exist.

The changed files contain no commands to run.

Every hunk is claimed by a sentence: the README, connect.md, `PGProperty` and `BaseDataSource` hunks by 27deb41 and 574b763, the `ConnectionFactoryImpl` hunk by the PR description. None is unclaimed.

## Item 3: boundaries, partitions, and the negative control

**Untested boundaries and invalid values (substantive):**
- **0**: `setSoTimeout(0)` means infinite. Worse, with `socketTimeout=N>0` the rule at `:542` keeps `sslTimeout=0`, so the SSL response read becomes unbounded where on the base commit it was bounded by `socketTimeout`. Setting the new property to 0 removes a limit the user already had.
- **Negative values** (e.g. `-1`): `Socket.setSoTimeout` throws `IllegalArgumentException`. That is neither an `IOException` nor a `SQLException`, so it skips the per-host failover handling at `:308-340` and escapes `getConnection` unwrapped.
- **Equal values** (`currentTimeout == sslTimeout`) and **current timeout 0** (no `socketTimeout`, the default) are the two branches of the min rule; neither is tested.
- **Non-integer values**: `getInt` throws `PSQLException`, consistent with other properties. No finding.

**Negative control:** `sslmode=disable` and `sslmode=allow` return before the new code. No test confirms that `disable` or `allow` connects to a silent server without the timeout firing (taste; the early return makes it plain).

**Settings users already pass:** under the default `sslmode=prefer`, every existing user now has a 5 s limit on the SSLRequest reply. Before, the limit came from `socketTimeout`, or there was none. A slow-to-wake server or proxy that answers after 5 s used to connect and now fails with "The connection attempt failed." Nothing in the description or CHANGELOG accepts this behaviour change (substantive: add a sentence, or a CHANGELOG entry).

**Failure mode, old vs new**, on a silent server after connect:
- **Old:** waits for `socketTimeout`, or for `loginTimeout` (`Driver.java:705`, which wraps the whole connect), or forever. Prints the timeout of whichever fired.
- **New:** fails after min(5 s, `socketTimeout`). The `SocketTimeoutException` "Read timed out" is wrapped as "The connection attempt failed." (`:322-331`), or the driver moves to the next host.

Nothing in the message names `sslResponseTimeout`, so a user cannot tell which setting to raise (taste).

**Other limits on the same work:**
- **`socketTimeout`** (seconds, set at `:112-114`) caps this one by design. Raising `sslResponseTimeout` past it has no effect, and no document says so (substantive, folded into the Item 1 doc finding).
- **`loginTimeout`** encloses the whole connect, across all hosts. With `loginTimeout=3`, the 5 s default never fires; that is acceptable for an outer limit. With several hosts, each costs up to 5 s, so `loginTimeout` may expire before later hosts are tried. Not stated (taste).
- **`connectTimeout`** bounds only the TCP connect, not this read. Not counted.

## Item 3a: level, placement, and the environment

There is no behaviour test. The behaviour is observable in one process with no PostgreSQL: a `ServerSocket` that accepts and never writes, with `sslmode=require` and `sslResponseTimeout=500`, then assert that `getConnection` fails within a bound and the cause is a `SocketTimeoutException`.

`LoginTimeoutTest` already has exactly such a silent server (`TimeoutHelper`, `LoginTimeoutTest.java:88-97`). New tests belong beside it, sharing that helper: the timeout, the min with `socketTimeout`, 0, and a negative value. No server prerequisite, so no skip is needed.

## Item 4: names by content, not by position

None. I checked the new property name, comments and docs for ordinal or positional references.

## Item 5: the failure report

None in the change: no assertions were added. The existing `testSortOrder` assertion that covers the new constant prints both names in its message.

## Item 6: what the writer says it verified

Neither the PR description nor the commits mention a red run on the base commit, a mutation verdict, or a manual run against a silent server. There is no evidence that the timeout fires.

## Item 7: siblings of the change

**Same unbounded read in GSS (substantive):** `enableGSSEncrypted` (`ConnectionFactoryImpl.java:433-470`) sends GSSENCRequest and calls `pgStream.receiveChar()` with no temporary timeout. It is reached when `gssEncMode` is `prefer` or `require`; the default is `allow`, so only opted-in users are exposed. A server swapped underneath the connection hangs there exactly as in the reported case. Fix it in this change, or name it as a follow-up.

**TLS handshake after `S` (taste):** `MakeSSL.convert(pgStream, info)` at `:577` runs the handshake under the restored timeout, which may be infinite. The same failover could hang there. It is outside "get the return from requesting SSL upgrade", but worth a follow-up sentence.

**Other code that saves and restores `SoTimeout`:**
- `QueryExecutorImpl.java:778` and `V3ReplicationProtocol.java:124-133`: unrelated operations. I read the replication one: it also takes a minimum, and it skips 0. That is the pattern the 0 case here lacks.
- `PGStream.java:124`: the copy constructor used for the `'E'` reconnect copies `soTimeout` from the old stream. The restore happens before it, so the reconnect inherits the right value. No finding.

**Places that list the members** (searched for `connectTimeout` and `socketTimeout` together):
- README table and `connect.md`: updated.
- `PGProperty` and `BaseDataSource`: updated.
- `CHANGELOG.md` `[Unreleased]`: not updated. That is the sibling list for user-visible additions (substantive).
- No prose counts the timeout properties.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `sslResponseTimeout=0` makes the SSL reply read unbounded, even when `socketTimeout` used to bound it. | Substantive | `ConnectionFactoryImpl.java:542-545` | Treat `sslTimeout <= 0` as "use the current timeout" (as `V3ReplicationProtocol` does), document 0, and test it. |
| 2 | A negative value throws `IllegalArgumentException` from `setSoTimeout`, which skips failover and escapes `getConnection` unwrapped. | Substantive | `ConnectionFactoryImpl.java:545` | Validate the value (or treat it like 0) and test the invalid partition. |
| 3 | No test for the timeout firing, the min with `socketTimeout`, or the restore of the old timeout. | Substantive | — (`LoginTimeoutTest.java:88`) | In-process tests using the silent `ServerSocket` helper in `LoginTimeoutTest`. |
| 4 | The docs and Javadoc don't mention the cap by `socketTimeout`, the meaning of 0, or (in `connect.md`) the default. | Substantive | `connect.md:330`, `README.md:121`, `PGProperty.java:675` | State all three; reword the run-on Javadoc sentence. |
| 5 | GSSENCRequest reply read has the same unbounded wait. | Substantive | `ConnectionFactoryImpl.java:465-470` | Apply the same timeout, or name it as a follow-up in the description. |
| 6 | New 5 s default for every `sslmode=prefer` user is not stated, and there is no CHANGELOG entry. | Substantive | `CHANGELOG.md` `[Unreleased]` | Add an entry that states the new default and the behaviour change. |
| 7 | No red run or other evidence that the timeout fires. | Substantive | — | State the run against a silent server, or the test's red run on the base commit. |
| 8 | Timeout error doesn't name `sslResponseTimeout`. | Taste | `ConnectionFactoryImpl.java:552` | Wrap the `SocketTimeoutException` with a message naming the property. |
| 9 | TLS handshake after `S` is still unbounded. | Taste | `ConnectionFactoryImpl.java:577` | Follow-up sentence in the description. |
| 10 | `connect.md` entry formatting differs from its siblings (no blank line, spaces instead of tab); README row has trailing spaces; `properties,sslResponseTimeout` is missing a space. | Taste | `connect.md:330`, `README.md:121`, `BaseDataSource.java:372` | Match the sibling formatting. |
| 11 | "We could do something tricky here…" talks about the change, not the code. | Taste | `ConnectionFactoryImpl.java:539-541` | Keep only "use the smaller of the two timeouts". |

Not checked: I did not build the project or run the suite, as instructed. I did not do a style-only pass over the prose. Comments were checked against the item questions without a `javadoc-authoring` skill, since none was among the provided copies.
