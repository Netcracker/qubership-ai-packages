## Why

`VisibleBufferedInputStream` throws a `SocketTimeoutException` from the wrapped stream only when the caller requested a timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` property and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits it out. `skip` did not follow that rule. Once its buffer was empty, it called the wrapped stream's `skip`, which reads on a JDK socket stream, so the timeout reached the caller.

The driver also sets a socket timeout that no caller requested. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval, 10 seconds unless the caller passes another value to `withStatusInterval`, and leaves it on the connection. With `socketTimeout` at 0, the default, discarding the rest of a message threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within the interval, where a read would have waited. `PGStream.skip` discards for a message that `QueryExecutorImpl.skipMessage` ignores, and for a field that `receiveTupleV3` could not allocate.

Counts of zero or less were also mishandled. A negative count was returned as the number discarded, and a count within the `int` range moved the read position back. After one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`.

## What

`VisibleBufferedInputStream.skip` discards what the buffer holds. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes`, so a timeout is handled as it is in a read. It never grows the buffer and never calls the wrapped stream's `skip`. That `skip` may skip nothing while data is still coming, as a stream from `socketFactory` can, and #4358 compensated with a loop in `PGStream.skip`. Because the method returns less than `n` only at end of stream, `PGStream.skip` drops that loop and throws `EOFException` on a short count. A comment there records that it relies on this.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception without reporting how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way loses its count the same way and cannot be restarted.

Reading through the 8192-byte buffer is also faster. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Discarding 256 MiB over a loopback socket took 75 ms through the buffer, against 149 ms with the old `skip`.

## User-visible changes

- When the caller requested no timeout, discarding a message waits for the rest of it, as a read does, instead of throwing `SocketTimeoutException`.
- `PGStream.skip` throws `EOFException` when the stream ends before the requested count.
- A count of zero or less discards nothing and returns 0.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` is new and runs without a server. Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and a wrapped stream whose `skip` returns 0.

`PGStreamSkipTest` is rewritten for the new contract, over a source whose `skip` returns 0. It covers sizes from 0 up to one byte short of the payload, the whole payload, a negative size, and `EOFException` past end of stream. It drops the streams that skip fully, the stream that skips one byte per call, and `skipDoesNotFallBackToReadingByteByByte`, because the wrapped `skip` is no longer called. No test now limits how many reads a long discard makes.

## Scope

#4359 and #4360 are open, and neither is a dependency of this change. #4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`, so whichever merges second has to combine the two test classes. This branch also carries a `-2` case, where the old code drove the read position below the start of the buffer. #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.

All three add a `CHANGELOG.md` bullet directly above the #4358 entry. This branch rewrites that entry to name the two hangs #4358 fixed and the `EOFException`. #4358 is merged and not released.
