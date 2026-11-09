## Commit message

````text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

A token whose key is not found got TOKEN_KID_UNKNOWN, whether the key
source held no such key or could not be asked. An outage of the identity
provider therefore reads like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source.
Verify turns that into its own reason code, as ADR-0091 and ADR-0095
call for. A JWKS that lacks the key is an answer, and so is the 404 of a
realm that holds no keys, so both stay TOKEN_KID_UNKNOWN. A realm that
held keys returns 404 only on a failed reload, and its keys stay.

A 200 response whose keys is not an array is a failed load too. null used
to count as an empty array and removed the loaded keys.

User-visible changes.
When no loaded key matches and the last load of the keys of the source failed, ran out of wait time, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable and Verify reports TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a 200 response has a keys value that is not an array, null included, the load counts as failed and the loaded keys stay.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
````

## Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## Pull request description

````markdown
When a token's key is not found, `Verify` gave `TOKEN_KID_UNKNOWN`, whether the source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 give this case a reason code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, so both keep `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only on a failed reload, and its keys stay. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.

A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the loaded keys. `null` used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the wait each one exercises is the case this change names.

**Scope.** This branch is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
````
