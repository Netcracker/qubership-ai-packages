## Change 1

### Commit message

````text
fix(verify): refuse a token with no kid with TOKEN_KID_MISSING

A token whose header has no kid was refused with HTTP 401 and the
reason code TOKEN_INVALID. A token whose kid names no loaded key gets
the same code, so a client could not tell the two cases apart.
ADR-0007 R5 requires TOKEN_KID_MISSING for a token with no kid.

R5 applies only to a token whose exp has not passed. An expired token
is still refused as expired, whether or not its header has a kid.

User-visible changes.
A token whose exp has not passed and whose header has no kid is refused with HTTP 401 and the reason code TOKEN_KID_MISSING, where it got HTTP 401 and TOKEN_INVALID before.

Not changed.
A token whose kid names no loaded key is still refused with HTTP 401 and TOKEN_INVALID; R5 asks for TOKEN_KID_UNKNOWN there, and #12 tracks that part.
A token whose exp has passed is still refused with HTTP 401 and TOKEN_EXPIRED, with or without a kid.

Defers: ADR-0007 R5 to #12
````

### Pull request description

````markdown
A token whose header has no `kid` was refused with HTTP 401 and the reason code `TOKEN_INVALID`. A token whose `kid` names no loaded key gets the same code, so a client could not tell the two cases apart. R5 of `docs/adr/0007-verify-tokens.md` requires `TOKEN_KID_MISSING` for a token with no `kid`.

When the token's `exp` has not passed and its header has no `kid`, `internal/verify` now refuses it with HTTP 401 and `TOKEN_KID_MISSING`. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`, with or without a `kid`, because R5 covers only tokens that have not expired.

**Scope.** A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`. The `TOKEN_KID_UNKNOWN` part of R5 is left to #12.

Defers: ADR-0007 R5 to #12
````

## Change 2

### Commit message

````text
ci: cache Go modules between workflow runs

Every CI run downloaded all the Go modules the build needs, because
the workflow in .github/workflows/ci.yml kept nothing from one run to
the next.

Cache the Go modules between runs, so a run that restores the cache
does not download them again.

Implements: ADR-0007 R4
````

### Pull request description

````markdown
Every CI run downloaded all the Go modules the build needs, because `.github/workflows/ci.yml` kept nothing from one run to the next.

The workflow now caches Go modules between runs, so a run that restores the cache does not download them again. No other file changes.

Implements: ADR-0007 R4
````
