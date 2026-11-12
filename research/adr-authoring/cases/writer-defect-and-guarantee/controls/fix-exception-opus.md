## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate ships as a container image, built by `build/token-gate/Dockerfile`, and as a Helm chart. The chart is the
only supported way to run it, so an operator without Kubernetes has no supported setup.

Under Docker, operators need the HTTPS calls of token-gate to the identity provider to trust a private CA. On the
platform, operators trust a private CA by mounting its certificate under `/tmp/cert`, and they do this for every image.

The token-gate image builds on the platform base image `ghcr.io/example/platform-base`. The README of the base image
states its contract. Its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file
under `/tmp/cert` to the trust store of the container. It then runs the scripts in `/app/init.d`, and then runs its
arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. A Compose example under `deploy/docker/` shows the setup, and a CI job starts it on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker Engine runs from the token-gate image, started by
  `docker run` or by Docker Compose, outside a Kubernetes Pod.
- **Compose example**: the Compose file under `deploy/docker/` and the files it mounts.

### Rules

#### Configuration

- **R1** (`server`). Every setting of token-gate can be given by an environment variable or by a file mounted into the
  container. No setting needs another source, such as a command-line flag or the Kubernetes API.

#### Trust of a private CA

- **R2** (`image`). In a Docker deployment, the HTTPS calls of token-gate to the identity provider trust every CA
  certificate that the operator mounts in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert`, with no other setting.

#### Compose example and CI

- **R3** (`docker`). The Compose example starts token-gate from the token-gate image as a Docker deployment, and gives
  every setting of token-gate by an environment variable or by a mounted file.
- **R4** (`ci`). On every pull request, a CI job starts the Compose example and calls `GET /ready` on token-gate. The
  job fails when the call gets no response with status 200.

### Implementation notes

Adds no requirement. R2 can be met only once the token-gate image runs its binary behind the entrypoint of the base
image, `/usr/bin/entrypoint.sh`. `build/token-gate/Dockerfile` replaces that entrypoint today.

In the Compose example, give settings with `environment` or `env_file`, and mount files with `volumes`. A commented
volume that mounts a CA certificate under `/tmp/cert` shows operators where R2 expects it. The CI job can run
`docker compose up --wait`, then call `/ready` with `curl` and compare the status with 200.

### Justification

`docker run` and Compose give a container its configuration through environment variables and mounted files, and a
Docker deployment has no Kubernetes objects to read (R1, R3). Starting the Compose example on every pull request keeps
it working as settings change, so the example stays a setup that operators can copy (R3, R4). Trusting the certificates
under `/tmp/cert` lets an operator handle a private CA for token-gate the same way as for every other image of the
platform (R2).

### Alternatives considered

- **A1. Support token-gate only through the Helm chart.** Operators without Kubernetes would have no supported setup.

## Consequences

Positive:

- An operator who already mounts a private CA under `/tmp/cert` for other images of the platform needs no new procedure
  for token-gate (R2).

Negative:

- Every pull request runs one more CI job, which starts a container from the token-gate image (R4).
- A new setting that only a command-line flag or the Kubernetes API can give cannot be added (R1).

Follow-ups:

- Describe the Docker deployment and the `/tmp/cert` mount in the operator documentation.

## Open points

- **O1.** R4 assumes that a ready token-gate responds to `GET /ready` with status 200, and that any other status means
  it is not ready. The architect, `example-architect`, confirms this or names the statuses that count as ready. Affects
  R4.
````

### Message to the user

I drafted ADR-0007 as `Proposed`. Open point O1 blocks acceptance: R4 assumes that `GET /ready` returns 200 when token-gate is ready, and the architect needs to confirm that or name the statuses that count as ready.

The record doesn't take up the meeting's open question about the entrypoint, because it isn't a decision. The base image's README and the platform's guide for service images already settle it: keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` follows that contract. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue gives a reason for it. That makes it a defect. I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform base entrypoint
- **Body:** The README of `ghcr.io/example/platform-base` and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` and set the service binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so certificates under `/tmp/cert` are not trusted and `/app/init.d` doesn't run. The fix is to remove the `ENTRYPOINT` line and end with `CMD ["/usr/local/bin/token-gate"]`, as `build/token-admin/Dockerfile` does. The chart runs the Pod with a read-only root file system, and the entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. So the chart also needs `emptyDir` volumes at those two paths.

ADR-0007 R2 can only be met after that fix, and the record's Implementation notes say so. Should I open the issue, or does one already exist? A change that brings R1, R3, or R4 before the fix can then name R2 under `Defers` with that issue.

I made `example-architect` the owner and the only approver. Please confirm that, or name anyone else who approves.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-algorithm-none-or-hmac.md

````markdown
# Refuse tokens whose algorithm is `none` or HMAC

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. When it verifies a signature, `jwx` refuses a token whose `alg` is `none`. It accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key. `internal/verify` passes `jwx` every key that the JWKS of an issuer
holds, so an issuer whose JWKS holds a symmetric key gets its HMAC tokens accepted.

The refusal of `none` by `jwx` carries no reason code of token-gate. So a token with `alg` set to `none` gets the same
response as any other token whose signature fails.

## Decision

We will refuse a token whose algorithm is `none` and a token signed with HMAC, each with HTTP 401 and a reason code of
its own.

### Terms

- **token**: the token that token-gate checks on a request before policy evaluation.
- **header algorithm**: the value of the `alg` parameter in the JOSE header of a token, compared case-sensitively as
  RFC 7515 defines it. `None` and `NONE` are not `none`.
- **refuse**: token-gate responds to the request with HTTP status 401 and the reason code that the rule names, and the
  request does not reach policy evaluation. `internal/verify` meets a rule that refuses by returning an error that
  carries the reason code.

### Rules

#### Algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose header algorithm is `none`, with the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose header algorithm is `HS256`, `HS384`, or `HS512`, with
  the reason code `TOKEN_ALG_SYMMETRIC`. R2 applies whatever keys the JWKS of the issuer holds, and no setting turns it
  off.

#### Precedence

- **R3** (`verify`, `server`). A token that R1 or R2 refuses gets the reason code of that rule, also where another check
  of token-gate, such as the expiry or the issuer, would refuse it too.

### Implementation notes

Adds no requirement. Read the header algorithm before calling `jwx`, and return the error of R1 or R2 before any other
check. Tests can build a token with each of `none`, `HS256`, `HS384`, and `HS512` and check the status and the reason
code. An `HS256` case whose issuer JWKS holds a symmetric key covers the path that `jwx` accepts today.

### Justification

With HMAC, the same key both verifies and signs. So any party that holds a key to verify a token can also mint one. An
issuer publishes its JWKS, so a symmetric key in it lets anyone who reads the JWKS sign tokens that token-gate accepts
today (R2). Refusing HMAC whatever the key set holds also blocks algorithm confusion, where a token signed with `HS256`
is checked against key material meant for an asymmetric algorithm (R2).

R1 makes the refusal of `none` a rule of token-gate rather than a property of `jwx`. Its reason code lets operators
tell a token with `none` apart from a token with a broken signature (R1). Checking the algorithm first gives each
refusal one reason code, whatever else is wrong with the token (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: token-gate would hold a key that can sign tokens
  for each issuer, and each secret would have to be distributed and rotated outside the JWKS.

## Consequences

Negative:

- An issuer that signs tokens with `HS256`, `HS384`, or `HS512` gets every token refused after the upgrade, including an
  issuer whose JWKS holds a symmetric key and whose tokens token-gate accepts today. No setting restores the old answer
  (R2).
- A token with `alg` set to `none` gets the reason code `TOKEN_ALG_NONE` instead of the response of a failed signature
  (R1). Clients or alerts that match the old response need updating.

## Open points

- **O1.** R1 and R2 assume that token-gate reports the reason code in the same place as the reason code of every other
  refused token. Either a record among ADR-0001 to ADR-0006 already defines that place, and **Terms** points at it, or
  the security architect, `example-security-architect`, names the response field. Affects R1 and R2.
- **O2.** R3 assumes that the reason code of R1 or R2 wins over the reason code of any other failed check. The other
  answer is to keep the order of checks that token-gate has today, with R1 and R2 applying only to a token that passes
  every earlier check. The security architect, `example-security-architect`, decides. Affects R3.
````

### Message to the user

I drafted ADR-0007 as `Proposed`. Open points O1 and O2 block acceptance:

- **O1:** where in the response the reason code goes. If one of ADR-0001 to ADR-0006 already defines reason codes, tell me which one, and I'll point **Terms** at it.
- **O2:** whether `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` win over the reason code of another failed check, such as an expired token.

The notes didn't give a reason for rejecting HMAC with a shared secret per issuer. I wrote the Justification and A1 from the facts about `jwx` and `internal/verify`. Please have `example-security-architect` confirm those reasons.

The code doesn't meet the rules yet. `jwx` refuses `none` without the `TOKEN_ALG_NONE` reason code. `jwx` also accepts `HS256`, `HS384`, and `HS512` whenever an issuer's JWKS holds a symmetric key, and `internal/verify` passes every key through.

I made `example-security-architect` the owner and the only approver. Please confirm that, or name anyone else who approves.

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

token-gate opens TLS connections as a client, such as for its HTTPS calls to the identity provider. Go's `crypto/tls`
client refuses TLS 1.1 and older by default when `tls.Config.MinVersion` is zero. token-gate sets no minimum version of
its own, so it relies on that default.

RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as a client, including a connection
  that a library opens inside that process.

### Rules

#### TLS version

- **R1** (`server`, `verify`). token-gate completes the handshake of an outgoing TLS connection only where the
  negotiated version is TLS 1.2 or later. Where the server offers only TLS 1.1 or older, the handshake fails and the call
  that needed the connection fails.

### Implementation notes

Adds no requirement. The Go default meets R1 as long as no `tls.Config` of token-gate sets `MinVersion` below
`tls.VersionTLS12`. Setting `MinVersion: tls.VersionTLS12` on each `tls.Config` that token-gate builds keeps R1 met if a
later Go release or a `GODEBUG` setting changes the default. A test can start an `httptest` TLS server with `MaxVersion`
set to `tls.VersionTLS11` and check that the client of token-gate fails to connect.

### Justification

TLS 1.0 and TLS 1.1 are deprecated, so a connection that uses them doesn't meet the security baseline of token-gate (R1).
The Go default is a property of the toolchain, not a decision for this system. A rule keeps a change that lowers the
minimum, in code or in a dependency, visible as a violation (R1).

## Consequences

Negative:

- token-gate cannot reach an identity provider or another server that offers only TLS 1.1 or older (R1). The Go default
  already has this effect, so no installation that works today stops working.
````

### Message to the user

I drafted ADR-0007 as `Proposed`. It has no open points, so it can be accepted once the team signs off. The code already meets R1 through Go's default, so no code change is needed. A test like the one in **Implementation notes** would give R1 an entry under **Confirmation**.

The notes recorded no alternatives, so I left out **Alternatives considered**. Was any other option discussed, such as requiring TLS 1.3? If so, I'll add it.

I made `example-security-architect` the owner and the only approver. Please confirm that, or name anyone else who approves.
