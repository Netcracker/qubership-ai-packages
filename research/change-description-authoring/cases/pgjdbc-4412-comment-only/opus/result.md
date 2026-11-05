Since 42.7.13 ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)), `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag. Comments in `PGXAConnection` and `XADataSourceTest` still describe the behavior that PR #4114 removed. Three of them state the opposite of what the code does:

- `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false any more, and the class javadoc says the opposite.
- The comment in `getConnection()` describes the `autoCommit=false` branch that PR #4114 deleted.
- `XADataSourceTest` quotes `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message went out with the fix. It also came from `commitPrepared`, not from `recover()`, where the comment placed it.

Two more contradict the code beside them. The `recover()` comment says PostgreSQL requires the user to *own* a prepared transaction, but the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`. A batch test calls the receive-buffer limit 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The rest of the first commit changes only wording. It removes history narrated in the present tense, branches the code does not have, positional references, and symbols used in place of words. The class javadoc used to list the XA statements. It now states the rule that every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, so the list cannot go stale. It also explains `QUERY_SUPPRESS_BEGIN` once, where four call sites used to repeat the explanation. The second commit renames `restoreOfAutoCommit` to `onePhaseBranch_leavesAutoCommitUnchanged` and `restoreOfAutoCommitEndThenJoin` to `endThenJoinBranch_leavesAutoCommitUnchanged`, along with their assertion messages, because both names referred to the save-and-restore that no longer exists.

Nothing changes at run time, so this has no changelog entry. With comments stripped, both files parse identically before and after the first commit. Across both commits, the only non-comment changes are the two method names and three message literals in `XADataSourceTest`.

**Scope.** I hadn't planned to edit `State.ACTIVE` or the `getConnection()` comment. I changed them because the rewritten class javadoc in the same file contradicts them. Should those two hunks stay in this pull request, or should I drop them?

I deliberately left two things unchanged:
- `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement. Its old comment said it silenced an unused-variable warning, but Error Prone is disabled for `compileTestJava`. I removed the false claim and kept the statement, because deleting it is a code change.
- The `conn` field javadoc still lists three of the SQL commands it is used for. The class javadoc's rule supersedes that list but does not contradict it.
