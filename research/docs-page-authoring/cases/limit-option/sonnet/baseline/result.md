* **`maxHeaderSize`** (size in bytes, default: unset, which applies a limit of 64 KiB (65536 bytes))
  The largest response header block the client accepts. The count covers the status line and all headers.
  Accepts a byte count with an optional suffix, such as `100`, `64k`, or `2M`. Suffixes are binary, so `64k` is 65536 bytes and `2M` is 2097152 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it when a server puts large cookies or tokens in response headers and they can exceed 64 KiB.
  A value you set applies whatever `strictParsing` is. With `maxHeaderSize` unset, `strictParsing=false` removes the limit entirely.
