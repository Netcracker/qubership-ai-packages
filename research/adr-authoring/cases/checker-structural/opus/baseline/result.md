## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, which is an HTTP package. |
| ADR-0012 R2 | Satisfied | `problem.go` doesn't import `net/http`. `internal/http/problem` imports only `encoding/json`, so `net/http` doesn't come in indirectly either. |

- ADR-0012 is `Accepted`, so the R1 violation blocks this change. The commit message and description have no trailers, so the change doesn't claim an exception and doesn't supersede the record.
- ADR-0012 says the depguard rule `token-no-http` in `.golangci.yml` should catch this import. The golangci-lint result for this change isn't available, so I can't tell whether CI reported it.
- The new import doesn't create a cycle: `internal/http/problem` imports only `encoding/json`. The Go build therefore won't catch the violation, and depguard is the only check that can.
- One fix is to have `verify` return the refusal as a value from the token layer, and build the RFC 9457 problem document in `internal/http/`, for example in `internal/http/middleware`.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not applicable | R1 covers the `token` layer, and the only file this change adds is `internal/http/middleware/scope.go` in the `http` layer. |
| ADR-0012 R2 | Not applicable | R2 also covers only the `token` layer. `scope.go` imports `net/http` from inside `internal/http/`, and ADR-0012 doesn't restrict that. |

- When `scope.go` imports `example/token-gate/internal/token/verify`, the dependency goes from the HTTP layer to the token layer. ADR-0012 allows this direction, and `internal/http/middleware` already imported `verify` before this change.
- The golangci-lint result for this change isn't available.
