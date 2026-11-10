## 1. Commit message

````text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

A token whose key is not found got TOKEN_KID_UNKNOWN both when the
source holds no such key and when the keys of the source could not be
loaded. During an outage of the identity provider, every token
therefore looked invented.

LookupOrReload now separates the two cases. When no loaded key matches
and the last load got no response about the keys of the source (the load
failed, the wait for it ran out, or a limit refused it), it returns
keys.ErrKeysUnavailable, and Verify reports it as a reason code of its
own. ADR-0091 and ADR-0095 decide that this case gets one.

A JWKS that lacks the key is a complete response, and so is the 404 of a
realm that holds no keys. A realm that held keys returns 404 only on a
failed reload, so that 404 counts as a failed load and the keys stay.
For the same reason a 200 response whose keys is not an array is a
failed load. null included: it used to count as an empty array and
removed the loaded keys.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable when no loaded key matches and the last load failed, the wait for it ran out, or a limit refused it.
Verify returns the reason code TOKEN_KEYS_UNAVAILABLE in that case, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
A 404 from a realm that held keys is a failed reload: the loaded keys stay, and a token whose key is not among them gets keys.ErrKeysUnavailable.
A 200 response whose keys is not an array, null included, is a failed load and the loaded keys stay.

Not changed.
A JWKS that lacks the key, or the 404 of a realm that holds no keys, still gives keys.ErrKeyUnknown and TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist still gets TOKEN_KID_UNKNOWN.
The packages are not wired into the service yet, so no request is handled differently.
````

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

````markdown
A token whose key is not found gets `TOKEN_KID_UNKNOWN`, both when the source holds no such key and when its keys could not be loaded. During an outage of the identity provider, every token therefore looks invented.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no response about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that as `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 decide that this case gets a reason code of its own.

A JWKS that lacks the key is a complete response, and so is the 404 of a realm that holds no keys; both still give `ErrKeyUnknown`. A realm that held keys returns 404 only on a failed reload, which counts as a failed load and keeps its keys. A 200 response whose `keys` is not an array is a failed load that keeps the keys. `null` is included here: it used to count as an empty array and removed them. A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait that ran out, which is a case this change names.

**Scope.** This is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
````
