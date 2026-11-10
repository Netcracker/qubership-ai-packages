## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose key was not found got TOKEN_KID_UNKNOWN in two cases: when
the source of its issuer holds no such key, and when the source could not
be asked. An outage of the identity provider therefore looked like a
stream of forged tokens.

ADR-0091 and ADR-0095 give the second case a reason code of its own.
LookupOrReload now keeps the two cases apart by what the last load got
from the source. A JWKS that lacks the key is an answer about the keys
of the source, and so is the 404 of a realm that holds no keys. A load
that failed, a wait for a load that ran out, and a load that a limit
refused got no answer. A realm that held keys returns 404 only on a
failed reload, and its keys stay.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown when no loaded key matches and the last load failed, the wait for it ran out, or a limit refused it.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose `keys` is not an array, `null` included, counts as a failed load and keeps the loaded keys; `null` used to count as an empty array and removed them.

Not changed.
A token keeps TOKEN_KID_UNKNOWN when the JWKS lacks its key, when its realm holds no keys and returns 404, or when its realm does not exist.
No request the service handles gets a different result, because these packages are not wired into the service yet.
```

## 2. Pull request title

```text
feat(token): return TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
A token that finds no key gets `TOKEN_KID_UNKNOWN` in two cases: when the source of its issuer holds no such key, and when the source could not be asked. An outage of the identity provider therefore looks like a stream of forged tokens. ADR-0091 and ADR-0095 give the second case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That covers three cases: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns this error into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, so both cases keep `TOKEN_KID_UNKNOWN`. A token that names a realm that does not exist keeps it too. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, now counts as a failed load and keeps the loaded keys. `null` used to count as an empty array and removed them. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait that each one exercises is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. The rest of ADR-0095 is left out, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route. It comes with the change that wires the packages into the service, and that change has no pull request yet.
```
