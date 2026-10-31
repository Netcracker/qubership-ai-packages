* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` with every request and closes the socket once the response body is read, so no connection is reused.
  In `relay.properties`, any value other than `true` (case-insensitive) is read as `false`, and no value is rejected.
