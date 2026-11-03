Since 42.7.13 (PR #4114), `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag, and comments in `PGXAConnection` and `XADataSourceTest` and two test names still describe it. Two comments also contradicted the code beside them: the `recover()` comment said PostgreSQL requires the user to own a prepared transaction, where the query keeps the rows for which `pg_has_role(current_user, owner, 'member')`; and a batch test called the receive-buffer limit 64 KB, where `MAX_BUFFERED_RECV_BYTES` is `64000`.

`restoreOfAutoCommit` and `restoreOfAutoCommitEndThenJoin` become `onePhaseBranch_leavesAutoCommitUnchanged` and `endThenJoinBranch_leavesAutoCommitUnchanged`.

Nothing changes at run time: with comments stripped, `PGXAConnection` is identical, and `XADataSourceTest` differs only in the two method names and three assertion messages.
