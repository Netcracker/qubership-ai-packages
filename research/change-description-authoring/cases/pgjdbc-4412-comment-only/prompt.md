# Task

A maintainer called the pull request description below too long for the change. Rewrite it, in Markdown, ready to
paste into GitHub. The facts in it were checked against the code; treat every fact as verified, and add none that
neither it, the commit messages, nor the diff carries.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template is used. The pull request lives on the target repository and has two commits.
  `git merge-base origin/master HEAD` is `e650e24ead2a3a43aed862cb7b59ceba1a7cceec`; the head commit is
  `168156e6296195b68242a359c2ded5933b3c0466`.
- CI runs the full test suite, the XA tests included, against a PostgreSQL server on every pull request.
- Files changed: `pgjdbc/src/main/java/org/postgresql/xa/PGXAConnection.java` +39 -47,
  `pgjdbc/src/test/java/org/postgresql/test/xa/XADataSourceTest.java` +74 -74.
- PR #4114 shipped in 42.7.13.

## The description

````markdown
### Why

Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)), and a number of comments in `PGXAConnection` and `XADataSourceTest` still describe the behavior that change removed. Three are wrong rather than merely dated, and a reader who trusts them reaches the opposite of what the code does:

* `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false any more, and the class javadoc three hundred lines above now says the opposite.
* The comment in `getConnection()` described the `autoCommit=false` branch that the same change deleted.
* `XADataSourceTest` quoted `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message went out with the fix, and it also came from `commitPrepared`, not from `recover()` where the comment placed it.

Two more claims contradicted the code beside them: the `recover()` comment said PostgreSQL requires the user to *own* a prepared transaction, where the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`; and a batch test called the receive-buffer limit 64 KB, where `MAX_BUFFERED_RECV_BYTES` is 64000.

### What

Two commits, both confined to `PGXAConnection` and `XADataSourceTest`.

The first corrects the comments. Beyond the five factual repairs above, the edits are wording: history narrated in the present tense (`no longer`, `the new contract`), counterfactual branches the code does not have, positional references (`above`, `below`, `the latter`), notation standing in for words (`+`, `/`, `→`), and the enumerated list of XA SQL statements in the class javadoc, which a criterion replaces — every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, so the list would go stale the next time one is added. It also drops the `QUERY_SUPPRESS_BEGIN` rationale from four call sites, where the class javadoc now carries it once.

`State.ACTIVE` and the `getConnection()` comment were not in the set I set out to sweep. I edited them because the class javadoc I had just rewritten contradicts them in the same file; say the word and I will drop those two hunks.

The second commit renames two tests and the assertion messages under them, which named the same vanished save-and-restore:

| Old | New |
| --- | --- |
| `restoreOfAutoCommit` | `onePhaseBranch_leavesAutoCommitUnchanged` |
| `restoreOfAutoCommitEndThenJoin` | `endThenJoinBranch_leavesAutoCommitUnchanged` |

### Verification

No behavior changes, so the evidence is that none could have. Both files were parsed with comments discarded before and after the first commit and compare identical, so that commit is mechanically comment-only; across both commits `PGXAConnection` is still comment-only, and the only non-comment delta in `XADataSourceTest` is the two method names and three message literals. `compileJava`, `compileTestJava`, `checkstyleMain`, `checkstyleTest`, and `autostyleJavaCheck` are green. Neither old test name is referenced outside its declaration. The XA suite itself was not run; it needs a server with `max_prepared_transactions > 0`.

### Scope

No changelog entry: nothing here is observable to a user.

Two things I found and deliberately left alone. `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement whose old comment claimed it silenced an unused-variable warning; Error Prone is disabled for `compileTestJava`, so nothing in this build needs it. I removed the false claim and left the statement, since deleting it is a code change. And `PGXAConnection`'s `conn` field javadoc still lists three of the SQL commands it is used for, which the class javadoc's criterion now supersedes; it is not contradictory, so I left it.
````

## The commit messages

````text
docs(xa): correct XA comments left behind by the autoCommit change

