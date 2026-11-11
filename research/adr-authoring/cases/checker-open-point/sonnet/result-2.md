## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` whose `exp` passed an hour ago is now accepted. Both answers to O1 (0 and 30 seconds) require a refusal with `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` is still refused with `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- Trailers: none present, so there are no trailer errors.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token whose `exp` passed 10 seconds ago is now accepted. That fails R4 if O1 is answered 0 seconds and meets it if O1 is answered 30 seconds. A token whose `exp` passed 40 seconds ago is still refused with `TOKEN_EXPIRED`, which meets R4 under both answers. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` is still refused with `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- Open point ADR-0007 O1 (the security architect decides) sets the outcome of the 10-second case. R4 stays `Cannot tell` until O1 is answered.
- Trailers: none present, so there are no trailer errors.
