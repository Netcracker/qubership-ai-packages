## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. The repository ships it as a container image,
built by `build/token-gate/Dockerfile`, and as a Helm chart for Kubernetes. Some operators run containers with Docker and
no Kubernetes.

Under Docker, token-gate calls the identity provider over HTTPS. An operator whose identity provider uses a certificate
from a private CA needs token-gate to trust that CA. Operators mount the CA certificate under `/tmp/cert`, as they do for
every image of the platform.

Both images of this repository build on the platform base image `ghcr.io/example/platform-base`. The README of the base
image states its contract. Its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or
`.pem` file under `/tmp/cert` to the trust store of the container. It then runs the scripts in `/app/init.d`, and then
runs its arguments. The platform's guide for service images says to keep that entrypoint and to set the service's binary
as `CMD`.

## Decision

We will support token-gate under Docker without Kubernetes, with every setting given through environment variables and
mounted files, and we will keep a Compose example that CI starts on every pull request.

### Terms

- **Docker without Kubernetes**: a container that Docker Engine runs from the image that `build/token-gate/Dockerfile`
  builds, where no Kubernetes API server is reachable and no Kubernetes service account token is mounted.
- **setting**: a value that an operator chooses for one installation, such as an issuer, a listen address, or a CA
  certificate. The keys and documents that token-gate fetches from an issuer at run time are not settings.
- **ready**: token-gate is ready when `GET /ready` returns HTTP 200.

### Rules

#### Settings

- **R1** (`server`). token-gate reads every setting from environment variables or from files in the file system of its
  container, and from no other source.

#### Running under Docker

- **R2** (`server`). Under Docker without Kubernetes, token-gate becomes ready when it gets every setting through
  environment variables and mounted files.

#### The Compose example

- **R3** (`docker`). A Compose file under `deploy/docker/` runs token-gate under Docker without Kubernetes, from the
  image that `build/token-gate/Dockerfile` builds, and passes it every setting through environment variables or mounted
  files.
- **R4** (`ci`). A workflow job under `.github/workflows/` runs on every pull request, starts the Compose file of R3, and
  calls `GET /ready` on token-gate. The job fails when token-gate is not ready within `<readiness timeout>` after the
  start.

### Confirmation

- **R2**, **R3**: the job of R4 fails when the Compose file of R3 does not start token-gate, or when token-gate does not
  become ready.

### Implementation notes

Adds no requirement. In the job of R4, build the image from the checkout of the pull request rather than pulling a
published tag, so that the job tests the change. Mount the settings files read-only in the Compose file, as the chart
does with its read-only root file system.

### Justification

Operators who run containers without Kubernetes can then use the same image as operators who use the chart (R2, R3).
Environment variables and mounted files are the two inputs that both Docker and the chart provide, so one image serves
both without a second way to load settings (R1). The Compose file gives operators a starting point, and it gives the CI
job a deployment to start (R3). A job on every pull request catches a change that makes token-gate depend on Kubernetes
before the change merges (R4).

### Alternatives considered

- **A1. Support token-gate only under Kubernetes, through the Helm chart.** Rejected by R2: operators who run Docker
  without Kubernetes could not run token-gate.

## Consequences

Positive:

- Developers can run token-gate on their own machine with the Compose file of R3, without a cluster.

Negative:

- Every pull request waits for the job of R4.
- A setting that token-gate would read from the Kubernetes API, such as a ConfigMap that it watches through the API,
  cannot be added (R1).

## Open points

- **O1.** The notes do not give the time the job of R4 waits for token-gate to become ready. `example-architect` decides
  the value of `<readiness timeout>`. Affects R4.
- **O2.** The term **ready** assumes that `GET /ready` returns HTTP 200 when token-gate is ready. The answers under
  consideration are HTTP 200 only, or any 2xx status. `example-architect` decides. Affects R2 and R4.
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. Two open points block acceptance: O1, the readiness timeout of the CI job, and O2, whether "ready" means HTTP 200 only or any 2xx status.

The record leaves out the open question about the entrypoint. It's not a design choice; the image departs from the platform's contract. The README of the base image and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and to set the service's binary as `CMD`. `build/token-admin/Dockerfile` does this. `build/token-gate/Dockerfile` instead ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains why. Because of that, certificates under `/tmp/cert` never reach the trust store, and the scripts in `/app/init.d` never run. The record covers the `/tmp/cert` behavior only in Context, because the base image already provides it.

I propose this issue:

- **Type**: Bug
- **Title**: token-gate image replaces the entrypoint of the platform base image
- **Body**: `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. The README of `ghcr.io/example/platform-base` and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` and to set the binary as `CMD`, as `build/token-admin/Dockerfile` does. Because of this, certificates mounted under `/tmp/cert` are not added to the trust store, and `/app/init.d` does not run. The fix is to set `CMD ["/usr/local/bin/token-gate"]` and drop the `ENTRYPOINT` line. The chart also needs `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, because the entrypoint writes there and the Pod's root file system is read-only.

Should I open it? If the `ENTRYPOINT` line is deliberate, tell me why, and I'll add a rule for it.

Without the code I couldn't check where token-gate loads its settings. I tagged R1 and R2 with `server`. Does the loading code live in `internal/server`, or in a package the reading guide doesn't map yet?

The notes named no rejected alternative, so A1 (Kubernetes only) is my wording of the status quo. Please confirm it, or tell me what the meeting actually considered.

## Request 2

### File: docs/adr/0007-refuse-tokens-signed-with-none-or-an-hmac-algorithm.md

````markdown
# Refuse a token whose algorithm is `none` or an HMAC algorithm with HTTP 401

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the signature of a
token with the `jwx` library, and passes it every key that the JWKS of the token's issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. `jwx` accepts a token signed with `HS256`,
`HS384`, or `HS512` when the key set it gets holds a symmetric key.

## Decision

We will refuse a token whose `alg` is `none` or an HMAC algorithm with HTTP 401, and give each case a reason code of its
own.

### Terms

- **token**: the token that token-gate checks for a request.

### Rules

#### The `alg` header parameter

- **R1** (`verify`, `server`). token-gate refuses a token whose JOSE header has the `alg` value `none`, in any letter
  case, with HTTP 401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose JOSE header has the `alg` value `HS256`, `HS384`, or
  `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the token's issuer holds.

