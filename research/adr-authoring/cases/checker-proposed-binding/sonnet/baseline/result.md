## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Satisfied | `internal/verify` still refuses an expired token with HTTP 401 and `TOKEN_EXPIRED`, and it compares `exp` before it reads `kid`. |
| ADR-0007 R5 | Violated | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. The `Implements: ADR-0007 R5` trailer claims more than the code does. |

Named apart from the verdicts:

- The unmet part of R5 is the `TOKEN_KID_UNKNOWN` case in `internal/verify`.
- ADR-0007 is `Proposed`, and `docs/adr/README.md` says `Proposed` records bind a change, so the R5 violation counts.
- The trailer in the commit message and the description says the change implements R5, which is false for the unknown-`kid` case.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Satisfied | `internal/verify` still refuses an expired token with HTTP 401 and `TOKEN_EXPIRED`, and it compares `exp` before it reads `kid`. |
| ADR-0007 R5 | Deferred | The `TOKEN_KID_MISSING` case is now met. The `TOKEN_KID_UNKNOWN` case is still `TOKEN_INVALID`, and the `Defers: ADR-0007 R5 to #12` trailer says so and points to open issue #12, which tracks the rest of R5. |

Named apart from the verdicts:

- The deferred part of R5 is the `TOKEN_KID_UNKNOWN` case, and issue #12 is open and tracks it.
- ADR-0007 is `Proposed`, and `docs/adr/README.md` says `Proposed` records bind a change. The trailer discloses the gap, so the change does not claim to satisfy R5.
