# Task

A maintainer called the pull request description below too long for the change. Rewrite it, in Markdown, ready to
paste into GitHub. The facts in it were checked against the code; treat every fact as verified, and add none that
neither it nor the diff carries.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template is used. The pull request lives on the target repository and has one commit.
  `git merge-base origin/master HEAD` is `8b1c16e0d1903309d4e0bbfc24840722828a4e8b`; the head commit is
  `1f76ddf95e090a1c53d62019852a4c19746ede72`.
- CI runs the full test suite, against a PostgreSQL server, on every pull request.
- Files changed: `CHANGELOG.md` +1 -0, `pgjdbc/src/main/java/org/postgresql/largeobject/BlobInputStream.java` +17 -9,
  `pgjdbc/src/test/java/org/postgresql/largeobject/BlobInputStreamCloseTest.java` +125 -0 (new).
- #4364 is open. The next release from `master` is a patch release.

## The description

````markdown
## Why

`BlobInputStream.close()` released the descriptor first and cleared `this.lo` afterwards, so a `LargeObject.close()` that threw left the stream holding the object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

Two consequences. The stream went on serving bytes from a descriptor the caller had been told to consider gone — `read()` after a failed `close()` succeeded. And a second `close()`, which `Closeable` requires to be a no-op, retried a release that had already failed and turned the caller's cleanup into a second failure. A `try`-with-resources that closes the stream after its own failure gets that second exception on the way out.

This is the read-side counterpart of [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364), which fixed the same shape on `BlobOutputStream`.

## What

The stream is marked closed, and its buffer released, before the descriptor goes. The failure still reaches the caller wrapped in an `IOException`; what changes is that it no longer leaves a stream that outlived its own `close()`.

Releasing the buffer here also drops up to 512 KiB that a closed stream used to hold until it was itself collected.

## How to verify

```bash
./gradlew :postgresql:test --tests 'org.postgresql.largeobject.BlobInputStreamCloseTest'
```

The test drives a `LargeObject` subclass whose `close()` refuses, the same technique #4364 uses. Reverting the fix fails `closeClosesTheStreamEvenWhenTheReleaseFails` (the read after the failed close succeeds instead of reporting a closed stream) and `closeIsIdempotentAfterAFailedRelease` (the second close throws again, and the release is attempted twice). `closeReportsAFailedRelease` passes either way by design: it pins the wrapping, which was already right.

Found by an adversarial review of `BlobInputStream`. Reviewed by Codex; the remaining findings from that review are coming as separate pull requests.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
````

## The diff

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d769e37f8f..494a9e79db 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -5,6 +5,7 @@ The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
 ## [Unreleased]
 
 ### Fixed
