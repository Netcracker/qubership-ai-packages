## Request 1

### File: docs/adr/0007-support-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart.
Some operators run containers with Docker on hosts that have no Kubernetes, and they need a supported way to run
token-gate there.

Under Docker, token-gate calls the identity provider over HTTPS, and operators need to trust a private CA for those
calls. The image of token-gate builds on the platform base image `ghcr.io/example/platform-base`. The README of that
base image states its contract: its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`,
or `.pem` file under `/tmp/cert` to the trust store of the container, runs the scripts in `/app/init.d`, and then runs
its arguments. Operators trust a private CA for every image of the platform by mounting its certificate under
`/tmp/cert`, and they do the same for token-gate.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, and we will ship a Compose example that CI starts on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker Engine runs, directly or through Docker Compose, on a host
  where no Kubernetes control plane manages the container.
- **setting**: a value that an operator chooses and that token-gate reads to decide its behavior, such as an address,
  an issuer, or a timeout.
- **Compose example**: the Compose file under `deploy/docker/` that R3 requires.

### Rules

#### Configuration and start

- **R1** (`server`). token-gate reads every setting from an environment variable or from a file. It reads no setting
  from the Kubernetes API.
- **R2** (`server`). token-gate starts and serves requests in a Docker deployment where no Kubernetes service account
  token is mounted and no environment variable whose name starts with `KUBERNETES_` is set.

#### Compose example and its check

- **R3** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from its container image and passes
  every setting to token-gate as an environment variable or as a mounted file.
- **R4** (`ci`). A job in `.github/workflows/` runs on every pull request, starts the Compose example with the
  token-gate image built from the head commit of the pull request, and calls `GET /ready`. The job fails where
  `GET /ready` does not return HTTP 200.

### Confirmation

- **R2**: the job of R4, which starts token-gate in a Docker deployment and fails where token-gate does not become
  ready.
- **R3**: the job of R4, which fails where the Compose example does not start token-gate.

### Implementation notes

Adds no requirement. Show in the Compose example how to mount a CA certificate under `/tmp/cert`, for example as a
commented-out volume, because operators look for that mount first. Where token-gate needs an issuer before it reports
ready, the Compose example can start a stub issuer that serves a JWKS, so that the job of R4 needs no network access
outside the runner.

### Justification

Environment variables and mounted files are the two inputs that both Docker and Kubernetes give a container, so one
image of token-gate serves both (R1, R2). The Compose example gives operators a working starting point (R3). Starting it
on every pull request catches a change that breaks a Docker deployment before the change merges (R4).

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Operators without Kubernetes would have no supported way to
  run it.
- **A2. Read settings from a ConfigMap or a Secret through the Kubernetes API.** Rejected by R1: a Docker deployment has
  no Kubernetes API to read from.

## Consequences

Positive:

- Developers can run token-gate on their own machines with the Compose example, without a Kubernetes cluster.

Negative:

- Every pull request builds the image and starts the Compose example, which adds that time to each CI run (R4).
- A setting that the chart takes from the Kubernetes API today has to reach token-gate as an environment variable or a
  file instead, for example through the downward API (R1).

Follow-ups:

- Document the Docker deployment for operators, including how to trust a private CA through a mount under `/tmp/cert`.

## Open points

- **O1.** R4 assumes that `GET /ready` returns HTTP 200 once token-gate is ready. If token-gate reports readiness with
  another answer, R4 names that answer instead. `example-architect` decides. Affects R4.
- **O2.** R4 assumes that the job starts the Compose example with the image built from the head commit of the pull
  request. The other answer under consideration is the latest published image, which would not test the change itself.
  `example-architect` decides. Affects R4.
````

### Message to the user

I wrote `docs/adr/0007-support-docker-without-kubernetes.md` with the status `Proposed`. Two open points block acceptance: O1 asks whether `GET /ready` signals readiness with HTTP 200, and O2 asks whether the CI job uses the image built from the pull request.

The record has no rule for the question your notes left open (binary as entrypoint, or the base entrypoint with the binary as `CMD`). The platform contract already answers it. The README of `ghcr.io/example/platform-base` and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and to set the service's binary as `CMD`. `build/token-admin/Dockerfile` follows that contract. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains why. Because of that, certificates mounted under `/tmp/cert` never reach token-gate's trust store. That makes this a defect rather than a decision, so I propose an issue instead of a rule:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body:** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. The README of `ghcr.io/example/platform-base` and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` as the entrypoint and to set the service's binary as `CMD`, the way `build/token-admin/Dockerfile` does. With the binary as the entrypoint, the certificates under `/tmp/cert` are never added to the trust store, and the scripts in `/app/init.d` never run. The fix is to remove the `ENTRYPOINT` line and set `CMD ["/usr/local/bin/token-gate"]`. The base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, and the chart runs the Pod with a read-only root file system. So the chart also needs `emptyDir` volumes mounted at both paths.

