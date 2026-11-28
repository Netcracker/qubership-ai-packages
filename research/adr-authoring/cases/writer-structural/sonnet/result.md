## Request 1

### File: docs/adr/0012-token-packages-free-of-http.md

````markdown
# Keep the `internal/token` packages free of imports of `internal/http` and `net/http`

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

The packages under `internal/token/` parse and verify a token. The HTTP server, its middleware, and its handlers live
under `internal/http/`. The planned command-line tool `tokencheck` verifies tokens offline and has to build without the
HTTP server. The depguard rule `token-no-http` in `.golangci.yml` checks both imports, and CI already runs it.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory beneath it, such as
  `internal/token/parse` and `internal/token/verify`.
- **imports**: a package imports another package when an import declaration in one of its Go files, a test file
  included, names the import path of the other package. A package that a third package imports on its behalf is not
  imported.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports `net/http`, or a package whose import path is
  `example/token-gate/internal/http` or begins with `example/token-gate/internal/http/`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which `golangci-lint run` applies to every pull request
  through `.github/workflows/ci.yml`. The rule checks both import paths of R1.

### Justification

`tokencheck` has to build without the HTTP server, so no package it uses may import the server or the standard HTTP
package (R1).

### Alternatives considered

- **A1. Let a token package import `internal/http` or `net/http`, and have `tokencheck` build with the HTTP server.**
  Rejected by R1: `tokencheck` has to build without the HTTP server.

## Consequences

Negative:

- A token package cannot use a type or constant of `net/http`, such as `http.StatusUnauthorized`. Code under
  `internal/http/` has to map the results of the token packages to HTTP (R1).

## Open points

- **O1.** Does R1 cover a package that a token package imports from `net/http/...`, such as `net/http/httptest`, and
  does it cover test files? R1 is written on the assumption that test files are covered and that only the exact path
  `net/http` is. The architect, @example-architect, decides, and the answer changes the scope of R1.
````

### File: docs/adr/README.md

````markdown
# Reading guide for the architecture records

The records in this directory govern the code under the paths in **Layers**. Read this guide before you change that
code, and read the records that apply to it.

## Layers

A rule of a record names its layer in parentheses, such as (`token`). A test beside its code belongs to the layer of
that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |
| `http` | HTTP server, middleware, and handlers | `internal/http/` |
| `entrypoint` | The service's entry point | `cmd/token-gate/` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `.github/`, `.golangci.yml`, `go.mod`, and `go.sum`. A change
that adds a file covered by neither the table nor this list extends one of them.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
binds nothing.

## What to read when you write code

In each record that governs your change, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes**.
Where no rule states a requirement, the choice is yours.

## Trailers

Every change to code under the paths in **Layers** ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R2 to #123
```

- `Implements` names the rules the change brings, each as `ADR-NNNN Rn`.
- `Defers` names each rule that the change leaves out, with the existing issue or pull request that will bring it.

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.

## Checking a change

The procedure for checking a change against the rules is **Checking a change** in the `adr-authoring` skill:
<URL of the adr-authoring skill at the version this repository pins>.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code. End the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that the guide describes.
````

### Message to the user

I wrote ADR-0012 with the status `Proposed`. The request names @example-architect as approver but doesn't say they have signed off. When they do, set `Accepted` and add a `#### Date` heading after the status. Set it to the acceptance date and place it inside the markdownlint comments, as in `0011-`.

The rule is a single rule, R1. It covers both forbidden imports because one depguard check confirms them and they share one reason. The Justification and alternative A1 come from your note that `tokencheck` has to build without the HTTP server. Please confirm that A1 matches what the meeting rejected.

I added `docs/adr/README.md` as the reading guide and a paragraph in `AGENTS.md`. The meeting agreed to the guide and the trailers, so I didn't ask first. The guide commits every change to code under the mapped paths to end its commit message and PR description with `Implements:` and `Defers:`. This change touches no mapped code, so it needs no trailers.

Questions:

