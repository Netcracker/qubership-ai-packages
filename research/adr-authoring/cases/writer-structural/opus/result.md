## Request 1

### File: docs/adr/0012-keep-token-packages-free-of-http-imports.md

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

The packages under `internal/token/` parse and verify the token of each request. The HTTP server, its middleware, and
its handlers are in the packages under `internal/http/`. Both are part of the service that `cmd/token-gate` builds.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It uses the token packages and has to
build without the HTTP server.

The depguard rule `token-no-http` in `.golangci.yml` denies imports of `net/http` and of the packages under
`internal/http/` in the packages under `internal/token/`. `.github/workflows/ci.yml` runs golangci-lint on every pull
request. depguard checks the import declarations of each file. It does not check the packages that an imported package
imports in turn.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it, such as
  `internal/token/parse` and `internal/token/verify`. Its files include its `_test.go` files, in the package itself and
  in its external test package (O1).
- **HTTP package**: the package `net/http`, every package whose import path starts with `net/http/`, and every package
  of the module `example/token-gate` whose directory is `internal/http/` or a directory under it.
- **imports**: a Go file imports a package when one of its import declarations names that package. A package that a
  file reaches only through another package it imports does not count (O2).

### Rules

#### Imports of the token packages

- **R1** (`token`). No file of a token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`. golangci-lint runs it on every pull request in
  `.github/workflows/ci.yml`, and the lint job fails on an import that the rule denies.

### Implementation notes

Adds no requirement. Where a token package needs to report an outcome that the HTTP server turns into a status code,
return an error or a result type that the token package defines, and map it to a status code in `internal/http`. Where a
token package needs data from a request, such as a header value, pass it in as a string or as a type of the token
package. Where a token package needs to fetch keys over the network, accept an interface that the token package defines,
and implement it outside `internal/token/`.

### Justification

`tokencheck` builds the token packages, so it builds without the HTTP server only if no token package imports one (R1).
`net/http/httptest` and `net/http/httputil` import `net/http` themselves, so the term **HTTP package** covers every
package whose import path starts with `net/http/` (R1). A lint rule that runs on every pull request finds a new import
before it merges, where a failed build of `tokencheck` would find it only after (R1).

### Alternatives considered

- **A1. Accept an `*http.Request` or return an HTTP status code from `internal/token/verify`.** Rejected by R1: the
  import of `net/http` puts the HTTP stack into the build of `tokencheck`.
- **A2. Keep the files of a token package that need `net/http` behind a build tag that `tokencheck` leaves out.**
  Rejected by R1: the files still import `net/http`, and every other build of the token packages still includes it.

## Consequences

Negative:

- Each new outcome of token verification that the service reports with its own status code takes a change in a token
  package and a change in `internal/http`, which maps the outcome to the status code.
- A token package cannot fetch keys over HTTP itself. The service and `tokencheck` each provide the code that fetches
  them.

## Open points

- **O1.** Do the `_test.go` files of a token package fall under R1? The record assumes that they do. The other answer
  is that they do not, because `go build` leaves test files out of `tokencheck`, and a test could then use
  `net/http/httptest`. Whether `token-no-http` checks test files depends on its settings in `.golangci.yml`, which the
  answer has to match. @example-architect decides. Affects R1 and the term **token package**.
- **O2.** Does R1 cover an HTTP package that a token package reaches through a package outside `internal/token/`, such
  as a third-party JOSE library that imports `net/http`? The record assumes that it does not, which matches what
  depguard checks. The other answer covers such packages too, so that `tokencheck` never builds `net/http`, and it
  needs a check other than depguard, such as a test that runs `go list -deps` on each token package.
  @example-architect decides. Affects R1 and the term **imports**.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. From ADR-0012 on, a record states its
requirements as numbered rules, and each change to the code that a record governs is checked against them.

## Layers

Each rule names the layer of the code it constrains, such as `(token)`. A layer covers these paths:

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies tokens | `internal/token/` |
| `http` | Runs the HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Holds the entry points of the programs, such as `cmd/token-gate` | `cmd/` |
| `build` | Declares the module, the lint settings, and the CI workflows | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/adr/` and `AGENTS.md`.

