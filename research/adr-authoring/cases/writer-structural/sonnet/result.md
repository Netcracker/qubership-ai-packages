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

Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service parses and verifies a token in `internal/token/parse` and `internal/token/verify`, and serves HTTP from
`internal/http/`. The planned command-line tool `tokencheck` verifies tokens offline and has to build without the HTTP
server. A Go package builds every package it imports.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`, so that `tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`, together with its test files, including external test packages.
- **HTTP server package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **net/http package**: the package `net/http`, and every package whose import path starts with `net/http/`.
- **imports**: a Go file names the package in an import declaration, with or without an alias, including a blank or dot
  import. A package that a token package reaches only through another package is not imported by it.

### Rules

#### Imports of the token packages

- **R1** (`token`). No file of a token package imports an HTTP server package.
- **R2** (`token`). No file of a token package imports a net/http package.

### Confirmation

- **R1, R2**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs through
  `.github/workflows/ci.yml` on every pull request, fails on an import of an HTTP server package or of `net/http` in a
  package under `internal/token/`.

### Justification

`tokencheck` has to build without the HTTP server. A package builds every package it imports, so a token package that
imported an HTTP server package or `net/http` would bring the HTTP server into `tokencheck` (R1, R2).

### Alternatives considered

- **A1. Let a token package import `internal/http` to read the request or to share a type.** Rejected by R1: `tokencheck`
  would then build the HTTP server.
- **A2. Let a token package take `*http.Request` or `http.Header` as a parameter.** Rejected by R2: the import of
  `net/http` is enough to bring the HTTP stack into `tokencheck`.

## Consequences

Negative:

- A token package cannot take an `net/http` type as a parameter or return value. The HTTP layer reads the token from the
  request and passes it on as a value of another type (R2).

## Open points

- **O1.** Does R2 cover the subpackages of `net/http`, such as `net/http/httptest`? The text assumes it does. The other
  answer is that R2 covers only the package `net/http`. @example-architect decides. It affects R2 and the configuration
  of `token-no-http`, which has to match the answer.
- **O2.** Do R1 and R2 cover test files of the token packages? The text assumes they do. The other answer is that they
  cover only the files that `go build` compiles. @example-architect decides. It affects R1, R2, and the configuration
  of `token-no-http`.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory are numbered from `0001-`. Records 0001 to 0011 have no numbered rules, so a check lists
them as unchecked. From ADR-0012 on, a record states its requirements as numbered rules, and each rule names the layer
of the code it constrains.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer, because no rule constrains them: `internal/http/`, `cmd/token-gate/`, `go.mod`,
`go.sum`, `.github/`, `.golangci.yml`, `docs/adr/`, and `AGENTS.md`. A change that adds a file covered by neither the
table nor this list extends one of them in the same change. When a rule starts to constrain a path from this list, the
change that adds the rule moves the path into a layer.

## Which records bind a change

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not.

## What to read before you change code

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
binding record that has a rule in that layer. A requirement that no rule states is your choice.

## Trailers

Every change to code under the paths of a layer ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-NNNN R1, R2
Defers: ADR-NNNN R3 to #<issue or pull request number>
```

- `Implements` names the rules the change brings.
- `Defers` names each rule that the change leaves out, with the existing issue or pull request that will bring it. A
  change that brings only some cases of a rule names the rule under `Defers`.
- Where no issue or pull request exists for a deferred rule, leave the rule out of the trailers and say in the
  description which rules wait for a change that has no issue yet.
- A change that brings no rule and leaves none out carries neither trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

A reviewer checks a change against the rules by the procedure in **Checking a change** in the `adr-authoring` skill:
<link to the skill at the version this repository pins, TBD>.
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

I wrote ADR-0012 with the status `Proposed` and no Date heading. Tell me whether the architecture meeting accepted it. If it did, I will set `Accepted` and add the date once O1 and O2 are settled.

Questions:

1. What is the URL of the `adr-authoring` skill at the version you pin? `docs/adr/README.md` has a visible placeholder for it, because the repository does not use APM and I have no link to give.
2. Please settle two assumptions I made, which are listed as open points in the record.
   - **O1:** R2 covers `net/http` and its subpackages, such as `net/http/httptest`.
   - **O2:** R1 and R2 cover test files.
   - I could not see `.golangci.yml`. Please confirm that `token-no-http` matches whichever answers you choose.

Notes:

- The guide, the `AGENTS.md` paragraph, and the trailers follow your request. I added the guide as `docs/adr/README.md`.
- The guide maps one layer, `token`. Every other path is listed as belonging to no layer, because no rule constrains it yet.
- Records 0001 to 0011 have no numbered rules, so checks report them as unchecked. I did not touch them.
- This change touches no code under a layer, so it carries no trailers.

## Request 2

