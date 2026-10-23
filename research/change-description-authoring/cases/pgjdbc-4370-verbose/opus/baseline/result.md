`VisibleBufferedInputStream.skip` now discards bytes through its own buffer and no longer calls the wrapped stream's `skip`. A socket timeout that the caller did not request is now waited out, the same way a read waits it out.

## Why

Reads in `VisibleBufferedInputStream` throw a `SocketTimeoutException` only when the caller requested the timeout through `PGStream.setNetworkTimeout`. The `socketTimeout` connection property and `Connection.setNetworkTimeout` both go through it. Otherwise `ensureBytes` waits the timeout out. Once its buffer was empty, [`skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java#L302-L314) called the wrapped stream's `skip`. On a JDK socket stream that call reads, so the timeout reached the caller.

The driver also sets a timeout that nobody requested. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval and leaves it on the connection. The interval is 10 seconds unless the caller passes another value to `withStatusInterval`. [`PGStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/PGStream.java#L679-L699) discards a message that `QueryExecutorImpl.skipMessage` ignores, or a field that `receiveTupleV3` could not allocate. With `socketTimeout` at its default of 0, it threw `java.net.SocketTimeoutException: Read timed out` when no byte arrived within the interval. A read would have waited.

The discard also depended on how a stream supplied through `socketFactory` implements `skip`. Such a stream may skip nothing while data is still coming, and #4358 compensated with a loop in `PGStream.skip`.

## What

- `VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes` and handles a timeout the same way. It never calls the wrapped stream's `skip` and never grows the buffer. It returns less than `n` only at end of stream.
- `PGStream.skip` drops the #4358 loop and throws `EOFException` on a short count. A comment there records that it relies on that contract.
- A count of zero or less discards nothing and returns 0. Before this change, a negative count was returned as the number discarded. A negative count within the `int` range also moved the read position back: after one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`. The #4358 loop never passed a negative count, but the single call that replaces it passes whatever size `PGStream.skip` receives.
- The changelog entry for #4358 is rewritten. It described the loop and said the driver used to mistake a stream that skips nothing for one that has ended. In fact, the loop before #4358 (`s += pgInput.skip(size - s)`) looped forever on such a stream. The entry now names the two hangs that #4358 fixed and the `EOFException`.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception and does not report how many there were, so a retry cannot tell how many are left. The new discard through the buffer is not restartable either: when it throws part-way, its count is lost the same way.

From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` is new and runs without a server. It covers discards within the buffer, across several reads, and longer than the buffer. It also covers end of stream, counts of 0 and below, an unrequested timeout that is waited out, a requested timeout thrown part-way, and a wrapped stream whose `skip` returns 0. Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream that skips nothing.

`PGStreamSkipTest` is rewritten for the new contract, over a source whose `skip` returns 0. It covers sizes from 0 to the whole payload, a negative size, and `EOFException` past end of stream. The wrapped `skip` is no longer called, so the test drops the streams that skip fully and one byte per call. It also drops `skipDoesNotFallBackToReadingByteByByte`, so no test now limits how many reads a long discard makes.

## Related pull requests

Neither open pull request is a dependency. Both add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

- #4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`. Whichever of the two merges second has to combine the test classes. This branch already carries the `-2` case from #4359.
- #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
