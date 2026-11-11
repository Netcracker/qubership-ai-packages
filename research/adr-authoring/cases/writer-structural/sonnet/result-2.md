## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports from `internal/http` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

- Architect, @example-architect: approves R1 to R3.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The packages under `internal/token/` parse and verify tokens. The command-line tool `tokencheck`, which the team plans,
will verify tokens offline with them and has to build without the HTTP server. A package under `internal/token/` that
imports `internal/http/` or `net/http` would bring HTTP code into that build. The depguard rule `token-no-http` in
`.golangci.yml` already checks both imports, and CI runs it.

## Decision

We will keep every package under `internal/token/` free of imports from `internal/http/` and of `net/http`.

### Terms

- **token code**: every `.go` file in a directory under `internal/token/`, test files included.
- **import**: an import declaration in a Go file. A package that a dependency of the file imports does not count.

### Rules

#### Imports of the token code

- **R1** (`token`). No token code imports a package whose import path is `example/token-gate/internal/http` or starts
  with `example/token-gate/internal/http/`.
- **R2** (`token`). No token code imports the package `net/http`.

#### The check

- **R3** (`build`). `.golangci.yml` defines a depguard rule named `token-no-http` that reports each import that R1 or R2
  forbids, and `.github/workflows/ci.yml` runs `golangci-lint` with that file on every pull request.

### Confirmation

- **R1**, **R2**: the depguard rule `token-no-http`, which the `golangci-lint` run in CI executes on every pull request,
  reports each import that R1 or R2 forbids.

### Implementation notes

Adds no requirement. Code in `internal/http/` maps the errors of the token packages to HTTP statuses, so a token package
returns an error and leaves the status to its caller. Put `tokencheck` under `cmd/tokencheck`.

### Justification

`tokencheck` has to build without the HTTP server, and an import from `internal/http/` brings the server's packages into
that build (R1). An import of `net/http` brings the HTTP package of the standard library into the token packages, which
then depend on HTTP code at all (R2). A depguard rule in CI fails the pull request that adds either import, so a
reviewer does not have to catch it (R3).

### Alternatives considered

- **A1. Import status codes or helpers from `internal/http/` into `internal/token/verify`.** Rejected by R1: the build
  of `tokencheck` would include the HTTP server.
- **A2. Import `net/http` in `internal/token/verify` for its status constants.** Rejected by R2: the token packages
  would then depend on the HTTP package of the standard library.

## Consequences

Negative:

- Token code cannot use `net/http` names such as `http.StatusUnauthorized` (R2).
- A token package can still reach HTTP code through a third-party dependency, because R1 and R2 cover direct imports
  only (Terms, **import**).

## Open points

- **O1.** Does `token-no-http` check `_test.go` files? R1 and R2 cover test files, and the Confirmation relies on the
  rule checking them. If `.golangci.yml` excludes them, either the configuration changes so that the rule covers test
  files, or token code is narrowed to non-test files. @example-architect decides. Affects R1, R2, R3.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory number their rules. A change to code that a record governs is checked against those
rules.

## Layers

Each layer has a name that the rules use in their tags.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying tokens, with the tests beside that code | `internal/token/` |
| `http` | HTTP server, middleware, and handlers, with the tests beside that code | `internal/http/` |
| `service` | Entry points of the service and its tools | `cmd/` |
| `build` | CI and lint configuration | `.golangci.yml`, `.github/workflows/ci.yml` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `go.mod`, and `go.sum`. A path stays outside the layers only
while no rule constrains it. A change that adds a file that neither this table nor that list covers extends one of
them.

## Which records bind a change

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not. A record without numbered rules, such as ADR-0001 to ADR-0011, is not checked against a change.

## What to read before you write code

Read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each binding record whose rules sit in the
layers you change. A rule is cited with its record, as `ADR-0012 R1`. Anything no rule states is your choice.

## Trailers

