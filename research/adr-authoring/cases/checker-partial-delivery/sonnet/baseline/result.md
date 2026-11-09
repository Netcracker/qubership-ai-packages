## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Satisfied | A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`, and `internal/verify` compares `exp` before it reads `kid`. |
| ADR-0007 R5 | Violated | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts:

- The `Implements: ADR-0007 R5` trailer is inaccurate. The change implements only the missing-`kid` half of R5.
- The unmet part is the unknown-`kid` case, which still returns `TOKEN_INVALID`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Satisfied | A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`, and `internal/verify` compares `exp` before it reads `kid`. |
| ADR-0007 R5 | Partly met, rest deferred | A token with no `kid` now gets `TOKEN_KID_MISSING`. A token whose `kid` names no loaded key still gets `TOKEN_INVALID`, and the `Defers: ADR-0007 R5 to #12` trailer says so. |

Named apart from the verdicts:

- Issue #12 is open and tracks the rest of ADR-0007 R5, so the deferral points at an existing issue.
- The unknown-`kid` case still does not meet R5 until #12 is resolved.
