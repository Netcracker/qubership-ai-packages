## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | `internal/token/verify/problem.go` is in a token package and imports `example/token-gate/internal/http/problem`, an HTTP package. |
| ADR-0012 R2 | Satisfied | The new file imports `internal/http/problem` and no `net/http`. |

- The `token-no-http` depguard result from CI is not available. These verdicts come from the imports.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Not applicable | The new file is in `internal/http/middleware`, an HTTP package, so no token package gains an import. Its import of `internal/token/verify` is not restricted. |
| ADR-0012 R2 | Not applicable | The new file imports `net/http`, but it is not in a token package. |

- The `token-no-http` depguard result from CI is not available. These verdicts come from the imports.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violated | The new `internal/token/verify/admin.go` imports `example/token-gate/internal/http/admin`, an HTTP package. |
| ADR-0012 R2 | Satisfied | The new file imports `internal/http/admin` and no `net/http`. |

- `internal/token/verify/session.go` already imports `example/token-gate/internal/http/auth`, which breaks R1. That violation predates Change C and is not counted against it. The R1 verdict rests on `admin.go` alone.
- The `token-no-http` depguard result from CI is not available. These verdicts come from the imports.
