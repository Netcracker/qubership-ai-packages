## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, which is an HTTP package. |
| ADR-0012 R2 | Not touched | The new file does not import `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Named apart:

- The golangci-lint result for the depguard rule `token-no-http` is not available. The R1 verdict comes from reading the import, not from that check.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not touched | `internal/http/middleware/scope.go` is in an HTTP package, and R1 constrains only imports made by token packages. |
| ADR-0012 R2 | Not touched | R2 constrains only token packages, and the new file adds no import to any of them. |

Named apart:

- Nothing.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`, which is an HTTP package. |
| ADR-0012 R2 | Not touched | The new file does not import `net/http`, and `internal/http/admin` imports only `encoding/json`. |

Named apart:

- `internal/token/verify/session.go` already imports `example/token-gate/internal/http/auth`. This R1 failure predates the change. The change leaves it as it was, so it is not judged here.
- The golangci-lint result for the depguard rule `token-no-http` is not available. The R1 verdict comes from reading the imports, not from that check.
