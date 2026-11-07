## 1. Commit message

````text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

A token that finds no key got TOKEN_KID_UNKNOWN, whether its source holds
no such key or could not be asked. During an outage of the identity
provider, every token therefore read like an invented one. ADR-0091 and
ADR-0095 give the second case a reason code of its own. The packages are
not wired into the service yet, so no request is handled differently.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source: the
load failed, the wait for it ran out, or a limit refused it. Verify turns
that error into the reason code. A JWKS that lacks the key is an answer,
and so is the 404 of a realm that holds no keys. A realm that held keys
returns 404 only on a failed reload, so that 404 is a failed load and the
keys stay.

A 200 response whose keys is not an array is also a failed load that
keeps the keys. null used to count as an empty array and removed them.

User-visible:
LookupOrReload returns keys.ErrKeysUnavailable when no loaded key matches and the last load failed, timed out, or was refused by a limit.
Verify reports that case as TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load, and the loaded keys stay.

Not changed:
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
````

## 2. Pull request title

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded
```

## 3. Pull request description

````markdown
When a token finds no key, `Verify` gave `TOKEN_KID_UNKNOWN`, whether the source of keys holds no such key or could not be asked. During an outage of the identity provider, every token therefore read like an invented one. ADR-0091 and ADR-0095 give the second case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that as `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. A realm that held keys returns 404 only on a failed reload, so that 404 counts as a failed load and its keys stay. A 200 response whose `keys` is not an array is a failed load too and keeps the keys; `null` used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is the case this change names, so the old expectation no longer describes it.

**Scope.** These packages are not wired into the service yet, so no request is handled differently. The change that wires them in brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route. That change has no pull request yet. This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them.
````
