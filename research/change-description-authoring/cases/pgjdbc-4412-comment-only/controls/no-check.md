Since 42.7.13 (PR #4114), `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag, and two test names and these comments still describe it: the `State.ACTIVE` javadoc, the comment in `getConnection()`, and the javadoc of `recover_withAutoCommitFalse_doesNotOpenTransaction`. Two comments also contradicted the code beside them: the `recover()` comment, against the `pg_has_role(current_user, owner, 'member')` filter of its query, and the javadoc of `batchProgressNotSecuredWithinXaBranch`, against `MAX_BUFFERED_RECV_BYTES`, which is `64000`.

`restoreOfAutoCommit` and `restoreOfAutoCommitEndThenJoin` become `onePhaseBranch_leavesAutoCommitUnchanged` and `endThenJoinBranch_leavesAutoCommitUnchanged`.

Nothing changes at run time.
