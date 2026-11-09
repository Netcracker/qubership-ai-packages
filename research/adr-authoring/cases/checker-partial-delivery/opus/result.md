## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | `Implements` claims every case. A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, which meets the rule. A token whose `kid` names no loaded key still gets `TOKEN_INVALID` where the rule requires `TOKEN_KID_UNKNOWN`. |

- Guide error: `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to a path. The changed file in `internal/verify` is under no mapped path, and the walk by layer cannot run.
- Not touched: 1 rule (ADR-0007 R4). `internal/verify` compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`.
- Trailer: the change brings only the missing-`kid` case of ADR-0007 R5. The trailer should name the rule as `Defers: ADR-0007 R5 to #12` rather than `Implements: ADR-0007 R5`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Conforms (named under `Defers` to #12) | The change touches the rule because it alters the outcome of the missing-`kid` case. That case now gets HTTP 401 and `TOKEN_KID_MISSING`, as the rule requires. |

- Deferral: the change names ADR-0007 R5 under `Defers` and also touches it, so the rule gets the verdict of a touched rule and not `Deferred`. The target, issue #12, exists and is open.
- Unchanged defect: a token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. The change does not alter this case, and issue #12 tracks it.
- Guide error: `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to a path. The changed file in `internal/verify` is under no mapped path, and the walk by layer cannot run.
- Not touched: 1 rule (ADR-0007 R4). `internal/verify` compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`.
