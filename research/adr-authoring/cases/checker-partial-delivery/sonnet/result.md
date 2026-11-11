## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | An expired token still gets 401 `TOKEN_EXPIRED`, because `exp` is compared before `kid` is read, so no case outcome changes. |
| ADR-0007 R5 | Violates | `Implements` claims every case. A token with no `kid` now gets 401 `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets 401 `TOKEN_INVALID` where the rule requires `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts: nothing. The trailer names a rule of an Accepted record, and the change touches no file outside `internal/verify/`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | An expired token still gets 401 `TOKEN_EXPIRED`, because `exp` is compared before `kid` is read, so no case outcome changes. |
| ADR-0007 R5 | Conforms | The one case the change alters, a token with no `kid`, now gets 401 `TOKEN_KID_MISSING` as required. The rule is named under `Defers ... to #12`, and the unaltered `kid`-unknown case still gets `TOKEN_INVALID`, which issue #12 tracks. |

Named apart from the verdicts: nothing. Issue #12 is open, so the `Defers` target is valid, and the change touches no file outside `internal/verify/`.
