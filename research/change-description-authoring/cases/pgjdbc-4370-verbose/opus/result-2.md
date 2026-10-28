## Why

Reads in `VisibleBufferedInputStream` pass a `SocketTimeoutException` from the wrapped stream to the caller only when the caller requested the timeout through `PGStream.setNetworkTimeout`. The `socketTimeout` connection property and `Connection.setNetworkTimeout` both request it that way. Otherwise `ensureBytes` keeps waiting. `skip` did not follow this rule. Once its buffer was empty, it called the wrapped stream's `skip`, which on a JDK socket stream reads, and the timeout reached the caller.

The driver also sets a timeout that no caller requested. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval and leaves it on the connection. That interval is 10 seconds unless the caller passes another value to `withStatusInterval`. With `socketTimeout` at its default of 0, discarding the rest of a message on that connection threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within the interval. A read would have waited. `PGStream.skip` discards through `VisibleBufferedInputStream.skip` in two cases: a message that `QueryExecutorImpl.skipMessage` ignores, and a field that `receiveTupleV3` could not allocate.

The discard also depended on how a stream supplied through `socketFactory` implements `skip`. Such a stream may skip nothing while data is still arriving, and #4358 added a loop in `PGStream.skip` to handle that.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes` and so handles a timeout the same way as any other read. It never calls the wrapped stream's `skip`, and it never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` replaces the #4358 loop with a single call.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception and does not report how many, so a retry cannot tell how many bytes are left. A requested timeout thrown part-way through the new `skip` also loses its count, so that discard cannot be restarted either. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

The unreleased changelog entry for #4358 described the loop. It also said the driver used to mistake a stream that skips nothing for one that has ended. In fact the loop before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream. The entry now names the two hangs that #4358 fixed and the `EOFException`.

## User-visible changes

- `VisibleBufferedInputStream.skip` with a count of zero or less discards nothing and returns 0. Before this change, a negative count was returned as the number of bytes discarded. A negative count within the `int` range also moved the read position back: after one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`. The #4358 loop never passed a negative count, but the single call that replaces it passes whatever size `PGStream.skip` receives.
- `PGStream.skip` throws `EOFException` when the stream ends before `size` bytes are discarded.

## How to verify

`PGStreamSkipTest` now runs over a source whose `skip` returns 0. It no longer has the sources that skip fully or one byte per call, because the wrapped `skip` is no longer called, and it no longer has `skipDoesNotFallBackToReadingByteByByte`. No test now limits how many reads a long discard makes. In `VisibleBufferedInputStreamSkipTest`, 5 of the 15 cases fail against the old `skip`: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream that skips nothing.

## Scope

Neither open sibling is a dependency. All three pull requests add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

* #4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`, so whichever pull request merges second has to combine the two test classes. This branch already includes the `-2` case from #4359.
* #4360 also changes `VisibleBufferedInputStream.java`, in `readMore` and `read(byte[],int,int)`. It does not change `skip`.
