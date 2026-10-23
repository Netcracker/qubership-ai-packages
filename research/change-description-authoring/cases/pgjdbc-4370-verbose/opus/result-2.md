## Why

With `socketTimeout` at 0, the default, discarding the rest of a message on a replication connection could throw `java.net.SocketTimeoutException: Read timed out`. It happened when none of the message's bytes arrived within the replication status interval. A read in the same place would have waited. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets the socket timeout to that interval and leaves it on the connection. The interval is 10 seconds unless the caller passes another value to `withStatusInterval`. `PGStream.skip` discards a message that `QueryExecutorImpl.skipMessage` ignores, and a field that `receiveTupleV3` could not allocate.

`VisibleBufferedInputStream` reads throw a timeout only when the caller requested it through `PGStream.setNetworkTimeout`, as `socketTimeout` and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits it out. `skip` did not follow that rule. Once its buffer was empty, it called the wrapped stream's `skip`, which reads on a JDK socket stream, so the timeout reached the caller. The discard also depended on how a stream from `socketFactory` implements `skip`, and that `skip` may skip nothing while data is still arriving. #4358 compensated with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills it through `ensureBytes`, so a discard handles a timeout the same way a read does. It never calls the wrapped stream's `skip` and never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop.

Counts of zero or less are guarded because the single call that replaces the loop passes whatever size `PGStream.skip` receives, and the loop never passed a negative count. Before, a negative count was returned as the number discarded. A count within the `int` range also moved the read position back. After one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception without reporting how many, so a retry cannot tell how many are left. A requested timeout that interrupts the new discard part-way loses its count the same way, so that discard cannot be restarted either. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

The unreleased #4358 changelog entry described the loop. It also said the driver used to mistake a stream that skips nothing for one that has ended, but the code before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream. The entry now names the two hangs #4358 fixed and the `EOFException`.

## User-visible changes

- `PGStream.skip` throws `EOFException` when the stream ends before the requested size is discarded.
- `VisibleBufferedInputStream.skip` discards nothing and returns 0 for a count of zero or less.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` is new and needs no server. It covers:

- discards inside the buffer, across several reads, and longer than the buffer;
- end of stream with counts up to `Long.MAX_VALUE`;
- counts of 0, -1, -2, and `Long.MIN_VALUE`;
- an unrequested timeout, which is waited out, and a requested one, which is thrown part-way;
- a wrapped stream whose `skip` returns 0.

Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream that skips nothing.

`PGStreamSkipTest` is rewritten over a source whose `skip` returns 0. It covers sizes from 0 to the whole payload, including sizes that need several buffer fills, a negative size, and `EOFException` past end of stream. It drops the streams that skip fully or one byte per call, because the wrapped `skip` is no longer called. It also drops `skipDoesNotFallBackToReadingByteByByte`, so no test limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency. All three pull requests add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

* #4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`, so whichever merges second has to combine the two test classes. This branch includes the `-2` case from #4359.
* #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
