## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Violates | `Implements` claims every case of R5. A token with an unexpired `exp` whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`, but R5 requires `TOKEN_KID_UNKNOWN`. |

Named apart from the verdicts:

- **Trailer:** `Implements: ADR-0007 R5` claims more than the change brings. The change brings only the no-`kid` case, which now gets HTTP 401 and `TOKEN_KID_MISSING` and meets R5. A change that brings only some cases of a rule names that rule under `Defers`, with the change that brings the rest. Issue #12 is open and tracks the rest of ADR-0007 R5.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to any paths. The changed code in `internal/verify` is under no mapped path.
- **ADR-0007 R4 not walked:** with no guide, the change touches no mapped layer. It also changes the outcome of no case of R4, because `internal/verify` still compares `exp` with the time of the check before it reads `kid`. An expired token still gets HTTP 401 and `TOKEN_EXPIRED`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R5 | Conforms (deferred to #12) | The change touches R5 by changing the outcome of one case: a token with an unexpired `exp` and no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`, which R5 requires. |

Named apart from the verdicts:

- **Deferral:** the trailer names ADR-0007 R5 under `Defers`, and the target is open issue #12, so the entry is valid. Because the change also touches R5, R5 gets the verdict of a touched rule and not `Deferred`. The change does not alter the case where the `kid` names no loaded key, so the check does not judge it. That case still gets HTTP 401 and `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`, and it waits on #12.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps the `verify` layer to any paths. The changed code in `internal/verify` is under no mapped path.
- **ADR-0007 R4 not walked:** with no guide, the change touches no mapped layer. It also changes the outcome of no case of R4, because `internal/verify` still compares `exp` with the time of the check before it reads `kid`. An expired token still gets HTTP 401 and `TOKEN_EXPIRED`.
