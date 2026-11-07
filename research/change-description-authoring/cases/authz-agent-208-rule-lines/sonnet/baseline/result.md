## 1. Commit message

```text
feat(token): add reason code TOKEN_KEYS_UNAVAILABLE

A token whose key was not found got TOKEN_KID_UNKNOWN, both when the
source holds no such key and when the keys of the source could not be
loaded. An outage of the identity provider therefore looked like a
stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load received no response about the keys of the
source: the load failed, the wait for it ran out, or a limit refused
it. Verify reports it as TOKEN_KEYS_UNAVAILABLE with the text:

    the keys of iss "<iss>" cannot be loaded, so the token cannot be checked

A JWKS that lacks the key is a response about the keys, and so is the
404 of a realm that holds no keys. A realm that held keys returns 404
only on a failed reload, and its keys stay. A token that names a realm
that does not exist keeps TOKEN_KID_UNKNOWN.

A 200 response whose keys is not an array, null included, is now a
failed load and keeps the loaded keys. null used to count as an empty
array and removed them.

Seven existing tests expected ErrKeyUnknown and now expect
ErrKeysUnavailable, because the limit or the wait each one exercises is
a case this change names.

Implements: ADR-0091 R23, R37, R38, R39
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16
```

## 2. Pull request title

```text
feat(token): add reason code TOKEN_KEYS_UNAVAILABLE
```

## 3. Pull request description

```markdown
Implements: ADR-0091 R23, R37, R38, R39
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16

## Why

A token whose key is not found got `TOKEN_KID_UNKNOWN`, both when the source holds no such key and when the keys of the source could not be loaded. An outage of the identity provider therefore looked like a stream of invented tokens.

## What changes

- `LookupOrReload` returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load received no response about the keys of the source: the load failed, the wait for it ran out, or a limit refused it.
- `Verify` reports that error as `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
- A JWKS that lacks the key is a response about the keys, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`.
- A realm that held keys returns 404 only on a failed reload, and its keys stay.
- A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.
- A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the loaded keys. `null` used to count as an empty array and removed them.

The packages this change touches are not wired into the service yet, so no request is handled differently.

## Tests

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each one exercises is a case this change names. CI runs `go test ./...` and golangci-lint on every push.

## Rules deferred

ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The next change does that, and it has no pull request yet. ADR-0095 also lists the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`. They depend on the route, so the wiring change adds them too.

## Merge order

This pull request is stacked on #203, which sits on #159, #202, and #201. It merges after all four.
```
