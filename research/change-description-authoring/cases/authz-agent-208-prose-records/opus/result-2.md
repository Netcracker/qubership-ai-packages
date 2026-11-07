## 1. Commit message

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

When no loaded key matched a token, the token got TOKEN_KID_UNKNOWN.
It got that code whether the source of its issuer holds no such key or
could not be asked. An outage of the identity provider therefore looked
like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source.
That covers a failed load, a load whose wait ran out, and a load that a
limit refused. Verify gives this case a reason code of its own, as
ADR-0091 and ADR-0095 decide.

A JWKS that lacks the key is an answer. So is the 404 of a realm that
holds no keys. A realm that held keys returns 404 only when a reload
fails, and its keys stay. A 200 response is a failed load when its
"keys" member is not an array.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
When no loaded key matches and the last load failed, timed out, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable, and Verify rejects the token with TOKEN_KEYS_UNAVAILABLE: `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a 200 JWKS response has a "keys" member that is not an array, null included, the load fails and the keys loaded before stay. null used to count as an empty array and removed them.

Not changed.
A token whose key is missing from a JWKS the source returned, or from a realm that holds no keys and answers 404, keeps TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for tokens whose issuer keys cannot be loaded
```

## 3. Pull request description

```markdown
When no loaded key matches a token, the token gets `TOKEN_KID_UNKNOWN`. It gets that code whether the source of its issuer holds no such key or could not be asked. An outage of the identity provider therefore looks like a stream of invented tokens. ADR-0091 and ADR-0095 give this case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That covers a failed load, a load whose wait ran out, and a load that a limit refused. `Verify` then rejects the token with `TOKEN_KEYS_UNAVAILABLE` and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only when a reload fails, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys. `null` used to count as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` where they expected `ErrKeyUnknown`. Each of them tests a limit or a wait, and that is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
