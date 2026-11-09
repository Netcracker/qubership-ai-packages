## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Pass | An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, because `internal/verify` compares `exp` before it reads `kid` and so also catches an expired token with no `kid` first. |
| ADR-0007 R5 | Fail | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. |

- The trailer `Implements: ADR-0007 R5` claims all of R5. The change covers only the missing-`kid` half. To fix this, add the `TOKEN_KID_UNKNOWN` branch for an unknown `kid`, or change the trailer to defer the rest of R5 to an open issue.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Pass | An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, because `internal/verify` compares `exp` before it reads `kid` and so also catches an expired token with no `kid` first. |
| ADR-0007 R5 | Deferred | A token with no `kid` now gets `TOKEN_KID_MISSING`. The trailer defers the rest of R5 to #12, which is open and tracks the `TOKEN_KID_UNKNOWN` case. |

- Issue #12: until it is closed, a token whose `kid` names no loaded key gets HTTP 401 and `TOKEN_INVALID` rather than `TOKEN_KID_UNKNOWN`.
- The trailer `Defers: ADR-0007 R5 to #12` doesn't mention that this change already implements the missing-`kid` half of R5.
