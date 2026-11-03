* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` with every request, so the client never reuses a connection. The client closes each
  connection once the response body is read, and the next request opens a new one.
  In `relay.properties`, `true` in any letter case turns it on. Any other value, including a misspelling, is read as
  `false` without an error.
  Set it to `true` when a server or a proxy mishandles connections that stay open between requests. Each request then
  opens its own TCP connection.
