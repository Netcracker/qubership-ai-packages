## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose key is not found got TOKEN_KID_UNKNOWN whether the source
of its keys held no such key or could not be queried. An outage of the
identity provider therefore looked like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
reports that as TOKEN_KEYS_UNAVAILABLE. ADR-0091 and ADR-0095 give this
case a reason code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, so that response is a failed load and the keys stay. A 200
response whose keys is not an array is a failed load as well. null used
to count as an empty array and removed the keys.

User-visible changes.
When no loaded key matches and the last load of the keys of the issuer failed, ran out of wait, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable and Verify reports the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When the JWKS lacks the key, or the realm answers 404 and holds no keys, the token still gets ErrKeyUnknown and TOKEN_KID_UNKNOWN.
When a realm that held keys answers 404 on a reload, the load counts as failed and the loaded keys stay.
When a 200 response has a keys member that is not an array, null included, the load counts as failed and the loaded keys stay; null used to remove them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): return TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

````markdown
Until now a token whose key was not found got `TOKEN_KID_UNKNOWN`, whether the source of its keys held no such key or could not be queried. An outage of the identity provider therefore reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 give this case a reason code of its own.

Three kinds of response are answers or failures, and the line falls between them as follows. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys, so both keep `ErrKeyUnknown` and `TOKEN_KID_UNKNOWN`. A realm that held keys returns 404 only on a failed reload, so that response is a failed load and its keys stay. A 200 response whose `keys` is not an array is a failed load that keeps the keys too; `null` used to count as an empty array and removed them, so check that this is the behavior you want. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. The limit or the wait each of them exercises is a case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
````
