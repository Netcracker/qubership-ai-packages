## Request 1

### File: docs/adr/0012-token-packages-free-of-http-imports.md

````markdown
# Keep packages under `internal/token/` free of imports of `internal/http/` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1 and decides O1 and O2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The packages that parse and verify a token live
under `internal/token/`. The HTTP server, its middleware, and its handlers live under `internal/http/`.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline and has to build without the HTTP server.
It can import the token packages only if they bring neither the HTTP server nor `net/http` with them.

The depguard rule `token-no-http` in `.golangci.yml` already reports both imports, and CI runs it.

## Decision

We will keep every package under `internal/token/` free of imports of `internal/http/` and of `net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token` or a directory beneath it, such as
  `internal/token/parse` and `internal/token/verify`. The test files in that directory belong to the package.
- **HTTP package**: a Go package whose import path is `net/http` or `example/token-gate/internal/http`, or lies beneath
  either path. O1 asks whether the extent beneath `net/http` is right.
- **imports**: a Go file imports a package when an import declaration in that file names the package's import path. A
  package that the file reaches only through another package is not imported by it. O2 asks whether that extent is
  right.

### Rules

#### Imports of the token packages

- **R1** (`token`). No Go file in a token package, `_test.go` files included, imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports an import of `internal/http/` or `net/http`, and
  the golangci-lint step that CI runs on every pull request fails on the report.

### Implementation notes

Adds no requirement. Where a token package needs a concept that the HTTP layer also uses, such as a refusal reason,
define the type in the token package and let `internal/http` map it to its own representation.

### Justification

`tokencheck` has to build without the HTTP server. A package that imports `internal/http/` brings the server into that
build, and a package that imports `net/http` brings in the HTTP stack that the server runs on (R1).

### Alternatives considered

- **A1. Forbid only imports of `internal/http/` and allow `net/http` in the token packages.** Rejected by R1: `net/http`
  still puts the HTTP stack into the `tokencheck` build.

## Consequences

Negative:

- A token package cannot use a `net/http` identifier, such as `http.StatusUnauthorized`, and has to define its own (R1).

## Open points

- **O1.** Does R1 reach `_test.go` files and the packages beneath `net/http`, such as `net/http/httptest`? R1 assumes
  that it reaches both. The answers under consideration are: both, as R1 reads; non-test files only; `net/http` itself
  only, with its subpackages allowed. @example-architect decides. The answer affects R1 and the matching in the
  `token-no-http` rule.
- **O2.** Does R1 reach a package that a token package imports only through another package? R1 assumes that it does
  not, because depguard reports only the imports a file declares. The answers under consideration are: declared imports
  only, as R1 reads; transitive imports as well, which needs a check other than depguard. @example-architect decides.
  The answer affects R1.
````

### File: docs/adr/README.md

````markdown
# Reading guide for the records

The records in this directory govern the code under the paths in the table below. A change to that code ends its commit
message and its pull request description with the trailers described under **Trailers**.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/`, with the tests beside the code |
| `http` | HTTP server, middleware, and handlers | `internal/http/`, with the tests beside the code |
| `entrypoint` | The service's entry point | `cmd/token-gate/` |
| `build` | Dependencies, lint, and CI configuration | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/ci.yml` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`. A change that adds a file that neither a layer nor this
list covers extends one of them.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not. Records 0001 to 0011 have no
numbered rules, so a trailer cannot name them.

## What to read

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
binding record whose rules name that layer. Where no rule states a requirement, the choice is yours.

## Trailers

End the commit message and the pull request description of every change to code in a layer with two trailers. They name
the rules the change brings and, for each rule it leaves out, the change that will bring it:

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R2 to #208
```

- Cite a rule with its record, as `ADR-0012 R1`.
- A `Defers` target is an issue or a pull request that exists.
- `Implements` claims every case of a rule. A change that brings only some cases of a rule names it under `Defers`.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- A rule of a `Proposed` record may appear in the trailers.

## Checking a change

[Checking a change in the adr-authoring skill](<URL of the adr-authoring skill at the version this repository pins>)
describes how a reviewer gives a verdict on each rule.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change that code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers it describes.
````

### Message to the user

I wrote ADR-0012 with status `Proposed`, because two open points are unanswered. Both are for @example-architect:

- **O1:** does R1 also cover `_test.go` files and subpackages of `net/http`, such as `net/http/httptest`? I assumed it does.
- **O2:** does R1 cover imports that arrive only through another package? I assumed it does not, because depguard reports only the imports a file declares.

I could not read `.golangci.yml`. I took "the `token-no-http` rule checks both" from your notes. Please check whether its matching agrees with O1. When the record is accepted, add the `Date` heading with the acceptance date.

