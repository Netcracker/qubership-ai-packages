## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | A token with no `kid` now gets 401 and `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. `Implements: ADR-0007 R5` claims both cases. |

- Guide error: `docs/adr/` has no `README.md`, so no layer maps to a path. The changed file under `internal/verify` is under no mapped path.
- Trailer errors: none.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change alters only the missing-`kid` case, and that case now gets 401 and `TOKEN_KID_MISSING`. The rule is also named under `Defers`, as described below. |

- Deferral: `Defers: ADR-0007 R5 to #12` is a valid entry, because issue #12 exists and is open. The unknown-`kid` case is unchanged and still gets 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. Issue #12 tracks that case.
- Guide error: `docs/adr/` has no `README.md`, so no layer maps to a path. The changed file under `internal/verify` is under no mapped path.
- Trailer errors: none.
