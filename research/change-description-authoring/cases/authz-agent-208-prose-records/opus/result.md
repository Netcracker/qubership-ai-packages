## 1. Commit message

```text
feat(token): report keys that can't be loaded as TOKEN_KEYS_UNAVAILABLE

A token whose key was not among the loaded keys got TOKEN_KID_UNKNOWN,
whether the source of its iss held no such key or could not be asked.
An outage of the identity provider therefore looked like a stream of
invented tokens. ADR-0091 and ADR-0095 give the second case a reason
code of its own.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source.
That happens when the load failed, the wait for it ran out, or a limit
refused it. A JWKS that lacks the key is an answer. So is the 404 of a
realm that holds no keys. A realm that held keys returns 404 only on a
failed reload, and its keys stay. Verify turns ErrKeysUnavailable into
the reason code TOKEN_KEYS_UNAVAILABLE.

User-visible changes.
When no loaded key matches and the last load of the keys of the iss failed, ran out of time, or was refused by a limit, Verify rejects the token with TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a 200 response carries a `keys` that is not an array, `null` included, the load counts as failed and the keys loaded before it stay; `null` used to count as an empty array and removed them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report keys that can't be loaded as TOKEN_KEYS_UNAVAILABLE, not TOKEN_KID_UNKNOWN
```

## 3. Pull request description

```markdown
A token whose key is not among the loaded keys gets `TOKEN_KID_UNKNOWN`, whether the source of its `iss` holds no such key or could not be asked. An outage of the identity provider therefore looks like a stream of invented tokens. ADR-0091 and ADR-0095 give the second case a reason code of its own.

`LookupOrReload` returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That happens when the load failed, the wait for it ran out, or a limit refused it. `Verify` then rejects the token with `TOKEN_KEYS_UNAVAILABLE` and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer. So is the 404 of a realm that holds no keys. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys. Before this change, `null` counted as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. These packages are not wired into the service yet, so no request is handled differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait they exercise is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The change that wires the packages into the service has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
