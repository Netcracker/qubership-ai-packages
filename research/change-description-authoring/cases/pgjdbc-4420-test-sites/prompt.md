# Task

A maintainer called the pull request description below too long for the change. Rewrite it, in Markdown, ready to
paste into GitHub. The facts in it were checked against the code; treat every fact as verified, and add none that
neither it nor the diff carries.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template is used. The pull request lives on the target repository and has one commit.
  `git merge-base origin/master HEAD` is `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7`; the head commit is
  `f4651192af4bc1fb16343ac50169c4d5184a06e3`.
- CI runs the full test suite, against a PostgreSQL server, on every pull request.
- Files changed: `pgjdbc/src/test/java/org/postgresql/test/jdbc2/BatchExecuteTest.java` +0 -5,
  `pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java` +86 -3.
- #1242 is closed.

## The description

````markdown
## Why

No test turned escape processing off: `git grep setEscapeProcessing` over the tests found nothing. A `Statement` that ignored `setEscapeProcessing(false)` and translated JDBC escapes anyway passed the whole suite.

## What

With escape processing off, a `Statement` sends escape syntax such as `{d '1900-01-01'}` to the server as written, and the server rejects it with SQLState 42601. The new tests in `StatementTest` check:

- the `execute`, `executeUpdate` with generated keys, and `addBatch` paths, with escape processing off and, as a control, with the default. Each path carries the flag to the parser in its own way: `addBatch` has its own call site in `PgStatement`, and generated keys use `QueryWithReturningColumnsKey` rather than `BaseQueryKey`;
- `setEscapeProcessing(true)` after `false` translates again;
- with `preferQueryMode=extendedCacheEverything`, a `Statement` with escape processing off does not reuse the translated query another `Statement` cached for the same SQL.

