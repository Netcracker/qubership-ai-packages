## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image, built by
`build/token-gate/Dockerfile`, and as a Helm chart. Apart from the chart, the repository ships no way to deploy it.
Some operators run their containers under Docker without Kubernetes, and they cannot use the chart.

Under Docker, a container receives its settings as environment variables and as files that the operator mounts. The
HTTPS calls to an identity provider often need a private CA to be trusted. The README of the platform base image
`ghcr.io/example/platform-base`, which the image of token-gate builds on, states that the image's entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container. It then runs the scripts in `/app/init.d`, and then runs its arguments. On every image of the
platform, operators trust a private CA by mounting its certificate under `/tmp/cert`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. We will ship a Compose example under `deploy/docker/` that CI starts on every pull request.

### Terms

- **configuration**: every value that an operator sets to change how token-gate behaves, such as its issuers, its
  listen address, and the certificates it trusts.

### Rules

#### Configuration

- **R1** (`server`, `verify`). token-gate reads its configuration only from environment variables and from files in the
  container's file system. It reads no configuration from the Kubernetes API.

#### The Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from the image that
  `build/token-gate/Dockerfile` builds. The Compose file configures token-gate only through environment variables and
  mounted files.

#### CI

- **R3** (`ci`). A job in `.github/workflows/` runs on every pull request. It builds the image of token-gate from the
  code of the pull request, starts the Compose file under `deploy/docker/` with that image, and calls `GET /ready` on
  token-gate. The job fails when `GET /ready` does not return HTTP 200.

### Implementation notes

Adds no requirement. Start the Compose file with `docker compose up --wait`, and retry `GET /ready` for a short time
before the job fails, so that a slow start does not fail the job. If `GET /ready` depends on a reachable issuer, the
Compose file can start a stub issuer that serves a JWKS, and token-gate can point to it through an environment variable.

### Justification

An operator without Kubernetes can run token-gate only if token-gate needs nothing that Kubernetes provides (R1).
Environment variables and mounted files are what Docker gives a container. Platform images already take CA
certificates as files under `/tmp/cert`, so token-gate needs no other configuration source (R1, R2). The Compose file
gives operators a working starting point, and it gives CI something to start (R2). Without a job on every pull request,
a change that makes token-gate depend on Kubernetes would only show up when an operator upgrades (R3).

## Consequences

Positive:

- The job that R3 requires also shows, on every pull request, that the image starts and becomes ready outside the chart.

Negative:

- Every pull request runs one more job, which builds the image and starts it under Compose (R3).
- A feature that needs a configuration source that only Kubernetes offers, such as watching a ConfigMap through the
  Kubernetes API, cannot land (R1).

Follow-ups:

- Document how to run token-gate under Docker, starting from the Compose file under `deploy/docker/`.

## Open points

- **O1.** R3 assumes that the job tests the image built from the code of the pull request. The alternative is the
  latest published image. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, owned by @example-architect. Open point O1 blocks acceptance. It asks whether the CI job tests the image built from the pull request. I assumed it does.

I left the entrypoint question out of the record because it isn't a decision, it's a defect. The README of `ghcr.io/example/platform-base` and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and to set the service binary as `CMD`. `build/token-admin/Dockerfile` does this. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue explains why. Until that changes, a certificate mounted under `/tmp/cert` has no effect on token-gate, under Docker or under the chart. I suggest this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body:** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. This replaces `/usr/bin/entrypoint.sh`, the entrypoint of `ghcr.io/example/platform-base`. The base image's README says that entrypoint adds the certificates under `/tmp/cert` to the trust store and runs `/app/init.d`. The platform's guide for service images says to keep it and to set the binary as `CMD`. The fix:
  - Replace the line with `CMD ["/usr/local/bin/token-gate"]`.
  - In the chart, add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. The entrypoint writes to both, and the Pod's root file system is read-only.
  - Check that the entrypoint rebuilds the whole system CA bundle in an empty `/etc/ssl/certs`. Otherwise the `emptyDir` would hide the public CAs that ship with the image.

If anyone knows a reason the `ENTRYPOINT` line has to stay, tell me and I'll add it to the record as a decision with a rule.

Questions:

1. Who else approves this record? For example, a maintainer of the CI or of the chart.
2. I tagged R1 with `server` and `verify` without seeing the code. Where does token-gate load its configuration? If it's in a directory the reading guide doesn't map, such as `cmd/`, the guide needs a layer for it, and R1 needs that tag.

## Request 2

### File: docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md

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
`jwx` library. It passes `jwx` every key that the JWKS of an issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. `jwx` accepts `HS256`, `HS384`, and `HS512`
when the key set holds a symmetric key. So token-gate accepts a token signed with HMAC when the JWKS of its issuer holds
a symmetric key.

## Decision

We will refuse every token whose header algorithm is `none`, `HS256`, `HS384`, or `HS512` with HTTP 401, and with a
reason code that names the cause.

### Terms

- **token**: the token that token-gate checks on a request.
- **header algorithm**: the value of the `alg` member in the JOSE header of a token, compared case-sensitively.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose header algorithm is `none` with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`. This holds for every value of every configuration setting of token-gate.
- **R2** (`verify`, `server`). token-gate refuses a token whose header algorithm is `HS256`, `HS384`, or `HS512` with
  HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`. This holds whatever keys the JWKS of its issuer holds, whether
  or not its signature is valid, and for every value of every configuration setting of token-gate.

#### Precedence

- **R3** (`verify`, `server`). Where a token is refused under R1 or R2 and also fails another check of token-gate,
  token-gate responds with the reason code that R1 or R2 names.

### Implementation notes

