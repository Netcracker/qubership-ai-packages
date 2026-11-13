## Request 1

### File: docs/adr/0007-support-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate is a Go service that checks the token of each request before policy evaluation. It ships as a container
image, built by `build/token-gate/Dockerfile`, and as a Helm chart. Some operators run containers under Docker without
Kubernetes. Under Docker, they configure a container with environment variables and mounted files.

Under Docker, operators need to trust a private CA for the HTTPS calls to the identity provider. The image builds on
the platform base image `ghcr.io/example/platform-base`. The README of the base image states its contract: its
entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to
the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. The platform's guide
for service images says to keep that entrypoint and to set the service's binary as `CMD`. On every image of the
platform that follows the guide, an operator trusts a private CA by mounting its certificate under `/tmp/cert`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, and start a Compose example of that setup on every pull request.

### Terms

- **Compose example**: the Compose file under `deploy/docker/` that R3 requires.

### Rules

#### Running without Kubernetes

- **R1** (`server`). token-gate reads each of its settings from an environment variable or from a file in the file
  system of its container, and from no other source.
- **R2** (`server`). token-gate starts and returns HTTP 200 for `GET /ready` in a container where no Kubernetes API
  server is reachable and no Kubernetes service account token is mounted.

#### The Compose example

- **R3** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from the image that
  `build/token-gate/Dockerfile` builds, and gives token-gate its settings only as environment variables and mounted
  files.
- **R4** (`ci`). A workflow under `.github/workflows/` runs on every pull request, builds the image of token-gate from
  the pull request, starts the Compose example with that image, sends `GET /ready` to token-gate, and fails when the
  response status is not 200.

### Confirmation

- **R2**: the workflow of R4 shows R2 for the container that the Compose example starts.
- **R3**: the workflow of R4 fails when the Compose example does not start.

### Implementation notes

Adds no requirement. In the workflow, `docker compose up --wait` starts the Compose example and waits for its health
checks. A request with `curl --silent --output /dev/null --write-out '%{http_code}'` then gives the status of
`GET /ready` to compare with 200.

### Justification

Under Docker, environment variables and mounted files are the configuration that `docker run` and Compose provide, and
a source such as the Kubernetes API is not there (R1, R2). The Compose example gives operators a setup that works as
shipped (R3). Starting it on every pull request finds a change that breaks the Docker setup before it merges, where a
test of the chart alone would not (R4).

### Alternatives considered

- **A1. Keep Kubernetes, through the Helm chart, as the only supported way to run token-gate.** Rejected by R2:
  operators without Kubernetes could not run token-gate.

## Consequences

Positive:

- A developer can start token-gate on a workstation with `docker compose up` in `deploy/docker/`.

Negative:

- A setting that needs another source, such as a command-line flag or the Kubernetes API, is not available to
  token-gate (R1).
- Every pull request waits for the workflow of R4, and a change that breaks only the Compose example fails CI even
  where the chart still works.

## Open points

- **O1.** R2 and R4 assume that `GET /ready` returns HTTP 200 when token-gate is ready. `example-architect` decides
  whether HTTP 200 is the right status, or whether any 2xx status counts as ready. Affects R2 and R4.
````

### Message to the user

I drafted ADR-0007 with the status `Proposed`. I named the file after the pattern `0001-tool-for-password-management.md`, so rename it if your records use a different pattern. Open point O1 (which status of `GET /ready` counts as ready) has to be settled before the record can be accepted.

I left the entrypoint question out of the record because there's no real decision to make: the code departs from a contract. The base image README and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` follows that with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue gives a reason. The Context section states the base image's `/tmp/cert` behavior as a fact, and the record has no rule for it. I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform base entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body:** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. This breaks the contract of `ghcr.io/example/platform-base`, whose README says `/usr/bin/entrypoint.sh` adds the certificates under `/tmp/cert` to the trust store and runs `/app/init.d`. The platform's guide for service images says to keep that entrypoint and set the binary as `CMD`, which `build/token-admin/Dockerfile` already does. The fix needs one more change: the chart runs the Pod with a read-only root file system, so it must mount `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, where the entrypoint writes.

Should I open this issue, or does one already report it? If the `ENTRYPOINT` line is deliberate, tell me and I'll add a rule for it with its reason.

Two more questions:

- R1 follows the notes ("environment variables and mounted files alone"), so it excludes command-line flags. Is that what you meant?
- I tagged R1 and R2 as `server` without reading where configuration loading lives. Is that the right layer?

## Request 2

### File: docs/adr/0007-refuse-none-and-hmac-algorithms.md

````markdown
# Refuse tokens whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

`internal/verify` verifies the signatures of tokens with the `jwx` library. When `jwx` verifies a signature, it refuses
a token whose `alg` is `none`. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key.
`internal/verify` passes `jwx` every key that the JWKS of an issuer holds. So a token signed with HMAC passes
verification whenever the JWKS of its issuer holds a symmetric key. Anyone who can read that JWKS holds the key.

## Decision

We will refuse a token whose algorithm is `none` or `HS256`, `HS384`, or `HS512`, each with HTTP 401 and a reason code
of its own.

