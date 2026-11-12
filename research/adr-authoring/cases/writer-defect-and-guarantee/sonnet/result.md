## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart, so
today it runs under Kubernetes.

Some operators run containers under Docker without Kubernetes. They need to trust a private certificate authority (CA)
for the HTTPS calls from token-gate to the identity provider. The platform base image, `ghcr.io/example/platform-base`,
states in its README that its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem`
file under `/tmp/cert` to the trust store of the container, runs the scripts in `/app/init.d`, and then runs its
arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
The repository ships a Compose example, and a CI job starts it on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker or Docker Compose starts from the token-gate image, in an
  environment with no Kubernetes cluster.
- **Compose example**: the Docker Compose project under `deploy/docker/`.

### Rules

#### Support under Docker

- **R1** (`image`, `server`). In a Docker deployment, token-gate starts and serves requests with its configuration given
  by environment variables and mounted files alone, and without access to a Kubernetes API.
- **R2** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate from its image, with its
  configuration given by environment variables and mounted files alone.

#### Verification in CI

- **R3** (`ci`). On every pull request, a CI job starts the Compose example, sends `GET /ready` to token-gate, and fails
  unless the response has HTTP status 200 within `<readiness timeout>`.

### Justification

An operator without a cluster can run token-gate only if it needs nothing that Kubernetes provides (R1), and a working
example shows how (R2). An example that no job runs stops working without notice, so the job runs it on every pull
request and calls the readiness endpoint (R3).

### Alternatives considered

- **A1. Support token-gate under Kubernetes only.** Rejected by R1: operators without a cluster could not run it.
- **A2. Ship the Compose example and start it only by hand.** Rejected by R3: a change to the image or to the
  configuration could break the example, and no pull request would show it.

## Consequences

Positive:

- An operator can run token-gate on a single host with Docker and a private CA, with no cluster.

Negative:

- The project supports two forms of deployment, and every pull request pays for the start of the Compose example (R3).

## Open points

- **O1.** R3 needs a time limit for `GET /ready`. The notes give none, and the record assumes that a ready token-gate
  answers with HTTP status 200. The owner decides the `<readiness timeout>` and confirms the status. This affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has two open items for you:

- **Owner:** the notes name no owner, so the field holds a placeholder. Which GitHub account owns this ADR?
- **R3, `GET /ready`:** what time limit should the job allow (`<readiness timeout>`)? I also assumed that a ready service answers with HTTP 200. Please confirm that. The record stays `Proposed` until O1 is settled.

The open question in the notes, whether the binary stays the entrypoint or the base entrypoint takes over, is not a decision, so it has no rule. It is a defect. The base image README states the contract: the entrypoint adds the certificates under `/tmp/cert` and then runs its arguments. The platform guide for service images says to keep that entrypoint and set the binary as `CMD`. `build/token-admin/Dockerfile` already does this with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains it. The record states only the base image contract, as a fact in Context. I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Contract it departs from:** the README of `ghcr.io/example/platform-base` and the platform guide for service images. The base entrypoint is kept, and the binary is set as `CMD`.
- **Fix:** in `build/token-gate/Dockerfile`, replace `ENTRYPOINT ["/usr/local/bin/token-gate"]` with `CMD ["/usr/local/bin/token-gate"]`. The base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, and the chart runs the Pod with a read-only root file system. So the same issue should add `emptyDir` volumes at those two paths to the chart.

If the team chose the current entrypoint on purpose, tell me. That would be a decision and would get a rule.

The reading guide already maps `docker` and `ci`, so I did not touch it. A change that implements R1 to R3 ends its commit message and pull request description with `Implements:` and, where it leaves a rule out, `Defers:` trailers. A `Defers` target must be an existing issue, so open one for any rule that waits.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-and-hmac-algorithms.md

````markdown
# Refuse tokens whose header names `none` or an HMAC algorithm

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

`internal/verify` verifies signatures with the `jwx` library. When `jwx` verifies a signature, it refuses a token whose
`alg` header is `none`. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key.
`internal/verify` passes `jwx` every key that the JWKS of an issuer holds. A JWKS that holds a symmetric key therefore
lets a holder of that key value sign tokens that token-gate accepts.

The security review considered accepting HMAC with a shared secret per issuer and rejected it.

## Decision

We will refuse a token whose header names the algorithm `none`, and a token whose header names an HMAC algorithm, each
with HTTP 401 and its own reason code.

### Terms

- **token**: a JWT that token-gate checks as the credential of a request.
- **`none` token**: a token whose `alg` header value is exactly the string `none`.
- **HMAC token**: a token whose `alg` header value is `HS256`, `HS384`, or `HS512`.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a `none` token with HTTP 401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses an HMAC token with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`,
  for every issuer and whatever keys the JWKS of the issuer holds. token-gate decides this from the `alg` header,
  before it verifies the signature.

### Implementation notes

Adds no requirement. Read the `alg` header in `internal/verify` before the call to `jwx`, so that the refusal does not
depend on the key set that `jwx` receives.

