## 1. Commit message

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

A token whose key is not loaded got TOKEN_KID_UNKNOWN, whether its
source held no such key or could not be asked. During an outage of the
identity provider, every rejection therefore looked like a token that
someone had invented.

LookupOrReload returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that into the reason code TOKEN_KEYS_UNAVAILABLE.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, and its keys stay. A 200 response whose keys is not an array is
a failed load for the same reason; null used to count as an empty array
and removed the keys.

User-visible:
When no loaded key matches and the last load of the keys of iss got no answer, Verify rejects the token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a 200 response has a keys value that is not an array, null included, the load fails and the loaded keys stay. null used to remove them.
When a realm that held keys returns 404 on a reload, the load fails and the loaded keys stay.

Not changed: a token that names a realm that does not exist, a JWKS that lacks the key, and the 404 of a realm that holds no keys keep TOKEN_KID_UNKNOWN.
Not changed: no request is handled differently, because these packages are not wired into the service yet.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2 to [PR #NNNN]; ADR-0095 R2, R16 to [PR #NNNN].
```

## 2. Pull request title

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded
```

## 3. Pull request description

```markdown
A token whose key is not loaded got `TOKEN_KID_UNKNOWN`, whether its source held no such key or could not be asked. During an outage of the identity provider, the rejections therefore read like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array is also a failed load that keeps the keys. `null` used to count as an empty array and removed them, so please check that this is the behavior you want.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait, which is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The wiring change has no pull request yet. It also adds `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which ADR-0095 lists and which depend on the route. Both `[PR #NNNN]` placeholders below, and the two in the commit message, are filled in before the merge.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2 to [PR #NNNN]; ADR-0095 R2, R16 to [PR #NNNN].
```
