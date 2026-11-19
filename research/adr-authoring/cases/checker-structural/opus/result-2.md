## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/problem.go` adds an import of `example/token-gate/internal/http/problem`, which is an HTTP package. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/problem` imports only `encoding/json`. |

Named apart:

- The golangci-lint result is not available, so the depguard rule `token-no-http` that ADR-0012 names under **Confirmation** settles no case. Both verdicts come from reading the imports in the diff.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |

The check walks no rule. The change touches only the `http` layer, and ADR-0012 has no rule in that layer. `scope.go` imports `example/token-gate/internal/token/verify` and `net/http` from an HTTP package. That changes no import of any token package, so it touches neither ADR-0012 R1 nor R2.

Named apart:

- Nothing.

## Change C

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0012 R1 | Violates | `internal/token/verify/admin.go` adds an import of `example/token-gate/internal/http/admin`, which is an HTTP package. This is a new forbidden import, even though the package already failed R1. |
| ADR-0012 R2 | Not touched | The change adds no import of `net/http`, and `internal/http/admin` imports only `encoding/json`. |

Named apart:

- An older violation of ADR-0012 R1: `internal/token/verify/session.go` already imports `example/token-gate/internal/http/auth`. The change leaves that import as it was, so it is not judged here.
- The golangci-lint result is not available, so the depguard rule `token-no-http` that ADR-0012 names under **Confirmation** settles no case. Both verdicts come from reading the imports in the diff.
