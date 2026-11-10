## 1. Commit message

```text
feat(token): report keys that cannot be loaded as TOKEN_KEYS_UNAVAILABLE

A token that found no key got TOKEN_KID_UNKNOWN in two cases: when its
source holds no such key, and when the source could not be asked. During
an outage of the identity provider, the rejections therefore looked the
same as a stream of invented tokens.

LookupOrReload now uses the last load of the source to tell the two
cases apart. If that load got no answer about the keys of the source,
the source could not be asked. The load failed, the wait for it ran
out, or a limit refused it. A JWKS that lacks the key is an answer, and
so is the 404 of a realm that holds no keys. A realm that held keys
returns 404 only on a failed reload, and its keys stay.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable, where it returned keys.ErrKeyUnknown, when no loaded key matches and the last load got no answer about the keys of the source.
Verify rejects such a token with the reason code TOKEN_KEYS_UNAVAILABLE and the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the loaded keys; `null` used to count as an empty array and removed them.

Not changed.
A token whose key is missing from a JWKS, or from a realm that returns 404 and holds no keys, keeps TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
```

## 2. Pull request title

```text
feat(token): report keys that cannot be loaded as TOKEN_KEYS_UNAVAILABLE instead of TOKEN_KID_UNKNOWN
```

## 3. Pull request description

```markdown
A token that finds no key gets `TOKEN_KID_UNKNOWN` in two cases: when its source holds no such key, and when the source could not be asked. During an outage of the identity provider, the rejections therefore look the same as a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. The load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE`, with this text:

```text
the keys of iss "<iss>" cannot be loaded, so the token cannot be checked
```

A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the keys. `null` used to count as an empty array and removed them. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. Each one exercises a limit or a wait, which is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 need the packages wired into the service. So do the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M` that ADR-0095 lists, because they depend on the route. The next change does that wiring. It has no pull request yet, so these rules have no `Defers:` line here.

Implements: ADR-0091 R23, R37, R38, R39
```
