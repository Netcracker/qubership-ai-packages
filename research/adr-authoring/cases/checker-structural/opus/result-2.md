## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` makes the token package `internal/token/verify` import `example/token-gate/internal/http/problem`. That package is an HTTP package, even though it imports only `encoding/json`. |
| ADR-0012 R2 | Not touched | `internal/token/verify` still does not import `net/http`, directly or through `internal/http/problem`. |

Also named in the report:

- Not touched: 1 rule (ADR-0012 R2).
- ADR-0012 names the depguard rule `token-no-http` in `.golangci.yml` as the check for R1 and R2. The golangci-lint result for this change is not available, so the R1 verdict rests on the import in the diff, not on the check.
- No trailer errors, because the change carries no trailers.
- No guide errors: the guide maps the only changed file, `internal/token/verify/problem.go`, to the `token` layer.

## Change B

This check walks no rules, so Change B has no rows. The change touches only the `http` layer, through `internal/http/middleware/scope.go`, and ADR-0012 has no rule tagged `http`. The new imports of `example/token-gate/internal/token/verify` and `net/http` sit in an HTTP package, and R1 and R2 cover only token packages. No token package changes.

Also named in the report:

- Not touched: 2 rules (ADR-0012 R1, R2).
- No trailer errors, because the change carries no trailers.
- No guide errors: the guide maps the only changed file, `internal/http/middleware/scope.go`, to the `http` layer.
