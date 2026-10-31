* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` with every request and closes the connection once the response body is read, so no connection is reused.
  In `relay.properties`, any value other than `true`, matched case-insensitively, is read as `false`.
