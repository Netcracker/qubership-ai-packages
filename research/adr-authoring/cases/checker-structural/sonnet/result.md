## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, an HTTP package, from a token package. |
| ADR-0012 R2 | Not touched | The new file does not import `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Named apart:
- The golangci-lint result, including the `token-no-http` check, is not available. The R1 verdict rests on reading the imports.
- The commit message and description carry no trailers, so no claim was read.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not touched | The change touches only the `http` layer, and no token package gains or loses an import. `scope.go` imports a token package, not the reverse. |
| ADR-0012 R2 | Not touched | No token package gains or loses an import. `net/http` is imported only from `internal/http/middleware`, which is not a token package. |

Named apart:
- Both rules are tagged `token`, and the change touches no file in that layer, so the walk does not reach them. They are listed as the nearest rules.
- The commit message and description carry no trailers, so no claim was read.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`, an HTTP package, from a token package. |
| ADR-0012 R2 | Not touched | The new file does not import `net/http`, and `internal/http/admin` imports only `encoding/json`. |

Named apart:
- `internal/token/verify/session.go` already imports `example/token-gate/internal/http/auth`. This R1 failure predates the change and the change leaves it as it was, so it is not judged here.
- The golangci-lint result, including the `token-no-http` check, is not available. The R1 verdict rests on reading the imports.
- The commit message and description carry no trailers, so no claim was read.
