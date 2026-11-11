## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` checks `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`, as it did before the change. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5, and a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

Other items in the report:

- 1 rule is `Not touched` (ADR-0007 R4).
- The change adds the missing-`kid` case of R5, which now gets HTTP 401 and `TOKEN_KID_MISSING`. That case conforms, but the unknown-`kid` case still fails R5.
- The verified facts don't say which outcome a token with no `kid` gets when its `exp` equals the time of the check. This doesn't change the R5 verdict.
- `Implements` claims every case of a rule, and this change brings only one case of R5. The trailer that matches this change is `Defers: ADR-0007 R5 to #12`.
- There are no trailer errors and no guide errors. ADR-0007 names no check under **Confirmation**.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `internal/verify` checks `exp` before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`, as it did before the change. |
| ADR-0007 R5 | Conforms (deferred to #12) | The change alters only the missing-`kid` case, and that case now gets HTTP 401 and `TOKEN_KID_MISSING`. |

Other items in the report:

- 1 rule is `Not touched` (ADR-0007 R4).
- The change names ADR-0007 R5 under `Defers`, but it also touches R5. R5 therefore gets the verdict of a touched rule, and the report records the deferral to #12 next to it.
- The change doesn't alter the unknown-`kid` case of R5, so that case isn't judged. A token whose `kid` names no loaded key still gets `TOKEN_INVALID`, and open issue #12 tracks that case.
- There are no trailer errors, because #12 is an existing issue. There are no guide errors. ADR-0007 names no check under **Confirmation**.
