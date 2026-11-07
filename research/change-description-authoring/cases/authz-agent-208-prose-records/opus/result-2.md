## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

Verify gave the reason code TOKEN_KID_UNKNOWN to every token whose kid
matched no loaded key. It did so both when the source of the issuer held
no such key and when the source could not be reached. An outage of the
identity provider therefore looked like a stream of invented tokens.

LookupOrReload now uses the last load of the source to tell the two
cases apart. A JWKS that lacks the key still counts as an answer about
the keys of the source. So does the 404 of a realm that holds no keys.
A load that failed, whose wait ran out, or that a limit refused gets no
such answer. A realm that held keys returns 404 only when a reload
fails, and its loaded keys stay. ADR-0091 and ADR-0095 give this case a
reason code of its own.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible:
When no loaded key matches and the last load of the source failed, its wait ran out, or a limit refused it, LookupOrReload returns keys.ErrKeysUnavailable, and Verify fails with TOKEN_KEYS_UNAVAILABLE: `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`
A 200 JWKS response whose `keys` is not an array, `null` included, is a failed load and keeps the loaded keys; `null` used to count as an empty array and removed them.
Not changed:
A token whose key the source does not hold, or that names a realm that does not exist, still gets TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
Before this change, `Verify` gave `TOKEN_KID_UNKNOWN` to every token whose `kid` matched no loaded key. It did so both when the source of the issuer held no such key and when the source could not be reached. An outage of the identity provider therefore looked like a stream of invented tokens. ADR-0091 and ADR-0095 give this case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load of the source failed, its wait ran out, or a limit refused it. `Verify` turns that error into `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key still counts as an answer and keeps `TOKEN_KID_UNKNOWN`. So does the 404 of a realm that holds no keys. A realm that held keys returns 404 only when a reload fails, and its loaded keys stay. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the loaded keys. Before, `null` counted as an empty array and removed them. The packages are not wired into the service yet, so no request is handled differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because each one exercises a limit or a wait, which is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The rest of ADR-0095 comes with the change that wires the packages into the service, which has no pull request yet. That includes the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
