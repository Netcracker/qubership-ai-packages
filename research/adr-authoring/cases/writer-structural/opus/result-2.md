## Request 1

### File: docs/adr/0012-keep-token-packages-free-of-http-imports.md

````markdown
# Keep the token packages free of imports of `net/http` and of the HTTP server

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

The service checks the token of each request before policy evaluation. `internal/token/parse` and
`internal/token/verify` parse and verify a token. `internal/http` holds the HTTP server, its middleware, and its
handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It uses the packages under
`internal/token/`, and it has to build without the HTTP server.

`.golangci.yml` holds the depguard rule `token-no-http`. It reports an import of `net/http` or of a package under
`internal/http/` from a package under `internal/token/`. `.github/workflows/ci.yml` runs golangci-lint with that file on
every pull request.

## Decision

We will keep the packages under `internal/token/` free of imports of `net/http` and of the packages under
`internal/http/`.

### Terms

- **token code**: the `.go` files in `internal/token/` and in every directory below it, `_test.go` files included.
- **HTTP package**: a Go package whose import path is `net/http`, starts with `net/http/`, is
  `example/token-gate/internal/http`, or starts with `example/token-gate/internal/http/`.
- **imports**: a file imports a package when one of the file's import declarations names that package. The packages
  that the named package imports in turn are outside this extent.

### Rules

#### Imports of the token code

- **R1** (`token`). No file of token code imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs from
  `.github/workflows/ci.yml` on every pull request, reports a file of token code that imports `net/http` or a package
  under `internal/http/`.

### Implementation notes

Adds no requirement. Where token code has to report why a token failed, return an error type from `internal/token` that
carries the reason, and let `internal/http` map that reason to a status code. `tokencheck` can then use
`internal/token/parse` and `internal/token/verify` without building the HTTP server.

### Justification

`tokencheck` verifies tokens offline and is built from the token code. An import of an HTTP package from token code
would put the HTTP server, or `net/http`, into the build of `tokencheck` (R1). The depguard rule reports such an import
on the pull request that adds it, before it merges (R1).

### Alternatives considered

- **A1. Import `net/http` in token code only for its status constants, such as `http.StatusUnauthorized`.** Rejected by
  R1: the import puts `net/http` into the build of `tokencheck`.

## Consequences

Negative:

- Token code cannot fetch keys or other data over HTTP itself. That code has to live outside `internal/token/` and pass
  its result in (R1).
- A token error that needs an HTTP status needs a mapping in `internal/http` (R1).

## Open points

- **O1.** Does R1 cover `_test.go` files? The record assumes it does, in **token code**. The answers under
  consideration: keep test files in the extent, or leave them out, because tests do not go into the `tokencheck`
  binary. @example-architect decides. Affects R1.
- **O2.** Does R1 cover a package that token code reaches through another package, such as a third-party library that
  imports `net/http`? The record assumes it does not, in **imports**, because depguard checks only the import
  declarations of a file. The answers under consideration: direct imports only, or every package in the build of the
  token code, which needs a check other than depguard, such as one built on `go list -deps`. @example-architect
  decides. Affects R1.
- **O3.** Do the standard library packages under `net/http/`, such as `net/http/httptest`, count as HTTP packages? The
  record assumes they do, in **HTTP package**. The answers under consideration: `net/http` alone, or `net/http` and
  every package under it. @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code under the paths that this guide maps to a layer. Read the records that
govern a path before you change code there.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the binaries | `cmd/` |
| `build` | The Go module, the lint settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/`, `AGENTS.md`.

A test beside its code belongs to the layer of that code. A change that adds a file that neither the table nor the list
covers adds the file to one of them in the same change.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
does not.

## What to read in a record

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of every
binding record with a rule tagged with that layer. Anything that no rule states is your choice.

## Trailers

Every change to code under a path that the table maps to a layer ends its commit message and its pull request
description with two trailers:

```text
Implements: ADR-<NNNN> R<n>, R<n>
Defers: ADR-<NNNN> R<n> to #<issue or pull request>
```

`Implements` names the rules the change brings, each with every case. `Defers` names each rule the change leaves out,
or brings only in part, with the existing issue or pull request that brings the rest. A rule of a `Proposed` record may
appear in either trailer. A change that brings no rule and leaves none out, such as a refactoring, carries neither
trailer.

## Checking a change

A change is checked against the records as
[Checking a change in the adr-authoring skill](<URL of adr-authoring SKILL.md at the pinned version>#checking-a-change)
describes.
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

I added ADR-0012 as `Proposed`, the reading guide at `docs/adr/README.md`, and a bullet in `AGENTS.md` that points agents to the guide and the trailers. This change only touches `docs/` and `AGENTS.md`, which belong to no layer, so it doesn't need trailers.

**What blocks acceptance:** the record has three open points, and @example-architect decides each one:

- **O1:** does R1 cover `_test.go` files? The draft assumes yes.
- **O2:** does R1 cover only direct imports, or every package in the build? The draft assumes direct imports only, because that is what depguard checks.
- **O3:** do packages under `net/http/` such as `httptest` count? The draft assumes yes.

Once they're settled and approved, set the status to `Accepted` and add a `#### Date` heading after the status.

**Questions:**

