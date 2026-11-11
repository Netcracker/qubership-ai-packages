## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | After the change, a token with a `kid` whose `exp` passed an hour ago is accepted. R4 requires HTTP 401 and `TOKEN_EXPIRED` for that token under both answers O1 lists, 0 seconds and 30 seconds. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` gets HTTP 401 and `TOKEN_KID_MISSING` both before and after the change. |

- `Not touched`: 1 rule (ADR-0007 R5).
- Trailer errors: none, because the change carries no trailers.
- Guide errors: none, because every changed file is under `internal/verify/`, which the guide maps to `verify`.
- Unchecked records: none.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token with a `kid` whose `exp` passed 10 seconds ago is accepted. That meets R4 if O1 settles on 30 seconds and fails it if O1 settles on 0 seconds. The 40-second case meets R4 under both answers. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` gets HTTP 401 and `TOKEN_KID_MISSING` both before and after the change. |

- `Not touched`: 1 rule (ADR-0007 R5).
- `Cannot tell` on ADR-0007 R4 depends on open point ADR-0007 O1, the allowance after `exp`, where the answers are 0 seconds or 30 seconds. The security architect decides it.
- Trailer errors: none, because the change carries no trailers.
- Guide errors: none, because every changed file is under `internal/verify/`, which the guide maps to `verify`.
- Unchecked records: none.
