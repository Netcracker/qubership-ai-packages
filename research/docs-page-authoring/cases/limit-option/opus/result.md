```markdown
* **`maxHeaderSize`** (size, default: unset, which applies a built-in limit of 64 KiB)
  The largest response header block the client accepts, counting the status line and every header.
  Accepts a byte count or a `k` or `M` suffix: `100`, `64k`, `2M`. Suffixes are binary, so `64k` is 65536 bytes.
  Past the limit, the request fails with
  `RelayProtocolException: response headers exceed maxHeaderSize of <limit> bytes; raise maxHeaderSize`, and the
  client closes the connection.
  Raise it for servers that send large cookies or tokens in headers. A value you set applies whatever `strictParsing`
  says. With `strictParsing` set to `false` and `maxHeaderSize` unset, no limit applies.
```
