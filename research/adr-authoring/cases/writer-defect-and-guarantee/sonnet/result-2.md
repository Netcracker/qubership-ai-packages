## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

## Context

token-gate ships as a container image and a Helm chart. Some operators run the image under Docker without Kubernetes.
They need to trust a private CA for the HTTPS calls to the identity provider.

The images of the platform build on `ghcr.io/example/platform-base`. Its README states that its entrypoint,
`/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. Operators mount the certificate
of a private CA under `/tmp/cert`, as for every image of the platform.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, and we will ship a Compose example that a CI job starts on every pull request.

### Terms

- **Docker deployment**: a run of the token-gate image by Docker or Docker Compose, with no Kubernetes cluster involved.
- **Compose example**: the Compose file under `deploy/docker/` that R2 requires.

### Rules

#### Support under Docker

- **R1** (`server`). In a Docker deployment, token-gate starts and serves requests when its configuration comes from
  environment variables and mounted files alone, and it calls no Kubernetes API.
- **R2** (`docker`). The directory `deploy/docker/` holds a Compose example that starts token-gate as a Docker
  deployment.
- **R3** (`ci`). A CI job starts the Compose example on every pull request, calls `GET /ready` on the started
  token-gate, and fails the job where the response is not HTTP 200.

### Justification

Operators without a cluster can run token-gate only if it needs nothing that Kubernetes provides (R1), and the Compose
example shows them how (R2). The CI job fails a pull request that breaks the example, so the example stays usable
(R2, R3).

### Alternatives considered

- **A1. Ship a Compose example that no CI job starts.** Rejected by R3: nothing would show that the example still
  starts token-gate after a change.

## Consequences

Negative:

- Every setting of token-gate needs a form that an environment variable or a mounted file can carry (R1).
- Every pull request pays for one CI job that starts the Compose example (R3).

## Open points

- **O1.** The notes do not say which response of `GET /ready` passes the job. R3 assumes HTTP 200. The architect,
  `example-architect`, decides whether another status or a response body also counts. This affects R3.
````

### Message to the user

I wrote the record as `Proposed`. O1 blocks acceptance: the notes don't say which `GET /ready` response passes the CI job, so I assumed HTTP 200.

The open question about the entrypoint is not in the record, because it is a defect and not a decision. The base image README and the platform guide for service images both say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-gate/Dockerfile` replaces the entrypoint with `ENTRYPOINT ["/usr/local/bin/token-gate"]`. No record or issue explains that line, and `build/token-admin/Dockerfile` already uses `CMD ["token-admin"]`. Restoring the entrypoint is a fix, and `/tmp/cert` is a guarantee of the base image. So neither gets a rule. The record states the `/tmp/cert` behavior in Context as a fact.

I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Contract:** the README of `ghcr.io/example/platform-base` and the platform guide for service images. The entrypoint adds the certificates under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. Service images keep it and set the binary as `CMD`.
- **Departure:** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`.
- **Fix:** remove the `ENTRYPOINT` and end with `CMD ["/usr/local/bin/token-gate"]`. In the chart, add `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. The base entrypoint writes there, and the root file system of the Pod is read-only.

If the replaced entrypoint is deliberate, tell me. It then becomes a decision with a rule.

Changes under `deploy/docker/`, `.github/workflows/`, and the code for R1 end their commit message and pull request description with the `Implements` and `Defers` trailers. A `Defers` target must be an issue that exists. Please open one for R3 if the CI job lands in a later change.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-a-symmetric-algorithm.md

````markdown
# Refuse a token whose header names the algorithm none or a symmetric algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library. `jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`,
and `HS512` when the key set holds a symmetric key, and `internal/verify` passes it every key that the JWKS of an issuer
holds. A token signed with HMAC therefore passes verification where the JWKS of its issuer holds a symmetric key.

## Decision

We will refuse a token whose header names the algorithm `none`, and a token whose header names a symmetric algorithm,
each with HTTP 401 and its own reason code.

### Terms

- **token**: the token that token-gate checks on a request.
- **header algorithm**: the value of the `alg` parameter in the JOSE header of a token, compared as an exact,
  case-sensitive string.
- **symmetric algorithm**: `HS256`, `HS384`, or `HS512`.

### Rules

#### Algorithms

