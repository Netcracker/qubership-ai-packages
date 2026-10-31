* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` on every request and closes the socket once the response body is read, so each request opens a new connection.
  Any value other than `true` (case-insensitive) in `relay.properties` is read as `false`, and the client rejects none.
