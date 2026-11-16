## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, with a Compose example checked in CI

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart, so
Kubernetes is the only deployment the repository documents today.

Some operators run containers under Docker alone. To make HTTPS calls to the identity provider, they need to trust a
private CA, and they mount its certificate under `/tmp/cert`, as for every image of the platform.

The image of token-gate builds on the platform base image `ghcr.io/example/platform-base`. Its README states that its
entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to
the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone,
and we will ship a Compose example that a CI job starts on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker or Docker Compose starts, in an environment with no
  Kubernetes cluster.
- **Compose example**: the Compose file under `deploy/docker/` that R2 requires.

### Rules

#### Running under Docker

- **R1** (`server`). In a Docker deployment, token-gate starts and serves requests with its configuration taken from
  environment variables and from files mounted into its container alone, and it needs no Kubernetes API or other
  Kubernetes service.
- **R2** (`docker`). `deploy/docker/` holds a Compose example that runs token-gate as a Docker deployment, and the
  example sets the configuration of token-gate through environment variables and mounted files alone.

#### Checking the example

- **R3** (`ci`). On every pull request, a CI job starts the Compose example and calls `GET /ready` on token-gate, and
  the job fails unless that call returns HTTP 200.

### Confirmation

- **R3**: the CI job that R3 requires is the check, and it runs on every pull request.

### Justification

Operators who run Docker without Kubernetes need a documented, supported way to run token-gate (R1, R2). An example that
no job runs goes stale, so a job that starts it on every pull request shows that the example still works (R3).

## Consequences

Negative:

- Every pull request pays for one more CI job, which starts the Compose example (R3).
- The Compose example is a second deployment description to keep working next to the Helm chart (R2).

## Open points

- **O1.** What counts as success for the CI job of R3, and how long the job waits for token-gate to become ready? The
  rule assumes HTTP 200 from `GET /ready`, and a timeout is not set. The architect, `example-architect`, decides. It
  affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has three rules: R1 (Docker without Kubernetes, configured by environment variables and mounted files), R2 (the Compose example) and R3 (the CI job that calls `GET /ready`).

- **The open question about the entrypoint has no rule.** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, which replaces the platform entrypoint. The base image README and the platform guide for service images already settle this: keep the base entrypoint and set the binary as `CMD`. `build/token-admin/Dockerfile` already does that with `CMD ["token-admin"]`. The `ENTRYPOINT` line has no comment and no record or issue explains it, so I treat it as a defect, not a decision. The ADR states the `/tmp/cert` behavior of the base image as a fact in Context and does not name the fix.
- **I propose this issue.**
  - Type: Bug.
  - Title: "token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are ignored".
  - Contract: the base image README, and the platform guide that says to keep the entrypoint and set the binary as `CMD`.
  - Scope: change `build/token-gate/Dockerfile` to use `CMD`. Also add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart, because the base entrypoint writes there and the Pod's root file system is read-only. Both changes belong in the same issue.
  - If the `ENTRYPOINT` was deliberate, tell me and I will add a rule for it.
- **Trailers.** The Compose example under `deploy/docker/` can only trust a private CA after that issue is fixed. The changes that bring R1 to R3 should end with `Implements:` trailers, and `Defers:` should point at that issue once it exists. I did not guess an issue number.
- **Owner.** I left the Owner as the placeholder `<owner account>`. Tell me the GitHub account. I assumed `example-architect` approves R1 to R3.
- **Open point.** O1 asks what counts as success for the CI job, and I assumed HTTP 200. It blocks `Accepted`.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-the-none-or-an-hmac-algorithm.md

````markdown
# Refuse tokens whose algorithm is none or an HMAC algorithm

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate verifies the signature of each token with the `jwx` library, in `internal/verify`. `jwx` refuses a token
whose `alg` header is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set
holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an issuer holds. A token signed with an
HMAC algorithm can therefore pass verification today, for an issuer whose JWKS holds a symmetric key.

`jwx` does not choose the HTTP status or the reason code of a refusal, so the response of token-gate to such a token is
a decision of this system.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and a
token whose header names an HMAC algorithm with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`.

### Terms

- **HMAC algorithm**: the algorithm `HS256`, `HS384`, or `HS512`.
- **none token**: a token whose header names the algorithm `none` in its `alg` field.
- **HMAC token**: a token whose header names an HMAC algorithm in its `alg` field.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a none token with HTTP 401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses an HMAC token with HTTP 401 and the reason code
  `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of its issuer holds, and including a token whose signature is valid for
  such a key.

### Implementation notes

Adds no requirement. Read the `alg` field of the header before the token reaches `jwx`, and return the refusal there.
Passing `jwx` only the keys that fit the algorithm of the token is a second safeguard, but it does not by itself give
the reason codes of R1 and R2.

### Justification

