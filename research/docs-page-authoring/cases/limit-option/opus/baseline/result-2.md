* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 65536 bytes)
  The largest response header block the client accepts, counting the status line and every header. Accepts a byte
  count, or a number with a `k` or `M` suffix: `100`, `64k`, `2M`. The suffixes are binary, so `64k` is 65536 bytes.
  Over the limit, the request fails with
  `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client
  closes the connection.
  A value you set applies whatever `strictParsing` says. When `maxHeaderSize` is unset, setting `strictParsing` to
  `false` turns the built-in limit off.
  Raise it for servers that put large cookies or tokens in headers, which can exceed 64 KiB.
