## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` whose `exp` passed an hour ago is now accepted. R4 requires HTTP 401 and `TOKEN_EXPIRED` for it under both answers that O1 lists, 0 seconds and 30 seconds. |

- **Not touched:** 1 rule, ADR-0007 R5. `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps any path to a layer. The changed file in `internal/verify` is under no mapped path. ADR-0007 R4 was walked because the change alters the outcome of one of its cases, not because the change touches the `verify` layer.
- **Trailers:** none. The change carries no `Implements` or `Defers` line, so no rule is claimed or `Deferred`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token with a `kid` whose `exp` passed 10 seconds ago is now accepted. That meets R4 if O1 settles on 30 seconds and fails it if O1 settles on 0 seconds. A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`, as it was before the change. |

- **Open point that decides the verdict:** ADR-0007 O1, the allowance after `exp`. The security architect decides between 0 seconds and 30 seconds. If O1 settles on 30 seconds, R4 conforms. If it settles on 0 seconds, R4 is violated.
- **Not touched:** 1 rule, ADR-0007 R5. `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps any path to a layer. The changed file in `internal/verify` is under no mapped path. ADR-0007 R4 was walked because the change alters the outcome of one of its cases, not because the change touches the `verify` layer.
- **Trailers:** none. The change carries no `Implements` or `Defers` line, so no rule is claimed or `Deferred`.
