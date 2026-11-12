The reference page `docs/configuration.md` of the Java HTTP client library `relay-client` documents its client
properties. The part of the page around the new entry, as it stands on the branch:

```markdown
## Client properties

Every property below is set on a `RelayConfig` builder or in `relay.properties`, and applies to every request the
client sends. The client reads them once, when `RelayClient.create` is called.

* **`connectTimeout`** (duration, default: `10s`)
  How long the client waits for a TCP connection to open. Accepts `ms`, `s`, and `m` suffixes; a bare number is
  milliseconds. `0` waits forever.
  Past the timeout, the request fails with `RelayConnectException: connect timed out after 10000 ms`.

* **`followRedirects`** (boolean, default: `true`)
  Follows `3xx` responses to the `Location` they name, up to five hops.

* **`gzip`** (boolean, default: `true`)
  Sends `Accept-Encoding: gzip` and decompresses gzip response bodies.

* **`strictParsing`** (boolean, default: `true`)
  Rejects a response whose status line or headers break RFC 9112. Set it to `false` to accept the malformed
  responses some legacy servers send; it also turns off the built-in `maxHeaderSize` limit.

* **`userAgent`** (string, default: `relay-client/<version>`)
  The `User-Agent` header sent with every request.
```

The entries are in alphabetical order. No entry on the page carries a version marker.
