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

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart.
Some operators run services under Docker without Kubernetes. They configure those services with environment variables
and mounted files.

Under Docker, these operators need token-gate to trust a private CA for its HTTPS calls to the identity provider. On
the platform, operators mount the certificate of such a CA under `/tmp/cert`, and they do this for every image.

Both images of this repository build on the platform base image `ghcr.io/example/platform-base`. The README of the base
image states its contract. Its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or
`.pem` file under `/tmp/cert` to the trust store of the container. It then runs the scripts in `/app/init.d`, and then
runs its arguments.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. We will keep a Compose example in the repository, and CI will start it on every pull request.

### Terms

- **Docker without Kubernetes**: a container that Docker Engine starts, directly or through Docker Compose, where no
  Kubernetes API server is reachable from the container and no Kubernetes service account files are mounted into it.
- **setting**: a value that an operator chooses and that token-gate reads to decide its behavior, such as a listen
  address or an issuer URL. The keys that token-gate fetches from the JWKS of an issuer are not settings.
- **Compose example**: the Compose file that R3 requires, with the files it mounts.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads every setting from environment variables or from files in its container file
  system, and from no other source.
- **R2** (`server`). Under Docker without Kubernetes, with every setting given by environment variables or mounted
  files, token-gate starts and answers `GET /ready` with a 2xx status.

#### The Compose example

- **R3** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate under Docker without Kubernetes and
  gives it every setting by environment variables or mounted files.
- **R4** (`ci`). A job in a workflow under `.github/workflows/` runs on every pull request. It starts the Compose
  example with the token-gate image built from the pull request's commit, and calls `GET /ready` on token-gate. The job
  fails when token-gate does not answer that call with a 2xx status.

### Implementation notes

Adds no requirement. Name the file `deploy/docker/compose.yaml`. In the job of R4, build the image with
`docker build -f build/token-gate/Dockerfile`, pass its tag to Compose through an environment variable, and poll
`GET /ready` until it answers or the job's timeout passes. Where readiness depends on reaching an issuer, add a stub
issuer that serves a JWKS to the Compose example.

### Justification

Operators who run Docker without Kubernetes can run token-gate with the tools Docker already gives them (R1, R2). A
setting read from the Kubernetes API would stop token-gate from starting under Docker (R1). The Compose example gives
operators a working starting point (R3). Starting it on every pull request finds a change that breaks the Docker setup
before the change merges, and keeps the example from drifting away from the code (R2, R4).

### Alternatives considered

- **A1. Read settings from ConfigMaps or Secrets through the Kubernetes API.** Rejected by R1: token-gate could not
  start under Docker without Kubernetes.
- **A2. Describe the Docker setup in a README, with no Compose file and no CI job.** Rejected by R3 and R4: nothing would
  show that the described setup still starts.

## Consequences

Negative:

- A setting that only Kubernetes can supply, such as a value read from the Kubernetes API, cannot be added to token-gate
  (R1).
- Every pull request spends CI time on building the image and starting the Compose example (R4).

## Open points

- **O1.** The notes do not say which image the job starts. R4 assumes the image built from the pull request's commit.
  The other answer is a published image, which would not test the change in the pull request.
  `example-architect` decides. Affects R4.
- **O2.** The notes do not say which response counts as ready. R2 and R4 assume any 2xx status. The other answer is one
  status, such as 200. `example-architect` decides. Affects R2 and R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance. O1 is about which image the CI job starts, and O2 is about which status of `GET /ready` counts as ready. In each case I wrote the rule under an assumption that `@example-architect` should confirm.

I left the entrypoint question out of the record because the existing contract already settles it. The base image's README and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and to set the service's binary as `CMD`. `build/token-admin/Dockerfile` does this. `build/token-gate/Dockerfile` breaks the contract with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue gives a reason for it. Restoring the contract is a bug fix, not a decision. I suggest this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Contract:** the README of `ghcr.io/example/platform-base` and the platform's guide for service images say to keep `/usr/bin/entrypoint.sh` as the entrypoint and set the binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]` instead, so the entrypoint never runs. A private CA mounted under `/tmp/cert` is then not trusted, and the scripts in `/app/init.d` don't run.
- **Fix:** replace the line with `CMD ["/usr/local/bin/token-gate"]`. The chart runs the Pod with a read-only root file system, so add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, where the entrypoint writes.
- **Check:** an `emptyDir` at `/etc/ssl/certs` hides the CA bundle that ships in the image. Confirm that the entrypoint rebuilds the whole bundle, public CAs included, and not only the added certificates.

Until that issue is fixed, operators can't use a private CA under Docker the way the meeting notes expect.

I couldn't read the code, so I took the layer tags (`server`, `docker`, `ci`) from the reading guide. If token-gate reads its settings outside `internal/server`, the tag on R1 and R2 needs to change. The reading guide already maps every layer the record uses, so it needs no change.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-an-hmac-algorithm.md

````markdown
# Refuse a token whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the token's signature
with the `jwx` library. It passes `jwx` every key that the JWKS of the token's issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts a token signed with `HS256`,
`HS384`, or `HS512` when the key set holds a symmetric key. A JWKS is published for any party to read. A symmetric key
in the JWKS of an issuer therefore lets any reader of that JWKS sign tokens that token-gate accepts as tokens of that
issuer.

## Decision

We will refuse a token whose header names the algorithm `none`, and a token signed with an HMAC algorithm, each with
HTTP 401 and a reason code of its own.

### Terms

- **`alg` value**: the value of the `alg` parameter in the protected header of the token that token-gate checks for a
  request.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a request whose token has the `alg` value `none`, compared without
  regard to letter case. The response has HTTP status 401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a request whose token has the `alg` value `HS256`, `HS384`, or
  `HS512`, compared without regard to letter case, whatever keys the JWKS of the token's issuer holds. The response has
  HTTP status 401 and the reason code `TOKEN_ALG_SYMMETRIC`.

