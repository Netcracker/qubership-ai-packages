* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB)
  The largest response header block the client accepts, counting the status line and all headers together. A bare
  number is bytes. The `k` and `M` suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with
  `RelayProtocolException: response headers exceed maxHeaderSize of 65536 bytes; raise maxHeaderSize` and the client
  closes the connection.
  Raise it for servers that put large cookies or tokens in their headers. A value you set applies whatever
  `strictParsing` says. If `maxHeaderSize` is unset and `strictParsing` is `false`, no limit applies.
