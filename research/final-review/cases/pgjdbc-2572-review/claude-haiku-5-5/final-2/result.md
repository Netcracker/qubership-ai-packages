## Final review: `6e453aa..HEAD`, SSL response timeout

Loaded `test-authoring` and `english-developer-style` from the skills directory. `javadoc-authoring` is not in that directory, so the Javadoc rules were not applied from a loaded skill. The comments were checked against the Javadoc conventions visible in neighboring code and against `english-developer-style` §4 to §5. The drift script ran. Its `getName() comment-changed` tag is a parse artifact: the PGProperty hunk only adds the enum constant, and the `getName` comment is untouched. The previous-report table does not apply, since this is the first review.

### Item 1: comments consistent with the code and with each other

Finding 7 and finding 8 below. The `BaseDataSource` getter and setter have an empty first line in Javadoc and no sentence before the `@return` or `@param` tag. Their siblings at lines 330 to 355 use the same shape, so this is consistent and not a finding. The `connect.md` and README entries omit the cap by `socketTimeout` and the meaning of 0 and negative values, which is finding 1 and finding 3. No comment says "now", "no longer", or "used to".

### Item 2: claimed cases covered

The task statement, commit messages, and comments claim these cases. None has a test, because the diff contains no test file:
- The timeout is set before the request and restored after the response.
- The effective timeout is the lesser of `sslResponseTimeout` and a non-zero `socketTimeout`.
- The property name and default of 5000 ms.
- The `BaseDataSource` getter and setter.

Finding 5.

### Item 3: boundaries, partitions, and the negative control

No boundary or control is tested. Partitions the tests would need: 0, a negative value, a value just above and just below `socketTimeout`, and `socketTimeout` of 0. The control is `sslmode=disable` or `allow`, which sends no request and should stay unchanged.

Limits on the same work:
- `sslResponseTimeout`: the new value, default 5000 ms, per request. `ConnectionFactoryImpl.java:535-545`.
- `socketTimeout`: documented, in seconds, default 0. It caps the new value when non-zero. `ConnectionFactoryImpl.java:535-540`. Finding 1.
- `loginTimeout`: documented, in seconds, default 0. `Driver.java:283-298` abandons the attempt after this time while the connect thread keeps running. It is an outer limit on the same work, and it caps the new value. Finding 2.
- `connectTimeout`: default 10 s. It applies to the TCP connect. I did not find that it bounds the SSL reply, but I did not trace every use.

Pre-existing state: the change reads no persisted state, so there is nothing to test there.

Failure path: `openConnectionImpl` closes the stream on any exception (`ConnectionFactoryImpl.java` catch block after the `newStream` try), so the timeout not being reset on the exception path does no harm today. Finding 9.

Findings 1, 2, and 3.

### Item 3a: level, placement, and the environment

The timed read is observable only across a socket. The smallest level that observes it is medium: a `ServerSocket` on the local machine that accepts and never answers the SSL request, which needs no external server. Put it beside the neighbors `SocketTimeoutTest` and `ConnectTimeoutTest` in `pgjdbc/src/test/java/org/postgresql/test/jdbc2/`. The `BaseDataSource` accessors can use a small test. I did not check the `ds` subclasses beyond `BaseDataSource`.

Finding 5.

### Item 4: names by content, not by position

None. The names `sslTimeout`, `currentTimeout`, and `SSL_RESPONSE_TIMEOUT` name their content. The phrase "without a timeout here" in `PGProperty.java:676` refers to the driver, not to a position in the text.

### Item 5: the failure report

None. The change adds no assertions. The tests that finding 5 asks for should assert the operands, for example `assertEquals(expected, actual)` on the elapsed bound or on `getSoTimeout()`.

### Item 6: what the writer says it verified

Neither a red run on the base commit nor a mutation verdict is stated in the change or in the task statement. Finding 6.

### Item 7: siblings of the change

- `enableGSSEncrypted`, `ConnectionFactoryImpl.java:462-470`, sends the same request and waits on `receiveChar()` with no timeout. The same defect applies. Finding 4.
- `PGStream.java:200-211` restores the socket timeout in a `finally`. The new code restores it only on normal return. Finding 9.
- `setSoTimeout` call sites I did not read: `QueryExecutorImpl.java:780-830` and `V3ReplicationProtocol.java:133`.
- The new `connect.md` and README rows are the only other property lists that carry the setting. `ds` subclasses beyond `BaseDataSource` were not checked.

