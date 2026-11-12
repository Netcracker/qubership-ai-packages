## Request 1

### File: docs/adr/0012-token-packages-no-http-imports.md

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

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

`internal/token/` holds the packages that parse and verify a token, and `internal/http/` holds the HTTP server, its
middleware, and its handlers. The team plans a command-line tool, `tokencheck`, that verifies tokens offline and is
meant to build without the HTTP server. A Go binary links every package that its packages import, so a token package
that imports the HTTP server or `net/http` brings it into `tokencheck`. The depguard rule `token-no-http` in
`.golangci.yml` already checks both imports, and CI runs it on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of any package under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory below it. Every `.go` file in the
  directory counts, test files included.
- **imports**: a token package imports a package when an import declaration in one of its files names that package. A
  package that a token package reaches only through another package is not imported.
- **HTTP package**: the package `net/http` itself, and any package whose import path is
  `example/token-gate/internal/http` or begins with `example/token-gate/internal/http/`. A subpackage of `net/http`,
  such as `net/http/httptest`, is not an HTTP package.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` fails `golangci-lint run`, which CI runs on every pull
  request, when a package under `internal/token/` imports `net/http` or a package under `internal/http/`.

### Justification

`tokencheck` builds without the HTTP server only if no token package brings it in (R1). The rule ranges over import
declarations, so the linter that CI already runs can check it (R1).

### Alternatives considered

- **A1. Let a token package import `net/http`, and link the HTTP server into `tokencheck`.** Rejected by R1:
  `tokencheck` is meant to build without the HTTP server.

## Consequences

Negative:

- A token package cannot use a type of `net/http`, such as `http.Header`. Code in `internal/http/` has to convert a
  request into values that the token packages define (R1).

## Open points

- **O1.** Do the test files of a token package count? The record assumes they do (**token package**). The architect
  decides. Whether `token-no-http` sees test files depends on the settings in `.golangci.yml`. Affects R1.
- **O2.** Does R1 cover more than direct imports of `net/http` itself? The record assumes it covers direct imports only,
  and that `net/http/httptest` and the other subpackages of `net/http` are allowed (**imports**, **HTTP package**). The
  architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Records `0001-` to `0011-` have no numbered rules, so a check reports them as unchecked. Later records number their
rules (`R1`, `R2`).

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/`, with the tests beside it |
| `http` | HTTP server, middleware, and handlers | `internal/http/`, with the tests beside it |
| `entrypoint` | Entry point of the service | `cmd/token-gate/` |
| `build` | Dependencies, lint settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/ci.yml` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`. A change that adds a file that neither the layers nor
this list cover extends one of them.

## Which records bind

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Writing code under a record

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
binding record that has rules for that layer. Anything that no rule states is your choice.

## Trailers

Every change to code under the paths of a layer ends its commit message and its pull request description with these two
trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-NNNN Rn to #<issue or pull request number>
```

- `Implements` names the rules that the change brings.
- `Defers` names each rule that the change leaves out, with the issue or pull request that will bring it. The target
  has to exist.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description
  carries them for the whole change.

## Checking a change

[Checking a change](<URL of the adr-authoring skill at the pinned version, section "Checking a change">) describes how
a change is checked against these records.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that the guide describes.
````

### Message to the user

I wrote ADR-0012 with the status `Proposed`, because you didn't say the team signed off. Two open points block `Accepted`, and @example-architect decides both:

- **O1:** do the test files under `internal/token/` count? I assumed they do. Whether `token-no-http` sees them depends on the settings in `.golangci.yml`, which I couldn't read.
- **O2:** does the rule cover more than direct imports of `net/http` itself? I assumed it doesn't, so `net/http/httptest` stays allowed.

On acceptance, add a `#### Date` heading with the acceptance date after the status line and set the status to `Accepted`.

The team agreed to a reading guide and trailers, so I added `docs/adr/README.md` and a paragraph in `AGENTS.md`. I kept that process decision out of ADR-0012, which covers the import rule only. If you want the process recorded as a decision, it needs a record of its own.

