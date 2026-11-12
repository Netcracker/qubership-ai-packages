## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Met | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violated | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a `kid` that names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

- The `Implements: ADR-0007 R5` trailer claims the whole rule, but the change covers only the missing-`kid` half.
- Required before merge: make `internal/verify` refuse an unknown `kid` with HTTP 401 and `TOKEN_KID_UNKNOWN`. The alternative is to change the trailer to a deferral that points at a tracking issue.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Met | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Partly met, remainder deferred | A token with no `kid` now gets `TOKEN_KID_MISSING`. The unknown-`kid` case still gets `TOKEN_INVALID`, and the `Defers: ADR-0007 R5 to #12` trailer declares that gap. |

- Issue #12 is open and tracks the rest of ADR-0007 R5, which is the unknown-`kid` case (`TOKEN_KID_UNKNOWN`).
