## Commit message

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

When no loaded key matched a token, Verify gave TOKEN_KID_UNKNOWN,
whether the source held no such key or could not be asked. During an
outage of the identity provider, every token with a key ID that was
not loaded therefore looked invented.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no result about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. A
JWKS that lacks the key is a result, and so is the 404 of a realm that
holds no keys, so both stay TOKEN_KID_UNKNOWN. A 404 for a realm that
held keys is a failed reload and keeps its keys.

A 200 response whose keys is not an array is a failed load too. null
used to count as an empty array, so it removed the loaded keys.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown when no loaded key matches and the last load failed, ran out of wait, or was refused by a limit.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys; null used to remove them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
```

## Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## Pull request description

```markdown
When no loaded key matches a token, `Verify` gives `TOKEN_KID_UNKNOWN`, whether the source holds no such key or could not be asked. During an outage of the identity provider, every token with a key ID that is not loaded therefore looks invented.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no result about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that as `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is a result, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A 404 for a realm that held keys is a failed reload, and its keys stay. A 200 response whose `keys` is not an array is also a failed load that keeps the keys; `null` used to count as an empty array and removed them. These packages are not wired into the service yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the wait each one exercises is a case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service, which the next change does. That change has no issue or pull request yet, so these rules are not in `Defers:` and will be added once it has one. The reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095 depend on the route, so the wiring change adds them too. The squash message is the title alone, so paste the trailer below into the body of the squash commit.

Implements: ADR-0091 R23, R37, R38, R39
```
