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

- Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The packages under `internal/token/` parse and
verify a token. The packages under `internal/http/` hold the HTTP server, its middleware, and its handlers.

We plan a command-line tool, `tokencheck`, that verifies tokens offline. It uses the token packages, and it has to
build without the HTTP server.

`.golangci.yml` defines the depguard rule `token-no-http`. `.github/workflows/ci.yml` runs golangci-lint with that
configuration on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it. It includes every `.go`
  file in that directory, `_test.go` files and external test packages included.
- **HTTP server package**: the package `example/token-gate/internal/http`, and every package whose import path starts
  with `example/token-gate/internal/http/`.
- **standard HTTP package**: the package `net/http`, and every package whose import path starts with `net/http/`, such
  as `net/http/httptest`.
- **imports**: a Go file imports a package when one of its import declarations names that package's import path. A
  package that a token package reaches only through another imported package is not imported.

### Rules

#### Imports of the token packages

- **R1** (`token`). No file of a token package imports an HTTP server package.
- **R2** (`token`). No file of a token package imports a standard HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports a file of a token package that imports an HTTP
  server package. golangci-lint runs it in `.github/workflows/ci.yml` on every pull request and fails the job.
- **R2**: the same depguard rule reports a file of a token package that imports a standard HTTP package.

### Implementation notes

Adds no requirement. Let `internal/token/verify` return errors of its own, and let `internal/http` map each error to a
status code and a response. A test that needs an HTTP request or a response recorder belongs in `internal/http`, and
calls the token packages from there. `cmd/tokencheck` imports the token packages and no package under
`internal/http/`.

### Justification

`tokencheck` verifies tokens offline and has to build without the HTTP server. An import of an HTTP server package or
of a standard HTTP package in a token package puts that package into every binary that uses the token packages,
`tokencheck` included (R1, R2). A depguard rule reports the import in the pull request that adds it, before review
(R1, R2).

### Alternatives considered

- **A1. Use the status constants of `net/http`, such as `http.StatusUnauthorized`, in `internal/token/verify`.**
  Rejected by R2: the import makes `tokencheck` depend on `net/http`.

## Consequences

Negative:

- A token package cannot return an HTTP status code or read a token from an `http.Request` or an `http.Header`. The
  mapping from a token error to a response lives in `internal/http` (R1, R2).
- A test in a token package cannot use `net/http/httptest` (R2).

## Open points

- **O1.** Whether R1 and R2 also forbid a token package to import a package that imports an HTTP server package or a
  standard HTTP package, directly or further down. The answers under consideration: direct imports only, as the term
  **imports** states and as `token-no-http` checks; or every package in the dependency graph of a token package, which
  needs a check such as `go list -deps` in CI. @example-architect decides. It affects R1 and R2.
- **O2.** Whether `_test.go` files of a token package fall under R1 and R2. The answers under consideration: they do,
  as the term **token package** states; or they are exempt, so that a test can use `net/http/httptest`.
  @example-architect decides. It affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. A record from `0012-` on states its
requirements as numbered rules, cited outside the record as `ADR-0012 R1`. Records `0001-` to `0011-` have no numbered
rules.

## Layers

Each rule names, in parentheses, the layer of the code it constrains.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | Serves HTTP: the server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Builds the binaries | `cmd/` |
| `build` | Declares the module and the CI checks | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/adr/` and `AGENTS.md`.

A change that adds a file that neither the table nor this list covers adds its path to one of them.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Writing code under a record

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in every
binding record with a rule in that layer. Anything no rule states is your choice.

## Trailers

A change to a file in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-<record> R<rule> to #<issue or pull request>
```

- `Implements` names each rule the change brings, in every case the rule describes.
- `Defers` names each rule the change leaves out or brings only in part, with the issue or pull request that brings
  the rest. The issue or pull request has to exist. Where none exists yet, open an issue first.

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer. In a pull request
with several commits, each commit carries the trailers of its own part, and the description carries them for the whole
change.

## Checking a change