Since 42.7.13 PGXAConnection no longer saves and restores the caller's
autoCommit flag (PR #4114), and comments in PGXAConnection and
XADataSourceTest still describe the behavior that change removed.
State.ACTIVE says "autoCommit is false on a connection returned by
getConnection", and nothing sets it to false any more; the getConnection()
comment describes the deleted branch; and the test quotes "2nd phase commit
must be issued using an idle connection" as a live precondition, though that
message went out with the fix and no build of the driver emits it.

Two further claims contradicted the code beside them. The recover() comment
said PostgreSQL requires the user to own a prepared transaction, where the
WHERE clause filters on pg_has_role(current_user, owner, 'member'). A batch
test called the receive-buffer limit 64 KB, where MAX_BUFFERED_RECV_BYTES
is 64000.

The remaining edits are wording: history narrated in the present tense,
counterfactual branches the code does not have, positional references, and
lists of call sites that a criterion replaces.

Nothing changes at run time. Both files parse identically with comments
stripped.


test(xa): rename the autoCommit tests after what they now check

restoreOfAutoCommit and restoreOfAutoCommitEndThenJoin, and the assertion
messages under them, name a save-and-restore that PGXAConnection stopped
doing in 42.7.13 (PR #4114). The tests themselves are correct: each sets
autoCommit, runs a branch to completion, and asserts the flag still holds
the value the caller set.

restoreOfAutoCommit becomes onePhaseBranch_leavesAutoCommitUnchanged, and
restoreOfAutoCommitEndThenJoin becomes
endThenJoinBranch_leavesAutoCommitUnchanged. The three messages that read
"XaResource should have restored connection autocommit mode ... to the
initial state" now name the value each case expects.

Neither name is referenced outside its declaration.


````

## The diff

````diff
diff --git a/pgjdbc/src/main/java/org/postgresql/xa/PGXAConnection.java b/pgjdbc/src/main/java/org/postgresql/xa/PGXAConnection.java
index c1926a990..7ffca7335 100644
--- a/pgjdbc/src/main/java/org/postgresql/xa/PGXAConnection.java
+++ b/pgjdbc/src/main/java/org/postgresql/xa/PGXAConnection.java
@@ -42,17 +42,16 @@
  *
  * <p>Two-phase commit requires PostgreSQL server version 8.1 or higher.</p>
  *
- * <p>XA-protocol SQL (BEGIN, PREPARE TRANSACTION, COMMIT, ROLLBACK, COMMIT PREPARED,
- * ROLLBACK PREPARED, and the recover() SELECT) is sent through
- * {@link org.postgresql.core.BaseConnection#execSQLUpdate(String) execSQLUpdate} /
+ * <p>Every statement this class issues goes through
+ * {@link org.postgresql.core.BaseConnection#execSQLUpdate(String) execSQLUpdate} or
  * {@link org.postgresql.core.BaseConnection#execSQLQuery(String) execSQLQuery}, both of which set
- * {@code QueryExecutor.QUERY_SUPPRESS_BEGIN}. As a result, the caller's JDBC {@code autoCommit}
- * flag is invariant across every {@code XAResource} call; the driver never prepends a {@code BEGIN}
- * of its own around XA SQL.</p>
+ * {@code QueryExecutor.QUERY_SUPPRESS_BEGIN}. The driver therefore prepends no {@code BEGIN} of its
+ * own, and the caller's JDBC {@code autoCommit} flag keeps its value across every
+ * {@code XAResource} call.</p>
  *
- * <p>{@link #getConnection()} is the exception: when {@code state == IDLE} it sets
- * {@code autoCommit=true} on the returned handle, because that path returns a JDBC handle in the
- * JDBC default state to the caller and is not part of the XA protocol.</p>
+ * <p>{@link #getConnection()} is the one exception. When {@code state == IDLE} it sets
+ * {@code autoCommit=true} on the handle it returns, since that handle is outside the XA protocol
+ * and {@code true} is the JDBC default.</p>
  *
  * @author Heikki Linnakangas
  */
@@ -91,10 +90,8 @@ public PGXAConnection(BaseConnection conn) throws SQLException {
   public Connection getConnection() throws SQLException {
     Connection conn = super.getConnection();
 
-    // When we're outside an XA transaction, autocommit
-    // is supposed to be true, per usual JDBC convention.
-    // When an XA transaction is in progress, it should be
-    // false.
+    // The handle starts at autoCommit=true only when no branch is open; inside a branch the
+    // caller's own value stands.
     if (state == State.IDLE) {
       conn.setAutoCommit(true);
     }
@@ -235,10 +232,9 @@ public void start(Xid xid, int flags) throws XAException {
           XAException.XAER_RMERR);
     }
 
-    // TMNOFLAGS opens a fresh server-side transaction with an explicit BEGIN sent below
-    // QUERY_SUPPRESS_BEGIN so the JDBC autoCommit flag is left alone. TMJOIN attaches to an existing
-    // (ended) branch, where BEGIN was already sent at the prior start(TMNOFLAGS) call, so no SQL is
-    // issued here.
+    // TMNOFLAGS opens a fresh server-side transaction with an explicit BEGIN. TMJOIN attaches to an
+    // existing branch that end() left behind, where the prior start(TMNOFLAGS) already sent that
+    // BEGIN, so this path issues no SQL.
     if (flags == TMNOFLAGS) {
       try {
         conn.execSQLUpdate("BEGIN");
@@ -361,10 +357,10 @@ public int prepare(Xid xid) throws XAException {
       String s = RecoveredXid.xidToString(xid);
       conn.execSQLUpdate("PREPARE TRANSACTION '" + s + "'");
     } catch (SQLException ex) {
-      // Mutate XA state only after PREPARE TRANSACTION succeeds. On failure state stays ENDED with
-      // currentXid set, so the transaction manager can recover by calling rollback(xid) — which
-      // takes the active-branch path and issues a plain ROLLBACK against the still-open server
-      // transaction.
+      // The XA state changes only after PREPARE TRANSACTION succeeds, so a failure leaves state at
+      // ENDED with currentXid set. The transaction manager can then recover by calling
+      // rollback(xid), which takes the active-branch path and issues a plain ROLLBACK against the
+      // still-open server transaction.
       throw new PGXAException(GT.tr("Error preparing transaction. prepare xid={0}", xid), ex, mapSQLStateToXAErrorCode(ex));
     }
 
@@ -416,13 +412,11 @@ public Xid[] recover(int flag) throws XAException {
       return new Xid[0];
     }
 
-    // execSQLQuery passes QUERY_SUPPRESS_BEGIN, so this SELECT never causes pgjdbc to prepend a
-    // BEGIN regardless of the caller's autoCommit setting. If the caller has a local transaction
-    // already open on this connection, the SELECT runs inside it as a metadata read; it does not
-    // extend or close the caller's transaction.
+    // A local transaction that the caller already opened on this connection stays open across this
+    // SELECT, which runs inside it as a metadata read.
     //
-    // PostgreSQL requires the user to own the transaction in order to successfully execute COMMIT
-    // PREPARED or ROLLBACK PREPARED, so the WHERE clause filters by current_user.
+    // PostgreSQL restricts COMMIT PREPARED and ROLLBACK PREPARED to the transaction's owner, so
+    // the WHERE clause keeps only the rows for which pg_has_role(current_user, owner, 'member').
     // See https://github.com/postgres/postgres/blob/15afb7d61c142a9254a6612c6774aff4f358fb69/src/backend/access/transam/twophase.c#L583C32-L599
     try (ResultSet rs = conn.execSQLQuery(
         "SELECT gid FROM pg_prepared_xacts where database = current_database() and pg_has_role(current_user, owner, 'member')")) {
@@ -468,15 +462,15 @@ public void rollback(Xid xid) throws XAException {
 
     try {
       if (currentXid != null && currentXid.equals(xid)) {
-        // Active branch: ROLLBACK closes the server transaction that start() opened. Use the
-        // QUERY_SUPPRESS_BEGIN path so it works regardless of the caller's autoCommit, and so it
-        // accepts a connection that is in TransactionState.FAILED (PG accepts ROLLBACK there).
+        // The branch is still active, so a plain ROLLBACK closes the server transaction that
+        // start() opened. The server accepts ROLLBACK inside an aborted transaction block, so this
+        // path works when the driver's state is TransactionState.FAILED too.
         conn.execSQLUpdate("ROLLBACK");
         state = State.IDLE;
         currentXid = null;
       } else {
-        // Prepared branch: ROLLBACK PREPARED is not allowed inside a transaction block. Refuse
-        // upfront rather than commit/rollback the caller's local transaction silently. XAER_RMFAIL
+        // The branch was prepared, and PostgreSQL rejects ROLLBACK PREPARED inside a transaction
+        // block. Refusing the call keeps the caller's local transaction intact, and XAER_RMFAIL
         // lets the transaction manager retry on a fresh XAResource.
         if (conn.getTransactionState() != TransactionState.IDLE) {
           if (LOGGER.isLoggable(Level.FINEST)) {
@@ -548,14 +542,13 @@ public void commit(Xid xid, boolean onePhase) throws XAException {
    * </ol>
    */
   private void commitOnePhase(Xid xid) throws XAException {
-    // Check preconditions
     if (xid.equals(preparedXid)) { // TODO: check if the condition should be negated
       throw new PGXAException(GT.tr("One-phase commit called for xid {0} but connection was prepared with xid {1}",
           xid, preparedXid), XAException.XAER_PROTO);
     }
     if (currentXid == null && !committedOrRolledBack) {
-      // We cannot tell whether xid is unknown to this resource manager or whether the caller
-      // routed the commit to the wrong connection. Treat it as the latter, which is the typical
+      // Either the xid is unknown to this resource manager, or the caller routed the commit to the
+      // wrong connection. The error reports the routing mistake, which is the common
       // application-server bug.
       throw new PGXAException(GT.tr(
           "One-phase commit must be issued on the connection that started the branch. commit xid={0}", xid),
@@ -570,14 +563,13 @@ private void commitOnePhase(Xid xid) throws XAException {
           XAException.XAER_PROTO);
     }
 
-    // Send COMMIT through QUERY_SUPPRESS_BEGIN so it works regardless of the caller's autoCommit.
-    // Cannot use conn.commit() because PgConnection.commit() throws when autoCommit=true, and the
-    // new contract leaves autoCommit at whatever the caller set.
+    // conn.commit() is unusable here: PgConnection.commit() throws when autoCommit is true, and
+    // autoCommit keeps whatever value the caller set.
     try {
       conn.execSQLUpdate("COMMIT");
     } catch (SQLException ex) {
-      // Mutate XA state only after COMMIT succeeds. On failure state stays ENDED with currentXid
-      // set, so the transaction manager can recover by calling rollback(xid).
+      // The XA state changes only after COMMIT succeeds, so a failure leaves state at ENDED with
+      // currentXid set and the transaction manager can recover by calling rollback(xid).
       throw new PGXAException(GT.tr("Error during one-phase commit. commit xid={0}", xid), ex, mapSQLStateToXAErrorCode(ex));
     }
 
@@ -603,8 +595,8 @@ private void commitOnePhase(Xid xid) throws XAException {
    * </ol>
    */
   private void commitPrepared(Xid xid) throws XAException {
-    // The XA state of this XAResource must be IDLE — we cannot commit a prepared transaction while
-    // a different XA branch is still active on this connection.
+    // The XA state of this XAResource must be IDLE. A prepared transaction cannot be committed
+    // while a different XA branch is still active on this connection.
     if (state != State.IDLE) {
       if (LOGGER.isLoggable(Level.FINEST)) {
         debug("2-phase commit rejected: XA branch active. commit xid=" + xid
@@ -615,9 +607,9 @@ private void commitPrepared(Xid xid) throws XAException {
               + "commit xid={0}, currentXid={1}, state={2}", xid, currentXid, state),
           XAException.XAER_PROTO);
     }
-    // The underlying connection must also be outside any local transaction. COMMIT PREPARED is not
-    // allowed inside a transaction block, and we must not silently commit or roll back the caller's
-    // local work. XAER_RMFAIL lets the transaction manager retry on a fresh XAResource.
+    // The underlying connection must also be outside any local transaction: PostgreSQL rejects
+    // COMMIT PREPARED inside a transaction block, and refusing the call keeps the caller's local
+    // work intact. XAER_RMFAIL lets the transaction manager retry on a fresh XAResource.
     if (conn.getTransactionState() != TransactionState.IDLE) {
       if (LOGGER.isLoggable(Level.FINEST)) {
         debug("2-phase commit rejected: local transaction in progress. commit xid=" + xid
@@ -716,8 +708,8 @@ private enum State {
     IDLE,
     /**
      * {@link #start(Xid, int)} has been called, and we're associated with an XA transaction. {@code currentXid}
-     * is valid. autoCommit is false on a connection returned by getConnection, and should not be messed with by
-     * the caller or the XA transaction will be broken.
+     * is valid. {@link #getConnection()} leaves autoCommit at the value the caller set, and the handle it
+     * returns rejects {@code setAutoCommit} until the branch ends.
      */
     ACTIVE,
     /**
diff --git a/pgjdbc/src/test/java/org/postgresql/test/xa/XADataSourceTest.java b/pgjdbc/src/test/java/org/postgresql/test/xa/XADataSourceTest.java
index 678b850d2..9878a7424 100644
--- a/pgjdbc/src/test/java/org/postgresql/test/xa/XADataSourceTest.java
+++ b/pgjdbc/src/test/java/org/postgresql/test/xa/XADataSourceTest.java
@@ -325,11 +325,13 @@ void rollbackWithoutPrepare() throws XAException {
   }
 
   /**
-   * Large object operations must work inside an active XA branch. Before 42.7.13 {@code start()}
-   * forced {@code autoCommit=false} for the duration of the branch and restored it afterwards, so
-   * {@code LargeObjectManager} saw a transaction. Since #4114 {@code start()} no longer changes
-   * {@code autoCommit}, so it stays {@code true} here even though a transaction is open, and the
-   * manager must look at the transaction state rather than {@code autoCommit} alone.
+   * Large object operations must work inside an active XA branch.
+   *
+   * <p>{@code start()} leaves {@code autoCommit} at the value the caller set, {@code true} here, so
+   * the flag still reads {@code true} while a transaction is open, and {@code LargeObjectManager}
+   * has to read the transaction state rather than {@code autoCommit} alone. Before 42.7.13
+   * {@code start()} forced {@code autoCommit=false} for the duration of the branch and restored it
+   * afterwards, so {@code autoCommit} alone was enough to detect the transaction.</p>
    *
    * @see <a href="https://github.com/pgjdbc/pgjdbc/issues/4309">Issue #4309</a>
    */
@@ -340,8 +342,8 @@ void largeObjectWithinXaBranch() throws Exception {
 
     xaRes.start(xid, XAResource.TMNOFLAGS);
     try {
-      // Regression precondition (#4309): the XA branch is active, yet autoCommit stays true, so
-      // LargeObjectManager can no longer rely on getAutoCommit() to detect the surrounding transaction.
+      // Precondition for the case that issue #4309 reported: the branch is active and autoCommit is
+      // still true.
       assertTrue(conn.getAutoCommit(), "XA start() must leave autoCommit unchanged");
 
       LargeObjectManager lom = ((PGConnection) conn).getLargeObjectAPI();
@@ -354,7 +356,7 @@ void largeObjectWithinXaBranch() throws Exception {
       }
     } finally {
       xaRes.end(xid, XAResource.TMSUCCESS);
-      // Roll back so the large object created above never leaks past the test.
+      // Roll back so the test leaves no large object behind.
       xaRes.rollback(xid);
     }
   }
@@ -362,14 +364,15 @@ void largeObjectWithinXaBranch() throws Exception {
   /**
    * Fails when the driver reports a statement of a failing batch as committed inside an XA branch.
    *
-   * <p>The driver forces a mid-batch {@code Sync} once its estimated receive buffer (64 KB) fills,
-   * and that is the only path that reaches {@code BatchResultHandler.secureProgress()} while an XA
-   * branch is active. The branch keeps {@code autoCommit=true}, so a handler that trusts that flag
-   * alone secures the flushed rows and reports their update counts as {@code 1}. Nothing is durable
-   * until the transaction manager commits, so every entry must be {@code EXECUTE_FAILED}.</p>
+   * <p>The driver forces a mid-batch {@code Sync} once its estimated receive buffer reaches
+   * {@code QueryExecutorImpl.MAX_BUFFERED_RECV_BYTES} (64000 bytes), and only that Sync reaches
+   * {@code BatchResultHandler.secureProgress()} while an XA branch is active. The branch keeps
+   * {@code autoCommit=true}, so a handler that reads that flag alone secures the flushed rows and
+   * reports their update counts as {@code 1}. Nothing is durable until the transaction manager
+   * commits, so every entry must be {@code EXECUTE_FAILED}.</p>
    *
-   * <p>Each unprepared statement is estimated at 250 bytes, so a few hundred statements guarantee at
-   * least one forced Sync before the failing entry.</p>
+   * <p>The driver estimates each unprepared statement at 250 bytes, so a few hundred statements
+   * force at least one Sync before the failing entry.</p>
    *
    * @see <a href="https://github.com/pgjdbc/pgjdbc/issues/4309">Issue #4309</a>
    */
@@ -386,7 +389,7 @@ void batchProgressNotSecuredWithinXaBranch() throws Exception {
       for (int i = 1; i <= rows; i++) {
         stmt.addBatch("INSERT INTO testxa2 VALUES (" + i + ")");
       }
-      // A duplicate primary key fails after the forced Sync has already flushed earlier rows.
+      // This INSERT violates the primary key after the forced Sync has already flushed earlier rows.
       stmt.addBatch("INSERT INTO testxa2 VALUES (1)");
 
       try {
@@ -413,8 +416,9 @@ void autoCommit() throws Exception {
     // per normal JDBC rules.
     assertTrue(conn.getAutoCommit());
 
-    // XAResource methods leave the JDBC autoCommit flag invariant (see xaMethods_doNotChangeAutoCommit
-    // for the full per-method check). Spot-check the one-phase and two-phase paths here.
+    // XAResource methods leave the JDBC autoCommit flag at the value the caller set. This test adds
+    // the one-phase commit and the rollback of a prepared branch, which
+    // xaMethods_doNotChangeAutoCommit leaves out.
     xaRes.start(xid, XAResource.TMNOFLAGS);
     assertTrue(conn.getAutoCommit(), "start() must not change autoCommit");
     xaRes.end(xid, XAResource.TMSUCCESS);
@@ -429,20 +433,19 @@ void autoCommit() throws Exception {
     xaRes.commit(xid, false);
     assertTrue(conn.getAutoCommit(), "two-phase commit() must not change autoCommit");
 
-    // Same for a 1-phase rollback
     xaRes.start(xid, XAResource.TMNOFLAGS);
     xaRes.end(xid, XAResource.TMSUCCESS);
     xaRes.rollback(xid);
     assertTrue(conn.getAutoCommit(), "1-phase rollback() must not change autoCommit");
 
-    // Same for a 2-phase rollback
     xaRes.start(xid, XAResource.TMNOFLAGS);
     xaRes.end(xid, XAResource.TMSUCCESS);
     xaRes.prepare(xid);
     xaRes.rollback(xid);
     assertTrue(conn.getAutoCommit(), "2-phase rollback() must not change autoCommit");
 
-    // close()+getConnection() during an active XA branch returns to the same server transaction
+    // close() followed by getConnection() during an active XA branch keeps the same server
+    // transaction
     conn = xaconn.getConnection();
     assertTrue(conn.getAutoCommit());
 
@@ -454,14 +457,14 @@ void autoCommit() throws Exception {
 
     conn.close();
     conn = xaconn.getConnection();
-    // state != IDLE on getConnection(), so the JDBC handle is not reset to autoCommit=true here.
-    // The physical connection's autoCommit is whatever it was before start() (true in this test).
+    // The XA state is not IDLE here, so the handle keeps the physical connection's autoCommit,
+    // which is the value it had before start(): true in this test.
     assertTrue(conn.getAutoCommit());
 
     Timestamp ts2 = getTransactionTimestamp(conn);
 
     /*
-     * Check that we're still in the same transaction. close+getConnection() should not rollback the
+     * Check that we're still in the same transaction. close() followed by getConnection() should not rollback the
      * XA-transaction implicitly.
      */
     assertEquals(ts1, ts2);
@@ -499,7 +502,7 @@ void endThenJoin() throws XAException {
   }
 
   @Test
-  void restoreOfAutoCommit() throws Exception {
+  void onePhaseBranch_leavesAutoCommitUnchanged() throws Exception {
     conn.setAutoCommit(false);
 
     Xid xid = new CustomXid(14);
@@ -509,7 +512,7 @@ void restoreOfAutoCommit() throws Exception {
 
     assertFalse(
         conn.getAutoCommit(),
-        "XaResource should have restored connection autocommit mode after commit or rollback to the initial state.");
+        "a one-phase branch must leave autoCommit at false, the value set before start()");
 
     // Test true case
     conn.setAutoCommit(true);
@@ -521,12 +524,12 @@ void restoreOfAutoCommit() throws Exception {
 
     assertTrue(
         conn.getAutoCommit(),
-        "XaResource should have restored connection autocommit mode after commit or rollback to the initial state.");
+        "a one-phase branch must leave autoCommit at true, the value set before start()");
 
   }
 
   @Test
-  void restoreOfAutoCommitEndThenJoin() throws Exception {
+  void endThenJoinBranch_leavesAutoCommitUnchanged() throws Exception {
     // Test with TMJOIN
     conn.setAutoCommit(true);
 
@@ -539,7 +542,7 @@ void restoreOfAutoCommitEndThenJoin() throws Exception {
 
     assertTrue(
         conn.getAutoCommit(),
-        "XaResource should have restored connection autocommit mode after start(TMNOFLAGS) end() start(TMJOIN) and then commit or rollback to the initial state.");
+        "start(TMNOFLAGS) end() start(TMJOIN) end() commit() must leave autoCommit at true");
 
   }
 
@@ -944,10 +947,11 @@ private TransactionState transactionState(Connection c) throws SQLException {
   }
 
   /**
-   * recover() on a connection with autoCommit=false must not leave the connection in OPEN: the
-   * SELECT against pg_prepared_xacts uses QUERY_SUPPRESS_BEGIN, so pgjdbc does not prepend a BEGIN.
-   * A follow-up commit(xid, false) on the recovered xid then succeeds, instead of failing the
-   * "2nd phase commit must be issued using an idle connection" precondition.
+   * recover() on a connection with autoCommit=false leaves the transaction state at IDLE, so a
+   * following commit(xid, false) on the recovered xid succeeds. The SELECT against
+   * pg_prepared_xacts uses QUERY_SUPPRESS_BEGIN, so the driver opens no transaction of its own.
+   * Before 42.7.13 that commit(xid, false) failed with "2nd phase commit must be issued using an
+   * idle connection".
    */
   @Test
   void recover_withAutoCommitFalse_doesNotOpenTransaction() throws Exception {
@@ -957,8 +961,8 @@ void recover_withAutoCommitFalse_doesNotOpenTransaction() throws Exception {
     xaRes.end(xid, XAResource.TMSUCCESS);
     xaRes.prepare(xid);
 
-    // Simulate the managed-datasource scenario: the recovery flow lands on a connection that the
-    // pool has put into autoCommit=false.
+    // The managed-datasource scenario: the recovery flow runs on a connection the pool has put
+    // into autoCommit=false.
     conn.setAutoCommit(false);
     assertEquals(TransactionState.IDLE, transactionState(conn),
         "autoCommit=false alone must not start a transaction");
@@ -968,31 +972,32 @@ void recover_withAutoCommitFalse_doesNotOpenTransaction() throws Exception {
     assertEquals(TransactionState.IDLE, transactionState(conn),
         "recover() must leave transactionState=IDLE on an autoCommit=false connection");
 
-    // Same XAResource, same xid → 2nd phase commit must succeed.
+    // The same XAResource and the same xid, so the 2nd phase commit succeeds.
     xaRes.commit(xid, false);
     assertEquals(TransactionState.IDLE, transactionState(conn));
   }
 
   /**
-   * recover() called on a connection that already has an open local transaction must not commit
-   * or roll back that transaction. The SELECT against pg_prepared_xacts runs inside the caller's
-   * transaction with QUERY_SUPPRESS_BEGIN; transactionState ends where it started.
+   * recover() called on a connection that already has an open local transaction leaves that
+   * transaction open, and neither commits nor rolls it back. The SELECT against pg_prepared_xacts
+   * runs inside the caller's transaction with QUERY_SUPPRESS_BEGIN, so transactionState is OPEN
+   * before and after.
    */
   @Test
   void recover_withUserTransactionInFlight_doesNotCommitUserWork() throws Exception {
-    // First, prepare a transaction so recover() has something to return.
+    // Prepare a transaction so recover() returns at least one xid.
     Xid prepared = new CustomXid(0xa1000002);
     xaRes.start(prepared, XAResource.TMNOFLAGS);
     conn.createStatement().executeUpdate("INSERT INTO testxa1 VALUES (2)");
     xaRes.end(prepared, XAResource.TMSUCCESS);
     xaRes.prepare(prepared);
 
-    // Now open a local transaction on the same physical connection with an unrelated INSERT.
+    // Open a local transaction on the same physical connection with an unrelated INSERT.
     conn.setAutoCommit(false);
     conn.createStatement().executeUpdate("INSERT INTO testxa1 VALUES (99)");
     assertEquals(TransactionState.OPEN, transactionState(conn));
 
-    // recover() must see the prepared xid and leave the local transaction OPEN.
+    // recover() must return the prepared xid and leave the local transaction OPEN.
     Xid[] recovered = xaRes.recover(XAResource.TMSTARTRSCAN);
     assertTrue(Arrays.asList(recovered).contains(prepared), "Did not recover prepared xid");
     assertEquals(TransactionState.OPEN, transactionState(conn),
@@ -1005,15 +1010,14 @@ void recover_withUserTransactionInFlight_doesNotCommitUserWork() throws Exceptio
       assertEquals(0, rs.getInt(1), "recover() must not have committed the caller's INSERT");
     }
 
-    // Clean up the prepared transaction.
     conn.setAutoCommit(true);
     xaRes.rollback(prepared);
   }
 
   /**
-   * When the caller's local transaction is already in FAILED state, recover() cannot read
-   * pg_prepared_xacts (PG rejects the SELECT with "current transaction is aborted"). The driver
-   * surfaces this as XAException(XAER_RMERR); the caller's transaction is left untouched.
+   * recover() on a connection whose local transaction is already FAILED throws
+   * XAException(XAER_RMERR) and leaves that transaction FAILED. PostgreSQL rejects the SELECT
+   * against pg_prepared_xacts with "current transaction is aborted".
    */
   @Test
   void recover_inFailedTransaction_failsWithRMERR() throws Exception {
@@ -1038,7 +1042,7 @@ void recover_inFailedTransaction_failsWithRMERR() throws Exception {
     assertEquals(TransactionState.FAILED, transactionState(conn),
         "recover() must not silently reset the caller's transaction");
 
-    // Clean up so the @AfterEach connection close does not complain.
+    // Leave the connection idle for teardown.
     conn.rollback();
     conn.setAutoCommit(true);
   }
@@ -1050,7 +1054,7 @@ void recover_inFailedTransaction_failsWithRMERR() throws Exception {
    */
   @Test
   void commitPrepared_failsCleanlyOnDirtyConnection() throws Exception {
-    // Prepare a transaction on a separate XAConnection so we can attempt the 2-phase commit on a
+    // Prepare the transaction on a separate XAConnection, so the 2-phase commit runs on a
     // connection that is also holding a local transaction.
     Xid prepared = new CustomXid(0xa1000003);
     XAConnection xaconn2 = xaDs.getXAConnection();
@@ -1080,16 +1084,15 @@ void commitPrepared_failsCleanlyOnDirtyConnection() throws Exception {
     assertEquals(TransactionState.OPEN, transactionState(conn),
         "commit(prepared, false) must not touch the caller's transaction");
 
-    // Clean up.
     conn.rollback();
     conn.setAutoCommit(true);
     xaRes.rollback(prepared);
   }
 
   /**
-   * Symmetric to {@link #commitPrepared_failsCleanlyOnDirtyConnection()}: rollback(xid) of a
-   * prepared transaction on a connection with an open local transaction must fail with
-   * XAER_RMFAIL, not silently roll back the caller's work.
+   * rollback(xid) of a prepared transaction on a connection with an open local transaction must
+   * fail with XAER_RMFAIL, not silently roll back the caller's work. This is the rollback
+   * counterpart of {@link #commitPrepared_failsCleanlyOnDirtyConnection()}.
    */
   @Test
   void rollbackPrepared_failsCleanlyOnDirtyConnection() throws Exception {
@@ -1120,15 +1123,17 @@ void rollbackPrepared_failsCleanlyOnDirtyConnection() throws Exception {
     assertEquals(TransactionState.OPEN, transactionState(conn),
         "rollback(prepared) must not touch the caller's transaction");
 
-    // Clean up.
     conn.rollback();
     conn.setAutoCommit(true);
     xaRes.rollback(prepared);
   }
 
   /**
-   * XAResource methods must not change the caller's JDBC autoCommit flag on either the success or
-   * the failure path. Verified on every method in the lifecycle.
+   * XAResource methods leave the caller's JDBC autoCommit flag at the value the caller set, on the
+   * success path and on the failure path. start(), end(), prepare(), two-phase commit() and
+   * recover() are checked with autoCommit starting at {@code true} and at {@code false}; a
+   * PREPARE TRANSACTION rejected by a deferred constraint, and the rollback that follows it, are
+   * checked at {@code true}.
    */
   @Test
   void xaMethods_doNotChangeAutoCommit() throws Exception {
@@ -1158,12 +1163,13 @@ void xaMethods_doNotChangeAutoCommit() throws Exception {
       assertEquals(initial, conn.getAutoCommit(), "2-phase commit() must not change autoCommit");
 
       Xid[] recovered = xaRes.recover(XAResource.TMSTARTRSCAN);
-      Arrays.toString(recovered); // silence unused warnings; the call is the point
+      // recover() must run here; the xids it returns are not part of this check
+      Arrays.toString(recovered);
       assertEquals(initial, conn.getAutoCommit(), "recover() must not change autoCommit");
     }
 
-    // Also check the failure path: a forced PREPARE TRANSACTION failure via a deferred FK
-    // violation must leave autoCommit untouched.
+    // The failure path: a PREPARE TRANSACTION that fails on a deferred FK violation must still
+    // leave autoCommit at the caller's value.
     Xid xid = new CustomXid(0xa1000020);
     conn.setAutoCommit(true);
     xaRes.start(xid, XAResource.TMNOFLAGS);
@@ -1184,11 +1190,11 @@ void xaMethods_doNotChangeAutoCommit() throws Exception {
   }
 
   /**
-   * When PREPARE TRANSACTION fails (here, on a deferred foreign-key constraint), the driver must leave the XA
-   * branch in a state where the transaction manager can recover it by calling rollback(xid).
-   * That means {@code state == ENDED} with {@code currentXid == xid}, so rollback(xid) takes the
-   * active-branch path and issues a plain ROLLBACK — not the prepared-branch path that would
-   * issue ROLLBACK PREPARED against a non-existent gid.
+   * When PREPARE TRANSACTION fails, here on a deferred foreign-key constraint, the driver leaves
+   * the XA branch recoverable by rollback(xid): {@code state} stays {@code ENDED} with
+   * {@code currentXid == xid}, so rollback(xid) takes the active-branch path and issues a plain
+   * ROLLBACK. The driver used to move the state to IDLE before the SQL ran, and rollback(xid) then
+   * took the prepared-branch path and issued ROLLBACK PREPARED for a gid the server never had.
    *
    * <p>Reproduces the scenario from
    * <a href="https://github.com/pgjdbc/pgjdbc/issues/3123">Issue #3123</a> (Narayana escalating
@@ -1213,11 +1219,6 @@ void prepareFailure_leavesBranchRollbackable() throws Exception {
       // ignore
     }
 
-    // The driver must still let us roll back the active branch. The successful rollback issues
-    // ROLLBACK (active-branch path) and clears the INSERT from the server transaction. If state
-    // had been mutated to IDLE before SQL — as the pre-fix code did — rollback(xid) would have
-    // taken the prepared-branch path and tried ROLLBACK PREPARED against a gid the server has
-    // never seen.
     xaRes.rollback(xid);
 
     try (ResultSet rs = dbConn.createStatement().executeQuery("SELECT count(*) FROM testxa3 WHERE foo = 777")) {
@@ -1228,8 +1229,8 @@ void prepareFailure_leavesBranchRollbackable() throws Exception {
 
   /**
    * The ConnectionHandler proxy must reject both setAutoCommit(true) and setAutoCommit(false)
-   * while an XA branch is active on the connection, per JTA 1.2 §3.4. The previous behaviour
-   * blocked only setAutoCommit(true).
+   * while an XA branch is active on the connection, per JTA 1.2 §3.4. The guard used to reject
+   * setAutoCommit(true) alone.
    */
   @Test
   void connectionHandler_rejectsBothAutoCommitDirections() throws Exception {
@@ -1255,10 +1256,9 @@ void connectionHandler_rejectsBothAutoCommitDirections() throws Exception {
   }
 
   /**
-   * The ConnectionHandler must also reject {@code setSavepoint()} and {@code setSavepoint(name)}
-   * while an XA branch is active, per JTA 1.2 §3.4. Until this fix the guard misspelled the
-   * method name as {@code setSavePoint}, so savepoints silently went through to the underlying
-   * connection.
+   * The ConnectionHandler must reject {@code setSavepoint()} and {@code setSavepoint(name)} while
+   * an XA branch is active, per JTA 1.2 §3.4. The guard used to misspell the method name as
+   * {@code setSavePoint}, so savepoints silently went through to the underlying connection.
    */
   @Test
   void connectionHandler_rejectsSetSavepoint() throws Exception {
````
