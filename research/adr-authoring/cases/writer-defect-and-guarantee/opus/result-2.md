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

token-gate ships as a container image and a Helm chart. The repository ships no way to run token-gate under Docker
without Kubernetes.

Under Docker, operators need to trust a private CA for the HTTPS calls that token-gate makes to the identity provider.
On every image of the platform, operators do this by mounting the CA certificate under `/tmp/cert`. The token-gate image
builds on the platform base image `ghcr.io/example/platform-base`. The README of that base image states its contract:
the entrypoint `/usr/bin/entrypoint.sh` adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to
the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
The repository will ship a Compose example, and CI will start it on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker Engine runs, directly or through Docker Compose, with no
  Kubernetes cluster involved.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads each of its settings from an environment variable or from a file in the file
  system of its container, and reads no setting from the Kubernetes API.

#### Compose example

- **R2** (`docker`). `deploy/docker/` holds a Docker Compose file that starts token-gate as a Docker deployment and
  configures it only with environment variables and with files mounted into the container.

#### Continuous integration

- **R3** (`ci`). A job in a workflow under `.github/workflows/` runs on every pull request. It starts the Compose file
  in `deploy/docker/` with the token-gate image built from the commit of the pull request, and sends `GET /ready` to
  token-gate. The job fails when the call gets no response or a status other than `200`.

### Implementation notes

Adds no requirement. In the Compose file, let an environment variable choose the token-gate image, so that the CI job
can start the image it has just built. Mount a directory read-only at `/tmp/cert` in the example, so that operators can
see where a private CA certificate goes. In the CI job, wait for the container to start before the call to `GET /ready`,
and print the container logs when the job fails.

### Justification

Docker and Kubernetes both provide environment variables and mounted files, so a setting that comes only from those
reaches token-gate in either deployment (R1). The Compose example gives operators a configuration that works, and gives
CI a configuration to start (R2). A Docker deployment that no check starts breaks without notice, for example when a
change adds a setting that only the chart provides. The job catches that change before it merges (R3).

### Alternatives considered

- None recorded in the architecture meeting.

## Consequences

Negative:

- Every pull request pays for an image build and a start of the Compose example (R3).
- token-gate cannot take a setting from a Kubernetes object through the Kubernetes API, even when it runs under the
  chart (R1).

## Open points

- **O1.** R3 assumes that the job passes only on status `200` from `GET /ready`. The answers under consideration are
  `200` only, or any `2xx` status. `example-architect` decides. Affects R3.
- **O2.** R3 assumes that the job starts the image built from the commit of the pull request. The other answer is the
  latest released image, and then the job checks only the Compose file. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. O1 and O2 are assumptions I made in R3 (the `200` status and the image built from the pull request). The record can't be accepted until `example-architect` confirms or changes them.

I didn't record the meeting's open question about the entrypoint, because the platform contract already answers it. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains that line. The base image's README and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`, and `build/token-admin/Dockerfile` already does that. This is a defect, not a decision, so I suggest opening this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Contract it departs from:** the README of `ghcr.io/example/platform-base` (its entrypoint adds every `.crt`, `.cer`, and `.pem` file under `/tmp/cert` to the trust store, runs `/app/init.d`, then runs its arguments) and the platform's guide for service images (keep that entrypoint and set the service's binary as `CMD`).
- **Fix:** replace the `ENTRYPOINT` line in `build/token-gate/Dockerfile` with `CMD ["/usr/local/bin/token-gate"]`. The chart's Pod has a read-only root file system, so it also needs `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, because the entrypoint writes there. Check whether the chart sets `args` or `command` for the container. With the binary as `CMD`, `args` would replace the binary and `command` would bypass the platform entrypoint.

If someone knows a deliberate reason for that `ENTRYPOINT` line, tell me. Then it is a decision, and I'll add a rule for it.

Questions:

- Who else approves this record? For example, whoever owns the CI workflows or the Compose example.
- I tagged R1 `server` without seeing the code. If settings are loaded somewhere else, which layer should it have?
- The meeting notes list no alternatives. Were any discussed that I should record?

## Request 2

### File: docs/adr/0007-refuse-request-tokens-with-alg-none-or-hmac.md

````markdown
# Refuse a request token whose algorithm is `none` or HMAC, with HTTP 401 and a reason code for each

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the signature of that
token with the `jwx` library.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It reports that refusal like any other failed
verification, so the response does not say that the algorithm caused it.

`jwx` accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key. `internal/verify` passes `jwx` every
key that the JWKS of an issuer holds. A JWKS is published to every client of the issuer, so a symmetric key in it can be
read by anyone who fetches the JWKS, and anyone who reads it can sign a token that token-gate accepts.

## Decision

We will refuse a request token whose algorithm is `none` or one of the HMAC algorithms, with HTTP 401 and a reason code
for each case.

### Terms

- **request token**: the token that token-gate checks for a request before policy evaluation.
- **`alg`**: the `alg` parameter of the protected JOSE header of a request token, compared as an exact, case-sensitive
  string.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). When the `alg` of a request token is `none`, token-gate responds to the request with HTTP
  401 and the reason code `TOKEN_ALG_NONE`, and does not pass the request to policy evaluation.
- **R2** (`verify`, `server`). When the `alg` of a request token is `HS256`, `HS384`, or `HS512`, token-gate responds to
  the request with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, and does not pass the request to policy
  evaluation. This holds for every issuer, whatever keys the JWKS of the issuer holds.

#### Precedence

