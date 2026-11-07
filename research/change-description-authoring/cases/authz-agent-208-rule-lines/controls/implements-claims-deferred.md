## Commit message

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

A token that found no key got TOKEN_KID_UNKNOWN, whether its source held
no such key or could not be asked. During an outage of the identity
provider, every token therefore looked invented instead of unverifiable.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that error into the reason code TOKEN_KEYS_UNAVAILABLE.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, so that 404 counts as a failed load and the keys stay. A 200
response whose keys is not an array is a failed load too.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown when no loaded key matches and the last load failed, ran out of wait time, or was refused by a limit.
Verify returns the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked` in that case.
A 200 response whose keys is not an array, null included, is a failed load and the loaded keys stay; null used to count as an empty array and removed them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN, as does a token whose key is absent from a JWKS or from a realm that holds no keys.

Implements: ADR-0091 R23, R37, R38, R39; ADR-0092 R2
```

## Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## Pull request description

```markdown
A token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys; both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so that 404 is a failed load and its keys stay. A 200 response whose `keys` is not an array is a failed load that keeps the keys. `null` is included: it used to count as an empty array and removed them.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names as unavailable.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service, so no request is handled differently. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need that wiring, which the next change does. That change has no pull request or issue yet, so those rules are not in the trailers. The same change adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095, because they depend on the route.

Implements: ADR-0091 R23, R37, R38, R39; ADR-0092 R2
```
