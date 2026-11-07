## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose kid matches no loaded key got TOKEN_KID_UNKNOWN, whether
the source of the keys holds no such key or could not be asked. During
an outage of the identity provider, every token that needs a reload
therefore failed with the code for a token signed by a key that was
never published, and the outage read like a stream of invented tokens.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load of the issuer's keys did not complete: the
load failed, the wait for it ran out, or a limit refused it. A JWKS that
lacks the key is a completed load, and so is the 404 of a realm that
holds no keys; both still end in ErrKeyUnknown. A realm that held keys
returns 404 only on a failed reload, and its keys stay.

A 200 response whose keys is not an array is a failed load too, and it
keeps the loaded keys. null used to count as an empty array and removed
them, so one malformed response emptied a working set.

ADR-0091 and ADR-0095 give this case a reason code of its own.

User-visible changes.
When no loaded key matches the kid and the last load of the issuer's keys failed, timed out, or was refused by a limit, LookupOrReload returns keys.ErrKeysUnavailable and Verify returns the reason code TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. These cases returned TOKEN_KID_UNKNOWN before.
A 200 response whose keys is not an array, null included, is a failed load that keeps the loaded keys. A null used to empty them.

Not changed.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when the keys of an issuer cannot be loaded
```

## 3. Pull request description

```markdown
During an outage of the identity provider, a token whose kid matches no loaded key gets `TOKEN_KID_UNKNOWN`. That is the same code a token signed with a key the issuer never published gets, so the outage reads like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load of the issuer's keys did not complete: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that into the reason code `TOKEN_KEYS_UNAVAILABLE` with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is a completed load, and so is the 404 of a realm that holds no keys. Both keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, which keeps its keys. A 200 response whose `keys` is not an array is also a failed load that keeps the keys; `null` used to count as an empty array and removed them. ADR-0091 and ADR-0095 give this case a reason code of its own.

Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`. Each exercises a limit or a wait that ran out, which is the case this change names, so no coverage is lost.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The packages it touches are not wired into the service yet, so no request is handled differently. The change that wires them in has no pull request yet. It brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
