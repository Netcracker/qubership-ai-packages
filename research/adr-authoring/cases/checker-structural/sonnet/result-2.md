## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, an HTTP package. |
| ADR-0012 R2 | Not touched | `problem.go` imports no `net/http`, and `internal/http/problem` imports only `encoding/json`. |

- The depguard rule `token-no-http`, which confirms R1 and R2, has no result available. Both verdicts come from reading the imports.
- The change carries no `Implements` or `Defers` trailers. The facts don't say the guide requires them, so no trailer error is reported.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| None walked | n/a | The change touches only the `http` layer, and no rule of ADR-0012 is tagged `http`. |

- The new import runs from an HTTP package to a token package. R1 and R2 forbid only the opposite direction, so the change alters no outcome of either rule.
- No other binding record is in view.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`, an HTTP package. |
| ADR-0012 R2 | Not touched | `admin.go` imports no `net/http`, and `internal/http/admin` imports only `encoding/json`. |

- `internal/token/verify/session.go` already imported `example/token-gate/internal/http/auth` before this change. The change leaves that import as it was, so it is not judged here. It is a separate R1 failure that predates the change.
- The depguard rule `token-no-http` has no result available. Both verdicts come from reading the imports.
- The change carries no `Implements` or `Defers` trailers. The facts don't say the guide requires them, so no trailer error is reported.
