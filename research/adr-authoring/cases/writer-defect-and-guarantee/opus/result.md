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

token-gate checks the token of each request before policy evaluation. It ships as a container image, which
`build/token-gate/Dockerfile` builds, and as a Helm chart. The chart, under Kubernetes, is the only way to run
token-gate that the repository describes.

Under Docker, operators need token-gate to trust a private CA for its HTTPS calls to the identity provider. On the
platform, operators mount the certificate of such a CA under `/tmp/cert`, as they do for every image of the platform.
The image of token-gate builds on the platform base image `ghcr.io/example/platform-base`. The README of the base image
states that its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a `.crt`, `.cer`, or `.pem` file under
`/tmp/cert` to the trust store of the container, runs the scripts in `/app/init.d`, and then runs its arguments. The
platform's guide for service images says to keep that entrypoint and to set the service's binary as `CMD`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. The repository ships a Compose example, and a CI job starts it on every pull request and calls `GET /ready`.

### Terms

- **setting**: a value that an operator chooses for one installation of token-gate and that changes what token-gate
  does, such as the URL of an issuer, the port token-gate listens on, or the path of a key file.
- **without Kubernetes**: in a container that Docker starts, with no Kubernetes API server reachable from the container
  and no Kubernetes service account token in it.
- **Compose example**: the Compose file that R2 requires.

### Rules

#### Configuration

- **R1** (`server`). token-gate reads every setting from an environment variable or from a file in the file system of
  its container, and reads no setting from any other source, such as the Kubernetes API. Started without Kubernetes,
  token-gate starts and serves requests.

#### The Compose example

- **R2** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate without Kubernetes, from the image
  that `build/token-gate/Dockerfile` builds.

#### The CI job

- **R3** (`ci`). A workflow under `.github/workflows/` runs a job on every pull request. The job builds the token-gate
  image from the commit of the pull request, starts the Compose example with that image, and calls `GET /ready` on
  token-gate. The job fails when `GET /ready` does not return HTTP 200 within `<ready timeout>` after the Compose example
  starts.

### Implementation notes

Adds no requirement. Let the Compose file take the image reference from a variable, such as `TOKEN_GATE_IMAGE`, with the
released image as its default, so that the job of R3 can start it with the image it built. Where token-gate needs an
identity provider before it reports ready, the Compose example can start a stub issuer beside it. A commented-out volume
in the Compose file can show how to mount a CA certificate under `/tmp/cert`.

### Justification

The chart and the Compose example run the same image. Because token-gate takes no setting that only Kubernetes can
supply, an operator configures it the same way under both (R1, R2). A Compose example that nothing starts goes stale
without anyone noticing when a setting changes. The job catches that in the pull request that breaks it, and it tests
the image of that pull request, not the last release (R3).

### Alternatives considered

- **A1. Keep Kubernetes as the only supported platform, and leave each Docker user to write their own Compose file.**
  Each team would rebuild the same example, and nothing in the repository would show that token-gate still runs under
  Docker.
- **A2. Read settings through the Kubernetes API, such as by watching a ConfigMap with a Kubernetes client.** Rejected
  by R1: token-gate would then need a Kubernetes API server to start.
- **A3. Ship the Compose example without a job that starts it.** Rejected by R3: a broken example would reach operators
  before anyone noticed.

## Consequences

Positive:

- A setting documented for the chart works the same way under Docker, because both pass it as an environment variable
  or a file (R1).

Negative:

- Every pull request waits for the job of R3, including a pull request that changes only documentation, and fails when
  the Compose example does not report ready (R3).
- token-gate cannot gain a feature that needs the Kubernetes API, such as reloading a setting by watching a ConfigMap
  through the API (R1).

Follow-ups:

- Document how to run token-gate under Docker, including how to mount a private CA certificate under `/tmp/cert`.

## Open points

- **O1.** How long does the job of R3 wait for `GET /ready` to return HTTP 200 before it fails? `example-architect`
  decides. Affects R3.
- **O2.** R3 assumes that `/ready` returns HTTP 200 when token-gate is ready. The answers under consideration are HTTP
  200 only, or any 2xx status. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md`. Its status is `Proposed`, and two open points block acceptance: the timeout for `GET /ready` (O1) and which status counts as ready (O2). The reading guide already maps `docker` to `deploy/docker/` and `ci` to `.github/workflows/`, so it needs no change.

The record has no rule about the entrypoint, because the platform contract already answers that question from the notes. The base image's README and the platform's guide for service images both say to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-gate/Dockerfile` breaks that contract with no recorded reason, so this is a defect, not a decision. `build/token-admin/Dockerfile` already follows the contract. Here is the issue I'd open instead:

