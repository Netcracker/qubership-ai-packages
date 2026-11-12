## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

The repository ships token-gate as a container image and a Helm chart. Operators who run it under Docker without
Kubernetes need to trust a private CA for the HTTPS calls from token-gate to the identity provider.

The README of the platform base image `ghcr.io/example/platform-base` states that its entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container. Operators mount the certificate of the private CA there, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. We will ship a Compose example for it and start that example in CI on every pull request.

### Terms

- **Docker deployment**: a container of the token-gate image that Docker or Docker Compose starts, in an environment
  with no Kubernetes cluster.
- **container configuration**: the environment variables of the container and the files mounted into it.
- **Compose example**: the Compose file under `deploy/docker/` that R1 requires.

### Rules

#### Compose example

- **R1** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate with container configuration
  only.
- **R2** (`ci`). A CI job starts the Compose example on every pull request, calls `GET /ready` on the started
  token-gate, and fails unless the response is `<ready response>`.

#### Behavior in a Docker deployment

- **R3** (`server`). In a Docker deployment, token-gate starts and answers `GET /ready` with `<ready response>` when
  container configuration is its only configuration.

### Implementation notes

Adds no requirement. Mount the certificate of a private CA under `/tmp/cert` in the Compose example, so that the
example shows operators the path that the base image reads. Give the example a stub identity provider, so that
`GET /ready` can succeed inside the CI job.

### Justification

An operator without a cluster can run token-gate only if its configuration does not depend on Kubernetes objects (R3)
and a maintained example shows how (R1). The CI job keeps the example working, so the claim of support stays true as
the code changes (R2).

### Alternatives considered

- **A1. Support token-gate on Kubernetes only.** Operators who run plain Docker would have no supported deployment.

## Consequences

Positive:

- An operator with no cluster can run token-gate from the Compose example.

Negative:

- Every pull request runs one more CI job (R2).
- A configuration option that only a Kubernetes object can set is not allowed, because R3 requires that container
  configuration alone configures token-gate.

## Open points

- **O1.** What `GET /ready` returns when token-gate is ready: the status code and, where it matters, the body.
  `example-architect` decides. It affects R2 and R3.
````

### Message to the user

I wrote the record as `Proposed`, because O1 is open: the notes do not say what a successful `GET /ready` returns, so R2 and R3 carry the placeholder `<ready response>`. Please give me the status code, and the body if it matters.

**The entrypoint question is a defect, not an open point.** The record has no rule on it. The base image README and the platform guide for service images say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` already does this with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, with no comment, record, or issue to explain it. Here is the issue I propose:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are ignored
- **Contract it departs from:** the base image README says the entrypoint adds the certificates under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. The platform guide says to keep that entrypoint and set the binary as `CMD`.
- **Fix:** replace the `ENTRYPOINT` line in `build/token-gate/Dockerfile` with a `CMD` for the binary. Also add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart, because the restored entrypoint writes there and the Pod has a read-only root file system.

If the `ENTRYPOINT` is deliberate, tell me and I will add a rule for it.

Assumptions and questions:

- **Owner:** I set `example-architect` as owner and approver of R1 to R3. Please confirm.
- **Layer of R3:** I tagged R3 `server` because it concerns `/ready`. I could not read the code, so check this.
- **Related ADRs:** I could not read records 0001 to 0006, so I linked none. Check whether any of them touches the chart or configuration.
- **Reading guide:** it needs no change, because the `docker` and `ci` layers already exist.
- **Trailers:** the pull requests that add the Compose example and the CI job will carry `Implements:` trailers for R1 and R2. The change that makes R3 true will carry one for R3.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md

````markdown
# Refuse a token whose `alg` header is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when
the key set holds a symmetric key. `internal/verify` passes it every key that the JWKS of an issuer holds, so a token
signed with HMAC can verify today where the JWKS of its issuer holds a symmetric key.

## Decision

We will refuse a token whose `alg` header is `none`, and a token whose `alg` header is `HS256`, `HS384`, or `HS512`.
Each gets HTTP 401 and its own reason code.

### Terms

- **`alg` header**: the `alg` parameter of the JOSE header of a token.
- **refuse a token**: respond to the request with the status and the reason code that the rule names, and do not
  evaluate policy for that request.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose `alg` header is `none` with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose `alg` header is `HS256`, `HS384`, or `HS512` with HTTP
  401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the issuer of the token holds.
- **R3** (`verify`, `server`). Where R1 or R2 refuses a token that also fails another check, such as the signature or
  the expiry, the response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. Read the `alg` header before the key lookup and before the call to `jwx`, and map `none` and the
three HMAC values to the two reason codes there. Do not rely on `jwx` for R1: its refusal is a library error, and it
carries neither the status nor the reason code. Do not rely on the key set for R2: `jwx` accepts an HMAC token when
the key set holds a symmetric key.

Add a table test in `internal/verify` with one token for each of `none`, `HS256`, `HS384`, and `HS512`. For the HMAC
tokens, use an issuer whose JWKS holds a symmetric key. Assert the status and the reason code of each response.

### Justification

`jwx` already refuses `none` (R1), but it does not give the status and reason code that callers need, so the service
states them itself. `jwx` accepts HMAC when the JWKS of an issuer holds a symmetric key, and `internal/verify` passes
every key of that JWKS, so the code alone does not refuse HMAC (R2). One fixed reason code for each refusal lets a
caller tell the two cases apart without reading error text (R1, R2). R3 keeps that reason code stable when a token
fails several checks.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: the security review considered it and decided
  against it.
- **A2. Leave the refusal of `none` to `jwx`.** Rejected by R1: the library error has neither the status nor the
  reason code that R1 requires.
- **A3. Pass an HMAC token to `jwx` and let the key set decide.** Rejected by R2: the token verifies whenever the
  JWKS of the issuer holds a symmetric key.

## Consequences

Negative:

- A token signed with `HS256`, `HS384`, or `HS512` that verifies today, because the JWKS of its issuer holds a
  symmetric key, gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` after this change (R2). The table test of **Implementation
  notes** shows the case. An issuer that signs with HMAC cannot use token-gate.

