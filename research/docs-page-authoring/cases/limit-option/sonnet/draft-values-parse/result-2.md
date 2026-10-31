* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 65536 bytes)
  The largest response header block the client accepts. The count covers the status line and the headers.
  A bare number is bytes. The suffixes `k` and `M` are binary, so `64k` is 65536 bytes and `2M` is 2097152 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it when a server puts large cookies or tokens in response headers and they can exceed 64 KiB.
  A value you set applies whatever `strictParsing` is. Only the built-in limit is turned off by `strictParsing=false`, so with both unset, no limit applies.
