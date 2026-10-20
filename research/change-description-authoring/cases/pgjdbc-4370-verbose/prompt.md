# Task

A maintainer called the pull request description below verbose. Rewrite it, in Markdown, ready to paste into GitHub.
The facts in it were checked against the code and against a running server; treat every fact as verified, and add
none that it does not carry.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template is used. The pull request lives on the target repository and has one commit.
  `git merge-base origin/master HEAD` is `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7`; the head commit is
  `bce4a1a4b3dadf28d03e7a5de25e8217dccfc7c5`.
- Files changed: `CHANGELOG.md` +2 -1, `pgjdbc/src/main/java/org/postgresql/core/PGStream.java` +5 -19,
  `pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java` +35 -10,
  `pgjdbc/src/test/java/org/postgresql/core/PGStreamSkipTest.java` +83 -129,
  `pgjdbc/src/test/java/org/postgresql/core/VisibleBufferedInputStreamSkipTest.java` +249 -0 (new).
- #4359 and #4360 are open; #4358 has merged and is not released.

## The description

````markdown
## Why

The reads in `VisibleBufferedInputStream` throw a `SocketTimeoutException` from the wrapped stream only when the caller requested the timeout through `PGStream.setNetworkTimeout`, as the `socketTimeout` connection property and `Connection.setNetworkTimeout` do; otherwise `ensureBytes` waits it out. [`skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/VisibleBufferedInputStream.java#L302-L314) did not follow that rule: once its buffer was empty it called the wrapped stream's `skip`, which on a JDK socket stream reads, and the timeout reached the caller.

The driver also sets the socket timeout without requesting it: [`V3ReplicationProtocol.configureSocketTimeout`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/v3/replication/V3ReplicationProtocol.java#L121-L142) sets it to the replication status interval, 10 seconds unless the caller passes another value to `withStatusInterval`, and leaves it on the connection. With `socketTimeout` at 0, the default, discarding the rest of a message on that connection threw `java.net.SocketTimeoutException: Read timed out` when no byte of it arrived within the interval, where a read would have waited. [`PGStream.skip`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/src/main/java/org/postgresql/core/PGStream.java#L679-L699) discards through `VisibleBufferedInputStream.skip`, for a message `QueryExecutorImpl.skipMessage` ignores and for a field `receiveTupleV3` could not allocate.

The discard also depended on how a stream supplied through `socketFactory` implements `skip`, which may skip nothing while data is still coming. #4358 compensated with a loop in `PGStream.skip`.

## What

`VisibleBufferedInputStream.skip` takes what the buffer holds and, when it is empty, calls `read()`, which refills the buffer through `ensureBytes` and so handles a timeout the same way. It never calls the wrapped stream's `skip`, and it never grows the buffer. It returns less than `n` only at end of stream, so `PGStream.skip` drops the #4358 loop and throws `EOFException` on a short count; a comment there records that it relies on this.

The unreleased #4358 changelog entry described that loop, and said the driver used to mistake a stream that skips nothing for one that has ended. The loop before #4358, `s += pgInput.skip(size - s)`, looped forever on such a stream instead. The entry now names the two hangs #4358 fixed and the `EOFException`.

A count of zero or less now discards nothing and returns 0. Before, a negative count was returned as the number discarded, and one within the `int` range moved the read position back: after one byte was read, `skip(-2)` moved it below the start of the buffer, and the next read threw `ArrayIndexOutOfBoundsException`. The #4358 loop never passed one, but the single call that replaces it passes whatever size `PGStream.skip` receives.

Catching the timeout around the wrapped `skip` would not work: `InputStream.skip` discards the bytes it read before the exception without reporting how many, so a retry cannot tell how many are left. A discard through the buffer that throws part-way loses its count the same way and is not restartable either. From Java 13 on, the JDK socket stream inherits `InputStream.skip`, which reads 2048 bytes at a time. Reading through the 8192-byte buffer is faster: discarding 256 MiB over a loopback socket took 75 ms, against 149 ms with the old `skip`.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.VisibleBufferedInputStreamSkipTest' --tests 'org.postgresql.core.PGStreamSkipTest'
```

`VisibleBufferedInputStreamSkipTest` (new) runs without a server. It covers a discard served from the buffer without reading the wrapped stream, one that spans several reads, a discard longer than the buffer leaving the buffer in place, end of stream with counts up to `Long.MAX_VALUE`, counts of 0, -1, -2, and `Long.MIN_VALUE`, an unrequested timeout waited out, a requested one thrown part-way, and a wrapped stream whose `skip` returns 0. Against the old `skip`, 5 of its 15 cases fail: the unrequested timeout, the counts -1, -2, and `Long.MIN_VALUE`, and the stream that skips nothing.

`PGStreamSkipTest` is rewritten for the new contract, over a source whose `skip` returns 0: sizes from 0 up to one byte short of the payload, including one that needs several fills of the 8192-byte buffer, the whole payload, a negative size, which discards nothing, and `EOFException` past end of stream. The buffer boundaries themselves are covered by `VisibleBufferedInputStreamSkipTest`. It drops the streams that skip fully and one byte per call, since the wrapped `skip` is no longer called, and `skipDoesNotFallBackToReadingByteByByte`; no test now limits how many reads a long discard makes.

## Scope

Neither open sibling is a dependency, and all three add a `CHANGELOG.md` bullet directly above the #4358 entry, which this branch rewrites.

* #4359 adds the same `if (n <= 0) { return 0; }` guard and creates `VisibleBufferedInputStreamSkipTest.java` as well, so whichever merges second has to combine the two test classes. This branch also carries its `-2` case, where the old code drove the read position below the start of the buffer.
* #4360 changes `readMore` and `read(byte[],int,int)`, not `skip`.




````
