## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` whose `exp` passed an hour ago is now accepted, where the rule requires HTTP 401 and `TOKEN_EXPIRED`. No answer to O1 makes this acceptable. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- Guide error: `docs/adr/` has no `README.md`, so no layer map ties `internal/verify` to the `verify` layer. I read the `verify` tag as the code in `internal/verify`.
- ADR-0007 is `Proposed`, so it binds the change.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token whose `exp` passed 10 seconds ago is now accepted. That fails R4 if O1 settles on 0 seconds and meets it if O1 settles on 30 seconds. A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`, which meets R4 under both answers. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

Named apart from the verdicts:

- Guide error: `docs/adr/` has no `README.md`, so no layer map ties `internal/verify` to the `verify` layer. I read the `verify` tag as the code in `internal/verify`.
- ADR-0007 is `Proposed`, so it binds the change.
- Open point O1 (the clock-skew allowance, 0 or 30 seconds, decided by the security architect) is what blocks a verdict on R4. The 30-second allowance matches one of its two listed answers, but the open point is still unresolved.