A change that adds a file that no layer and no entry of that list covers adds its path to one of them.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not. ADR-0001 to ADR-0011 have
no numbered rules, and a check reports them as unchecked.

## Reading a record before you change code

Before you change code in a layer, read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each
binding record with a rule in that layer. **Implementation notes** recommends a way to meet the rules and adds no
requirement. Anything that no rule states is your choice.

## Trailers

A change to a file in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0013 R1 to #208
```

- `Implements` names each rule that the change brings in full.
- `Defers` names each rule that the change leaves out or brings only in part, with the issue or pull request that will
  bring the rest. The issue or pull request exists before the change names it.

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer. In a pull request with
several commits, each commit carries the trailers of its own part, and the description carries them for the whole
change.

## Checking a change

A reviewer checks a change against the rules as
[Checking a change in the adr-authoring skill](<URL of the adr-authoring skill at the pinned version>#checking-a-change)
describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

## Architecture decision records

The records in `docs/adr/` govern the code under the paths that the guide in `docs/adr/README.md` maps to layers. Read
the guide before you change that code. End the commit message and the pull request description of such a change with
the `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012 as `Proposed` with one rule. R1 says no file of a package under `internal/token/` imports `net/http`, a package under `net/http/`, or a package under `internal/http/`. Its confirmation is the existing depguard rule `token-no-http`.

Two open points keep the record from being accepted. @example-architect needs to settle both:

- **O1:** Do the `_test.go` files of the token packages fall under R1? I assumed they do. Please also check that `token-no-http` in `.golangci.yml` checks test files the same way. I couldn't read that file.
- **O2:** Does R1 also cover `net/http` pulled in through a package outside `internal/token/`, such as a third-party library? I assumed it doesn't, because that's all depguard checks. Covering it would need a second check, such as a test that runs `go list -deps`.

Once both are answered, I'll update R1 and the terms, set the status to `Accepted`, and add the Date heading.

The team agreed to the reading guide and the trailers, so I added `docs/adr/README.md` and a paragraph in `AGENTS.md` that points to it. Three questions about the guide:

1. **Skill link:** Which URL should it use for "Checking a change"? The repository doesn't use APM, so the link has to point at the adr-authoring skill on GitHub at a fixed version. I left a visible placeholder, which needs filling in before merge.
2. **Other paths:** Are there files outside the mapped paths, such as a root `README.md`, `LICENSE`, or a `Makefile`? A change to an unmapped file is a guide error, so each one needs a layer or a place on the list of paths that belong to no layer.
3. **Layer for `cmd/`:** I mapped all of `cmd/` to one layer, `cmd`, so `cmd/tokencheck` is covered when it lands. Is that what you want?

ADR-0001 to ADR-0011 stay as they are. They have no numbered rules, so a check reports them as unchecked. This change only touches `docs/adr/` and `AGENTS.md`, which belong to no layer, so its commit carries no trailers.

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

- Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-keep-token-packages-free-of-http-imports.md):
  R1 keeps `net/http` out of `internal/token/verify`, so the status code of R1 comes from code in `internal/http`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. `internal/token/parse` parses a token, and
`internal/token/verify` verifies it. A JOSE header names the signing algorithm in its `alg` parameter. The value `none`
marks an unsecured token, which carries no signature (RFC 7519, section 6), so any client can write one with any claims.

`internal/token/verify` holds a check for the algorithm `none`. No test covers it.

## Decision

We will refuse every request whose token names the algorithm `none` in its header, with HTTP 401 and the reason code
`TOKEN_ALG_NONE`.

### Terms

- **token package**: as ADR-0012 defines it.
- **alg-none token**: a token whose JOSE header has the parameter `alg` with the value `none`, written in any mix of
  uppercase and lowercase letters, such as `none`, `None`, and `NONE` (O1).
- **refuses**: the service answers the request with HTTP status 401 and the reason code that the rule names, and policy
  evaluation does not receive the request. A token package meets this by returning an error that carries the reason
  code, and code in `internal/http` turns that error into the response.

### Rules

#### Tokens with the algorithm `none`

