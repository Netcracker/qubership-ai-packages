## Final review: `6e453aa..HEAD` (sslResponseTimeout)

No previous report exists, so there is no table of prior findings. I read the diff whole and ran the drift script (`python3 -I comment-drift.py 6e453aa… HEAD`). Two of its three flags are false positives. `BaseDataSource.setConnectTimeout` (line 353) is tagged code-changed, but the hunk only inserts after its closing brace. `PGProperty.getName()` (line 811) is tagged comment-changed, but no hunk touches it. The `enableSSL` no-comment tag is correct: `ConnectionFactoryImpl.java:522` has no doc comment.

The main finding came from reading the code path, not from a run. I did not build or run the suite.

### Item 1: comments consistent with the code and with each other

Findings 5, 6, and 10 below. The `PGProperty` class comment (`PGProperty.java:21-24`) still holds. No comment in the change narrates the change with `now`, `no longer`, or `used to`.

### Item 2: claimed cases covered

Claimed cases, none with a test:
- The property exists, defaults to 5000, and is configurable (`PGProperty.java:679-683`). Only the generic `PGPropertyTest` loops (`testGetSetAllProperties`, `testSortOrder`, `testEnumConstantNaming`) touch it, and they check no behavior.
- The SSL reply wait is bounded (`ConnectionFactoryImpl.java:545`). No test.
- The wait is the lesser of `socketTimeout` and this value (commit `574b763`, `ConnectionFactoryImpl.java:541-543`). No test.
- The socket timeout is restored after the reply (`:554`). No test.
- The `BaseDataSource` accessors (`BaseDataSource.java:357-373`) are claimed only by commit `27deb41`'s subject, not by the PR text. No test.

Command lines in the changed files: none.

Reverse check: every hunk belongs to a commit subject or to the PR sentence. The `BaseDataSource` hunk is the weakest claim, and I did not raise it as a finding.

### Item 3: boundaries, partitions, and the negative control

- Socket timeout unset, the default: the timeout does not fire. Finding 1.
- Value 0: unbounded wait. Finding 2.
- Negative value: uncaught `IllegalArgumentException`. Finding 3.
- Value above `socketTimeout`: the lesser-of path is the one the commit claims, and it has no case.
- Negative control: no case where the server answers `N` inside the timeout, and no case that stays green on the base commit.
- Pre-existing state: none. The setting is read from the URL and nothing is persisted.
- Other limits on the same work:
  - `loginTimeout` encloses the whole attempt (`Driver.java:289-298`). Its default is 0, so it is off by default.
  - `connectTimeout` covers only the TCP connect, not the SSL reply, so it does not enclose this work.
  - `socketTimeout` sits inside the work and is handled by the lesser-of rule, but only when it is set (`ConnectionFactoryImpl.java:113-114`).
  - Once finding 1 is fixed, the inner limit fires first at the defaults.
- No replacement mechanism, so no duration or output comparison is owed.

### Item 3a: level, placement, and environment

Finding 4. The behavior is observable with a local `ServerSocket` that accepts and never answers the 8-byte SSLRequest. No PostgreSQL server is needed, so the test belongs at medium level. `ConnectTimeoutTest` (`pgjdbc/src/test/java/org/postgresql/test/jdbc2/`) is the sibling, but it uses an unroutable IP and is not hermetic. The new test should sit beside it and not copy that approach.

### Item 4: names by content

None. The new names are not positional, and no test names exist.

### Item 5: failure report

None. The change adds no assertions.

### Item 6: what the writer says it verified

Not stated. The PR text and the commit bodies mention no test run, no red run on the base commit, and no mutation verdict. A default-settings test would have failed on the current code (finding 1), so the absence of a red run is what let it through.

### Item 7: siblings of the change

