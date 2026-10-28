`BlobInputStream.close()` cleared `this.lo` only after the descriptor was released. When `LargeObject.close()` threw, the stream kept the large object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

As a result, `read()` after a failed `close()` still returned bytes from a descriptor the caller had been told to consider gone. A second `close()` tried the release again and threw again, although `Closeable` requires it to be a no-op. A try-with-resources block that closes the stream after its own failure got that second exception on the way out.

The stream is now marked closed, and its buffer released, before the descriptor is released. The first `close()` still throws `IOException` (`Can not close large object {0}`) with the `SQLException` as its cause. After that, `read()` throws an `IOException` for a closed stream, and another `close()` returns without trying the release again. Releasing the buffer here also frees up to 512 KiB that a closed stream used to hold until the stream itself was garbage collected.

`closeReportsAFailedRelease` passes without the fix. It pins the wrapping, which was already right. [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364), still open, fixes the same defect in `BlobOutputStream`.
