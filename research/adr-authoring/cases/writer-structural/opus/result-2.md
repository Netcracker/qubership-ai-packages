## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of `internal/http` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The packages under `internal/token/`, `internal/token/parse` and `internal/token/verify`, parse and verify the token of
each request. The packages under `internal/http/` hold the HTTP server, its middleware, and its handlers. The standard
library package `net/http` holds an HTTP client and an HTTP server.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It uses the token packages, and it has
to build without the HTTP server.

The depguard rule `token-no-http` in `.golangci.yml` reports an import of `internal/http` or `net/http` in the token
packages. `.github/workflows/ci.yml` runs golangci-lint with `.golangci.yml` on every pull request.

## Decision

We will keep every token package free of imports of the service's HTTP packages and of `net/http`.

### Terms

- **token package**: a Go package whose source files sit in `internal/token/` or in a directory below it. The test
  files of the package and its external test package, named with the suffix `_test`, are included.
- **HTTP package**: `net/http`, a package whose import path starts with `net/http/`, the package
  `example/token-gate/internal/http`, and a package whose import path starts with `example/token-gate/internal/http/`.
- **imports**: a Go file imports a package when the package's path appears in the file's `import` declarations.

### Rules

#### Imports of the token packages

- **R1** (`token`). No Go file in a token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in `.github/workflows/ci.yml`
  on every pull request.

### Implementation notes

Adds no requirement. Where a token package needs to report why it refused a token, return an error value that the
token package defines, and let the handler or the middleware in `internal/http` map that error to a status code.
`tokencheck` belongs under `cmd/tokencheck` and imports the token packages, not `internal/http`.

### Justification

`tokencheck` builds the token packages, and it can build without the HTTP server only if no token package imports one
(R1). `net/http` holds the server beside the client, so an import of `net/http` for the client alone still builds the
server package into `tokencheck` (R1).

### Alternatives considered

- **A1. Import `net/http` in a token package for its client only, such as to fetch verification keys.** Rejected by
  R1: `net/http` is one package, and the import builds its server into `tokencheck` as well.

## Consequences

Negative:

- A token package cannot fetch keys or other data over HTTP. Code that does so sits outside `internal/token/` and
  passes the result to the token packages (R1).

## Open points

- **O1.** R1 covers the test files of a token package, so a test cannot use `net/http/httptest`. The other answer is
  that R1 covers only the files that `go build` compiles, since `tokencheck` builds no test file. @example-architect
  decides. Affects R1.
- **O2.** R1 covers direct imports only, as depguard checks them. The other answer is that a token package also must
  not depend on an HTTP package through another package it imports, which a depguard rule does not check.
  @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory decide how `example/token-gate` is built. From `0012-` on, records state their
requirements as numbered rules, and a change to the code they govern is checked against those rules. Records `0001-` to
`0011-` have no numbered rules.

## Layers

Each rule names the layer it constrains, such as `(token)`. A test file beside its code belongs to the layer of that
code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies tokens | `internal/token/` |
| `http` | Serves HTTP: the server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Holds the entry points of the programs | `cmd/` |
| `build` | Holds the module, lint, and CI configuration | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`.

A change that adds a file outside every path in this section also adds the file's path to a layer or to the list of
paths that belong to no layer.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Writing code under a record

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
record that binds the change and has a rule in that layer. Anything no rule states is your choice.

## Trailers

A change to a file in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-<NNNN> R<n> to #<issue>
```

`Implements` names each rule that the change brings in full. `Defers` names each rule that the change leaves out or
brings only in part, with the issue or the pull request that will bring the rest. That issue or pull request exists
before the change names it. A rule that waits for a change with no issue yet stays out of the trailers, and the pull
request description names it.

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer. In a pull request with
several commits, each commit carries the trailers for its own part, and the description carries them for the whole
change.

## Checking a change

A reviewer checks a change against the rules as
[Checking a change](<link to the "Checking a change" section of the adr-authoring skill at a pinned version>) describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers it describes.
````

### Message to the user

I wrote the decision as `docs/adr/0012-token-packages-without-http.md`. It has one rule: no file in `internal/token/` or below imports `internal/http` or `net/http`, and that includes subpackages such as `net/http/httptest`. The rule's check is the depguard rule `token-no-http`.

The record stays `Proposed`. Two open points block acceptance, and @example-architect has to settle both:

- **O1:** Should R1 also apply to test files? I assumed it does, which matches depguard's default of checking every file. Can you confirm that `token-no-http` doesn't exclude `_test.go` files?
- **O2:** Should R1 stop at direct imports, or also forbid reaching an HTTP package through a third-party dependency? Depguard only sees direct imports.

The meeting notes didn't name any alternatives. I added one myself, A1: importing `net/http` only for its client. Please confirm it, or tell me to remove it.

Since the team agreed to keep a reading guide and to use the trailers, I added `docs/adr/README.md` and a bullet in `AGENTS.md` that points to it. The guide maps `go.mod`, `go.sum`, `.golangci.yml`, and `.github/` to a `build` layer. That means changes to those files also carry the trailers whenever they bring or defer a rule.

I need one more thing from you. The guide has to link to the "Checking a change" section of the adr-authoring skill, and the repository doesn't use APM or pin a version of the skill. Which URL and version should the link use? Until then the guide has a visible placeholder.

This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer, so its own commit needs no trailers.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. A token's header names the algorithm of its
signature in the `alg` parameter. The value `none` marks a token that carries no signature, so anyone can write one.
The security review asked the service to refuse such a token with its own reason code.

`internal/token/verify` holds the check of the `alg` parameter. No test covers the check or the response.

## Decision

We will refuse a token whose header names the algorithm `none`, with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **`alg` of a token**: the value of the `alg` parameter in the header of the token.
- **refuses**: for `internal/token/verify`, returns a non-nil error for the token and no verified token.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses a token whose `alg` is `none` in any letter case, and the error it
  returns for that token differs from the error for every other cause of a refusal.

#### Response

- **R2** (`http`). A request whose token `internal/token/verify` refuses under R1 gets the status 401 and the reason
  code `TOKEN_ALG_NONE` in `<field that carries the reason code>`.

### Implementation notes

Adds no requirement. Define a sentinel error in `internal/token/verify`, such as `ErrAlgNone`, and return it before the
signature check. In `internal/http`, match it with `errors.Is` and write the response of R2. A table test in
`internal/token/verify` with `none`, `None`, and `NONE` confirms R1. A test of the middleware or handler that sends such
a token confirms R2.

### Justification

A token whose `alg` is `none` carries no signature, so accepting it would let any client forge a token (R1). Attacks
that send `alg: none` also try other letter cases, such as `None` and `NONE` (R1). A reason code of its own lets
operators find forged tokens in the logs and in client reports, apart from expired or badly signed ones (R1, R2). The
verifier reports the cause, and the HTTP layer chooses the status, so each rule sits in the layer that produces its
result (R1, R2).

### Alternatives considered

- **A1. Refuse a token whose `alg` is `none` with the reason code that other verification failures get.** Rejected by
  R2: the security review asked for a reason code of its own.

## Consequences

Negative:

- A client that sends tokens whose `alg` is `none`, such as a test harness, gets 401 for every request (R2).

## Open points

- **O1.** Which field of the 401 response carries the reason code: a field in the response body, a response header, or
  the field that other refusals of the service already use. @example-security-architect decides. Affects R2.
- **O2.** R1 refuses `none` in any letter case. The other answer is to refuse only the exact value `none`, which is the
  value the JWA registry defines, and to let the signature check refuse the other spellings. @example-security-architect
  decides. Affects R1.
````

### Message to the user

I wrote the decision as `docs/adr/0013-refuse-alg-none.md`, with two rules:

- **R1** (layer `token`): the refusal itself, in `internal/token/verify`.
- **R2** (layer `http`): the 401 and the reason code, which `internal/http` writes.

The record stays `Proposed` until @example-security-architect settles two open points:

- **O1:** Where does the reason code go in the 401 response? For example, a field in the response body, a header, or wherever the service already puts reason codes for other refusals. R2 has a visible placeholder until then.
- **O2:** Should R1 refuse `none` in any letter case, as I assumed, or only the exact lowercase value?

No test covers R1 or R2 yet, so the record has no **Confirmation** section. I suggest an issue:

- Type: Task
- Title: "Add tests for ADR-0013 R1 and R2"
- Scope: a table test in `internal/token/verify` with `none`, `None`, and `NONE`, plus a test in `internal/http` that checks the 401 and `TOKEN_ALG_NONE`.

Once those tests land, add them to **Confirmation**. An accepted record allows that edit.

This change touches only `docs/adr/`, so its commit needs no trailers.
