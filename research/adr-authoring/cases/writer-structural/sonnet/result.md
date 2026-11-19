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

`internal/token/` holds the packages that parse and verify a token, and `internal/http/` holds the HTTP server, its
middleware, and its handlers. The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It has to
build without the HTTP server, so the packages it uses must not bring the server code or `net/http` with them.

## Decision

We will keep every package under `internal/token/` free of imports of `internal/http` and of `net/http`, so that
`tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it. The test files of a
  token package are part of it.
- **server code**: the package with the import path `example/token-gate/internal/http` and every package whose import
  path begins with `example/token-gate/internal/http/`.
- **imports**: a Go file contains an import declaration of the package. The imports of the imported package are not
  followed (O2).

### Rules

#### Imports of the token packages

- **R1** (`token`). No Go file of a token package, a test file included, imports server code.
- **R2** (`token`). No Go file of a token package, a test file included, imports `net/http` (O1).

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which `golangci-lint` runs in `.github/workflows/ci.yml`
  on every pull request.
- **R2**: the same depguard rule.

### Implementation notes

Adds no requirement. Where a token package needs a value that arrives in an HTTP request, such as the token string, a
package under `internal/http/` reads it from the request and passes it in as a plain Go value.

### Justification

`tokencheck` builds without the HTTP server only if no token package imports the server code (R1) or `net/http` (R2).

## Consequences

Negative:

- A token package cannot use a `net/http` type, such as `http.Header` or `*http.Request`, in its API or its tests (R2).
  Code under `internal/http/` converts such values before it calls a token package.

## Open points

- **O1.** Does R2 also cover the packages below `net/http`, such as `net/http/httptest` and `net/http/httputil`? The
  answers under consideration are the import path `net/http` only, and every import path that begins with `net/http`.
  @example-architect decides. This affects R2.
- **O2.** Does the ban cover imports that a token package reaches through another package, for example through an
  internal package that imports `net/http`? The answers under consideration are direct imports only, and the whole
  import graph of each token package. @example-architect decides. This affects R1 and R2.
- **O3.** The rules assume that the test files of a token package are bound like its other files, because a test that
  imports `net/http` would also put it into a build of the package. @example-architect confirms or corrects this. This
  affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Reading guide for the architecture decision records

The records in this directory govern the code of the repository. Records 0012 and later number their rules (`R1`,
`R2`, ...) and name a layer for each rule. Records 0001 to 0011 have no numbered rules, so a check lists them as
unchecked.

## Layers

Each rule names the layer whose code it constrains. A test file beside its code belongs to the layer of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |
| `http` | HTTP server, middleware, and handlers | `internal/http/` |
| `entrypoint` | The service's entry point | `cmd/token-gate/` |

These paths belong to no layer, because no rule constrains them: `docs/adr/`, `AGENTS.md`, `go.mod`, `go.sum`,
`.golangci.yml`, and `.github/`. A change that adds a file covered neither by a layer nor by this list extends one of
them.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
binds nothing.

## What to read before you change code

Read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each binding record that has a rule in
a layer your change touches. Anything that no rule states is your choice.

## Trailers

Every change to code under the paths of a layer ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to <issue or pull request>
```

- `Implements` names the rules the change brings.
- `Defers` names each rule the change leaves out, with the existing issue or pull request that will bring it.

A change that brings no rule and leaves none out, such as a refactoring that keeps every rule met, carries neither
trailer. In a pull request with several commits, each commit carries the trailers of its own part, and the description
carries them for the whole change.

## Checking a change

