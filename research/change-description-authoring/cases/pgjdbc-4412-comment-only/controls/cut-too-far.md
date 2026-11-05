Since 42.7.13 (PR #4114), `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag, and two test names and these comments still describe it: the `State.ACTIVE` javadoc, the comment in `getConnection()`, and the javadoc of `recover_withAutoCommitFalse_doesNotOpenTransaction`. Two other comments contradicted the code beside them. The two tests are renamed after what they check.

Nothing changes at run time: with comments stripped, `PGXAConnection` is identical, and `XADataSourceTest` differs only in the two method names and three assertion messages.
