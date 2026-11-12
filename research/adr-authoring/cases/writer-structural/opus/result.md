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

- Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The packages under `internal/token/` parse and
verify a token. The packages under `internal/http/` hold the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It has to build from the token packages
without the HTTP server.

The depguard rule `token-no-http` in `.golangci.yml` reports an import of a package under `internal/http/` and an import
of `net/http` in the packages under `internal/token/`. The golangci-lint job in `.github/workflows/ci.yml` runs it on
every pull request.

## Decision

We will keep every token package free of imports of the packages under `internal/http/` and of `net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token` or a directory below it. The external test package
  of such a directory, the one whose name ends in `_test`, is a token package too.
- **imports**: a token package imports a package when one of its Go files, `_test.go` files included, names that package
  in an import declaration.
- **HTTP server package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP server package.
- **R2** (`token`). No token package imports `net/http`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in `.github/workflows/ci.yml` on
  every pull request, fails when a token package imports an HTTP server package.
- **R2**: the same rule fails when a token package imports `net/http`.

### Implementation notes

Adds no requirement. Where token code has to tell its caller why it refused a token, return an error type of the token
package, and let a handler or a middleware under `internal/http/` map that error to a status code. Code that fetches
keys over HTTP lives outside `internal/token/`, and the token packages receive the keys through an interface that they
define.

### Justification

`tokencheck` can build from the token packages without the HTTP server only if no token package imports it or
`net/http` (R1, R2). The depguard rule reports a forbidden import in the pull request that adds it, so no one has to
wait for `tokencheck` to exist and fail its build (R1, R2).

### Alternatives considered

- **A1. Use the status constants of `net/http`, such as `http.StatusUnauthorized`, in a token package to describe a
  refusal.** Rejected by R2: the import puts `net/http` into the build of every binary that uses the token package.
- **A2. Move the verification code into `internal/http/` and let `tokencheck` import it from there.** `tokencheck` would
  then build with the HTTP server.

## Consequences

Positive:

- A change under `internal/http/` leaves the cached test results of the token packages valid.

Negative:

- A token package cannot fetch keys or other data over HTTP itself. That code lives outside `internal/token/` and passes
  its result in (R2).
- The status code for a refused token is chosen under `internal/http/`, apart from the check that refuses the token (R1,
  R2).

## Open points

- **O1.** R1 and R2 forbid direct imports only, as the architecture meeting stated them. Should they also forbid indirect
  imports, such as a token package that imports `net/http/httptest` or a third-party library that imports `net/http`?
  The answers are direct imports only, which `token-no-http` checks, or direct and indirect imports, which needs a
  further check such as a test over the output of `go list -deps`. @example-architect decides. This affects R1 and R2.
- **O2.** R1 and R2 count `_test.go` files, on the assumption that `token-no-http` checks them too. The answers are that
  test files count, or that only non-test files count, since `tokencheck` does not build test files.
  @example-architect decides. This affects R1, R2, and their entries under **Confirmation**.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Each file in this directory records one architecture decision for token-gate. A record with numbered rules governs the
code under the layers its rules name.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the binaries | `cmd/` |
| `build` | The Go module, the linter settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/` and `AGENTS.md`. A path stays in this list only while no rule constrains it.

A change that adds a file that neither the layers nor this list cover extends one of them in the same change.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read before you change code

In each record that governs the code you change, read **Terms**, **Rules**, **Confirmation**, and **Implementation
notes**. Anything no rule states is your choice.

Records `0001-` to `0011-` have no numbered rules, and a check of a change lists them as unchecked.

## Trailers

Every change to code under the layers in [Layers](#layers) ends its commit message and its pull request description
with two trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0013 R1 to #208
```

`Implements` names the rules the change brings, every case of each. `Defers` names each rule the change leaves out, or
brings only in part, with the existing issue or pull request that will bring the rest. A change that brings no rule and
leaves none out, such as a refactoring, carries neither trailer. In a pull request with several commits, each commit
carries the trailers of its own part, and the description carries them for the whole change.

## Checking a change

A reviewer checks a change against the rules as the section "Checking a change" of the `adr-authoring` skill describes:
`<link to that section, at the version this repository pins>`.
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

I added ADR-0012 as `Proposed`, along with the reading guide in `docs/adr/README.md` and a paragraph in `AGENTS.md` that points to the guide. From now on, every change to code under `internal/`, `cmd/`, `go.mod`, `go.sum`, `.golangci.yml`, or `.github/` ends with the `Implements:` and `Defers:` trailers, as the team agreed. This change only touches `docs/adr/` and `AGENTS.md`, so it carries no trailers.

The record has two open points. They block `Accepted` until @example-architect decides them:

- **O1:** Do R1 and R2 forbid only direct imports, or indirect ones as well, such as `net/http/httptest` or a library that imports `net/http`? `token-no-http` checks only direct imports.
- **O2:** Do `_test.go` files count? I assumed they do. I couldn't see the `files` setting of `token-no-http` in `.golangci.yml`, so please confirm that the rule checks test files.

