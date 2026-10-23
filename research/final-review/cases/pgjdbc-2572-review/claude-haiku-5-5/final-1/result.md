# Final review: `6e453aa..HEAD` (SSL response timeout)

Reviewed the diff whole, then ran the drift script. Loaded `test-authoring` and `english-developer-style` from the skills directory. `javadoc-authoring` is not among the provided copies, so the doc-comment rules are applied from the item text and §7 of `english-developer-style`. No previous report exists, so there is no table of prior findings.

## Item 1: comments consistent with the code and with each other

Findings are below, in the table. The comment at `ConnectionFactoryImpl.java:538-540` says the code uses "the smaller timeout". That is false when `sslResponseTimeout=0`, which is finding 1. The `PGProperty.java:674-678` javadoc first sentence describes history, not what the property does, and ends in an unfinished "reset after" (finding 4). The drift script's `BaseDataSource.setConnectTimeout` and `PGProperty.getName` tags are parser artifacts: the diff does not touch either body or comment.

## Item 2: claimed cases covered

The task statement claims a timeout on the SSL response wait. No test method exists for it, and the diff adds no test file. Claimed cases with no test: the wait ends when the server is silent, the default is 5000, the property is configurable, and the socket timeout is restored after the response. See finding 6.

## Item 3: boundaries, partitions, and the negative control

- **Zero value:** `sslResponseTimeout=0` with `socketTimeout=10000` makes `sslTimeout` 0 and sets `SO_TIMEOUT` to 0, so the SSL wait is unbounded and the socket timeout is bypassed (finding 1).
- **Negative value:** `getInt` accepts `-1`, and `Socket.setSoTimeout` throws `IllegalArgumentException`, which escapes as an unchecked exception (finding 2).
- **Other limits on the same work:**
  - `loginTimeout` (Driver.java:289-298, `ConnectThread`; "Connection attempt timed out." at Driver.java:398) ends the whole connect, so any `sslResponseTimeout` above `loginTimeout * 1000` never fires. Not documented, not tested (finding 3).
  - `socketTimeout` is handled by the `min` logic, but the docs do not say so (finding 3).
  - `connectTimeout` bounds the socket connect only, not this read.
  - The default 5000 applies to every connection with `sslmode` other than `disable` or `allow`, where previously the wait was unbounded. The docs do not say this (finding 3).
- **Control:** no test sets the other value of the setting. Nothing is tested.
- **Pre-existing state:** none; the change writes no persisted state.

## Item 3a: level, placement, and the environment

The behavior crosses a socket boundary (bytes on a socket), so a medium test is owed. A local `ServerSocket` that accepts and never answers, with `sslmode=require` and a short `sslResponseTimeout`, is the natural shape. The control is the same server answering `N`. Place the test beside `ConnectTimeoutTest` and `SocketTimeoutTest` in `pgjdbc/src/test/java/org/postgresql/test/jdbc2`. Those tests use the real database through `TestUtil`, so this one must not depend on the database. None of this exists yet (finding 6).

## Item 4: names by content, not by position

none. The new identifiers (`sslTimeout`, `currentTimeout`, `SSL_RESPONSE_TIMEOUT`, `getSslResponseTimeout`, `setSslResponseTimeout`) name content. No test names or messages refer by position.

## Item 5: the failure report

none. The change adds no assertions or test cases, so there is nothing to check here.

## Item 6: what the writer says it verified

Neither the commit messages nor the diff state a red run on the base commit or any mutation verdict. The writer has not stated evidence that the change is observable. This is a finding (finding 6).

## Item 7: siblings of the change

- `ConnectionFactoryImpl.java:470` (`enableGSSEncrypted`) sends a request and calls `receiveChar()` with no timeout. The same unbounded wait applies. It is not fixed here and not named in the PR (finding 5).
- The other save/restore sites use the `min` rule correctly. `V3ReplicationProtocol.java:124-129` guards `previousTimeOut > 0`. `PGStream.java:201-210` restores in `finally` (see taste T2).
- `enableSSL` has one caller, `tryConnect` at line 168.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | `sslResponseTimeout=0` with `socketTimeout>0` leaves `SO_TIMEOUT` at 0, so the SSL wait is unbounded and the socket timeout is bypassed. The comment at 538 says "smaller timeout". | substantive | `ConnectionFactoryImpl.java:538-545` | Treat 0 as "no bound" explicitly, so `socketTimeout` still applies when it is set. Follow the `V3ReplicationProtocol.java:124-129` pattern. Add a test for the 0 case. |
| 2 | A negative value passes `getInt`, and `setSoTimeout` throws `IllegalArgumentException`, which escapes `getConnection` as an unchecked exception. | substantive | `ConnectionFactoryImpl.java:535,545`; `PGProperty.java:679-682` | Reject negatives with a `PSQLException` naming the property, and test `-1`. |
| 3 | The docs do not state the effective wait (`min` with `socketTimeout`), that `loginTimeout` caps it (values above `loginTimeout * 1000` have no effect), or that the 5000 default applies to every SSL connection. "The timeout … that we wait" has no condition. | substantive | `docs/documentation/head/connect.md:330-332`; `README.md:121`; `PGProperty.java:674-682` | State the three facts. Add a boundary test with `sslResponseTimeout` just past `loginTimeout * 1000`. |
| 4 | The `SSL_RESPONSE_TIMEOUT` javadoc first sentence describes why, not what the property does. "without a timeout here" is unclear, and "reset after" is unfinished. | substantive | `PGProperty.java:674-678` | Make the first sentence state what the property bounds. Finish or drop the reset sentence. |
| 5 | `enableGSSEncrypted` has the same unbounded `receiveChar()` wait. The change does not fix it and the PR does not name it. | substantive | `ConnectionFactoryImpl.java:470` | Fix it in this change, or name it as a follow-up in the PR description. |
| 6 | No test covers any claimed case, and the PR states no red run or mutation evidence. | substantive | none in the diff | Add a medium test beside `ConnectTimeoutTest` and `SocketTimeoutTest`, using a silent local `ServerSocket`. Assert failure within a bound, with the `SocketTimeoutException` as cause. Add the `N`-reply control. State the red run on the base commit in the PR. |
| T1 | The comment "We could do something tricky … pretty readable" narrates a discarded alternative. | taste | `ConnectionFactoryImpl.java:538-540` | Remove it, or keep only the first clause, which states the rule. |
| T2 | The timeout restore at 554 is not in a `finally`, unlike `PGStream.java:201-210`. The stream is closed on `IOException` by `closeStream`, so this is not a live defect. | taste | `ConnectionFactoryImpl.java:554` | Use `try`/`finally` to match the sibling. |
| T3 | `connect.md` uses first-person "we", and the new entry is indented with four spaces where its siblings use a tab. | taste | `docs/documentation/head/connect.md:330-332` | Write "The driver waits…" or the equivalent, and use a tab. |
| T4 | Trailing whitespace after the README row. | taste | `README.md:121` | Strip it. |
| T5 | `set(properties,sslResponseTimeout)` has no space after the comma. Siblings use `, `. | taste | `BaseDataSource.java:372` | Add the space. |

Churn: none reported.

Not checked: the suite was not run, and nothing was built. The `IllegalArgumentException` in finding 2 comes from the JDK `Socket.setSoTimeout` contract, not from a run. The GSS sibling in finding 5 was read, not exercised against a server. The drift script does not parse the in-body comment at 538, so I read it directly. Doc-comment rules were applied without `javadoc-authoring`, which was not supplied.
