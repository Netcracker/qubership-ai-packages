## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

`Verify` gave `TOKEN_KID_UNKNOWN` to every token whose kid matched no
loaded key. It did so both when the source held no such key and when
the source could not be asked. As a result, an outage of the identity
provider looked like a stream of invented tokens. The packages are not
wired into the service yet, so no request is handled differently.

`LookupOrReload` now uses the last load of the source to tell the two
cases apart. When no loaded key matches and that load got no answer
about the keys of the source, it returns `keys.ErrKeysUnavailable`.
That happens when the load failed, the wait for it ran out, or a limit
refused it. `Verify` turns the error into its own reason code.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A token that names a realm that does not exist
therefore keeps `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404
only when a reload fails, so that 404 counts as a failed load and the
keys stay.

A 200 response whose `keys` is not an array also counts as a failed
load. `null` used to count as an empty array, so a response with
`"keys": null` removed every loaded key of the source.

User-visible changes.
`Verify` rejects a token with the reason code `TOKEN_KEYS_UNAVAILABLE` and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked` when no loaded key matches and the last load of the keys of its source failed, timed out, or was refused by a limit.
`LookupOrReload` returns `keys.ErrKeysUnavailable` in that case, where it returned `ErrKeyUnknown`.
A 200 response whose `keys` is not an array, `null` included, keeps the keys already loaded, where `null` removed them.

Not changed.
A token whose key the JWKS of its source lacks, or that names a realm that does not exist, keeps `TOKEN_KID_UNKNOWN`.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
`Verify` gave `TOKEN_KID_UNKNOWN` to every token whose kid matched no loaded key. It did so both when the source held no such key and when the source could not be asked. As a result, an outage of the identity provider looked like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` instead of `ErrKeyUnknown` when no loaded key matches and the last load got no answer about the keys of the source. That happens when the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that case as `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. A token that names a realm that does not exist therefore keeps `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only when a reload fails, so that 404 counts as a failed load and the keys stay. A 200 response whose `keys` is not an array, `null` included, also counts as a failed load and keeps the keys already loaded. Before this change, `null` counted as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. The limit or the wait that each of them exercises is the case this change names.

**Scope.** The packages are not wired into the service yet, so no request is handled differently. This pull request is stacked on #203 and merges after it. #203 sits on #159, #202, and #201. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The next change does that wiring, and it has no issue or pull request yet, so these rules have no `Defers:` line. That change also adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095, because they depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
```
