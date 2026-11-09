## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violated | A token with a `kid` and an `exp` an hour in the past is now accepted. R4 requires HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Satisfied | A token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. `internal/verify` reads `kid` before it looks at `exp`, and only the `exp` comparison was removed. |

- O1: it does not excuse the R4 violation. Its candidate allowances are 0 seconds and 30 seconds, and an hour is outside both.
- ADR-0007 has status Proposed.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Undecided, blocked on O1 | A token whose `exp` passed 10 seconds ago is now accepted, and R4 as written refuses it. The 30-second allowance is one of the two answers O1 considers, and O1 is not yet decided. |
| ADR-0007 R5 | Satisfied | A token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. `internal/verify` reads `kid` before it looks at `exp`, and the change touches only the `exp` comparison. |

- O1: the security architect decides it, and the change picks the 30-second answer. The change should not merge until that decision is made. If it is 0 seconds, R4 is violated. If it is 30 seconds, R4 needs its text updated.
- A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`. This is consistent with R4 under either answer to O1.
- ADR-0007 has status Proposed.
