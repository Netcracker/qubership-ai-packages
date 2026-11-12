## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate ships as a container image and as a Helm chart. Operators who do not run Kubernetes need to run the image
under Docker.

Under Docker, operators trust a private CA for the HTTPS calls from token-gate to the identity provider. They mount the
CA certificate under `/tmp/cert`, as for every image of the platform. The image builds on the platform base image
`ghcr.io/example/platform-base`. According to the README of the base image, its entrypoint `/usr/bin/entrypoint.sh` adds
every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container, runs the
scripts in `/app/init.d`, and then runs its arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
We will ship a Compose example under `deploy/docker/`, and a CI job will start it on every pull request and call
`GET /ready`.

### Terms

- **Docker deployment**: a run of the token-gate image by Docker or Docker Compose where no Kubernetes cluster is
  involved.
- **mounted file**: a file that a Docker deployment makes visible inside the container through a bind mount or a volume.
- **Compose example**: the Compose file under `deploy/docker/` that runs token-gate.

### Rules

#### Running under Docker

- **R1** (`server`). In a Docker deployment, token-gate takes all of its configuration from environment variables and
  mounted files.
- **R2** (`server`). In a Docker deployment, token-gate starts and serves requests where no Kubernetes API is
  reachable.

#### The Compose example

- **R3** (`docker`). `deploy/docker/` holds a Compose example that runs token-gate as a Docker deployment.
- **R4** (`ci`). A workflow under `.github/workflows/` runs on every pull request, with no path or branch filter. Its job
  starts the Compose example, calls `GET /ready` on token-gate, and fails where the response status is not 200.

### Confirmation

- **R2, R3**: the job of R4 starts the Compose example on a runner that has no Kubernetes cluster.

### Justification

A Compose example that CI starts on every pull request stays working as the code changes (R3, R4). Environment variables
and mounted files are what Docker offers without Kubernetes objects, so an operator needs nothing else to run the
service (R1, R2).

### Alternatives considered

- **A1. Support token-gate only on Kubernetes, through the Helm chart.** Rejected by R2: operators without a cluster
  could not run the service.

## Consequences

Negative:

- Every pull request pays for the start of the Compose example (R4).

## Open points

- **O1.** R4 assumes that `GET /ready` returns HTTP 200 when token-gate is ready. The architect confirms the status, or
  names another success criterion. This affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has one open point, O1, which blocks acceptance. It asks you to confirm that `GET /ready` returns HTTP 200 when the service is ready, because R4 assumes that status.

**The entrypoint question is a defect, so the record has no rule for it.** The platform guide and the base image README say that service images keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` does this, with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains that line. The record keeps the base-image contract in Context as a fact and names neither the issue nor the fix. I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform base entrypoint, so certificates under `/tmp/cert` are never trusted
- **Contract it departs from:** the README of `ghcr.io/example/platform-base` and the platform guide for service images, which say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`.
- **Scope:** the issue covers the Dockerfile fix and the chart change that goes with it. Change the last line of `build/token-gate/Dockerfile` to `CMD ["token-gate"]`, as in the token-admin image. Add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart, because the base entrypoint writes there and the Pod has a read-only root file system.

If keeping the binary as the entrypoint is deliberate, tell me. It then becomes a decision and gets a rule.

**Questions and assumptions:**

- I took `example-architect` as the owner and sole approver. Please confirm.
- I assumed the configuration loading and the start-up code sit under `internal/server`, so R1 and R2 carry the `server` tag. Please confirm.
- Records 0001 to 0006 were not available to me, so I linked no related ADRs. If one of them covers configuration or the readiness endpoint, the link belongs under **Related ADRs**.

No existing record or the `README.md` guide changes. I wrote no Confirmation entry for R1, because no check shows that configuration comes from environment variables and mounted files alone. Reviewers read the diff for that.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-the-none-or-an-hmac-algorithm.md

````markdown
# Refuse tokens whose header names the algorithm `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and
`HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an issuer
holds. A symmetric key in the JWKS of an issuer therefore makes the service accept a token signed with an HMAC.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`. We
will refuse a token signed with `HS256`, `HS384`, or `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`.

### Terms

- **request token**: the token that token-gate takes from a request to check before policy evaluation.
- **header algorithm**: the value of the `alg` parameter in the header of a request token.
- **refuse**: token-gate answers the request with the stated HTTP status and reason code, and does not pass the request
  to policy evaluation.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a request token whose header algorithm is exactly `none`, with HTTP
  401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a request token whose header algorithm is `HS256`, `HS384`, or
  `HS512`, with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of its issuer holds.

#### Precedence

- **R3** (`verify`, `server`). Where a request token fails R1 or R2 and also fails another check of the token, the
  response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. Read the header algorithm before the signature is verified, and refuse the token there. Keep