- `enableSSL` has one call site (`ConnectionFactoryImpl.java:168`).
- The flag-aware timeout path has siblings: `tryConnect` (`ConnectionFactoryImpl.java:113-114`) and `QueryExecutorImpl.setSocketTimeout` (`QueryExecutorImpl.java:831-835`) both use `PGStream.setNetworkTimeout`. The new code is the odd one out (finding 1).
- The GSS encryption request has the same unbounded read (`ConnectionFactoryImpl.java:470`). Finding 7.
- Property lists that name the setting: `README.md:121` and `connect.md:330-332`. A grep for `connectTimeout` found no other list, so no list omits the new member.
- No prose counts the set's size.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | With `socketTimeout` unset (the default), the SSL reply wait is unbounded. The raw `setSoTimeout` bypasses the `timeoutRequested` flag, so `readMore` swallows the `SocketTimeoutException` and `ensureBytes` loops. Only `socketTimeout > 0` fires. | Substantive | `ConnectionFactoryImpl.java:545, 554`; `PGStream.java:743-745`; `VisibleBufferedInputStream.java:125-134, 165-171` | Use `pgStream.setNetworkTimeout(...)` for both the set and the restore, as `QueryExecutorImpl.setSocketTimeout` does. Add the default-settings test in #4, which fails on the current code. |
| 2 | `sslResponseTimeout=0` yields `setSoTimeout(0)`, which is infinite, even when `socketTimeout` is set. This contradicts the lesser-of claim. The docs do not say what 0 means. | Substantive | `ConnectionFactoryImpl.java:541-545`; `connect.md:330-332` | Either reject non-positive values with a `PSQLException` that names the property, or define 0 as "use `socketTimeout`" and state it in the docs and the comment. Add the 0 case to the tests. |
| 3 | A negative value reaches `Socket.setSoTimeout` and throws a raw `IllegalArgumentException`. `getInt` does no sign check, and no caller catches `RuntimeException` on this path. | Substantive | `ConnectionFactoryImpl.java:545`; `PGProperty.java:909-918` | Validate the sign and throw a `PSQLException` naming the property. Add the negative case. |
| 4 | No test covers any claim, and no red run or mutation verdict is stated. | Substantive | Test location: `pgjdbc/src/test/java/org/postgresql/test/jdbc2/` beside `ConnectTimeoutTest.java` | Add a medium test with a local `ServerSocket` that accepts and never replies. Cases: socket timeout unset; socket timeout below and above the setting; 0; negative. Add a control where the server answers `N` inside the timeout, which stays green on the base commit. Name the red run on the base commit in the PR. |
| 5 | The `PGProperty` Javadoc's first sentence does not state what the property does. It also omits the lesser-of rule and the 0 behavior. | Substantive | `PGProperty.java:675-678` | Open with what the property sets, for example: "Milliseconds to wait for the server's reply to an SSL request." Then state the lesser-of rule and the 0 behavior. Move the history sentence after it. |
| 6 | The docs and README state the wait as if it were exactly this value. A reader with `socketTimeout=2` would expect 5 s. The docs also omit the default and the 0 behavior. | Substantive | `connect.md:330-332`; `README.md:121` | State the effective wait (the lesser of this and `socketTimeout`), the default, and the 0 behavior. |
| 7 | The GSS encryption request waits for a reply with no timeout, the same unbounded read as the SSL request. The PR does not name it. | Substantive | `ConnectionFactoryImpl.java:470` | Fix it in this change, or name it as a follow-up in the PR description. |
| 8 | The default of 5000 now caps the SSL reply on every SSL connection with `socketTimeout` unset, which is a behavior change the PR text does not mention. | Taste | `PGProperty.java:679-683` | State the default and its scope in the PR description. |
| 9 | When the timeout fires, the user gets "The connection attempt failed." with a `SocketTimeoutException` cause. The message does not name the property. | Taste | `ConnectionFactoryImpl.java:331` | Name the property in the message, or wrap the timeout in a message that does. |
| 10 | The new inline comment opens with a fragment, omits the `currentTimeout > 0` case, and narrates a rejected alternative. | Taste | `ConnectionFactoryImpl.java:538-540` | State what the code does: when `socketTimeout` is set and shorter, its value is used. Drop the alternative. |

The drift script's false positives are not findings.

Not checked: I did not build or run anything, so finding 1 rests on reading the code path and needs the test in #4 to confirm it. `javadoc-authoring` and the `test-authoring` reference files were not among the provided skills, so the doc-comment and assertion-library rules were checked only against the form and the two loaded skills.
