**Commit message**

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token for which no key was found got TOKEN_KID_UNKNOWN, whether the
source of the keys holds no such key or could not be reached. An outage
of the identity provider therefore looked like a stream of tokens with
invented key IDs.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load did not establish what keys the source holds:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that error into its own reason code. ADR-0091 and ADR-0095 give
this case a code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, so that 404 is a failed load and the keys stay. A 200 response
whose keys is not an array is a failed load as well. null used to count
as an empty array and removed the loaded keys.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable when no loaded key matches and the last load failed, the wait for it ran out, or a limit refused it.
Verify returns the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked` in that case.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys; null used to count as an empty array and removed them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

**Pull request title**

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of a token's issuer cannot be loaded
```

**Pull request description**

````markdown
A token whose key is not found got `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be reached. An outage of the identity provider therefore looks like a stream of tokens with invented key IDs. ADR-0091 and ADR-0095 give the unreachable case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load did not establish what keys the source holds: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys; a realm that held keys returns 404 only on a failed reload, so that 404 is a failed load and the keys stay. A 200 response whose `keys` is not an array is also a failed load that keeps the keys. `null` used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait, which is the case this change names, so none of them was narrowed.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. The rest of ADR-0095 comes with the change that wires the packages into the service, which has no pull request yet. That includes the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, because they depend on the route.
````
