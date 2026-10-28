````markdown
## Why

`BlobInputStream.close()` cleared `this.lo` only after a successful `LargeObject.close()`:

```java
lo.close();       // throws
this.lo = null;   // never reached
```

When the release failed, the stream kept the large object. `read()` still returned bytes, and a second `close()`, which `Closeable` requires to be a no-op, retried the release and threw again. A `try`-with-resources that closes the stream after its own failure gets that second exception.

## What

`close()` now marks the stream closed, and releases its buffer, before it releases the descriptor. Retrying the release from a second `close()` was rejected: it would turn the caller's cleanup into a second failure.

## User-visible changes

- `read()` after a failed `close()` throws `IOException`.
- A `close()` after a failed release returns without calling `LargeObject.close()` again.
- The buffer, up to 512 KiB (524288 bytes), is freed at `close()` instead of when the stream is collected.

Not changed: a failed release still throws `IOException`, with the `SQLException` as its cause and the English message `Can not close large object <oid>`.

## How to verify

`closeReportsAFailedRelease` passes with or without the change, by design: it pins the `IOException` wrapping, which was already right.

## Scope

[#4364](https://github.com/pgjdbc/pgjdbc/pull/4364) fixes the same shape in `BlobOutputStream` and is still open. Other `BlobInputStream` problems are out of scope here.
````
