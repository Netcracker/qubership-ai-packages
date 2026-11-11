## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | The change names R5 under `Implements`, so every case is judged. A token with no `kid` now gets 401 `TOKEN_KID_MISSING`, which meets R5. A token whose `kid` names no loaded key still gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts:

- The `Implements: ADR-0007 R5` trailer claims the whole rule, but the unknown-`kid` case is unmet. A claim for only the missing-`kid` part would need `Defers: ADR-0007 R5 to #12`.
- Trailer errors: none. ADR-0007 is `Proposed`, and the guide makes `Proposed` records bind.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets 401 `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Conforms | The change alters one case, a token with no `kid` and an `exp` that has not passed. It now gets 401 `TOKEN_KID_MISSING`, as R5 requires. Deferred to #12 by `Defers: ADR-0007 R5 to #12`. |

Named apart from the verdicts:

- Deferral: R5 is named under `Defers` and also touched, so it gets the verdict of a touched rule. The deferral is beside it. #12 is open and tracks the rest of R5, so the target is valid.
- The unknown-`kid` case of R5 failed before the change, and the change leaves it as it was (401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`). It is not judged here. It is the part that #12 tracks.
- Trailer errors: none.
