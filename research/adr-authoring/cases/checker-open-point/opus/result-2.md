## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Violates | A token with a `kid` whose `exp` passed an hour ago is now accepted. R4 requires HTTP 401 with `TOKEN_EXPIRED`, and an hour is past both answers that O1 lists (0 seconds and 30 seconds). |

- **Not touched:** 1 rule (ADR-0007 R5). `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps a path to the `verify` layer. The changed code in `internal/verify` is under no mapped path. As a result, only rules that the change touches were walked, not every rule in the layer.
- **Trailer errors:** none. The commit message and the description carry no trailers.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Cannot tell | A token with a `kid` whose `exp` passed 10 seconds ago is now accepted. This fails R4 if O1 is answered with 0 seconds and meets it if O1 is answered with 30 seconds. A token whose `exp` passed 40 seconds ago is still refused with HTTP 401 and `TOKEN_EXPIRED`, which meets R4 under both answers. |

- **Not touched:** 1 rule (ADR-0007 R5). `internal/verify` reads `kid` before it compares `exp`, so a token with no `kid` is still refused with HTTP 401 and `TOKEN_KID_MISSING`.
- **Open point:** the verdict on R4 depends on ADR-0007 O1, which the security architect decides.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps a path to the `verify` layer. The changed code in `internal/verify` is under no mapped path. As a result, only rules that the change touches were walked, not every rule in the layer.
- **Trailer errors:** none. The commit message and the description carry no trailers.
