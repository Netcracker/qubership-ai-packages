## Request 1

### File: docs/adr/0007-support-token-gate-under-docker.md

````markdown
# Support token-gate under Docker, configured by environment variables and mounted files alone

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart.
No record and no example in the repository describes how to run it without Kubernetes. Operators who run containers
under Docker without Kubernetes have no supported way to run token-gate.

Under Docker, token-gate makes HTTPS calls to the identity provider, and operators often need it to trust a private CA
for those calls. Both images of the repository build on the platform base image `ghcr.io/example/platform-base`. The
README of that image states its contract. Its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`,
`.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container. It then runs the scripts in
`/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and to
set the service's binary as `CMD`. Operators trust a private CA in every image of the platform by mounting its
certificate under `/tmp/cert`, and under Docker they trust the CA of their identity provider in the same way.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
We will also keep a Compose example under `deploy/docker/`, and CI will start it on every pull request.

### Terms

- **Docker deployment**: a container of the token-gate image that Docker Engine runs, directly or through Docker
  Compose. No Kubernetes API server is reachable from it, and no file that Kubernetes mounts, such as a service account
  token, is present in it.
- **mounted file**: a file that a bind mount, a Docker volume, or a Compose `configs` or `secrets` entry places in the
  container.

### Rules

#### Running under Docker

- **R1** (`server`, `image`). In a Docker deployment that gives token-gate its configuration through environment
  variables and mounted files alone, and where every service that this configuration names is reachable, token-gate
  starts and responds to `GET /ready` with `<ready status>`.

#### The Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate in a Docker deployment. The file gives
  token-gate its configuration through environment variables and mounted files alone, and every service that this
  configuration names is a service of the same Compose file.

#### Continuous integration

- **R3** (`ci`). A job in `.github/workflows/` runs on every pull request. It builds the token-gate image from the
  commit under test, starts the Compose file of R2 with that image, and calls `GET /ready` on token-gate. The job fails
  when token-gate does not respond with `<ready status>` within `<ready timeout>` of the start.

### Implementation notes

Adds no requirement. Let the Compose file take the token-gate image from a variable, such as `TOKEN_GATE_IMAGE`, with a
published tag as its default. Operators can then run the example as it is, and the job of R3 can pass the image it
built. A stub identity provider that serves a JWKS keeps the example self-contained. The job can publish the port of
token-gate and poll `GET /ready` with `curl` from the runner, so that the image needs no HTTP client of its own. The job
of R3 also exercises R1 for the configuration of R2.

### Justification

Environment variables and mounted files are the means that Docker and Compose give a container for its configuration,
so an operator needs nothing from Kubernetes to configure token-gate (R1). A Compose file in the repository gives
operators a working starting point, and CI starts the same file (R2). Starting it on every pull request stops a change
that makes token-gate depend on Kubernetes before it merges (R1, R3). The job builds the image from the commit under
test, so it tests the change and not the last release (R3).

### Alternatives considered

- **A1. Support token-gate only on Kubernetes, through the Helm chart.** Operators who run Docker without Kubernetes
  would have no supported way to run token-gate.

## Consequences

Positive:

- The job of R3 starts the image without the chart, so it also catches an image that starts only with values that the
  chart supplies.

Negative:

- Every pull request waits for the job of R3, which builds the image and starts the Compose example.
- A feature that needs the Kubernetes API, or a file that Kubernetes mounts, cannot be added to token-gate without a new
  record (R1).
- The repository maintains the Compose file of R2 and its stub services next to the chart.

Follow-ups:

- Describe the Docker deployment in the operator documentation, including how to trust a private CA by mounting its
  certificate under `/tmp/cert`.

## Open points

- **O1.** Which response `GET /ready` gives when token-gate is ready, and how long after the start the job of R3 waits
  for it. The notes name neither. `example-architect` decides. Affects R1 and R3.
- **O2.** The record assumes that the job of R3 tests an image built from the commit under test, not a published image.
  `example-architect` confirms this, or chooses the published image. Affects R3.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. Two open points block acceptance:

- **O1:** What status should `GET /ready` return when token-gate is ready, and how long should the CI job wait for it? I put the placeholders `<ready status>` and `<ready timeout>` in R1 and R3 rather than guess.
- **O2:** Should the CI job test an image built from the pull request's commit? R3 assumes it does. Can you confirm, or should it use a published image?

The record doesn't keep the open question about the entrypoint, because the platform contract already answers it. The base image's README and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` does that. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no comment, record, or issue gives a reason. That makes it a defect to fix, not a decision for the ADR. The record states the base image's `/tmp/cert` behavior in Context as a fact and has no rule for it.