- **Type:** Bug
- **Title:** token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body:** The README of `ghcr.io/example/platform-base` says that its entrypoint, `/usr/bin/entrypoint.sh`, adds every `.crt`, `.cer`, and `.pem` certificate under `/tmp/cert` to the trust store, runs the scripts in `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and to set the service's binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so the base entrypoint never runs. A CA certificate mounted under `/tmp/cert` is therefore not trusted, and neither are the `/app/init.d` scripts run. The fix is to replace that line with `CMD ["/usr/local/bin/token-gate"]`, as `build/token-admin/Dockerfile` does. The chart runs the Pod with a read-only root file system. Because the entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, the chart needs an `emptyDir` volume at each of those paths. Check that the entrypoint rebuilds the full CA bundle in `/etc/ssl/certs`. An empty volume at that path hides the image's bundle, and the Pod would lose the public CAs.

If the `ENTRYPOINT` line is deliberate, tell me and I'll write it as a rule instead. In that case, trusting a CA under Docker needs a mechanism other than `/tmp/cert`.

Questions:
- Should anyone else approve this record, such as the maintainer of the CI workflows or of the chart? Right now only `example-architect` is listed.
- I tagged R1 `server` on the assumption that settings are loaded in `internal/server`. If another package loads them, which layer is it in?
- The notes don't give reasons, so the Justification and Alternatives considered are my own. Please have `example-architect` confirm them.

## Request 2

### File: docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md

````markdown
# Refuse tokens whose header names `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library and passes it every key that the JWKS of an issuer holds.

`jwx` refuses a token whose `alg` is `none` when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when
the key set holds a symmetric key. token-gate therefore accepts a token signed with HMAC from any issuer whose JWKS holds
a symmetric key. A symmetric key both signs and verifies, so anyone who holds that key can sign a token that token-gate
accepts.

## Decision

We will refuse every token whose header names `none` or an HMAC algorithm, with HTTP 401 and a separate reason code for
each case.

### Terms

- **header algorithm**: the value of the `alg` parameter in the JOSE header of the token, compared case-sensitively, as
  RFC 7515 requires.
- **HMAC algorithm**: `HS256`, `HS384`, or `HS512`.
- **refuse**: token-gate responds to the request with the HTTP status and the reason code that the rule names, and the
  request does not reach policy evaluation.

### Rules

#### Algorithms

- **R1** (`verify`, `server`). token-gate refuses a token whose header algorithm is `none` with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`.
- **R2** (`verify`, `server`). token-gate refuses a token whose header algorithm is an HMAC algorithm with HTTP 401 and
  the reason code `TOKEN_ALG_SYMMETRIC`. This holds whatever keys the JWKS of the token's issuer holds and whatever the
  settings of token-gate are.

#### Precedence

- **R3** (`verify`, `server`). Where R1 or R2 refuses a token that also fails another check of token-gate, such as an
  expired token or a signature that does not verify, the response carries the reason code of R1 or R2.

### Implementation notes

Adds no requirement. Check the header algorithm before signature verification. Leave the symmetric keys of a JWKS (`kty`
`oct`) out of the key set passed to `jwx`, so that a later change to the algorithm check cannot let an HMAC token
through. Before upgrading, operators of an issuer that signs with HMAC need to move that issuer to an asymmetric
algorithm.

### Justification

A symmetric key in a JWKS lets anyone who can read that JWKS, or who holds the issuer's secret, sign a token that
token-gate accepts. An asymmetric public key only verifies (R2). `jwx` already refuses `none`, and R1 adds a reason code
of its own. With separate reason codes, an operator can tell a forged token with `none` apart from an issuer that signs
with HMAC without reading the logs (R1, R2). Checking the algorithm first gives a refused token the same reason code
whatever else is wrong with it (R3).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer, configured in token-gate.** Rejected by R2: token-gate would hold a
  secret that can sign tokens for that issuer. Anyone who reads token-gate's settings could then sign tokens, and each
  secret would have to be distributed and rotated in step with its issuer.

## Consequences

Negative:

- After the upgrade, token-gate refuses the tokens of an issuer that signs with an HMAC algorithm, with HTTP 401 and
  `TOKEN_ALG_SYMMETRIC`, and no setting accepts them again (R2).
- A client that matches the reason code of another check, such as expiry, gets `TOKEN_ALG_NONE` or
  `TOKEN_ALG_SYMMETRIC` for a token that R1 or R2 refuses (R3).

Follow-ups:

- Tell the operators of issuers that sign with an HMAC algorithm before the release that brings R2.

## Open points

- **O1.** R3 assumes that the reason codes of R1 and R2 take precedence over every other check. The other answer is that
  the code of an earlier check, such as expiry, takes precedence. `example-security-architect` decides. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-refuse-tokens-signed-with-none-or-hmac.md`. Its status is `Proposed`, and one open point blocks acceptance. O1 covers which reason code a token gets when it also fails another check. I assumed the algorithm codes take precedence and wrote R3 that way.

