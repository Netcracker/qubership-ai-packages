When `LargeObject.close()` threw, `BlobInputStream.close()` left the stream open: `read()` kept returning bytes from the descriptor, and a second `close()` retried the release and threw again instead of being a no-op, so a try-with-resources cleanup after a failure got a second exception.

`close()` now marks the stream closed and drops its read buffer before releasing the descriptor. The release failure is still thrown as an `IOException`. This is the read-side counterpart of #4364 for `BlobOutputStream`.

`BlobInputStreamCloseTest` uses a `LargeObject` whose `close()` throws.
