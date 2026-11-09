## 1. Commit message

```text
feat(token): reject with TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

Before this change, a token whose key was not found got
TOKEN_KID_UNKNOWN in two cases: when its source holds no such key, and
when the source could not be asked. An outage of the identity provider
therefore reads like a stream of invented tokens.

LookupOrReload now tells the two cases apart by the result of the last
load of the source's keys. A JWKS that lacks the key is an answer. The
404 of a realm that holds no keys is also an answer. A realm that held
keys returns 404 only on a failed reload, and its keys stay. A failed
load gives no answer. Neither does a wait for a load that runs out, nor
a load that a limit refuses.

User-visible changes.
When no loaded key matches and the last load of the source's keys failed, ran out of time, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown.
In that case, Verify rejects the token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose `keys` is not an array, `null` included, counts as a failed load and keeps the keys already loaded; `null` used to count as an empty array and removed them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
The service handles every request as before, because these packages are not wired into it yet.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): reject with TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded
```

## 3. Pull request description

````markdown
Before this change, a token whose key was not found got `TOKEN_KID_UNKNOWN` in two cases: when its source holds no such key, and when the source could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the source's keys. That covers a load that failed, a wait for a load that ran out, and a load that a limit refused. `Verify` turns this error into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer. The 404 of a realm that holds no keys is also an answer. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load that keeps the loaded keys. Before, `null` counted as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. The packages are not wired into the service yet, so the service handles every request as before.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because each one exercises a limit or a wait, which is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after all four. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. They wait for the wiring change, which has no issue or pull request yet, so no `Defers:` line lists them. That change also adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` from ADR-0095, because both depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
````