### Justification

A refusal with its own reason code tells an operator why a token failed (R1, R2). `jwx` refuses `none` only while it
verifies a signature, and it accepts HMAC algorithms when a symmetric key is in the key set, so the service decides the
response itself (R1, R2). A shared secret per issuer would make every verifier of an issuer able to mint tokens for it,
and a symmetric key in a published JWKS would expose that secret (R2).

### Alternatives considered

- **A1. Accept HMAC tokens with a shared secret per issuer.** Rejected by R2: the security review considered it and
  rejected it.
- **A2. Leave `none` to the refusal of `jwx`.** Rejected by R1: the response and the reason code `TOKEN_ALG_NONE` would
  depend on how `jwx` reports the failure.

## Consequences

Negative:

- A token whose `alg` header is `HS256`, `HS384`, or `HS512` is refused after the upgrade, also where the JWKS of its
  issuer holds a symmetric key that `internal/verify` accepted before (R2). An issuer that signs with HMAC has to
  switch to an asymmetric algorithm.

## Open points

- **O1.** The record assumes that algorithm names are case-sensitive, so a header value such as `None` or `hs256` is
  neither a `none` token nor an HMAC token. The security architect decides whether such values get the same refusal as
  their exact forms. This affects R1 and R2.
- **O2.** The record assumes that the `alg` check comes first, so a token that is also expired or malformed gets
  `TOKEN_ALG_NONE` or `TOKEN_ALG_SYMMETRIC`. The security architect decides the order against the other refusals of
  token-gate. This affects R1 and R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It needs two decisions, and one detail from you:

- **Owner:** the notes name no owner, so the field holds a placeholder. Which GitHub account owns this ADR?
- **O1:** do case variants such as `None` or `hs256` get the same refusal? I assumed they do not, because algorithm names are case-sensitive.
- **O2:** does the `alg` check come before the other refusals, such as an expired token? I assumed it does.

I kept the refusal of `none` as a rule, although `jwx` already refuses that algorithm when it verifies a signature. The notes decide the HTTP status and the reason code, and no record covers them. I defined the HMAC algorithms by their three names, because the notes list exactly those.

The record names one cost: after the upgrade, tokens signed with `HS256`, `HS384`, or `HS512` get 401, also where the JWKS of their issuer holds a symmetric key. I added no Confirmation section, because no check exists yet. When you add a test, add its entry to the record.

A change that implements R1 or R2 ends its commit message and pull request description with the `Implements:` trailer.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

The `crypto/tls` client of Go refuses TLS 1.1 and older by default, and token-gate sets no minimum TLS version of its
own. The security review decided that outgoing TLS connections of token-gate use TLS 1.2 or later. The Go default meets
that decision today, and a later Go release could change the default.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client. A TLS connection that
  token-gate accepts as the server is not one.
- **TLS 1.2 or later**: TLS 1.2 and TLS 1.3.

### Rules

#### TLS version

- **R1** (`verify`, `server`). An outgoing TLS connection of token-gate completes its handshake only at TLS 1.2 or
  later. Where the other side offers only TLS 1.1 or older, the handshake fails and token-gate sends no application data
  on the connection.

### Implementation notes

Adds no requirement. Set `MinVersion: tls.VersionTLS12` on each client `tls.Config`, so that a change to the default of
a later Go release does not lower the version. A test can start a TLS server that sets `MaxVersion: tls.VersionTLS11`
and check that the client fails the handshake.

### Justification

TLS 1.1 and older have known weaknesses, and a version floor keeps token-gate from talking to a server that offers
nothing better (R1). The rule states the floor as a requirement, so a change that lowers it fails the rule, even though
the Go default meets it today (R1).

### Alternatives considered

- **A1. Allow TLS 1.0 and 1.1 for identity providers that offer nothing newer.** Rejected by R1: the handshake with such
  a server fails.

## Consequences

Negative:

- token-gate cannot reach a server that offers only TLS 1.1 or older (R1). Nothing changes on upgrade, because the Go
  default already refuses those versions.

## Open points

- **O1.** The record assumes that the packages `internal/verify` and `internal/server` hold the code that opens
  outgoing TLS connections, and tags R1 with those layers. The owner confirms the packages, or names others. This
  affects the layer tags of R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two items need your answer:

- **Owner:** the notes name no owner, so the field holds a placeholder. Which GitHub account owns this ADR?
- **O1:** which packages open outgoing TLS connections? I tagged R1 with `verify` and `server` as an assumption. Please correct the tags if the code is elsewhere.

I made the decision a rule, although the Go default already meets it. The security architect chose the version floor for this system, and a rule lets a reviewer fail a change that lowers it. The record does not require an explicit `MinVersion`. Implementation notes recommends one, in case a later Go release changes the default. If you want the explicit setting required, tell me and I will add a rule.

The record has no Confirmation section, because no check exists yet. The Implementation notes describe a test that would serve as one. When it lands, add its entry to the record.
