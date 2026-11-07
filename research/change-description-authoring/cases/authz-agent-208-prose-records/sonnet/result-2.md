## 1. Commit message

````text
feat(token): give keys that cannot be loaded a reason code of their own

When a token's key ID matches no loaded key, Verify reported
TOKEN_KID_UNKNOWN, whether the key source holds no such key or could not
be read. During an outage of the identity provider, every token
therefore looked invented, and the operator saw a stream of unknown key
IDs instead of an unreachable provider.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load did not obtain the keys of the source: the
load failed, the wait for it ran out, or a limit refused it. Verify
maps that error to TOKEN_KEYS_UNAVAILABLE. ADR-0091 and ADR-0095 give
this case a reason code of its own.

A JWKS that lacks the key is a complete result, and so is the 404 of a
realm that holds no keys; both stay ErrKeyUnknown. A realm that held
keys and returns 404 on a reload is a failed reload, and its keys stay.
A 200 response whose keys is not an array is a failed load as well.
null used to count as an empty array and removed the loaded keys.

User-visible:
When no loaded key matches and the last load failed, ran out of wait, or was refused by a limit, Verify returns the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, and LookupOrReload returns keys.ErrKeysUnavailable.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys; null used to remove them.

Not changed:
A JWKS that lacks the key, and the 404 of a realm that holds no keys, still give TOKEN_KID_UNKNOWN (keys.ErrKeyUnknown).
A token that names a realm that does not exist still gives TOKEN_KID_UNKNOWN.
````

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

````markdown
A token whose key ID matches no loaded key got `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be read. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load did not obtain the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 give this case a reason code of its own.

A JWKS that lacks the key is a complete result, and so is the 404 of a realm that holds no keys; both keep `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only on a failed reload, and its keys stay. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. A 200 response whose `keys` is not an array is a failed load and keeps the keys. `null` used to count as an empty array and removed them, which is the one behavior here that changes how loaded keys are kept.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the wait each of them exercises is the case this change names.

**Scope.** This change merges after #203, which is stacked on #159, #202, and #201. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
````
