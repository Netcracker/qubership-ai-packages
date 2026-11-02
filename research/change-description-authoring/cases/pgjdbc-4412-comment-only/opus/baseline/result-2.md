Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)). Comments in `PGXAConnection` and `XADataSourceTest` still describe the old behavior, and three of them say the opposite of what the code does:

- `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection", but nothing sets it to false any more.
- The comment in `getConnection()` describes the `autoCommit=false` branch that PR #4114 deleted.
- `XADataSourceTest` quotes `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message was removed with the fix, and it came from `commitPrepared`, not from `recover()`.

Two more comments contradicted the code next to them. The `recover()` comment said PostgreSQL requires the user to *own* a prepared transaction, but the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`. A batch test called the receive-buffer limit 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The first commit corrects these. The other comment edits only change wording: they remove history told in the present tense, branches the code does not have, positional references, and symbols used in place of words. The class javadoc used to list the XA statements. It now states that every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, so adding a statement can't make it stale. The `QUERY_SUPPRESS_BEGIN` rationale is now stated once in the class javadoc instead of at four call sites. The second commit renames `restoreOfAutoCommit` to `onePhaseBranch_leavesAutoCommitUnchanged` and `restoreOfAutoCommitEndThenJoin` to `endThenJoinBranch_leavesAutoCommitUnchanged`, along with their assertion messages, because both names referred to the removed save-and-restore.

Nothing changes at run time, so there is no changelog entry. With comments discarded, both files parse identically before and after the first commit. Across both commits, the only non-comment changes are the two method names and three message literals in `XADataSourceTest`.

I didn't plan to touch `State.ACTIVE` or the `getConnection()` comment. I edited them because the rewritten class javadoc contradicts them. Do you want me to drop those two hunks?

Two things are deliberately left as they are:

- **`Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit`:** this statement has no effect. Its old comment claimed it silenced an unused-variable warning, but Error Prone is disabled for `compileTestJava`. I corrected the comment and kept the statement, because deleting it would be a code change.
- **The `conn` field javadoc:** it still lists three of the SQL commands the field is used for. The class javadoc's rule now covers this, but the two don't contradict each other.
