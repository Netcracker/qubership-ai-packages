## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

When no loaded key matched a token, the token got TOKEN_KID_UNKNOWN.
That happened both when the source of the keys held no such key and
when the source could not be asked. An outage of the identity provider
therefore read like a stream of invented tokens.

ADR-0091 and ADR-0095 give this case a reason code of its own. The key
lookup now separates a load that got no answer about the keys of the
source from a load that got one. A failed load, a wait for the load
that ran out, and a load that a limit refused are no answer. A JWKS
that lacks the key is an answer, and so is the 404 of a realm that
holds no keys. A realm that held keys returns 404 only on a failed
reload, so that 404 keeps its keys.

The packages are not wired into the service yet, so no request is
handled differently.

User-visible:
When no loaded key matches and the last load got no answer, LookupOrReload returns keys.ErrKeysUnavailable, and Verify reports the reason code TOKEN_KEYS_UNAVAILABLE with the text:
    the keys of iss "<iss>" cannot be loaded, so the token cannot be checked
When a 200 response carries a keys member that is not an array, null included, the load fails and the loaded keys stay; null used to count as an empty array and removed them.
Not changed:
A token whose key the JWKS lacks, whose realm holds no keys, or whose realm does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
When no loaded key matched a token, the token got `TOKEN_KID_UNKNOWN`. That happened both when the source of the keys held no such key and when the source could not be asked. An outage of the identity provider therefore read like a stream of invented tokens. ADR-0091 and ADR-0095 give this case a reason code of its own.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source. That covers a failed load, a wait for the load that ran out, and a load that a limit refused. `Verify` turns the error into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array, `null` included, is now a failed load and keeps the loaded keys. Before this change, `null` counted as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` where they expected `ErrKeyUnknown`. The limit or the wait that each one exercises is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after all four. The packages it touches are not wired into the service yet, so no request is handled differently. Wiring them in is a separate change that has no pull request yet. That change brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
