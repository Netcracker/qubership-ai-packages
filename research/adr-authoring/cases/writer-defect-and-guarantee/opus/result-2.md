## Request 1

### File: docs/adr/0007-support-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. The repository ships token-gate as a container
image and as a Helm chart. The chart is the only deployment that the repository describes, and the chart runs the Pod
with a read-only root file system. Operators who run containers with Docker and without Kubernetes have no supported way
to run token-gate.

Under Docker, operators need token-gate to trust a private CA for the HTTPS calls to the identity provider. The image
builds on the platform base image `ghcr.io/example/platform-base`. The README of the base image states that its
entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to
the trust store of the container. The entrypoint then runs the scripts in `/app/init.d` and runs its arguments. The
platform's guide for service images says that an image keeps that entrypoint and sets the service's binary as `CMD`.
Operators of every image of the platform mount a private CA under `/tmp/cert` for this reason.

## Decision

We will support running token-gate under Docker without Kubernetes, configured by environment variables and mounted
files alone. We will keep a Compose example under `deploy/docker/` that CI starts on every pull request.

### Terms

- **Docker deployment**: a container of the token-gate image that Docker Engine runs, directly or through Docker
  Compose, where the container reaches no Kubernetes API server and has no Kubernetes service account token mounted.
- **mounted file**: a file that a bind mount or a Docker volume places in the file system of the container.
- **Compose example**: the Compose file that R2 requires, with the files it mounts.

### Rules

#### Configuration

- **R1** (`server`). In a Docker deployment, token-gate starts and serves requests with every setting taken from
  environment variables, from mounted files, or from the defaults built into the image, and token-gate reads no setting
  from any other source, such as the Kubernetes API.

#### The Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose file that runs token-gate as a Docker deployment and configures
  token-gate only through environment variables and mounted files.
- **R3** (`ci`). A workflow under `.github/workflows/` runs on every pull request, starts the Compose example with the
  token-gate image built from the code of the pull request, and calls `GET /ready` on token-gate. The job fails when
  `GET /ready` does not return HTTP 200 within `<readiness timeout>` of the start of the Compose example.

### Implementation notes

Adds no requirement. In the Compose example, pass settings as `environment` entries and mount configuration files
read-only. Include a commented volume that mounts a directory of CA certificates at `/tmp/cert`, so that an operator sees
where a private CA goes. If `GET /ready` depends on a reachable issuer, add a service to the Compose example that serves
a static JWKS, and point token-gate at it.

In the workflow, build the image with `docker compose build`, start the example with `docker compose up --detach`, and
poll `GET /ready` with `curl --fail` until it succeeds or the timeout runs out. Print `docker compose logs` when the job
fails.

### Justification

An operator without Kubernetes can supply configuration only through Docker, that is, through environment variables and
mounted files, so token-gate takes every setting from those sources (R1). When CI starts the Compose example on every
pull request, a change that makes token-gate depend on Kubernetes fails its pull request instead of failing an
operator's deployment (R2, R3). Building the image from the pull request makes the job test the change, not a published
image (R3).

Mounting a private CA under `/tmp/cert` follows the contract of the base image. So operators of token-gate take the same
step as for every image of the platform, and token-gate needs no setting of its own for the CA.

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Operators without Kubernetes would have no supported
  deployment.

## Consequences

Positive:

- A developer can start token-gate locally with the Compose example, without a Kubernetes cluster.

Negative:

- Every pull request runs the job of R3, which adds the time to build the image and start the Compose example.
- A setting that only Kubernetes can provide, such as one that token-gate reads from the Kubernetes API, cannot be
  added (R1).

Follow-ups:

- Add operator documentation for the Docker deployment, including the mount of a private CA under `/tmp/cert`.

## Open points

- **O1.** R3 needs the readiness timeout: how long the job waits for `GET /ready` to return HTTP 200. `example-architect`
  decides. Affects R3.
- **O2.** R3 assumes that `GET /ready` returns HTTP 200 when token-gate is ready. The answers under consideration are
  HTTP 200 alone or any 2xx status. `example-architect` decides. Affects R3.
