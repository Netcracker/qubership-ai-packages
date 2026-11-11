## Change 1

### Commit message

````text
feat(verify): refuse a token with no kid as TOKEN_KID_MISSING

ADR-0007 R5 gives a token whose header has no `kid` its own reason
code. verify refused such a token with the generic `TOKEN_INVALID`, so
a caller could not tell a missing `kid` from any other invalid token.

verify now checks for the `kid` header and refuses the token with
`TOKEN_KID_MISSING`.

User-visible changes.
A token whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`; it was refused with HTTP 401 and `TOKEN_INVALID`. A client that matches `TOKEN_INVALID` for this case must match `TOKEN_KID_MISSING`.

Not changed.
A token whose `kid` names no loaded key is still refused with HTTP 401 and `TOKEN_INVALID`; R5 gives it `TOKEN_KID_UNKNOWN`, which is tracked in #12. A token whose `exp` has passed is still refused with HTTP 401 and `TOKEN_EXPIRED`.

Defers: ADR-0007 R5 to #12
````

### Pull request description

````text
**Breaking changes.** A token whose header has no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID`. A client that matches `TOKEN_INVALID` to detect this case must match `TOKEN_KID_MISSING` instead.

ADR-0007 R5 gives a missing `kid` its own reason code, but `internal/verify` folded it into `TOKEN_INVALID`, so a caller could not tell it from any other invalid token. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`.

**Scope.** The other half of R5, `TOKEN_KID_UNKNOWN` for a `kid` that names no loaded key, is not part of this change. Such a token still gets HTTP 401 and `TOKEN_INVALID`. Issue #12 tracks it and stays open.

Defers: ADR-0007 R5 to #12
````

## Change 2

### Commit message

````text
ci: cache Go modules between workflow runs

Cache Go modules in `.github/workflows/ci.yml` so a run reuses the
modules an earlier run downloaded.
````

### Pull request description

````text
The CI workflow now caches Go modules between runs, so a run reuses the modules an earlier run downloaded. Only `.github/workflows/ci.yml` changes.
````
