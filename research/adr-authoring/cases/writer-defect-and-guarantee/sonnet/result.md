## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, with a Compose example that CI starts

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart,
and until now it has run on Kubernetes. Some operators run it under Docker, with no Kubernetes cluster.

Under Docker, operators need to trust a private certificate authority (CA) for the HTTPS calls that token-gate makes to
the identity provider. The platform base image `ghcr.io/example/platform-base` provides this. Its README states that its
entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to
the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. Operators mount their
CA certificate under `/tmp/cert`, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone,
and we will ship a Compose example that a CI job starts on every pull request.

### Terms

- **Docker deployment**: a container that Docker or Docker Compose runs from the token-gate image, with no Kubernetes
  API reachable from the container.
- **Compose example**: the Compose files under `deploy/docker/`.
- **ready response**: a response with HTTP status 200 to `GET /ready` (see O1).

### Rules

#### Configuration

- **R1** (`server`). token-gate reads each of its settings from an environment variable or from a file, and it starts
  and serves `GET /ready` in a Docker deployment where no Kubernetes API is reachable.

#### Compose example and CI

- **R2** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate as a Docker deployment, and the
  Compose example gives token-gate its settings only as environment variables and mounted files.
- **R3** (`ci`). A workflow under `.github/workflows/` runs on every pull request, with no path or branch filter that
  skips a pull request. The workflow starts the Compose example, sends `GET /ready` to token-gate, and fails when it
  receives no ready response.

### Implementation notes

Adds no requirement. The CI job needs to retry `GET /ready` for a short time after the start, because the container
takes a moment to listen. Put the retry limit in the workflow.

### Justification

A Docker deployment works for an operator only if token-gate needs nothing from a cluster (R1) and the repository shows
how to run it (R2). A Compose example that no job starts drifts from the image, so the job on every pull request keeps
the example working (R3).

### Alternatives considered

- **A1. Ship the Compose example without a CI job.** Rejected by R3: an example that no job starts stops working
  unnoticed when the image or its settings change.

## Consequences

Negative:

- Every pull request pays for a CI job that starts a container (R3).
- A change that makes token-gate need a Kubernetes API, or a setting that is neither an environment variable nor a
  file, fails R1.

## Open points

- **O1.** The notes say the CI job "calls `GET /ready`" and give no success criterion. The record assumes HTTP status
  200. The architect, `example-architect`, decides whether another status counts. The answer affects R3 and the term
  **ready response**.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It cannot be `Accepted` until O1 is settled.

- **Owner:** the notes name the architect as the decider, not as the owner of the record. Who owns it? I left `<owner>` in the metadata.
- **O1:** I assumed that a ready response means HTTP 200. Please confirm it or give the status that counts.
- **The open question about the entrypoint is not in the record.** The base image README and the platform's guide for service images settle it: keep the base entrypoint and set the binary as `CMD`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains why. `build/token-admin/Dockerfile` already follows the guide with `CMD ["token-admin"]`. Restoring the contract is a fix, not a decision, so it gets no rule. The `/tmp/cert` behavior is a guarantee of the base image, so the record states it only as a fact in Context.
- **Proposed issue** (I did not open it, and the record names no issue):
  - Type: Bug.
  - Title: "token-gate image replaces the platform entrypoint, so certificates under /tmp/cert are not trusted".
  - Contract: the `platform-base` README says its entrypoint `/usr/bin/entrypoint.sh` adds the certificates under `/tmp/cert` to the trust store, runs `/app/init.d`, and runs its arguments. The platform's guide for service images says to keep that entrypoint and to set the service binary as `CMD`.
  - Departure: `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`.
  - Fix: replace that line with a `CMD` that runs the binary, as `build/token-admin/Dockerfile` does. Because the chart's Pod has a read-only root file system and the base entrypoint writes to the trust store, the same issue adds `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart. Check that the chart sets no `command` that overrides the entrypoint.
- **Guide:** `docs/adr/README.md` already maps `docker`, `ci`, and `server`, so it needs no change. The pull request that brings the Compose example and the CI job should end with the `Implements: ADR-0007 R1, R2, R3` trailer once the record is accepted. The entrypoint fix carries no trailer.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-a-symmetric-algorithm.md

````markdown
# Refuse a token whose algorithm is none or symmetric with HTTP 401 and a reason code

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

`internal/verify` verifies the signature of a token with the `jwx` library. `jwx` refuses a token whose `alg` is `none`
when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key, and
`internal/verify` passes it every key that the JWKS of an issuer holds. A symmetric key in the JWKS of an issuer
therefore makes `jwx` accept a token signed with an HMAC algorithm. A refusal by `jwx` carries no reason code that tells
a client which of the two cases occurred.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and a
token whose header names `HS256`, `HS384`, or `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`.

### Terms

