## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, and test that support in CI

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart,
so Kubernetes is the only supported way to run it today. Operators who run it under Docker without Kubernetes need to
trust a private CA for the HTTPS calls from token-gate to the identity provider.

The platform base image `ghcr.io/example/platform-base` documents its entrypoint in its README. The entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. Operators of every image of the
platform mount a CA certificate under `/tmp/cert` for that reason.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone,
and we will ship a Compose example that a CI job starts on every pull request.

### Terms

- **Compose example**: the Compose file under `deploy/docker/` and the files that it mounts.

### Rules

#### Running under Docker

- **R1** (`server`). token-gate starts and serves requests with configuration taken from environment variables and files
  alone.
- **R2** (`docker`). The repository ships a Compose example that runs token-gate, and the Compose example configures
  token-gate with environment variables and mounted files alone.

#### Testing the Compose example

- **R3** (`ci`). A CI job starts the Compose example on every pull request and calls `GET /ready`. The job fails when
  the response status is not 2xx.

### Confirmation

- **R3**: the CI job that R3 describes is the check. It fails the pull request when the Compose example does not start
  or `GET /ready` does not return a 2xx status.

### Justification

Docker without Kubernetes offers environment variables and mounted files as its configuration channels, so token-gate
must start from those alone (R1, R2). A Compose example that no job starts can break without notice, and a request that
returns 2xx from `GET /ready` shows that the example starts and serves (R3).

### Alternatives considered

- **A1. Ship a Compose example that no CI job starts.** Rejected by R3: nothing would show a pull request that breaks
  it.

## Consequences

Negative:

- Every pull request pays for one Compose start in CI (R3).
- The Compose example is a second supported way to run token-gate, next to the Helm chart, and a change to the
  configuration of token-gate has to keep both working (R1, R2).

## Open points

- **O1.** R3 assumes that `GET /ready` signals readiness with a 2xx status. `example-architect` confirms the status, or
  names another. R3 depends on the answer.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Its Owner is a placeholder because the notes name no owner. Who owns this ADR?

Open point O1 blocks acceptance. I assumed that `GET /ready` returns a 2xx status when ready, so please confirm the status.

I wrote no rule for the entrypoint question, because the repository's contracts already settle it. The base image README and the platform guide for service images say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-admin/Dockerfile` does that with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and nothing records a reason. That makes `/tmp/cert` ignored for token-gate, so it is a defect, not a decision. The record states the base entrypoint's behavior as a Context fact and names no issue or fix.

Proposed issue:

- **Type**: Bug
- **Title**: token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are ignored
- **Contract departed from**: the README of `ghcr.io/example/platform-base` and the platform guide for service images.
- **Fix**: in `build/token-gate/Dockerfile`, remove the `ENTRYPOINT` and set the binary as `CMD`, as `build/token-admin/Dockerfile` does.
- **Chart change**: add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. The restored entrypoint writes there, and the chart runs the Pod with a read-only root file system.

If the `ENTRYPOINT` is deliberate, tell me and I will write a rule for it.

`docs/adr/README.md` already maps `docker`, `ci`, and `server`, so it needs no change. Changes that bring R1 to R3 end their commit message and pull request description with `Implements: ADR-0007 R1, R2, R3`, or with `Defers` for the rules they leave out.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-hmac-algorithms.md

````markdown
# Refuse a token whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation, and `internal/verify` verifies its signature with
the `jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. `jwx` accepts `HS256`,
`HS384`, and `HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of
an issuer holds. A symmetric key in an issuer's JWKS would therefore make token-gate accept an HMAC-signed token.

## Decision

We will refuse a token whose header names the algorithm `none` with the reason code `TOKEN_ALG_NONE`, and a token whose
header names `HS256`, `HS384`, or `HS512` with the reason code `TOKEN_ALG_SYMMETRIC`, both with HTTP 401.

### Terms

- **token**: the token that token-gate checks in a request.
- **names an algorithm**: the `alg` value of the token header equals that algorithm string exactly, as RFC 7518 spells
  it. O1 asks whether other spellings count.
- **refused**: token-gate sends the stated response, and policy evaluation does not run for the request.

### Rules

#### Algorithm refusals

