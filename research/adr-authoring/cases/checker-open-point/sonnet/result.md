## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` and an `exp` an hour past is now accepted, which fails R4 under both O1 answers (0 and 30 seconds). |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` is still refused with `TOKEN_KID_MISSING`. |

Apart from the verdicts: nothing.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token 10 seconds past `exp` is accepted, which meets R4 if O1 settles on 30 seconds and fails it if O1 settles on 0 seconds; a token 40 seconds past is refused under both. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` is still refused with `TOKEN_KID_MISSING`. |

Apart from the verdicts: nothing.
