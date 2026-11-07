## Commit message

````text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose key is not loaded got TOKEN_KID_UNKNOWN, whether the key
source holds no such key or could not be queried. During an outage of the
identity provider, every token therefore looked invented.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source: the
load failed, the wait for it ran out, or a limit refused it. Verify turns
that into the reason code TOKEN_KEYS_UNAVAILABLE.

Two kinds of response count as an answer, so the keys of the source stay
as they are or are removed: a JWKS that lacks the key, and the 404 of a
realm that holds no keys. A realm that held keys returns 404 only on a
failed reload, and its keys stay. A 200 response whose keys is not an
array is a failed load and keeps the keys; null used to count as an empty
array and removed them.

User-visible:
When no loaded key matches and the keys of the source cannot be loaded, Verify returns the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is null or any other non-array leaves the loaded keys in place; null used to remove them.
Not changed: a token whose JWKS lacks its key, or that names a realm that does not exist, keeps TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39; ADR-0092 R2.
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN].
````

## Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## Pull request description

````markdown
A token whose key is not loaded got `TOKEN_KID_UNKNOWN`, whether the key source holds no such key or could not be queried. During an outage of the identity provider, every token therefore looked invented.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array is a failed load and keeps the keys; `null` used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names, so the old expectation no longer holds.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. The reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which ADR-0095 also lists, depend on the route, so the wiring change adds them. That change has no pull request yet. The `[PR #NNNN]` placeholder below stands for it and is filled in, here and in the commit message, before the merge.

Implements: ADR-0091 R23, R37, R38, R39; ADR-0092 R2.
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN].
````
