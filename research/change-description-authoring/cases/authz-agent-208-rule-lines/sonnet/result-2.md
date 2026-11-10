## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

A token whose key matched no loaded key got TOKEN_KID_UNKNOWN, whether
its source held no such key or could not be asked. An outage of the
identity provider therefore read like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that into TOKEN_KEYS_UNAVAILABLE. A JWKS that lacks the key is an
answer, and so is the 404 of a realm that holds no keys. A 404 from a
realm that held keys counts as a failed reload, and its keys stay.

A 200 response whose keys is not an array is now a failed load too.
null used to count as an empty array and removed the loaded keys.

Seven existing tests changed their expectation from ErrKeyUnknown to
ErrKeysUnavailable, because the limit or the wait they exercise is a
case this change names.

User-visible changes.
When no loaded key matches and the last load got no answer about the keys of the source, LookupOrReload returns keys.ErrKeysUnavailable and Verify reports TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and keeps the loaded keys.

Not changed.
A token whose JWKS lacks the key, or whose realm holds no keys and returns 404, still gets TOKEN_KID_UNKNOWN, as does a token that names a realm that does not exist.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
A token that finds no key got `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys; both keep `TOKEN_KID_UNKNOWN`, as does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so that case is a failed load and its keys stay.

A 200 response whose `keys` is not an array, `null` included, is also a failed load and keeps the loaded keys. `null` used to count as an empty array and removed them.

The packages this change touches are not wired into the service yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait, which is a case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The next change does that, and it has no pull request yet, so those rules are not in `Defers:`. ADR-0095 also lists the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`. They depend on the route, so the wiring change adds them too.

Implements: ADR-0091 R23, R37, R38, R39
```
