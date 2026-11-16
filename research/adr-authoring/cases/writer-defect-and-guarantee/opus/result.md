## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image, built by
`build/token-gate/Dockerfile`, and as a Helm chart under `helm/`. The chart is the only supported way to run it, so
operators who run containers with Docker and without Kubernetes have no tested setup.

Under Docker, operators need token-gate to trust a private CA for its HTTPS calls to the identity provider. On the
platform, an operator does this by mounting the CA certificate under `/tmp/cert`. The image of token-gate builds on the
platform base image `ghcr.io/example/platform-base`. The README of the base image states its contract: its entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. The platform's guide for
service images says to keep that entrypoint and to set the service's binary as `CMD`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
The repository ships a Compose example, and CI starts it on every pull request.

### Terms

- **Compose example**: the Compose file under `deploy/docker/` that R2 requires, with the files it mounts.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads every setting from environment variables or from files in its container's file
  system, and from no other source, such as the Kubernetes API.

#### Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate and configures it by environment
  variables and mounted files alone.

#### Continuous integration

- **R3** (`ci`). A job under `.github/workflows/` runs on every pull request, starts the Compose example with the
  token-gate image built from the pull request, calls `GET /ready` on token-gate, and fails unless the response has the
  status HTTP 200.

### Implementation notes

Adds no requirement. Name the Compose file `deploy/docker/compose.yaml`. In the CI job, build the image, override the
image of the token-gate service through an environment variable in the Compose file, start the example with
`docker compose up --wait`, and call `GET /ready` with `curl --fail`. Where token-gate needs an identity provider to
become ready, add a stub issuer that serves a JWKS to the Compose example.

### Justification

Operators who run containers without Kubernetes can only use token-gate if every setting reaches it through what Docker
provides, which is environment variables and mounted files (R1). A Compose file in the repository gives them a working
starting point (R2). A job that starts that file on every pull request keeps it working as the service changes (R3).

### Alternatives considered

- **A1. Support Kubernetes only, and leave Docker to operators.** Each operator would then have to work out the
  configuration from the chart, and no check would show that token-gate starts outside Kubernetes.

## Consequences

Positive:

- A developer can start token-gate locally with the Compose example, without a cluster.

Negative:

- Every pull request waits for the Compose job of R3, and a change that breaks the Compose example fails CI even where
  the chart still works.
- token-gate cannot take a setting from a source that only Kubernetes provides, such as a watch on a ConfigMap (R1).

## Open points

- **O1.** R3 assumes that the job fails unless `GET /ready` returns HTTP 200. The alternative is to accept any 2xx
  status. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md`, with the status `Proposed`. It has one open point, O1, which blocks acceptance. The notes only say that the CI job calls `GET /ready`. So I assumed the job fails unless the response is HTTP 200, and @example-architect needs to confirm that.

I left the notes' open question (keep the binary as the entrypoint, or switch to the base entrypoint) out of the record. It isn't a decision. The base image's contract and the platform's guide already settle it, and `build/token-gate/Dockerfile` departs from them with no recorded reason. `build/token-admin/Dockerfile` already follows the contract. Restoring the entrypoint is a fix, so I propose an issue instead:

- **Type**: Bug
- **Title**: token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body**: `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. That replaces `/usr/bin/entrypoint.sh` from `ghcr.io/example/platform-base`. The base image's README says that entrypoint adds every `.crt`, `.cer`, and `.pem` file under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and to set the service's binary as `CMD`, as `build/token-admin/Dockerfile` does. Because of this, a CA certificate mounted under `/tmp/cert` isn't trusted, and the scripts in `/app/init.d` don't run.
  - Fix: replace the line with `CMD ["/usr/local/bin/token-gate"]`.
  - Fix: the chart runs the Pod with a read-only root file system, and the base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. So the chart needs an `emptyDir` volume at each of those paths.

Operators can trust a private CA under Docker only once this issue is fixed. Shall I open it? If the binary is the entrypoint on purpose, tell me why, and I'll add a rule and the reason to the record.

## Request 2

### File: docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md

````markdown
# Refuse tokens whose algorithm is `none` or HMAC with HTTP 401 and a reason code for each

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the signature with the
`jwx` library and passes it every key that the JWKS of the issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature, and it reports this with the same kind of error
as any other failed verification. `jwx` accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key. So
token-gate accepts a token with an HMAC signature from any issuer whose JWKS holds a symmetric key.

## Decision

We will refuse a token whose algorithm is `none`, and a token signed with HMAC, with HTTP 401 and a reason code for each.

### Terms

- **token**: the JWS that token-gate checks for a request before policy evaluation.
- **`alg` header**: the `alg` parameter in the protected header of a token.

### Rules

#### Unsigned tokens

- **R1** (`verify`, `server`). token-gate refuses a token whose `alg` header is `none`, compared without regard to
  letter case, with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

#### HMAC signatures

- **R2** (`verify`, `server`). token-gate refuses a token whose `alg` header is `HS256`, `HS384`, or `HS512` with HTTP
  401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the issuer holds and whatever the settings
  of token-gate.

#### Precedence

- **R3** (`verify`, `server`). Where R1 or R2 applies to a token that another check of token-gate also refuses, such as
  the check of its expiry or of its issuer, the response carries the reason code that R1 or R2 names.

### Implementation notes

Adds no requirement. In `internal/verify`, parse the protected header and check the `alg` header before calling `jwx`,
and return an error for each of R1 and R2 that `internal/server` maps to its response. Check the `alg` header before
every other check of the token, so that R3 holds without further code. `jwx` already refuses `none`, but its error
doesn't separate that case from a bad signature, so R1 needs its own check. As a second safeguard, leave keys whose
`kty` is `oct` out of the key set that `internal/verify` passes to `jwx`.