### File: docs/adr/0013-refuse-token-alg-none.md

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

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  R1 and R2 apply to the package that holds the check.
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` carries no signature. The service checks the token of each request
before policy evaluation, and the security review found that a token of this kind has to be refused.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and
we will make that check in `internal/token/verify`.

### Terms

- **alg-none token**: a token whose header has the member `alg` with the string value `none`, compared case-sensitively.

### Rules

#### Refusal of an alg-none token

- **R1** (`token`). A function of `internal/token/verify` that verifies a token returns an error that carries the reason
  code `TOKEN_ALG_NONE` for an alg-none token, including where another check would also refuse that token.
- **R2** (`http`). The HTTP server answers a request that carries an alg-none token with status 401 and the reason code
  `TOKEN_ALG_NONE` in <the response field that carries a reason code>.

### Justification

An alg-none token has no signature, so accepting it would let a caller choose its own claims (R1, R2). The check sits
in `internal/token/verify`, so every caller of that package refuses the token, and the HTTP server only maps the
refusal to a response (R1, R2).

### Alternatives considered

- **A1. Refuse the token in HTTP middleware before it calls `internal/token/verify`.** Rejected by R1: a caller of
  `internal/token/verify` outside the HTTP server, such as the planned `tokencheck`, would then accept the token.

## Consequences

Negative:

- No test covers R1 or R2 yet, so a regression shows only in review.

## Open points

- **O1.** Is `none` compared case-sensitively? The text assumes it is, as RFC 7518 defines `alg` values. The other
  answer is that `None` and `NONE` are alg-none tokens too. @example-security-architect decides. It affects the term
  **alg-none token**, R1, and R2.
- **O2.** Does the reason code `TOKEN_ALG_NONE` win where an alg-none token has another defect, such as an expired
  claim? The text assumes it does. @example-security-architect decides. It affects R1 and R2.
- **O3.** Which field of the HTTP response carries the reason code, such as a JSON body member or a header? A value is
  needed in R2, in place of the placeholder. @example-security-architect decides.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory are numbered from `0001-`. Records 0001 to 0011 have no numbered rules, so a check lists
them as unchecked. From ADR-0012 on, a record states its requirements as numbered rules, and each rule names the layer
of the code it constrains.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |
| `http` | HTTP server, middleware, and handlers | `internal/http/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer, because no rule constrains them: `cmd/token-gate/`, `go.mod`, `go.sum`, `.github/`,
`.golangci.yml`, `docs/adr/`, and `AGENTS.md`. A change that adds a file covered by neither the table nor this list
extends one of them in the same change. When a rule starts to constrain a path from this list, the change that adds the
rule moves the path into a layer.

## Which records bind a change

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not.

## What to read before you change code

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
binding record that has a rule in that layer. A requirement that no rule states is your choice.

## Trailers

Every change to code under the paths of a layer ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-NNNN R1, R2
Defers: ADR-NNNN R3 to #<issue or pull request number>
```

- `Implements` names the rules the change brings.
- `Defers` names each rule that the change leaves out, with the existing issue or pull request that will bring it. A
  change that brings only some cases of a rule names the rule under `Defers`.
- Where no issue or pull request exists for a deferred rule, leave the rule out of the trailers and say in the
  description which rules wait for a change that has no issue yet.
- A change that brings no rule and leaves none out carries neither trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

A reviewer checks a change against the rules by the procedure in **Checking a change** in the `adr-authoring` skill:
<link to the skill at the version this repository pins, TBD>.
````

### Message to the user

I wrote ADR-0013 with the status `Proposed`. Tell me whether @example-security-architect has accepted it. It stays `Proposed` until O1 to O3 are settled.

Questions:

1. Which field of the HTTP response carries the reason code, such as a JSON body member or a header? R2 has a visible placeholder for it (O3). I did not invent a value.
2. Is `none` compared case-sensitively (O1)? I assumed it is, as RFC 7518 defines `alg` values. If `None` and `NONE` must also get `TOKEN_ALG_NONE`, say so and I will widen the term.
3. Does `TOKEN_ALG_NONE` win where an alg-none token has another defect, such as an expired claim (O2)? I assumed it does.
4. Do you want me to add the tests? No test covers the rule yet, so the record has no **Confirmation** section. Two tests would cover it:
   - a test in `internal/token/verify` for R1;
   - a handler test for R2.

   When they land, the record gains **Confirmation** entries. That edit is allowed on an accepted record. The change that adds the tests ends with `Implements: ADR-0013 R1, R2`.

Notes:

- I split the decision into two rules because the HTTP status cannot come from `internal/token/verify`. ADR-0012 R1 and R2 apply to that package. `verify` returns an error with the reason code, and the HTTP layer maps it to the response.
- I could not read the code. The layer tags `token` and `http` are unverified, so please check that the mapping from error to status sits in `internal/http/`.
- R2 constrains `internal/http/`, so I moved that path out of the no-layer list in `docs/adr/README.md` and mapped it to a new layer, `http`.
- ADR-0012 stays as it is.
