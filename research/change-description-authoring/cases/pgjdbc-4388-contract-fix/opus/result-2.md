`BlobInputStream.close()` cleared `this.lo` only after the descriptor was released. When `LargeObject.close()` threw, the stream kept the object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

After that failed `close()`, `read()` still returned bytes from a descriptor the caller had been told to consider gone. A second `close()` tried the release again and threw again, but `Closeable` requires a second `close()` to have no effect. A `try`-with-resources that closes the stream after its own failure got that second exception on the way out.

`close()` now marks the stream closed and releases its buffer before it releases the descriptor. The failure still reaches the caller wrapped in an `IOException`. After it, `read()` throws an `IOException` reporting a closed stream, and a second `close()` returns without trying the release again. Releasing the buffer also frees up to 512 KiB that a closed stream used to hold until the stream itself was garbage-collected.

`closeReportsAFailedRelease` passes without the fix because it pins the `IOException` wrapping, which was already correct.

**Scope.** [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364) is still open and fixes the same defect in `BlobOutputStream`.
