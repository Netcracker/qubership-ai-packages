## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, an HTTP package, so a token package now imports an HTTP package. |
| ADR-0012 R2 | Not touched | The new file does not import `net/http`, and `internal/http/problem` imports only `encoding/json`, so `verify` met R2 before the change and still does. |

- The CI golangci-lint result is not available. The depguard rule `token-no-http` that confirms R1 and R2 therefore earns no credit, and the R1 verdict comes from reading the import.
- The commit message and description carry no trailers. The change brings no rule, so none are owed.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| None | | ADR-0012 sets no rule on an HTTP package. |

- ADR-0012 R1 and R2 are Not touched (count: 2). They range over token packages, and the change adds no file to one. The new import in `internal/http/middleware/scope.go` points from the `http` layer to the `token` layer, which R1 and R2 do not constrain.
- The CI golangci-lint result is not available, so no machine check is credited.
- The commit message and description carry no trailers. The change brings no rule and leaves none out, so none are owed.
