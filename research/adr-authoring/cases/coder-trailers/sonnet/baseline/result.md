## Change 1

### Commit message

````text
feat(verify)!: refuse a token without kid with TOKEN_KID_MISSING

A token whose header has no `kid` was refused with HTTP 401 and
`TOKEN_INVALID`, the same response as a token whose `kid` names no
loaded key. A client could not tell the two apart.

This implements part of ADR-0007 R5. Issue #12 tracks the rest and
stays open, so this commit references it without closing it.

User-visible changes.
A token whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`; it got HTTP 401 and `TOKEN_INVALID` before.

Not changed.
A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, and a token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`.

See #12.

BREAKING CHANGE: a token whose header has no `kid` gets `TOKEN_KID_MISSING` instead of `TOKEN_INVALID`. The HTTP status stays 401. A client that matches on `TOKEN_INVALID` for this case must also handle `TOKEN_KID_MISSING`.
````

### Pull request description

````text
**Breaking changes.** A token whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`; it got HTTP 401 and `TOKEN_INVALID` before. The HTTP status is unchanged. A client that matches on `TOKEN_INVALID` for this case must also handle `TOKEN_KID_MISSING`.

A token with no `kid` in its header got the same HTTP 401 and `TOKEN_INVALID` as a token whose `kid` names no loaded key, so the response could not tell the two cases apart.

`internal/verify` now has a separate branch for the missing `kid`. The other refusals keep their codes: a `kid` that names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, and an expired `exp` still gets HTTP 401 and `TOKEN_EXPIRED`.

**Scope.** This covers part of ADR-0007 R5. Issue #12 tracks the rest of R5, so the commit says `See #12` and does not close it.
````

## Change 2

### Commit message

````text
ci: cache Go modules between workflow runs

The CI workflow had no Go module cache, so every run downloaded all
the modules the build and tests need. `.github/workflows/ci.yml` now
caches the modules, and a run restores those that an earlier run
downloaded.
````

### Pull request description

````text
The CI workflow had no Go module cache, so every run downloaded all the modules the build and tests need. This change caches them between runs in `.github/workflows/ci.yml`. Nothing else changes.
````