- **R1** (`verify`, `server`). Where the header algorithm of a token is `none`, token-gate refuses the token with HTTP
  401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). Where the header algorithm of a token is a symmetric algorithm, token-gate refuses the
  token with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whether or not the JWKS of the issuer holds a symmetric
  key.

### Implementation notes

Adds no requirement. Read the `alg` parameter from the token header before the token goes to `jwx`, so that token-gate
chooses the reason code itself. The refusal of `jwx` for `none` produces `TOKEN_ALG_NONE` only where the code maps it
to that code.

### Justification

R1 gives a token with `none` a reason code of its own. R2 closes the path on which `jwx` accepts HMAC for every issuer
whose JWKS holds a symmetric key, because `internal/verify` passes it every key of the JWKS.

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2. The security review considered this option and
  rejected it. O2 asks for the reason.

## Consequences

Negative:

- A token signed with `HS256`, `HS384`, or `HS512` that token-gate accepted before, because the JWKS of its issuer holds
  a symmetric key, gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` after the change (R2). An issuer that signs with HMAC has to
  change its algorithm.

## Open points

- **O1.** The record assumes that the header algorithm is compared as an exact, case-sensitive string, so `None` and
  `hs256` match neither R1 nor R2. The security architect, `example-security-architect`, decides whether the comparison
  ignores case instead. This affects R1 and R2.
- **O2.** The notes give no reason for rejecting HMAC with a shared secret per issuer. The security architect,
  `example-security-architect`, supplies it for the Justification and for A1. This affects R2.
````

### Message to the user

I wrote the record as `Proposed`. Two open points block acceptance:

- **O1:** I assumed an exact, case-sensitive comparison of `alg`. Do `None` or `hs256` count as `none` or a symmetric algorithm?
- **O2:** the notes give no reason for rejecting HMAC with a shared secret per issuer, and I did not invent one. Please ask `example-security-architect` for it.

The two refusals stay in one record because one authority settles them for one reason.

The code isn't visible to me, so I tagged both rules `verify` and `server`. `verify` produces the refusal and `server` produces the 401. Please correct the tags if the response mapping lives elsewhere.

I named no check under Confirmation because I know of no existing test. Tests for each rule would belong in the implementing change.

R2 changes the answer for issuers that sign with HMAC and whose JWKS holds a symmetric key. The Negative consequence names that case.

A change under `internal/verify` or `internal/server` ends its commit message and pull request description with the `Implements` and `Defers` trailers for R1 and R2.

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

The Go `crypto/tls` client refuses TLS 1.1 and older by default. token-gate sets no minimum version of its own, so its
outgoing TLS connections get that default.

## Decision

We will require TLS 1.2 or later on every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, whether its own code or
  a library it uses opens the connection.

### Rules

#### TLS version

- **R1** (`verify`, `server`). On an outgoing TLS connection, token-gate completes the handshake only at TLS 1.2 or
  later, and ends the handshake with an error where the peer offers only TLS 1.1 or older.

### Implementation notes

Adds no requirement. Code that sets no minimum version meets R1 through the default of the Go client. Setting
`MinVersion` to `tls.VersionTLS12` on each `tls.Config` makes R1 independent of the Go version that builds the binary.

### Justification

The security review set TLS 1.2 as the lowest version that token-gate accepts (R1). The default of the Go client
already enforces it, so R1 needs no code change today.

## Consequences

Negative:

- A peer that supports only TLS 1.1 or older, such as an old identity provider, is unreachable for token-gate (R1).
````

### Message to the user

I wrote the record as `Proposed`, with no open points. Once the team signs off, set it to `Accepted` and add the Date heading with the acceptance date.

This is a decision and not a dependency guarantee, because the architect chose TLS 1.2 for this system. It gets R1 although the code already meets it.

Please confirm two things:

- The tags `verify` and `server` are my guess for the code that opens outgoing connections. Add the right layer if other code, such as the startup code, also opens one.
- The notes don't say whether R1 should hold if a future Go release changes its client default. The Implementation notes suggest an explicit `MinVersion`. If you want that explicit setting required, say so, and it becomes part of R1.

I named no check under Confirmation. A test that connects to a server limited to TLS 1.1 and expects a handshake error would confirm R1.

The record needs no code change. A later change that adds an explicit `MinVersion` ends its commit message and pull request description with `Implements: ADR-0007 R1`.
