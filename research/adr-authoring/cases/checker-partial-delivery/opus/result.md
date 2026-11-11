## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | The `Implements` trailer claims both cases of R5. A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, which meets R5. A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` with the time of the check before it reads `kid`, both before and after the change. An expired token therefore still gets HTTP 401 and `TOKEN_EXPIRED` whatever its `kid` is, and the trailers don't name R4. |

- Not touched: 1 rule (ADR-0007 R4).
- The `Implements: ADR-0007 R5` trailer claims every case of R5, but the change brings only the missing-`kid` case. A change that brings only some cases of a rule names that rule under `Defers`, with the change that brings the rest.
- Trailer errors: none.
- Guide errors: none. The only changed path is `internal/verify/`, which the guide maps to `verify`.
- ADR-0007 names no machine check under **Confirmation**, so every case was judged against the code.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Conforms | The change alters only the missing-`kid` case. A token with no `kid` whose `exp` has not passed now gets HTTP 401 and `TOKEN_KID_MISSING`, as R5 requires. The unknown-`kid` case keeps its outcome, and the change doesn't name R5 under `Implements`, so that case isn't judged. |
| ADR-0007 R4 | Not touched | `internal/verify` compares `exp` with the time of the check before it reads `kid`, both before and after the change. An expired token therefore still gets HTTP 401 and `TOKEN_EXPIRED` whatever its `kid` is, and the trailers don't name R4. |

- ADR-0007 R5 is deferred to #12, and the change also touches R5. It therefore gets the verdict of a touched rule rather than `Deferred`. Issue #12 is open and tracks the rest of R5: a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`.
- Not touched: 1 rule (ADR-0007 R4).
- Trailer errors: none. The `Defers` target #12 is an existing issue.
- Guide errors: none. The only changed path is `internal/verify/`, which the guide maps to `verify`.
- ADR-0007 names no machine check under **Confirmation**, so every case was judged against the code.
