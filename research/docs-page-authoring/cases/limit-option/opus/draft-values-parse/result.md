* **`maxHeaderSize`** (size, default: unset, which applies a limit of 64 KiB)
  Limits the size of a response's status line and headers, counted together in bytes.
  Accepts a byte count, or a number with a `k` or `M` suffix. The suffixes are binary, so `64k` is 65536 bytes and `2M`
  is 2097152 bytes.
  Past the limit, the request fails with
  `RelayProtocolException: response headers exceed maxHeaderSize of 65536 bytes; raise maxHeaderSize`
  and the client closes the connection.
  Raise it for servers that send large cookies or tokens in headers. A value you set applies whatever `strictParsing`
  says. If you leave `maxHeaderSize` unset and set `strictParsing` to `false`, no limit applies.
