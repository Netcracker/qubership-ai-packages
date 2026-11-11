## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` whose `exp` passed an hour ago is now accepted, but R4 requires 401 `TOKEN_EXPIRED` under both O1 answers (0 and 30 seconds). |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with 401 `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- ADR-0007 is `Proposed`, and the reading guide makes `Proposed` records bind, so R4 and R5 were walked as binding rules.
- The change carries no trailers. There is no trailer error, no guide error, and no `would violate` line.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token whose `exp` passed 10 seconds ago is now accepted. That violates R4 if O1 settles on 0 seconds and meets it if O1 settles on 30 seconds. A token whose `exp` passed 40 seconds ago is still refused with 401 `TOKEN_EXPIRED`, which meets R4 under both answers. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with 401 `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- ADR-0007 O1 decides the R4 verdict. The security architect decides it, and the answers under consideration are 0 seconds and 30 seconds.
- ADR-0007 is `Proposed`, and the reading guide makes `Proposed` records bind, so R4 and R5 were walked as binding rules.
- The change carries no trailers. There is no trailer error, no guide error, and no `would violate` line.
