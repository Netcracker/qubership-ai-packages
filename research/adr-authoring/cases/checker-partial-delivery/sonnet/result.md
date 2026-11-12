## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | The change alters no outcome for a token whose `exp` has passed: `internal/verify` still compares `exp` before it reads `kid` and returns 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | `Implements: ADR-0007 R5` claims every case. A token whose `kid` names no loaded key still gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. The missing-`kid` case now meets the rule with 401 `TOKEN_KID_MISSING`. |

Named apart from the verdicts: nothing. The trailer names a rule of a binding record, and every changed file is under `internal/verify/`, which the guide maps to a layer.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | The change alters no outcome for a token whose `exp` has passed: `internal/verify` still compares `exp` before it reads `kid` and returns 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change alters one case: a token with no `kid` and an `exp` that has not passed now gets 401 `TOKEN_KID_MISSING`, as R5 requires. The rule is also named under `Defers`, so the deferral stands beside this verdict. |

Named apart from the verdicts:

- Deferral: `Defers: ADR-0007 R5 to #12` names an existing open issue that tracks the rest of R5, so it is not a trailer error.
- Unjudged case of R5: a token whose `kid` names no loaded key gets 401 `TOKEN_INVALID` where R5 requires `TOKEN_KID_UNKNOWN`. This failed before the change, the change leaves it as it was, and it is not judged here. The deferral to #12 covers it.
