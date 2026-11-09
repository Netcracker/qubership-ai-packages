## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token that finds no key got TOKEN_KID_UNKNOWN, whether its source
holds no such key or could not be asked. An outage of the identity
provider therefore read like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that into the reason code TOKEN_KEYS_UNAVAILABLE.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, so that response is a failed load and the keys stay. A 200
response whose keys is not an array is a failed load too; null used to
count as an empty array and removed the keys.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown when no loaded key matches and the last load failed, ran out of wait, or was refused by a limit.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 404 on the reload of a realm that held keys leaves those keys loaded.
A 200 response whose keys is not an array, null included, is a failed load and leaves the loaded keys in place, where null used to remove them.

Not changed.
A JWKS that lacks the key, the 404 of a realm that holds no keys, and a token that names a realm that does not exist still give TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): give keys that cannot be loaded the reason code TOKEN_KEYS_UNAVAILABLE
```

## 3. Pull request description

```markdown
**Breaking changes.** Code that calls `LookupOrReload` and matches `keys.ErrKeyUnknown` now gets `keys.ErrKeysUnavailable` when no loaded key matches and the last load failed, ran out of wait, or was refused by a limit. Such callers must handle `ErrKeysUnavailable`.

A token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys; both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so that response is a failed load and its keys stay. A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the keys; `null` used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the wait they exercise is the case this change names.

**Scope.** The packages this change touches are not wired into the service yet, so no request is handled differently. This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service, which the next change does. That change has no pull request or issue yet, so these rules are not in a `Defers:` line. The same change adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` that ADR-0095 lists, because they depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
```
