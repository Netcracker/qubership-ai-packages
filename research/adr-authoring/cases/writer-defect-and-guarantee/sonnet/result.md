## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, with a Compose example that CI starts

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate ships as a container image and a Helm chart. Operators who run the image under Docker without Kubernetes
configure it through the container's environment and mounted files.

These operators need to trust a private CA for the HTTPS calls from token-gate to the identity provider. The README of
the platform base image `ghcr.io/example/platform-base` states that its entrypoint, `/usr/bin/entrypoint.sh`, adds every
certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container. Operators mount
the certificate of their CA there, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, ship a Compose example for it under `deploy/docker/`, and start that example in CI on every pull request.

### Terms

- **ready**: the state in which `GET /ready` returns HTTP 200.
- **Compose example**: the Compose project under `deploy/docker/` that R2 requires.

### Rules

#### Running under Docker

- **R1** (`server`, `docker`). Under Docker without Kubernetes, token-gate becomes ready when its configuration comes
  from environment variables and from files mounted into the container, and from no other source.

#### The Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate.
- **R3** (`ci`). On every pull request, a CI job starts the Compose example and calls `GET /ready`. The job fails
  unless token-gate is ready.

### Justification

Operators without Kubernetes need a supported way to run token-gate (R1). A Compose example gives them a working
starting point (R2), and the CI job keeps that example and the readiness of the service from breaking unnoticed (R3).

## Consequences

Negative:

- Every pull request runs a Compose job, and a pull request cannot merge while the Compose example fails to start
  token-gate (R3).
- The Compose example is an artifact the team maintains alongside the Helm chart (R2).

## Open points

- **O1.** The notes do not name the success status of `GET /ready`. The record assumes HTTP 200, in the definition of
  **ready**. The architect confirms the status. It affects R1 and R3.
````

### Message to user

I wrote the record as `docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md`, with status `Proposed`.

- **Owner:** the Owner heading holds the placeholder `<owner GitHub account>`. Who owns this record?
- **O1 blocks acceptance:** the notes don't give the success status of `GET /ready`, so I assumed HTTP 200. Please confirm it.
- **Layer tags:** I tagged R1 `server` and `docker` because I couldn't see where configuration is read. Correct the tag if that code lives elsewhere.

Your open question, whether to keep the binary as the entrypoint, is not a decision, so the record has no rule or open point for it. The platform base image and the platform's guide for service images already settle it:

