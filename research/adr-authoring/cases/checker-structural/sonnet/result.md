## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, and `verify` is a token package. |
| ADR-0012 R2 | Not touched | `problem.go` imports no `net/http`, and `internal/http/problem` imports only `encoding/json`, so `verify` meets R2 before and after. |

Named apart from the verdicts:

- The depguard rule `token-no-http` is the check that ADR-0012 names under Confirmation for R1 and R2. Its CI result is not available, so the R1 verdict comes from reading the import in the diff.
- The commit message and description carry no trailers. No entry names a missing rule, so there is no trailer error.
- The one changed file maps to the `token` layer, so there is no guide error.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not touched | The change adds a file only under `internal/http/middleware`, which is no token package. No token package gains or loses an import. |
| ADR-0012 R2 | Not touched | `scope.go` imports `net/http`, but it sits in an HTTP package. R2 constrains token packages only, and none changes. |

Named apart from the verdicts:

- `internal/http/middleware` already imported `internal/token/verify`, and `scope.go` repeats that import. The direction http to token is the one ADR-0012 allows.
- Both rules are tagged `token`, and the change touches only the `http` layer, so the check walks neither as a layer rule. Both rows are the count of rules not touched.
- The commit message and description carry no trailers. The change brings and defers no rule, so none are owed and there is no trailer error.
- The one changed file maps to the `http` layer, so there is no guide error.
- CI golangci-lint results are not available for this change.
