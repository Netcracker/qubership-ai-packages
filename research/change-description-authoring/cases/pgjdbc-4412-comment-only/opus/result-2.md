Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)). Comments in `PGXAConnection` and `XADataSourceTest` still describe the old behavior, and five of them contradict the code:

- `State.ACTIVE` says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false any more, and the class javadoc says the opposite.
- The comment in `getConnection()` describes the `autoCommit=false` branch that #4114 deleted.
- `XADataSourceTest` quotes `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message went out with the fix, and it came from `commitPrepared`, not from `recover()`.
- The `recover()` comment says PostgreSQL requires the user to *own* a prepared transaction. The `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`.
- A batch test calls the receive-buffer limit 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The first commit corrects these five, and the rest of its edits are wording. It removes history told in the present tense, branches the code does not have, positional references, and symbols used in place of words. The class javadoc used to list the XA statements. It now states that every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, so the text stays accurate when a new statement is added. The `QUERY_SUPPRESS_BEGIN` rationale now appears once in the class javadoc instead of at four call sites.

With comments discarded, both files parse identically before and after the first commit. Across both commits, the only change outside comments is the second commit. It renames `restoreOfAutoCommit` to `onePhaseBranch_leavesAutoCommitUnchanged` and `restoreOfAutoCommitEndThenJoin` to `endThenJoinBranch_leavesAutoCommitUnchanged`, and it rewrites three assertion messages. All of them referred to the save-and-restore that no longer happens.

**Scope.** I hadn't planned to change `State.ACTIVE` or the `getConnection()` comment. I edited them because the class javadoc I rewrote contradicts them in the same file. Should I keep those two hunks or drop them? I left two things alone on purpose:
- `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement. Its comment claimed it silenced an unused-variable warning, but Error Prone is off for `compileTestJava`. I removed the claim and kept the statement, because deleting it would be a code change.
- The javadoc on the `conn` field lists three of the SQL commands it runs. The new class javadoc covers this without contradicting it.

No changelog entry, since users can't observe any of this.
