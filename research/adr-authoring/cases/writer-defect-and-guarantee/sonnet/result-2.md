## Request 1

### File: docs/adr/0007-support-token-gate-under-docker.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

Operators run token-gate under Docker without a Kubernetes cluster. The repository ships token-gate as a container image
and a Helm chart, and has no Docker deployment example.

Under Docker, operators need token-gate to trust a private certificate authority (CA) for its HTTPS calls to the
identity provider. Every image of the platform builds on `ghcr.io/example/platform-base`. The README of that base image
states that its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under
`/tmp/cert` to the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments.
Operators mount the CA certificate under `/tmp/cert`, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, and we will ship a Compose example that CI starts on every pull request.

### Terms

- **Compose example**: the Docker Compose file under `deploy/docker/` that R1 requires, with the files it mounts.

### Rules

#### Running under Docker

- **R1** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate from its image, with configuration
  given by environment variables and mounted files only.
- **R2** (`server`). token-gate reads its configuration only from environment variables and files, and starts with no
  Kubernetes API, Kubernetes object, or service account available.

#### Checking the example

- **R3** (`ci`). A CI job runs on every pull request, starts the Compose example, and calls `GET /ready` on the started
  token-gate. The job fails when the response is not HTTP 200.

### Justification

Operators without Kubernetes need a supported way to run token-gate, and the Compose example gives them one that
depends on nothing but environment variables and files (R1, R2). A CI job that starts the example on every pull request
reports a change that stops it from starting (R3).

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Rejected by R1 and R2: operators without a Kubernetes cluster
  would have no supported way to run it.

## Consequences

Negative:

- The Compose example is a second deployment description next to the Helm chart. A change to the configuration of
  token-gate can break it, and the CI job of R3 then fails the pull request.
- Every pull request pays the time to start the Compose example (R3).

## Open points

- **O1.** R3 assumes that a ready token-gate answers `GET /ready` with HTTP 200. The architect, `example-architect`,
  confirms the status or names another. This affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two things block acceptance. Please give me the GitHub account of the owner. Please also ask `example-architect` to confirm O1, the status that a ready token-gate returns from `GET /ready`. I assumed HTTP 200.

I did not turn the open question about the entrypoint into a rule or an open point. The base image README and the platform guide for service images already settle it: keep the base entrypoint and set the binary as `CMD`. The `ENTRYPOINT` line in `build/token-gate/Dockerfile` departs from that contract, and nothing in the repository explains it. That makes it a defect. The `/tmp/cert` handling is a guarantee of the base image, so the record states it in Context as a fact, with no rule. I suggest this issue instead:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are ignored
- **Contract:** the README of `ghcr.io/example/platform-base` and the platform guide for service images say to keep `/usr/bin/entrypoint.sh` and set the service binary as `CMD`. `build/token-admin/Dockerfile` already does this with `CMD ["token-admin"]`.
- **Fix:** replace `ENTRYPOINT ["/usr/local/bin/token-gate"]` in `build/token-gate/Dockerfile` with a `CMD` for the binary. Add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart, because the entrypoint writes there and the root file system is read-only.

If the architect says the `ENTRYPOINT` is deliberate, tell me and I will turn it into a rule.

Once you open the issue, tell me its number. The pull request that fixes it needs no trailers, since it brings no rule of this record. The pull requests for R1 to R3 will end with `Implements: ADR-0007 R1, R2, R3`, or name any rule they leave out under `Defers` with an issue that exists.

## Request 2

### File: docs/adr/0007-refuse-none-and-hmac-token-algorithms.md

````markdown
# Refuse tokens whose algorithm is none or an HMAC algorithm

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an issuer
holds. A symmetric key in the JWKS of an issuer therefore lets a token signed with an HMAC algorithm pass verification.

## Decision

We will refuse a token whose algorithm is `none` with the reason code `TOKEN_ALG_NONE`, and a token whose algorithm is
`HS256`, `HS384`, or `HS512` with the reason code `TOKEN_ALG_SYMMETRIC`, each with HTTP 401.

### Terms

- **token**: the token that token-gate checks in a request.
- **algorithm of a token**: the value of the `alg` field in the header of the token.
- **symmetric algorithm**: `HS256`, `HS384`, or `HS512`.
- **refuses a token**: token-gate answers the request that carries the token with the HTTP status and the reason code
  that the rule names.
