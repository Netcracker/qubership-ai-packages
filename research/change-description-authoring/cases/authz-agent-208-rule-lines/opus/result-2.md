## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

Before this change, a token that found no key got TOKEN_KID_UNKNOWN in
two cases: when its source held no such key, and when its source could
not be asked. An outage of the identity provider therefore looked like
a stream of tokens with invented key IDs.

LookupOrReload now separates the two cases by the outcome of the last
load of the source's keys. A JWKS that lacks the key is an answer, and
so is the 404 of a realm that holds no keys. A realm that held keys
returns 404 only on a failed reload, and its keys stay.

User-visible changes.
When no loaded key matches and the last load of the source's keys failed, ran out of time, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable instead of ErrKeyUnknown.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the loaded keys; `null` used to count as an empty array and removed them.

Not changed.
A token whose key is missing from the JWKS, whose realm holds no keys, or whose realm does not exist keeps TOKEN_KID_UNKNOWN.
The service handles every request as before, because the token packages are not wired into it yet.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of a source cannot be loaded
```

## 3. Pull request description

````markdown
Before this change, a token that finds no key gets `TOKEN_KID_UNKNOWN` in two cases: when its source holds no such key, and when its source could not be asked. An outage of the identity provider therefore looks like a stream of tokens with invented key IDs.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. This covers a failed load, a wait for the load that ran out, and a load that a limit refused. `Verify` rejects such a token with the reason code `TOKEN_KEYS_UNAVAILABLE` and this text:

```text
the keys of iss "<iss>" cannot be loaded, so the token cannot be checked
```

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys. Before, `null` counted as an empty array and removed them. The packages are not wired into the service yet, so the service handles every request as before.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. Each one exercises a limit or a wait, and that is the case this change names.

**Scope.** This branch is stacked on #203, which sits on #159, #202, and #201, and it merges after all four. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The next change does the wiring, but it has no pull request yet, so this description has no `Defers:` line. ADR-0095 also lists the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route, so the wiring change adds them as well.

Implements: ADR-0091 R23, R37, R38, R39
````
