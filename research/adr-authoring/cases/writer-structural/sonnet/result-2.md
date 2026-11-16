## Request 1

### File: docs/adr/0012-token-packages-free-of-http-imports.md

````markdown
# Keep the token packages free of imports of HTTP packages

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

- Architect, @example-architect: approves R1.
<!-- markdownlint-enable MD001 -->

## Context

Packages under `internal/token/` parse and verify tokens. The HTTP server, its middleware, and its handlers are under
`internal/http/`. The planned command-line tool `tokencheck` verifies tokens offline and has to build without the HTTP
server. The depguard rule `token-no-http` in `.golangci.yml` checks imports of `internal/http/` and of `net/http`, and
CI already runs it.

## Decision

We will keep every package under `internal/token/` free of imports of `internal/http/` and of `net/http`.

### Terms

- **token package**: a Go package in a directory under `internal/token/`, with its test files.
- **HTTP package**: `net/http` or a package below it, and `example/token-gate/internal/http` or a package below it.

### Rules

#### Imports of the token packages

- **R1** (`token`). No Go file of a token package imports an HTTP package.

### Confirmation

- **R1**: the golangci-lint rule `token-no-http` (depguard), configured in `.golangci.yml`, which CI runs on every pull
  request. The lint step fails when a token package imports `internal/http/` or `net/http`.

### Implementation notes

Adds no requirement. A token package returns its own result and error types, and `internal/http` maps them to HTTP
statuses and responses.

### Justification

`tokencheck` builds without the HTTP server only if no token package imports an HTTP package (R1). Depguard checks an
import rule, and CI already runs it (R1).

### Alternatives considered

- **A1. Let a token package import an HTTP package and build `tokencheck` with the HTTP server.** Rejected by R1:
  `tokencheck` has to build without the HTTP server.

## Consequences

Negative:

- A token package cannot use `net/http` types or constants, such as `http.StatusUnauthorized`, and its tests cannot use
  `net/http/httptest` (R1).

## Open points

- **O1.** Do the test files of a token package fall under R1? The answers are yes, as the **token package** term
  assumes, and no, so that a test may import `net/http/httptest`. @example-architect decides. It affects R1.
- **O2.** Does R1 cover the packages below `net/http`, such as `net/http/httptest`? The answers are yes, as the **HTTP
  package** term assumes, and no, so that only `net/http` itself is barred. @example-architect decides. It affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code under the paths of the layers below. Records `0001-` to `0011-` have no
numbered rules, so a check lists them as unchecked.

## Layers

| Layer | Paths |
| --- | --- |
| `token` | `internal/token/`, with the tests beside the code |
| `http` | `internal/http/`, with the tests beside the code |
| `entrypoint` | `cmd/` |

These paths belong to no layer, because no rule constrains them: `docs/adr/`, `AGENTS.md`, `go.mod`, `go.sum`,
`.golangci.yml`, and `.github/workflows/`. A change that adds a rule over one of them maps it to a layer. A change that
adds a file that neither the layers nor this list cover extends one of them.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
does not.

## What to read before you change code

Read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each binding record whose rules name a
layer that your change touches. Anything that no rule states is your choice. Where a rule cites a rule of another
record, read the **Related ADRs** of that record too, because a line there names any later record that replaces the
cited rule.

## Trailers

Every change to code under the paths above ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0013 R2 to #208
```

`Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with the issue or pull
request that will bring it. A `Defers` target must exist. Where no change exists yet, open an issue first. A change that
brings no rule and leaves none out, such as a refactoring, carries neither trailer. In a pull request with several
commits, each commit carries the trailers of its own part, and the description carries them for the whole change.

## Checking a change

[Checking a change](TBD) in the `adr-authoring` skill describes how a change is checked against the rules.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that it describes.
````

### Message to the user

I added ADR-0012, the reading guide, and a bullet in `AGENTS.md`. The guide is included because the meeting agreed to it and to the trailers.

- **Status:** ADR-0012 is `Proposed`, not `Accepted`, because it has two open points. I left out the Date heading. Add it on acceptance.
- **Related ADRs:** I left out the heading because the record cites no other record.
- **Alternatives:** A1 is my inference from the `tokencheck` requirement. Please confirm it.
- **Open points:** both were assumptions I had to make:
  - **O1:** Do test files of `internal/token/` packages count? I assumed they do, because depguard checks tests unless `run.tests` is false.
  - **O2:** Does the rule cover `net/http/httptest` and the other packages below `net/http`? I assumed it does, because depguard matches by prefix.
  - If either is wrong, say so and I will change the term and close the point.