Follow-ups:

- Check before the rollout whether any issuer of an existing installation signs its tokens with `HS256`, `HS384`, or
  `HS512`.

## Open points

- **O1.** Whether a header value that differs from `none` only in letter case, such as `None`, gets R1. Case-sensitive
  matching is assumed, so that R1 covers only `none`. `example-security-architect` decides. It affects R1.
- **O2.** Whether R3 is the intended precedence. R3 assumes that the algorithm refusal wins over every other failure
  of the same token. `example-security-architect` decides. It affects R1, R2, and R3.
- **O3.** Where the response carries the reason code, such as a body field or a header. The assumption is that it
  follows the way token-gate reports its other reason codes. `example-security-architect` decides. It affects R1 and
  R2.
````

### Message to the user

The record is `Proposed`, because three open points block acceptance:

- **O1:** whether a case variant such as `None` gets `TOKEN_ALG_NONE`. I assumed exact matching.
- **O2:** whether the algorithm refusal wins over other failures, such as an expired or badly signed token. I assumed it does, and stated that in R3.
- **O3:** where a reason code goes in the response. I assumed the existing convention. Please confirm what it is.

Other questions and assumptions:

- **Alternative A1:** the notes say that HMAC with a shared secret per issuer was rejected, but give no reason, so A1 says only that. Please send the reason if you want it recorded.
- **Behavior change:** R2 is a behavior change. Today `jwx` can verify an HMAC token when the issuer's JWKS holds a symmetric key. The Negative consequence records that.
- **Owner:** I set `example-security-architect` as owner and approver. Please confirm.
- **Layers:** I tagged both rules `verify` and `server`, because the check sits in `internal/verify` and the 401 is produced by the server. I could not read the code, so check this.
- **Related ADRs:** I could not read records 0001 to 0006, so I linked none. Check whether any of them defines reason codes.
- **Trailers:** the change that brings R1 to R3 will carry `Implements: ADR-0007 R1, R2, R3`.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, for example for the HTTPS calls to the identity provider. The `crypto/tls`
client of Go refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. The minimum
that token-gate enforces is therefore the default of the Go version that builds it.

## Decision

We will use TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, through any HTTP
  client or library, including a connection to an identity provider. A TLS connection that token-gate accepts as the
  server is not one.

### Rules

#### TLS version

- **R1** (`verify`, `server`). token-gate completes no handshake of an outgoing TLS connection below TLS 1.2. Where
  the peer offers only TLS 1.1 or an earlier version, the connection attempt fails with a handshake error.

### Implementation notes

Adds no requirement. The default of `crypto/tls` already meets R1, so the code needs no change. Add a test that starts
a local TLS server limited to TLS 1.1, for example with `httptest.NewUnstartedServer` and a `tls.Config` whose
`MaxVersion` is `tls.VersionTLS11`. Make token-gate call it as it calls an identity provider, and assert the handshake
error. Add a second case with a server that offers TLS 1.2, and assert that the call succeeds. A later change that
lowers the minimum, or a Go version that changes the default, then fails the test.

### Justification

The default of `crypto/tls` meets the decision today, but it belongs to the Go version, and a later edit of a
`tls.Config` could lower it unnoticed. A rule and a test that state the minimum keep the decision true when either
changes (R1).

### Alternatives considered

- **A1. Rely on the default of `crypto/tls` and write no rule.** Rejected by R1: the default depends on the Go version
  that builds token-gate, so nothing would fail if it changed.

## Consequences

Negative:

- token-gate cannot reach an identity provider or any other peer that offers only TLS 1.1 or an earlier version (R1).
  Calls to such a peer fail with a handshake error.
````

### Message to the user

I wrote the decision as one behavior rule, R1. Go's default already meets it, so no code changes. The only code the record asks for is the test in **Implementation notes**, which keeps the minimum from changing unnoticed. I did not write a rule against setting `MinVersion` below TLS 1.2, because R1 already makes that fail.

The status is `Proposed`, because the notes say "decided" and do not say the team accepted the record. There are no open points, so once the team has signed off, set the status to `Accepted` and add the Date heading with the acceptance date.

I need these confirmed:

- **Owner:** I set `example-security-architect` as owner and approver. Please confirm.
- **Layers:** I tagged R1 `verify` and `server`, on the assumption that those packages open the outgoing connections, such as the JWKS fetch. I could not read the code. Tell me if another package opens one, and I will add its layer.
- **Related ADRs:** I could not read records 0001 to 0006, so I linked none. Check whether one covers outgoing connections or trust configuration.
- **Trailers:** the change that adds the test will carry `Implements: ADR-0007 R1`.