I suggest this issue instead. Shall I open it?

- **Type:** Bug
- **Title:** token-gate image replaces the entrypoint of the platform base image
- **Body:** The README of `ghcr.io/example/platform-base` defines `/usr/bin/entrypoint.sh` as the image's entrypoint. It adds the certificates under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and set the binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so certificates mounted under `/tmp/cert` are never trusted and the `/app/init.d` scripts never run. `build/token-admin/Dockerfile` follows the contract with `CMD ["token-admin"]`. Fix: remove the `ENTRYPOINT` line and set `CMD ["/usr/local/bin/token-gate"]`. The chart runs the Pod with a read-only root file system, so it also needs `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, where the entrypoint writes. Check that the entrypoint rebuilds the whole CA bundle into the empty `/etc/ssl/certs`, not only the added certificates.

Until that issue is fixed, mounting a private CA under `/tmp/cert` won't work for token-gate under Docker. If the `ENTRYPOINT` line is deliberate, tell me and I'll add a rule for it to the record.

I tagged R1 `server` and `image` without seeing the code that loads the configuration. If that code lives in another layer, the tag should change.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-the-algorithm-none-or-hmac.md

````markdown
# Refuse tokens whose algorithm is `none` or HMAC, each with its own reason code

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an issuer
holds. So token-gate accepts a token signed with HMAC whenever the JWKS of its issuer holds a symmetric key. Anyone who
can fetch that JWKS can then sign such a token.

## Decision

We will refuse a token that names the algorithm `none` and a token that names an HMAC algorithm, each with HTTP 401 and
a reason code of its own.

### Terms

- **names the algorithm**: a token names the algorithm `X` when the `alg` header parameter in the JOSE header of any of
  its signatures is the string `X`. The comparison is case-sensitive, as RFC 7515, section 4.1.1, requires.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate responds to a request whose token names the algorithm `none` with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate responds to a request whose token names the algorithm `HS256`, `HS384`, or
  `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`. This holds for every key that the JWKS of the issuer
  holds and for every setting of token-gate.

#### Precedence

- **R3** (`verify`). Where the token of a request falls under R1 or R2 and also fails another check of token-gate, such
  as the signature or a claim, token-gate gives the response of R1 or R2.

### Implementation notes

Adds no requirement. Parse the protected header first, for example with `jws.Parse`, and map `none` and the three HMAC
algorithms to their reason codes before verification runs. `jwx` refuses `none` on its own, but with an error that
does not distinguish it from other signature failures, so `internal/verify` has to classify the header first to give
`TOKEN_ALG_NONE`. You can also drop the keys whose `kty` is `oct` from the key set before `jwx` sees it, as a second
defense. Test with a table in `internal/verify` that covers `none`, `HS256`, `HS384`, and `HS512`, each one also expired
or with a bad signature, against a JWKS that holds an `oct` key.

### Justification