1. What is the URL of the `adr-authoring` skill at the version you pin? The guide has a visible placeholder for it, and the repository doesn't use APM.
2. Does `token-no-http` cover test files and subpackages of `net/http`, such as `net/http/httptest`? I couldn't see `.golangci.yml`. R1 assumes it covers test files and only the exact path `net/http`, and O1 records that assumption.
3. Should a rule require `token-no-http` to stay in `.golangci.yml`? Today the guide lists `.golangci.yml` as belonging to no layer, so a change that removes the depguard rule would not be walked against R1.

## Request 2

### File: docs/adr/0013-refuse-none-algorithm-tokens.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the `internal/token` packages free of imports of `internal/http` and `net/http`](0012-token-packages-free-of-http.md): the import limits of the packages under `internal/token/`, which decide how `internal/token/verify` reports the refusal (Implementation notes).
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` declares that it carries no signature. The security review decided that
the service refuses such a token. The check sits in `internal/token/verify`. No test covers it yet.

## Decision

We will refuse every request whose token header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`.

### Terms

- **none algorithm**: the value `none` in the algorithm field of a token header, compared ignoring case.
- **refused**: a request is refused with a status and a reason code when the HTTP server answers it with that status and
  carries the reason code in the response. A package under `internal/token/` takes part by returning an error that
  carries the reason code.

### Rules

#### Tokens with the none algorithm

- **R1** (`token`, `http`). A request whose token header names the none algorithm is refused with HTTP status 401 and the
  reason code `TOKEN_ALG_NONE`, carried in <location of the reason code in the response>. The check that detects the
  none algorithm sits in `internal/token/verify`.

### Implementation notes

Adds no requirement. `internal/token/verify` cannot import `net/http` (ADR-0012 R1), so it returns an error that
carries the reason code `TOKEN_ALG_NONE`. The code under `internal/http/` maps that error to status 401 and writes the
reason code into the response.

### Justification

A token that names the none algorithm carries no signature, so the verifier cannot show who issued it (R1).

### Alternatives considered

- **A1. Accept a token whose header names the none algorithm as an unsigned token.** Rejected by R1: the service
  refuses every such token.

## Consequences

Negative:

- A client or a test fixture that sends an unsigned token receives status 401 (R1).

## Open points

- **O1.** Where does the response carry the reason code `TOKEN_ALG_NONE`: a header, a field of the body, or both? The
  security architect, @example-security-architect, decides. The answer fills the placeholder in R1.
- **O2.** Does R1 cover the spellings `None` and `NONE`? R1 is written on the assumption that it does, as the
  definition of the none algorithm says. The security architect decides, and the answer changes the extent of the term.
- **O3.** Which reason code does a request receive when its token names the none algorithm and also fails another check,
  such as a malformed payload? The answers under consideration are `TOKEN_ALG_NONE` and the code of the other check. The
  security architect decides, and the answer affects R1.
````

### Message to the user

I wrote ADR-0013 with the status `Proposed`, because @example-security-architect hasn't approved it yet. On acceptance, add the `#### Date` heading as in `0011-`. Three open points block acceptance:

- **O1:** The request doesn't say where the response carries `TOKEN_ALG_NONE`, such as a header or the body. R1 has a visible placeholder for it, and I didn't invent a value.
- **O2:** I assumed the match on `none` ignores case, so `None` and `NONE` are refused too. Please confirm.
- **O3:** The request doesn't say which reason code wins when a token names `none` and also fails another check.

The rule has layers `token` and `http`, because `internal/token/verify` can't import `net/http` under ADR-0012 R1. So `verify` returns an error that carries the reason code, and `internal/http` maps it to status 401. The Implementation notes say so, and Related ADRs links ADR-0012 for that reason. The Justification and alternative A1 are my inference from the request, so please check them.

The record has no **Confirmation** section, because no test covers the rule yet. I suggest opening an issue of type Task titled "Test the refusal of tokens with algorithm `none` (`TOKEN_ALG_NONE`, 401)". It would add a `verify` test and a handler test for the 401 response and the reason code. The change that brings those tests can then carry `Implements: ADR-0013 R1` and give R1 a **Confirmation** entry. Please send me the issue number once it exists, because I won't guess one.

This change adds only a record, so it carries no trailers.
