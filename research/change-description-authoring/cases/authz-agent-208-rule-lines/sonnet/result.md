## Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose kid matches no loaded key got TOKEN_KID_UNKNOWN, whether
its source holds no such key or could not be reached. An outage of the
identity provider therefore read like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load produced no key set for the source: the load
failed, the wait for it ran out, or a limit refused it. Verify reports
that as TOKEN_KEYS_UNAVAILABLE. A JWKS that lacks the key is a result,
and so is the 404 of a realm that holds no keys, so both still end in
ErrKeyUnknown. A realm that held keys returns 404 only on a failed
reload, and its keys stay.

A 200 response whose keys is not an array is a failed load too and keeps
the keys. null used to count as an empty array and removed them.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
When no loaded key matches the kid and the last load of the keys of iss failed, ran out of wait, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a 200 response has a keys value that is not an array, null included, the load counts as failed and the loaded keys stay.

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
A token whose kid matches no loaded key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be reached. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load produced no key set for the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that as `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is a result, and so is the 404 of a realm that holds no keys, so both still give `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the keys; `null` used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. Nothing in the service calls these packages yet, so no request is handled differently.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names, so the old expectation no longer described it.

**Scope.** This branch is stacked on #203, which sits on #159, #202, and #201, and merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The wiring change covers them, has no pull request or issue yet, and so these rules are not in the trailers. It also adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095, which depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
```
