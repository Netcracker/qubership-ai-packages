## Request 1

### File: docs/adr/0012-keep-token-packages-free-of-http-imports.md

````markdown
# Keep the token packages free of imports of HTTP packages

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
`internal/token/verify` parse and verify a token. `internal/http/` holds the HTTP server, its middleware, and its
handlers. The standard library package `net/http` holds an HTTP server and an HTTP client.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It is built from the token packages and
has to build without the HTTP server.

`.golangci.yml` defines the depguard rule `token-no-http`. `.github/workflows/ci.yml` runs golangci-lint with that file
on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of `net/http` and of the packages under
`internal/http/`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or any directory under it, at any depth, with all
  of its `.go` files, including its `_test.go` files (O1).
- **HTTP package**: `net/http`; every standard library package whose import path starts with `net/http/`, such as
  `net/http/httptest`; and every package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **imports**: a Go file imports a package when one of its import declarations names that package. A package that a
  file reaches only through another package that it imports is not imported by that file (O2).

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: golangci-lint runs the depguard rule `token-no-http` in `.golangci.yml` in `.github/workflows/ci.yml` on every
  pull request. The rule reports an import of `net/http`, or of a package under `internal/http/`, in a package under
  `internal/token/`.

### Implementation notes

Adds no requirement. Where a token package needs to report a failure that the HTTP server turns into a status code,
return an error value or a result type that the token package defines. Then let a handler or the middleware in
`internal/http/` map it to the status code.

### Justification

`tokencheck` verifies tokens offline and is built from the token packages. It builds without the HTTP server only if no
token package imports `net/http` or the server, middleware, and handlers in `internal/http/` (R1).

### Alternatives considered

- **A1. Import `net/http` in a token package only for its constants, such as `http.StatusUnauthorized`.** Rejected by
  R1: the import still builds `net/http` into `tokencheck`.

## Consequences

Negative:

- A token package cannot fetch keys over HTTP itself, because the HTTP client is in `net/http` too (R1). Code that
  fetches keys sits outside `internal/token/`.
- Under the answer to O1 that this record assumes, a test of a token package cannot start a test server with
  `net/http/httptest` (R1).

## Open points

- **O1.** Does R1 cover the `_test.go` files of a token package? This record assumes that it does, as the term **token
  package** states, so no test under `internal/token/` imports `net/http/httptest`. The other answer limits R1 to the
  files that `go build` compiles, because tests are not built into `tokencheck`. @example-architect decides. This
  affects R1.
- **O2.** Does R1 cover an import made through a package outside `internal/token/` and `internal/http/`, such as a token
  package that imports a package that imports `net/http`? This record assumes that it does not, as the term **imports**
  states, and depguard checks direct imports only. The other answer forbids such a chain too, and needs a check beyond
  depguard, such as a test that reads the output of `go list -deps` for each token package. @example-architect decides.
  This affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. Records from `0012-` on state their
requirements as numbered rules, cited as `ADR-0012 R1`.

## Layers

Each rule names the layer it constrains in parentheses, such as `(token)`. A test beside its code belongs to the layer
of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the programs | `cmd/` |
| `build` | The Go module, the linter settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/`, `AGENTS.md`, and the Markdown files at the repository root. A change that adds
a file under none of these paths adds its path to a layer or to this list.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read before you change code

In each record that governs the code you change, read **Terms**, **Rules**, **Confirmation**, and **Implementation
notes**. Anything that no rule states is your choice.

## Trailers

Every change to a file under a layer's paths ends its commit message and its pull request description with two
trailers. `Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with the
existing issue or pull request that will bring it:

```text
Implements: ADR-0012 R1
Defers: ADR-0013 R2 to #42
```

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer. In a pull request with
several commits, each commit carries the trailers of its own part, and the description carries them for the whole
change.

## Checking a change

