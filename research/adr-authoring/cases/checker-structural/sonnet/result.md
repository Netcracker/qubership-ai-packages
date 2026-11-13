## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, an HTTP package. |
| ADR-0012 R2 | Not touched | The new file imports no `net/http`, and `internal/http/problem` imports only `encoding/json`. |

- Not touched: 1 rule (ADR-0012 R2).
- The result of the `token-no-http` depguard check is not available, so the R1 verdict comes from reading the imports.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| none | n/a | The change touches only the `http` layer, and both rules of ADR-0012 sit in the `token` layer. |

- Not touched: 2 rules (ADR-0012 R1, R2). `scope.go` is an HTTP package importing a token package, which neither rule forbids.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` adds an import of `example/token-gate/internal/http/admin`, an HTTP package. |
| ADR-0012 R2 | Not touched | The new file imports no `net/http`, and `internal/http/admin` imports only `encoding/json`. |

- Not touched: 1 rule (ADR-0012 R2).
- Named apart: `internal/token/verify/session.go` already imports `example/token-gate/internal/http/auth`, which breaks R1. This case failed before the change, the change leaves it as it was, and it is not judged here.
- The result of the `token-no-http` depguard check is not available, so the R1 verdict comes from reading the imports.
