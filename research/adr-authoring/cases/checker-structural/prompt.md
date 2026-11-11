# Task

Check two pull requests against the repository's architecture decision records. Check each one on its own, as if the
other did not exist.

For each pull request, give a heading `## Change A` or `## Change B`, then a Markdown table with one row per rule that
your check walks: the rule as `ADR-NNNN Rn`, its verdict, and one line of reason. After the table, list anything the
report names apart from the verdicts.

The facts below were checked against the code; treat every fact in them as verified, and add none that they do not
carry.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation. Its
  module path is `example/token-gate`.
- `docs/adr/` holds the records. `docs/adr/README.md` is the reading guide: it maps the layer `token` to
  `internal/token/` and the layer `http` to `internal/http/`, lists `docs/adr/`, `.github/`, and `.golangci.yml` as
  belonging to no layer, and says that `Accepted` records bind a change.
- CI runs golangci-lint on every pull request. Its result for these two changes is not available to you.

## The records

### ADR-0012: Keep token verification independent of the HTTP layer

Status: Accepted. Date: 2026-09-30.

Terms:

- **token package**: a Go package whose directory is under `internal/token/`.
- **HTTP package**: a Go package whose directory is under `internal/http/`.

Rules:

- **R1** (`token`). No token package imports an HTTP package.
- **R2** (`token`). No token package imports `net/http`.

Confirmation:

- **R1**, **R2**: the depguard rule `token-no-http` in `.golangci.yml`.

## The changes

Before either change, no token package imports an HTTP package or `net/http`, and `internal/http/middleware` imports
`example/token-gate/internal/token/verify`.

Change A adds `internal/token/verify/problem.go`, which imports `example/token-gate/internal/http/problem` to build an
RFC 9457 problem document for a refused token. `internal/http/problem` imports only `encoding/json`. Nothing else
changes. Its commit message and description carry no trailers.

Change B adds `internal/http/middleware/scope.go`, which imports `example/token-gate/internal/token/verify` and
`net/http` to refuse a request whose token lacks a scope. Nothing else changes. Its commit message and description carry
no trailers.
