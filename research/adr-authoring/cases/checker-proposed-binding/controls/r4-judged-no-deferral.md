## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Conforms | Expired tokens still get `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. A token whose `exp` has not passed and whose `kid` names no loaded key gets `TOKEN_INVALID`, but R5 requires `TOKEN_KID_UNKNOWN`. |

- Not touched: 1 rule (ADR-0007 R4).
- The case that fails R5 is a token whose `kid` names no loaded key. It failed before the change too, and the change leaves it as it was. The case of a token with no `kid` now conforms, because it gets HTTP 401 with `TOKEN_KID_MISSING`.
- `Implements: ADR-0007 R5` claims more than the change delivers, because the change brings only the missing-`kid` case. The trailer should name the rule under `Defers` and point at the change that brings the rest, which is issue #12.
- The repository does not show which response a token gets when its `exp` equals the time of the check. Under one reading of "has not passed", R5 covers that token, so that case cannot be judged. This does not change the verdict.
- No trailer errors, no guide errors, and no unchecked records.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Conforms | Expired tokens still get `TOKEN_EXPIRED`. |

- Not touched: 1 rule (ADR-0007 R4).
- No trailer errors, no guide errors, and no unchecked records.
