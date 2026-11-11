## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | The new file `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, so the token package `internal/token/verify` now imports an HTTP package. |
| ADR-0012 R2 | Not touched | The change adds no `net/http` import to any token package. `internal/http/problem` imports only `encoding/json`, so `net/http` doesn't arrive indirectly either. |

- Not touched: 1 rule (ADR-0012 R2).
- The depguard rule `token-no-http` in `.golangci.yml` is the check that ADR-0012 names for R1 and R2. Its CI result for this change isn't available, so R1 was judged by reading the diff.
- Guide errors: none. `internal/token/verify/problem.go` sits under `internal/token/`, which the guide maps to the `token` layer.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |

- The check walks no rule. The change touches only the `http` layer, and no rule of ADR-0012 sits in that layer. R1 and R2 sit in the `token` layer, and the change makes no token package import anything new.
- The `net/http` import in `internal/http/middleware/scope.go` comes from an HTTP package, and no rule constrains what an HTTP package imports.
- Guide errors: none. `internal/http/middleware/scope.go` sits under `internal/http/`, which the guide maps to the `http` layer.
