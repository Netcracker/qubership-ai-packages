## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

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
handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. `tokencheck` has to build without the
HTTP server. A Go program links every package that its packages import, either directly or through other packages. One
import of `internal/http/` or of `net/http` in a token package therefore puts the HTTP server or the HTTP stack into
`tokencheck`.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token` or a directory below it. The external test
  package of such a directory, whose name ends in `_test`, is a token package too.
- **imports**: a package imports another package when an import declaration in one of its `.go` files names that
  package. Test files (`_test.go`) count. An import through a third package does not count.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports a package whose import path is `example/token-gate/internal/http` or
  starts with `example/token-gate/internal/http/`, or a package whose import path is `net/http` or starts with
  `net/http/`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in `.github/workflows/ci.yml`
  on every pull request, reports an import of a package under `internal/http/` or of `net/http` in a token package.

### Justification

`tokencheck` builds without the HTTP server only if no token package imports it or the HTTP stack (R1). R1 also covers
the packages below `net/http`, such as `net/http/httptest`, because each of them imports `net/http` itself (R1). The
depguard rule runs on every pull request, so CI fails on a forbidden import before `tokencheck` exists (R1).

### Alternatives considered

- **A1. Let `internal/token/verify` take an `*http.Request` and read the token from its header.** Rejected by R1:
  `internal/token/verify` would import `net/http`, and `tokencheck`, which has no request, would link the HTTP stack.

## Consequences

Negative:

- A token package cannot return an HTTP status or use types such as `http.Header`. The code in `internal/http/` maps
  each error of a token package to a status itself (R1).

## Open points

- **O1.** Whether **imports** also covers indirect imports. R1 assumes direct imports only, which depguard checks. The
  other answer forbids a token package to import any package that imports a forbidden package, at any depth, and needs
  a check such as `go list -deps` in CI. @example-architect decides. Affects R1.
- **O2.** Whether test files count under **imports**. R1 assumes that they do. The other answer leaves `_test.go`
  files out, because `tokencheck` does not link them, and lets a test in a token package use `net/http/httptest`.
  @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Each file in this directory records one architecture decision for token-gate. Records from `0012-` on state their
requirements as numbered rules, and a change to the code they govern is checked against those rules.

## Layers

A rule names the layer it constrains, such as `(token)`. Each layer maps to these paths:

| Layer | Paths |
| --- | --- |
| `token` | `internal/token/` |
| `http` | `internal/http/` |
| `cmd` | `cmd/` |
| `build` | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/` and `AGENTS.md`.

A test beside its code belongs to the layer of that code. A change that adds a file outside every path in this section
adds the path to a layer or to the list of paths that belong to no layer, in the same change.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Reading a record before you change code

In each record that governs the layer you change, read **Terms**, **Rules**, **Confirmation**, and **Implementation
notes**. Anything no rule states is your choice. Where a rule cites a rule of another record, also read that record's
**Related ADRs**, where a line names any later record that replaces the cited rule.

## Trailers

A change to code under a path that this guide maps to a layer ends its commit message and its pull request description
with two trailers. `Implements` names the rules the change brings. `Defers` names each rule it leaves out, with the issue
or pull request that will bring it:

```text
Implements: ADR-0012 R1
Defers: ADR-0013 R2 to #123
```

A `Defers` target is an issue or a pull request that exists. Where none exists, leave the rule out of the trailers, and
name it in the pull request description. A change that brings no rule and leaves none out, such as a refactoring, carries
neither trailer.

## Checking a change

