## Why

`VisibleBufferedInputStream` lets a `SocketTimeoutException` from the wrapped stream reach the caller only when the caller requested the timeout through `PGStream.setNetworkTimeout`. The `socketTimeout` connection property and `Connection.setNetworkTimeout` both request it that way. Any other timeout is waited out by `ensureBytes`. [`skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java#L302-L314) broke that rule. Once its buffer was empty, it called the wrapped stream's `skip`, which reads on a JDK socket stream, and the timeout reached the caller.

The driver sets a timeout that the caller did not request on replication connections. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the status interval and leaves it on the connection. The interval is 10 seconds unless the caller passes another value to `withStatusInterval`. With `socketTimeout` at its default of 0, [`PGStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/PGStream.java#L679-L699) on that connection threw `java.net.SocketTimeoutException: Read timed out` if no byte arrived within the interval. A read would have waited instead. `PGStream.skip` discards a message that `QueryExecutorImpl.skipMessage` ignores, and a field that `receiveTupleV3` could not allocate.

The discard also depended on how a stream supplied through `socketFactory` implements `skip`, which may skip nothing while data is still arriving. #4358 worked around this with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills the buffer through `ensureBytes` and so handles a timeout like every other read. It never calls the wrapped stream's `skip`, and it never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop and throws `EOFException` on a short count. The #4358 loop never passed a count of zero or less, but the single call that replaces it passes whatever size `PGStream.skip` receives, so this branch adds a guard for those counts.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception without reporting how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way on a requested timeout also loses its count and cannot be restarted. Reading through the 8192-byte buffer is faster too. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Discarding 256 MiB over a loopback socket took 75 ms with the new `skip` and 149 ms with the old one.

The unreleased #4358 changelog entry described the loop. It also said the driver used to mistake a stream that skips nothing for one that has ended, but the loop before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream. The entry now names the two hangs that #4358 fixed and the `EOFException`.

## User-visible changes

- `VisibleBufferedInputStream.skip(n)` with `n <= 0` discards nothing and returns 0. Before, it returned a negative `n` as the number of bytes discarded. A negative `n` within the `int` range also moved the read position back: after one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`.
- `PGStream.skip` with a negative size discards nothing.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` (new) runs without a server. Its cases cover:

- a discard served from the buffer alone
- a discard across several reads
- a discard longer than the buffer, which leaves the buffer in place
- end of stream with counts up to `Long.MAX_VALUE`
- counts of 0, -1, -2, and `Long.MIN_VALUE`
- an unrequested timeout, which is waited out, and a requested one, which is thrown part-way
- a wrapped stream whose `skip` returns 0

Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream that skips nothing.

`PGStreamSkipTest` is rewritten over a source whose `skip` returns 0. It covers sizes from 0 to the whole payload, including one that needs several fills of the buffer, a negative size, and `EOFException` past end of stream. Since the wrapped `skip` is no longer called, the rewrite drops the sources that skip fully or one byte per call. It also drops `skipDoesNotFallBackToReadingByteByByte`, so no test now limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency. All three pull requests add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

* #4359 adds the same `if (n <= 0) { return 0; }` guard. It also creates `VisibleBufferedInputStreamSkipTest.java`, so whichever pull request merges second has to combine the two test classes. This branch includes its `-2` case.
* #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