- **R1** (`token`, `http`). The service refuses a request whose token is an alg-none token, with the reason code
  `TOKEN_ALG_NONE`. The reason code is `TOKEN_ALG_NONE` also where the token would fail another check, such as a
  check of its expiry (O2). The response carries the reason code where the service's other refusals carry theirs (O3).

### Implementation notes

Adds no requirement. Compare `alg` before looking up a key or checking a signature, so that no path in
`internal/token/verify` reaches signature verification with an alg-none token. A table test in `internal/token/verify`
that covers `none`, `None`, and `NONE`, together with a handler test in `internal/http` that checks the status and the
reason code, covers R1. Name both under **Confirmation** when they land.

### Justification

An alg-none token carries no signature, so a service that accepted one would act on claims that anyone can write (R1).
The request then has no valid credentials, which is the case HTTP 401 reports (R1). A reason code of its own lets a log
query or an alert find alg-none tokens apart from expired or malformed ones, and reporting it ahead of other failures
keeps those queries from missing a token that also failed another check (R1).

### Alternatives considered

- **A1. Accept an alg-none token as an unsecured JWT, as RFC 7519 section 6 allows.** Rejected by R1.
- **A2. Refuse an alg-none token with the reason code of another failed verification, such as an invalid signature.**
  Rejected by R1: the reason code is `TOKEN_ALG_NONE`.

## Consequences

Negative:

- No client can authenticate with an unsecured JWT, whatever its claims (R1).
- A client that sends an alg-none token gets HTTP 401 with `TOKEN_ALG_NONE`, also where the token is expired or fails
  another check (R1).

## Open points

- **O1.** Does the term **alg-none token** cover `alg` values that differ from `none` only in letter case, such as
  `None` and `NONE`? The record assumes that it does. The other answer covers only the exact value `none`, which RFC 7515
  treats as case-sensitive, and leaves the other spellings to the handling of unknown algorithms.
  @example-security-architect decides. Affects R1 and the term **alg-none token**.
- **O2.** Does `TOKEN_ALG_NONE` win over the reason code of every other check that the token fails? The record assumes
  that it does. The other answer checks the algorithm after a named set of checks, such as the parsing of the payload,
  and reports their reason codes first. @example-security-architect decides. Affects R1.
- **O3.** Where does the response carry `TOKEN_ALG_NONE`? The record assumes the place where the service's other
  refusals carry their reason codes. The other answers name a place, such as a field of the JSON body or a response
  header, which then becomes part of the contract. @example-security-architect decides. Affects R1.
````

### Message to the user

I added ADR-0013 as `Proposed` with one rule. R1 says a request whose token names `alg: none` gets HTTP 401 with the reason code `TOKEN_ALG_NONE`, and policy evaluation never receives it. The rule is tagged with two layers:

- **`token`:** `internal/token/verify` returns an error that carries the reason code.
- **`http`:** code in `internal/http` turns that error into the 401. ADR-0012 R1 keeps `net/http` out of `internal/token/verify`, so the status code can't come from there.

Three open points keep the record from being accepted. @example-security-architect needs to settle each one:

- **O1:** Do `None` and `NONE` count as `none`? I assumed they do.
- **O2:** Does `TOKEN_ALG_NONE` win over every other failure of the same token, such as an expired token? I assumed it does.
- **O3:** Where in the response does the reason code go? I assumed it goes wherever the service's other refusals put theirs. I couldn't see that code, so please name the field or header if it should be fixed in the contract.

**Missing tests:** no test covers R1 yet, so **Confirmation** is left out. A test of R1 doesn't need a rule of its own: R1 is the requirement, and the test joins **Confirmation** when it lands. An accepted record can take that addition. I suggest you open an issue for it:

- **Type:** Task
- **Title:** "Test the refusal of tokens with the algorithm `none` (ADR-0013 R1)"
- **Scope:** a table test in `internal/token/verify` and a handler test in `internal/http` that checks the 401 and the reason code

Please also check that `internal/http` already turns the verify error into a 401 with `TOKEN_ALG_NONE`. I could only confirm that the check exists in `internal/token/verify`.

The change that adds the tests should end with `Implements: ADR-0013 R1`. Until then, a change in those layers that leaves R1 unmet can name it under `Defers:` with that issue's number. This record change only touches `docs/adr/`, so its commit carries no trailers.
