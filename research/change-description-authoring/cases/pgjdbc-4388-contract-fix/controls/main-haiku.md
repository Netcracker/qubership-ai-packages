## Breaking changes

- `read()` on `BlobInputStream` after a `close()` that failed to release the large object now throws `IOException` and reports the stream as closed. Before, it returned bytes from the object. Code that reads after a failed `close()` must handle that exception.

## Why

`BlobInputStream.close()` released the large object descriptor first and cleared the `lo` field only after a successful release. When `LargeObject.close()` threw, the stream kept the object and went on serving bytes from a descriptor the caller had been told to consider released. A second `close()` retried the failed release and threw again, which turned the caller's cleanup into a second failure, while `Closeable` requires a second `close()` to do nothing. An adversarial review of `BlobInputStream` found this.

## What

The stream now marks itself closed, and drops its buffer, before it releases the descriptor. The release still happens, and a failure still reaches the caller as an `IOException` that wraps the `SQLException`. The difference is that a failed release leaves the stream closed with no object to read from, so a second `close()` has nothing left to release.

## User-visible changes

- A second `close()` after a failed release returns without an exception. Before, it retried the release and threw `IOException` again.
- `close()` frees the stream's buffer even when the release fails, so up to 512 KiB (524288 bytes) is released at that point. Before, a closed stream held it until the garbage collector reclaimed the stream.

Not changed:

- The first `close()` that fails still throws `IOException`, with the `SQLException` as its cause and the message `Can not close large object {0}`, where `{0}` is the object ID.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.largeobject.BlobInputStreamCloseTest'
```

The new `BlobInputStreamCloseTest` has three tests and needs a running PostgreSQL server, as the other integration tests do. It drives a `LargeObject` subclass whose `close()` refuses, the same technique as [PR #4364](https://github.com/pgjdbc/pgjdbc/pull/4364). Reverting the fix fails two of them: `closeClosesTheStreamEvenWhenTheReleaseFails`, where the read after the failed close succeeds, and `closeIsIdempotentAfterAFailedRelease`, where the second close throws again and the release runs twice. `closeReportsAFailedRelease` passes either way, because it pins the wrapping, which was already right.

## Scope

This is the read-side counterpart of PR #4364, which fixed the same shape in `BlobOutputStream`. The other findings from the review that found this are outside this change.