+* fix: `BlobInputStream.close()` now marks the stream closed and releases its buffer even when releasing the large object descriptor fails. It cleared the descriptor only after a successful release, so a failed `close()` left a stream that went on serving bytes from an object the caller had been told to consider gone, and a second `close()` retried the release and failed again instead of being the no-op `Closeable` requires [PR #4388](https://github.com/pgjdbc/pgjdbc/pull/4388)
 * fix: `PGStream.skip` no longer loops forever when the connection ends while the driver is discarding bytes, and no longer mistakes a stream that skips nothing for one that has ended. `InputStream.skip` may return zero with more data still coming, which a stream supplied through the `socketFactory` property is free to do; the driver now reads a byte in that case and treats only `-1` as the end [PR #4358](https://github.com/pgjdbc/pgjdbc/pull/4358)
 * fix: `LargeObjectManager` operations now work inside an active XA transaction. Since 42.7.13 an XA branch keeps the caller's `autoCommit=true`, and the guard rejected large objects as if the connection were idle. It now checks the server transaction state (`getTransactionState()`) instead of `autoCommit`, so a genuine auto-commit connection with no open transaction is still refused [Issue #4309](https://github.com/pgjdbc/pgjdbc/issues/4309) [PR #4310](https://github.com/pgjdbc/pgjdbc/pull/4310)
 * fix: batch update counts are no longer secured as committed inside an XA transaction. `BatchResultHandler` treated per-statement progress as durable whenever `autoCommit=true`, but an XA branch keeps `autoCommit=true` while the transaction is open, so a batch that flushed mid-way and then failed could report rolled-back statements as succeeded. Progress is now secured only when no server transaction is open [Issue #4309](https://github.com/pgjdbc/pgjdbc/issues/4309) [PR #4311](https://github.com/pgjdbc/pgjdbc/pull/4311)
diff --git a/pgjdbc/src/main/java/org/postgresql/largeobject/BlobInputStream.java b/pgjdbc/src/main/java/org/postgresql/largeobject/BlobInputStream.java
index 7304ef435d..1331d7e728 100644
--- a/pgjdbc/src/main/java/org/postgresql/largeobject/BlobInputStream.java
+++ b/pgjdbc/src/main/java/org/postgresql/largeobject/BlobInputStream.java
@@ -253,19 +253,27 @@ public int read(byte[] dest, int off, int len) throws IOException {
    */
   @Override
   public void close() throws IOException {
-    long loId = 0;
     try (ResourceLock ignore = lock.obtain()) {
       LargeObject lo = this.lo;
-      if (lo != null) {
-        loId = lo.getLongOID();
-        lo.close();
+      if (lo == null) {
+        return;
       }
+      long loId = lo.getLongOID();
+      // The stream is marked closed, and its buffer released, before the descriptor goes. It stays
+      // closed even when releasing the descriptor fails: a second close() would fail the same way,
+      // and until this.lo is cleared the stream goes on reading from a large object the caller
+      // believes is gone.
       this.lo = null;
-    } catch (SQLException e) {
-      throw new IOException(
-          GT.tr("Can not close large object {0}",
-              loId),
-          e);
+      buffer = null;
+      bufferPosition = 0;
+      try {
+        lo.close();
+      } catch (SQLException e) {
+        throw new IOException(
+            GT.tr("Can not close large object {0}",
+                loId),
+            e);
+      }
     }
   }
 
diff --git a/pgjdbc/src/test/java/org/postgresql/largeobject/BlobInputStreamCloseTest.java b/pgjdbc/src/test/java/org/postgresql/largeobject/BlobInputStreamCloseTest.java
new file mode 100644
index 0000000000..ca08bf1778
--- /dev/null
+++ b/pgjdbc/src/test/java/org/postgresql/largeobject/BlobInputStreamCloseTest.java
@@ -0,0 +1,125 @@
+/*
+ * Copyright (c) 2026, PostgreSQL Global Development Group
+ * See the LICENSE file in the project root for more information.
+ */
+
+package org.postgresql.largeobject;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+import static org.junit.jupiter.api.Assertions.assertNull;
+import static org.junit.jupiter.api.Assertions.assertThrows;
+import static org.junit.jupiter.api.Assertions.assertTrue;
+
+import org.postgresql.PGConnection;
+import org.postgresql.fastpath.Fastpath;
+import org.postgresql.test.TestUtil;
+import org.postgresql.util.PSQLException;
+import org.postgresql.util.PSQLState;
+
+import org.junit.jupiter.api.AfterEach;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+
+import java.io.IOException;
+import java.io.InputStream;
+import java.sql.Connection;
+import java.sql.SQLException;
+
+/**
+ * What {@link BlobInputStream#close()} leaves behind when releasing the descriptor fails.
+ */
+@SuppressWarnings("deprecation") // support for deprecated Fastpath API
+class BlobInputStreamCloseTest {
+  private static final String CLOSE_REFUSED = "close refused by the test";
+
+  private Connection con;
+  private LargeObjectManager lom;
+  private Fastpath fastpath;
+  private long loid;
+
+  @BeforeEach
+  void setUp() throws Exception {
+    con = TestUtil.openDB();
+    con.setAutoCommit(false);
+    PGConnection pgCon = con.unwrap(PGConnection.class);
+    lom = pgCon.getLargeObjectAPI();
+    fastpath = pgCon.getFastpathAPI();
+    loid = lom.createLO();
+    try (LargeObject blob = lom.open(loid, LargeObjectManager.WRITE)) {
+      blob.write(new byte[64]);
+    }
+  }
+
+  @AfterEach
+  void tearDown() throws SQLException {
+    TestUtil.closeDB(con);
+  }
+
+  /**
+   * A large object whose descriptor refuses to be released, and which records whether the release
+   * was attempted.
+   */
+  private static class FailingLargeObject extends LargeObject {
+    private int closeCalls;
+
+    FailingLargeObject(Fastpath fp, long oid, int mode) throws SQLException {
+      super(fp, oid, mode);
+    }
+
+    @Override
+    public void close() throws SQLException {
+      closeCalls++;
+      throw new PSQLException(CLOSE_REFUSED, PSQLState.IO_ERROR);
+    }
+  }
+
+  private FailingLargeObject failingLargeObject() throws SQLException {
+    return new FailingLargeObject(fastpath, loid, LargeObjectManager.READ);
+  }
+
+  /**
+   * The failure reaches the caller, wrapped, so nobody mistakes the descriptor for released.
+   */
+  @Test
+  void closeReportsAFailedRelease() throws Exception {
+    LargeObject blob = failingLargeObject();
+    InputStream bis = blob.getInputStream();
+
+    IOException e = assertThrows(IOException.class, bis::close);
+    assertTrue(e.getCause() instanceof SQLException, () -> "cause of " + e);
+    assertEquals(CLOSE_REFUSED, e.getCause().getMessage());
+  }
+
+  /**
+   * The stream is closed even so. It used to keep the large object, so it went on serving bytes
+   * from a descriptor the caller had been told to consider gone.
+   */
+  @Test
+  void closeClosesTheStreamEvenWhenTheReleaseFails() throws Exception {
+    LargeObject blob = failingLargeObject();
+    InputStream bis = blob.getInputStream();
+    assertEquals(0, bis.read());
+
+    assertThrows(IOException.class, bis::close);
+
+    // The stream reports itself closed, rather than passing on the failure it met while closing.
+    // Checked through the cause rather than the message, which is translated
+    IOException afterClose = assertThrows(IOException.class, bis::read);
+    assertNull(afterClose.getCause(), () -> "unexpected cause under " + afterClose);
+  }
+
+  /**
+   * A second close is the no-op {@link java.io.Closeable} requires, and does not ask the server
+   * again. Retrying a release that has already failed only turns the caller's cleanup into a
+   * second failure.
+   */
+  @Test
+  void closeIsIdempotentAfterAFailedRelease() throws Exception {
+    FailingLargeObject blob = failingLargeObject();
+    InputStream bis = blob.getInputStream();
+
+    assertThrows(IOException.class, bis::close);
+    bis.close();
+    assertEquals(1, blob.closeCalls, "attempts to release the descriptor");
+  }
+}
````
