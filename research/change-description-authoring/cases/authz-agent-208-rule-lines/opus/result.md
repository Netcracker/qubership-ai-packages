## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded

A token whose key was not found got TOKEN_KID_UNKNOWN in two cases: the
source held no such key, or the source could not be asked. During an
outage of the identity provider, every token therefore looked as if it
named a key that does not exist.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source.
That covers a failed load, a wait for the load that ran out, and a load
that a limit refused. A JWKS that lacks the key is an answer, and so is
the 404 of a realm that holds no keys; both keep TOKEN_KID_UNKNOWN. A
realm that held keys returns 404 only when a reload fails, so its keys
stay.

A 200 response whose keys member is not an array is a failed load. This
includes null, which used to count as an empty array.

User-visible:
Verify returns the reason code TOKEN_KEYS_UNAVAILABLE, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, when no loaded key matches and the last load of the keys of that iss failed, ran out of time, or was refused by a limit.
A 200 JWKS response whose keys is not an array, null included, keeps the keys already loaded. A null keys used to remove them.
Not changed:
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
The service handles every request as before, because the packages this commit changes are not wired into it yet.

Implements: ADR-0091 R23, R37, R38, R39
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN]
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
A token whose key was not found got `TOKEN_KID_UNKNOWN` in two cases: the source held no such key, or the source could not be asked. During an outage of the identity provider, every token therefore looked as if it named a key that does not exist.

`Verify` now returns the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, when no loaded key matches and the last load got no answer about the keys of the source. That covers a failed load, a wait for the load that ran out, and a load that a limit refused. `LookupOrReload` reports this case as `keys.ErrKeysUnavailable`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, so both keep `TOKEN_KID_UNKNOWN`. A token that names a realm that does not exist also keeps `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only when a reload fails, so its keys stay. A 200 response whose `keys` is not an array is now a failed load and keeps the loaded keys. This includes `null`, which used to count as an empty array and removed them.

The packages are not wired into the service yet, so the service handles every request as before.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. The limit or the wait each one exercises is the case this change gives its own error.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The rules below need the packages wired into the service. The next change does that, and it also adds the route-dependent reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095. That change has no pull request yet. Replace `[PR #NNNN]` with its number here and in the commit message before the merge.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16 to [PR #NNNN].
```
