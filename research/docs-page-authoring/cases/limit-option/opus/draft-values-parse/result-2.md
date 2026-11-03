* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB)
  The largest response header block the client accepts, counting the status line and every header. Accepts `k` and
  `M` suffixes, such as `64k` or `2M`; a bare number is bytes. Suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with
  `RelayProtocolException: response headers exceed maxHeaderSize of 65536 bytes; raise maxHeaderSize` and the client
  closes the connection.
  Raise it for servers that send large cookies or tokens in headers. A value you set applies whatever `strictParsing`
  says. When `maxHeaderSize` is unset and `strictParsing` is `false`, no limit applies.
