Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)). Comments in `PGXAConnection` and `XADataSourceTest` still describe the old behavior, and three of them say the opposite of what the code does:

* `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection", but nothing sets it to false any more.
* The comment in `getConnection()` describes the `autoCommit=false` branch that PR #4114 deleted.
* `XADataSourceTest` quotes `"2nd phase commit must be issued using an idle connection"` as a current precondition. That message was removed by the same fix, and it came from `commitPrepared`, not from `recover()`.

Two more comments contradicted the code next to them. The `recover()` comment said PostgreSQL requires the user to *own* a prepared transaction, but the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`. A batch test called the receive-buffer limit 64 KB, but `MAX_BUFFERED_RECV_BYTES` is 64000.

The first commit fixes these comments and rewords the rest of the XA comments. The class javadoc no longer lists the XA statements, because that list would go stale the next time a statement is added. It now says that every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`. It also explains `QUERY_SUPPRESS_BEGIN` once, so the four call sites that repeated the explanation no longer do. The second commit renames `restoreOfAutoCommit` and `restoreOfAutoCommitEndThenJoin`, and the assertion messages in them, which referred to the old save-and-restore. Neither old name is referenced outside its declaration.

The `State.ACTIVE` and `getConnection()` hunks go beyond the comments I meant to fix. I changed them because the rewritten class javadoc in the same file contradicts them. I can drop those two hunks if you prefer.

Nothing changes at run time. I parsed both files with comments discarded, and they are identical before and after the first commit. Across both commits, only comments change in `PGXAConnection`. In `XADataSourceTest`, the only changes outside comments are the two method names and three message literals.

There is no changelog entry, because no user can observe the change. I left two things as they are:

* `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` does nothing. Its old comment said it silenced an unused-variable warning, but Error Prone is disabled for `compileTestJava`. I removed that claim and kept the statement, because deleting it would change code.
* The javadoc on the `conn` field still lists three of the SQL commands the field is used for. The class javadoc's rule covers those commands and doesn't contradict the list.
