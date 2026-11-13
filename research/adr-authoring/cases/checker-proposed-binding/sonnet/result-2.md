## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. `Implements` claims every case of R5. |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets `TOKEN_EXPIRED` and the new branch alters no R4 outcome. |

Named apart from the verdicts: nothing.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | A token with no `kid` now gets `TOKEN_KID_MISSING`, so the change touches R5. A token whose `kid` names no loaded key still gets `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` before it reads `kid`, so an expired token still gets `TOKEN_EXPIRED` and the new branch alters no R4 outcome. |

Named apart from the verdicts:

- The change names ADR-0007 R5 under `Defers` to #12, which is an open issue, so the trailer is valid. The deferral does not change the verdict, because the change also touches R5. The unknown-`kid` case is the part that waits for #12.