Once the architect approves and both points are closed, set the status to `Accepted` and add the `#### Date` heading with the acceptance date.

Questions:

1. The guide has to link to the section "Checking a change" of the `adr-authoring` skill. The repository doesn't use APM, so the link has to go to GitHub at a pinned version. What is the skill's repository URL, and which version or commit should the guide pin? Until you tell me, `docs/adr/README.md` has a visible placeholder there.
2. Are the layers in the guide (`token`, `http`, `cmd`, `build`) and the no-layer list (`docs/`, `AGENTS.md`) right? Are there other root files, such as a `README.md` or a `Dockerfile`, that need to go in one of them?

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

- Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of `internal/http` and `net/http`](0012-token-packages-without-http.md):
  its `net/http` import rule, R2, decides where **Implementation notes** puts the status code.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The header of a token names the algorithm of its
signature. The name `none` declares a token with no signature. A verifier that follows the header would accept that
token, although anyone can write one.

A security review decided how token-gate handles such a token. The check sits in `internal/token/verify`. No test covers
it yet.

## Decision

We will refuse every token whose header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`.

### Terms

- **token**: the token that token-gate checks for a request before policy evaluation.

### Rules

#### Tokens without a signature

- **R1** (`token`, `http`). When the header of a token names the algorithm `none`, compared without regard to case,
  token-gate responds with HTTP status 401 and the reason code `TOKEN_ALG_NONE`, and the request does not reach policy
  evaluation. R1 applies whatever else the token carries, such as an expiry time in the past or an invalid signature.

### Implementation notes

Adds no requirement. In `internal/token/verify`, check the algorithm before the signature and before every other check
of the token. Return an error that carries `TOKEN_ALG_NONE`. A handler or a middleware under `internal/http/` maps that
error to the status 401, as the `net/http` import rule of ADR-0012 R2 requires.

Cover R1 with a table test in `internal/token/verify` for the header values `none`, `None`, and `NONE`, plus one for a
token that names `none` and has also expired. Add a test under `internal/http/` that checks the status 401 and the
reason code in the response.

### Justification

A token that names `none` has no signature, so if token-gate accepted one, anyone could write a token that passes the
check (R1). Comparing without regard to case also refuses `None` and `NONE`. Otherwise, a library that matches
algorithm names without regard to case could treat those spellings as `none` (R1). A reason code of its own keeps these
refusals apart from expired or malformed tokens in the responses and the logs (R1).

### Alternatives considered

- **A1. Let the signature check refuse a token that names `none`, as it refuses any token without a valid signature.**
  Rejected by R1: the response would carry the reason code of a failed signature instead of `TOKEN_ALG_NONE`.
- **A2. Compare the algorithm name with `none` exactly, and leave `None` and `NONE` to the other checks.** Rejected by
  R1, under the assumption that O1 names.

## Consequences

Negative:

- token-gate refuses a token that names `none` from every client, including test environments and tools. Such a client
  has to sign its tokens (R1).
- A token that names `none` and fails another check also gets `TOKEN_ALG_NONE`, not the reason code of that other check
  (R1).

## Open points

- **O1.** R1 compares the algorithm name without regard to case, on the assumption that `None` and `NONE` are to be
  refused like `none`. The answers are: without regard to case, or exactly `none`, which leaves other spellings to the
  other checks in `internal/token/verify`. @example-security-architect decides. This affects R1.
- **O2.** R1 assumes that a 401 response from token-gate already has a place for a reason code, and that
  `TOKEN_ALG_NONE` goes there. If no such place exists yet, @example-security-architect chooses one: a field of the
  response body or a response header. This affects R1.
````

### Message to the user

I added ADR-0013 as `Proposed`, with one rule, R1, tagged with both `token` and `http`. The check lives in `internal/token/verify`, but the 401 comes from `internal/http/`. The record has two open points. They block `Accepted` until @example-security-architect decides them:

- **O1:** Should `None` and `NONE` be refused like `none`? I assumed they should.
- **O2:** Where does a 401 response carry the reason code `TOKEN_ALG_NONE`? I assumed token-gate already has a place for reason codes. If it doesn't, the security architect chooses a body field or a header.

R1 also says that `TOKEN_ALG_NONE` wins over every other refusal reason, such as an expired token. That is my literal reading of the review's decision. If the review meant something else, tell me and I'll change R1.

Since no test covers R1, the record has no **Confirmation** section yet. I suggest opening an issue:

- **Type:** Task
- **Title:** Add tests for the refusal of tokens whose header names the algorithm `none`
- **Body:** Covers ADR-0013 R1. Add a table test in `internal/token/verify` for `none`, `None`, `NONE`, and for an expired token that names `none`. Add a test under `internal/http/` for the status 401 and the reason code `TOKEN_ALG_NONE`.

The pull request that adds the tests ends with `Implements: ADR-0013 R1`, and it also adds the test names under **Confirmation** in ADR-0013. An accepted record can take that edit too. Can you open the issue and send me its number? A later change that leaves R1 out can then name the issue in `Defers:`.

This change only touches `docs/adr/`, so it carries no trailers.