Adds no requirement. Read the header algorithm from the protected header before calling `jwx` to verify the signature.
Return a typed error for each of the two cases, and map that error to the status and the reason code in
`internal/server`. Also leave out every key whose `kty` is `oct` when building the key set that is passed to `jwx`.
Then no other code path can verify an HMAC signature. A table test can cover the following tokens:

- a token whose header algorithm is `none`;
- a token for each of `HS256`, `HS384`, and `HS512`;
- an `HS256` token with a valid signature over a symmetric key in the JWKS;
- an `HS256` token that has also expired.

### Justification

A token whose header algorithm is `none` carries no signature (R1). `jwx` already refuses it. A reason code of its own
lets operators and alerts tell an attack apart from a broken key, and the refusal stays in place if the library or the
way it is called changes (R1).

A JWKS publishes keys. Anyone who can fetch an issuer's JWKS can read a symmetric key in it, and can then sign an HMAC
token that the key verifies (R2). A token with an invalid signature or an expired claim is often what an attacker
sends, so the reason code for the algorithm names the cause that matters (R3).

### Alternatives considered

- **A1. Accept `HS256`, `HS384`, and `HS512` with a shared secret configured per issuer.** Rejected by R2: every
  holder of the secret, including each service that verifies tokens, could sign tokens that the issuer never issued.
  The secret would also need distribution and rotation outside the JWKS.

## Consequences

Negative:

- A token signed with `HS256`, `HS384`, or `HS512` by an issuer whose JWKS holds a symmetric key passed before. After
  the upgrade it gets HTTP 401 with `TOKEN_ALG_SYMMETRIC`, and no setting restores the old behavior (R2).

Follow-ups:

- In the release notes, tell operators to check which of their issuers sign with an HMAC algorithm before they upgrade.

## Open points

- **O1.** R3 assumes that the algorithm's reason code wins over every other reason a token is refused. The alternative
  is the existing order of checks, whatever reason code that order produces. `example-security-architect` decides.
  Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, owned by @example-security-architect. Open point O1 blocks acceptance. It asks which reason code wins when a token is also refused for another cause, such as an expired claim. I assumed `TOKEN_ALG_NONE` or `TOKEN_ALG_SYMMETRIC` wins.

R1 is a rule even though `jwx` already refuses `none`: the review chose the status and the reason code, and `jwx` doesn't provide those. R2 changes behavior. Tokens signed with HMAC that pass today will get HTTP 401 after the upgrade. The record lists this under Negative.

Questions:

1. The notes give no reasons. I wrote the Justification and the reason for rejecting A1 from the standard arguments. Do they match what the security review concluded?
2. I compare `alg` case-sensitively, as RFC 7515 requires. So a token with `NONE` or `None` doesn't get `TOKEN_ALG_NONE`. Instead it fails as an unsupported algorithm with whatever reason code token-gate already uses for that. Is that what you want?
3. Does anyone else approve this record?

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate opens TLS connections as a client, including the HTTPS calls to identity providers. token-gate sets no
minimum version of TLS of its own, so the default of Go's `crypto/tls` applies. The documentation of
`tls.Config.MinVersion` states that a client uses TLS 1.2 as its minimum by default, and it describes this as the
current default. With that default, the client refuses TLS 1.1 and older.

## Decision

We will use only TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: every TLS connection in which token-gate acts as the client, whatever the host. This
  includes connections to identity providers and to an HTTPS proxy.

### Rules

#### Versions of TLS

- **R1** (`server`, `verify`). token-gate aborts the handshake of an outgoing TLS connection when the server offers no
  version later than TLS 1.1, and sends no request over that connection. This holds for every value of every
  configuration setting of token-gate.
- **R2** (`server`, `verify`). token-gate completes the handshake of an outgoing TLS connection with a server that
  offers TLS 1.2 and no later version.

### Implementation notes

Adds no requirement. token-gate meets R1 today through the default of `crypto/tls`. Set `MinVersion: tls.VersionTLS12`
in every client `tls.Config` that token-gate builds. Then neither a new Go release nor a `GODEBUG` setting can change
the version token-gate accepts. A test can start an `httptest` TLS server with `MaxVersion: tls.VersionTLS11` for R1,
and another with `MaxVersion: tls.VersionTLS12` for R2.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1 (R1). Go's default already meets R1. The documentation calls it the current
default, though, so the rule doesn't rely on it. The rule also turns an explicit lower `MinVersion` into a violation
that a checker can see (R1). Identity providers that offer only TLS 1.2 stay reachable (R2).

## Consequences

Negative:

- token-gate cannot reach an identity provider or another server that offers only TLS 1.1 or older, and no setting
  changes that (R1).

## Open points

- **O1.** R2 assumes that the decision keeps TLS 1.2 allowed. The alternative is to let a later change raise the
  minimum to TLS 1.3. `example-security-architect` decides. Affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, owned by @example-security-architect. Open point O1 blocks acceptance. The notes set TLS 1.2 as the minimum but don't say whether a server that offers only TLS 1.2 must stay reachable. I assumed it must (R2).

According to the notes, the code already meets R1 through Go's default, so the record needs no code change. I still recommend setting `MinVersion: tls.VersionTLS12` explicitly in every client `tls.Config`, with a test for each rule. That is in Implementation notes as a recommendation, not a requirement.

Questions:

1. The notes give no reasons. I based the Justification on RFC 8996 and on the fact that Go's default may change. Does that match the security review?
2. I tagged both rules with `server` and `verify` without seeing the code. Which packages open outgoing TLS connections? If one sits outside the layers the reading guide maps, the guide and the tags need that layer.
3. Does anyone else approve this record?