The default cases cover the same paths as the `{d}` insert in `StatementTest.escapeProcessing` and the `Statement.addBatch` half of `BatchExecuteTest.testBatchEscapeProcessing`, so I removed both. The batch half gained nothing from the `reWriteBatchedInserts` and binary-mode parameters of `BatchExecuteTest`: `PgStatement.transformQueriesAndParameters` does nothing, and a statement without parameters has nothing to send in binary. The `PreparedStatement` half stays.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.test.jdbc2.StatementTest' --tests 'org.postgresql.test.jdbc2.BatchExecuteTest'
```

I checked that each new test can fail by applying one mutant at a time to the production code:

| Mutant | Red |
| --- | --- |
| `CachedQueryCreateAction.create` always escapes | all three "off" cases and the cache test |
| `create` never escapes | all three default cases |
| `executeCachedSql` passes `true` instead of the flag | "off" `execute` and generated keys |
| `addBatch` passes `true` instead of the flag | "off" `addBatch` |
| `createQueryKey` passes `true` to `QueryWithReturningColumnsKey` | "off" generated keys |
| `BaseQueryKey.equals` and `hashCode` ignore `escapeProcessing` | the cache test |
| `setEscapeProcessing` ignores its argument | the turn-back-on test |

## Scope

`PreparedStatement` and `CallableStatement` are not covered: their cache keys always escape, and JDBC says `setEscapeProcessing` has no effect on a prepared statement. #1242 (closed) duplicated existing tests of the same parser path and did not reach this branch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
````

## The diff

````diff
diff --git a/pgjdbc/src/test/java/org/postgresql/test/jdbc2/BatchExecuteTest.java b/pgjdbc/src/test/java/org/postgresql/test/jdbc2/BatchExecuteTest.java
index ee81d0a303..b3344157ee 100644
--- a/pgjdbc/src/test/java/org/postgresql/test/jdbc2/BatchExecuteTest.java
+++ b/pgjdbc/src/test/java/org/postgresql/test/jdbc2/BatchExecuteTest.java
@@ -419,9 +419,6 @@ public void testBatchEscapeProcessing() throws SQLException {
     Statement stmt = con.createStatement();
     stmt.execute("CREATE TEMP TABLE batchescape (d date)");
 
-    stmt.addBatch("INSERT INTO batchescape (d) VALUES ({d '2007-11-20'})");
-    stmt.executeBatch();
-
     PreparedStatement pstmt =
         con.prepareStatement("INSERT INTO batchescape (d) VALUES ({d '2007-11-20'})");
     pstmt.addBatch();
@@ -431,8 +428,6 @@ public void testBatchEscapeProcessing() throws SQLException {
     ResultSet rs = stmt.executeQuery("SELECT d FROM batchescape");
     assertTrue(rs.next());
     assertEquals("2007-11-20", rs.getString(1));
-    assertTrue(rs.next());
-    assertEquals("2007-11-20", rs.getString(1));
     assertTrue(!rs.next());
     TestUtil.closeQuietly(stmt);
   }
diff --git a/pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java b/pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java
index 2fcfa6b5d0..2168cd9e41 100644
--- a/pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java
+++ b/pgjdbc/src/test/java/org/postgresql/test/jdbc2/StatementTest.java
@@ -10,13 +10,16 @@
 import static org.junit.jupiter.api.Assertions.assertNotEquals;
 import static org.junit.jupiter.api.Assertions.assertNotNull;
 import static org.junit.jupiter.api.Assertions.assertNull;
+import static org.junit.jupiter.api.Assertions.assertThrows;
 import static org.junit.jupiter.api.Assertions.assertTrue;
 import static org.junit.jupiter.api.Assertions.fail;
 import static org.junit.jupiter.api.Assumptions.assumeTrue;
+import static org.junit.jupiter.params.provider.Arguments.argumentSet;
 
 import org.postgresql.PGProperty;
 import org.postgresql.core.ServerVersion;
 import org.postgresql.jdbc.PgStatement;
+import org.postgresql.jdbc.PreferQueryMode;
 import org.postgresql.test.TestUtil;
 import org.postgresql.test.util.StrangeProxyServer;
 import org.postgresql.util.LazyCleaner;
@@ -29,6 +32,9 @@
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
 import org.junit.jupiter.api.Timeout;
+import org.junit.jupiter.params.ParameterizedTest;
+import org.junit.jupiter.params.provider.Arguments;
+import org.junit.jupiter.params.provider.MethodSource;
 
 import java.io.IOException;
 import java.sql.Connection;
@@ -52,6 +58,7 @@
 import java.util.concurrent.TimeoutException;
 import java.util.concurrent.atomic.AtomicInteger;
 import java.util.concurrent.atomic.AtomicReference;
+import java.util.stream.Stream;
 
 class StatementTest {
   private Connection con;
@@ -183,9 +190,6 @@ void escapeProcessing() throws SQLException {
     count = stmt.executeUpdate("insert into escapetest (ts) values ({ts '1900-01-01 00:00:00'})");
     assertEquals(1, count);
 
-    count = stmt.executeUpdate("insert into escapetest (d) values ({d '1900-01-01'})");
-    assertEquals(1, count);
-
     count = stmt.executeUpdate("insert into escapetest (t) values ({t '00:00:00'})");
     assertEquals(1, count);
 
@@ -227,6 +231,85 @@ void escapeProcessing() throws SQLException {
     assertEquals("%found", rs.getString(1));
   }
 
+  private interface StatementAction {
+    void run(Statement stmt) throws SQLException;
+  }
+
+  /**
+   * Each case carries the statement's escape-processing flag to the query parser along its own
+   * path: {@code addBatch} has its own call site in {@link PgStatement}, and generated keys use
+   * their own query key class.
+   */
+  static Stream<Arguments> escapedDateInserts() {
+    return Stream.of(
+        argumentSet("execute", (StatementAction) stmt ->
+            stmt.execute("insert into escapetest (d) values ({d '1900-01-01'})")),
+        argumentSet("executeUpdate with generated keys", (StatementAction) stmt ->
+            stmt.executeUpdate("insert into escapetest (d) values ({d '1900-01-01'})",
+                Statement.RETURN_GENERATED_KEYS)),
+        argumentSet("addBatch", (StatementAction) stmt -> {
+          stmt.addBatch("insert into escapetest (d) values ({d '1900-01-01'})");
+          stmt.executeBatch();
+        }));
+  }
+
+  @ParameterizedTest
+  @MethodSource("escapedDateInserts")
+  void escapeSyntaxIsTranslatedByDefault(StatementAction action) throws SQLException {
+    try (Statement stmt = con.createStatement()) {
+      action.run(stmt);
+      try (ResultSet rs = stmt.executeQuery("select d from escapetest")) {
+        assertTrue(rs.next(), "select d from escapetest returned no rows");
+        assertEquals("1900-01-01", rs.getString(1));
+      }
+    }
+  }
+
+  @ParameterizedTest
+  @MethodSource("escapedDateInserts")
+  void escapeSyntaxReachesTheServerAsWrittenWhenEscapeProcessingIsOff(StatementAction action)
+      throws SQLException {
+    try (Statement stmt = con.createStatement()) {
+      stmt.setEscapeProcessing(false);
+      SQLException e = assertThrows(SQLException.class, () -> action.run(stmt));
+      assertEquals(PSQLState.SYNTAX_ERROR.getState(), e.getSQLState(), e::getMessage);
+    }
+  }
+
+  @Test
+  void escapeSyntaxIsTranslatedAgainWhenEscapeProcessingIsTurnedBackOn() throws SQLException {
+    try (Statement stmt = con.createStatement()) {
+      stmt.setEscapeProcessing(false);
+      stmt.setEscapeProcessing(true);
+      stmt.execute("insert into escapetest (d) values ({d '1900-01-01'})");
+      try (ResultSet rs = stmt.executeQuery("select d from escapetest")) {
+        assertTrue(rs.next(), "select d from escapetest returned no rows");
+        assertEquals("1900-01-01", rs.getString(1));
+      }
+    }
+  }
+
+  /**
+   * With {@code preferQueryMode=extendedCacheEverything} a plain {@link Statement} caches its
+   * query, so the translating statement leaves the translated query in the cache under the same
+   * SQL text the verbatim statement then executes.
+   */
+  @Test
+  void aCachedTranslatedQueryIsNotReusedWhenEscapeProcessingIsOff() throws SQLException {
+    Properties props = new Properties();
+    PGProperty.PREFER_QUERY_MODE.set(props, PreferQueryMode.EXTENDED_CACHE_EVERYTHING.value());
+    try (Connection cachingCon = TestUtil.openDB(props);
+         Statement translating = cachingCon.createStatement();
+         Statement verbatim = cachingCon.createStatement()) {
+      translating.executeQuery("select {fn version()}").close();
+
+      verbatim.setEscapeProcessing(false);
+      SQLException e = assertThrows(SQLException.class,
+          () -> verbatim.executeQuery("select {fn version()}"));
+      assertEquals(PSQLState.SYNTAX_ERROR.getState(), e.getSQLState(), e::getMessage);
+    }
+  }
+
   @Test
   void preparedFunction() throws SQLException {
     PreparedStatement pstmt = con.prepareStatement("SELECT {fn concat('a', ?)}");
````