An HMAC key signs tokens as well as verifying them. A JWKS is published to every party that verifies tokens, so a
symmetric key in it lets any reader sign tokens that token-gate accepts (R2). The refusal applies whatever keys the JWKS
holds, because `internal/verify` passes `jwx` every key, and an issuer can publish a symmetric key by mistake (R2).
`jwx` already refuses `none`, and a reason code of its own lets operators tell an attempt with `none` apart from a
broken signature (R1). The check needs only the header, so it can run before every other check, and a token with a
refused algorithm always gets the same response (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate instead of read from the JWKS.** Rejected
  by R2: every party that holds the secret of an issuer, token-gate included, could sign tokens for that issuer, and the
  secret would have to be distributed and rotated outside the JWKS.
- **A2. Leave `none` to `jwx`.** Rejected by R1: `jwx` refuses the token, but its error does not distinguish `none` from
  other signature failures.

## Consequences

Positive:

- Monitoring can count tokens refused for `none` or HMAC apart from tokens refused for other reasons.

Negative:

- token-gate accepts tokens from an issuer that signs with `HS256`, `HS384`, or `HS512` and publishes the key in its
  JWKS. After the upgrade, it refuses every such token as R2 states, and no setting restores the old behavior. A test
  case of R2 against a JWKS that holds an `oct` key shows this change.

Follow-ups:

- Add `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` to the documentation of reason codes.
- Before the release that brings R2, tell the operators of any issuer that signs with HMAC.

## Open points

- **O1.** The record assumes that R1 and R2 take precedence over every other check of token-gate (R3).
  `example-security-architect` confirms this, or names the checks that take precedence over them, such as a missing
  token or an unknown issuer. Affects R3.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. One open point blocks acceptance. In O1, R3 assumes that the two algorithm checks take precedence over every other check. Does the security architect agree, or should some checks, such as a missing token or an unknown issuer, come first?

The notes give no reasons, so the reasons in the Justification and in A1 are mine. Please have the security architect confirm them.

Does any of the records 0001 to 0006 define where reason codes go in a response, or list the other reason codes? If so, tell me which one and I'll link it under Related ADRs.

Until R2 is implemented, token-gate accepts HMAC-signed tokens from any issuer whose JWKS holds a symmetric key. It's worth checking the issuers' JWKS for `oct` keys now.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client. Since Go 1.18, the `crypto/tls` client refuses TLS 1.1 and older when
`tls.Config.MinVersion` is zero. token-gate sets no minimum version of its own, so its outgoing connections use TLS 1.2
or later because of that default. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate negotiates TLS 1.2 or later on every outgoing TLS connection, whatever its
  settings. When the server offers only TLS 1.1 or older, the handshake fails, and token-gate sends no request on that
  connection.

### Implementation notes

Adds no requirement. The default of `crypto/tls` meets R1 while each `tls.Config` that token-gate builds for a client
leaves `MinVersion` at zero or sets `tls.VersionTLS12` or `tls.VersionTLS13`. Setting `MinVersion: tls.VersionTLS12`
where token-gate builds its client configuration makes R1 visible in the code, and it keeps R1 met if the default
changes. To test R1, start an `httptest` server whose `MinVersion` and `MaxVersion` are both `tls.VersionTLS11`, and
check that the HTTP client of token-gate fails the handshake. The test server needs both values because Go 1.22 and
later also raise the default minimum of a server.

### Justification

TLS 1.0 and TLS 1.1 are deprecated, so token-gate should not use them for its outgoing calls (R1). The default of
`crypto/tls` already meets R1. A recorded rule turns a change that lowers the minimum, through a setting or a
`tls.Config`, into a violation a checker can name (R1).

### Alternatives considered

- **A1. Leave the minimum version to the default of `crypto/tls` with no record.** A change that lowers the minimum would
  leave nothing in the repository to check it against.

## Consequences

Negative:

- token-gate cannot reach a server, such as an identity provider, that offers only TLS 1.1 or older, and no setting
  allows it (R1).
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. It has no open points, so once the security architect signs off, set the status to `Accepted` and add the Date heading with the date of acceptance.

R1 is a rule even though Go's default already meets it, because the security architect chose this minimum for token-gate. As the repository is described, no code change is needed. Implementation notes suggest an explicit `MinVersion` and a test.

Two questions:

- Should the rule also cover token-admin? The notes name only token-gate.
- I tagged R1 `verify` and `server` without seeing which packages open outgoing connections. Which packages open them, so I can correct the tags?