Cover each rule with a test that sends a token through `internal/server` and checks the status and the reason code: one
for `none` and one for `NONE` (R1), one for each of `HS256`, `HS384`, and `HS512` against a JWKS that holds a matching
symmetric key (R2), and one with `alg` set to `none` and an expired `exp` (R3).

### Justification

A token with `alg` set to `none` carries no signature, so a client that sends one chooses its own claims (R1). Attackers
also send the value in other letter cases, such as `None`, to get past a check that compares it exactly (R1).

An HMAC key both signs and verifies. A JWKS is published, so a symmetric key in it lets anyone sign tokens for that
issuer, and `internal/verify` passes such a key to `jwx` today (R2). Refusing HMAC whatever the JWKS holds also closes
algorithm confusion, where a client signs an HMAC token with a key that the issuer meant for another algorithm (R2).

A reason code for each case lets operators separate these refusals from expired or badly signed tokens in logs and
responses (R1, R2). Checking the algorithm first makes the reported cause the same whatever else is wrong with the token
(R3).

### Alternatives considered

- **A1. Accept `HS256`, `HS384`, and `HS512` with a shared secret configured per issuer.** Rejected by R2: every party
  that holds the secret can sign tokens that token-gate accepts, so a leak at any of them, the issuer or any token-gate
  installation, lets the holder sign tokens for that issuer.

## Consequences

Positive:

- A JWKS that publishes a symmetric key by mistake no longer lets anyone sign tokens that token-gate accepts (R2).

Negative:

- After the upgrade, token-gate refuses with `TOKEN_ALG_SYMMETRIC` every token of an issuer that signs with `HS256`,
  `HS384`, or `HS512`, including tokens it accepted before because the issuer's JWKS holds the symmetric key (R2).

Follow-ups:

- Before the release that brings R2, find the issuers that sign with HMAC, and tell their owners.

## Open points

- **O1.** R1 assumes that `alg` is compared without regard to letter case, so that `None` and `NONE` get
  `TOKEN_ALG_NONE`. The alternative is to match `none` exactly and leave other cases to the response for an unknown
  algorithm. `example-security-architect` decides. Affects R1.
- **O2.** R3 assumes that the reason codes of R1 and R2 take precedence over every other check of the token. The
  alternatives are to let another check, such as the check of the issuer, take precedence, or to follow an order that
  records 0001 to 0006 already set. `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md`, with the status `Proposed`. Two open points block acceptance, and @example-security-architect decides both:

- **O1.** Does `none` match without regard to letter case (`None`, `NONE`)? R1 assumes it does.
- **O2.** Do `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` take precedence over the reason code of any other check that also refuses the token? R3 assumes they do. If records 0001 to 0006 already set an order for reason codes, tell me and I'll change R3 to match.

The notes don't say why HMAC with a shared secret per issuer was rejected. I wrote the reasons in the Justification and in A1 from the facts above: a JWKS is public, and anyone who holds an HMAC key can sign with it. Can @example-security-architect confirm that these are the reasons, or give theirs?

R2 changes what token-gate accepts today. `internal/verify` passes symmetric keys from a JWKS to `jwx`, so an issuer that signs with HMAC loses its tokens on upgrade. The record names this under Negative, with a follow-up to find those issuers first.

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

token-gate makes HTTPS calls to the identity providers of its issuers. token-gate sets no minimum TLS version of its own,
so the default of Go's `crypto/tls` applies. Under that default, a `crypto/tls` client refuses TLS 1.1 and older (Go
documentation of `tls.Config.MinVersion`). The default belongs to the Go toolchain, and a `GODEBUG` setting can lower it
(Go documentation of `GODEBUG`).

RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, through any library,
  including the HTTPS calls to an identity provider.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate completes the handshake of an outgoing TLS connection only at TLS 1.2 or
  later. Where the server offers only TLS 1.1 or older, the handshake fails, and token-gate sends no request on that
  connection.

### Implementation notes

Adds no requirement. The default of `crypto/tls` meets R1 today. Set `MinVersion: tls.VersionTLS12` in the `tls.Config`
of each HTTP client that token-gate builds, so that neither a `GODEBUG` setting nor a newer toolchain can lower the
minimum. Show R1 with a test that starts an `httptest` server whose `tls.Config` sets `MaxVersion: tls.VersionTLS11`,
and checks that the call to it fails with no request received.

### Justification

TLS 1.0 and TLS 1.1 are deprecated, and the calls to an identity provider carry the keys that token-gate trusts (R1). A
rule makes the minimum a requirement that a change can fail. A default can change without any change to token-gate
(R1).

### Alternatives considered

- **A1. Leave the minimum to the default of `crypto/tls`, with no record.** The default meets the requirement today, but
  a `GODEBUG` setting or a change of toolchain could lower it, and no review would treat that as a failure.

## Consequences

Negative:

- token-gate can't reach an identity provider that serves only TLS 1.1 or older (R1). Installations get no change on
  upgrade, because the default of `crypto/tls` already refuses those versions.
````

### Message to the user

I wrote the record as `docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md`, with the status `Proposed`. It has no open points, so you can set it to `Accepted`, with the date, once @example-security-architect signs off.

The notes say that Go's default already meets the decision. I still recorded it as a rule, because the minimum is a decision, and the default could change without any change to token-gate. No code change is needed to meet R1. The implementation notes recommend setting `MinVersion: tls.VersionTLS12` explicitly, plus a test.

I couldn't read the code, so I tagged R1 with `verify` and `server` because I assumed those layers make the outgoing calls. Which packages open outgoing TLS connections? If another layer does, I'll add its tag.