- **O3.** R3 assumes that the job starts the image built from the code of the pull request. The other answer under
  consideration is the latest published image. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote `docs/adr/0007-support-docker-without-kubernetes.md` with the status `Proposed`. Open points O1 to O3 block acceptance:

- **O1:** the readiness timeout in R3. I left the placeholder `<readiness timeout>` in the rule.
- **O2:** whether `/ready` must return exactly 200 or any 2xx status.
- **O3:** whether CI starts the image built from the pull request.

I didn't make the entrypoint question a rule or an open point. The platform contract already settles it. The base image's README and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` does that, but `build/token-gate/Dockerfile` replaces the entrypoint, and no record explains why. That makes it a defect, not a decision. I suggest opening this issue:

- **Type:** Bug
- **Title:** The token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body:** The README of `ghcr.io/example/platform-base` says `/usr/bin/entrypoint.sh` adds every `.crt`, `.cer`, and `.pem` file under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and set the binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so the base entrypoint never runs and a mounted CA is ignored. To fix it, replace that line with `CMD ["/usr/local/bin/token-gate"]`, as `build/token-admin/Dockerfile` does. The chart runs the Pod with a read-only root file system, and the restored entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. So the chart also needs `emptyDir` volumes at both paths. Check as well that the chart sets no `command` that would replace the entrypoint again.

Question: should anyone besides `example-architect` approve this record, for example the CI workflow maintainers for R3?

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md

````markdown
# Refuse a token whose algorithm is `none` or an HMAC algorithm, with HTTP 401 and a reason code for each

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the signature of a
token with the `jwx` library and passes `jwx` every key that the JWKS of the token's issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. `jwx` accepts `HS256`, `HS384`, and `HS512`
when the key set holds a symmetric key. So token-gate accepts a token signed with HMAC whenever the JWKS of its issuer
holds a symmetric key. With HMAC, the key that verifies a signature is also the key that creates one. So whoever can read
that JWKS can sign a token that token-gate accepts for that issuer.

## Decision

We will refuse a token whose header names the algorithm `none` or an HMAC algorithm. Each case gets HTTP 401 and its
own reason code.

### Terms

- **token**: the JWT that token-gate checks for a request before policy evaluation.
- **header algorithm**: the value of the `alg` parameter in the JOSE header of a token.
- **HMAC algorithm**: `HS256`, `HS384`, or `HS512`.
- **refuse**: token-gate answers the request with the HTTP status and the reason code that the rule names, and does not
  pass the request to policy evaluation.

### Rules

#### Algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose header algorithm is `none` with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`. The comparison ignores letter case.
- **R2** (`verify`, `server`). token-gate refuses a token whose header algorithm is an HMAC algorithm with HTTP 401 and
  the reason code `TOKEN_ALG_SYMMETRIC`. The comparison ignores letter case. R2 holds whatever keys the JWKS of the
  token's issuer holds and whatever the configuration of token-gate.

#### Precedence

- **R3** (`verify`, `server`). When a token fails R1 or R2 and also fails another check of token-gate, the response
  carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. In `internal/verify`, read the header algorithm before calling `jwx`, and return a distinct error
for `none` and for an HMAC algorithm. Let `internal/server` map each error to HTTP 401 and its reason code. Also drop
every key whose `kty` is `oct` from the key set before passing the key set to `jwx`. Then a later change that skips the
header check still cannot verify an HMAC signature.

Cover R1 and R2 with a table test in `internal/verify` that includes `none`, `None`, `NONE`, `HS256`, `HS384`, `HS512`,
and `hs256`, with a symmetric key in the key set. Cover the status and the reason code with a test in `internal/server`.
For R3, use an expired token with the header algorithm `HS256`.

### Justification

A symmetric key in a JWKS is a signing key, so whoever reads that JWKS can create tokens. Refusing every HMAC algorithm,
whatever keys the JWKS holds, removes that path (R2). `jwx` already refuses `none`. A reason code of its own lets
operators tell a token without a signature apart from an ordinary verification failure (R1). Ignoring letter case keeps
variants such as `None` and `hs256` from getting a different reason code (R1, R2). One reason code per algorithm
case, whatever else is wrong with the token, lets monitoring count every such token by its reason code (R3).

### Alternatives considered

