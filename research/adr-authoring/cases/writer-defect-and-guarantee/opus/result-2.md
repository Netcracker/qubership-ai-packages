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

token-gate checks the token of each request before policy evaluation. It ships as a container image, built by
`build/token-gate/Dockerfile`, and as a Helm chart. The repository ships no way to run it outside Kubernetes. Some
operators want to run it under Docker on hosts that have no Kubernetes cluster.

Under Docker, a container gets its configuration from environment variables and from files mounted into it. Some
operators use an identity provider whose certificate comes from a private CA. For the HTTPS calls to that identity
provider, token-gate has to trust the CA. On the platform, operators do this by mounting the CA certificate under
`/tmp/cert`. The README of the base image `ghcr.io/example/platform-base` states its contract. Its entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container. It then runs the scripts in `/app/init.d`, and then runs its arguments. The platform's guide for
service images says to keep that entrypoint and to set the service's binary as `CMD`. Both images of this repository
build on that base image.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. A Compose example in the repository shows the setup, and CI starts it on every pull request.

### Terms

- **Kubernetes API**: the API server of any Kubernetes cluster, reached through any client or credential, including the
  service account token of a Pod.

### Rules

#### Configuration

- **R1** (`server`, `verify`). Every setting of token-gate can be given through an environment variable or a file.
- **R2** (`server`, `verify`). token-gate makes no call to the Kubernetes API.

#### The Compose example

- **R3** (`docker`). A Compose file under `deploy/docker/` starts token-gate and gives it every setting through an
  environment variable or a mounted file.
- **R4** (`ci`). A job in `.github/workflows/` runs on every pull request. It builds the image from
  `build/token-gate/Dockerfile` at the head commit of the pull request, starts the Compose file under `deploy/docker/`
  with that image, and calls `GET /ready` on token-gate. The job fails unless `GET /ready` returns HTTP 200 within
  `<readiness timeout>` of the start.

### Implementation notes

Adds no requirement. If `GET /ready` waits for the JWKS of an issuer, add a stub issuer to the Compose file. The job of
R4 then needs no identity provider outside the runner.

### Justification

Operators already configure every image of the platform through environment variables and mounted files. With these
alone, token-gate needs no Kubernetes object to run under Docker (R1, R3). A call to the Kubernetes API fails on a host
that has no cluster (R2). Support that no job exercises can break unnoticed. The job of R4 starts token-gate the way an
operator does, from the Compose file, on every pull request (R3, R4).

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Operators without a Kubernetes cluster could not run it.

## Consequences

Negative:

- Every pull request waits for the image build and the start of the Compose file (R4).
- A feature that needs the Kubernetes API, such as reading a ConfigMap through the API, needs a new record that
  replaces R2.

## Open points

- **O1.** The value of `<readiness timeout>` in R4. `example-architect` decides. Affects R4.
- **O2.** R4 assumes that the job tests the image built at the head commit of the pull request. The other answer is to
  start the latest published image, which leaves the change under review untested. `example-architect` decides.
  Affects R4.
- **O3.** R4 assumes that the job passes only when `GET /ready` returns HTTP 200. The other answer is any 2xx status.
  `example-architect` decides. Affects R4.
````

### Message to the user

I wrote the record as `docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md`, with the status
`Proposed`. Open points O1 to O3 block acceptance: the readiness timeout, whether the job tests the image built from
the pull request, and whether only HTTP 200 counts as ready.

I didn't put the entrypoint question in the record, because the platform contract already answers it. The base image's
README and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and to set the service's
binary as `CMD`. `build/token-admin/Dockerfile` follows that contract. `build/token-gate/Dockerfile` replaces the
entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue gives a reason. That makes it a
defect to fix, not a decision to record. I propose this issue:

- **Type**: Bug
- **Title**: The token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body**: `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. This replaces
  `/usr/bin/entrypoint.sh` of `ghcr.io/example/platform-base`. As a result, certificates mounted under `/tmp/cert` never
  reach the trust store, and the scripts in `/app/init.d` never run. The base image's README and the platform's guide
  for service images say to keep the base entrypoint and to set the binary as `CMD`, as `build/token-admin/Dockerfile`
  does. Fix: replace the line with `CMD ["/usr/local/bin/token-gate"]`. The chart runs the Pod with a read-only root
  file system, and the base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. So the chart
  also needs an `emptyDir` volume mounted at each of those paths.

Until that issue is fixed, operators can't make token-gate trust a private CA under Docker. If the binary entrypoint is
deliberate, tell me the reason and I'll add it to this record as a rule.

Questions:

- Should anyone else approve this record, such as whoever maintains the CI workflows?
- The notes don't name any alternatives. I added A1, "support token-gate only through the Helm chart", because it's
  the current state. Does that match what the meeting weighed?

## Request 2

### File: docs/adr/0007-refuse-tokens-whose-algorithm-is-none-or-hmac.md

````markdown
# Refuse tokens whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the signature of a
token with the `jwx` library. It passes `jwx` every key that the JWKS of the token's issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when
the key set holds a symmetric key. HMAC verifies a token with the same key that signs it. So any party that can read a
symmetric key in the JWKS of an issuer can sign a token that `internal/verify` accepts for that issuer.

## Decision

We will refuse every token whose algorithm is `none`, `HS256`, `HS384`, or `HS512`, with HTTP 401 and a reason code
that names the cause.

### Terms

- **`alg`**: the value of the `alg` parameter in the protected header of the token of a request.
- **refuses**: token-gate responds to the request with HTTP 401 and the reason code that the rule names, and the request
  does not reach policy evaluation. `internal/verify` meets a rule that uses this word by returning an error that
  carries the reason code.

### Rules

#### Algorithms

- **R1** (`verify`, `server`). token-gate refuses a request whose `alg` is `none`, compared without regard to letter
  case, with the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a request whose `alg` is `HS256`, `HS384`, or `HS512`, compared
  without regard to letter case, with the reason code `TOKEN_ALG_SYMMETRIC`. This holds whatever keys the JWKS of the
  token's issuer holds.

#### Precedence and upgrade

- **R3** (`verify`, `server`). Where the token of a request fails R1 or R2 and also fails another check of token-gate,
  the response carries the reason code of R1 or R2.
- **R4** (`verify`, `server`). No setting of token-gate turns off R1 or R2. An installation refuses the requests that R1
  and R2 describe from the first release that contains those rules.

### Implementation notes

Adds no requirement. Read `alg` from the protected header before `internal/verify` calls `jwx`, and return an error
that carries the reason code. The error `jwx` returns for `none` carries no reason code of token-gate. Leaving symmetric
keys out of the key set that `internal/verify` passes to `jwx` also stops HMAC tokens from passing verification. On its
own, though, that change returns the generic error of `jwx` and not `TOKEN_ALG_SYMMETRIC`. A table test in
`internal/verify` can cover each algorithm of R1 and R2 in lowercase, uppercase, and mixed case.

### Justification

A token whose `alg` is `none` carries no signature, so nothing shows that its issuer produced it (R1). A symmetric key
in a JWKS can sign as well as verify, so any party that can read the JWKS can sign tokens for that issuer (R2). A
separate reason code for each cause tells an operator which algorithm a refused client used (R1, R2, R3). A setting that
turned the refusal off would bring back the tokens that R1 and R2 refuse (R4).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2. Every party that holds the secret of an issuer,
  token-gate included, could sign tokens for that issuer, and token-gate would have to store and rotate one secret per
  issuer.

## Consequences

Negative:

- An issuer might sign tokens with `HS256`, `HS384`, or `HS512` and publish a symmetric key in its JWKS. Requests with
  such a token got through `internal/verify` before. They now get HTTP 401 with `TOKEN_ALG_SYMMETRIC` (R2, R4). Such an
  issuer has to move to an asymmetric algorithm before the installations that trust it upgrade.
- The response to a request whose `alg` is `none` now carries `TOKEN_ALG_NONE` (R1). A client that matches on the
  reason code of that refusal sees the new code.

Follow-ups:

- Name the refusal of HMAC tokens in the release notes of the first release that contains R2. Operators can then find
  issuers that sign with HMAC before they upgrade.

## Open points

- **O1.** R1 and R2 assume that `alg` is compared without regard to letter case, so that `None` and `hs256` also get
  the reason codes. The other answer is exact comparison, where such a token gets whatever refusal `jwx` produces.
  `example-security-architect` decides. Affects R1 and R2.
- **O2.** R3 assumes that R1 and R2 take precedence over every other check, such as expiry. The other answer is that
  the checks of earlier records come first. `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-refuse-tokens-whose-algorithm-is-none-or-hmac.md`, with the status `Proposed`.
Open points O1 (letter case of `alg`) and O2 (which reason code wins when a token fails several checks) block
acceptance.

R1 is a rule even though `jwx` already refuses `none`. The decision adds the status and the reason code, and `jwx`
provides neither. R2 isn't met yet: `internal/verify` passes `jwx` every key of the JWKS, so an HMAC token signed with a
symmetric key from that set gets through. R4 records the upgrade outcome: no setting turns the refusal off. The record
needs that rule because the change alters what token-gate trusts.

Questions:

- The notes give no reasons. The Justification and the reason for rejecting A1 are mine. Do they match the review?
- Does one of ADR-0001 to ADR-0006 define where a refusal carries its reason code, such as a field of the response
  body? If so, tell me which one, and I'll link it under **Related ADRs** and use its term.
- Should anyone else approve this record?

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-on-outgoing-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, among them the HTTPS calls to the identity provider. When
`tls.Config.MinVersion` is unset, Go's `crypto/tls` client refuses TLS 1.1 and older, as it has since Go 1.18.
token-gate sets no minimum version of its own. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will open the outgoing TLS connections of token-gate only with TLS 1.2 or later.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host. This
  includes connections opened by token-gate's own code and connections opened by a library it calls.

### Rules

- **R1** (`verify`, `server`). token-gate negotiates TLS 1.2 or later on every outgoing TLS connection. When a server
  offers no version from TLS 1.2 on, the handshake fails.

### Implementation notes

Adds no requirement. Go's default meets R1, so the code needs no change. Where a `tls.Config` sets `MinVersion`, use
`tls.VersionTLS12` or `tls.VersionTLS13`. A test can start an `httptest` TLS server with `MaxVersion` set to
`tls.VersionTLS11`, point the JWKS fetch at it, and expect an error.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). Go's default already meets R1. As a rule, though, R1 also makes a change
that sets `MinVersion` below `tls.VersionTLS12` fail a check that a reviewer can apply to the diff (R1).

### Alternatives considered

- **A1. Set `MinVersion` to `tls.VersionTLS10` for an identity provider that offers nothing newer.** Rejected by R1.
  The connection would use a protocol version that RFC 8996 deprecates.

## Consequences

Negative:

- token-gate can't reach a server that offers only TLS 1.1 or older, such as an older identity provider (R1). Existing
  installations see no change, because Go's default already refuses such a server.
````

### Message to the user

I wrote the record as `docs/adr/0007-use-tls-1-2-or-later-on-outgoing-connections.md`. It has no open points, and the
code already meets R1, so no code change is needed. Its status is `Proposed` because the notes don't say that the team
signed it off. Once they do, set the status to `Accepted` and add the Date heading with the date of acceptance.

R1 is a rule even though Go's default provides it. The security architect chose TLS 1.2 for this system, and the rule
lets a reviewer catch a later change that lowers `MinVersion`.

Questions:

- R1 covers only the token-gate process, as the notes do. Should the outgoing connections of `token-admin` follow the
  same rule? If so, that would be a second rule in this record.
- The notes don't name any alternatives. A1, allowing TLS 1.0 for an identity provider that offers nothing newer, is
  mine. Does it match what the review considered?
- Should anyone else approve this record?
