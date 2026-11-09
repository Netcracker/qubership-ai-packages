## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Fails | Change A deletes the `exp` check, so `internal/verify` accepts a token whose `exp` passed an hour ago. R4 requires HTTP 401 with `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Passes | `internal/verify` still reads `kid` first and refuses a token with no `kid` with HTTP 401 and `TOKEN_KID_MISSING`. |

- **Open point O1:** O1 doesn't change the R4 verdict. The two allowances under consideration are 0 seconds and 30 seconds, and both refuse a token whose `exp` passed an hour ago.
- **Record status:** ADR-0007 is Proposed, not Accepted.
- **Trailers:** The commit message and description carry no trailers.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Undecided, waiting on O1 | A token whose `exp` passed 10 seconds ago is now accepted. That is correct with a 30-second allowance and breaks R4 with a 0-second allowance. The 40-second case meets R4 with either allowance. |
| ADR-0007 R5 | Passes | `internal/verify` still reads `kid` first and refuses a token with no `kid` with HTTP 401 and `TOKEN_KID_MISSING`. |

- **Open point O1:** Change B uses the 30-second allowance, which is one of the two answers O1 is still considering. O1 hasn't been decided.
- **Decider:** The security architect decides O1, so the security architect needs to settle it before R4 can get a verdict.
- **Record status:** ADR-0007 is Proposed, not Accepted.
- **Trailers:** The commit message and description carry no trailers, so neither one points to a decision on O1.