- **R3** (`verify`). When a request token falls under R1 or R2 and would also fail another check of token-gate, such as
  an expiry check, the response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. Read `alg` from the protected header before calling `jwx` to verify the signature, and return a
distinct error for each case that the server maps to its reason code. Also leave symmetric keys (`kty` `oct`) out of the
key set that `internal/verify` passes to `jwx`, so that no other path can verify an HMAC signature.

Add these test cases:

- an unsigned token with `alg` `none`;
- a token signed with `HS256`, where the test JWKS holds the matching symmetric key;
- an expired token with `alg` `HS256`, for R3.

### Justification

A token with `alg` `none` carries no signature, so it shows nothing about who issued it. A reason code of its own lets
operators find such tokens in logs apart from tokens with a bad signature (R1). To verify an HMAC signature, the
verifier holds the key that creates it. A symmetric key in a JWKS is readable by every client of the issuer, and every
such client could then sign tokens (R2). A refusal based on the header alone gives the same answer whichever other check
fails, so the reason code depends on the token and not on the order of the checks (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate.** Rejected by R2: token-gate would hold a
  key that signs tokens for that issuer, so a leak of its configuration would let an attacker sign tokens. Each secret
  would also have to be distributed to token-gate and rotated.

## Consequences

Negative:

- An issuer that signs tokens with `HS256`, `HS384`, or `HS512` gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` for every
  request after the upgrade, even where its JWKS holds the symmetric key (R2). No test shows this yet.
- A request token with `alg` `none` gets `TOKEN_ALG_NONE`, where it got the reason code of a failed signature before
  (R1). Clients that match on the old reason code see a new one.

Follow-ups:

- Name the refusal of HMAC-signed tokens in the release notes of the version that brings R2, so that operators can
  check their issuers before the upgrade.

## Open points

- **O1.** R3 assumes that the reason code of R1 or R2 takes precedence over the reason code of every other failed check.
  The other answer is the reason code of whichever check token-gate runs first. `example-security-architect` decides.
  Affects R3.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. R3 sets which reason code wins when a token with `none` or HMAC also fails another check, such as expiry. The notes don't settle this, so I wrote it as an assumption, and O1 asks `example-security-architect` to confirm it. The record can't be accepted until that's settled.

R1 stays a rule even though `jwx` already refuses `none`. The decision is about the HTTP 401 and the `TOKEN_ALG_NONE` reason code, and `jwx` alone doesn't produce either.

Questions:

- Does one of ADR-0001 to ADR-0006 define the reason codes or the format of the 401 response? If so, I'll add it under **Related ADRs** and use its terms in R1 and R2.
- Who else approves this record?
- I tagged R1 and R2 `verify` and `server` on the assumption that `internal/verify` picks the reason code and `internal/server` writes the response. Is that where the code lives?

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

token-gate opens outgoing TLS connections, for example to fetch the JWKS of an issuer. It uses the client of Go's
`crypto/tls` and sets no minimum TLS version of its own, so Go's default applies. That default refuses TLS 1.1 and
older. Go's `GODEBUG` setting `tls10server=1` lowers the default minimum version to TLS 1.0, and the process environment
or a `godebug` line in `go.mod` can set it. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host.

### Rules

#### TLS version

- **R1** (`verify`, `server`). Every outgoing TLS connection of token-gate uses TLS 1.2 or later. Where the server at
  the other end offers no version from TLS 1.2 up, the handshake fails, and token-gate sends no application data on the
  connection. This holds for every value of the `GODEBUG` environment variable and of the `godebug` lines in `go.mod`.

### Implementation notes

Adds no requirement. Set `MinVersion: tls.VersionTLS12` in every `tls.Config` that token-gate uses for an outgoing
connection. That includes the `TLSClientConfig` of each `http.Transport`, which needs a `tls.Config` of its own for this
setting. To test it, start an `httptest.NewUnstartedServer`, set its `TLS.MaxVersion` to `tls.VersionTLS11`, call
`StartTLS`, and expect the client's request to fail during the handshake.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). A minimum version that token-gate sets itself stays in force when the Go
default changes, whether through the Go version or through a `GODEBUG` setting (R1).

### Alternatives considered

- None recorded in the security review.

## Consequences

Negative:

- token-gate cannot reach a host that offers only TLS 1.1 or older, such as an old identity provider (R1).
- An installation that sets `GODEBUG=tls10server=1` loses TLS 1.0 and TLS 1.1 on its outgoing TLS connections after
  the upgrade (R1).

## Open points

- **O1.** R1 assumes that the minimum version holds whatever the value of `GODEBUG` and of the `godebug` lines in
  `go.mod`, which needs code that sets the minimum version. The other answer is that R1 holds only under Go's default
  settings, which needs no code change, and then the last sentence of R1 and the second Negative item go.
  `example-security-architect` decides. Affects R1.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. It's a rule even though Go's default already meets it, because the security architect chose the minimum for this service.

O1 blocks acceptance. Go's default minimum can be lowered with `GODEBUG=tls10server=1`, so the decision is either:

- a guarantee that holds under every `GODEBUG` value, which means token-gate has to set `MinVersion` itself, or
- a guarantee that holds only under Go's default, which needs no code change.

I wrote R1 as the first option, and `example-security-architect` should confirm it.

Questions:

- The notes say "token-gate". Does the decision also cover `token-admin`, which the repository builds as a second image?
- I tagged R1 `verify` and `server` without seeing where token-gate opens its outgoing connections. Which layers hold that code?
- Who else approves this record?
