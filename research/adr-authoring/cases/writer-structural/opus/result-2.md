## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

- Architect, @example-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The packages `internal/token/parse` and
`internal/token/verify` parse and verify a token. The packages under `internal/http/` hold the HTTP server, its
middleware, and its handlers. `cmd/token-gate` is the service's entry point.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. A Go binary links every package that
its imports reach. So `tokencheck` builds without the HTTP server only if the token packages it imports do not bring in
the server or `net/http`.

The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the token packages. The workflow
`.github/workflows/ci.yml` runs golangci-lint on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`, so that `tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it, together with the
  `_test.go` files in that directory.
- **HTTP package**: a package whose import path is `net/http`, starts with `net/http/`, is
  `example/token-gate/internal/http`, or starts with `example/token-gate/internal/http/`.
- **imports**: a package imports another package when one of its Go files names that package in an import declaration.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs on every pull request in
  `.github/workflows/ci.yml`.

### Implementation notes

Adds no requirement. Have the token packages return their own errors and result types, and have the middleware under
`internal/http/` map them to HTTP status codes. If a token package needs data that has to be fetched over HTTP, such as
signing keys, the fetching code can sit outside `internal/token/`. It then reaches the token package through an
interface that the token package defines.

### Justification

`tokencheck` has to build without the HTTP server. If a token package imports an HTTP package, the HTTP server or
`net/http` gets linked into every binary that imports that token package (R1). Packages under `net/http/`, such as
`net/http/httptest` and `net/http/httputil`, import `net/http` themselves, so **HTTP package** covers the whole prefix
(R1). The depguard rule checks every pull request and needs no test of its own (R1).

### Alternatives considered

- **A1. Let a token package import `net/http` only for its types and constants, such as `http.Header` or
  `http.StatusUnauthorized`.** Rejected by R1: the import still adds `net/http` and its initialization to every binary
  that imports the token package.

## Consequences

Negative:

- A token package cannot return an HTTP status code or read an `*http.Request`. The mapping from a token error to a
  status code sits in `internal/http/` (R1).
- A test in a token package cannot start a test server with `net/http/httptest` (R1, O2).

## Open points

- **O1.** Does R1 also cover indirect imports? An indirect import is one where a token package imports a package
  outside `internal/http/` and that package imports an HTTP package. Two answers are under consideration. The first is
  direct imports only, which the depguard rule `token-no-http` checks. The second is direct and indirect imports, which
  needs a check of the dependency graph, such as one built on `go list -deps`. R1 and **imports** are written for
  direct imports only. @example-architect decides. Affects R1.
- **O2.** Do the `_test.go` files in a token package count? One answer is yes, which keeps `net/http/httptest` out of
  the token tests. The other is no, because `tokencheck` contains no test file. **token package** is written with the
  test files included. @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. Records from `0012-` on number their
requirements as rules (`R1`, `R2`, and so on), and changes to the code they govern are checked against those rules.

## Records that bind a change

Every record with the status `Accepted` binds a change. Records with the status `Proposed`, `Superseded`, or `Rejected`
do not.

## Layers

Each rule names the layer it constrains, such as `(token)`. A test that sits beside its code belongs to the layer of
that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the binaries | `cmd/` |
| `build` | Module, lint, and CI configuration | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/` and `AGENTS.md`. If a change adds a file that no path in this section covers,
the change also adds the path to a layer or to this list.

## Changing code that a record governs

Before you change code under a path in the table, read these sections of every record that binds the change: **Terms**,
**Rules**, **Confirmation**, and **Implementation notes**. Anything that no rule states is your choice. Where a rule
cites a rule of another record, also read that record's **Related ADRs**. A line there names any later record that
replaces the cited rule.

## Trailers

A change to code under a path in the table ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-NNNN R1, R2
Defers: ADR-NNNN R3 to #<issue>
```

- `Implements` names the rules that the change brings, and claims every case of each one.
- `Defers` names each rule that the change leaves out, or brings only in part, together with the issue or pull request
  that will bring the rest. The target has to be an issue or pull request that exists. If a rule waits for a change
  that has no issue yet, leave it out of the trailers and name it in the pull request description.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- In a pull request with several commits, each commit carries the trailers for its own part, and the description
  carries them for the whole change.
- The trailers may name a rule of a `Proposed` record.

## Checking a change

