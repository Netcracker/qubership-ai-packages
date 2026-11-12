## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | After the change, a token with a `kid` whose `exp` passed an hour ago is accepted. R4 requires HTTP 401 with `TOKEN_EXPIRED` for that token under both answers O1 lists (0 seconds and 30 seconds). |
| ADR-0007 R5 | Not touched | `internal/verify` still reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- Not touched: 1 rule (R5).
- Trailer errors: none. The commit message and the description carry no trailers.
- Guide errors: none. The change touches only `internal/verify/`, which the guide maps to `verify`.
- Records left unchecked: none.
- Machine checks: none counted. ADR-0007 names no check under **Confirmation**.
- Cases judged `Cannot tell`: a token with a `kid` whose `exp` passed 30 seconds ago or less. Its outcome depends on O1, which the security architect has not yet decided. The verdict on R4 does not change, because the token whose `exp` passed an hour ago already violates the rule.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token with a `kid` whose `exp` passed 10 seconds ago is now accepted. R4 allows that if O1 settles on 30 seconds and forbids it if O1 settles on 0 seconds. |
| ADR-0007 R5 | Not touched | `internal/verify` still reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- Not touched: 1 rule (R5).
- Trailer errors: none. The commit message and the description carry no trailers.
- Guide errors: none. The change touches only `internal/verify/`, which the guide maps to `verify`.
- Records left unchecked: none.
- Machine checks: none counted. ADR-0007 names no check under **Confirmation**.
- What the check could not settle: whether O1 allows 0 seconds or 30 seconds after `exp`. The security architect decides that.
- Cases the change leaves as they were: a token with a `kid` whose `exp` passed more than 30 seconds ago, for example 40 seconds ago. It was refused with HTTP 401 and `TOKEN_EXPIRED` before the change and still is, so it was not judged.