Because the team agreed to keep a reading guide, I added `docs/adr/README.md` and a bullet in `AGENTS.md` that points to it. The layer map in the guide is my reading of the repository layout. In particular, I put `go.mod`, `go.sum`, `.golangci.yml`, and the CI workflow into one `build` layer. Please correct it if the layers should be cut differently.

Two questions:

1. **Skill link.** The link to "Checking a change" in the guide is a visible placeholder. Which URL and pinned version of the `adr-authoring` skill should it point to? The repository does not use APM, so there is no committed copy to link.
2. **Where `tokencheck` will live.** Which path will it have? Its files need a layer in the guide, or a new one.

This change adds no code, so its commit and pull request description carry no `Implements:` or `Defers:` trailers.

## Request 2

### File: docs/adr/0013-refuse-tokens-naming-alg-none.md

````markdown
# Refuse a token whose header names the algorithm `none` with HTTP 401 and `TOKEN_ALG_NONE`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1 and R2 and decides O1 and O2.

#### Related ADRs

- [ADR-0012: Keep packages under `internal/token/` free of imports of `internal/http/` and `net/http`](0012-token-packages-free-of-http-imports.md):
  R1 keeps `net/http` out of `internal/token/verify`, so R1 here returns an error and R2 here maps it to the status.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The header of a token names the algorithm that
signed it. A header that names the algorithm `none` declares that the token carries no signature.

The security review decided that such a token is refused. The check sits in `internal/token/verify`. No test covers it
yet.

## Decision

We will refuse every token whose header names the algorithm `none`. `internal/token/verify` returns the reason code
`TOKEN_ALG_NONE` for it, and the HTTP server answers the request with HTTP 401 and that reason code.

### Terms

- **header algorithm**: the value of the `alg` field in the header of a token. O2 asks which spellings of `none` count.

### Rules

#### The check in the verify package

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE`, and no
  verified token, for a token whose header algorithm is `none`, whatever else the token contains.

#### The HTTP response

- **R2** (`http`). The HTTP server responds with status 401 to a request whose token `internal/token/verify` rejected
  with the reason code `TOKEN_ALG_NONE` (R1), and the response carries that reason code in
  `<where a response carries its reason code>`.

### Implementation notes

Adds no requirement. `internal/token/verify` can expose the reason code through a sentinel error or an error type that
the HTTP layer reads with `errors.Is` or `errors.As`, so that the token package needs no HTTP type (ADR-0012 R1).

### Justification

A token whose header names `none` carries no signature, so no claim in it is backed by one (R1). The status code belongs
to the HTTP server, because ADR-0012 R1 keeps `net/http` out of `internal/token/verify` (R2).

### Alternatives considered

- **A1. Write the HTTP 401 response from `internal/token/verify`.** Rejected by ADR-0012 R1: the package would have to
  import `net/http`.

## Consequences

Negative:

- No test covers R1 or R2 yet, so a change to `internal/token/verify` or to the HTTP server can break either rule
  without failing CI.

Follow-ups:

- Add a test in `internal/token/verify` for R1 and a test in `internal/http` for R2, then add their names under
  **Confirmation**.

## Open points

- **O1.** Where does an HTTP response carry its reason code, such as a body field or a header? R2 needs the value. The
  answers under consideration are the convention that the service's other error responses already use, or a new field.
  @example-security-architect decides. The answer affects R2.
- **O2.** Which spellings of the header algorithm does R1 refuse? R1 assumes only the exact value `none`. The answers
  under consideration are the exact value, as R1 reads, and every case variant, such as `None` and `NONE`.
  @example-security-architect decides. The answer affects R1.
````

### Message to the user

I wrote ADR-0013 with status `Proposed`, because two open points are unanswered. Both are for @example-security-architect:

- **O1:** where does an HTTP response carry its reason code, such as a body field or a header? R2 holds the visible placeholder `<where a response carries its reason code>`, because your notes do not say. If the service's other 401 responses already carry one, tell me where and I will fill it in.
- **O2:** does R1 refuse only the exact value `none`, or case variants such as `None` and `NONE` as well? I wrote the exact value because your notes name only `none`. I recommend refusing every case variant. Libraries have historically accepted `None` and `NONE`, and an exact match would let those through this check.

I split the decision into two rules because of ADR-0012 R1. `internal/token/verify` cannot import `net/http`, so R1 makes it return an error that carries `TOKEN_ALG_NONE`. R2 puts the HTTP 401 in the HTTP server. If you wanted the status code produced inside `verify`, that conflicts with ADR-0012 R1, and that record would need a superseding one.

The record has no **Confirmation** section, because no test covers either rule yet. I listed the two tests as a follow-up. Do you want me to write them? I could not read `internal/token/verify`, so the record states the decision and does not confirm that the code already behaves this way.

ADR-0012 stays as it is, and this record only cites it. This change adds no code, so its commit and pull request description carry no trailers.
