## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | `Implements` claims every case. A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, which meets the rule. A token whose `kid` names no loaded key still gets `TOKEN_INVALID` where the rule requires `TOKEN_KID_UNKNOWN`. |
| ADR-0007 R4 | Conforms | The expiry check still holds. |

- Guide error: `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to a path. The changed file in `internal/verify` is under no mapped path, and the walk by layer cannot run.
- Not touched: 1 rule (ADR-0007 R4). `internal/verify` compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`.
- Trailer: the change brings only the missing-`kid` case of ADR-0007 R5. The trailer should name the rule as `name: ADR-0007 R5 to the issue` rather than `Implements: ADR-0007 R5`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Conforms (named under `name` to the issue) | The change touches the rule because it alters the outcome of the missing-`kid` case. That case now gets HTTP 401 and `TOKEN_KID_MISSING`, as the rule requires. |
| ADR-0007 R4 | Conforms | The expiry check still holds. |

- name: the change names ADR-0007 R5 under `name` and also touches it, so the rule gets the verdict of a touched rule and not `name`. The target, issue the issue, exists and is open.
- Unchanged defect: a token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. The change does not alter this case, and issue the issue tracks it.
- Guide error: `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to a path. The changed file in `internal/verify` is under no mapped path, and the walk by layer cannot run.
- Not touched: 1 rule (ADR-0007 R4). `internal/verify` compares `exp` with the time of the check before it reads `kid`, so an expired token still gets HTTP 401 and `TOKEN_EXPIRED`.
