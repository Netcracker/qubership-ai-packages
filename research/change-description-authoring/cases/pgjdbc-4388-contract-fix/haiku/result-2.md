`BlobInputStream.close()` released the large object descriptor first and cleared `this.lo` only after that succeeded. When `LargeObject.close()` threw, the stream kept holding the object:

```java
if (lo != null) {
  loId = lo.getLongOID();
  lo.close();          // throws
}
this.lo = null;        // never reached
```

After a failed `close()`, `read()` still returned bytes from a descriptor the caller had been told to consider gone. A second `close()`, which `Closeable` requires to be a no-op, retried the failed release and threw again. A `try`-with-resources that closes the stream after its own failure got that second exception.

The stream is now marked closed, and its buffer released, before the descriptor is released. The failure is still thrown as before: an `IOException` wrapping the `SQLException`, with the message `Can not close large object {0}`. After a failed `close()`, `read()` throws an `IOException` that reports the stream as closed, and a second `close()` returns without calling `LargeObject.close()` again. A closed stream also drops its buffer, up to 512 KiB, at `close()` rather than when the garbage collector reclaims the stream.

The one test that passes without the change is `closeReportsAFailedRelease`. It pins the wrapping, which was already right.

The same shape is fixed for `BlobOutputStream` in [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364), which is still open. This change touches only `BlobInputStream`. The other findings on `BlobInputStream` are not in this change and will come as separate pull requests.
