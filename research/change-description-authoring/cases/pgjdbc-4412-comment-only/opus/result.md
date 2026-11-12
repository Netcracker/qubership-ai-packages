Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)). Comments in `PGXAConnection` and `XADataSourceTest` still describe that behavior, and three of them contradict the code:

* `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false anymore, and the class javadoc says the opposite.
* The comment in `getConnection()` describes the `autoCommit=false` branch that PR #4114 deleted.
* `XADataSourceTest` quotes `2nd phase commit must be issued using an idle connection` as a live precondition. That message was removed with the fix. It also came from `commitPrepared`, not from `recover()`, where the comment placed it.

Two other comments contradicted the code next to them. The `recover()` comment said PostgreSQL requires the user to *own* a prepared transaction, but the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`. A batch test called the receive-buffer limit 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The first commit corrects these comments. Its other edits are wording: past behavior described in the present tense, branches the code doesn't have, positional references, and symbols used in place of words. The class javadoc no longer lists the XA statements. Instead, it states that every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, because a list would go stale when the next statement is added. The `QUERY_SUPPRESS_BEGIN` rationale now appears once in the class javadoc, and four call sites drop their copies. The second commit renames `restoreOfAutoCommit` to `onePhaseBranch_leavesAutoCommitUnchanged` and `restoreOfAutoCommitEndThenJoin` to `endThenJoinBranch_leavesAutoCommitUnchanged`. It also rewrites the three assertion messages in those tests, which still referred to the old save-and-restore.

Nothing changes at run time. I parsed both files with comments discarded, before and after the first commit, and the results are identical. Across both commits, the only non-comment changes are the two method names and three message literals in `XADataSourceTest`.

**Scope.** This needs no changelog entry because users can't observe any of it. I left two things as they are:
* `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement. Its old comment said it silenced an unused-variable warning, but Error Prone is disabled for `compileTestJava`. I corrected the comment and kept the statement, since deleting it would be a code change.
* The javadoc on `PGXAConnection`'s `conn` field still lists three of the SQL commands the field is used for. The new class javadoc covers them without contradicting it.
