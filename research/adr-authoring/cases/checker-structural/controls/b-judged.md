## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` is in a token package and imports `example/token-gate/internal/http/problem`, which is an HTTP package. |
| ADR-0012 R2 | Conforms | The new file in the token layer does not import `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Named apart from the verdicts:

- The depguard rule `token-no-http` confirms R1 and R2, but its CI result is not available. Both verdicts come from reading the imports in the diff.
- Trailer errors: none. The commit message and description carry no trailers, so there are no entries to check.
- Guide errors: none. The changed file is under `internal/token/`, which the guide maps to the `token` layer.
- Not touched: no other rule is walked.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Conforms | `internal/http/middleware/scope.go` imports a token package, which R1 allows. |
| ADR-0012 R2 | Conforms | The token packages still import no `net/http`. |

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`. |
| ADR-0012 R2 | Conforms | The new file imports no `net/http`. |
