## Why

The reads in `VisibleBufferedInputStream` throw a `SocketTimeoutException` from the wrapped stream only when the caller requested the timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` connection property and `Connection.setNetworkTimeout` do. Otherwise, `ensureBytes` waits it out. [`skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java#L302-L314) broke that rule. Once its buffer was empty, it called the wrapped stream's `skip`. On a JDK socket stream, that call reads, so the timeout reached the caller.

The driver also sets a socket timeout that the caller did not request. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval. The interval is 10 seconds unless the caller passes another value to `withStatusInterval`, and the method leaves the timeout set on the connection. With `socketTimeout` at its default of 0, discarding the rest of a message on that connection threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within the interval, where a read would have waited. [`PGStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/PGStream.java#L679-L699) discards through `VisibleBufferedInputStream.skip`, for a message `QueryExecutorImpl.skipMessage` ignores and for a field `receiveTupleV3` could not allocate.

The discard also depended on how a stream supplied through `socketFactory` implements `skip`. Such a stream may skip nothing while data is still coming. #4358 compensated with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` discards what the buffer holds, up to `n`. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes`, so a timeout is handled the same way as in a read. `skip` never calls the wrapped stream's `skip`, and it never grows the buffer. It returns less than `n` only at end of stream.

`PGStream.skip` therefore drops the #4358 loop and throws `EOFException` on a short count. A comment there records that it relies on this.

The unreleased #4358 changelog entry describes that loop. It says the driver used to take a stream that skips nothing for one that has ended. The loop before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream instead. The entry now names the two hangs #4358 fixed and the `EOFException`.

A count of zero or less now discards nothing and returns 0. Before, a negative count was returned as the number discarded. A negative count within the `int` range also moved the read position back. After one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`. The #4358 loop never passed a negative count, but the single call that replaces it passes whatever size `PGStream.skip` receives.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception, without reporting how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way loses its count the same way, so it cannot be restarted either.

From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster. Discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` (new) runs without a server. It covers:

- a discard served from the buffer, without reading the wrapped stream;
- a discard that spans several reads;
- a discard longer than the buffer, which leaves the buffer in place;
- end of stream, with counts up to `Long.MAX_VALUE`;
- counts of 0, -1, -2, and `Long.MIN_VALUE`;
- an unrequested timeout, waited out;
- a requested timeout, thrown part-way;
- a wrapped stream whose `skip` returns 0.

Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream whose `skip` returns 0.

`PGStreamSkipTest` is rewritten for the new contract. It runs over a source whose `skip` returns 0 and covers:

- sizes from 0 up to one byte short of the payload, including one that needs several fills of the 8192-byte buffer;
- the whole payload;
- a negative size, which discards nothing;
- `EOFException` past end of stream.

The buffer boundaries are covered by `VisibleBufferedInputStreamSkipTest`. The rewrite also drops the streams that skip fully and the ones that skip one byte per call, because the wrapped `skip` is no longer called, and it drops `skipDoesNotFallBackToReadingByteByByte`. No test now limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency. All three add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

- #4359 adds the same `if (n <= 0) { return 0; }` guard and creates `VisibleBufferedInputStreamSkipTest.java` as well. Whichever merges second has to combine the two test classes. This branch also has a `-2` case, where the old code drove the read position below the start of the buffer.
- #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
