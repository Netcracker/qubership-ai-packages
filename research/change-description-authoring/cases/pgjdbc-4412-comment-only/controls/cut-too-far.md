Since 42.7.13 (PR #4114), `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag, and comments in `PGXAConnection` and `XADataSourceTest` and two test names still describe it. Two other comments contradicted the code beside them. The two tests are renamed after what they check.

Nothing changes at run time: with comments stripped, `PGXAConnection` is identical, and `XADataSourceTest` differs only in the two method names and three assertion messages.