- **A1. Accept HMAC tokens with a shared secret configured per issuer.** Rejected by R2: token-gate would hold a secret
  that signs tokens for the issuer, so anyone who obtained it from the configuration of token-gate could create tokens
  for that issuer.

## Consequences

Positive:

- Operators can find refused tokens without a signature or with an HMAC signature by the reason codes `TOKEN_ALG_NONE`
  and `TOKEN_ALG_SYMMETRIC`.

Negative:

- An issuer that signs tokens with HMAC cannot be used with token-gate. After an upgrade, an installation that accepted
  such tokens because the JWKS of the issuer holds a symmetric key refuses them, and no setting restores the old answer
  (R2). The test that the Implementation notes recommend for R2 shows this case.

Follow-ups:

- State in the release notes that token-gate refuses tokens with an HMAC algorithm (R2), and name the reason code.

## Open points

- **O1.** R1 and R2 assume that the comparison of the header algorithm ignores letter case. The answers under
  consideration are to ignore letter case, or to match only the exact values `none`, `HS256`, `HS384`, and `HS512`
  and leave other spellings to another reason code. `example-security-architect` decides. Affects R1 and R2.
- **O2.** R3 assumes that the algorithm check takes precedence over every other check of a token. The answers under
  consideration are that it takes precedence, or that an earlier check, such as a malformed header, keeps its own
  reason code. `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote `docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md` with the status `Proposed`. Two open points block acceptance:

- **O1:** whether the comparison of `alg` ignores letter case.
- **O2:** whether the algorithm reason codes take precedence over other refusal reasons.

R1 is a rule even though `jwx` already refuses `none`, because the reason code `TOKEN_ALG_NONE` is a decision. R2 changes behavior today: `internal/verify` passes `jwx` every key from the JWKS, so `jwx` accepts HMAC tokens when an issuer's JWKS has a symmetric key. The Negative consequences record that cost.

Questions:

1. The notes give no reasons for the decision. I wrote the Justification and the reason for rejecting A1 from the repository facts. Can `example-security-architect` confirm or correct them?
2. Does a record among 0001 to 0006 define the reason code and the field that carries it? If so, I'll list it under **Terms** with a pointer and add the record under **Related ADRs**.

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

token-gate checks the token of each request before policy evaluation, and token-gate opens TLS connections as a client.
By default, the `crypto/tls` client of Go refuses TLS 1.1 and older. token-gate sets no minimum TLS version of its own,
so its outgoing connections use TLS 1.2 or later. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every TLS connection that token-gate opens as a client.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host. This
  includes a connection that a library opens for token-gate.

### Rules

#### TLS version

- **R1** (`verify`, `server`). token-gate negotiates TLS 1.2 or later on every outgoing TLS connection. When the server
  offers only TLS 1.1 or older, token-gate ends the handshake with an error.

### Implementation notes

Adds no requirement. The default of `crypto/tls` meets R1, so a `tls.Config` that leaves `MinVersion` at zero needs no
change. Setting `MinVersion` to `tls.VersionTLS12` or higher also meets R1. A test can start an
`httptest.NewUnstartedServer` whose `TLS.MaxVersion` is `tls.VersionTLS11` and check that the HTTP client that token-gate
uses for its outgoing calls fails the handshake.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). R1 is a rule even though Go's default meets it. Without R1, a later change
that sets a lower `MinVersion`, or that opens connections through another TLS stack, would break no rule.

### Alternatives considered

The security review recorded no alternative.

## Consequences

Negative:

- token-gate cannot connect to a server that offers only TLS 1.1 or older (R1). token-gate already behaves this way
  because of Go's default.
````

### Message to the user

I wrote `docs/adr/0007-tls-1-2-or-later-for-outgoing-connections.md` with the status `Proposed`. The code already meets R1, because Go's default does. The rule is there so that a later change can't lower the minimum. The record has no open points, so it can be set to `Accepted`, with the acceptance date, once the team signs off.

Questions:

1. Did the security review consider any alternatives, such as requiring TLS 1.3? The record says none were recorded.
2. I tagged R1 with `verify` and `server`, assuming all outgoing connections come from those packages. Does any other code open outgoing TLS connections? If so, R1 needs that layer's tag as well.
3. Should anyone besides `example-security-architect` approve the record?
