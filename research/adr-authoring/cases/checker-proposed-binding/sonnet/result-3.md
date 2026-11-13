## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so the new branch does not alter the outcome for a token whose `exp` has passed. It still gets 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | A token with no `kid` now gets 401 `TOKEN_KID_MISSING`, as required. A token whose `kid` names no loaded key still gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. `Implements: ADR-0007 R5` claims every case of the rule, so that case is judged. |

Named apart from the verdicts: none. The `Implements` entry names a rule of ADR-0007, which is `Proposed` and binds changes in this repository, so it is not a trailer error.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so the new branch does not alter the outcome for a token whose `exp` has passed. It still gets 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change touches R5 and alters one case: a token with no `kid` now gets 401 `TOKEN_KID_MISSING`, as required. The change defers R5 to #12 and also touches it, so it gets the verdict of a touched rule. |

Named apart from the verdicts:

- Deferral: the change names ADR-0007 R5 under `Defers`, with target issue #12. That issue is open and tracks the rest of R5, so the entry is valid.
- Case not judged: a token whose `kid` names no loaded key gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. This case failed before the change and the change leaves it as it was. #12 tracks it.