A change is checked against the rules as
[Checking a change in the adr-authoring skill](<URL of the adr-authoring SKILL.md at a pinned version>#checking-a-change)
describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

The architecture decision records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to
layers. Read that guide before you change such code. End the commit message and the pull request description of such a
change with the `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012 with one rule: R1 says no package under `internal/token/` imports `net/http`, a package under `net/http/`, or a package under `internal/http/`. Its Confirmation names the depguard rule `token-no-http`.

I also added the reading guide in `docs/adr/README.md` and a paragraph in `AGENTS.md` that points to it. From now on, every change to code under the mapped paths has to end its commit message and pull request description with the `Implements:` and `Defers:` trailers, as the team agreed. This change only touches `docs/adr/` and `AGENTS.md`, which belong to no layer, so it carries no trailers. Suggested commit subject: `docs(adr): add ADR-0012 and a reading guide for the records`.

ADR-0012 stays `Proposed` because two open points block acceptance. @example-architect needs to answer them:

1. **O1:** Should R1 also cover `_test.go` files? I assumed yes, which keeps `net/http/httptest` out of the token packages' tests.
2. **O2:** Should R1 also forbid an indirect import through another package? I assumed no, because depguard only checks direct imports.

Once both are settled and @example-architect signs off, the record gets the status `Accepted` and a Date heading.

Questions:

- **Skill link:** The repository doesn't use APM, so no copy of the adr-authoring skill gets deployed into it. Which URL and pinned version should the guide link to for "Checking a change"? For now the link is a placeholder.
- **Depguard coverage:** Does `token-no-http` match `net/http` and `example/token-gate/internal/http` by prefix, so it also catches subpackages like `net/http/httptest`? If it doesn't, R1 covers more than the lint check does.

Records 0001 to 0011 have no numbered rules. They still bind changes, but a check reports them as unchecked.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-alg-none.md

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

- [ADR-0012: Keep the token packages free of imports of HTTP packages](0012-keep-token-packages-free-of-http-imports.md):
  its R1, on the imports of the token packages, is the reason the HTTP status is set outside `internal/token/verify`.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. `internal/token/verify` verifies a token, and the
HTTP server in `internal/http/` answers the request. The command-line tool `tokencheck` is planned to verify tokens
offline through the token packages, without the HTTP server.

A token's header names its signature algorithm in the `alg` parameter. RFC 7518, section 3.6, defines the value `none`
for an Unsecured JWS, which carries no signature. A verifier that accepts such a token accepts a token that anyone can
write.

## Decision

We will refuse every token whose header names the algorithm `none`. `internal/token/verify` refuses it with the reason
code `TOKEN_ALG_NONE`, and the HTTP server answers the request with HTTP status 401.

### Terms

- **alg-none token**: a token whose header has an `alg` parameter with the value `none` in any letter case, such as
  `none`, `None`, or `NONE` (O1).

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses every alg-none token: it returns an error that carries the reason
  code `TOKEN_ALG_NONE`, and it returns no verified token. Where an alg-none token also fails another check, the reason
  code is still `TOKEN_ALG_NONE` (O3).

#### The HTTP answer

- **R2** (`http`). When `internal/token/verify` refuses the token of a request with the reason code `TOKEN_ALG_NONE`,
  the HTTP server answers the request with HTTP status 401 and with `TOKEN_ALG_NONE` in
  `<response field for the reason code>` (O2).

### Implementation notes

Adds no requirement. Export the refusal from `internal/token/verify` as an error value, such as `verify.ErrAlgNone`.
Read `alg` before you look up a key or check the signature. In `internal/http/`, match the error with `errors.Is` and
write the 401 answer.

A table test in `internal/token/verify` can cover `none`, `None`, and `NONE`. A handler test in `internal/http/` that
uses `net/http/httptest` can cover the 401 answer and its reason code. When these tests land, add them under
**Confirmation**.

### Justification

An alg-none token carries no signature, so a verifier that accepts it lets anyone write a token that passes (R1). The
check sits in `internal/token/verify`, so `tokencheck` and every other program that verifies tokens through that package
refuses alg-none tokens too (R1).

The term covers every letter case, so `NONE` cannot pass where `none` is refused (R1). One reason code for every
alg-none token lets a client and the logs name the cause without depending on the order of the other checks (R1).

The import rule of ADR-0012 R1 keeps `net/http` out of `internal/token/verify`, so the HTTP server sets the status (R2).
Status 401 tells the client that its credentials were not accepted, and the reason code tells it why (R2).

### Alternatives considered

- **A1. Refuse alg-none tokens only in the HTTP middleware in `internal/http/`.** Rejected by R1: `tokencheck`, which
  verifies tokens without the HTTP server, would accept them.

## Consequences

Positive:

- `tokencheck` refuses alg-none tokens with the same reason code as the service (R1).

Negative:

- A test setup or a client that sends unsigned tokens to token-gate gets status 401 (R2), and `tokencheck` refuses
  those tokens (R1).

## Open points

- **O1.** Does an `alg` value of `none` in another letter case, such as `None` or `NONE`, make an alg-none token? This
  record assumes that it does. The other answer limits the term to the exact value `none`, which RFC 7518 registers.
  @example-security-architect decides. This affects R1, and R2 through it.
- **O2.** Which part of the 401 answer carries the reason code: a field of the JSON body, such as `reason`, a response
  header, or the `error` parameter of `WWW-Authenticate`? R2 holds a placeholder until this is settled.
  @example-security-architect decides. This affects R2.
- **O3.** When an alg-none token also fails another check, such as an expired token, which reason code does
  `internal/token/verify` return? This record assumes `TOKEN_ALG_NONE`. The other answer lets the first failed check
  decide the reason code. @example-security-architect decides. This affects R1.
````

### Message to the user

I added ADR-0013 with two rules:

- **R1 (`token`):** `internal/token/verify` refuses every alg-none token with the reason code `TOKEN_ALG_NONE`.
- **R2 (`http`):** the HTTP server answers such a request with status 401 and the reason code.

They're two rules because ADR-0012 R1 keeps `net/http` out of the token packages, so the 401 has to be set in `internal/http/`. This change only touches `docs/adr/`, so it carries no trailers.

The record stays `Proposed` until @example-security-architect answers three open points:

1. **O1:** Does `alg` match `none` in any letter case, such as `None` or `NONE`? I assumed yes.
2. **O2:** Which part of the 401 response carries the reason code? R2 has a placeholder, `<response field for the reason code>`, until this is answered. If the service already has a convention for reason codes, tell me what it is and I'll fill it in.
3. **O3:** If an alg-none token fails another check too, which reason code wins? I assumed `TOKEN_ALG_NONE`.

No test covers the check yet, so the record has no Confirmation section. Do you want to open an issue for the tests, for example "Test the refusal of alg-none tokens in `internal/token/verify` and `internal/http`"? Once the record is accepted, the change that adds those tests can add them under Confirmation. That is an allowed edit to an accepted record.

If the answer to O1 is "any letter case" and the current code only matches `none` exactly, the code doesn't fully meet R1. The change that fixes it names `ADR-0013 R1` under `Implements:`.