### Sorted findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | The docs do not say that a non-zero `socketTimeout` caps `sslResponseTimeout`. Raising the setting past it has no effect and no warning. | substantive | `docs/documentation/head/connect.md:330-332`, `README.md:121`, `PGProperty.java:676-682` | State the cap in the `connect.md` entry and in the README row, or derive one limit from the other. Test a value just above `socketTimeout`. |
| 2 | `loginTimeout` is an outer limit on the same work. If it is shorter than `sslResponseTimeout`, the caller sees the login timeout and the SSL wait is cut off. | substantive | `Driver.java:283-298`, `Driver.java:704-714` | Document the pair. Add a case with `loginTimeout` below `sslResponseTimeout` that asserts which limit fires. |
| 3 | A value of 0 with `socketTimeout` 0 sets `SO_TIMEOUT` to 0, which means infinite wait, the hang the change exists to prevent. A negative value makes `Socket.setSoTimeout` throw `IllegalArgumentException`, which is not a `PSQLException`. Neither case is documented or tested. | substantive | `ConnectionFactoryImpl.java:535-545` | Reject or clamp 0 and negative values through a `PSQLException` path, as `getInt` does for non-integers. Document the rule. Test 0, -1, and 1. |
| 4 | The GSS encryption request has the same unbounded request-and-wait. It is reached whenever `gssEncMode` is `prefer` or `require`. | substantive | `ConnectionFactoryImpl.java:462-470` | Apply the same timeout in the same change, or name the GSS path as a follow-up in the pull request description. |
| 5 | No test covers any claimed case. There are no tests in the diff for the timeout ordering, the minimum rule, the default, or the accessors. | substantive | `ConnectionFactoryImpl.java:535-554`, `BaseDataSource.java:357-374` | Add a medium test with a local silent `ServerSocket` that asserts the failure within `sslResponseTimeout` and that the socket timeout is restored after a successful reply. Add cases for the minimum rule. Add a small test for the accessors. |
| 6 | The change states no red run on the base commit and no mutation verdict. | substantive | change description | State the red run on `6e453aa` or the test-first commit that shows it. |
| 7 | The first sentence of the enum Javadoc narrates a report and does not say what the constant does. It is a comma splice, and "there are reports of" is a vague attribution. | substantive | `PGProperty.java:675-677` | Make the first sentence state what the constant bounds, for example "bounds the wait for the server's reply to an SSL request." |
| 8 | The inline comment reads "if the current timeout is less than sslTimeout", so 0 reads as less. The guard excludes 0 with `currentTimeout > 0`. | substantive | `ConnectionFactoryImpl.java:535-537` | Say that the rule applies only when the socket has a timeout set. |
| 9 | The timeout is restored only on normal return, not in a `finally` as the sibling in `PGStream.java:200-211` does. It does no harm today, because the stream is closed on failure. | taste | `ConnectionFactoryImpl.java:553-554` | Restore in a `finally`, so the "reset after" claim holds on every path. Expect this to be declined, since the stream is closed. |
| 10 | The `connect.md` entry uses four spaces where its siblings use a tab. The phrase "we wait" names the driver less clearly than "the driver waits." | taste | `connect.md:330-332`, `PGProperty.java:681` | Match the tab indentation and name the driver as the actor. |
| 11 | The README row has trailing whitespace, which `git diff --check` flags. | taste | `README.md:121` | Remove the trailing spaces. |
| 12 | The `BaseDataSource` Javadoc has an empty first line the siblings lack. The setter is missing the space after the comma that its sibling has. | taste | `BaseDataSource.java:357-374` | Match the sibling form at lines 330 to 355. |
| 13 | A timeout surfaces as the socket's own read-timeout exception. I did not trace how the caller wraps it. If the wrapper does not name `sslResponseTimeout`, the reader cannot find the knob. | taste | `ConnectionFactoryImpl.java:548-552` | Check the wrapped message and, if it names no property, name `sslResponseTimeout` in it. |

No churn items were found.

**Not checked:** I did not build the project or run its tests. The `javadoc-authoring` rules were not applied from a loaded skill, since that skill is not in the directory. The drift script's parse is approximate. I did not read the `QueryExecutorImpl` timeout sites or the `ds` subclasses beyond `BaseDataSource`.