- **alg-none token**: a token whose header parameter `alg` equals `none`, compared without regard to case (see O2).
- **symmetric-algorithm token**: a token whose header parameter `alg` is `HS256`, `HS384`, or `HS512`.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses an alg-none token with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a symmetric-algorithm token with HTTP 401 and the reason code
  `TOKEN_ALG_SYMMETRIC`, also where the JWKS of the issuer of the token holds a symmetric key.

### Implementation notes

Adds no requirement. Read the `alg` header before the token reaches `jwx`, and refuse it there. Filtering the symmetric
keys out of the key set would leave a symmetric-algorithm token without a reason code of its own, so it would not meet
R2.

### Justification

`jwx` already refuses `none` at signature verification, but it gives no reason code, so R1 makes the refusal and its
code part of this service. `jwx` accepts a symmetric-algorithm token whenever a JWKS holds a symmetric key, so without
R2 the acceptance depends on the content of an issuer's JWKS, which this service does not control (R2). A separate code
for each case lets a client and an operator tell the two refusals apart (R1, R2).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2. The notes of the security review record the
  rejection and give no reason.

## Consequences

Positive:

- A symmetric key added to the JWKS of an issuer does not make token-gate accept an HMAC token.

Negative:

- An issuer that signs its tokens with `HS256`, `HS384`, or `HS512` gets HTTP 401 for every token (R2).

## Open points

- **O1.** The notes give the HTTP status and the reason codes, and not where a response carries the reason code, such as
  a body field or a header. The security architect, `example-security-architect`, decides. The answer affects R1 and R2.
- **O2.** The record assumes that `alg` is compared with `none` without regard to case, so `None` and `NONE` also count
  as alg-none tokens. The security architect decides whether the comparison is exact. The answer affects R1 and the term
  **alg-none token**.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has two open points.

- **Owner:** who owns the record? I left `<owner>` in the metadata.
- **O1:** how does a 401 carry the reason code (body field, header, or the format that existing reason codes use)? I did not see this and did not guess it.
- **O2:** I assumed a case-insensitive match on `none`, because a stricter reading would let `None` through to `jwx`. Please confirm.
- **Rejected alternative:** A1 records that HMAC with a shared secret per issuer was rejected. The notes give no reason for the rejection, so the record gives none either. Please send the reason.
- **Layer tags:** I tagged R1 and R2 with `verify` and `server`, because `internal/verify` decides and I assume `internal/server` writes the 401. Correct me if the response is built elsewhere.
- **Dependency guarantee:** `jwx` already refuses `none`. I still made it a rule, because the reason code `TOKEN_ALG_NONE` is a decision of this service.
- **Trailers:** a change that implements these rules ends with `Implements: ADR-0007 R1, R2`.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate calls other services over TLS, such as the identity provider of an issuer. The `crypto/tls` client of Go
refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. The minimum therefore comes
from the Go version that builds token-gate, and no rule fixes it. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection for which token-gate is the TLS client, whichever service it calls.

### Rules

#### Minimum version

- **R1** (`verify`, `server`). token-gate fails the handshake of an outgoing TLS connection, and sends no application
  data on it, where the other side supports only TLS 1.1 or older.
- **R2** (`verify`, `server`). No `tls.Config` that token-gate uses for an outgoing TLS connection sets `MinVersion`
  below `tls.VersionTLS12`.

### Implementation notes

Adds no requirement. A test for R1 can start an `httptest` TLS server limited to TLS 1.1 and expect the client call to
fail. Setting `MinVersion` to `tls.VersionTLS12` explicitly is allowed, and leaving it unset also meets R1 and R2 as
long as the Go version of the build refuses TLS 1.1 by default.

### Justification

R1 states the outcome that the security architect decided. R2 keeps a later change from lowering the minimum, because
the default of the Go version alone does not stop a `tls.Config` from allowing TLS 1.1 or older (R2). TLS 1.0 and TLS
1.1 are deprecated by RFC 8996 (R1, R2).

### Alternatives considered

- **A1. Rely on the default of `crypto/tls` with no rule.** The default holds today, but it follows the Go version, and
  nothing would fail a change that lowers the minimum.

## Consequences

Negative:

- A service that supports only TLS 1.1 or older, such as an old identity provider, cannot be called by token-gate (R1).
- The decision covers only connections where token-gate is the TLS client. A minimum version for a TLS listener of
  token-gate, if it has one, needs its own decision.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, with no open points.

- **Owner:** who owns the record? I left `<owner>` in the metadata.
- **Status:** the notes record the decision, not the team's sign-off. Tell me when the team has signed off, and I will set `Accepted` and add the Date.
- **Why a rule when Go already does this:** the security architect chose this requirement for the service. The Go default is a property of the toolchain version, so the record states the requirement as R1, and R2 stops a later `tls.Config` from lowering it.
- **Layer tags:** I tagged R1 and R2 with `verify` and `server`, because I don't know which packages open the outgoing connections. Tell me if another path of the guide holds them, and I will change the tags.
- **Scope:** the record covers only connections where token-gate is the client. I did not add a rule for a TLS listener.
- **Trailers:** a change that implements these rules ends with `Implements: ADR-0007 R1, R2`.
