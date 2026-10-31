* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` on every request and closes the socket once the response body is read, so no connection is reused. With the default, the client may reuse a connection for later requests.
  Accepts `true` or `false`. In `relay.properties`, any value other than `true` (case-insensitive) is read as `false`, and no error is reported.
  Because every request opens a new connection, `connectTimeout` applies to every request.
  Set it to `true` when a server or intermediary mishandles reused connections.
