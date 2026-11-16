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

token-gate ships as a container image and a Helm chart. Operators who run it under Docker without Kubernetes have no
documented way to do so and no check that the image starts there.

Under Docker, operators need token-gate to trust a private CA for its HTTPS calls to the identity provider. The README
of the platform base image, `ghcr.io/example/platform-base`, states that its entrypoint, `/usr/bin/entrypoint.sh`, adds
every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container. Operators
mount the certificate there, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone,
ship a Compose example for it, and start that example in CI on every pull request.

### Terms

- **Docker deployment**: a container of the image built by `build/token-gate/Dockerfile`, run on a container runtime
  without a Kubernetes cluster.
- **Compose example**: the Compose file and the files it mounts under `deploy/docker/`.

### Rules

#### Support under Docker

- **R1** (`server`). In a Docker deployment, token-gate takes every setting from environment variables or mounted
  files, and from no other source.
- **R2** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate as a Docker deployment.

#### Verification in CI

- **R3** (`ci`). A job under `.github/workflows/` starts the Compose example on every pull request, calls `GET /ready`,
  and fails when the response is not `<ready status>` within `<ready timeout>`.

### Justification

An operator without Kubernetes needs a working starting point (R2) and a way to know that it keeps working (R3). Limiting
configuration to environment variables and mounted files keeps the Docker deployment free of anything that only a
cluster provides (R1).

## Consequences

Negative:

- Every pull request pays for starting the Compose example (R3).

## Open points

- **O1.** The notes do not give the response that `GET /ready` must return or how long the job waits for it. Answers
  under consideration: HTTP 200 and a wait time chosen by `example-architect`. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It stays `Proposed` until O1 is settled: the notes give neither the status that `GET /ready` must return nor the wait time, so R3 has the placeholders `<ready status>` and `<ready timeout>`. Please supply both.

**The entrypoint question is not a decision, so the record has no rule for it.** The base image README and the platform guide for service images say to keep the base entrypoint and set the binary as `CMD`. `token-admin` already does this. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains that line. Restoring the contract is a fix. I suggest this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so `/tmp/cert` is ignored
- **Contract it departs from:** the platform guide for service images keeps `/usr/bin/entrypoint.sh` and sets the service binary as `CMD`. The base entrypoint adds the certificates under `/tmp/cert` to the trust store and runs the scripts in `/app/init.d`.
- **Fix:** drop the `ENTRYPOINT` line and end `build/token-gate/Dockerfile` with `CMD ["token-gate"]`, as `build/token-admin/Dockerfile` does. The chart runs the Pod with a read-only root file system and the base entrypoint writes to the trust store. So the same issue adds `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart.

Until that issue lands, mounting a private CA under `/tmp/cert` has no effect on token-gate.

The guide in `docs/adr/README.md` already maps `server`, `docker`, and `ci`, so I changed nothing else. A change that implements the rules should end its commit message and pull request description with `Implements: ADR-0007 R1, R2, R3`, or defer the rules it leaves out.

## Request 2

### File: docs/adr/0007-refuse-none-and-hmac-token-algorithms.md

````markdown
# Refuse tokens whose header names the algorithm `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

`internal/verify` verifies signatures with the `jwx` library. `jwx` refuses a token whose `alg` is `none` when it
verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key, and
`internal/verify` passes it every key that the JWKS of an issuer holds. A symmetric key in the JWKS of an issuer would
therefore make token-gate accept an HMAC-signed token.

## Decision

We will refuse a token whose header names the algorithm `none` or an HMAC algorithm, each with HTTP 401 and its own
reason code, and we will not accept HMAC with a shared secret per issuer.

### Terms

- **token named `none`**: a token whose header parameter `alg` has exactly the value `none`, compared case-sensitively.
- **HMAC token**: a token whose header parameter `alg` has exactly the value `HS256`, `HS384`, or `HS512`, compared
  case-sensitively.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a token named `none` with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses an HMAC token with HTTP 401 and the reason code
  `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the issuer holds and whether or not the signature is valid.

### Justification

R2 closes the path that `jwx` leaves open when a JWKS holds a symmetric key. R1 fixes the response for `none` as a
decision of token-gate, so it does not depend on the behavior of a library.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2.

## Consequences

Negative:

- An issuer that signs its tokens with `HS256`, `HS384`, or `HS512` cannot use token-gate (R2). A token that `jwx`
  accepts today because the JWKS holds a symmetric key gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` after this change.

## Open points

- **O1.** Case variants such as `None` or `hs256`. Assumed here: they are not matched by the terms, and no rule covers
  them. `example-security-architect` decides whether they get the same refusal. Affects R1 and R2.
- **O2.** Where the reason code appears in the response, such as a body field or a header. `example-security-architect`
  decides. Affects R1 and R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. These points block acceptance:

- **O1:** I assumed that `alg` is compared case-sensitively, as in RFC 7518. Should `None` or `hs256` get the same refusal?
- **O2:** The notes do not say where the reason code appears in the response, such as a body field or a header.

Two more questions:

- The notes record no reason for rejecting HMAC with a shared secret per issuer, so A1 only cites R2. What was the reason? I can add it to the Justification.
- I tagged both rules `verify` and `server` without seeing the code. Which layer produces the HTTP 401? I'll drop the other tag.

R2 changes an answer that callers get today. A token that `jwx` accepts because a JWKS holds a symmetric key now gets 401, and Consequences names this case. No test exists to cite, so Confirmation is empty. Once a test lands, it can be added there.

I wrote no rule for the fact that `jwx` already refuses `none`. R1 states the decision on the response, which `jwx` does not provide.

## Request 3

### File: docs/adr/0007-require-tls-1-2-for-outgoing-connections.md

````markdown
# Require TLS 1.2 or later on the outgoing TLS connections of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

Go's `crypto/tls` client refuses TLS 1.1 and older by default. token-gate sets no minimum TLS version of its own, so its
outgoing connections get that default.

## Decision

We will use TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that token-gate opens as the client, to any host.

### Rules

#### Minimum TLS version

- **R1** (`verify`, `server`). An outgoing TLS connection never completes a handshake with a protocol version older
  than TLS 1.2, whatever the setting or the host.

### Justification

The rule states the minimum as a decision of token-gate. A change that lowers it fails R1, and the minimum does not
depend on the default of a Go release (R1).

## Consequences

Negative:

- A host that supports only TLS 1.1 or older is unreachable for token-gate (R1), such as an identity provider that has
  not been upgraded.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, with no open points. It becomes `Accepted` once the team signs off. Then add the Date heading.

Today's code already meets R1 through the Go default, so I added no code or Confirmation entry. A test that fails when a `tls.Config` in token-gate sets a lower `MinVersion` would give R1 a machine check.

Two questions:

- I tagged R1 `verify` and `server` without seeing the code. Which package opens the outgoing connections, such as the JWKS fetch? I'll tag that one.
- The notes give no reason beyond the TLS 1.2 minimum. If there is a compliance or threat reason, I can add it to the Justification.
