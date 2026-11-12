* **`disableKeepAlive`** (boolean, default: `false`)
  Sends `Connection: close` on every request and closes the connection once the response body is read, so each request opens a new connection. Any value other than `true`, in any letter case, is read as `false`.
