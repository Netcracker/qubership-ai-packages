# Task

Two requests follow, in one repository. Answer each under a heading `## Request 1` or `## Request 2`, as if the other
did not exist, except that Request 2 comes after Request 1 has merged.

Under each request, give every file you would create or change as a heading `### File: <path>`, followed by the file's
full content in a fence of four backticks. Then give a heading `### Message to the user` with what you would tell the
user. Ask nothing and wait for nothing: where you would ask the user something, write the question in that message.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation. Its
  module path is `example/token-gate`.
- `internal/token/` holds the packages that parse and verify a token: `internal/token/parse` and
  `internal/token/verify`, each with its tests beside it. `internal/http/` holds the HTTP server, its middleware, and
  its handlers. `cmd/token-gate` is the service's entry point, and `go.mod` and `go.sum` sit at the root.
- `.github/workflows/ci.yml` runs `go test ./...` and golangci-lint, with the settings in `.golangci.yml`, on every pull
  request.
- `docs/adr/` holds eleven accepted records, `0001-` to `0011-`, and no `README.md`. They follow one template, shown
  below with `0011-` as the example. None of them has terms or numbered rules.
- `AGENTS.md` at the repository root is written by hand, and the repository does not use APM. Its content is below.

### `docs/adr/0011-structured-logs.md`

````markdown
# Write logs as JSON lines

## Status

Accepted

<!-- markdownlint-disable MD001 -->
#### Date

2026-08-14

#### Owner

@example-platform-lead

#### Participants and approvers

Platform team

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The log pipeline parses JSON, and a plain-text line reaches it as one unparsed message.

## Decision

We will write every log record as one JSON object per line, with the fields `time`, `level`, and `msg`.

### Justification

The pipeline parses JSON lines without a parser of its own for this service.

## Consequences

Plain-text logs from versions before 1.4 are not parsed.
````

### `AGENTS.md`

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
````

## Request 1

Record this decision, from the architecture meeting:

- Packages under `internal/token/` must not import anything under `internal/http/`, and must not import `net/http`.
  The command-line tool we plan, `tokencheck`, will verify tokens offline and has to build without the HTTP server.
- The depguard rule `token-no-http` in `.golangci.yml` checks both, and CI already runs it.
- The architect, @example-architect, owns the record and approves it.
- The team agreed to keep a reading guide for the records from now on, and to end every change to the code the records
  govern with `Implements:` and `Defers:` trailers.

## Request 2

Record this decision, from the security review:

- A token whose header names the algorithm `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. The
  check sits in `internal/token/verify`.
- @example-security-architect owns the record and approves it.
- No test covers it yet.