#### Precedence

- **R3** (`verify`). Where R1 or R2 applies to a token, the response gets the reason code of that rule, also where
  another check of token-gate would refuse the token.

### Implementation notes

Adds no requirement. In `internal/verify`, read the `alg` value from the protected header before calling `jwx`, and
return a distinct error for R1 and for R2. `internal/server` maps each error to its status and reason code. `jwx`
refuses `none` on its own, but the reason code of R1 comes from token-gate, so the check belongs in `internal/verify`.
Dropping symmetric keys from the key set before it reaches `jwx` is a sound extra measure, and it does not replace the
check of R2.

A table test in `internal/verify` can cover `none`, `None`, `HS256` with an `oct` key in the JWKS, `HS512`, an expired
token with `alg` value `none`, and an `RS256` token that passes.

### Justification

A token whose `alg` value is `none` carries no signature (R1). A token signed with an HMAC algorithm is checked with a
key that also signs, and a key published in a JWKS can be read by anyone (R2). A reason code for each case lets an
operator tell a forged or misconfigured token from an expired token or a bad signature (R1, R2). The code stays the same
whatever else is wrong with the token (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate instead of read from the JWKS.** Rejected
  by R2: token-gate would hold a key that can sign tokens of the issuer.
- **A2. Drop symmetric keys from the key set passed to `jwx`, and let an `HS256` token fail as a bad signature.**
  Rejected by R2: the token would get the reason code of a failed signature instead of `TOKEN_ALG_SYMMETRIC`.

## Consequences

Negative:

- A token signed with `HS256`, `HS384`, or `HS512` by an issuer whose JWKS holds a symmetric key passes the signature
  check today. After the upgrade, it gets HTTP 401 with `TOKEN_ALG_SYMMETRIC`, and no setting restores the old answer
  (R2).

## Open points

- **O1.** The notes do not say whether the `alg` value is compared with or without regard to letter case. R1 and R2
  assume without, so `None` and `hs256` get the codes of those rules. Under an exact match, `jwx` refuses such a token
  as an unknown algorithm, and the token gets the code of that failure. `example-security-architect` decides. Affects
  R1 and R2.
- **O2.** The notes do not say which reason code wins when a token also fails another check, such as an expired token
  whose `alg` value is `none`. R3 assumes that R1 and R2 win over every other check. The other answer is that R1 and R2
  apply only to a token that passes the earlier checks. `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance, and `@example-security-architect` decides both:

- **O1:** does the `alg` match ignore letter case? I assumed it does, so `None` gets `TOKEN_ALG_NONE`.
- **O2:** which code wins when a token also fails another check? I assumed `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` win over every other check.

R2 changes an answer existing installations get. Today `internal/verify` passes `jwx` every JWKS key, so an `HS256` token from an issuer that publishes an `oct` key passes the signature check. After this change it gets 401. Do any issuers in current deployments sign with `HS256`, `HS384`, or `HS512`? If so, their owners need notice before this ships.

I couldn't read the code, so I took the layer tags from the reading guide. I left out **Confirmation** because there are no tests for these rules yet. Add the tests there once they land.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-on-outgoing-tls-connections.md

````markdown
# Use TLS 1.2 or later on every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, such as its HTTPS calls to the identity provider. It sets no minimum TLS
version of its own. With no minimum version set, Go's `crypto/tls` client refuses TLS 1.1 and older. The documentation
of `tls.Config.MinVersion` states this default. A `tls.Config` that sets a lower `MinVersion`, in token-gate or in a
library it uses, lowers the minimum for the connections opened with that configuration.

RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or a later version on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection in which a token-gate process is the TLS client, whatever code opens
  it, including a library, and whether it goes through a proxy or not.

### Rules

#### TLS version

- **R1** (`verify`, `server`). token-gate uses TLS 1.2 or a later version on every outgoing TLS connection. Where the
  server supports only TLS 1.1 or older, the handshake fails, and token-gate sends no application data on that
  connection.

### Implementation notes

Adds no requirement. Go's default meets R1 for a `tls.Config` whose `MinVersion` is zero, and `http.DefaultTransport`
uses that default, so the code needs no change today. Setting `MinVersion: tls.VersionTLS12` in each `tls.Config` also
meets R1, and it shows the minimum in the code.

To test R1, start an `httptest.NewUnstartedServer` with `TLS.MaxVersion` set to `tls.VersionTLS11`, and call it through
the HTTP client that token-gate uses for the identity provider. The call has to fail.

### Justification

TLS 1.0 and TLS 1.1 are deprecated (R1). A rule binds token-gate whatever Go's default is. A change that sets a lower
`MinVersion`, or that adds a library with its own TLS configuration, then fails a rule instead of lowering the minimum
unnoticed (R1).

### Alternatives considered

- **A1. Rely on the default of `crypto/tls` with no recorded decision.** The connections would use TLS 1.2 or later
  today, but a change that set a lower `MinVersion` would break no rule.

## Consequences

Negative:

- token-gate cannot reach a server that supports only TLS 1.1 or older (R1). Go's default already refuses such a
  server, so no existing installation sees a different result.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has no open points, so it can move to `Accepted` once `@example-security-architect` signs off. Do you want me to set that status and the date now?

Go's default already meets R1, so the code needs no change. The record still makes any change that lowers the minimum version break a rule. For a test, I'd make the issuer client call a server limited to TLS 1.1 and expect the call to fail. Once that test exists, list it under **Confirmation**.

I couldn't read the code, so I took the layer tags (`verify`, `server`) from the reading guide. If outgoing connections are opened anywhere else, R1 needs that layer's tag too.
