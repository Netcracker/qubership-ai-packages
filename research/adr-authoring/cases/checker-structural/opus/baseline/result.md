## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | `internal/token/verify/problem.go` imports `example/token-gate/internal/http/problem`, so a token package now imports an HTTP package. |
| ADR-0012 R2 | Satisfied | The change adds no `net/http` import, and before the change no token package imported `net/http`. |

Other points in the report:

- `internal/http/problem` imports only `encoding/json`. R1 is about the direct import, so this doesn't change the R1 verdict.
- The depguard rule `token-no-http` in `.golangci.yml` checks R1 and R2. The CI golangci-lint result for this change isn't available, so both verdicts come from the import facts alone.
- The commit message and the description carry no trailers.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not applicable | The only added file, `internal/http/middleware/scope.go`, is in an HTTP package, and R1 covers token packages only. |
| ADR-0012 R2 | Not applicable | The `net/http` import is in an HTTP package, and R2 covers token packages only. |

Other points in the report:

- The new import of `example/token-gate/internal/token/verify` goes from the `http` layer to the `token` layer. ADR-0012 doesn't restrict that direction, and `internal/http/middleware` already imported that package before the change.
- The CI golangci-lint result for this change isn't available.
- The commit message and the description carry no trailers.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`, so a token package now imports an additional HTTP package. |
| ADR-0012 R2 | Satisfied | The change adds no `net/http` import to a token package. |

Other points in the report:

- `internal/token/verify/session.go` already imported `example/token-gate/internal/http/auth` before this change, which is an older R1 violation. Change C didn't introduce it and doesn't touch it. It also doesn't excuse the new import in `admin.go`.
- `internal/http/admin` imports only `encoding/json`. R1 is about the direct import, so this doesn't change the R1 verdict.
- The depguard rule `token-no-http` in `.golangci.yml` checks R1 and R2. The CI golangci-lint result for this change isn't available, so both verdicts come from the import facts alone.
- The commit message and the description carry no trailers.
