* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB (65536 bytes))
  The largest response header block the client accepts, counting the status line and the headers, in bytes.
  Accepts a byte count with an optional suffix, such as `100`, `64k`, or `2M`. Suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it when a server sends large cookies or tokens in headers and responses exceed 64 KiB. A value you set applies whatever `strictParsing` is; the built-in limit is the one `strictParsing=false` turns off.
