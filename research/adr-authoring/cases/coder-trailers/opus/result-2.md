## Change 1

### Commit message

````text
feat(verify)!: refuse a token without kid with TOKEN_KID_MISSING

ADR-0007 R5 requires that a token whose exp has not passed and whose
header has no kid be refused with HTTP 401 and the reason code
TOKEN_KID_MISSING. internal/verify refused such a token with HTTP 401
and TOKEN_INVALID instead. A token whose kid names no loaded key gets
the same code, so a client could not tell the two cases apart.

This commit covers only the missing-kid half of R5. TOKEN_KID_UNKNOWN
for a kid that names no loaded key is left to #12, which stays open.

User-visible changes.
A token whose exp has not passed and whose header has no kid is refused with HTTP 401 and reason code TOKEN_KID_MISSING, where it got HTTP 401 and TOKEN_INVALID before; a client that matched TOKEN_INVALID for this case has to match TOKEN_KID_MISSING.

Not changed.
A token whose kid names no loaded key is still refused with HTTP 401 and TOKEN_INVALID, not TOKEN_KID_UNKNOWN.
A token whose exp has passed is still refused with HTTP 401 and TOKEN_EXPIRED, with or without a kid.

Defers: ADR-0007 R5 to #12
````

### Pull request description

````text
**Breaking changes.** This breaks a client that reads the reason code of a refused token and expects `TOKEN_INVALID` for a token without `kid`:
A token whose `exp` has not passed and whose header has no `kid` is refused with HTTP 401 and `TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before. Match `TOKEN_KID_MISSING` for that case.

ADR-0007 R5 (`docs/adr/0007-verify-tokens.md`) requires this reason code. `internal/verify` gave a token without `kid` the same `TOKEN_INVALID` as a token whose `kid` names no loaded key, so a client could not tell the two apart.

A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`, with or without a `kid`, as R4 requires.

**Scope.** The rest of R5, `TOKEN_KID_UNKNOWN` for a `kid` that names no loaded key, is left to #12. That is why #12 stays open.

Defers: ADR-0007 R5 to #12
````

## Change 2

### Commit message

````text
ci: cache Go modules between workflow runs

Every CI run downloaded all of the Go modules again because nothing
kept the module cache from one run to the next. The workflow in
.github/workflows/ci.yml now caches the Go modules between runs, so a
run downloads only the modules that are missing from the cache.
````

### Pull request description

````text
Every CI run downloaded all of the Go modules again because nothing kept the module cache from one run to the next. `.github/workflows/ci.yml` now caches the Go modules between runs, so a run downloads only the modules that are missing from the cache. The workflow is the only file this changes.
````
