## Request 1

### File: docs/adr/0007-support-token-gate-under-docker.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate ships as a container image, built by `build/token-gate/Dockerfile`, and as a Helm chart under `helm/`.
Operators want to run token-gate under Docker without Kubernetes. Under Docker, a container gets environment variables
and mounted files. It gets no Kubernetes API, no service account token, and no downward API.

Under Docker, operators need to trust a private CA for the HTTPS calls that token-gate makes to the identity provider.
Both images of the repository build on the platform base image `ghcr.io/example/platform-base`, pinned by digest. The
README of the base image states its contract. Its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a
`.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container. It then runs the scripts in
`/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and
to set the service's binary as `CMD`. An operator of a platform image trusts a private CA by mounting its certificate
under `/tmp/cert`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone, and we will keep a Compose example that CI starts on every pull request.

### Terms

- **Kubernetes-provided input**: the Kubernetes API, and every file that Kubernetes writes into a container without a
  volume the operator declares, such as a service account token or a downward API file. A ConfigMap or a Secret that
  the chart mounts as a file is a mounted file, not a Kubernetes-provided input.
- **ready**: token-gate is ready when `GET /ready` returns HTTP 200.
- **Compose example**: the Compose file that R3 requires.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads its settings only from environment variables and from files in the file system
  of its container. A setting that neither source gives keeps the default in the code.
- **R2** (`server`). token-gate starts and becomes ready in a container where no Kubernetes-provided input exists.

#### The Compose example and its check

- **R3** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from the image that
  `build/token-gate/Dockerfile` builds.
- **R4** (`ci`). A workflow under `.github/workflows/` runs on every pull request. It builds the image of
  `build/token-gate/Dockerfile` from the commit under review, starts the Compose example with that image, and calls
  `GET /ready` on token-gate. The job fails where token-gate is not ready within `<ready timeout>`.

### Implementation notes

Adds no requirement. Add a commented volume at `/tmp/cert` to the Compose example, so that an operator sees where the
certificate of a private CA goes. Where token-gate reads a setting from a file, take the path of that file from an
environment variable, so that the chart and the Compose example can mount the file at different paths.

### Justification

Docker gives a container environment variables and mounted files and no Kubernetes-provided input. token-gate therefore
runs under Docker only where it needs nothing else (R1, R2). A Compose example that nothing runs can stop working
unnoticed. A job that starts it on every pull request fails the pull request that breaks it (R3, R4).

### Alternatives considered

The meeting notes record no alternative.

## Consequences

Negative:

- No setting can come from the Kubernetes API at runtime. The chart passes every setting as an environment variable or
  a mounted file (R1, R2).
- Every pull request pays for an image build and a container start in CI (R4).

Follow-ups:

- Restore the platform entrypoint in the token-gate image under its own Bug issue.

## Open points

- **O1.** The value of `<ready timeout>` in R4. `example-architect` decides it.
- **O2.** R4 assumes that the job tests the image built from the commit under review. The other answer is the latest
  published image. `example-architect` decides. The answer affects R4.
````

### Message to the user

I wrote the record as `docs/adr/0007-support-token-gate-under-docker.md` with the status `Proposed`. Two open points block acceptance: O1, the value of `<ready timeout>`, and O2, which image the CI job starts.

The meeting asked whether token-gate should keep its binary as the entrypoint or switch to the base entrypoint with the binary as `CMD`. The record doesn't treat that as a decision. The README of the base image and the platform's guide for service images already settle it: keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-gate/Dockerfile` breaks that contract with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, and no record or issue gives a reason for it. That makes it a defect, so the record has no rule about it. I propose this issue:

- **Type:** Bug
- **Title:** token-gate image replaces the platform base entrypoint, so certificates under `/tmp/cert` are ignored
- **Contract:** The README of `ghcr.io/example/platform-base` says `/usr/bin/entrypoint.sh` adds the certificates under `/tmp/cert` to the trust store, runs `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and to set the binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, while `build/token-admin/Dockerfile` follows the contract with `CMD ["token-admin"]`.
- **Fix:** Replace the `ENTRYPOINT` line with `CMD ["/usr/local/bin/token-gate"]`. The chart runs the Pod with a read-only root file system, and the base entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. So in the same change, add `emptyDir` volumes at those two paths to the chart.

Until that fix lands, a certificate mounted under `/tmp/cert` has no effect on token-gate under Docker or under Kubernetes.

Questions:

1. What value should `<ready timeout>` have (O1)?
2. Should the CI job start the image built from the pull request, as R4 assumes, or a published image (O2)?
3. The notes name no alternatives. Were any discussed that the record should list?
4. Besides `example-architect`, who approves this record? For example, a maintainer of the CI workflows for R4.
5. Should I open the Bug issue as proposed?

## Request 2

### File: docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md

````markdown
# Refuse request tokens whose algorithm is `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library and passes it every key that the JWKS of an issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. No record states which status or reason code
token-gate returns for that token.

`jwx` accepts a token signed with `HS256`, `HS384`, or `HS512` when the key set holds a symmetric key. token-gate
therefore accepts such a token today, where the JWKS of its issuer holds a symmetric key.

## Decision

We will refuse a request token whose algorithm is `none` with `TOKEN_ALG_NONE`, and a request token signed with an
HMAC algorithm with `TOKEN_ALG_SYMMETRIC`, both with HTTP 401.

### Terms

- **request token**: the token that token-gate checks on a request before policy evaluation.
- **`alg`**: the `alg` parameter of the JOSE header of the request token.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). token-gate refuses a request token whose `alg` is `none`, in any letter case, with HTTP
  401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a request token whose `alg` is `HS256`, `HS384`, or `HS512`, in any
  letter case, with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of its issuer holds.