A change to code under the paths of the layers ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R3 to #123
```

- `Implements` names the rules that the change brings, every case of each.
- `Defers` names each rule that the change leaves out, with the issue or pull request that will bring it. The target
  must exist.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

The procedure for checking a change against the rules is **Checking a change** in the
[adr-authoring skill](<URL of the adr-authoring skill at the pinned version>).
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that it describes.
````

### Message to the user

I wrote ADR-0012, a reading guide at `docs/adr/README.md`, and a bullet in `AGENTS.md` that points at the guide. I used the commitment you gave: every change to code under the mapped paths ends with the `Implements:` and `Defers:` trailers.

- **Status:** The record is `Proposed` with no Date heading. After @example-architect approves it and the open point is closed, set the status to `Accepted` and add the Date heading with that day.
- **Question 1:** What URL and pinned version should the guide's link to **Checking a change** use? The repository doesn't use APM, so the link has to point at the skill on GitHub. It holds a visible placeholder, `<URL of the adr-authoring skill at the pinned version>`.
- **Question 2 (O1):** Does `token-no-http` check `_test.go` files? I wrote R1 and R2 to cover test files, and the record stays `Proposed` until you answer.
- **Choices to confirm:**
  - R2 names the package `net/http` only, not subpackages such as `net/http/httptest`.
  - R1 and R2 cover direct imports only, and the Negative consequence says so.
  - In the guide, I mapped `cmd/` to a `service` layer so that `cmd/tokencheck` is covered later. I also put the two CI files in a `build` layer, because R3 constrains them.
  - I wrote A1 and A2 under **Alternatives considered** from the stated reasons. Delete them if the meeting did not discuss them.
- **Existing records:** ADR-0001 to ADR-0011 have no numbered rules, so a checker lists them as unchecked.
- **Trailers:** This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer, so its commit message needs neither trailer.

## Request 2

### File: docs/adr/0013-refuse-token-with-algorithm-none.md

````markdown
# Refuse a token whose header names the algorithm `none` with HTTP 401 and `TOKEN_ALG_NONE`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports from `internal/http` and `net/http`](0012-token-packages-without-http.md):
  R2 forbids `net/http` in `internal/token/verify`, so R1 returns an error and R2 sets the status in `internal/http`.
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` declares that no signature protects it. The service checks the token of
each request before policy evaluation, and `internal/token/verify` holds the verification.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, and the check will sit in `internal/token/verify`.

### Terms

- **reason code**: the identifier `TOKEN_ALG_NONE` for this refusal. R2 states where a response carries it.

### Rules

#### Refusal of the algorithm `none`

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE` for a token
  whose header names the algorithm `none`.
- **R2** (`http`). The server answers a request with HTTP status 401 and the reason code `TOKEN_ALG_NONE` in
  `<reason code location>` when the verification of the token of that request returns the error of R1.

### Implementation notes

Adds no requirement. The error of R1 carries the reason code, and the code in `internal/http/` maps that error to the
status and the response of R2. Cover R1 with a table test in `internal/token/verify` and R2 with a handler test in
`internal/http/`.

### Justification

A token that names `none` declares that no signature protects it, so nothing shows who issued it, and the service must
not accept it (R1, R2). A distinct reason code lets a caller and the logs tell this refusal from other token failures
(R1, R2). The check sits in `internal/token/verify` with the other verification of the token (R1).

### Alternatives considered

- **A1. Accept a token whose header names `none` and leave the decision to policy evaluation.** Rejected by R1 and R2:
  the token carries no signature, so policy evaluation would act on claims that nobody vouches for.

## Consequences

Negative:

- A client that sends a token with the algorithm `none`, such as a development setup that issues unsigned tokens, gets
  HTTP 401 (R2).

## Open points

- **O1.** Where does the response carry the reason code: a field of the response body, a response header, or both? The
  security architect decides. Affects R2.
- **O2.** Does a header that names `None` or `NONE` count as naming the algorithm `none`? The answers are that only the
  exact value `none` counts, which is how R1 reads now, or that any letter case counts. The security architect decides.
  Affects R1, R2.
````

### Message to the user

I wrote ADR-0013 as a separate record from ADR-0012. The two have different owners and different reasons to change, and ADR-0012 stays as it is. ADR-0013 links ADR-0012 because its R2 shapes this record: `internal/token/verify` cannot import `net/http`. So R1 has `verify` return an error with the reason code, and R2 has `internal/http` set the 401.

- **Status:** The record is `Proposed`, with no Date heading, until @example-security-architect approves it and both open points are closed.
- **Question 1 (O1):** Where does the 401 response carry `TOKEN_ALG_NONE`: a body field, a header, or both? R2 holds the placeholder `<reason code location>` until you answer.
- **Question 2 (O2):** Does `None` or `NONE` count as the algorithm `none`? R1 reads the exact value `none`, which follows your wording. Security may prefer any letter case.
- **Confirmation:** The record has no **Confirmation** section because no test covers R1 or R2. The Implementation notes suggest a table test in `internal/token/verify` and a handler test in `internal/http/`. When those tests land, add the entries to **Confirmation** in this record. An accepted record allows that edit.
- **Trailers:** I assumed the check and the 401 mapping already exist, since you described where the check sits. This change adds only the record, so its commit message needs neither trailer. If either piece is missing, open an issue for it, and the change that adds it will name the issue under `Defers`.
- **Alternatives:** A1 is the reverse of the decision, written so a checker can recognize it in code. Delete it if you prefer.
