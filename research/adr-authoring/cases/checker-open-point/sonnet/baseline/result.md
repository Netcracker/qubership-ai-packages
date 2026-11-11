## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violated | A token with a `kid` whose `exp` passed an hour ago is accepted, where R4 requires HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Satisfied | `internal/verify` still reads `kid` first and refuses a token with no `kid` with HTTP 401 and `TOKEN_KID_MISSING`. |

- ADR-0007 is `Proposed`, and the reading guide says `Proposed` records bind a change. The change touches the `verify` layer.
- Open point O1 (clock-skew allowance, 0 or 30 seconds, security architect decides) does not excuse this change. An allowance of one hour is outside both answers under consideration.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Open, depends on O1 | A token whose `exp` passed 10 seconds ago is accepted, which R4 as written forbids. The 30-second allowance is one of the two answers to O1, and that point is undecided. |
| ADR-0007 R5 | Satisfied | `internal/verify` still reads `kid` first and refuses a token with no `kid` with HTTP 401 and `TOKEN_KID_MISSING`. |

- ADR-0007 is `Proposed`, and the reading guide says `Proposed` records bind a change. The change touches the `verify` layer.
- O1 (how long after `exp` a token is still accepted) is undecided, and the security architect decides it. Change B picks the 30-second answer. If the architect chooses 30 seconds, R4 is satisfied. If the architect chooses 0 seconds, R4 is violated.
- A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`, as R4 requires.
