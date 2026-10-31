<page>

The branch adds one property. The diff to `RelayConfig.java`:

```java
+  /**
+   * Whether the client sends {@code Connection: close} on every request, so that no connection is reused.
+   * Default {@code false}.
+   */
+  public Builder disableKeepAlive(boolean disableKeepAlive) {
+    this.disableKeepAlive = disableKeepAlive;
+    return this;
+  }
```

and in `RelayConfig.fromProperties`:

```java
+    b.disableKeepAlive(Boolean.parseBoolean(props.getProperty("disableKeepAlive", "false")));
```

When `disableKeepAlive` is `true`, `HttpExchange` adds `Connection: close` to each request and closes the socket once
the response body is read. No other property reads the field, and the field reads no other property. Any string other
than `true` (case-insensitive) parses as `false`; nothing is rejected.

Write the entry for the new property that goes into the page above. Give the Markdown of the entry only, as it would
appear in the list.
