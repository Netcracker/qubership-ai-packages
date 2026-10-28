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
