## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `verify` compares `exp` before it reads `kid`, so an expired token still gets 401 `TOKEN_EXPIRED` whether or not it has a `kid`. |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. The missing-`kid` case now gets 401 `TOKEN_KID_MISSING` and meets the rule. A `kid` that names no loaded key still gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. |

Named apart:

- Guide error: `docs/adr/` has no `README.md`, so no guide maps `internal/verify` to a layer. I took the `verify` layer from the tags on the rules.
- Trailer errors: none. `Implements: ADR-0007 R5` names a rule of a binding record.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Not touched | `verify` compares `exp` before it reads `kid`, so an expired token still gets 401 `TOKEN_EXPIRED` whether or not it has a `kid`. |
| ADR-0007 R5 | Conforms | The change touches R5 and also names it under `Defers`. The only case the change alters is a token with no `kid`. That token now gets 401 `TOKEN_KID_MISSING`, as R5 requires. The deferral to #12 is named in the first item below. |

Named apart:

- Deferral: R5 is deferred to #12. The case where a `kid` names no loaded key still gets 401 `TOKEN_INVALID`, where R5 requires `TOKEN_KID_UNKNOWN`. This code is unchanged, so the change does not touch that case. It is unmet, and #12 is meant to bring it.
- Guide error: `docs/adr/` has no `README.md`, so no guide maps `internal/verify` to a layer. I took the `verify` layer from the tags on the rules.
- Trailer errors: none. #12 is an open issue that tracks the rest of R5.
