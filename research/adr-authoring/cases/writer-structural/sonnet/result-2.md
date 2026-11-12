## Request 1

### File: docs/adr/0012-token-packages-without-http-imports.md

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

`internal/token/parse` and `internal/token/verify` parse and verify the token of each request. `internal/http/` holds
the HTTP server, its middleware, and its handlers. The planned command-line tool `tokencheck` will verify tokens
offline and has to build without the HTTP server.

The depguard rule `token-no-http` in `.golangci.yml` checks imports of `internal/http/` and of `net/http` from the
packages under `internal/token/`. CI runs golangci-lint with `.golangci.yml` on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`, so that `tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`.
- **server package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **imports**: a package imports another package when one of its Go source files, a `_test.go` file included, names the
  other package in an import declaration. An import of the other package through a third package does not count.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports a server package.
- **R2** (`token`). No token package imports the package `net/http`.

### Confirmation

- **R1**, **R2**: the depguard rule `token-no-http` in `.golangci.yml` reports an import of a server package or of
  `net/http` from a token package. golangci-lint runs it in CI on every pull request, and the run fails on a report.

### Implementation notes

Adds no requirement. A token package that needs an HTTP concept, such as a status code, defines its own type. The code
under `internal/http/` maps that type to the HTTP value.

### Justification

`tokencheck` verifies tokens with the token packages and has to build without the HTTP server. A token package that
imports a server package would pull the server into that build (R1), and one that imports `net/http` would pull in the
standard HTTP package (R2).

### Alternatives considered

- **A1. Let a token package import a server package or `net/http`, and build `tokencheck` together with the HTTP
  server.** Rejected by R1 and R2: `tokencheck` has to build without the HTTP server.

## Consequences

Negative:

- A token package cannot use a type or constant from `net/http`, such as `http.Header` or a status code. The code under
  `internal/http/` converts at the boundary (R2).

## Open points

- **O1.** Do R1 and R2 cover imports in `_test.go` files? The rules assume that they do. The alternative is to exempt
  test files. @example-architect decides. It affects R1 and R2 through the term **imports**.
- **O2.** Do R1 and R2 cover an import through a third package, such as a token package that imports a package that
  imports `net/http`? The rules assume that they do not, because `token-no-http` names direct imports. The alternative is
  to forbid the transitive import, which needs a check beyond `token-no-http`. @example-architect decides. It affects R1
  and R2 through the term **imports**.
- **O3.** Does R2 cover the subpackages of `net/http`, such as `net/http/httptest` and `net/http/httputil`? The rule
  assumes that it covers only `net/http` itself. The alternative is to forbid every package below it. @example-architect
  decides. It affects R2.
````

### File: docs/adr/README.md

````markdown
# Decision records

The records in this directory state numbered rules. A change to code under the paths below is checked against the rules
of the records that bind it.

## Layers

Each rule names the layer of the code it constrains.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying tokens | `internal/token/` and everything below it, tests included |
| `http` | HTTP server, middleware, and handlers | `internal/http/` and everything below it, tests included |
| `entrypoint` | Service start | `cmd/token-gate/` |

These paths belong to no layer: `docs/adr/`, `.github/`, `.golangci.yml`, `go.mod`, `go.sum`, and `AGENTS.md`. A path
stays in no layer only while no rule constrains it. A change that adds a file covered by neither the layers nor this
list extends one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read before you change code

In each record that governs the code, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes**.
Anything that no rule states is your choice. Where a rule cites a rule of another record, read the **Related ADRs** of
that record too: a line there names any later record that replaces the cited rule.

## Trailers

The commit message and the pull request description of every change to code under the paths of the layers end with two
trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to <issue or pull request>
```

- `Implements` lists the rules the change brings.
- `Defers` lists each rule the change leaves out, with the existing issue or pull request that will bring it.
- A change that brings no rule and leaves none out, such as a refactoring that keeps every rule met, carries neither
  trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