symmetric keys out of the key set that `internal/verify` passes to `jwx`, so that the library cannot accept an HMAC
token even if the check is bypassed.

### Justification

`jwx` already refuses `none` but gives the caller no reason code, so R1 states the answer that the service returns. It
accepts an HMAC token whenever the JWKS of an issuer holds a symmetric key, so R2 closes that case whatever the key set
holds (R2). R3 gives a caller one reason code for a token that fails several checks.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: the security review considered it and rejected it.
- **A2. Pass every key of the JWKS of an issuer to the library and rely on the library to refuse the algorithm.**
  Rejected by R1 and R2: the library accepts `HS256`, `HS384`, and `HS512` where the key set holds a symmetric key, and
  it gives no reason code for `none`.

## Consequences

Positive:

- A caller tells a refused `none` token from a refused HMAC token by the reason code (R1, R2).

Negative:

- An issuer that signs tokens with `HS256`, `HS384`, or `HS512` gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` for every
  token, including an issuer whose JWKS holds a symmetric key and whose tokens the service accepted before (R2).

## Open points

- **O1.** R1 and R2 match the header algorithm exactly. The security architect decides whether a case variant such as
  `None` or `hs256` is refused with the same codes (case-insensitive match), or falls to the handling of any other
  unsupported algorithm (exact match). This affects R1 and R2.
- **O2.** R3 assumes that the algorithm refusal wins over every other refusal reason. The security architect confirms
  this, or names the checks whose reason code wins. This affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance:

- **O1:** whether a case variant such as `None` or `hs256` gets the same refusal as the exact value.
- **O2:** whether the algorithm refusal wins over every other refusal reason. I wrote R3 on that assumption because a token can fail several checks at once.

**Questions and assumptions:**

- The notes give no reason for rejecting a shared secret per issuer, so A1 says only that the review rejected it. Please send the reason.
- I took `example-security-architect` as the owner and sole approver. Please confirm.
- I tagged R1 to R3 with `verify` and `server`, on the assumption that `internal/verify` decides the refusal and `internal/server` produces the 401. Please confirm.
- Records 0001 to 0006 were not available to me, so I linked no related ADRs. If an earlier record owns the reason codes or the 401 response, add its link under **Related ADRs**.

**Notes on the record:**

- The `none` refusal already comes from `jwx`, but R1 stays a rule because it fixes the code that callers see.
- There is no **Confirmation** section yet, because no test for these rules exists. Add it when tests land. Suggested tests: one per algorithm, plus one for an issuer whose JWKS holds a symmetric key.
- Upgrade effect: issuers that sign with HMAC now get 401. The record lists this under **Negative**, citing R2.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections-of-token-gate.md

````markdown
# Use TLS 1.2 or later for the outgoing TLS connections of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate calls other services over TLS, such as the identity provider. According to the documentation of Go's
`crypto/tls` package, a client refuses TLS 1.1 and older by default. token-gate sets no minimum version of its own, so
the default applies to every outgoing connection.

## Decision

We will use TLS 1.2 or later for the outgoing TLS connections of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, whatever the peer.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). An outgoing TLS connection is established only with TLS 1.2 or later. Where the peer
  offers no version from TLS 1.2 on, the handshake fails.

### Implementation notes

Adds no requirement. The default of the `crypto/tls` client already meets R1, so the code needs no change. Setting
`MinVersion: tls.VersionTLS12` in the `tls.Config` that token-gate uses for outgoing connections keeps the floor in
place if a later Go release changes the default.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1, so TLS 1.2 is the oldest version that the service accepts (R1).

### Alternatives considered

- **A1. Accept TLS 1.0 and TLS 1.1 for identity providers that offer nothing newer.** Rejected by R1.

## Consequences

Negative:

- token-gate cannot reach a peer that offers only TLS 1.1 or older, such as an old identity provider. Its calls to that
  peer fail at the handshake (R1).
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has no open points, so it can become `Accepted` once the team signs off. Add the Date heading with the acceptance date at that point.

**Questions and assumptions:**

- I wrote R1 as a rule even though the Go default already provides the behavior. The security architect chose TLS 1.2 or later for this system, which makes it a decision. The rule keeps the requirement if the Go default changes.
- The notes give no reason for the choice. I added RFC 8996, which deprecates TLS 1.0 and TLS 1.1, to the Justification. Please confirm it matches the reasoning of the review, or replace it.
- I took `example-security-architect` as the owner and sole approver. Please confirm.
- I assumed the outgoing connections come from `internal/verify` and `internal/server`, and tagged R1 with both. Please confirm which code opens them.
- The scope is the token-gate process. `token-admin` is not covered. If it should be, say so.
- Records 0001 to 0006 were not available to me, so I linked no related ADRs.

There is no **Confirmation** section yet, because no check exists for R1. A test that fails the handshake against a server limited to TLS 1.1 would fill it.
