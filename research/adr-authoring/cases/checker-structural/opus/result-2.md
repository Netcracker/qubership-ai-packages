## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` adds an import of `example/token-gate/internal/http/problem`, which is an HTTP package. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Not touched: 1 rule (ADR-0012 R2).

Named apart:

- The `token-no-http` depguard rule in `.golangci.yml` is the confirmation check for R1 and R2. Its CI result for this change isn't available, so the R1 verdict comes from reading the diff.
- The change has no trailers, so it claims no rule and defers none.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |

The check walks no rule. The change touches only the `http` layer, and ADR-0012 has no rule tagged `http`. R1 and R2 cover imports made by token packages, and this change adds imports only in `internal/http/middleware`, which is an HTTP package. The imports of `example/token-gate/internal/token/verify` and `net/http` are not relations that either rule forbids.

Named apart:

- The change has no trailers, so it claims no rule and defers none.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` adds an import of `example/token-gate/internal/http/admin`, which is an HTTP package. It's a new forbidden import, even though the package already broke R1. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/admin` imports only `encoding/json`. |

Not touched: 1 rule (ADR-0012 R2).

Named apart:

- The import of `example/token-gate/internal/http/auth` in `internal/token/verify/session.go` already broke ADR-0012 R1 before this change. The change leaves it as it was, so it isn't judged here.
- The `token-no-http` depguard rule in `.golangci.yml` is the confirmation check for R1 and R2. Its CI result for this change isn't available, so the R1 verdict comes from reading the diff.
- The change has no trailers, so it claims no rule and defers none.
