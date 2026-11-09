## 1. Commit message

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE when keys cannot be loaded

Before this change, a token whose kid matched no loaded key got
TOKEN_KID_UNKNOWN in two cases. In one, the source of its issuer holds
no such key. In the other, the source could not be asked. An outage of
the identity provider therefore looked like a stream of invented tokens.

LookupOrReload now separates the two cases by what the last load of the
source learned about its keys. When no loaded key matches and the last
load got no answer about those keys, it returns keys.ErrKeysUnavailable.
The load got no answer when it failed, when the wait for it ran out, or
when a limit refused it. Verify turns that error into a reason code of
its own, as ADR-0091 and ADR-0095 decide.

A JWKS that lacks the key is an answer. So is the 404 of a realm that
holds no keys. A realm that held keys returns 404 only on a failed
reload, and its keys stay. A 200 response whose keys is not an array is
a failed load, null included, and the loaded keys stay.

User-visible changes.
LookupOrReload returns keys.ErrKeysUnavailable instead of ErrKeyUnknown when no loaded key matches and the last load failed, ran out of time waiting, or was refused by a limit.
Verify reports TOKEN_KEYS_UNAVAILABLE, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`, when LookupOrReload returns keys.ErrKeysUnavailable.
A 200 JWKS response whose keys is null keeps the loaded keys; null used to count as an empty array and removed them.

Not changed.
A token whose key is missing from a JWKS that loaded, or from a realm that returns 404 and holds no keys, keeps TOKEN_KID_UNKNOWN.
A token that names a realm that does not exist keeps TOKEN_KID_UNKNOWN.
```

## 2. Pull request title

```text
feat(token): report TOKEN_KEYS_UNAVAILABLE, not TOKEN_KID_UNKNOWN, when keys cannot be loaded
```

## 3. Pull request description

```markdown
A token whose `kid` matched no loaded key got `TOKEN_KID_UNKNOWN` in two cases: when the source of its issuer holds no such key, and when the source could not be asked. An outage of the identity provider therefore looked like a stream of invented tokens.

`LookupOrReload` now returns `keys.ErrKeysUnavailable` instead of `ErrKeyUnknown` when no loaded key matches and the last load got no answer about the keys of the source. That covers a failed load, a wait that ran out, and a load a limit refused. `Verify` turns that error into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`. ADR-0091 and ADR-0095 give this case a reason code of its own. A JWKS that lacks the key still counts as an answer and keeps `TOKEN_KID_UNKNOWN`. The 404 of a realm that holds no keys also counts as an answer, and so does a realm that does not exist. A realm that held keys returns 404 only on a failed reload, and its keys stay. A 200 response whose `keys` is not an array is now a failed load and keeps the loaded keys. Before, `null` counted as an empty array and removed them.

The service does not use these packages yet, so it handles no request differently.

Seven existing tests now expect `ErrKeysUnavailable` instead of `ErrKeyUnknown`. Each one exercises a limit or a wait that runs out, which is the case this change names.

**Scope.** This pull request is stacked on #203, which sits on #159, #202, and #201, and it merges after them. The change that wires these packages into the service has no pull request yet. That change brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED` and `CALLER_NOT_M2M`, which depend on the route.
```
