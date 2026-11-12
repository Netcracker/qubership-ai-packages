## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

When a token's key was not found, Verify gave it TOKEN_KID_UNKNOWN,
whether the source of the keys held no such key or the load of its keys
got no answer. During an outage of the identity provider, the result was
a stream of TOKEN_KID_UNKNOWN that reads like a stream of invented
tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that into the reason code TOKEN_KEYS_UNAVAILABLE. ADR-0091 and
ADR-0095 give this case a reason code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, so that response is a failed load and the keys stay.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown when no loaded key matches and the last load of the keys of the source failed, ran out of wait, or was refused by a limit.
Verify reports the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys; null used to count as an empty array and removed them.

Not changed.
A token whose JWKS lacks the key, whose realm holds no keys (404), or whose realm does not exist still gets TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

````markdown
A token whose key is not found gets `TOKEN_KID_UNKNOWN`, whether the source holds no such key or its keys could not be loaded. During an outage of the identity provider, that reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 give this case a reason code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, so both keep `TOKEN_KID_UNKNOWN`. So does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, which is a failed load and keeps its keys. A 200 response whose `keys` is not an array, `null` included, is also a failed load that keeps the keys. `null` used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`: the limit or the wait each one exercises is a case this change names.

**Scope.** Stacked on #203, which sits on #159, #202, and #201; merge this after all four. The packages are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
````