- The base README says its entrypoint, `/usr/bin/entrypoint.sh`, adds the certificates under `/tmp/cert`, runs `/app/init.d`, and then runs its arguments.
- The guide says to keep that entrypoint and set the binary as `CMD`.
- `build/token-admin/Dockerfile` already does this with `CMD ["token-admin"]`.
- `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. No record or issue explains the line.

So the Docker CA setup you describe fails for token-gate today. I suggest this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Contract departed from:** the platform-base README and the platform guide for service images, as above.
- **Fix:**
  - In `build/token-gate/Dockerfile`, replace the `ENTRYPOINT` line with `CMD ["token-gate"]`.
  - In the chart, add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. The base entrypoint writes there, and the Pod has a read-only root file system.

If the `ENTRYPOINT` is deliberate, tell me and I will add a rule for it. A change that implements R2 or R3 should end its commit message and pull request description with the `Implements` trailer once the record is accepted.

## Request 2

### File: docs/adr/0007-refuse-tokens-whose-algorithm-is-none-or-hmac.md

````markdown
# Refuse a token whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when
the key set holds a symmetric key. `internal/verify` passes `jwx` every key that the JWKS of an issuer holds, so a
symmetric key in that JWKS makes a token signed with an HMAC algorithm verify.

## Decision

We will refuse a token whose header names the algorithm `none` or an HMAC algorithm, each with HTTP 401 and its own
reason code.

### Terms

- **HMAC algorithm**: `HS256`, `HS384`, or `HS512`, and no other algorithm.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). A token whose header `alg` is an HMAC algorithm is refused with HTTP 401 and the reason
  code `TOKEN_ALG_SYMMETRIC`, also where the JWKS of its issuer holds a symmetric key.

### Implementation notes

Adds no requirement. `jwx` refuses `none` with its own error, so `internal/verify` can read the header `alg` before it
calls `jwx` and return `TOKEN_ALG_NONE` itself. The same check can return `TOKEN_ALG_SYMMETRIC`, which also keeps a
symmetric key in a JWKS from making a token verify.

### Justification

`jwx` already refuses `none`, but its refusal carries no reason code, and R1 fixes the answer that callers get. `jwx`
accepts an HMAC algorithm whenever a symmetric key is among the keys that `internal/verify` passes it, and R2 removes
that case.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: a token signed with an HMAC algorithm is refused
  for every issuer.

## Consequences

Negative:

- A token signed with an HMAC algorithm is refused with `TOKEN_ALG_SYMMETRIC`, so an issuer that signs this way and
  publishes a symmetric key in its JWKS no longer authenticates (R2).

## Open points

- **O1.** The notes do not say where the response carries a reason code. The record assumes the place where the
  responses of token-gate already carry theirs. The security architect confirms it. It affects R1 and R2.
````

### Message to user

I wrote the record as `docs/adr/0007-refuse-tokens-whose-algorithm-is-none-or-hmac.md`, with status `Proposed`.

- **Owner:** the Owner heading holds the placeholder `<owner GitHub account>`. Who owns this record?
- **O1 blocks acceptance:** where does a 401 response carry the reason code? I assumed the place that existing reason codes use.
- **Reason for rejecting HMAC:** the notes only say it was considered and rejected. What was the security reason? I'd add it to the Justification and A1.
- **Layer tags:** I tagged both rules `verify` and `server`, assuming `internal/verify` decides and `internal/server` writes the response. Correct the tags if that's wrong.
- **Not covered by the notes:**
  - R1 matches the lowercase `none`. A header with `None` or `NONE` falls outside it.
  - The notes don't say which reason code wins when a token also fails another check, such as expiry.

Tell me how you want either handled and I'll add a rule.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, such as the HTTPS calls to an identity provider. The `crypto/tls` client
of Go refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host. A
  connection that token-gate accepts as a server is not one.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate opens an outgoing TLS connection only where the handshake negotiates TLS 1.2
  or later. A handshake with a server that supports only TLS 1.1 or older fails.

### Implementation notes

Adds no requirement. A client `tls.Config` that leaves `MinVersion` unset meets R1 under the Go default, which refuses
TLS 1.1 and older. A test can start a local TLS server limited to TLS 1.1 and check that the outgoing call fails.

### Justification

The security review decided R1. The Go default already refuses older versions, so token-gate needs no setting of its own
to meet it.

## Consequences

Negative:

- token-gate cannot reach an identity provider, or any other host, that supports only TLS 1.1 or older (R1).
````

### Message to user

I wrote the record as `docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md`, with status `Proposed`. If the team has signed off, set `Accepted` and add the Date heading.

- **Owner:** the Owner heading holds the placeholder `<owner GitHub account>`. Who owns this record?
- **Reason for the decision:** the notes give none, so the Justification only says the Go default already meets R1. What was the security reason? I'd add it.
- **Layer tags:** I tagged R1 `verify` and `server`, assuming those packages open the outgoing connections. Correct the tags if another package does.
- **Rule form and test:** R1 states the requirement as behavior, not as "token-gate sets no `MinVersion`". That way a future change that sets a lower minimum fails R1, and a change to the Go default doesn't affect the rule. No check exists yet, so the record has no Confirmation section. A test against a local TLS 1.1 server, as in the Implementation notes, would be the natural check.
- **Incoming connections:** they are outside the rule, as in the notes. A separate record would cover them.
