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

token-gate checks the token of each request before policy evaluation. The repository ships it as a container image and
a Helm chart, so the only documented way to run it is on Kubernetes. Operators who run containers with Docker alone
have no example of a supported setup, and nothing in CI starts the image outside the chart.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
The repository ships a Compose example under `deploy/docker/`, and a CI job starts it on every pull request and calls
`GET /ready`.

### Terms

- **mounted file**: a file in the container's file system that is not part of the image and that Docker mounts into the
  container, by a bind mount or a volume.
- **Compose example**: the Compose file under `deploy/docker/` that R2 requires.

### Rules

#### Running without Kubernetes

- **R1** (`server`). token-gate starts and serves requests with no Kubernetes API reachable and with no configuration
  source other than environment variables and mounted files.

#### The Compose example

- **R2** (`docker`). The repository holds a Compose example that starts token-gate with no Kubernetes component and
  supplies its configuration only through environment variables and mounted files.
- **R3** (`ci`). A CI job starts the Compose example on every pull request, whatever files the pull request changes,
  calls `GET /ready` on the started token-gate, and fails where the response status is not 200.

### Implementation notes

Adds no requirement. The job can poll `GET /ready` until it returns 200 or a timeout passes, so that a slow start does
not fail the job. It should stop the Compose project at the end, also when the call fails.

### Justification

Operators who run Docker without Kubernetes can use token-gate only if it needs nothing that Kubernetes supplies (R1).
A Compose example shows them a configuration that works (R2). A CI job that starts the example on every pull request
keeps the example and the image working together (R3).

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Operators without Kubernetes would have to build their own
  setup and could not rely on the repository to keep it working.

## Consequences

Positive:

- Operators without Kubernetes get a tested starting point.

Negative:

- Every pull request pays for one more CI job (R3).
- A change that makes token-gate depend on a Kubernetes API or on another configuration source breaks R1, even where the
  chart still works.

## Open points

- **O1.** R3 treats a response with status 200 from `GET /ready` as success. The security and platform owners can
  confirm that 200 is the only success status. The architect, `example-architect`, decides. It affects R3.
````

### Message to the user

I wrote the record as `Proposed`. O1 blocks acceptance: I assumed that `GET /ready` signals success with status 200. Please confirm or give the status.

