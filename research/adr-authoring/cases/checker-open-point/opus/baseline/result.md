## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violated | `internal/verify` now accepts a token that has a `kid` and whose `exp` passed an hour ago. R4 requires HTTP 401 with `TOKEN_EXPIRED` for that token. |
| ADR-0007 R5 | Holds | The change leaves the `kid` check alone, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- O1 does not affect the R4 verdict. The two allowances under consideration are 0 seconds and 30 seconds, and a token that expired an hour ago is past both of them.
- ADR-0007 has the status `Proposed`. The `docs/adr/README.md` reading guide says that `Proposed` records bind a change in this repository, so the R4 violation blocks the change.
- `internal/verify` reads `kid` before it compares `exp`. An expired token with no `kid` is therefore refused under R5 and gets `TOKEN_KID_MISSING`. Only expired tokens that have a `kid` are now accepted.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Undecided (O1) | The 30-second allowance is one of the two answers under consideration in O1, and that open point affects R4. Until the security architect decides, the token that expired 10 seconds ago can't be judged. |
| ADR-0007 R5 | Holds | The change leaves the `kid` check alone, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- The R4 verdict depends on how the security architect answers O1:
  - **30 seconds:** Change B conforms to R4.
  - **0 seconds:** Change B violates R4, because it accepts a token whose `exp` passed 10 seconds ago.
- The token whose `exp` passed 40 seconds ago is refused with HTTP 401 and `TOKEN_EXPIRED`. That outcome conforms to R4 under either answer.
- Change B settles O1 in code, but its commit message and description have no trailers, so neither one records a decision by the security architect. Before the merge, ask the security architect whether the allowance is 0 seconds or 30 seconds.
- ADR-0007 has the status `Proposed`. The `docs/adr/README.md` reading guide says that `Proposed` records bind a change in this repository.