A reviewer checks a change as described in [Checking a change](<skill-url>#checking-a-change) of the `adr-authoring`
skill.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

## Architecture decision records

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
before you change such code. End the commit message and the pull request description of such a change with the
`Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012 as `Proposed`, along with the reading guide in `docs/adr/README.md` and a paragraph in `AGENTS.md` that points to it, as the team agreed.

**Questions for @example-architect.** These two open points block acceptance:

- **O1:** Does R1 cover only direct imports, which is what depguard checks? Or does it also cover indirect imports through other packages, which would need a dependency-graph check?
- **O2:** Do the `_test.go` files in `internal/token/` count? If they do, the token tests can't use `net/http/httptest`.

I wrote R1 as "direct imports only, test files included." Once the architect answers, I'll set the status to `Accepted` and add the Date heading.

**Things to check:**

- **The depguard rule:** Please confirm that `token-no-http` in `.golangci.yml` matches what **HTTP package** and **token package** cover. That means it should deny `net/http` by prefix, deny `example/token-gate/internal/http`, and apply to test files. If it doesn't, the rule and its check disagree, and either the config or the terms need to change.
- **The guide's link:** The guide has to link to "Checking a change" in the `adr-authoring` skill. The repository doesn't use APM, so the link should point to the skill on GitHub at a pinned version. Which URL and version should I use? The guide has the visible placeholder `<skill-url>` until you tell me.
- **The layer names:** I chose `token`, `http`, `cmd`, and `build`. Rename them if the team prefers other names; no rule uses `cmd` or `build` yet.

This change touches only `docs/` and `AGENTS.md`, so its commit carries no trailers.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose JOSE header names the `none` algorithm with HTTP 401 and `TOKEN_ALG_NONE`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  the import rule of R1, which applies to `internal/token/verify`.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation, and `internal/token/verify` verifies the token.
A JWS whose JOSE header sets `alg` to `none` is an unsecured JWS (RFC 7518, section 3.6), which has no signature. If a
verifier accepts such a token, it accepts claims that anyone can write. RFC 7515 defines `alg` as a case-sensitive
string.

The planned command-line tool `tokencheck` verifies tokens offline with the token packages.

## Decision

We will refuse, in `internal/token/verify`, every token whose JOSE header names the `none` algorithm, and answer the
request that carries it with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **JOSE header**: the header of a token, as RFC 7515 defines it, decoded from the part of the token before the first
  `.`. The term does not cover the HTTP headers of the request.
- **names the `none` algorithm**: a JOSE header names the `none` algorithm when its `alg` parameter is a string equal to
  `none`, compared case-insensitively.
- **refuses**: `internal/token/verify` refuses a token when it returns an error and no verified token.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses a token whose JOSE header names the `none` algorithm, with an error
  that identifies the `none` algorithm as the reason. This also holds when the token fails another check, such as an
  expired `exp`.

#### Response

- **R2** (`http`). A request whose token `internal/token/verify` refuses under R1 gets an HTTP 401 response with the
  reason code `TOKEN_ALG_NONE` in `<location of the reason code>`.

### Implementation notes

Adds no requirement. In `internal/token/verify`, read `alg` from the JOSE header before any other check, and return a
sentinel error such as `ErrAlgNone`. The middleware under `internal/http/` can match that error with `errors.Is` and map
it to the response of R2. Useful tests:

- A table test in `internal/token/verify` with `alg` set to `none` and to `NONE`, one of them with an expired `exp`.
- A middleware test in `internal/http/` that checks the status and the reason code.

### Justification

A token that names the `none` algorithm has no signature, so its claims don't show who issued them (R1). The check sits
in `internal/token/verify` so that every caller of the package refuses such a token, including `tokencheck` (R1). The
import rule of ADR-0012 R1 applies to `internal/token/verify`, so the HTTP response comes from `internal/http/` (R2). A
reason code of its own lets a client and an operator tell this refusal apart from the refusal of an expired or wrongly
signed token (R2).

### Alternatives considered

- **A1. Refuse a token with `alg` set to `none` in the middleware under `internal/http/`.** Rejected by R1: `tokencheck`
  and every other caller of `internal/token/verify` would accept such a token.

## Consequences

Negative:

- A token that names the `none` algorithm and also fails another check, such as an expired `exp`, gets
  `TOKEN_ALG_NONE`. It does not get the reason code of the other check (R1, R2).

## Open points

- **O1.** Where does the response of R2 carry the reason code? Two answers are under consideration: a field of the JSON
  response body, or a parameter of the `WWW-Authenticate` response header. R2 holds the placeholder
  `<location of the reason code>` until this is decided. @example-security-architect decides. Affects R2.
- **O2.** Is `alg` compared with `none` case-insensitively? One answer is case-insensitively, which also refuses `None`
  and `NONE` with `TOKEN_ALG_NONE`. The other is an exact match, as RFC 7515 compares algorithm names. That answer leaves
  `None` to whatever check refuses an unknown algorithm. **names the `none` algorithm** is written case-insensitively.
  @example-security-architect decides. Affects R1 and R2.
- **O3.** Does `TOKEN_ALG_NONE` take precedence over the reason of another check that the token fails? One answer is
  yes, which is how R1 is written. The other is that the first failing check, in the order `internal/token/verify` runs
  them, decides the reason. @example-security-architect decides. Affects R1 and R2.
````

### Message to the user

I added ADR-0013 as `Proposed`. ADR-0012 and the reading guide need no change.

**Questions for @example-security-architect.** These three open points block acceptance:

- **O1:** Where does the 401 response carry `TOKEN_ALG_NONE`: a JSON body field, or a `WWW-Authenticate` parameter? R2 has a placeholder until this is answered.
- **O2:** Should `None` and `NONE` also count as `none`? R1 assumes they do.
- **O3:** Does `TOKEN_ALG_NONE` win when the token also fails another check, such as an expired `exp`? R1 assumes it does.

**Tests:** Since no test covers the check yet, the record has no **Confirmation** section. I propose this issue:

- Type: Task
- Title: "Test the refusal of tokens whose JOSE header names the `none` algorithm (ADR-0013 R1, R2)"
- Body: a table test in `internal/token/verify` and a middleware test in `internal/http/` that checks the status and the reason code.

Once the tests merge, add them to **Confirmation**. An accepted record allows that edit.

**Questions for you:**

- Does the code already return an error from `internal/token/verify` that the middleware can tell apart? And does the middleware already send 401 with `TOKEN_ALG_NONE`? If either is missing, the change that adds it should end with `Implements: ADR-0013 R1, R2`, or name the missing rule under `Defers` with an existing issue.
- Should I open the test issue?

This record's own change touches only `docs/adr/`, so it carries no trailers.
