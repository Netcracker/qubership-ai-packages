```markdown
## Why

`VisibleBufferedInputStream` throws a `SocketTimeoutException` from the wrapped stream only when the caller requested the timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` property and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits. `VisibleBufferedInputStream.skip` did not follow that rule. Once its buffer was empty, it called the wrapped stream's `skip`, which on a JDK socket stream reads, so the timeout reached the caller.

The driver also sets the socket timeout without a request. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval, 10 seconds unless the caller passes another value to `withStatusInterval`, and leaves it on the connection. With `socketTimeout` at 0, the default, discarding the rest of a message threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within that interval. A read would have waited. The discards run through `PGStream.skip`, for a message that `QueryExecutorImpl.skipMessage` ignores and for a field that `receiveTupleV3` could not allocate.

The count was not checked either. A negative count was returned as the number discarded, and a negative count within the `int` range moved the read position back. After one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`.

The discard also depended on how a stream from `socketFactory` implements `skip`. Such a stream may skip nothing while data is still coming. Before #4358, `PGStream.skip` looped forever on it, and #4358 added a loop to compensate.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes`, so a timeout is handled as a read handles it. It never calls the wrapped stream's `skip`, and it never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception and does not report how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way loses its count the same way and is not restartable either.

From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

## User-visible changes

- Without a timeout requested through `Connection.setNetworkTimeout` or `socketTimeout`, a discard waits for data, as a read does.
- On a replication connection with `socketTimeout` at 0, discarding a message or field waits for data when none arrives within the status interval, as a read does.
- A negative count returns 0 and discards nothing.
- `PGStream.skip` throws `EOFException` when the stream ends before the requested count is discarded.

Not changed: a timeout requested through `Connection.setNetworkTimeout` or `socketTimeout` still throws from a discard part-way, and the discard is not resumed.

## How to verify

Five of the fifteen cases in `VisibleBufferedInputStreamSkipTest` fail against the old `skip`: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the wrapped stream whose `skip` returns 0. The other ten pass against the old `skip`, because they pin behavior it already had.

`PGStreamSkipTest` no longer tests the streams that skip fully, the stream that skips one byte per call, or `skipDoesNotFallBackToReadingByteByByte`, since the wrapped `skip` is no longer called. Coverage lost: no test limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency. #4358 is merged but not released, so all three add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

#4359 adds the same `n <= 0` guard to `skip` and creates `VisibleBufferedInputStreamSkipTest.java` too, so whichever merges second has to combine the two test classes. This branch's test class also covers the `-2` case, where the old code moved the read position below the start of the buffer. #4360 changes `readMore` and `read(byte[],int,int)` in `VisibleBufferedInputStream`, not `skip`.
```