If keeping the binary as the entrypoint is deliberate, tell me why and I'll add it as a rule with that reason.

Some questions:

- Who else approves this record besides `example-architect`? For example, the maintainers of the chart or of CI.
- I tagged R1 and R2 `server` without seeing the code. If configuration loading lives outside `internal/server`, the tag needs to change, and the reading guide may need a new path.
- I used the metadata block of the skill's template because I couldn't see the records 0001 to 0006. If their metadata block differs, the new record should match theirs.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md

````markdown
# Refuse tokens whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an
issuer holds. A token signed with an HMAC algorithm therefore passes verification where the JWKS of its issuer holds the
symmetric key it was signed with.

## Decision

We will refuse a token whose algorithm is `none` or an HMAC algorithm with HTTP 401 and a reason code for each case.

### Terms

- **token**: the token that token-gate checks for a request before policy evaluation.
- **algorithm of a token**: the value of the `alg` parameter in the JOSE header of the token, compared as an exact,
  case-sensitive string.
- **HMAC algorithm**: `HS256`, `HS384`, or `HS512`.
- **reason code**: the machine-readable code that a 401 response of token-gate carries to name why token-gate refused
  the token.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate answers a request whose token has the algorithm `none` with HTTP 401 and the
  reason code `TOKEN_ALG_NONE`, and does not pass the request to policy evaluation.
- **R2** (`verify`, `server`). token-gate answers a request whose token has an HMAC algorithm with HTTP 401 and the
  reason code `TOKEN_ALG_SYMMETRIC`, and does not pass the request to policy evaluation, whatever keys the JWKS of the
  token's issuer holds.

#### Precedence

- **R3** (`verify`). Where the algorithm of a token is `none` or an HMAC algorithm, the 401 response carries
  `TOKEN_ALG_NONE` or `TOKEN_ALG_SYMMETRIC` also when the token fails another check, such as its expiry or its issuer.

### Implementation notes

Adds no requirement. Read `alg` from the protected header and check it before the signature is verified, so that R3
holds whatever order `jwx` runs its own checks in. Leaving symmetric keys out of the key set that `internal/verify`
passes to `jwx` adds a second guard. On its own it does not meet R2, because the token would then fail with the reason
code of a failed signature.

### Justification

