## 1. Commit message

```text
feat(token): report keys that cannot be loaded as TOKEN_KEYS_UNAVAILABLE

Verify gave TOKEN_KID_UNKNOWN to every token that found no key, whether
the source of its keys holds no such key or could not be asked. An
outage of the identity provider therefore looked like a stream of
invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that error into a reason code of its own, as ADR-0091 and
ADR-0095 decide.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only when a
reload fails, so its keys stay.

User-visible changes.
When no loaded key matches the token and the last load of the keys of its iss failed, the wait for it ran out, or a limit refused it, LookupOrReload returns keys.ErrKeysUnavailable instead of keys.ErrKeyUnknown.
In that case Verify rejects the token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, where it gave TOKEN_KID_UNKNOWN.
When a 200 response carries a `keys` that is not an array, `null` included, the load fails and the keys loaded before stay; `null` used to count as an empty array and removed them.

Not changed.
A token whose key is missing from a JWKS that loaded, or from a realm that holds no keys and returns 404, keeps TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): give tokens whose keys cannot be loaded the reason code TOKEN_KEYS_UNAVAILABLE
```

## 3. Pull request description

```markdown
`Verify` gives `TOKEN_KID_UNKNOWN` to every token that finds no key, whether the source of its keys holds no such key or could not be asked. An outage of the identity provider therefore looks like a stream of invented tokens. ADR-0091 and ADR-0095 give this case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` rejects such a token with `TOKEN_KEYS_UNAVAILABLE` and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer and still gives `TOKEN_KID_UNKNOWN`. So does the 404 of a realm that holds no keys. A realm that held keys returns 404 only when a reload fails, so its keys stay. A token that names a realm that does not exist also keeps `TOKEN_KID_UNKNOWN`. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys. Before this change, `null` counted as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait each one exercises is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it changes are not wired into the service yet, so no request is handled differently. The rest of ADR-0095 comes with the change that wires them in, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route. That change has no pull request yet.
```
