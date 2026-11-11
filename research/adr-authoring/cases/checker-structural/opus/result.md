## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` adds an import of `example/token-gate/internal/http/problem`, so the token package `internal/token/verify` now imports an HTTP package. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Named apart:

- The result of the depguard rule `token-no-http` is not available. The verdict on R1 comes from the imports in the diff.
- Not touched: 1 rule (ADR-0012 R2).

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| None | None | The change touches only the `http` layer, where ADR-0012 has no rules. The new imports in `internal/http/middleware` come from an HTTP package, not a token package, so they change no outcome of R1 or R2. |

Named apart:

- Not touched: 2 rules (ADR-0012 R1 and R2).

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` adds a new import of `example/token-gate/internal/http/admin` to a token package. The package already failed R1, but a new forbidden import still changes an outcome. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/admin` imports only `encoding/json`. |

Named apart:

- Older violation, not judged: `internal/token/verify/session.go` imports `example/token-gate/internal/http/auth`. This import existed before the change, which leaves it unchanged.
- The result of the depguard rule `token-no-http` is not available. The verdict on R1 comes from the imports in the diff.
- Not touched: 1 rule (ADR-0012 R2).
