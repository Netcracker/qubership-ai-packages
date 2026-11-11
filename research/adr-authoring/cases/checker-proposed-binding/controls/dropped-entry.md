## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | An expired token still gets HTTP 401 with `TOKEN_EXPIRED`, and `exp` is still checked before `kid`, so no outcome of R4 changes. |
| ADR-0007 R5 | Conforms | ADR-0007 is `Proposed`, so the `Implements` entry counts for no verdict; the missing-`kid` case is right. |

- Not touched: 1 rule (ADR-0007 R4).
- The case that fails R5 is a token whose `kid` names no loaded key. It failed before the change too, and the change leaves it as it was. The case of a token with no `kid` now conforms, because it gets HTTP 401 with `TOKEN_KID_MISSING`.
- `Implements: ADR-0007 R5` claims more than the change delivers, because the change brings only the missing-`kid` case. The trailer should name the rule under `Defers` and point at the change that brings the rest, which is issue #12.
- The repository does not show which response a token gets when its `exp` equals the time of the check. Under one reading of "has not passed", R5 covers that token, so that case cannot be judged. This does not change the verdict.
- No trailer errors, no guide errors, and no unchecked records.
- would violate ADR-0007 R5: the unknown-`kid` case still gets `TOKEN_INVALID`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | An expired token still gets HTTP 401 with `TOKEN_EXPIRED`, and `exp` is still checked before `kid`, so no outcome of R4 changes. |
| ADR-0007 R5 | Conforms (deferred to #12) | The only case whose outcome changes is a token with no `kid` whose `exp` has not passed, and it now gets HTTP 401 with `TOKEN_KID_MISSING`. |

- Not touched: 1 rule (ADR-0007 R4).
- The trailer defers ADR-0007 R5 to issue #12, which exists and is open. The change also touches R5, so R5 gets the verdict of a touched rule rather than `Deferred`.
- A token whose `exp` has not passed and whose `kid` names no loaded key still gets `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. That case failed before the change, the change leaves it as it was, and issue #12 tracks it.
- No trailer errors, no guide errors, and no unchecked records.
