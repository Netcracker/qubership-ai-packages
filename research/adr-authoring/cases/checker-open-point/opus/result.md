## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | `internal/verify` accepts a token that has a `kid` and whose `exp` passed an hour ago, which is outside both answers that O1 lists (0 and 30 seconds). |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- Not touched: 1 rule (ADR-0007 R5).
- Root cause of the violation: Change A deletes the comparison of `exp` with the time of the check in `internal/verify`.
- Trailer errors: none. The change carries no trailers.
- Guide errors: none. Every changed file is under `internal/verify/`, which the guide maps to `verify`.
- `would violate` lines: none. ADR-0007 is `Proposed`, and the guide makes `Proposed` records bind a change, so its rules get verdicts.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | `internal/verify` now accepts a token that has a `kid` and whose `exp` passed 10 seconds ago. This conforms if O1 is answered 30 seconds and violates R4 if it is answered 0 seconds. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`. |

- Not touched: 1 rule (ADR-0007 R5).
- The `Cannot tell` on R4 depends on ADR-0007 O1, the clock-skew allowance after `exp`. The security architect decides it.
- A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`, as it was before the change. That case was not judged because its outcome did not change.
- Trailer errors: none. The change carries no trailers.
- Guide errors: none. Every changed file is under `internal/verify/`, which the guide maps to `verify`.
- `would violate` lines: none. ADR-0007 is `Proposed`, and the guide makes `Proposed` records bind a change, so its rules get verdicts.