A token with the algorithm `none` carries no signature, so it proves nothing about its issuer. A reason code of its own
lets operators tell such a token apart from an expired or a malformed one (R1). A JWKS is public, so anyone who can
fetch it can read a symmetric key it holds and sign a token with that key. An HMAC signature from such a key proves
nothing about the issuer (R2). The algorithm is the cause of the refusal whatever else is wrong with the token, so its
reason code wins (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate.** Rejected by R2: every holder of the
  secret, token-gate included, could sign tokens for that issuer.
- **A2. Leave the refusal of `none` to `jwx`.** Rejected by R1, which requires the reason code `TOKEN_ALG_NONE` rather
  than the code of a failed signature.

## Consequences

Positive:

- Operators can count attempts with `none` and with HMAC algorithms by their reason codes, apart from expired or
  malformed tokens.

Negative:

- On upgrade, every token signed with an HMAC algorithm gets HTTP 401 with `TOKEN_ALG_SYMMETRIC`, also where the JWKS of
  its issuer holds the symmetric key (R2). A test that signs a token with `HS256` and a symmetric key from the issuer's
  JWKS shows the change.
- A token with the algorithm `none` gets the reason code `TOKEN_ALG_NONE` instead of the code it got before (R1). A
  client that matches the old code has to match the new one.

## Open points

- **O1.** R3 assumes that the reason codes of R1 and R2 win over the reason code of every other check. The other answer
  under consideration is that another check, such as the issuer, wins. `example-security-architect` decides. Affects
  R3.
- **O2.** The term **algorithm of a token** assumes an exact, case-sensitive comparison, so a token with `None` or
  `NONE` falls outside R1. The other answer is a case-insensitive comparison, which brings such a token under R1.
  `example-security-architect` decides. Affects R1 and R2.
- **O3.** R1 and R2 assume that a 401 response of token-gate already carries a reason code in a place that an existing
  record or the API reference fixes. Where nothing fixes it, this record needs a rule that names the field.
  `example-security-architect` decides with the owner of the API. Affects R1 and R2.
````

### Message to the user

I wrote `docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md` with the status `Proposed`. Three open points block acceptance:

- O1: which reason code wins when a token also fails another check.
- O2: whether `alg` is compared case-sensitively.
- O3: where a 401 response carries its reason code.

The code doesn't meet R2 today. `internal/verify` passes `jwx` every key in an issuer's JWKS, so a token signed with `HS256` and a symmetric key from that JWKS passes. R1 needs work too: `jwx` already refuses `none`, but the response has to carry `TOKEN_ALG_NONE`.

Some questions:

- Your notes don't say why the per-issuer shared secret was rejected. The reason in A1 is mine (every holder of the secret could sign tokens). Please confirm it or give me the real reason.
- I couldn't read the records 0001 to 0006. If one of them states which signature algorithms token-gate accepts, this record has to supersede that part by rule number. Which record, if any, is it?
- Who else approves this record besides `example-security-architect`?

## Request 3

### File: docs/adr/0007-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, such as its HTTPS calls to the identity provider. Go's `crypto/tls`
client refuses TLS 1.1 and older by default, where `tls.Config.MinVersion` is zero. token-gate sets no minimum version
of its own, so the minimum it uses is that default. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection in which the token-gate process is the client, including a connection
  that a library opens inside that process. A connection that token-gate accepts as a server is not an outgoing TLS
  connection.

### Rules

#### TLS version

- **R1** (`server`, `verify`). token-gate uses TLS 1.2 or later on every outgoing TLS connection. Where the server
  supports no version of TLS 1.2 or later, the handshake fails, and token-gate sends no request on the connection.

### Implementation notes

Adds no requirement. The default of Go's `crypto/tls` client meets R1 while that default holds. Setting
`MinVersion: tls.VersionTLS12` in each `tls.Config` that token-gate builds keeps R1 met if a later Go release or a
`GODEBUG` setting changes the default. A test that points a client of token-gate at a server limited to TLS 1.1, and
expects a failed handshake, can be added under **Confirmation** once it exists.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1, and a connection that uses either one doesn't protect the token-gate calls to
the identity provider to the level the platform expects (R1).

### Alternatives considered

- **A1. Allow TLS 1.0 or TLS 1.1 for a server that supports nothing newer, such as through a setting for the minimum
  version.** Rejected by R1.

## Consequences

Negative:

- token-gate cannot reach a server that supports only TLS 1.1 or older, such as an old identity provider (R1).
````

### Message to the user

I wrote `docs/adr/0007-tls-1-2-or-later-for-outgoing-connections.md` with the status `Proposed`. It has no open points, so you can set it to `Accepted` and add the Date heading once the team signs off.

R1 is a rule even though Go's default already meets it. The security architect chose TLS 1.2 for this system, and the record should keep that choice if the default changes. The code meets R1 today without changes. The implementation notes recommend setting `MinVersion` explicitly and adding a handshake test, which would go under **Confirmation** when it lands.

Some questions:

- I tagged R1 with `server` and `verify` without seeing the code, assuming those are the packages that open outgoing connections (for example, the JWKS fetch). If another package opens them, the tags need to change.
- I couldn't read the records 0001 to 0006. If one of them already sets a TLS version for outgoing connections, this record has to supersede that part. Is there one?
- Who else approves this record besides `example-security-architect`?