- **Questions for you:**
  - What is the URL of the `adr-authoring` skill at the version you pin? The guide has `TBD` as the link target, and I did not guess one. The repository does not use APM, so the link goes to the skill on GitHub.
  - Are the layer names `token`, `http`, and `entrypoint` fine? Is it right that `go.mod`, `go.sum`, `.golangci.yml`, and the workflow files belong to no layer? A change that weakens `token-no-http` is not checked today. Do you want a rule that requires the depguard rule? That would be a new decision, so I did not add it.
- **Trailers:** this change touches only docs and `AGENTS.md`, so it carries no trailers.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

````markdown
# Refuse a token whose header names the algorithm none

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of HTTP packages](0012-token-packages-free-of-http-imports.md): R1
  bars imports of HTTP packages from `internal/token/`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The header of a token names the algorithm that
signs it. A token whose header names the algorithm `none` carries no signature to verify. The security review found
that no test covers the refusal of such a token.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and
we will make that check in `internal/token/verify`.

### Terms

- **none token**: a token whose header names the algorithm `none`, in any letter case.

### Rules

#### Refusal of a none token

- **R1** (`token`, `http`). The service answers a request whose token is a none token with HTTP 401 and the reason code
  `TOKEN_ALG_NONE` in <reason code field>.
- **R2** (`token`). The check that detects a none token is in the package `internal/token/verify`.

### Implementation notes

Adds no requirement. A token package cannot import HTTP packages (ADR-0012 R1), so `internal/token/verify` reports the
reason code `TOKEN_ALG_NONE` in its own error type, and `internal/http` maps that error to HTTP 401.

### Justification

A none token has no signature to verify, so the service refuses it before policy evaluation (R1). Keeping the check in
the package that verifies tokens gives one place that decides which tokens are valid (R2).

### Alternatives considered

- **A1. Accept a none token and leave the decision to policy evaluation.** Rejected by R1: a none token carries no
  signature, so nothing shows who issued it.

## Consequences

Negative:

- A client that sends a none token gets HTTP 401, also where the token is otherwise well formed (R1).

## Open points

- **O1.** Does `None` or `NONE` count as the algorithm `none`? The answers are yes, as the **none token** term assumes,
  and no, so that only the exact string `none` counts. @example-security-architect decides. It affects R1.
- **O2.** Which field of the 401 response carries the reason code: a body member, a header, or another field?
  @example-security-architect decides. It affects R1, where `<reason code field>` stands for the answer.
- **O3.** Which reason code does a token get when it is a none token and also has another defect, such as an expired
  time or a malformed claim? The answers are `TOKEN_ALG_NONE` always, or the code of the first check that fails in
  `internal/token/verify`. @example-security-architect decides. It affects R1.
````

### Message to the user

I added ADR-0013 and changed no other file. The reading guide from Request 1 already maps both layers, so it needs no edit.

- **Status:** the record is `Proposed`, and the Date heading is left out until acceptance. Three open points block acceptance, and @example-security-architect decides all of them:
  - **O1:** Does `None` or `NONE` count as the algorithm `none`? I assumed yes, which is the safer reading.
  - **O2:** Which field of the 401 response carries `TOKEN_ALG_NONE`? R1 has the visible placeholder `<reason code field>`. Please tell me the field, or point me to the code that sets it.
  - **O3:** Which reason code wins when a none token has another defect as well?
- **Two rules, two layers:**
  - R1 is the behavior and carries the `token` and `http` layers.
  - R2 is the location of the check in `internal/token/verify`.
  - ADR-0012 R1 stops `internal/token/verify` from producing an HTTP status. So the record says the status is produced in `internal/http`, and I cited ADR-0012 under Related ADRs. ADR-0012 is still `Proposed`, so it does not bind yet, and the layering follows it anyway.
- **Alternatives:** A1 is my inference. Please confirm it.
- **No Confirmation section:** no check exists yet, so the section is left out. A test should cover both the `TOKEN_ALG_NONE` result from `internal/token/verify` and the 401 from `internal/http`. When it lands, add a Confirmation entry for R1. Its commit then ends with `Implements: ADR-0013 R1` once the record is accepted.
- **Defect check:** I did not treat the missing test as a defect that needs an issue. The input does not say whether the code already behaves as R1 describes. If it does not, tell me, and I will propose a Bug issue for that.
