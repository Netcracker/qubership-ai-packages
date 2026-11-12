## Request 1

### File: docs/adr/0007-support-token-gate-under-docker.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R7.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image, built by
`build/token-gate/Dockerfile`, and as a Helm chart under `helm/`. The chart is the only deployment that the repository
describes. An operator who runs token-gate under Docker without Kubernetes has no example, and no check shows that
token-gate starts there.

Under Docker, operators need token-gate to trust a private CA for its HTTPS calls to the identity provider. On the
platform, an operator mounts the certificate of such a CA under `/tmp/cert`, and every image of the platform trusts it.

Both images of the repository build on `ghcr.io/example/platform-base`, pinned by digest. The README of the base image
states its contract: its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem`
file under `/tmp/cert` to the trust store of the container, runs the scripts in `/app/init.d`, and then runs its
arguments. The platform's guide for service images says to keep that entrypoint and to set the service's binary as
`CMD`. `build/token-admin/Dockerfile` follows the guide and ends with `CMD ["token-admin"]`.

`build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. That line replaces the base
entrypoint, so token-gate ignores `/tmp/cert`. The line dates from the first commit of the file, and no record or issue
explains it.

The chart runs the Pod of token-gate with a read-only root file system. The base entrypoint writes to `/etc/ssl/certs`
and `/usr/local/share/ca-certificates`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone,
and ship a Compose example that CI starts on every pull request. token-gate will trust the certificates that an operator
mounts under `/tmp/cert`, as every image of the platform does.

### Terms

- **Docker deployment**: a token-gate container that Docker Engine runs, started directly or from a Compose file, where
  no Kubernetes API server is reachable and no Kubernetes service account token is mounted.
- **Compose example**: the Compose file under `deploy/docker/` that R3 requires.
- **private CA file**: a file under `/tmp/cert` in the token-gate container whose name ends in `.crt`, `.cer`, or
  `.pem`.
- **outgoing trust store**: the set of CA certificates against which token-gate verifies the server certificate of its
  outgoing HTTPS calls.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads its settings only from environment variables and from files in its container's
  file system.
- **R2** (`server`). In a Docker deployment that the Compose example starts, token-gate starts and responds to
  `GET /ready` with HTTP 200.

#### The Compose example

- **R3** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from its image and sets every setting
  of token-gate through an environment variable or a mounted file.
- **R4** (`ci`). A job under `.github/workflows/` runs on every pull request. The job builds the token-gate image from
  the commit of the pull request, starts the Compose example with that image, and sends `GET /ready` to token-gate. The
  job fails unless token-gate responds with HTTP 200 within `<ready timeout>` of the start.

#### Private CA certificates

- **R5** (`image`). When the token-gate container starts, every certificate in a private CA file joins the outgoing trust
  store before token-gate serves its first request.
- **R6** (`image`). Where the token-gate container holds no private CA file, the outgoing trust store holds the
  certificates of the base image's trust store and no other.
- **R7** (`chart`, `image`). An installation of the chart that upgrades to an image built under this record needs no
  change to its values, keeps a read-only root file system for the token-gate container, and its token-gate Pod becomes
  ready.

### Implementation notes

Adds no requirement. The Compose example can mount a private CA file from `deploy/docker/` to show the `/tmp/cert`
mount. For the CI job, `docker compose up --wait` followed by a `curl` loop against `/ready` is enough. How the image
meets R5 and R6 depends on O1.

### Justification

An operator outside Kubernetes can run token-gate only if no setting needs Kubernetes to reach it (R1, R3). No
Kubernetes test covers the Docker deployment, so a job on every pull request is the only way to catch a change that
breaks it (R2, R4). `/tmp/cert` is the platform's convention, so an operator mounts a private CA for token-gate the same
way as for every other image (R5). Existing installations mount nothing under `/tmp/cert` and run under the chart, so
R6 and R7 keep their behavior on upgrade.

### Alternatives considered

- **A1. Document the Docker deployment without a CI job.** Rejected by R4: nothing would fail when a change breaks the
  Docker deployment.
- **A2. Let each operator build a derived image with the private CA baked in.** Operators would rebuild and re-pin an
  image for each CA rotation, and token-gate would differ from every other image of the platform.

## Consequences

Positive:

- Under the chart too, an operator can make token-gate trust a private CA by mounting it under `/tmp/cert` (R5).

Negative:

- Every pull request waits for the image build and the start of the Compose example (R4).

Follow-ups:

- Describe the Docker deployment and the `/tmp/cert` mount in the operator documentation.

## Open points

