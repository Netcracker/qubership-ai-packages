* **`maxHeaderSize`** (size in bytes, default: unset, which applies a built-in limit of 64 KiB (65536 bytes) unless `strictParsing` is `false`)
  The largest response header block the client accepts. The count covers the status line and the headers.
  Accepts a byte count with an optional suffix, such as `100`, `64k`, or `2M`. Suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it when a server puts large cookies or tokens in response headers and they exceed 64 KiB.
  With `strictParsing` set to `false` and `maxHeaderSize` unset, no limit applies. A value you set applies whatever `strictParsing` says.
