## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. The repository ships it as a container image and
a Helm chart, and the chart is the only documented way to run it. Some operators run containers under Docker with no
Kubernetes cluster.

Under Docker, operators need to trust a private certificate authority for the HTTPS calls from token-gate to the
identity provider. The README of the platform base image `ghcr.io/example/platform-base` states that the entrypoint of
that image adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the
container.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone.
The repository ships a Compose example, and a CI job starts it on every pull request.

### Terms

- **Docker deployment**: a token-gate container that Docker or Docker Compose runs, in an environment with no
  Kubernetes cluster.
- **Compose example**: the Docker Compose file under `deploy/docker/` that starts token-gate as a Docker deployment.

### Rules

#### Running under Docker

- **R1** (`server`). In a Docker deployment, token-gate starts and answers requests when its only configuration sources
  are environment variables and files mounted into its container.
- **R2** (`docker`). `deploy/docker/` holds a Compose example that configures token-gate with environment variables and
  mounted files alone.

#### Checking the example

- **R3** (`ci`). A job in `.github/workflows/` runs on every pull request, starts the Compose example, and sends
  `GET /ready` to token-gate. The job fails when the response is not HTTP 200.

### Confirmation

- **R1**: the job of R3 starts token-gate from the Compose example and fails when token-gate does not answer
  `GET /ready`.
- **R2**: the job of R3 fails when `deploy/docker/` holds no Compose example that starts.

### Justification

The job of R3 starts the Compose example of R2 on every pull request, so a change that breaks the Docker deployment of
R1 fails before it merges.

## Consequences

Negative:

- Every pull request runs a Docker start and a readiness call (R3), which adds CI time.
- A change to the configuration of token-gate must keep working from environment variables and mounted files (R1), so a
  setting that only Kubernetes can supply is not allowed.

## Open points

- **O1.** Assumption: `GET /ready` exists and answers HTTP 200 when token-gate is ready. The architect confirms the
  status code. It affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has one open point, O1, which blocks acceptance. I assumed `GET /ready` answers HTTP 200 when ready. Please confirm that.

Questions:
- Who owns the ADR? The Owner field holds the placeholder `<owner account>`. I put `example-architect` under approvers.
- Which layer holds the configuration code? I tagged R1 with `server`. Change the tag if that code lives elsewhere.

The open question in the notes, whether to keep the binary as the entrypoint, is not a decision, so the record has no rule and no open point for it. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. That replaces the platform entrypoint, which `build/token-admin/Dockerfile` keeps. The base image README and the platform guide for service images both say to keep the platform entrypoint and set the binary as `CMD`. The line has been there since the first commit, and no record or issue explains it. Restoring the contract is a fix, so I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so `/tmp/cert` certificates and `/app/init.d` scripts are ignored
- **Contract:**
  - The entrypoint `/usr/bin/entrypoint.sh` of `ghcr.io/example/platform-base` adds the certificates under `/tmp/cert` to the trust store, runs the scripts in `/app/init.d`, and then runs its arguments.
  - The platform guide says to keep that entrypoint and set the service binary as `CMD`.
- **Fix:**
  - Replace the `ENTRYPOINT` in `build/token-gate/Dockerfile` with `CMD ["token-gate"]`, as `build/token-admin/Dockerfile` does.
  - Add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates` to the chart, because the entrypoint writes there and the chart runs the Pod with a read-only root file system.

If the `ENTRYPOINT` is deliberate, tell me and I will add a rule for it.

Until that issue is fixed, a private CA mounted under `/tmp/cert` has no effect in the Compose example.

I did not change `docs/adr/README.md`. The layers `docker`, `ci`, and `server` are already mapped there. The pull request that adds the Compose example and the CI job should end with `Implements: ADR-0007 R1, R2, R3`.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-algorithm-none-or-a-symmetric-algorithm.md

````markdown
# Refuse tokens with the algorithm none or a symmetric algorithm

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. `jwx` accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key. `internal/verify` passes `jwx` every key that the JWKS of an issuer
holds, so a symmetric key in that JWKS makes a token with one of those algorithms verifiable.

## Decision

We will refuse a token whose `alg` header is `none` with the reason code `TOKEN_ALG_NONE`, and a token whose `alg`
header is `HS256`, `HS384`, or `HS512` with the reason code `TOKEN_ALG_SYMMETRIC`. Both refusals are HTTP 401.

### Terms

- **token**: the token that token-gate checks in a request.
- **refuses**: token-gate answers the request with the stated HTTP status and reason code and passes the request to no
  policy evaluation.
- **symmetric algorithm**: one of `HS256`, `HS384`, and `HS512`.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a request with HTTP 401 and the reason code `TOKEN_ALG_NONE` in
  `<reason code field>` when the `alg` header of its token is `none`, whatever else is wrong with the token.
- **R2** (`verify`, `server`). token-gate refuses a request with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC` in
  `<reason code field>` when the `alg` header of its token is a symmetric algorithm, whatever else is wrong with the
  token and whichever keys the JWKS of the issuer holds.

### Implementation notes

