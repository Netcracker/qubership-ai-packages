## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` and an `exp` that passed an hour ago is accepted, where R4 requires 401 and `TOKEN_EXPIRED`. Every answer to O1 refuses such a token. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` still gets 401 and `TOKEN_KID_MISSING`. |

Named apart from the verdicts: nothing.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token that expired 10 seconds ago is accepted. That fails R4 under the 0-second answer to O1 and meets it under the 30-second answer, and the security architect has not decided O1. A token that expired 40 seconds ago is refused with 401 and `TOKEN_EXPIRED`, which meets R4 under both answers. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` still gets 401 and `TOKEN_KID_MISSING`. |

Named apart from the verdicts: nothing.
