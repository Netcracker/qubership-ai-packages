## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

Before this change, a token that matched no loaded key got
TOKEN_KID_UNKNOWN in both cases: when the source of its issuer holds no
such key, and when the source could not be asked. An outage of the
identity provider therefore reads like a stream of invented tokens.

LookupOrReload now separates an answer from a missing answer. A JWKS
that lacks the key is an answer, and so is the 404 of a realm that holds
no keys. A load that failed, ran out of time, or was refused by a limit
is not an answer. ADR-0091 and ADR-0095 give that case a reason code of
its own. A realm that held keys returns 404 only on a failed reload, so
that 404 keeps the keys already loaded.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose keys is not an array, null included, is a failed load and keeps the keys already loaded; null used to count as an empty array and removed them.

Not changed.
A token whose key the JWKS lacks, or that names a realm that does not exist, keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): give keys that cannot be loaded the reason code TOKEN_KEYS_UNAVAILABLE
```

## 3. Pull request description

```markdown
Before this change, `Verify` gave a token that matched no loaded key `TOKEN_KID_UNKNOWN` in both cases: when the source of its issuer holds no such key, and when the source could not be asked. An outage of the identity provider therefore reads like a stream of invented tokens. ADR-0091 and ADR-0095 give the second case a reason code of its own. The packages are not wired into the service yet, so no request is handled differently.

`LookupOrReload` returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That happens when the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that error into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. A token in either case keeps `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, so its keys stay. A 200 response whose `keys` is not an array is now a failed load and keeps the keys. `null` used to count as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. The limit or the wait each of them exercises is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The rest of ADR-0095 is left to the change that wires these packages into the service, which has no pull request yet. That includes the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
