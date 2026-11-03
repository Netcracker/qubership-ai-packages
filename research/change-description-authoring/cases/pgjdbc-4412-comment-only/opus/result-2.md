Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)). Comments in `PGXAConnection` and `XADataSourceTest` still describe the old behavior, and three of them state the opposite of what the code does:

* The `State.ACTIVE` javadoc says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false any more.
* The comment in `getConnection()` describes the `autoCommit=false` branch that PR #4114 deleted.
* `XADataSourceTest` quotes `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message was removed by the fix. It also came from `commitPrepared`, not from `recover()`.

Two other comments contradicted the code next to them. The `recover()` comment said that PostgreSQL requires the user to *own* a prepared transaction, but the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`. A batch test gave the receive-buffer limit as 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The rest of the first commit only rewords comments. The second commit renames `restoreOfAutoCommit` and `restoreOfAutoCommitEndThenJoin`, and rewrites their assertion messages, because both named the save-and-restore that no longer exists.

Nothing changes at run time. I parsed both files with comments discarded, and they are identical before and after the first commit. After the second commit, the only non-comment changes are the two method names and three message literals. There is no changelog entry because users can't observe any of this.

**Scope.** I left two things as they are:

* `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement. Its old comment said it silenced an unused-variable warning, but Error Prone is disabled for `compileTestJava`. I corrected the comment and kept the statement, since removing it would be a code change.
* The javadoc on the `conn` field in `PGXAConnection` still lists three of the SQL commands the field is used for. The class javadoc now covers every statement, and the list doesn't contradict it.
