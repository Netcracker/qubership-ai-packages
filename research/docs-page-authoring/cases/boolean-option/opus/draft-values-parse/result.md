* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` with every request and closes the connection once the response body is read, so each
  request opens a new connection.