- **R1** (`verify`, `server`). A token whose header names `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). A token whose header names `HS256`, `HS384`, or `HS512` is refused with HTTP 401 and the
  reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of its issuer holds and whether or not its signature would
  verify.

### Implementation notes

Adds no requirement. The check can read the `alg` value from the token header before the token reaches `jwx`. That way
the reason codes do not depend on how `jwx` reports its own refusals.

### Justification

`jwx` already refuses `none`, but its refusal carries neither of the reason codes, so R1 fixes the response that a
caller sees. `jwx` accepts an HMAC algorithm whenever the key set holds a symmetric key, and `internal/verify` passes it
every key of the JWKS, so R2 states the refusal independently of the keys. Separate reason codes tell an operator which
of the two refusals happened (R1, R2).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2: the security review considered this design and
  rejected it, and R2 refuses `HS256`, `HS384`, and `HS512` for every issuer.

## Consequences

Negative:

- A token from an issuer that signs with HMAC, which `jwx` may verify today, is refused with `TOKEN_ALG_SYMMETRIC`
  after this change (R2). A test that sends an `HS256` token signed with a key from the JWKS of an issuer shows the new
  answer.

## Open points

- **O1.** The rules assume that `alg` is compared exactly, so that `None` or `hs256` does not count as `none` or
  `HS256`. `example-security-architect` decides whether other spellings are also refused with the same codes. The answer
  affects R1 and R2.
- **O2.** The notes do not say how a response carries the reason code. The rules assume the mechanism that other
  refusals of token-gate use. `example-security-architect` confirms it. The answer affects R1 and R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Its Owner is a placeholder because the notes name no owner. Who owns this ADR?

Two open points block acceptance:

- **O1**: whether `None` or `hs256` count as `none` or `HS256`. I assumed an exact match.
- **O2**: how a response carries the reason code. I assumed the mechanism that other refusals use.

The notes give no reason for rejecting HMAC with a shared secret per issuer, so A1 says only that the review rejected it. Send me the reason and I will add it.

I kept R1 as a rule although `jwx` already refuses `none`. The status and the reason code are the decision, and `jwx` provides neither. R2 describes behavior that the code does not have today: `jwx` accepts HMAC when the key set holds a symmetric key.

`docs/adr/README.md` already maps `verify` and `server`, so it needs no change. Changes that bring R1 or R2 carry the `Implements` trailer. A change that brings only R1 names R2 under `Defers`, with an issue that exists.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections as a client, for example to the identity provider. The `crypto/tls` client of Go
refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. The behavior therefore follows
the Go release that builds token-gate. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will require TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any peer.

### Rules

#### Minimum TLS version

- **R1** (`verify`, `server`). An outgoing TLS connection of token-gate negotiates TLS 1.2 or later, and its handshake
  fails where the peer offers only TLS 1.1 or older.

### Implementation notes

Adds no requirement. The default of the Go `crypto/tls` client already meets R1, so no code has to change. Setting
`MinVersion` to `tls.VersionTLS12` in each `tls.Config` of token-gate would keep R1 true if a later Go release changed
the default.

### Justification

TLS 1.1 and older are deprecated (R1). A rule that holds for every outgoing TLS connection also holds for connections
that a later change adds (R1).

### Alternatives considered

- **A1. Set no requirement and rely on the default of the Go `crypto/tls` client.** The default belongs to the Go
  release and no decision of this system fixes it, so a Go upgrade could change what token-gate accepts.

## Consequences

Negative:

- A connection from token-gate to a peer that offers only TLS 1.1 or older fails its handshake (R1).

## Open points

- **O1.** The rule assumes that the outgoing TLS connections are opened by code in `internal/verify` and
  `internal/server`. The maintainers of token-gate confirm which packages open them, and the layer tags of R1 change
  accordingly.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Its Owner is a placeholder because the notes name no owner. Who owns this ADR?

Open point O1 blocks acceptance. I could not tell from the repository facts which packages open the outgoing connections, so I tagged R1 with both `verify` and `server`.

R1 is already met, because Go's default refuses TLS 1.1 and older. I wrote it as a rule anyway, since the security architect decided it and the Go default is not a choice of this system. No issue is needed. The Implementation notes suggest setting `MinVersion` explicitly, so that a later Go release cannot weaken R1. The record adds no Confirmation entry because no check exists yet. A test that dials a peer limited to TLS 1.1 would be a natural one.

`docs/adr/README.md` already maps `verify` and `server`, so it needs no change. A change that adds the explicit `MinVersion` or the test names R1 under `Implements`.
