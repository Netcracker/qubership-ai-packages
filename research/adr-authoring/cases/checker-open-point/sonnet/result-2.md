## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` and an `exp` an hour past is accepted, but R4 requires HTTP 401 and `TOKEN_EXPIRED`. Both answers to O1 (0 or 30 seconds) refuse it. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` still gets HTTP 401 and `TOKEN_KID_MISSING`, whatever its `exp`. |

- Guide error: `docs/adr/` has no `README.md`, so no layer maps to a path. The changed file under `internal/verify` is under no mapped path. I took the `verify` layer from the rules' own tags.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token 40 seconds past `exp` is refused, which meets R4 under both answers to O1. A token 10 seconds past `exp` is accepted, which meets R4 if O1 is 30 seconds and fails it if O1 is 0 seconds. The security architect has not decided O1. |
| ADR-0007 R5 | Not touched | `internal/verify` reads `kid` before `exp`, so a token with no `kid` still gets HTTP 401 and `TOKEN_KID_MISSING`, whatever its `exp`. |

- Guide error: `docs/adr/` has no `README.md`, so no layer maps to a path. The changed file under `internal/verify` is under no mapped path. I took the `verify` layer from the rules' own tags.