### Terms

- **algorithm of a token**: the value of the `alg` parameter in the JOSE header of the token, compared byte for byte,
  because RFC 7515, section 4.1.1, makes the value case-sensitive. `None` and `hs256` are not algorithms that R1 or R2
  names.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose algorithm is `none` with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose algorithm is `HS256`, `HS384`, or `HS512` with HTTP 401
  and the reason code `TOKEN_ALG_SYMMETRIC`, also where a key in the JWKS of the token's issuer verifies its signature.

#### Precedence

- **R3** (`verify`). Where a token fails R1 or R2 and also fails another check, token-gate refuses it with the reason
  code of R1 or R2.

### Implementation notes

Adds no requirement. Read `alg` from the protected header before calling `jwx`, and return the error for R1 or R2
there, so that `jwx` never verifies such a token. Removing keys whose `kty` is `oct` from the key set passed to `jwx`
also stops HMAC verification. On its own, though, that change gives a `jwx` error and not `TOKEN_ALG_SYMMETRIC`.

### Justification

`jwx` already refuses `none`, but under its general verification error. A reason code of its own separates an unsigned
token from a token whose signature fails (R1). With HMAC, the key that verifies a token can also sign one. A symmetric
key in a JWKS can be read by whoever fetches the JWKS, so any of those readers could sign a token that token-gate would
accept (R2). The algorithm check needs only the header, and it gives a forged token the same reason code whatever its
claims hold (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate.** Rejected by R2: every holder of the
  shared secret, token-gate included, can sign a token for that issuer.

## Consequences

Negative:

- token-gate used to accept a token signed with `HS256`, `HS384`, or `HS512` when the JWKS of its issuer held a
  symmetric key. After this change, it refuses that token with HTTP 401 (R2). The issuer has to switch to an asymmetric
  algorithm. A test that signs a token with `HS256` against a JWKS that holds a key with `kty` `oct` shows the change.

## Open points

- **O1.** R3 assumes that the reason code of R1 or R2 wins over the reason code of every other check, such as a check
  of expiry. The alternative is to let some other check win. `example-security-architect` decides. Affects R3.
````

### Message to the user

I drafted ADR-0007 with the status `Proposed`. Open point O1 has to be settled before the record can be accepted. The notes don't say which reason code a token gets when it fails both the algorithm check and another check, such as expiry. I wrote R3 assuming the algorithm code wins.

The notes give no reasons for the decision. I based the Justification on facts about the repository: `internal/verify` passes every JWKS key to `jwx`, and anyone who can read a JWKS holds a symmetric key in it. Please confirm these are the reasons the security review had.

The code doesn't meet R2 yet. `jwx` accepts `HS256`, `HS384`, and `HS512` when the JWKS of an issuer holds a symmetric key. I tagged R1 and R2 as `verify` and `server` without reading which layer sets the HTTP status and the reason code. Please correct the tags if that work lives in one layer only.

## Request 3

### File: docs/adr/0007-tls-1-2-minimum-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for the outgoing TLS connections of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, for example to fetch the JWKS of an issuer. When a `tls.Config` leaves
`MinVersion` at zero, Go's `crypto/tls` client uses TLS 1.2 as the minimum version and refuses TLS 1.1 and older. The
documentation of `Config.MinVersion` describes this as the current default. token-gate sets no minimum version of its
own.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection in which the token-gate process is the client, whatever code opens it,
  a library included.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate completes the handshake of an outgoing TLS connection only at TLS 1.2 or
  later. Where the server offers only TLS 1.1 or older, the handshake fails, and token-gate sends no request on that
  connection.

### Implementation notes

Adds no requirement. Go's default meets R1 for every `tls.Config` whose `MinVersion` is zero, so the code needs no
change today. Code that builds a `tls.Config` should leave `MinVersion` at zero or set it to `tls.VersionTLS12` or
later. To test R1, start an `httptest.NewUnstartedServer` whose `TLS.MaxVersion` is `tls.VersionTLS11`, and check that
the client of token-gate fails the handshake.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). With a rule in place, a `tls.Config` that lowers `MinVersion` is a
violation that review can find. Go's documentation calls TLS 1.2 the current default, so a later Go release or a
library with its own `tls.Config` could change it without notice (R1).

### Alternatives considered

- **A1. Set `MinVersion: tls.VersionTLS12` explicitly in every `tls.Config` of token-gate.** R1 states the outcome
  and leaves the mechanism free, and Go's default already meets it.

## Consequences

Negative:

- token-gate cannot connect to an issuer or any other server that supports only TLS 1.1 or older (R1).
````

### Message to the user

I drafted ADR-0007 with the status `Proposed`. It has no open points, so the team can accept it once it signs off. On acceptance, add the Date heading.

The code already meets R1 through Go's default, so the rule matters for future changes. A change that builds a `tls.Config` with a lower `MinVersion`, or adds a library that does, would violate it.

I tagged R1 as `verify` and `server` without reading which packages open outgoing connections. Please correct the tags if the client code lives in only one of them.