1. **Guide link:** the repository doesn't use APM, so the guide has to link to the adr-authoring skill on GitHub at a pinned version. What is the URL and the version? Until you tell me, the guide has a placeholder there.
2. **depguard settings:** I haven't seen `.golangci.yml`. Does `token-no-http` match packages under `net/http/` and check test files? If not, the Confirmation entry only covers some cases of R1, depending on how O1 and O3 are answered.
3. **Unmapped paths:** I only know of the paths listed in the repository facts. Which other files at the root (for example `README.md`, `.gitignore`, `Makefile`) should go in a layer or in the no-layer list?
4. **Older records:** ADR-0001 to ADR-0011 have no numbered rules, so a check will list them as unchecked. Rewriting them for checking would mean 11 new `Proposed` records, each replacing an old one once it's accepted. Should I go ahead?
5. **Alternatives:** the meeting notes listed no rejected alternatives. I wrote A1 based on the decision, so please confirm it or replace it with what the meeting actually discussed.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

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

- [ADR-0012: Keep the token packages free of imports of `net/http` and of the HTTP server](0012-keep-token-packages-free-of-http-imports.md):
  R1 keeps `net/http` out of `internal/token/verify`, so the HTTP status of R2 is set in `internal/http`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. `internal/token/verify` verifies a token, and
`internal/http` holds the HTTP server and its middleware. A token header names the algorithm that signs the token. The
algorithm `none` means that the token carries no signature, so anyone can write a token with any claims.

The check that refuses such a token sits in `internal/token/verify`. No test covers it.

## Decision

We will refuse every token whose header names the algorithm `none`, in `internal/token/verify`, and the HTTP server will
respond to such a request with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **alg-none token**: a token whose header has an algorithm parameter (`alg`) equal to `none` in a case-insensitive
  comparison, such as `none`, `None`, or `NONE`.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE` for an
  alg-none token. This holds whatever else the token holds, such as an expired time or a malformed signature.

#### HTTP response

- **R2** (`http`). The HTTP server responds to a request that carries an alg-none token with status 401 and the reason
  code `TOKEN_ALG_NONE` in `<where the reason code appears in the response>`, and policy evaluation is not run for that
  request.

### Implementation notes

Adds no requirement. Compare the `alg` value with `strings.EqualFold(alg, "none")` before any other check of the token in
`internal/token/verify`. Return an error type from `internal/token` that carries the reason code, and let the middleware
in `internal/http` map that reason code to status 401, so that `internal/token/verify` does not import `net/http`
(ADR-0012 R1). A table test in `internal/token/verify` with `none`, `None`, and `NONE`, and a handler test in
`internal/http`, would cover R1 and R2.

### Justification

A token signed with `none` has no signature, so the service cannot tell a forged token from a real one (R1, R2). With
the check in `internal/token/verify`, every caller of that package refuses the token, including the planned
`tokencheck`, and not only the HTTP server (R1). A reason code of its own lets a client and the logs tell this refusal
from other token failures (R1, R2). Status 401 tells the client that the request has no valid credentials (R2).

### Alternatives considered

- **A1. Check `alg` in the HTTP middleware before verification.** Rejected by R1: `tokencheck` calls
  `internal/token/verify` without the middleware, and it would accept an alg-none token.
- **A2. Refuse an alg-none token with the reason code that any other unsupported algorithm gets.** Rejected by R1 and
  R2, which require `TOKEN_ALG_NONE`.

## Consequences

Negative:

- A client that sends an unsigned token with `alg` set to `none`, such as a local test setup, gets status 401 (R2).

## Open points

- **O1.** Where in the 401 response does the reason code appear, for example a field of a JSON body or a response
  header? R2 holds a placeholder until this is settled. @example-security-architect decides. Affects R2.
- **O2.** Should the comparison with `none` ignore case? The record assumes it does, in **alg-none token**. The answers
  under consideration: only the exact value `none`, or any case of `none`. @example-security-architect decides.
  Affects R1 and R2.
- **O3.** Does `TOKEN_ALG_NONE` take precedence over the reason code for any other problem in the same token, such as
  an expired time? The record assumes it does, in R1. The answers under consideration: `TOKEN_ALG_NONE` always, or the
  reason code of whichever check `internal/token/verify` runs first. @example-security-architect decides. Affects R1
  and R2.
````

### Message to the user

I added ADR-0013 as `Proposed`. It links ADR-0012 because `verify` can't import `net/http`: the reason code comes from `internal/token/verify`, and the 401 is set in `internal/http`. This change only touches `docs/adr/`, so it doesn't need trailers.

**What blocks acceptance:** three open points, and @example-security-architect decides each one:

- **O1:** where the reason code goes in the 401 response. R2 has a placeholder there.
- **O2:** does the comparison with `none` ignore case? The draft assumes it does.
- **O3:** does `TOKEN_ALG_NONE` win over other problems in the same token? The draft assumes it does.

**No test yet:** the record has no Confirmation section. When a test lands, add it to Confirmation. An accepted record allows that edit.

**Questions:**

1. **Current behavior:** does the existing check in `internal/token/verify` already compare without regard to case and return `TOKEN_ALG_NONE` before any other check? Does the middleware already map that reason to 401 and skip policy evaluation? If not, the change that brings this behavior should end with `Implements: ADR-0013 R1, R2`.
2. **Issue for the test:** do you want to open an issue for the missing test so the work is tracked?
3. **Alternatives:** the review notes listed no rejected alternatives. I wrote A1 and A2 based on the decision, so please confirm them or replace them with what the review discussed.
