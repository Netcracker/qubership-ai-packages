## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

Named apart: nothing. The trailer has no errors, because ADR-0007 R5 is a rule of an `Accepted` record, and no file the change touches is a guide error.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms (deferred to #12) | The change touches R5 and changes only the outcome for a token with no `kid`, which now gets HTTP 401 and `TOKEN_KID_MISSING`. |

Named apart:

- The `Defers` trailer names ADR-0007 R5 to #12, and the change also touches R5. #12 is an open issue, so it is a valid `Defers` target.
- One case of ADR-0007 R5 failed before the change, and the change leaves it as it was, so it is not judged. A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`.
