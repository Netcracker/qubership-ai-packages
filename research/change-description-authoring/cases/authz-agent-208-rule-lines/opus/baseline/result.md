## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose key was not among the loaded keys got TOKEN_KID_UNKNOWN,
both when its source holds no such key and when the keys of the source
could not be loaded. An outage of the identity provider therefore
looked like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load produced no result for the keys of the
source: the load failed, the wait for it ran out, or a limit refused
it. Verify maps that error to the reason code TOKEN_KEYS_UNAVAILABLE,
with the text:

  the keys of iss "<iss>" cannot be loaded, so the token cannot be checked

A JWKS that lacks the key is a result, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a
failed reload, so its keys stay loaded. A token that names a realm
that does not exist keeps TOKEN_KID_UNKNOWN.

A 200 response whose keys member is not an array is now a failed load
and keeps the loaded keys. This includes null, which used to count as
an empty array and removed them.

Seven existing tests now expect ErrKeysUnavailable instead of
ErrKeyUnknown, because the limit or the wait they exercise is the case
this change names.

The packages are not wired into the service yet, so no request is
handled differently.

Implements ADR-0091 R23, R37, R38, and R39.
```

## 2. Pull request title

```text
feat(token): give keys that cannot be loaded a reason code of their own
```

## 3. Pull request description

```markdown
A token whose key is missing from the loaded keys now gets `TOKEN_KEYS_UNAVAILABLE` when the keys of its source could
not be loaded. Before this change it got `TOKEN_KID_UNKNOWN` in both cases, so an outage of the identity provider
looked like a stream of invented tokens.

Implements: ADR-0091 R23, R37, R38, R39
Defers: ADR-0092 R2, ADR-0095 R2, ADR-0095 R16

The deferred rules need the packages wired into the service, and the next change does that wiring. It has no pull
request yet. That change also adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095,
because both depend on the route.

## Stack

This pull request is stacked on #203, which sits on #159, #202, and #201. Merge it after them.

## What changes

- `LookupOrReload` returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load produced no result
  for the keys of the source. That happens when the load failed, the wait for it ran out, or a limit refused it.
- `Verify` maps that error to `TOKEN_KEYS_UNAVAILABLE`, with the text
  `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
- A JWKS that lacks the key is a result and still gives `TOKEN_KID_UNKNOWN`. The same applies to the 404 of a realm
  that holds no keys, and to a token that names a realm that does not exist.
- A realm that held keys returns 404 only on a failed reload, so its keys stay loaded.
- A 200 response whose `keys` member is not an array is a failed load and keeps the loaded keys. This includes `null`,
  which used to count as an empty array and removed them.

The packages are not wired into the service yet, so no request is handled differently.

## Tests

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. The limit or the wait each one
exercises is the case this change names. CI runs `go test ./...` and golangci-lint on every push.
```
