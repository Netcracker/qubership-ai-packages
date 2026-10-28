## Why

On a replication connection with `socketTimeout` at 0, the default, discarding the rest of a message threw this exception when no byte of it arrived within the replication status interval:

```text
java.net.SocketTimeoutException: Read timed out
```

A read in the same situation waits instead. [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets the socket timeout to that interval and leaves it on the connection. The interval is 10 seconds unless the caller passes another value to `withStatusInterval`. `PGStream.skip` discards a message that `QueryExecutorImpl.skipMessage` ignores and a field that `receiveTupleV3` could not allocate.

Reads in `VisibleBufferedInputStream` throw the timeout only when the caller requested it through `PGStream.setNetworkTimeout`, as `socketTimeout` and `Connection.setNetworkTimeout` do. Otherwise `ensureBytes` waits it out. Once its buffer was empty, `skip` called the wrapped stream's `skip` instead. On a JDK socket stream that call reads, so the timeout reached the caller. The discard also depended on how a stream supplied through `socketFactory` implements `skip`, which may skip nothing while data is still coming. #4358 compensated with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds. When the buffer is empty, it calls `read()`, which refills it through `ensureBytes` and so handles a timeout the same way. It never calls the wrapped stream's `skip` and never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop.

Catching the timeout around the wrapped `skip` would not work. `InputStream.skip` discards the bytes it read before the exception without reporting how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way loses its count the same way, and it cannot be restarted either. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Over a loopback socket, discarding 256 MiB through the 8192-byte buffer took 75 ms, against 149 ms with the old `skip`.

The single call that replaces the #4358 loop passes whatever size `PGStream.skip` receives, and the loop never passed a count of zero or less. The old `skip` returned a negative count as the number discarded. A negative count within the `int` range also moved the read position back:

```java
in.read();
in.skip(-2);  // moved the read position below the start of the buffer
in.read();    // ArrayIndexOutOfBoundsException
```

The #4358 changelog entry is unreleased, and it described the removed loop. It also said the driver used to mistake a stream that skips nothing for one that has ended. In fact, the code before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream. The entry now names the two hangs #4358 fixed and the `EOFException`.

## User-visible changes

- `VisibleBufferedInputStream.skip(n)` with `n <= 0` discards nothing and returns 0.
- `PGStream.skip` throws `EOFException` when the stream ends before `size` bytes are discarded.

## How to verify

`PGStreamSkipTest` drops its wrapped streams that skip fully or one byte per call, because the wrapped `skip` is no longer called. It also drops `skipDoesNotFallBackToReadingByteByByte`, so no test now limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency. All three pull requests add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

* #4359 adds the same `if (n <= 0) { return 0; }` guard and also creates `VisibleBufferedInputStreamSkipTest.java`. Whichever pull request merges second has to combine the two test classes. This branch also carries the `-2` case from #4359.
* #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.
