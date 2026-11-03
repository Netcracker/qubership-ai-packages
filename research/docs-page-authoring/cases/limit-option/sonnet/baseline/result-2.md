* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB (65536 bytes))
  The largest response header block the client accepts, counting the bytes of the status line and the headers.
  Accepts `100`, `64k`, or `2M`. A bare number is bytes, and the suffixes are binary, so `64k` is 65536 bytes.
  The limit applies to every response, and the client reads it once, when `RelayClient.create` is called.
  Past the limit, the request fails with `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the client closes the connection.
  Raise it when a server puts large cookies or tokens in headers and responses exceed 64 KiB.
  With `maxHeaderSize` unset, `strictParsing=false` turns off the built-in limit. A value you set applies whatever `strictParsing` says.
  Since TBD.