A none token carries no signature, so it proves nothing about its sender. `jwx` already refuses it, and R1 fixes the
status and the reason code, so that a change of the library cannot change the answer (R1). An HMAC token is verified with
a secret that both the issuer and token-gate hold, so a holder of that secret can also issue tokens. R2 refuses it
whatever the JWKS holds, because `internal/verify` passes `jwx` every key of the JWKS (R2).

### Alternatives considered

- **A1. Accept HMAC tokens with a shared secret per issuer.** Rejected by R2: token-gate would have to hold a secret per
  issuer, and each holder of such a secret could issue tokens for that issuer.

## Consequences

Positive:

- A client and an operator can tell a refusal for the algorithm from other refusals by the reason code (R1, R2).

Negative:

- An issuer whose tokens use an HMAC algorithm, and whose JWKS holds a symmetric key, passes verification before this
  change and gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` after it (R2). Such an issuer has to sign with an asymmetric
  algorithm.

## Open points

- **O1.** Which reason code does token-gate return for a none token or an HMAC token that also fails another check, such
  as expiry? The rules assume that R1 and R2 decide, because the algorithm is read before any other check. The security
  architect, `example-security-architect`, decides. It affects R1 and R2.
````

### Message to the user

I wrote the ADR as `Proposed`, with two rules: R1 for `none` and R2 for the HMAC algorithms.

- **Why `none` gets a rule.** `jwx` already refuses it. I still wrote R1, because the status and the reason code `TOKEN_ALG_NONE` are a decision of this system, and the library does not provide them. The Context says so.
- **A1 reason is mine.** The notes say HMAC with a shared secret per issuer was rejected and give no reason. I wrote that a shared secret lets each holder issue tokens. Please confirm or replace it.
- **Open point.** O1 asks which reason code wins when a `none` or HMAC token also fails another check. I assumed the algorithm refusal wins. It blocks `Accepted`.
- **Owner.** I left the Owner as the placeholder `<owner account>`. Tell me the GitHub account. I assumed `example-security-architect` approves R1 and R2.
- **Layers.** I could not read the code. I tagged R1 and R2 with `verify` and `server`, assuming the algorithm check sits in `internal/verify` and the HTTP response in `internal/server`.
- **Existing issuers.** Issuers whose JWKS holds a symmetric key and who sign with HMAC pass today and get 401 after this change. The Negative consequence names that case. No test exists yet, so Confirmation is empty. A test for each of R1 and R2 can be added to Confirmation when it lands.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, for example for the HTTPS calls to the identity provider. It sets no
minimum TLS version of its own. The `crypto/tls` client of Go already refuses TLS 1.1 and older by default, so the
connections meet the requirement of this record today, and only through that default. TLS 1.0 and 1.1 are deprecated by
RFC 8996.

## Decision

We will require every outgoing TLS connection of token-gate to use TLS 1.2 or later.

### Terms

- **outgoing TLS connection**: a TLS connection that a token-gate process opens as the client, to any host. A TLS
  connection that token-gate accepts as a server is not one.

### Rules

#### TLS version

- **R1** (`verify`, `server`). token-gate completes the handshake of an outgoing TLS connection only with TLS 1.2 or
  later, and it fails the connection where the other side offers TLS 1.1 or older.

### Implementation notes

Adds no requirement. Leaving the minimum version unset meets R1 with the default of the Go toolchain that builds
token-gate. Setting `MinVersion` to `tls.VersionTLS12` on the `tls.Config` of each client makes R1 hold without
depending on that default. A test can start a TLS server that accepts TLS 1.1 only and check that the connection fails.

### Justification

TLS 1.0 and 1.1 are deprecated, and a client that accepts them can be downgraded to a protocol with known weaknesses
(R1).

## Consequences

Negative:

- An identity provider or another host that supports TLS 1.1 or older only cannot be called by token-gate (R1).

## Open points

- **O1.** Which components of token-gate open outgoing TLS connections? The rule assumes the calls to the identity
  provider from `internal/verify`, and the layer tags `verify` and `server` rest on that. The security architect,
  `example-security-architect`, decides, and a maintainer who can read the code answers. It affects R1.
````

### Message to the user

I wrote the ADR as `Proposed`, with one rule, R1.

- **A decision, not a default.** The notes say Go already refuses TLS 1.1 and older. I still wrote R1, because the architect chose the requirement, and a default can change with a toolchain upgrade. R1 states the guarantee to callers and does not name `MinVersion`. The Implementation notes recommend setting `MinVersion` explicitly, so that R1 does not depend on the Go default.
- **Open point.** O1 asks which components open outgoing TLS connections. I could not read the code, so I tagged R1 with `verify` and `server`. Please confirm or correct the layers. This blocks `Accepted`.
- **No Confirmation entry.** No check exists yet. A test against a TLS server limited to TLS 1.1 would confirm R1, and I can add it to Confirmation when it lands.
- **Owner.** I left the Owner as the placeholder `<owner account>`. Tell me the GitHub account. I assumed `example-security-architect` approves R1.
