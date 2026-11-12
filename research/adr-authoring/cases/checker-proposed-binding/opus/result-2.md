## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` with the time of the check before it reads `kid`, both before and after the change. An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, and no outcome of R4 changes. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts: nothing. The `Implements` entry names a rule of a binding record, so it is not a trailer error. Every changed file is under `internal/verify/`, which the guide maps to `verify`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` with the time of the check before it reads `kid`, both before and after the change. An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, and no outcome of R4 changes. |
| ADR-0007 R5 | Conforms (deferred to #12) | The change alters one case of R5: a token with no `kid` whose `exp` has not passed. That token now gets HTTP 401 and `TOKEN_KID_MISSING`, as R5 requires. R5 gets the verdict of a touched rule because the change touches it, even though `Defers` names it. |

Named apart from the verdicts:

- The trailer defers ADR-0007 R5 to #12, an open issue that tracks the rest of R5. The target exists, so the entry is not a trailer error.
- One case of R5 failed before the change and still fails after it. The change leaves this case as it was, so it is not judged: a token whose `kid` names no loaded key gets HTTP 401 and `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`.
