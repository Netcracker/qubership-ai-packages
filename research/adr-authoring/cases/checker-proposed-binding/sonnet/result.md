## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets 401 and `TOKEN_EXPIRED`, with or without a `kid`. |
| ADR-0007 R5 | Violates | The change names R5 under `Implements`, which claims every case. A token with no `kid` now gets `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets 401 and `TOKEN_INVALID` where R5 requires `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts: nothing.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` still compares `exp` before it reads `kid`, so an expired token still gets 401 and `TOKEN_EXPIRED`, with or without a `kid`. |
| ADR-0007 R5 | Conforms | The change alters one case of R5: a token with no `kid` and an `exp` that has not passed. That token now gets 401 and `TOKEN_KID_MISSING`, as R5 requires. |

Named apart from the verdicts:

- ADR-0007 R5 is deferred to issue #12, which is open. The deferral stands beside the verdict `Conforms` because the change also touches R5.
- The case of a token whose `kid` names no loaded key is not judged. It gets 401 and `TOKEN_INVALID` before and after the change, where R5 requires `TOKEN_KID_UNKNOWN`. The change leaves it as it was.
