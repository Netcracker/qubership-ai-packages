* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB)
  The largest response header block the client accepts, status line included. On the builder, the value is a byte
  count. In `relay.properties`, it also accepts `k` and `M` suffixes, such as `64k` or `2M`, and a bare number is
  bytes. The suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it for servers that put large cookies or tokens in their headers. A value you set applies whatever
  `strictParsing` says. The built-in limit applies only while `strictParsing` is `true`.
