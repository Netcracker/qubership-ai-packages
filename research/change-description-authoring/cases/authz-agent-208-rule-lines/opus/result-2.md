## 1. Commit message

```text
feat(token): give keys that cannot be loaded a reason code of their own

A token whose kid matched no loaded key got TOKEN_KID_UNKNOWN, whether
its source holds no such key or could not be asked. An outage of the
identity provider therefore read like a stream of invented tokens. The
packages this commit touches are not wired into the service yet, so no
request the service handles changes.

LookupOrReload now returns keys.ErrKeysUnavailable when no loaded key
matches and the last load got no answer about the keys of the source:
the load failed, the wait for it ran out, or a limit refused it. Verify
turns that error into a reason code of its own.

A JWKS that lacks the key is an answer, and so is the 404 of a realm
that holds no keys. A realm that held keys returns 404 only on a failed
reload, and its keys stay. A 200 response whose keys is not an array is
a failed load as well, and keeps the keys.

User-visible:
When no loaded key matches and the last load of the source got no answer, Verify reports TOKEN_KEYS_UNAVAILABLE with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
When a limit refuses the load or the wait for it runs out, LookupOrReload returns keys.ErrKeysUnavailable where it returned ErrKeyUnknown.
A 200 JWKS response whose keys is null is a failed load and keeps the loaded keys; it used to count as an empty array and remove them.
Not changed:
A token whose key the JWKS lacks, or whose realm holds no keys and returns 404, keeps TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.

Implements: ADR-0091 R23, R37, R38, R39
Defers: ADR-0092 R2 to [PR #NNNN]; ADR-0095 R2, R16 to [PR #NNNN]
```

## 2. Pull request title

```text
feat(token): give keys that cannot be loaded the reason code TOKEN_KEYS_UNAVAILABLE
```

## 3. Pull request description

```markdown
Before this change, a token whose kid matched no loaded key got `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could not be asked. An outage of the identity provider therefore read like a stream of invented tokens. The packages this change touches are not wired into the service yet, so no request the service handles changes.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` reports that case as `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. Those tokens keep `TOKEN_KID_UNKNOWN`, and so does a token that names a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array is a failed load and keeps the keys. `null` used to count as an empty array and removed them.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`, because the limit or the wait they exercise is the case this change names.

**Scope.** This is stacked on #203, which sits on #159, #202, and #201, and it merges after all four. The deferred rules need the packages wired into the service, and the next change does that. That change has no pull request yet. Its number replaces `[PR #NNNN]` here and in the commit's `Defers:` trailer before this merges. The same change adds the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which ADR-0095 lists and which depend on the route.

Implements: ADR-0091 R23, R37, R38, R39.
Defers: ADR-0092 R2 to [PR #NNNN]; ADR-0095 R2, R16 to [PR #NNNN].
```
