## Change 1

### Commit message

````text
feat(verify): refuse a token without kid with TOKEN_KID_MISSING

A token whose header had no `kid` was refused with HTTP 401 and
`TOKEN_INVALID`. A token whose `kid` names no loaded key got the same
response, so a client could not tell a token built without a key ID
from one signed with a key the service does not hold.

internal/verify now gives the missing `kid` its own error code. The
HTTP status stays 401, so a client that branches on the status alone
sees no difference. This implements part of ADR-0007 R5, and #12
tracks the rest of R5.

User-visible changes.
A token whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before.

Not changed.
A token whose `kid` names no loaded key is still refused with HTTP 401 and `TOKEN_INVALID`.

BREAKING CHANGE: a token without `kid` is refused with `TOKEN_KID_MISSING` instead of `TOKEN_INVALID`.
````

### Pull request description

````text
**Breaking changes.** A client that matches `TOKEN_INVALID` to handle a token without `kid` must now also match `TOKEN_KID_MISSING`. The HTTP status does not change.
A token whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before.

Before this change, a token with no `kid` and a token whose `kid` names no loaded key both got `TOKEN_INVALID`. A client could not tell a token built without a key ID from one signed with a key the service does not hold.

The missing `kid` now has its own code in `internal/verify`. A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, and an expired token still gets HTTP 401 and `TOKEN_EXPIRED`.

**Scope.** This implements part of ADR-0007 R5. #12 tracks the rest of R5 and stays open.
````

## Change 2

### Commit message

````text
ci: cache Go modules between workflow runs

Each CI run downloaded every Go module again, because
.github/workflows/ci.yml kept no module cache from one run to the next.
The workflow now caches Go modules between runs.
````

### Pull request description

````text
Each CI run downloaded every Go module again, because `.github/workflows/ci.yml` kept no module cache from one run to the next. The workflow now caches Go modules between runs. The service code and tests are unchanged.
````