A reviewer, a person or an agent, checks a change as
[Checking a change in the adr-authoring skill](<URL of the adr-authoring SKILL.md at the pinned version>#checking-a-change)
describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to a layer. Read that guide
  before you change such code. End the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that the guide describes.
````

### Message to the user

I've drafted ADR-0012 with one rule, R1. The rule is about imports from the token packages: none of them may import a package under `internal/http/`, `net/http` itself, or any package below `net/http`. Confirmation names the depguard rule `token-no-http`. I also added the reading guide in `docs/adr/README.md` and a bullet in `AGENTS.md` that points to it. From now on, every change to code under the mapped paths ends with the `Implements:` and `Defers:` trailers. This change only touches `docs/` and `AGENTS.md`, so it needs no trailers itself.

The record is `Proposed`. It needs two answers from @example-architect before it can be accepted:

- **O1:** Should R1 cover only direct imports, which is what depguard checks and what I assumed? Or should it also cover indirect imports? Indirect imports also affect `tokencheck`, but checking them would need something like `go list -deps` in CI.
- **O2:** Should test files count? I assumed yes. If they don't, tests in the token packages could use `net/http/httptest`.

Once the architect approves and both points are settled, set the status to `Accepted` and add a `#### Date` heading with the acceptance date above `#### Owner`.

Before merging, please check these:

1. **The skill link in the guide.** The guide links to the **Checking a change** section of the adr-authoring skill through the placeholder `<URL of the adr-authoring SKILL.md at the pinned version>`. The repository doesn't use APM, so which URL and version should it point to? Please fill it in before the merge.
2. **What `token-no-http` covers.** I haven't seen `.golangci.yml`. Does the depguard rule check `_test.go` files, and does it deny the packages below `net/http` as well as `net/http` itself? If not, the Confirmation entry claims more than the check does. Either the depguard rule or the record needs to change.
3. **The `build` layer.** I mapped `go.mod`, `go.sum`, `.golangci.yml`, and `.github/` to a `build` layer, and `docs/` and `AGENTS.md` to no layer. I don't know about any other top-level files, such as a `README.md` or a `Makefile`. If there are any, they need to be added to one of those lists.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose `alg` is `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  the import rule of ADR-0012 R1, which `internal/token/verify` falls under.
<!-- markdownlint-enable MD001 -->

## Context

The JOSE header of a token names its signing algorithm in the `alg` parameter. RFC 7518, section 3.6, defines the
value `none` for an unsecured JWS, which carries no signature. A service that accepts such a token accepts claims that
any client can write.

The security review asked the service to refuse such a token. `internal/token/verify` holds the check, and no test
covers it. `internal/token/verify` is a token package under the import rule of ADR-0012 R1.

## Decision

We will refuse every token whose JOSE header names the algorithm `none`. The service will answer such a request with
HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses a token whose JOSE header has the `alg` parameter `none`, in any
  letter case, and reports the refusal with the reason code `TOKEN_ALG_NONE`.

#### HTTP response

- **R2** (`http`). The service responds to a request whose token `internal/token/verify` refuses under R1 with HTTP
  status 401 and the reason code `TOKEN_ALG_NONE` in `<response field that carries the reason code>`, and does not pass
  the request to policy evaluation.

### Implementation notes

Adds no requirement. A table test in `internal/token/verify` can cover `none`, `None`, and `NONE`. A handler test in
`internal/http/` that uses `net/http/httptest` can cover R2.

### Justification

A token whose `alg` is `none` carries no signature, so accepting it lets a client choose its own claims (R1). R1 refuses
every letter case, because a library that compares `alg` without regard to case would treat `None` as `none` (R1).

R1 names a reason code and R2 names the HTTP status. `tokencheck` can then report the refusal without the HTTP server,
and `internal/token/verify` stays within the import rule of ADR-0012 R1 (R1, R2). The status 401 tells the client that
its credentials were refused, and policy evaluation never sees a token that carries no signature (R2).

### Alternatives considered

- **A1. Let the HTTP middleware read `alg` and refuse `none` before it calls `internal/token/verify`.** Rejected by R1:
  `tokencheck` does not run the middleware, so it would accept such a token.

## Consequences

Negative:

- A test or a tool that sends an unsecured token to the service gets HTTP 401 and has to sign its tokens (R2).

## Open points

- **O1.** Whether R1 refuses `none` in every letter case. R1 assumes that it does. The other answer refuses only the
  exact value `none`, and `None` or `NONE` gets whatever `internal/token/verify` returns for an unknown algorithm.
  @example-security-architect decides. Affects R1.
- **O2.** Where the response carries the reason code: for example a field of a JSON body, or a response header.
  @example-security-architect decides. Affects R2.
````

### Message to the user

I've drafted ADR-0013 with two rules. Under R1, `internal/token/verify` refuses a token whose `alg` is `none` and reports the reason code `TOKEN_ALG_NONE`. Under R2, the HTTP layer turns that refusal into a 401 with the same reason code and doesn't pass the request to policy evaluation. I split them because ADR-0012 R1 keeps `net/http` out of `internal/token/verify`, so the 401 has to come from `internal/http/`. The split also means `tokencheck` gets the R1 check without the HTTP server.

The record is `Proposed`. It needs two answers from @example-security-architect before it can be accepted:

- **O1:** Should R1 refuse `none` in any letter case (`None`, `NONE`), as I assumed, or only the exact value `none`?
- **O2:** Where does the response carry the reason code? R2 has the visible placeholder `<response field that carries the reason code>` until this is decided. If the service already has a convention for reason codes, tell me what it is and I'll use it.

Once it's approved and both points are settled, set the status to `Accepted` and add a `#### Date` heading with the acceptance date above `#### Owner`.

No test covers the check yet, so the record has no **Confirmation** section. I suggest opening an issue, type Task, titled "Add tests for ADR-0013 R1 and R2": a table test in `internal/token/verify` and a handler test in `internal/http/`. When those tests land, add each one under **Confirmation** next to its rule. That edit is allowed even after the record is accepted.

I haven't seen the code in `internal/token/verify`. If the existing check compares `alg` case-sensitively and O1 keeps "any letter case", the code needs a change to meet R1. That change would carry `Implements: ADR-0013 R1`.

This change only adds a record under `docs/`, so it needs no trailers.