- **R3** (`verify`, `server`). Where R1 or R2 refuses a request token and another check of that request token also
  fails, token-gate responds with the reason code of R1 or R2.

#### Upgrade

- **R4** (`verify`, `server`). No setting, environment variable, or mounted file makes token-gate accept a request
  token that R1 or R2 refuses. An existing installation refuses those request tokens from its first start after the
  upgrade.

### Implementation notes

Adds no requirement. In `internal/verify`, read `alg` from the protected header and compare it before any key lookup,
so that the refusal doesn't depend on the keys of the issuer. Also pass `jwx` no key of type `oct` from a JWKS.
Existing tests that sign tokens with an HMAC key need an asymmetric key instead.

### Justification

A request token whose `alg` is `none` carries no signature, so any party can produce one (R1). A token signed with an
HMAC key can be produced by every party that holds the key, verifiers included. An asymmetric signature can be produced
only by the holder of the private key, so token-gate accepts only tokens that the issuer signed (R2). One reason code
per refused algorithm family lets an operator tell from the response which family the client used, and no other
failed check hides it (R1, R2, R3). With no setting to turn the refusals off, every installation gets them (R4).

### Alternatives considered

- **A1. Accept `HS256`, `HS384`, and `HS512` with a shared secret per issuer.** Rejected by R2: every holder of the
  shared secret, token-gate included, could mint request tokens for that issuer.

## Consequences

Negative:

- A client whose issuer signs with `HS256`, `HS384`, or `HS512`, and whose JWKS holds the symmetric key, gets HTTP 401
  with `TOKEN_ALG_SYMMETRIC` after the upgrade, where it got through before (R2, R4). No test shows this case yet.

## Open points

- **O1.** Where the reason code goes in the HTTP 401 response. The record assumes it goes where token-gate puts the
  reason codes of its other refusals. Where no such place exists, the answers are a field of a JSON body or a response
  header. `example-security-architect` decides. Affects R1 and R2.
- **O2.** R3 assumes that the reason codes of R1 and R2 win over the reason code of any other failed check. The other
  answer is that an earlier check, such as a malformed token, keeps its own reason code.
  `example-security-architect` decides. Affects R3.
- **O3.** R1 and R2 assume that `alg` matches in any letter case, so `None` and `hs256` are refused too. The other
  answer is an exact match, as RFC 7515 compares `alg` values. Under it, those values are unknown algorithms, and no
  rule of this record refuses them. `example-security-architect` decides. Affects R1 and R2.
````

### Message to the user

I wrote the record as `docs/adr/0007-refuse-tokens-with-alg-none-or-hmac.md` with the status `Proposed`. Three open points block acceptance:

1. **O1:** Where in the 401 response does the reason code go?
2. **O2:** When another check also fails, do `TOKEN_ALG_NONE` and `TOKEN_ALG_SYMMETRIC` win over its reason code, as R3 assumes?
3. **O3:** Should `alg` match in any letter case, as R1 and R2 assume, or exactly?

`jwx` already refuses `alg: none`, but R1 is still a rule, because the status and the reason code are this service's choice. R2 isn't met today: `internal/verify` passes every JWKS key to `jwx`, so an issuer with a symmetric key in its JWKS gets HMAC tokens accepted.

The notes don't say why per-issuer HMAC was rejected. I based the Justification and A1 on the standard reason: every holder of a shared secret can mint tokens. Could `example-security-architect` confirm that this was the review's reason? Also, who besides them approves this record?

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

token-gate opens TLS connections as a client, such as the HTTPS calls to the identity provider. Go's `crypto/tls`
client refuses TLS 1.1 and older by default. token-gate sets no minimum TLS version of its own, so it uses that default.
Go chooses the default, and Go has changed it before: the client default rose to TLS 1.2 in Go 1.18. RFC 8996
deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, to any host. A
  connection that token-gate accepts as a server, and a connection of `token-admin`, is not an outgoing TLS connection.

### Rules

#### Minimum version

- **R1** (`verify`, `server`). The handshake of an outgoing TLS connection fails where the server supports no TLS
  version from 1.2 on, and token-gate sends no request over that connection. This holds for every value of the
  settings of token-gate.

### Implementation notes

Adds no requirement. The code meets R1 today through Go's default. Setting `MinVersion: tls.VersionTLS12` on every
`tls.Config` that token-gate builds for a client keeps R1 met, whatever default a later Go release chooses. A test can
start an `httptest` TLS server with `MaxVersion: tls.VersionTLS11` and check that the call to it fails.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1. A connection on either version doesn't protect the calls token-gate makes to
the identity provider to the level the service requires (R1). R1 applies for every value of the settings, so a later
setting can't lower the minimum version (R1).

### Alternatives considered

The review notes record no alternative.

## Consequences

Negative:

- token-gate can't reach a server that supports only TLS 1.1 or older, such as an identity provider behind an old
  proxy (R1).
````

### Message to the user

I wrote the record as `docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md` with the status `Proposed`. It has no open points. Once the team signs off, it can move to `Accepted` with the date of acceptance.

Go's default already meets the decision, but I still wrote it as rule R1, because the security architect chose it for this service. That way, an explicit lower `MinVersion` or a new setting for the minimum version would break a recorded rule. Today, nothing would stop such a change.

Questions:

1. I limited the term **outgoing TLS connection** to the token-gate process, as the notes say. Should `token-admin` be covered as well?
2. The notes give no reason and no alternatives. I based the Justification on RFC 8996. Does that match the review's reasoning, and were any alternatives discussed, such as requiring TLS 1.3?
3. Who besides `example-security-architect` approves this record?
