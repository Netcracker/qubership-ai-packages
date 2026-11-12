## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`, with or without a `kid`. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. A token whose `exp` has not passed and whose header has no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, which conforms. A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`, which violates R5. |

Named apart:

- One rule is `Not touched`: ADR-0007 R4.
- The change brings only the missing-`kid` case of ADR-0007 R5, but `Implements` claims every case. The trailer names a rule of a binding record, so it isn't a trailer error. The unmet case is what gives R5 its `Violates` verdict.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`, with or without a `kid`. |
| ADR-0007 R5 (deferred to #12) | Conforms | The change alters only the missing-`kid` case. A token whose `exp` has not passed and whose header has no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`. |

Named apart:

- One rule is `Not touched`: ADR-0007 R4.
- ADR-0007 R5 is deferred to issue #12, which is open. The change also touches R5, so R5 gets the verdict of a touched rule and not `Deferred`.
- One case of ADR-0007 R5 already failed before the change and still fails after it, so it wasn't judged. A token whose `kid` names no loaded key gets HTTP 401 and `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`.
