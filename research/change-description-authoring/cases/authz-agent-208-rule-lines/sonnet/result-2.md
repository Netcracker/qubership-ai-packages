## 1. Commit message

```text
feat(token): add reason code TOKEN_KEYS_UNAVAILABLE for unloadable keys

A token that finds no key got TOKEN_KID_UNKNOWN, whether its source holds
no such key or could not be asked. An outage of the identity provider
therefore read like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source: the
load failed, the wait for it ran out, or a limit refused it. A JWKS that
lacks the key is an answer, and so is the 404 of a realm that holds no
keys. A realm that held keys returns 404 only on a failed reload, so that
404 counts as a failed load and the keys stay. A 200 response whose keys
is not an array is a failed load too; null used to count as an empty array
and removed the keys.

User-visible:
LookupOrReload returns keys.ErrKeysUnavailable when no loaded key matches and the last load failed, ran out of wait, or was refused by a limit.
Verify reports the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys.

Not changed:
A JWKS that lacks the key, and the 404 of a realm that holds no keys, still give TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist still gets TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN].
```

## 2. Pull request title

```text
feat(token): add reason code TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded
```

## 3. Pull request description

````markdown
Before this change, a token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so that 404 counts as a failed load and its keys stay. A 200 response whose `keys` is not an array, `null` included, is also a failed load that keeps the keys. `null` used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names, so `ErrKeysUnavailable` is the new correct result for them.

**Scope.** This is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need that wiring, which the next change does. That change has no pull request yet, so `Defers:` carries the placeholder `[PR #NNNN]`. Replace it with the real number in this description and in the commit message before the merge. ADR-0095 also lists the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`. They depend on the route, so the wiring change adds them too.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN].
````
