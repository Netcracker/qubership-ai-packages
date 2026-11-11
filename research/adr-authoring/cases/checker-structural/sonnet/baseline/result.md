## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | `internal/token/verify/problem.go` is in a token package and imports `example/token-gate/internal/http/problem`, an HTTP package. |
| ADR-0012 R2 | Satisfied | No token package imports `net/http`. `internal/http/problem` imports only `encoding/json`. |

- The golangci-lint result, including the depguard rule `token-no-http` that confirms R1 and R2, is not available to me. Both verdicts come from the imports.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not applicable | R1 is scoped to the `token` layer. `internal/http/middleware/scope.go` is in the `http` layer. |
| ADR-0012 R2 | Not applicable | R2 is scoped to the `token` layer. Importing `net/http` from the `http` layer is outside it. |

- The golangci-lint result, including the depguard rule `token-no-http`, is not available to me. Both verdicts come from the imports.
- The import of `example/token-gate/internal/token/verify` runs from the HTTP layer to the token layer. ADR-0012 has no rule against that direction, and `internal/http/middleware` already imports it.
