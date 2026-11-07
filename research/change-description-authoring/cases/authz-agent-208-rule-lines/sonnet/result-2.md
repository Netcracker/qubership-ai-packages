## 1. Commit message

```text
feat(token): reject with TOKEN_KEYS_UNAVAILABLE when issuer keys cannot be loaded

A token whose key is not loaded got TOKEN_KID_UNKNOWN, whether the
issuer's key source held no such key or could not be reached. During an
outage of the identity provider, every token therefore looked like an
invented one, and nothing told the operator that the keys were the
problem.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load of the source's keys failed, the wait for it
timed out, or a limit refused it. Verify reports that as the reason code
TOKEN_KEYS_UNAVAILABLE. A JWKS that lacks the key is a valid response and
still ends in TOKEN_KID_UNKNOWN, as does the 404 of a realm that holds
no keys.

A 200 response whose keys member is not an array is now a failed load
too. null used to count as an empty array and removed the loaded keys, so
a malformed response could empty a working key set.

User-visible changes.
When no loaded key matches and the last load of the keys of iss failed, timed out, or was refused by a limit, Verify rejects the token with reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, and LookupOrReload returns keys.ErrKeysUnavailable.
A 200 response whose keys is not an array, null included, is a failed load, and the keys already loaded stay. null used to remove them.
A 404 for a realm that held keys is a failed reload, and its keys stay.

Not changed.
A token whose key is absent from a JWKS that was loaded, a token that names a realm with no keys (404), and a token that names a realm that does not exist keep TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): reject with TOKEN_KEYS_UNAVAILABLE when issuer keys cannot be loaded
```

## 3. Pull request description

```markdown
A token whose key is not loaded got `TOKEN_KID_UNKNOWN`, whether the issuer's key source held no such key or could not be reached. During an outage of the identity provider, every token therefore looked like an invented one.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load of the source's keys failed, the wait for it timed out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. These stay `TOKEN_KID_UNKNOWN`: a JWKS that lacks the key, the 404 of a realm that holds no keys, and a token that names a realm that does not exist. A 404 for a realm that held keys is a failed reload, and its keys stay. A 200 response whose `keys` is not an array is a failed load and keeps the loaded keys. `null` used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait, which is the case this change names.

**Scope.** Stacked on #203, which sits on #159, #202, and #201. This pull request merges after all three. The packages it touches are not wired into the service yet, so no request is handled differently. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need that wiring, which the next change does. That change has no pull request or issue yet, so those rules are not in the `Defers:` line. The reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` depend on the route, so the wiring change adds them too.

Implements: ADR-0091 R23, R37, R38, R39
```
