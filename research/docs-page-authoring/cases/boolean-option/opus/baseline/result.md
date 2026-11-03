* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` with every request and closes the connection once the response body is read, so each
  request opens a new connection and none is reused. In `relay.properties`, `true` in any letter case turns it on.
  Any other value, including a misspelling, is read as `false` without an error.
  Set it to `true` for a server or proxy that mishandles persistent connections. Each request then waits for a new TCP
  connection to open, up to `connectTimeout`.
