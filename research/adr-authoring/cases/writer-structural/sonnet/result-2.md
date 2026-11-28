## Request 1

### File: docs/adr/0012-keep-token-packages-free-of-http-imports.md

````markdown
# Keep the packages under `internal/token/` free of imports of `internal/http/` and `net/http`

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

The service checks the token of each request before policy evaluation. The packages that parse and verify a token sit
under `internal/token/`. The HTTP server, its middleware, and its handlers sit under `internal/http/`.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It has to build without the HTTP
server. The depguard rule `token-no-http` in `.golangci.yml` reports both kinds of import, and CI runs it on every pull
request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory below it. Its test files belong to
  it.
- **HTTP package**: the package `net/http`, and any package whose directory is `internal/http/` or a directory below it.
  Packages below `net/http`, such as `net/http/httptest`, are not HTTP packages (O1).
- **import**: an import declaration in a Go file of a token package. A package that a token package imports is not
  itself covered by this term, so its own imports do not count (O3).

### Rules

#### Imports of the token packages

- **R1** (`token`). No Go file of a token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports an import of an HTTP package. The `golangci-lint`
  step of `.github/workflows/ci.yml` runs it on every pull request.

### Implementation notes

Adds no requirement. Where a token package needs a value that `net/http` or `internal/http/` provides, such as a header
or a status code, define a type for it in the token package. Let `internal/http/` convert between that type and the HTTP
one.

### Justification

`tokencheck` verifies tokens offline and has to build without the HTTP server. A token package that imports an HTTP
package pulls the HTTP stack into that build (R1).

## Consequences

Negative:

- A token package cannot use a type of `net/http`, such as `http.Header`, or a type of `internal/http/`. It takes a type
  of its own, and `internal/http/` converts (R1).

## Open points

- **O1.** Do the packages below `net/http`, such as `net/http/httptest`, count as HTTP packages? Under
  consideration: only `net/http` itself, as R1 is written, or every package below it. @example-architect decides. It
  affects R1.
- **O2.** Does R1 cover the test files of a token package? Under consideration: yes, as R1 is written, or an exemption
  for `_test.go` files. @example-architect decides, after checking what `token-no-http` covers today. It affects R1.
- **O3.** Does R1 cover an HTTP package that a token package reaches through another package? Under consideration: no,
  only direct imports, as R1 is written, or every package on the import graph of a token package. @example-architect
  decides. It affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

## Reading guide

The records in this directory carry numbered rules. A change to code under the paths in the layer table is checked
against the rules of the records that bind it.

### Layers

| Layer | Paths |
| --- | --- |
| `token` | `internal/token/`, with the tests beside the code |
| `http` | `internal/http/`, with the tests beside the code |
| `cmd` | `cmd/token-gate/` |

These paths belong to no layer, because no rule constrains them: `docs/adr/`, `AGENTS.md`, `.github/`,
`.golangci.yml`, `go.mod`, and `go.sum`. A change that adds a file that neither the table nor this list covers extends
one of them.

### Which records bind a change

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not.

### What to read before you change code

Read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each binding record whose rules sit in the
layer you change. Where no rule states a behavior, the choice is yours.

### Trailers

The commit message and the pull request description of every change to code under the paths in the layer table end with
two trailers:

```text
Implements: ADR-NNNN Rn, Rn; ADR-NNNN Rn
Defers: ADR-NNNN Rn to #<issue or pull request number>
```

`Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with an existing issue
or pull request that will bring it. A change that brings no rule and leaves none out carries neither trailer. In a pull
request with several commits, each commit carries the trailers of its own part, and the description carries them for the
whole change.

### Checking a change

The procedure is in <link to "Checking a change" in the adr-authoring skill, at the version this repository pins>.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that the reading guide in `docs/adr/README.md` maps to
  layers. Read that guide before you change such code, and end the commit message and the pull request description with
  the `Implements:` and `Defers:` trailers that it describes.
````

### Message to the user

I wrote ADR-0012 with the status `Proposed` and no Date heading. You didn't say the team accepted it, and it has three open points. Once @example-architect signs off and the points are settled, set `Accepted` and add the Date heading with the acceptance date.

Questions for @example-architect, each of which affects R1:

- **O1:** Should packages below `net/http`, such as `net/http/httptest`, count as HTTP packages? R1 covers only `net/http` itself.
- **O2:** Should R1 cover `_test.go` files? I wrote it as covering them. Please check what `token-no-http` does today.
- **O3:** Should R1 cover indirect imports? It covers direct imports only, which is all depguard sees. A token package that imports a third package which imports `net/http` would still pass, and that could break the offline `tokencheck` build.

I also added the reading guide you agreed to, as `docs/adr/README.md`, plus a paragraph in `AGENTS.md`. The guide commits the team to ending every commit message and pull request description for code under `internal/token/`, `internal/http/`, and `cmd/token-gate/` with `Implements:` and `Defers:` trailers.

Please send me the URL of the `adr-authoring` skill at the version you pin. The guide has a visible placeholder in "Checking a change", and I didn't want to guess a link.

Check that the layer table matches how you think of the code. I put `.golangci.yml`, `go.mod`, `go.sum`, and `.github/` in the no-layer list, because no rule constrains them. If you want a rule that keeps `token-no-http` in place, that needs its own decision.

This change touches no layer, so its commit and pull request carry no trailers. The first change to code under `internal/token/` should end with `Implements: ADR-0012 R1`, once the record is accepted or the team treats it as binding.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

````markdown
# Refuse a token whose header names the algorithm `none` with HTTP 401 and `TOKEN_ALG_NONE`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the packages under `internal/token/` free of imports of `internal/http/` and `net/http`](0012-keep-token-packages-free-of-http-imports.md):
  the import restriction of R1 applies to `internal/token/verify`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation, and the check sits in `internal/token/verify`.
A token whose header names the algorithm `none` declares that it carries no signature, so nothing in it can be
verified. The security review decided how the service answers such a token.

## Decision

We will refuse every token whose header names the algorithm `none` with HTTP 401 and the reason code
`TOKEN_ALG_NONE`, and the check will sit in `internal/token/verify`.

### Terms

- **none token**: a token whose header names its algorithm as the string `none`, in any letter case (O1).

### Rules

#### Refusal of none tokens

- **R1** (`token`, `http`). `internal/token/verify` refuses a none token with the reason code `TOKEN_ALG_NONE`, and the
  HTTP server answers a request that carries a none token with status 401 and that reason code (O2), whatever else is
  wrong with the token (O3).

### Implementation notes

Adds no requirement. The import restriction of ADR-0012 R1 keeps `net/http` out of `internal/token/verify`. Let
`verify` return an error that carries the reason code, and let the code under `internal/http/` map it to the status
401.

### Justification

A none token declares that it is unsigned. If the service accepted it, anyone could create a token that passes
verification (R1).

## Consequences

Negative:

- No setting lets the service accept a none token (R1).

## Open points

- **O1.** Does the algorithm name `none` match in any letter case, so that `None` and `NONE` also count? Under
  consideration: any letter case, as R1 is written, or the exact string `none` only. @example-security-architect
  decides. It affects R1.
- **O2.** How does the response carry the reason code `TOKEN_ALG_NONE`? Under consideration: a field of the response
  body, a response header, or the way the service already reports its other reason codes.
  @example-security-architect decides. It affects R1.
- **O3.** Which reason code wins where a none token also fails another check, such as an expired token or a malformed
  claim? Under consideration: `TOKEN_ALG_NONE` always, as R1 is written, or the first failure in the order of the
  checks. @example-security-architect decides. It affects R1.
````

### Message to the user

I wrote ADR-0013 with the status `Proposed` and no Date heading, because it has three open points. I assumed ADR-0012 has merged under the filename `0012-keep-token-packages-free-of-http-imports.md`. Correct the link under Related ADRs if the filename differs.

Questions for @example-security-architect, each of which affects R1:

- **O1:** Should `None` and `NONE` count as the algorithm `none`? I wrote R1 to match in any letter case.
- **O2:** How does the HTTP response carry `TOKEN_ALG_NONE`? Options are a body field, a header, or whatever the service already does for its other reason codes. I didn't invent one.
- **O3:** Which reason code should win where a none token also fails another check, such as expiry? I wrote R1 so that `TOKEN_ALG_NONE` always wins.

R1 has no entry under Confirmation, because no test covers it yet. I left that section out. Please add a test in `internal/token/verify` for the refusal, and a test under `internal/http/` for the 401 and the reason code. An accepted record takes an addition to Confirmation, so the entry can follow when the tests land.

R1 carries both the `token` and `http` layers. The check sits in `internal/token/verify`, but ADR-0012 R1 keeps `net/http` out of that package. The 401 therefore has to come from `internal/http/`, and the Implementation notes say so.

The first change that brings the refusal should end with `Implements: ADR-0013 R1`. Where the change leaves part of R1 out, name it under `Defers`, with an existing issue or pull request. If no issue exists yet, tell me and I'll draft one for you to open.
