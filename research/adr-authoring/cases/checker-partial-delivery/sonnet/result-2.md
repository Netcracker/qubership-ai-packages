## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token with no `kid` still gets 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | A token with no `kid` now gets 401 and `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets 401 and `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. `Implements: ADR-0007 R5` claims every case of the rule. |

Named apart from the verdicts: nothing.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token with no `kid` still gets 401 and `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change alters one case, a token with no `kid`, which now gets 401 and `TOKEN_KID_MISSING` as R5 requires. The rule is named under `Defers` and also touched, so it gets the verdict of a touched rule, with the deferral to #12 named here. |

Named apart from the verdicts:

- The case of a token whose `kid` names no loaded key still gets 401 and `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. The change leaves this case as it was, so it is not judged. The change names it for #12 under `Defers`.
- `Defers: ADR-0007 R5 to #12` is a valid trailer. R5 belongs to an `Accepted` record, and #12 is an open issue that tracks the rest of R5.
