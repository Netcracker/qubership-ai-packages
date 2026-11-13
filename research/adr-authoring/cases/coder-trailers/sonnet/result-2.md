## Change 1

### Commit message

````text
feat(verify): refuse a token with no kid as TOKEN_KID_MISSING

A token whose header has no `kid` was refused with HTTP 401 and
`TOKEN_INVALID`. ADR-0007 R5 requires `TOKEN_KID_MISSING` for an
unexpired token in that case, so a client could not tell a missing `kid`
from any other reason behind `TOKEN_INVALID`.

internal/verify now refuses a token with no `kid` in its header with
that reason code. Only the missing `kid` branch changes. R5's other
branch, `TOKEN_KID_UNKNOWN`, is left to #12.

User-visible changes.
A token whose header has no `kid` is refused with HTTP 401 and the reason code `TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before. A client that matches `TOKEN_INVALID` for this case must also match `TOKEN_KID_MISSING`.

Not changed.
A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, and a token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`.

Defers: ADR-0007 R5 to #12
````

### Pull request description

````text
**Breaking changes.** A token whose header has no `kid` is now refused with HTTP 401 and `TOKEN_KID_MISSING`; it got HTTP 401 and `TOKEN_INVALID` before. A client that matches `TOKEN_INVALID` for this case must also match `TOKEN_KID_MISSING`. The HTTP status is unchanged.

ADR-0007 R5 requires `TOKEN_KID_MISSING` for an unexpired token whose header has no `kid`, and `internal/verify` returned `TOKEN_INVALID` for it.

The new branch covers only the missing `kid`. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`.

**Scope.** R5's second branch, `TOKEN_KID_UNKNOWN` for a `kid` that names no loaded key, is not part of this change: such a token still gets HTTP 401 and `TOKEN_INVALID`. #12 tracks it and stays open after this merges.

Defers: ADR-0007 R5 to #12
````

## Change 2

### Commit message

````text
ci: cache Go modules between runs

CI did not cache Go modules, so every run downloaded them again.
.github/workflows/ci.yml now caches them between runs.

Nothing the service ships changes.
````

### Pull request description

````text
CI did not cache Go modules, so every run downloaded them again. `.github/workflows/ci.yml` now caches them between runs.

The change touches no code under `internal/`, so it carries no ADR trailers.
````
