`BlobInputStream.close()` released the descriptor first and cleared `this.lo` afterwards. When `LargeObject.close()` threw, the stream kept the object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

After a failed `close()`, `read()` went on returning bytes from a descriptor the caller had been told to consider gone. A second `close()` should be a no-op under `Closeable`. Instead it tried the failed release again and threw again. So a `try`-with-resources that closes the stream after its own failure got that second exception on the way out.

The stream is now marked closed before the descriptor is released, and its buffer of up to 512 KiB is released at the same point. After a failed `close()`, `read()` throws an `IOException` for a closed stream. A second `close()` returns without trying the release again. The failed release still reaches the caller as an `IOException` (`Can not close large object <oid>`) with the `SQLException` as its cause. `closeReportsAFailedRelease` pins that wrapping, and it passes without the fix.

This is the read-side counterpart of [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364), still open, which fixes the same defect in `BlobOutputStream`.
