## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | The new file `internal/token/verify/problem.go` makes the token package `internal/token/verify` import the HTTP package `example/token-gate/internal/http/problem`. |
| ADR-0012 R2 | Not touched | The change adds no `net/http` import, and `internal/http/problem` imports only `encoding/json`. |

- Not touched: 1 rule (ADR-0012 R2).
- The R1 verdict comes from the imports in the diff, not from the depguard rule `token-no-http`, because its CI result was not available.
- There are no trailer errors and no guide errors. `internal/token/verify/problem.go` is in the `token` layer.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |

- No rule is walked. The change touches only the `http` layer, and ADR-0012 has no rule there. Its imports of `example/token-gate/internal/token/verify` and `net/http` are in an HTTP package, so they add no import that R1 or R2 forbids.
- Not touched: 2 rules (ADR-0012 R1, R2).
- There are no trailer errors and no guide errors. `internal/http/middleware/scope.go` is in the `http` layer.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | The new file `internal/token/verify/admin.go` adds an import of the HTTP package `example/token-gate/internal/http/admin`. A new forbidden import still changes the outcome, even though `internal/token/verify` already failed R1. |
| ADR-0012 R2 | Not touched | The change adds no `net/http` import, and `internal/http/admin` imports only `encoding/json`. |

- Not touched: 1 rule (ADR-0012 R2).
- The existing import of `example/token-gate/internal/http/auth` in `internal/token/verify/session.go` already violated ADR-0012 R1. Change C leaves it as it was, so it was not judged.
- The R1 verdict comes from the imports in the diff, not from the depguard rule `token-no-http`, because its CI result was not available.
- There are no trailer errors and no guide errors. `internal/token/verify/admin.go` is in the `token` layer.