A reviewer checks a change against the rules as
[Checking a change](<URL of the adr-authoring skill at the version this repository pins>#checking-a-change) describes.
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

I've written the record as `docs/adr/0012-token-packages-without-http.md` with the status `Proposed`. It has two rules: R1 forbids imports of `internal/http/` and R2 forbids imports of `net/http`. Both name `token-no-http` as their check.

Two open points block acceptance. @example-architect needs to settle them:

- **O1:** Do the rules cover only direct imports, as depguard checks, or also packages a token package reaches through other imports? The record assumes direct imports only. A `go list -deps` check would be needed for the wider reading.
- **O2:** Do `_test.go` files count? The record assumes they do, which keeps `net/http/httptest` out of the token packages' tests.

Once the architect approves and both points are settled, set the status to `Accepted` and add a `#### Date` heading with the acceptance date before `#### Owner`.

The team agreed to the reading guide, so I've added it as `docs/adr/README.md`. I also added a paragraph to `AGENTS.md` that points to it. From now on, every change to a file in a mapped layer ends with the `Implements:` and `Defers:` trailers. This change only touches `docs/adr/` and `AGENTS.md`, which belong to no layer, so it doesn't need the trailers.

Questions:

1. The guide links to "Checking a change" in the adr-authoring skill. This repository doesn't use APM, so I need the GitHub URL of the skill and the version you want to pin. I've left a visible placeholder in `docs/adr/README.md`; please fill it in before merging.
2. I couldn't see `.golangci.yml`. Can you confirm that `token-no-http` denies `net/http` and `example/token-gate/internal/http` by prefix, so that subpackages like `net/http/httptest` are covered? Can you also confirm it checks `_test.go` files? If it doesn't, the **Confirmation** entries are too broad for those cases.
3. Is the layer map right? I don't know every path in the repository. Any other top-level file, such as a root `README.md` or a `Dockerfile`, needs to be added either to a layer or to the list of paths that belong to no layer.

## Request 2

### File: docs/adr/0013-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  R2 keeps `net/http` out of `internal/token/verify`, so `internal/http` sets the status code that R2 of this record
  requires.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. `internal/token/verify` verifies a token.
`internal/http` holds the HTTP server, its middleware, and its handlers.

The `alg` header parameter of a JSON Web Signature names the algorithm that secures the token. RFC 7518, section 3.6,
defines the value `none` for an unsecured token, which carries no signature. RFC 7515, section 4.1.1, makes the `alg`
value case-sensitive.

ADR-0012 R2 forbids a token package to import `net/http`. The planned command-line tool `tokencheck` verifies tokens
offline with the token packages and without the HTTP server.

## Decision

We will refuse every token whose header names the algorithm `none`, in token verification and in the HTTP response.

### Terms

- **none-algorithm token**: a token whose header parses as a JSON object and whose `alg` member is the string `none`,
  compared case-sensitively.

### Rules

#### Token verification

- **R1** (`token`). `internal/token/verify` returns an error for a none-algorithm token and returns no claims from it.
  This includes a none-algorithm token whose payload or claims are also invalid.

#### HTTP response

- **R2** (`http`). The HTTP server responds to a request that carries a none-algorithm token with HTTP status 401 and
  the reason code `TOKEN_ALG_NONE` in `<reason code field>`. The request does not reach policy evaluation. This
  includes a none-algorithm token whose payload or claims are also invalid.

### Implementation notes

Adds no requirement. Read `alg` from the header before you verify the signature or the claims, and return a sentinel
error from `internal/token/verify` that `internal/http` matches with `errors.Is` and maps to the response in R2. Add a
test for R1 beside `internal/token/verify`, and a test for R2 in `internal/http`. Name both under **Confirmation** in
the change that adds them.

### Justification

A none-algorithm token carries no signature, so any client can write the claims it wants into one (R1, R2). The check
sits in token verification, so every caller of `internal/token/verify` refuses the token, `tokencheck` included (R1).
The HTTP server sets the status code because ADR-0012 R2 keeps `net/http` out of the token packages (R2).

### Alternatives considered

- **A1. Accept a none-algorithm token when no verification key is configured.** Rejected by R1: the token's claims
  would be used with no signature behind them.
- **A2. Refuse a none-algorithm token only in the HTTP middleware.** Rejected by R1: `tokencheck` verifies tokens
  without the HTTP server and would accept the token.

## Consequences

Negative:

- A test or development setup that sends unsigned tokens gets 401, and has to sign its tokens (R2).

## Open points

- **O1.** Which field of the 401 response carries the reason code in R2. The answers under consideration: the field
  that the service's other 401 responses use for their reason code, or a new field. @example-security-architect
  decides. It affects R2.
- **O2.** Whether an `alg` value that differs from `none` only in case, such as `None` or `NONE`, also counts as a
  none-algorithm token. The answers under consideration: no, as the term states, following the case-sensitive
  comparison of RFC 7515; or yes, so that such tokens also get `TOKEN_ALG_NONE`. @example-security-architect decides.
  It affects R1 and R2.
````

### Message to the user

I've written the record as `docs/adr/0013-refuse-alg-none-tokens.md` with the status `Proposed`. It has two rules:

- **R1 (`token`):** `internal/token/verify` returns an error for a token whose `alg` is `none`.
- **R2 (`http`):** the HTTP server answers with 401 and `TOKEN_ALG_NONE`.

I split the requirement this way because ADR-0012 R2 keeps `net/http` out of the token packages, so the token layer can't produce the status code itself. Accepted ADR-0012 stays as it is. The new record links it under **Related ADRs**.

Two open points block acceptance. @example-security-architect needs to settle them:

- **O1:** Which response field carries the reason code? R2 has the visible placeholder `<reason code field>` until this is answered.
- **O2:** Do `None`, `NONE`, and other case variants count as `none`? The record assumes they don't, following the case-sensitive comparison in RFC 7515. Under that assumption, those variants fall outside both rules.

Once the record is approved and both points are settled, set the status to `Accepted` and add a `#### Date` heading with the acceptance date before `#### Owner`.

No test covers either rule yet, so the record has no **Confirmation** section. When tests land, the change that adds them can also add **Confirmation** entries to ADR-0013. An accepted record allows that edit.

This change only touches `docs/adr/`, so it doesn't need the trailers.

Questions:

1. Should I draft an issue for the two missing tests, one in `internal/token/verify` for R1 and one in `internal/http` for R2? With an issue number, a later change that brings only part of the work can name the rest under `Defers:`.
2. Does the service already respond with 401 and `TOKEN_ALG_NONE` today, or does only the check in `internal/token/verify` exist? If the HTTP mapping is missing, the change that adds it carries `Implements: ADR-0013 R2`.
