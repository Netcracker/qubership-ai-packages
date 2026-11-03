* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` on every request and closes the connection once the response body is read, so no connection is reused.
  In `relay.properties`, any value other than `true` (case-insensitive) is read as `false`.
