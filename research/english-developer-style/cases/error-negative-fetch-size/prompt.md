In pgjdbc, `PgStatement.setFetchSize(int rows)` now rejects a negative value:

```java
if (rows < 0) {
  throw new PSQLException(GT.tr("<message>", rows), PSQLState.INVALID_PARAMETER_VALUE);
}
```

`GT.tr` formats its pattern with `java.text.MessageFormat`, so `{0}` stands for `rows`. The exception reaches the
application that called `setFetchSize` and nothing runs after it in that call.

Write the English message pattern that replaces `<message>`. Give the pattern only, as it would appear between the
quotes in the Java source.