- **reason code**: the value that names why token-gate refused a token, carried in the response as
  `<where the response carries the reason code>`.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose algorithm is `none` with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`, for every issuer.
- **R2** (`verify`, `server`). token-gate refuses a token whose algorithm is a symmetric algorithm with HTTP 401 and the
  reason code `TOKEN_ALG_SYMMETRIC`, for every issuer, including an issuer whose JWKS holds a symmetric key.

### Implementation notes

Adds no requirement. Read the `alg` field of the header before `internal/verify` looks up a key, and map the two
outcomes to the status and reason codes of R1 and R2 in `internal/server`. Filtering symmetric keys out of the key set
alone does not meet R2, because the token must be refused with `TOKEN_ALG_SYMMETRIC`.

### Justification

A token whose algorithm is `none` has no signature to verify (R1). `jwx` already refuses it, and R1 fixes the status and
the reason code that the caller sees. A symmetric algorithm needs a key that is shared between the issuer and the
verifier, and the current code accepts such a token whenever the JWKS of the issuer holds a symmetric key (R2).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2. The security review considered and rejected it;
  the meeting notes record no reason (O2).

## Consequences

Negative:

- An issuer that signs its tokens with a symmetric algorithm cannot be used with token-gate. Its tokens get HTTP 401
  with `TOKEN_ALG_SYMMETRIC` (R2).
- A token whose algorithm is `none` was already refused by `jwx`. Its caller now gets the reason code `TOKEN_ALG_NONE`
  (R1).

## Open points

- **O1.** The notes do not say where the response carries the reason code, such as a body field or a header. The
  security architect, `example-security-architect`, names it. This affects R1 and R2.
- **O2.** The notes record no reason for rejecting HMAC with a shared secret per issuer. The security architect states
  it for A1 and the Justification. This affects R2.
- **O3.** The notes do not say how token-gate answers a token whose algorithm is another value, such as `None`, `NONE`,
  or an unknown name. R1 and R2 match the exact values `none`, `HS256`, `HS384`, and `HS512`. The security architect
  decides whether other values get a reason code of their own. This affects R1 and R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Please give me the GitHub account of the owner. Three open points block acceptance, and `example-security-architect` can answer all of them:

- **O1:** where the response carries the reason code.
- **O2:** why HMAC with a shared secret per issuer was rejected. The notes give no reason, so I did not invent one.
- **O3:** how token-gate answers algorithm values other than the four named, such as `NONE`.

R2 is a decision, not a fix. No record or contract settles it, and the current code departs from it: `internal/verify` passes every key of the JWKS to `jwx`, so an HS256 token passes when the JWKS holds a symmetric key. R1 is also a rule, even though `jwx` already refuses `none`, because the status and the reason code are the decision.

I left out **Confirmation**, because no check exists yet. I suggest a table-driven test in `internal/verify` with one `none` token, one token for each of the three symmetric algorithms, and a JWKS that holds a symmetric key. It should assert the status and the reason code. Once it exists, it can be added to the record as a Confirmation entry.

## Request 3

### File: docs/adr/0007-require-tls-1-2-for-outgoing-connections.md

````markdown
# Require TLS 1.2 or later for the outgoing TLS connections of token-gate

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, such as the HTTPS calls to the identity provider. The client of Go's
`crypto/tls` refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. The requirement
therefore holds today without any code in this repository.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate binary opens as a client, to any host, including a
  connection that a library called by token-gate opens.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate never completes the handshake of an outgoing TLS connection with a protocol
  version older than TLS 1.2, and no code of token-gate lowers the minimum protocol version of an outgoing TLS connection
  below TLS 1.2.

### Implementation notes

Adds no requirement. Leave `MinVersion` unset in the `tls.Config` of each outgoing client, or set it to
`tls.VersionTLS12`. The second form keeps R1 met if a later Go release changes the default.

### Justification

The default of Go's `crypto/tls` client meets the requirement today, and a later change could lower the minimum without
anyone noticing. R1 makes TLS 1.2 a requirement that a change can fail.

### Alternatives considered

- **A1. Set `MinVersion` below `tls.VersionTLS12` for an identity provider that offers only TLS 1.1 or older.** Rejected
  by R1.

## Consequences

Negative:

- An identity provider or another host that offers only TLS 1.1 or older cannot be reached by token-gate (R1).

## Open points

- **O1.** The notes do not say which package opens the outgoing TLS connections. R1 assumes the packages that hold the
  `verify` and `server` layers. The security architect, `example-security-architect`, or the owner names the package.
  This affects the layer tags of R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Please give me the GitHub account of the owner. O1 blocks acceptance: I could not see the code, so the layer tags of R1 are an assumption. Please tell me which package opens the outgoing connections.

I made this a rule even though Go's default already meets it. Security architect `example-security-architect` chose the requirement for this system, so it does not count as a mere guarantee of a dependency. The rule also covers a later change that lowers `MinVersion`.

I left out **Confirmation**, because no check exists yet. I suggest a test that dials a local TLS server capped at TLS 1.1 and expects the handshake to fail. It could also check that no `tls.Config` in the repository sets `MinVersion` below `tls.VersionTLS12`. Once it exists, it can be added to the record as a Confirmation entry.