- **O1.** How does the image meet R5 and R6? `example-architect` decides. The answers under consideration:
  - (a) Replace `ENTRYPOINT ["/usr/local/bin/token-gate"]` with `CMD ["/usr/local/bin/token-gate"]`, so that the base
    entrypoint runs, as the platform's guide says and as token-admin does. For R7, the chart then mounts `emptyDir`
    volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. An `emptyDir` volume starts empty and hides the
    CA bundle that the image holds at `/etc/ssl/certs`, so R6 holds only if the base entrypoint rebuilds that bundle
    rather than appending to it. Arguments that `docker run` or the `args` of a Pod spec pass replace `CMD`, so they
    have to start with the path of the binary. The base entrypoint also runs the scripts in `/app/init.d` in every
    installation.
  - (b) Keep the binary as the entrypoint, and let token-gate read the private CA files itself at start. token-gate
    would then reimplement the base image's contract, DER-encoded `.cer` files included, and track its changes by hand.

  The chosen answer becomes a rule of the `image` layer about the entrypoint, because the Compose example and every
  `docker run` command depend on it. Affects R5, R6, and R7.
- **O2.** What is `<ready timeout>` in R4? `example-architect` decides. Affects R4.
````

### Message to the user

I've written the record as `Proposed`. O1 and O2 block acceptance.

**O1 (the entrypoint).** I recommend answer (a): switch to the base entrypoint and set the binary as `CMD`. The platform's guide asks for it, token-admin already does it, and nothing explains the current `ENTRYPOINT` line. Before you decide, check three things:

- **The CA bundle.** Does `/usr/bin/entrypoint.sh` rebuild `/etc/ssl/certs` from scratch, or only append to it? If it only appends, an `emptyDir` volume at that path hides the public CA bundle, and the HTTPS calls to the identity provider fail under the chart.
- **Arguments.** Does the chart set `command` or `args` for the token-gate container? Under answer (a), `args` that start with a flag would run as the command itself.
- **Init scripts.** Does the base image ship scripts in `/app/init.d` that would now run in token-gate?

**O2.** What timeout should the CI job allow for `GET /ready`?

**Questions:**

- Should the platform team, which owns the base image, or the maintainer of the chart approve this record as well as `example-architect`?
- I tagged R1 and R2 with the `server` layer, assuming that `internal/server` loads the configuration. Is that where it lives?

## Request 2

### File: docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md

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
`jwx` library.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature, so token-gate already refuses such a token.
The refusal carries no reason code of its own, so an operator cannot tell it apart from other signature failures.

`jwx` accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key. `internal/verify` passes it every key
that the JWKS of an issuer holds. Where an issuer's JWKS holds a symmetric key, token-gate accepts a token signed with
that key. A JWKS is usually served without authentication, so anyone who can fetch it can sign such a token.

## Decision

We will refuse every token whose header names the algorithm `none` or an HMAC algorithm, with HTTP 401 and a reason code
for each case.

### Terms

- **header algorithm**: the value of the `alg` member of the JOSE protected header of the token of a request, compared
  as an exact, case-sensitive string.
- **HMAC algorithm**: one of `HS256`, `HS384`, and `HS512`.
- **reason code**: as ADR-<NNNN> defines it.

### Rules

#### The algorithm `none`

- **R1** (`verify`, `server`). token-gate refuses a request whose token has the header algorithm `none` with HTTP 401
  and the reason code `TOKEN_ALG_NONE`.

#### HMAC algorithms

- **R2** (`verify`, `server`). token-gate refuses a request whose token has an HMAC algorithm as its header algorithm
  with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the token's issuer holds. No setting
  turns this refusal off.

#### Precedence

- **R3** (`verify`, `server`). Where the token of a request matches R1 or R2 and also fails another check of
  token-gate, the response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. Read the header algorithm in `internal/verify` before the key lookup and before any other check,
so that R3 holds whatever order the other checks run in. Also leave keys whose `kty` is `oct` out of the key set that
`internal/verify` passes to `jwx`, so that a path that misses the header check still finds no symmetric key. For R2,
test each HMAC algorithm against a test issuer whose JWKS holds a symmetric key, because that key is the case R2 exists
for.

### Justification