R1 is a rule even though `jwx` already refuses `none`, because the HTTP status and the reason code `TOKEN_ALG_NONE` are a decision. R2 changes behavior: `internal/verify` passes `jwx` every key in a JWKS, so HMAC tokens are accepted today wherever an issuer publishes a symmetric key. I defined the header algorithm as case-sensitive, as RFC 7515 does. A value such as `None` falls outside this record and fails as an unknown algorithm under the existing checks.

Questions:
- Which record defines reason codes and where the response carries them? I'd add it under **Related ADRs** and point **Terms** at it.
- The notes give no reasons, so the Justification and the reasons in A1 are my own. Please have `example-security-architect` confirm them.
- Should anyone else approve this record, such as the owner of `internal/verify`?

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

token-gate opens TLS connections as a client, such as its HTTPS calls to identity providers for their JWKS. The key set
from those calls decides which tokens token-gate accepts. Since Go 1.18, the client of Go's `crypto/tls` refuses TLS 1.1
and older by default. token-gate sets no minimum version of its own, so its minimum comes from Go's default. Go's
defaults can be changed through the `GODEBUG` environment variable. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, whatever its
  destination and whichever package opens it, the dependencies of token-gate included.

### Rules

#### TLS version

- **R1** (`server`, `verify`, `image`, `chart`). The handshake of an outgoing TLS connection fails, and token-gate sends
  no data on the connection, where the server offers only TLS 1.1 or older. This holds for every value of the settings of
  token-gate and for every environment variable that the image or the chart sets.

### Implementation notes

Adds no requirement. Go's default meets R1 as long as nothing lowers it. A test can confirm R1: start an `httptest`
server whose TLS configuration has `MaxVersion: tls.VersionTLS11`, and expect the JWKS fetch to fail. That test also
catches a later Go version or a `godebug` setting that lowers the default. Setting `MinVersion: tls.VersionTLS12` on each
`tls.Config` that token-gate builds also meets R1.

### Justification

RFC 8996 deprecates TLS 1.0 and TLS 1.1. The JWKS that token-gate fetches decides which tokens it accepts, so a
connection with weaker protection would let an attacker on the path change the key set (R1). The rule covers every
package in the process and every environment variable that the image or the chart sets, because any of them can open a
connection or lower Go's default (R1).

### Alternatives considered

- **A1. Allow TLS 1.0 or 1.1, through a setting, for an identity provider that offers nothing newer.** Rejected by R1:
  the setting would bring back the weaker protection for exactly the connections that fetch the key set.

## Consequences

Negative:

- token-gate cannot fetch the JWKS of an identity provider that offers only TLS 1.1 or older, so it cannot verify that
  issuer's tokens, and no setting changes that (R1).
````

### Message to the user

I wrote the record as `docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections.md`. It has no open points, but its status stays `Proposed` until the team signs off. At that point, set it to `Accepted` and add the Date heading.

R1 is a rule even though Go already enforces the minimum, because the security architect chose it for this system. The rule describes the result, not the mechanism. Relying on Go's default meets it, and so does setting `MinVersion` explicitly. R1 also covers the environment that the image and the chart set, since `GODEBUG` can change Go's TLS defaults. No check exists yet, so the record has no **Confirmation** section. The test in **Implementation notes** would be the natural one to add.

Questions:
- The notes cover token-gate only, so `token-admin` is outside this record. Should it follow the same rule, in this record or in one of its own?
- I tagged R1 `server` and `verify` on the assumption that outgoing connections are opened only under `internal/server` and `internal/verify`. Is any other code opening them?
- A1 and the Justification are my own; the notes give no reasons. Please have `example-security-architect` confirm them.