#### Precedence

- **R3** (`verify`, `server`). Where token-gate refuses a token under R1 or R2 and the token also fails another check,
  the response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. In `internal/verify`, read `alg` from the protected header before calling `jwx`, and return one
error per reason code, which `internal/server` maps to its response. Leaving the symmetric keys out of the key set
passed to `jwx` also stops `jwx` from accepting an HMAC signature, but on its own it returns the error of `jwx` instead
of `TOKEN_ALG_SYMMETRIC`.

### Justification

A token with the `alg` value `none` carries no signature, so accepting one would let its sender choose every claim
(R1). `jwx` refuses such a token already. R1 gives the refusal a status and a reason code that token-gate defines, and
keeps the refusal when `jwx` changes.

An HMAC key both signs and verifies. A symmetric key in a JWKS is readable by every client that fetches the JWKS, so any
of those clients could sign a token that `jwx` accepts (R2).

Two reason codes let an operator tell a token with `none`, which points at an attack, from a token signed with HMAC,
which can also point at an issuer configured to sign with HMAC (R1, R2). Whether any other claim of a token can be
trusted depends on its algorithm, so the reason code for the algorithm comes first (R3).

### Alternatives considered

- **A1. Accept a token signed with HMAC when token-gate holds a shared secret for its issuer.** Rejected by R2:
  token-gate would hold a secret that can also sign tokens for that issuer, so a leak from token-gate would let its
  holder issue tokens.

## Consequences

Negative:

- An issuer that signs tokens with `HS256`, `HS384`, or `HS512` today, through a symmetric key in its JWKS, gets every
  token refused after the upgrade (R2). No setting restores the old answer.

## Open points

- **O1.** R1 assumes that `alg` is compared without regard to letter case, so that `None` and `NONE` also get
  `TOKEN_ALG_NONE`. The other answer is the exact value `none` only, which leaves other spellings to the reason code
  of an unknown algorithm. `example-security-architect` decides. Affects R1.
- **O2.** R3 assumes that the reason code of R1 or R2 wins over the reason code of every other check, such as expiry.
  The other answer is to let the first check that fails in `internal/verify` decide the reason code.
  `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. Two open points block acceptance. O1 asks whether `alg` is compared without regard to letter case. O2 asks whether the algorithm's reason code wins when a token also fails another check, such as expiry. I added R3 so that a checker knows which reason code applies when both fail.

R1 is a rule even though `jwx` already refuses `none`, because the status and the reason code are this service's decision. R2 is not met today. `internal/verify` passes `jwx` every key in an issuer's JWKS, so `jwx` accepts an HMAC token when the JWKS holds a symmetric key. The change that fixes this should end with `Implements: ADR-0007 R1, R2, R3`.

The notes gave no reasons, so I wrote the usual ones in the Justification and in A1. Please ask `example-security-architect` to confirm them.

Which record defines the response of a refused request and its reason codes? I'll link it under **Related ADRs** and use its terms for the response.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-on-outgoing-tls-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate checks the token of each request before policy evaluation. It opens TLS connections as a client, such as
the connections that fetch the JWKS of an issuer.

Go's `crypto/tls` client refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. RFC
8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection in which the token-gate process is the client, whether token-gate's own
  code opens it or a library that token-gate calls, such as `jwx`, does.

### Rules

#### TLS version

- **R1** (`verify`, `server`). token-gate completes the handshake of an outgoing TLS connection only at TLS 1.2 or
  later. Where the server supports only TLS 1.1 or older, the handshake fails, and token-gate sends no application data
  on that connection.

### Implementation notes

Adds no requirement. Go's default meets R1 for a `tls.Config` whose `MinVersion` is unset. A `tls.Config` that
token-gate builds also meets R1 with `MinVersion` set to `tls.VersionTLS12` or `tls.VersionTLS13`. A test that starts an
`httptest` server limited to TLS 1.1 and expects the call of the client to fail would give R1 a check.

### Justification

TLS 1.0 and TLS 1.1 are deprecated, so token-gate uses neither for the connections it opens (R1). Go's default already
meets this minimum. A rule lets a checker refuse a change that lowers it, such as a `tls.Config` with
`MinVersion: tls.VersionTLS10` added for one identity provider (R1).

### Alternatives considered

- **A1. Leave the minimum version to Go's default, with no record.** A change to the default, or a `tls.Config` that
  lowers it, would then have no rule that a checker could hold it against.

## Consequences

Negative:

- token-gate cannot use an identity provider or another server that supports only TLS 1.1 or older (R1).
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. It has no open points. Once the team signs off, set the status to `Accepted` and add the Date heading with the acceptance date.

R1 is a rule even though Go already provides this behavior, because the security architect chose the minimum for token-gate. The code meets R1 today, since token-gate sets no minimum version of its own, so no code change is needed. The record has no **Confirmation** section yet. A test that runs an `httptest` server limited to TLS 1.1 would give R1 a check, and the record would then gain the entry.

Without the code I couldn't see which packages open outgoing connections. I tagged R1 with `verify` and `server`. Does any other mapped layer, or an unmapped package, open TLS connections?

The notes named no alternatives or reasons. Please ask `example-security-architect` to confirm the Justification and A1.
