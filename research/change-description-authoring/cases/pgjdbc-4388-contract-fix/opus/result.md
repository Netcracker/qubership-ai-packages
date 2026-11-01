`BlobInputStream.close()` cleared `this.lo` only after it released the descriptor, so when `LargeObject.close()` threw, the stream kept the large object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

After a failed `close()`, `read()` still returned bytes from the descriptor. A second `close()` retried the release and threw again, though `Closeable` requires it to do nothing. So when code closed the stream explicitly inside a try-with-resources block and that close failed, the block's own close threw the second exception on the way out.

The stream is now marked closed, and its buffer released, before the descriptor is released. A closed stream used to hold that buffer, up to 512 KiB, until the stream itself was collected. A failed release still reaches the caller as an `IOException` wrapping the `SQLException`. After that failure, `read()` throws an `IOException` for a closed stream, and a second `close()` returns without trying the release again.

`closeReportsAFailedRelease` passes without the fix, by design: it pins the wrapping, which was already correct.

**Scope.** #4364, which is still open, fixes the same ordering in `BlobOutputStream.close()`.