A symmetric key in a JWKS is known to everyone who can fetch the JWKS, so a token signed with it shows nothing about who
issued it (R2). A token with the algorithm `none` carries no signature. A reason code of its own lets an operator tell a
forged token from a broken key (R1). The header algorithm settles the refusal before any other check runs, so its reason
code names the cause (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate.** Rejected by R2: every party that holds
  the secret can sign tokens in the issuer's name, and token-gate would store and rotate a secret per issuer.
- **A2. Rely on `jwx` to refuse `none`, with the reason code that its error maps to today.** Rejected by R1.
- **A3. Refuse HMAC only by leaving symmetric keys out of the key set.** Rejected by R2: the token then fails with the
  reason code of a missing key, not `TOKEN_ALG_SYMMETRIC`.

## Consequences

Negative:

- An issuer that signs with an HMAC algorithm and publishes a symmetric key in its JWKS gets its tokens refused after
  the upgrade, and no setting restores them (R2).
- A client or dashboard that matches the reason code of a token with the algorithm `none` sees `TOKEN_ALG_NONE` in
  place of the code that token-gate returned before (R1).

Follow-ups:

- Add `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` to the documentation of reason codes.

## Open points

- **O1.** Which record defines reason codes and where the response carries them? The owner fills in ADR-<NNNN> under
  **Terms** and adds the record under **Related ADRs**. Affects R1, R2, and R3.
- **O2.** The header algorithm is assumed to be compared case-sensitively, as RFC 7515 defines `alg`. `None` and `hs256`
  then fall outside R1 and R2, and token-gate refuses them as unknown algorithms with their existing reason code. The
  other answer compares case-insensitively, so `None` gets `TOKEN_ALG_NONE`. `example-security-architect` decides.
  Affects R1 and R2.
- **O3.** R3 assumes that the reason codes of R1 and R2 win over every other reason. The other answer keeps the existing
  order of the checks and gives R1 and R2 the last place. `example-security-architect` decides. Affects R3.
````

### Message to the user

I've written the record as `Proposed`. O1 to O3 block acceptance.

**Security issue today.** `internal/verify` passes every JWKS key to `jwx`. If a configured issuer's JWKS holds a key with `"kty": "oct"`, token-gate accepts HS256 tokens signed with it now, before this record lands. Check the JWKS of each configured issuer for such a key.

**Questions:**

- Which existing record defines reason codes and how the response carries them? I left ADR-<NNNN> as a placeholder under **Terms**.
- Should `None`, `NONE`, or `hs256` get the new reason codes (O2)? Should these two codes win over every other refusal reason (O3)?
- The notes say HMAC with a shared secret was rejected but give no reason. I wrote the usual one (anyone with the secret can sign tokens, and token-gate would have to store a secret per issuer) into A1. Please confirm it matches the review.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for the outgoing TLS connections of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, for example to fetch the JWKS of an issuer. It uses the `crypto/tls`
package of Go. Since Go 1.18, the `crypto/tls` client refuses TLS 1.1 and older by default. token-gate sets no minimum
version of its own, so the version it accepts follows the default of the Go toolchain that builds it.

## Decision

We will let every outgoing TLS connection of token-gate use TLS 1.2 or later.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host, through
  any library that token-gate links.

### Rules

#### TLS version

- **R1** (`verify`, `server`). An outgoing TLS connection negotiates TLS 1.2 or later. Where the server supports no
  version later than TLS 1.1, the handshake fails and token-gate sends no request over the connection.

### Implementation notes

Adds no requirement. R1 holds today through the default of `crypto/tls`, so it needs no code change. A test that starts
a TLS server with `MaxVersion: tls.VersionTLS11` and calls it through each HTTP client that token-gate builds shows that
R1 holds. The test also catches a later change of the default or a `tls.Config` with a lower `MinVersion`. Setting
`MinVersion: tls.VersionTLS12` in each `tls.Config` makes R1 independent of the toolchain default.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). Stating the version as a rule, rather than leaving it to the default of
the toolchain, lets a checker fail a change that lowers it (R1).

### Alternatives considered

- **A1. Record nothing and rely on the default of `crypto/tls`.** A change that sets a lower `MinVersion`, or a toolchain
  with another default, would then pass review.

## Consequences

Negative:

- token-gate cannot reach an identity provider or a JWKS host that supports no version later than TLS 1.1 (R1).

## Open points

- **O1.** The record covers the token-gate process only, as the security review named it. The other answer extends it
  to token-admin, which `build/token-admin/Dockerfile` builds from the same repository. `example-security-architect`
  decides. Affects R1.
````

### Message to the user

I've written the record as `Proposed`. O1 blocks acceptance: should the rule also cover token-admin, or only token-gate as the notes say?

**No code change needed.** The decision matches what the code does now, as long as the `go` line in `go.mod` and the toolchain are Go 1.18 or later. Please confirm that.

**Recommendation.** Nothing in the repository checks R1 yet. Add the test from **Implementation notes**, and consider setting `MinVersion: tls.VersionTLS12` explicitly so that R1 no longer depends on the toolchain default.

**Question.** I tagged R1 with `verify` and `server`, assuming those packages open the outgoing connections. If other packages open them, which layers should the tag name?