The procedure is **Checking a change** in the `adr-authoring` skill, at <URL of the pinned version of the skill, to be
filled in before the merge>.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code. End the commit message and the pull request description of the change with the
  `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012 as `Proposed`, with no Date heading. Three open points block acceptance, and @example-architect decides each:

- **O1:** Does R2 also cover `net/http/httptest` and `net/http/httputil`, or only the path `net/http`? I can't see the `token-no-http` configuration, so I haven't assumed what it matches.
- **O2:** Does the ban cover indirect imports? The rules and Confirmation cover direct imports only, which is what depguard checks. `tokencheck` would also pull in `net/http` through an intermediate package.
- **O3:** I assumed test files in `internal/token/` are covered. Please confirm.

Your request agreed to the reading guide and the trailers, so I added `docs/adr/README.md` and a paragraph in `AGENTS.md`.

The guide needs the URL of the `adr-authoring` skill at the version you pin. I left a visible placeholder, so please give me the URL or fill it in before the merge.

The guide maps three layers: `token`, `http`, and `entrypoint`. `.golangci.yml`, `.github/`, and `go.mod` belong to no layer, because no rule constrains them. A change that weakens `token-no-http` therefore touches no layer. If you want that guarded, say so and I'll propose a rule.

I haven't seen the code. If a package under `internal/token/` already imports `internal/http` or `net/http`, that is a departure from this decision. I'd open a Bug issue for it: "Remove HTTP imports from `internal/token/`", citing ADR-0012 R1 and R2.

This change touches only docs and `AGENTS.md`, which are in no layer, so it carries no trailers.

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

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http-imports.md):
  R2 keeps `net/http` out of `internal/token/verify`, so R1 states the refusal as a reason code and R2 states the HTTP
  status.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. A token whose header names the algorithm `none`
declares that it carries no signature. The security review found that such a token must not pass the check.

## Decision

We will refuse a token whose header names the algorithm `none`. The check sits in `internal/token/verify`, and the
request is answered with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **none algorithm**: the header field `alg` has the value `none` in any letter case (O1).
- **refuses**: `internal/token/verify` returns an error that carries a reason code, and returns no verified token.

### Rules

#### Refusal of the none algorithm

- **R1** (`token`). `internal/token/verify` refuses a token whose header names the none algorithm, with the reason code
  `TOKEN_ALG_NONE`, whatever the rest of the token contains (O2).
- **R2** (`http`). The server answers a request with HTTP 401 and the reason code `TOKEN_ALG_NONE` in
  `<location of the reason code in the response>` where `internal/token/verify` refuses the token of the request under
  R1 (O3).

### Implementation notes

Adds no requirement. `internal/token/verify` cannot import `net/http` (ADR-0012 R2), so it returns an error that
carries the reason code, and the middleware under `internal/http/` maps that error to the status 401.

### Justification

A token without a signature proves nothing about who sent it, and the check runs before policy evaluation, so the
refusal has to happen in verification (R1). A distinct reason code lets a client and a log query tell this refusal from
other 401 answers (R1, R2).

## Consequences

Negative:

- A client that sends a token with the algorithm `none` gets 401 for every such request (R2). No setting turns the
  refusal off.

## Open points

- **O1.** The record assumes that the algorithm sits in the header field `alg` and that `none` matches in any letter
  case, so that `None` and `NONE` are refused too. @example-security-architect confirms or names the field and the
  matching. This affects R1.
- **O2.** When a token names the none algorithm and also fails another check, such as expiry or a malformed payload,
  does `TOKEN_ALG_NONE` win or does the other reason code? @example-security-architect decides. This affects R1.
- **O3.** Where does the response carry the reason code, such as a body field or a header, and under which name?
  @example-security-architect decides. This affects R2.
````

### Message to the user

I added ADR-0013 as `Proposed`, with no Date heading. Three open points block acceptance, and @example-security-architect decides each:

- **O1:** I assumed the header field is `alg` and that `none` matches in any letter case, so `None` and `NONE` are refused too. Please confirm.
- **O2:** If a token names `none` and also fails another check, which reason code wins?
- **O3:** Where does the response carry the reason code, such as a body field or a header, and under which name? R2 holds a visible placeholder until you answer.

I split the decision into two rules. ADR-0012 R2, once accepted, bars `net/http` from `internal/token/verify`, so that package can only return the reason code. R1 covers the refusal in `verify`, and R2 covers the 401 answer in the HTTP layer. If the 401 is already produced elsewhere, tell me and I'll adjust the layer tag.

No test covers either rule, so the record has no **Confirmation** section. When a test lands, add its entry to the record. The pull request that adds the test and the code carries `Implements: ADR-0013 R1, R2`, or names a rule it leaves out under `Defers`, with an existing issue as the target. I can draft the test cases if you want them.

The guide and `AGENTS.md` need no change. ADR-0012 stays as it is, since this record adds a decision rather than replacing one. I'll add the link back from ADR-0012 when ADR-0013 is accepted.
