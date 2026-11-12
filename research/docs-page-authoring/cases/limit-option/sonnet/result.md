* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB (65536 bytes))
  The largest response header block the client accepts. The count covers the status line and the headers.
  Accepts a byte count with an optional suffix: `100`, `64k`, `2M`. The suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  With `strictParsing` set to `false`, an unset `maxHeaderSize` means no limit. A value you set applies whatever `strictParsing` says.
  Raise it when a server puts large cookies or tokens in response headers and they can exceed 64 KiB.
