In pgjdbc, the PostgreSQL JDBC driver, `PGStream.increaseByteCounter(long value)` adds the size of each row the driver
receives to a running total, and throws when the total passes the limit the user configured:

```java
private void increaseByteCounter(long value) throws SQLException {
  if (maxResultBuffer != -1) {
    resultBufferByteCount += value;
    if (resultBufferByteCount > maxResultBuffer) {
      setBroken();
      throw new PSQLException(GT.tr("<message>", resultBufferByteCount, maxResultBuffer),
          PSQLState.COMMUNICATION_ERROR);
    }
  }
}
```

What the code establishes:

- `maxResultBuffer` is a connection property (a JDBC URL parameter or a `DataSource` property), unset by default, which
  means no limit. It takes a byte count (`100000000`), a size with a decimal suffix (`100M` is 100000000 bytes; `K`, `M`,
  `G`, `T`), or a percent of the maximum heap (`10p`); the parser clamps it to 90% of the maximum heap.
- The limit bounds the memory the rows of one result can take on the client.
- The running total resets at every ReadyForQuery. With `Statement.setFetchSize` and autocommit off, the driver reads
  the result in batches of that many rows, and each batch starts from zero. With autocommit on, the driver reads the
  whole result at once.
- `setBroken()` closes the connection, so the application needs a new one.
- `GT.tr` formats its pattern with `java.text.MessageFormat`: `{0}` is `resultBufferByteCount`, `{1}` is
  `maxResultBuffer`, both `long` in bytes.

Write the English message pattern that replaces `<message>`. Give the pattern only, as it would appear between the
quotes in the Java source.
