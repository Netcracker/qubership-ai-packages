## 1. Commit message

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for keys that cannot be loaded

A token whose key was not among the loaded keys got TOKEN_KID_UNKNOWN
in two cases: when its source holds no such key, and when the source
could not be asked. During an outage of the identity provider, every
token was reported as TOKEN_KID_UNKNOWN, as if each one were invented.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source.
That happens when the load failed, the wait for it ran out, or a limit
refused it. Verify turns this error into a reason code of its own.

A JWKS that lacks the key is an answer. So is the 404 of a realm that
holds no keys. A realm that held keys returns 404 only on a failed
reload, and its keys stay. A 200 response whose keys is not an array
is a failed load, and the loaded keys stay. Before this change, null
was treated as an empty array and removed the keys.

User-visible changes.
When no loaded key matches and the last load of the keys failed, timed out, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable instead of ErrKeyUnknown.
In that case Verify reports TOKEN_KEYS_UNAVAILABLE instead of TOKEN_KID_UNKNOWN, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 JWKS response whose keys is `null`, or is anything else that is not an array, keeps the loaded keys. Before this change, `null` removed them.

Not changed.
A token gets TOKEN_KID_UNKNOWN as before when the JWKS lacks its key, when its realm holds no keys and returns 404, or when it names a realm that does not exist.
The service handles every request as before, because these packages are not wired into it yet.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): add TOKEN_KEYS_UNAVAILABLE for tokens whose issuer keys cannot be loaded
```

## 3. Pull request description

```markdown
A token whose key was not among the loaded keys got `TOKEN_KID_UNKNOWN` in two cases: when its source holds no such key, and when the source could not be asked. During an outage of the identity provider, every token was reported as `TOKEN_KID_UNKNOWN`, as if each one were invented.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That happens when the load failed, the wait for it ran out, or a limit refused it. In that case `Verify` reports `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array is a failed load and keeps the loaded keys. This includes `null`, which used to be treated as an empty array and removed them. No request is handled differently yet, because these packages are not wired into the service.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait that each one exercises is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. The change that wires them has no pull request or issue yet, so these rules are not in a `Defers:` line. That change also adds the ADR-0095 reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.

Implements: ADR-0091 R23, R37, R38, R39
```