The open question in the notes, whether to keep the binary as the entrypoint, is a defect and not a decision, so the record has no rule for it. The base image README and the platform guide for service images both say to keep the entrypoint `/usr/bin/entrypoint.sh` and to set the service binary as `CMD`. `build/token-admin/Dockerfile` already does this with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]` and has done so since its first commit, with no comment and no record or issue behind it. The record therefore leaves out the entrypoint, the `/tmp/cert` mount, and the chart volumes. If the departure is deliberate, tell me and I will write a rule for it.

Proposed issue (I found no existing issue that reports this):

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Description:** The README of `ghcr.io/example/platform-base` says that `/usr/bin/entrypoint.sh` adds every `.crt`, `.cer`, and `.pem` file under `/tmp/cert` to the trust store, runs the scripts in `/app/init.d`, and then runs its arguments. The platform guide for service images says to keep that entrypoint and to set the binary as `CMD`. `build/token-gate/Dockerfile` replaces the entrypoint, so a private CA mounted under `/tmp/cert` has no effect.
- **Fix:** Remove the `ENTRYPOINT` line and end the Dockerfile with `CMD ["/usr/local/bin/token-gate"]`.
- **Also in the issue:** The chart runs the Pod with a read-only root file system, and the base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. Add `emptyDir` volumes at those two paths under `helm/`.

R1 to R3 hold no code yet. The change that brings each rule should name it under `Implements`. A rule that waits for a later change goes under `Defers`, with an issue or pull request that exists. Tell me which issues to name and I will use them.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-algorithm-none-or-a-symmetric-algorithm.md

````markdown
# Refuse tokens whose algorithm is none or HMAC with a distinct reason code

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library and passes it every key that the JWKS of an issuer holds. `jwx` refuses a token whose `alg` is `none` when
it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key. A symmetric key
in the JWKS of an issuer therefore makes token-gate accept an HMAC-signed token.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and a
token signed with `HS256`, `HS384`, or `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`.

### Terms

- **refuse a token**: token-gate does not pass the request to policy evaluation, and the response carries the stated
  HTTP status and reason code.

### Rules

#### Algorithms that token-gate refuses

- **R1** (`verify`, `server`). token-gate refuses a token whose `alg` header parameter is exactly `none` with HTTP 401
  and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose `alg` header parameter is `HS256`, `HS384`, or `HS512`
  with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, also where the JWKS of the issuer holds a symmetric key with
  which the signature would verify.

### Implementation notes

Adds no requirement. `internal/verify` can read the `alg` header parameter before it calls `jwx` and return the refusal
for R1 or R2 from there. `jwx` already refuses `none`, but its error carries neither the status nor the reason codes.
For R2, the code can also leave symmetric keys out of the key set it passes to `jwx`.

### Justification

A token with `alg` `none` carries no signature, and a distinct reason code lets an operator tell that refusal from a
failed verification (R1). A symmetric key in a JWKS would otherwise make token-gate accept HMAC-signed tokens, because
`internal/verify` passes every key of the JWKS to `jwx`. R2 closes that path and gives the refusal its own reason code.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: the security review declined it. O2 asks for the
  reason.

## Consequences

Positive:

- Every token with a symmetric algorithm is refused whatever keys an issuer publishes.

Negative:

- A token signed with `HS256`, `HS384`, or `HS512` that token-gate accepted before is now refused with HTTP 401 (R2).
  This affects every issuer whose JWKS holds a symmetric key and whose tokens use such an algorithm.

## Open points

- **O1.** R1 compares the `alg` value exactly, so `None` and `NONE` are not covered by R1. The security architect,
  `example-security-architect`, decides whether R1 also covers other spellings. It affects R1.
- **O2.** The notes record that accepting HMAC with a shared secret per issuer was rejected, and not why. The security
  architect decides the wording of the reason. It affects A1 and the Justification of R2.
- **O3.** The notes do not say how the response carries a reason code. I assumed that it is carried the same way as the
  reason codes of other refusals. The security architect decides. It affects R1 and R2.
````

### Message to the user

I wrote the record as `Proposed`. Three open points block acceptance:

- **O1:** whether `None` or `NONE` also counts as `none`. I assumed the exact string.
- **O2:** the reason for rejecting HMAC with a shared secret per issuer. The notes give none, so I did not invent one.
- **O3:** how a response carries a reason code. I assumed it matches the other refusals. Tell me the existing mechanism and I will name it.

I kept the refusal of `none` as a rule even though `jwx` already refuses that token. The status and the reason code `TOKEN_ALG_NONE` are token-gate's own decision. The Negative consequence names the case that changes: an issuer whose JWKS holds a symmetric key and whose HS256, HS384, or HS512 tokens were accepted before now gets 401.

**Confirmation** is left out because I know of no test for either rule. A table test in `internal/verify` that covers `none` and the three HMAC algorithms would be the natural check. Once it exists, the accepted record can gain that entry.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, such as the HTTPS calls to an identity provider. The `crypto/tls` client of
Go refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. The minimum version of
token-gate therefore follows the default of the Go toolchain that builds it.

## Decision

We will require TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that token-gate opens as the client, to any host.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate completes no TLS handshake on an outgoing TLS connection with a protocol
  version below TLS 1.2, whatever the minimum version in the Go default is.

### Implementation notes

Adds no requirement. The default of the `crypto/tls` client meets R1 today, so no code change is needed. Setting
`MinVersion` to `tls.VersionTLS12` on the `tls.Config` of each outgoing client would keep R1 true if the default
changes. A test that connects to a local TLS server limited to TLS 1.1 and expects the handshake to fail would show R1.

### Justification

TLS 1.1 and older have known weaknesses, and a security decision of the review should not depend on a default that a
toolchain upgrade can change (R1).

### Alternatives considered

- **A1. Rely on the Go default and record no requirement.** The minimum version then changes with the toolchain, and no
  check in the repository would show a regression.

## Consequences

Positive:

- The minimum protocol version is a recorded requirement that a change can be checked against.

Negative:

- An identity provider or other host that supports only TLS 1.1 or older cannot be reached (R1). The Go default already
  refuses it today.

## Open points

- **O1.** I assumed that the outgoing TLS connections of token-gate are made by code in `internal/verify` and
  `internal/server`. The security architect, `example-security-architect`, confirms which components open them. It
  affects the layer tags of R1.
````

### Message to the user

I wrote the record as `Proposed`. O1 blocks acceptance: I assumed that the outgoing connections come from `internal/verify` and `internal/server`, and I tagged R1 with both layers. If another package opens them, tell me which.

The default of the Go client already meets the requirement, but the security architect decided it, so it is a decision and not a dependency guarantee. That is why R1 states the contract and does not mention `MinVersion`. Because no code change is needed, any change that touches R1 can name it under `Implements`.

I wrote A1 and the Justification from the notes' facts, because the notes give no other reasons. Please check that they match what the review said. The notes cover only outgoing connections. Incoming TLS is not covered, so it stays the implementer's choice.
