## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

A token that found no key got TOKEN_KID_UNKNOWN, whether its source
held no such key or could not be asked. During an outage of the
identity provider every token therefore looked invented.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. A JWKS
that lacks the key is an answer, and so is the 404 of a realm that
holds no keys. A realm that held keys returns 404 only on a failed
reload, so its keys stay.

A 200 response whose keys is not an array is now a failed load too.
null used to count as an empty array and removed the loaded keys.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
When no loaded key matches and the last load of the keys of the source failed, ran out of wait, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable and Verify reports the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and the loaded keys stay; null used to count as an empty array and removed them.
A 404 from a realm that held keys is a failed reload and its keys stay.

Not changed.
A JWKS that lacks the key, the 404 of a realm that holds no keys, and a token that names a realm that does not exist all keep TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

````markdown
A token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that as `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so its keys stay. A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the keys; `null` used to count as an empty array and removed them. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The next change does that and has no pull request yet, so those rules are not in `Defers:`. That change also adds the ADR-0095 reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
````