[Checking a change](<URL of the adr-authoring skill at the pinned version>#checking-a-change) describes how a reviewer or
an agent reaches a verdict on each rule.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern code under the paths that `docs/adr/README.md` maps to layers. Read that guide before
  you change such code, and end the commit message and the pull request description with its `Implements:` and
  `Defers:` trailers.
````

### Message to the user

I wrote ADR-0012 with two structural rules: R1 forbids imports of `internal/http/` from `internal/token/`, and R2 forbids imports of `net/http`. I also added the reading guide at `docs/adr/README.md` and a bullet in `AGENTS.md` that points to it. Your request already agrees to the trailer commitment, so I did not ask about it.

Questions:

1. What is the URL of the `adr-authoring` skill at the version you pin? The guide has no APM-deployed copy to link to, so its "Checking a change" link holds the visible placeholder `<URL of the adr-authoring skill at the pinned version>`. Please fill it in before the merge.
2. @example-architect, do you accept the assumptions in O1 to O3? They are:
   - O1: test files are covered.
   - O2: only direct imports count.
   - O3: R2 covers `net/http` itself, not `net/http/httptest` or other subpackages.

Things to know:

- The status is `Proposed` and the Date heading is left out, because the architect has not yet approved and O1 to O3 are open. Once they are settled and approved, set the status to `Accepted` and add the `#### Date` heading with that date.
- I could not read `.golangci.yml`. The Confirmation entry rests on your statement that `token-no-http` checks both imports and that CI runs it. Please check whether it covers test files (O1) and subpackages (O3).
- The guide maps `internal/token/`, `internal/http/`, and `cmd/token-gate/` to layers. `tokencheck` has no path yet, so map it when it is added.
- `.golangci.yml`, `go.mod`, and `go.sum` are in no layer, because neither rule constrains them.
- This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer, so its commit and pull request description need no trailers.

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

Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http-imports.md):
  the `net/http` import rule (R2) governs how `internal/token/verify` reports a refusal.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. A token whose header names the algorithm `none`
claims that no signature protects it. The decision comes from a security review.

## Decision

We will refuse every token whose header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, and `internal/token/verify` will make the check.

### Terms

- **none token**: a token whose header field `alg` has the value `none`, compared without regard to letter case. See O1.
- **refuse**: the service sends HTTP status 401 and a reason code in the response to the request that carries the
  token. A package below the server, such as `internal/token/verify`, meets a rule that requires a refusal by returning
  an error that carries the reason code. See O2.

### Rules

#### The none algorithm

- **R1** (`token`, `http`). The service refuses a none token with the reason code `TOKEN_ALG_NONE`, and the check that
  finds a none token sits in `internal/token/verify`.

### Implementation notes

Adds no requirement. `internal/token/verify` returns an error that carries `TOKEN_ALG_NONE`, and the middleware under
`internal/http/` maps that error to status 401. The `net/http` import rule of ADR-0012 R2 keeps the status constants of
`net/http` out of `internal/token/verify`.

### Justification

A none token states that no signature protects it, so accepting it would let any sender forge a token (R1). Comparing
`alg` without regard to letter case closes the spellings `None` and `NONE` (R1).

### Alternatives considered

- **A1. Accept a none token and leave the decision to policy evaluation.** Rejected by R1: the token check refuses the
  token before policy evaluation.

## Consequences

Negative:

- A token whose `alg` is spelled `None` or `NONE` is refused too (R1).

## Open points

- **O1.** Is `alg` compared without regard to letter case? The record assumes that it is. The alternative is to refuse
  only the exact value `none`. @example-security-architect decides. It affects R1 through the term **none token**.
- **O2.** Where does the response carry the reason code: a field of the response body, a response header, or another
  place, and under which name? @example-security-architect decides. It affects R1 through the term **refuse**.
- **O3.** Which reason code wins where a none token also fails another check of `internal/token/verify`, such as a
  malformed header or an expired token? The answers are `TOKEN_ALG_NONE` in every case, or the code of whichever check
  runs first. @example-security-architect decides. It affects R1.
````

### Message to the user

I wrote ADR-0013 with one rule, R1, tagged `token` and `http`. The `token` tag covers the check in `internal/token/verify`, and the `http` tag covers the 401 response. ADR-0012 R2 keeps `net/http` out of `internal/token/verify`, so I defined "refuse" so that `verify` returns an error carrying `TOKEN_ALG_NONE` and the HTTP layer sends the 401. ADR-0012 appears under Related ADRs for that reason. The record does not edit ADR-0012.

Questions for @example-security-architect (the three open points):

- O1: do you want `alg` compared without regard to letter case? I assumed yes.
- O2: where does the response carry the reason code (body field, header, or other), and under which name?
- O3: which code wins when a none token also fails another check?

Things to know:

- The status is `Proposed` because O1 to O3 are open. Set it to `Accepted` with a Date heading once they are settled and approved.
- I could not see the code. If the check in `verify` compares `alg` exactly, it does not meet R1 under the case-insensitive assumption.
- No test covers R1, so the record has no Confirmation section. Please open an issue, for example type Task, titled "Test that a token with alg none is refused with 401 and TOKEN_ALG_NONE". The change that adds the test can then add a Confirmation entry for R1, which an accepted record allows.
- This change touches only `docs/adr/`, so its commit and pull request description need no trailers.
