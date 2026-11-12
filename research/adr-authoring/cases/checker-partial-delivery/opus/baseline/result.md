## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Met | `internal/verify` still refuses a token whose `exp` has passed with HTTP 401 and `TOKEN_EXPIRED`, and the change keeps that. |
| ADR-0007 R5 | Not met | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

- The trailer `Implements: ADR-0007 R5` is false. The change implements only the missing-`kid` half of R5, so the trailer should be corrected or the unknown-`kid` case should be added before merge.
- `internal/verify` compares `exp` before it reads `kid`. A token that has expired and has no `kid` therefore gets `TOKEN_EXPIRED`. That matches the R5 condition "whose `exp` has not passed".

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Met | `internal/verify` still refuses a token whose `exp` has passed with HTTP 401 and `TOKEN_EXPIRED`, and the change keeps that. |
| ADR-0007 R5 | Not met | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

- The trailer `Defers: ADR-0007 R5 to #12` points to an open issue, and that issue tracks the rest of R5. The deferral is real and tracked.
- The deferral doesn't change the R5 verdict. `docs/adr/README.md` says that an `Accepted` record binds a change, and it gives no provision that lets a trailer release a rule.
- The trailer defers all of R5, but the change does implement the missing-`kid` half. Only the unknown-`kid` case is left, and the trailer could say that.
- `internal/verify` compares `exp` before it reads `kid`. A token that has expired and has no `kid` therefore gets `TOKEN_EXPIRED`. That matches the R5 condition "whose `exp` has not passed".
