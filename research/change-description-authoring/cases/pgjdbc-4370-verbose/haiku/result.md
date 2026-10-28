With `socketTimeout` at its default of 0, discarding the rest of a message on a replication connection threw `java.net.SocketTimeoutException: Read timed out` when no byte of the message arrived within the status interval, where a read would have waited. `V3ReplicationProtocol.configureSocketTimeout` sets the socket timeout to that interval, 10 seconds unless the caller passes another value to `withStatusInterval`, and leaves it on the connection. The caller did not request it. The discard runs through `VisibleBufferedInputStream.skip` for a message that `QueryExecutorImpl.skipMessage` ignores and for a field that `receiveTupleV3` could not allocate.

The reads in `VisibleBufferedInputStream` throw a `SocketTimeoutException` from the wrapped stream only when the caller requested the timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` property and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits. `skip` did not follow that rule: once its buffer was empty, it called the wrapped stream's `skip`, which on a JDK socket stream reads, so the timeout reached the caller.

A stream from `socketFactory` may skip nothing while data is still coming, so the discard depended on how it implemented `skip`. #4358 compensated with a loop in `PGStream.skip`.

A negative count within the `int` range also moved the read position back. After one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`.

`VisibleBufferedInputStream.skip` now takes what the buffer holds and, once the buffer is empty, calls `read()`. That refills the buffer through `ensureBytes`, so a timeout is handled as it is for any other read. It never calls the wrapped stream's `skip`, and it does not grow the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop. A comment there records that it relies on this.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception and does not report how many, so a retry cannot tell how many are left. A discard through the buffer that a requested timeout interrupts part-way loses its count the same way, and it cannot restart either.

Delegating to the wrapped `skip` is also slower. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Discarding 256 MiB over a loopback socket took 75 ms through the 8192-byte buffer, against 149 ms with the old `skip`.

User-visible:

- On a connection that a replication stream has configured, with `socketTimeout` at 0, a discard waits when no byte arrives within the status interval.
- A count of zero or less discards nothing and returns 0. The old code returned a negative count as the number discarded.
- A discard that reaches end of stream before its count throws `EOFException` from `PGStream.skip`.

`VisibleBufferedInputStreamSkipTest` fails five of its 15 cases on the old `skip`: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream whose `skip` returns 0. `PGStreamSkipTest` is rewritten for the new contract. It drops the streams that skip fully or one byte per call, and `skipDoesNotFallBackToReadingByteByByte`, because the wrapped `skip` is no longer called. No test now limits how many reads a long discard makes.

#4359 and #4360 are open, and neither is a dependency of this change. All three add a `CHANGELOG.md` bullet directly above the unreleased #4358 entry, which this branch rewrites. #4359 also adds the same `if (n <= 0) { return 0; }` guard to `skip` and creates `VisibleBufferedInputStreamSkipTest.java`, so whichever merges second has to combine the two test classes. This branch also has the `skip(-2)` case. #4360 changes `readMore` and `read(byte[], int, int)`, not `skip`.