Adds no requirement. `jwx` already refuses `none` at signature verification, so `internal/verify` needs to read the
`alg` header and map the case to its reason code. `jwx` accepts a symmetric algorithm when the key set holds a symmetric
key, so the check for R2 has to run before `internal/verify` calls `jwx`.

### Justification

R2 holds whichever keys the JWKS of the issuer holds, because `internal/verify` passes every key of that JWKS to `jwx`,
and `jwx` would accept a symmetric algorithm for a symmetric key among them. Two reason codes let a caller tell the
refusal of R1 from the refusal of R2.

### Alternatives considered

- **A1. Accept HMAC tokens, verified with a shared secret per issuer.** Rejected by R2: token-gate would hold a secret
  with which anyone can mint tokens for that issuer. The security review considered this option and rejected it.

## Consequences

Negative:

- A token signed with a symmetric algorithm is refused with HTTP 401 even where the JWKS of its issuer holds a symmetric
  key and `jwx` would have verified it (R2). An issuer that signs with HMAC cannot be used.
- A caller that matched the answer for a token with the algorithm `none` against the reason of an earlier answer sees
  `TOKEN_ALG_NONE` instead (R1).

## Open points

- **O1.** The place of the reason code in the answer, such as a field of the response body or a header, and its name.
  The security architect decides. It affects R1 and R2.
- **O2.** The values `None`, `NONE`, and `hs256`. The answers: refuse them with the same reason code as the lowercase
  value, or leave them to the refusal of an unsupported algorithm. The security architect decides. It affects R1 and R2.
- **O3.** Assumption: the algorithm refusals come before every other refusal of a token, such as a malformed or an
  expired token, so a token with an algorithm of R1 or R2 always gets that reason code. The security architect confirms
  or names another order. It affects R1 and R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance:
- **O1:** where the reason code appears in the response.
- **O2:** what to do with `alg` values in another case, such as `None` or `hs256`.
- **O3:** my assumption that the algorithm refusals come before every other refusal.

Questions:
- Who owns the ADR? The Owner field holds the placeholder `<owner account>`.
- What was the reason for rejecting HMAC with a shared secret per issuer? The notes give none. A1 states only that the service would hold a secret that can mint tokens, so please check it.
- What reason code and status did callers get for an `alg` of `none` before this change? The second Negative item says only that callers who matched the earlier answer will see `TOKEN_ALG_NONE`, because the notes do not give the old one.

The rule for `none` is a decision although `jwx` already refuses that algorithm. The decision adds the HTTP 401 answer and the reason code `TOKEN_ALG_NONE`. I tagged both rules with `verify` and `server`, because I assume `internal/verify` decides the refusal and `internal/server` writes the response. Change the tags if the response is written elsewhere.

I did not add a Confirmation section, because I know of no existing test. The change that brings the code should add one test per rule, then list the tests there.

The pull request that implements the rules should end with `Implements: ADR-0007 R1, R2`.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1.

## Context

token-gate opens TLS connections to other services, such as the identity provider of an issuer. The `crypto/tls` client
of Go refuses TLS 1.1 and older by default, and token-gate sets no minimum version of its own. TLS 1.0 and TLS 1.1 are
deprecated by RFC 8996.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that token-gate opens as the client, to any host. A connection that
  token-gate accepts as the server is not one.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate completes no outgoing TLS connection handshake with a protocol version below
  TLS 1.2, for every host and every configuration of token-gate. The handshake fails instead.

### Implementation notes

Adds no requirement. R1 needs no code today, because the default of the `crypto/tls` client already meets it. A test can
start a local TLS server that is limited to TLS 1.1 and expect the handshake of an outgoing connection to fail.

### Justification

TLS 1.0 and TLS 1.1 are deprecated (RFC 8996), and every deployed TLS endpoint that token-gate calls is expected to
support TLS 1.2 (R1).

## Consequences

Positive:

- token-gate carries no TLS version setting of its own to maintain.

Negative:

- token-gate cannot call a host that supports only TLS 1.1 or older (R1).
- R1 holds through the default of the `crypto/tls` client, so a Go toolchain whose default is lower, or a setting added
  later that lowers the minimum version, breaks it.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, and it has no open points. Once the security architect signs off, set the status to `Accepted` and add the Date heading.

Questions:
- Who owns the ADR? The Owner field holds the placeholder `<owner account>`.
- Which code opens the outgoing connections? I tagged R1 with `verify` and `server`. Please confirm the tags, or give me the right layer.

I wrote R1 as a rule although the Go default already meets it, because the security architect decided it. The rule also forbids a later setting that lowers the minimum. If you want token-gate to set `MinVersion` explicitly instead of relying on the default, tell me. That would be a separate structural rule.

The sentence in the Justification that every endpoint token-gate calls is expected to support TLS 1.2 is my inference, not from the notes. Please check it.

I did not add a Confirmation section, because I know of no existing test. The Implementation notes suggest one.

I did not change `docs/adr/README.md`. The pull request that adds a test, if any, should end with `Implements: ADR-0007 R1`.
