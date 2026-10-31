`httpkit` is a Java HTTP client library published to Maven Central. Its builder method
`HttpClientBuilder.connectTimeout(long millis)` sets how long a connection attempt may take, and now rejects a negative
value:

```java
public HttpClientBuilder connectTimeout(long millis) {
  if (millis < 0) {
    throw new IllegalArgumentException(<message>);
  }
  this.connectTimeoutMillis = millis;
  return this;
}
```

The exception reaches the application that called `connectTimeout`, and the builder is left unchanged. `0` means no
timeout, and that is documented on the method.

Write the Java expression that replaces `<message>`. Give the expression only, as it would appear in the source.
