## 1. Commit message

```text
feat(token): report keys that cannot be loaded as TOKEN_KEYS_UNAVAILABLE

A token that found no key got TOKEN_KID_UNKNOWN, whether the source of
its issuer holds no such key or could not be asked. An outage of the
identity provider was therefore reported as a stream of invented tokens.

The source could not be asked when the last load got no answer about
its keys: the load failed, the wait for it ran out, or a limit refused
it.

The two cases now differ by whether the last load got an answer about
the keys of the source. A JWKS that lacks the key is an answer, and so
is the 404 of a realm that holds no keys. A realm that held keys
returns 404 only on a failed reload, and its keys stay.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable, where it returned ErrKeyUnknown, when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the loaded keys; `null` used to count as an empty array and removed them.

Not changed.
A token whose key the JWKS lacks, or that names a realm that does not exist, keeps TOKEN_KID_UNKNOWN.
The service handles every request as before, because the packages this change touches are not wired into it yet.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report unloadable keys as TOKEN_KEYS_UNAVAILABLE, not TOKEN_KID_UNKNOWN
```

## 3. Pull request description

```markdown
A token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider is therefore reported as a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer and keeps `TOKEN_KID_UNKNOWN`, and so is the 404 of a realm that holds no keys. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys; `null` used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait each one exercises is the case this change names.

**Scope.** This is stacked on #203, which sits on #159, #202, and #201, and it merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. They wait for the change that wires them, and that change has no issue or pull request yet. The same change adds the ADR-0095 reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, because they depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
```
