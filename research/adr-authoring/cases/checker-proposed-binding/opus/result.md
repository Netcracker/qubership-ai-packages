## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | The `Implements` trailer claims every case of R5. A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, but a token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |
| ADR-0007 R4 | Not touched | An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, and `exp` is still compared before `kid` is read, so no R4 outcome changes. |

The report also names:

- Not touched: 1 rule (ADR-0007 R4).
- No trailer errors, guide errors, unchecked records, or `would violate` lines.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Conforms (deferred to #12) | The change touches R5, so R5 gets the verdict of a touched rule and not `Deferred`. The only case whose outcome changes is a token with no `kid` whose `exp` has not passed, and that token now gets HTTP 401 and `TOKEN_KID_MISSING`. |
| ADR-0007 R4 | Not touched | An expired token still gets HTTP 401 and `TOKEN_EXPIRED`, and `exp` is still compared before `kid` is read, so no R4 outcome changes. |

The report also names:

- The deferral: the trailer `Defers: ADR-0007 R5 to #12` names R5. Issue #12 exists and is open, so the target is valid.
- A case of R5 that failed before the change, that the change leaves as it was, and that is not judged: a token whose `exp` has not passed and whose `kid` names no loaded key gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`.
- Not touched: 1 rule (ADR-0007 R4).
- No trailer errors, guide errors, unchecked records, or `would violate` lines.
