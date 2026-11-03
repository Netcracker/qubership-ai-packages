<page>

The branch adds one property. The diff to `RelayConfig.java`:

```java
+  /**
+   * The largest response header block the client accepts, in bytes. {@code null} applies
+   * {@link #DEFAULT_MAX_HEADER_SIZE} unless strict parsing is off.
+   */
+  public Builder maxHeaderSize(@Nullable Long maxHeaderSize) {
+    this.maxHeaderSize = maxHeaderSize;
+    return this;
+  }
```

```java
+  static final long DEFAULT_MAX_HEADER_SIZE = 65536;
```

and in `RelayConfig.fromProperties`:

```java
+    String mhs = props.getProperty("maxHeaderSize");
+    if (mhs != null) {
+      b.maxHeaderSize(SizeParser.parse(mhs)); // the parser connectTimeout's siblings use for sizes: 100, 64k, 2M; k and M are binary
+    }
```

`ResponseReader.readHeaders` counts the bytes of the status line and the headers. When the count passes the limit it
throws:

```java
throw new RelayProtocolException(
    "response headers exceed maxHeaderSize of " + limit + " bytes; raise maxHeaderSize");
```

and closes the connection. Where `maxHeaderSize` is unset and `strictParsing` is `false`, no limit applies. Where
`maxHeaderSize` is set, its value applies whatever `strictParsing` says. Servers that put large cookies or tokens in
headers can exceed 64 KiB.

Write the entry for the new property that goes into the page above. Give the Markdown of the entry only, as it would
appear in the list.
