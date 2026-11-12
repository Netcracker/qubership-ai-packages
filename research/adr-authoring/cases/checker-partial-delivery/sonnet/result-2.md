## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | The change alters no outcome for an expired token, because `internal/verify` compares `exp` before it reads `kid`, so it still returns 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | `Implements` claims every case. A missing `kid` now gets 401 `TOKEN_KID_MISSING`, but a `kid` that names no loaded key still gets 401 `TOKEN_INVALID`, where the rule requires `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts: none.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | The change alters no outcome for an expired token, because `internal/verify` compares `exp` before it reads `kid`, so it still returns 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change alters one case, a missing `kid`, which now gets 401 `TOKEN_KID_MISSING` as the rule requires. |

Named apart from the verdicts:

- The change defers ADR-0007 R5 to #12, an open issue. The deferral is named beside the verdict, because the change also touches R5.
- A token whose `kid` names no loaded key gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. This case failed before the change, the change leaves it as it was, and it is not judged. Issue #12 tracks it.
