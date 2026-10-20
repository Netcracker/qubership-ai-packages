````markdown
## Why

Reads in `VisibleBufferedInputStream` throw the wrapped stream's `SocketTimeoutException` only when the caller requested the timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` property and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits out the timeout. [`VisibleBufferedInputStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java#L302-L314) did not follow that rule. Once its buffer was empty, it called the wrapped stream's `skip`, which on a JDK socket stream reads, so an unrequested timeout reached the caller.

The driver also sets the socket timeout without a caller asking for it. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval, 10 seconds unless the caller passes another value to `withStatusInterval`, and leaves it on the connection. With `socketTimeout` at 0, the default, discarding the rest of a message on that connection threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within the interval. A read would have waited. [`PGStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/PGStream.java#L679-L699) discards through `VisibleBufferedInputStream.skip`, both for a message that `QueryExecutorImpl.skipMessage` ignores and for a field that `receiveTupleV3` could not allocate.

A stream from `socketFactory` may skip nothing while data is still coming, and the discard depended on how that stream implements `skip`. #4358 compensated with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` discards the bytes the buffer holds. Once the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes`, so a timeout is handled as it is for reads. It never calls the wrapped stream's `skip` and never grows the buffer. It returns fewer than `n` bytes only at end of stream. `PGStream.skip` relies on that: it drops the #4358 loop and throws `EOFException` on a short count.

The unreleased #4358 changelog entry described that loop, and said the driver used to treat a stream that skips nothing as one that has ended. Before #4358, `s += pgInput.skip(size - s)` looped forever on such a stream. The entry now names the two hangs #4358 fixed and the `EOFException`.

A count of zero or less now discards nothing and returns 0. Before, a negative count was returned as the number discarded. A negative count within the `int` range also moved the read position back: after one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`. The #4358 loop never passed a negative count, but the single call that replaces it passes whatever size `PGStream.skip` receives.

Catching the timeout around the wrapped `skip` leaves no way to resume. `InputStream.skip` discards the bytes it read before the exception and does not report how many, so a retry cannot tell how many are left. A discard through the buffer loses its count the same way when a timeout is thrown part-way, so it cannot resume either.

From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` is new and runs without a server. It covers discards served from the buffer without reading the wrapped stream, discards across several reads, and a discard longer than the buffer, which leaves the buffer in place. It also covers end of stream for counts up to `Long.MAX_VALUE`, counts of 0 and negative counts, a wrapped stream whose `skip` returns 0, and both timeout cases: an unrequested timeout is waited out, and a requested one is thrown part-way. Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream whose `skip` returns 0.

`PGStreamSkipTest` is rewritten for the new contract. It runs over a source whose `skip` returns 0 and covers sizes from 0 up to one byte short of the payload, including one that needs several fills of the 8192-byte buffer; the whole payload; a negative size, which discards nothing; and `EOFException` past the end of the stream. The buffer boundaries themselves are covered in `VisibleBufferedInputStreamSkipTest`. The rewrite drops the streams that skip fully and the ones that skip one byte per call, since the wrapped `skip` is no longer called, and drops `skipDoesNotFallBackToReadingByteByByte`. No test now limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency, and all three add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

#4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`, so whichever merges second has to combine the two test classes. This branch also has the `-2` case, where the old code moved the read position below the start of the buffer.

#4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
````