The guide's link to the skill's "Checking a change" section holds a visible placeholder, because I couldn't look up the URL. What URL and pinned version should it use?

I mapped four layers (`token`, `http`, `entrypoint`, `build`) from the repository layout you gave. Please check that `.golangci.yml` and `.github/workflows/ci.yml` belong under `build`.

This change touches only `docs/adr/` and `AGENTS.md`, so it brings no rule and carries no trailers. A suitable commit subject is `docs(adr): add ADR-0012 on token package imports`.

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

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-no-http-imports.md):
  the import rule R1 applies to `internal/token/verify`, so R2 of this record places the HTTP status in
  `internal/http/`.
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` carries no signature, so a verifier that honors that header accepts a
token that anyone can write. The security review decided that the check against such a token sits in
`internal/token/verify`. The import rule of ADR-0012 R1 applies to that package, so the package cannot set an HTTP
status itself.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, with the check in `internal/token/verify` and the status set in `internal/http/`.

### Rules

#### Refusal of a token with the algorithm `none`

- **R1** (`token`). `internal/token/verify` refuses a token whose header has the value `none` in its `alg` parameter, in
  any letter case, and reports the reason code `TOKEN_ALG_NONE` for it to its caller. This holds also where the token
  fails another check.
- **R2** (`http`). Where `internal/token/verify` reports the reason code `TOKEN_ALG_NONE` for the token of a request,
  the HTTP server answers that request with status 401 and the reason code `TOKEN_ALG_NONE` in
  `<response field that carries the reason code>`.

### Justification

A token with the algorithm `none` has no signature to verify, so the check that refuses it has to sit in the verifier
(R1). The verifier reports a reason code, and the HTTP server turns it into a status, because the verifier cannot
import `net/http` (R2).

### Alternatives considered

- **A1. Compare the `alg` parameter with `none` as an exact, lowercase string.** Rejected by R1: a token that spells the
  value `None` or `NONE` would pass the comparison.
- **A2. Return the HTTP response from `internal/token/verify`.** Rejected by R2, which gives the response to the HTTP
  server. The import rule of ADR-0012 R1 rules it out as well.

## Consequences

Negative:

- A token whose header names `none` gets `TOKEN_ALG_NONE` even where it also fails another check, so the response does
  not report that other failure (R1).

## Open points

- **O1.** Does R1 cover every letter case of `none`? The record assumes it does. The security architect decides.
  Affects R1.
- **O2.** Which reason code wins where a token with the algorithm `none` also fails another check? The record assumes
  `TOKEN_ALG_NONE` wins. The security architect decides. Affects R1.
- **O3.** In which part of the response does the reason code appear, such as a body field or a header? The security
  architect decides, with the maintainers of `internal/http/`. Affects R2.
````

### Message to the user

I wrote ADR-0013 with the status `Proposed`. Three open points block `Accepted`, and @example-security-architect decides all three:

- **O1:** whether `none` is matched in every letter case. I assumed it is.
- **O2:** which reason code wins where the token also fails another check. I assumed `TOKEN_ALG_NONE`.
- **O3:** where the reason code appears in the 401 response. R2 holds the placeholder `<response field that carries the reason code>`, because I didn't invent a field.

I split the decision into two rules. The import rule of ADR-0012 R1 keeps `net/http` out of `internal/token/verify`, so R1 covers the check and the reason code in `verify`, and R2 covers the 401 in `internal/http/`. If the response is built somewhere else, say so and I will change R2's layer.

The record has no **Confirmation**, because no test covers either rule yet. I suggest two tests:

- A `verify` test for a token with `alg` set to `none`, with `None` as a second case.
- An HTTP test that expects 401 with `TOKEN_ALG_NONE`.

When they land, add their names under **Confirmation**. An accepted record allows that edit.

The change that adds the tests carries `Implements: ADR-0013 R1, R2` only if it also brings the code for those rules. Otherwise it carries neither trailer. This change adds only a record, so it carries no trailers. A suitable commit subject is `docs(adr): add ADR-0013 on tokens with alg none`.
