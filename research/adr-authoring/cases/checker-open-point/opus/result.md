## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | After the change, `internal/verify` accepts a token with a `kid` whose `exp` passed an hour ago. R4 requires HTTP 401 and `TOKEN_EXPIRED` for that token whether O1 settles on 0 or 30 seconds. |
| ADR-0007 R5 | Not touched | `internal/verify` still reads `kid` before `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

The report names nothing else: there are no trailer errors, no guide errors, and no unchecked records.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | `internal/verify` now accepts a token with a `kid` whose `exp` passed 10 seconds ago. That meets R4 if O1 settles on 30 seconds and fails it if O1 settles on 0 seconds. The security architect decides O1. |
| ADR-0007 R5 | Not touched | `internal/verify` still reads `kid` before `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

The report names nothing else: there are no trailer errors, no guide errors, and no unchecked records.
