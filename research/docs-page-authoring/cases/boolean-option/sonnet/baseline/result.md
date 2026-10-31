* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` on every request and closes the connection after the response body is read, so no connection is reused. Each request opens a new TCP connection, and `connectTimeout` applies to each one.
  Accepts `true`, case-insensitive. Any other value, including a misspelling, is read as `false`, and the client reports no error.
  Set it when a server or proxy between the client and the server mishandles reused connections. Leave it at `false` otherwise, because a new connection per request adds a TCP handshake to each one.
