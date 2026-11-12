## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, configured by environment variables and mounted files alone

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image, built by
`build/token-gate/Dockerfile`, and as a Helm chart under `helm/`. Some operators run containers under Docker without
Kubernetes. They have no chart there, so they configure token-gate through what Docker gives a container: environment
variables and mounted files.

Under Docker, token-gate makes HTTPS calls to the identity provider. When the identity provider's certificate comes from
a private CA, the operator needs the container to trust that CA. On the platform, operators do this the same way for
every image: they mount the CA certificate under `/tmp/cert`. The platform base image `ghcr.io/example/platform-base`
supports this. Both images of this repository build on that base image. According to its README, its entrypoint
`/usr/bin/entrypoint.sh` adds every certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust
store of the container. It then runs the scripts in `/app/init.d`, and then runs its arguments. The platform's guide for
service images says to keep that entrypoint and to set the service's binary as `CMD`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. The repository will ship a Compose example of that setup, and CI will start it on every pull request.

### Terms

- **Compose example**: the Compose file under `deploy/docker/` that R1 requires.
- **setting**: a value that an operator chooses for an installation of token-gate and that changes how token-gate
  behaves, such as an issuer, a listen port, or a log level.

### Rules

#### The Compose example

- **R1** (`docker`). `deploy/docker/` holds a Compose file that starts token-gate from the image that
  `build/token-gate/Dockerfile` builds. The Compose file configures token-gate only through environment variables and
  mounted files, and it passes token-gate no command-line arguments.

#### Configuration of token-gate

- **R2** (`server`). Every setting of token-gate can be set through an environment variable or through a mounted file.
  No setting can be set only through a command-line argument.
- **R3** (`server`). token-gate starts and serves requests when no Kubernetes API server and no Kubernetes service
  account token are available to it.

#### The check in CI

- **R4** (`ci`). A job under `.github/workflows/` runs on every pull request, starts the Compose example, and calls
  `GET /ready` on token-gate. The job fails when token-gate does not answer `GET /ready` with HTTP 200 within
  `<readiness timeout>` of the start of the Compose example.

### Implementation notes

Adds no requirement. Let the Compose example read its environment variables from an `.env` file beside it, and mount
configuration files read-only. `docker compose up --wait` with a health check on `GET /ready` gives the CI job a single
command that waits and fails. If `GET /ready` depends on a reachable issuer, add a stub issuer that serves a JWKS through
a Compose override file that only the CI job uses. That way the Compose example stays the file operators copy.

### Justification

Under Docker, environment variables and mounted files are the only configuration interfaces a container has without
extra tooling, so every setting needs one of them (R1, R2). An installation without Kubernetes has no API server and no
service account, so token-gate must not need either to start (R3). An example that nothing starts stops working without
anyone noticing. Starting the example on every pull request keeps the support claim true (R1, R4).

### Alternatives considered

- **A1. Support token-gate only on Kubernetes, through the Helm chart under `helm/`.** Operators without Kubernetes
  would have to work out a configuration from the chart's templates, and no check would show that it works.

## Consequences

Positive:

- The CI job of R4 also fails a change that makes token-gate depend on Kubernetes at start (R3).

Negative:

- Every pull request pays for starting the Compose example in CI (R4).
- A new setting needs an environment variable or a file form, even where the chart could pass it as an argument (R2).

Follow-ups:

- Describe in the repository's README how to run token-gate under Docker, and link the Compose example.

## Open points

- **O1.** How long the CI job of R4 waits for token-gate to answer `GET /ready` with HTTP 200, which R4 names as
  `<readiness timeout>`. `example-architect` decides. Affects R4.
- **O2.** R4 assumes that token-gate answers `GET /ready` with HTTP 200 once it is ready. The other answer under
  consideration is any 2xx status. `example-architect` decides. Affects R4.
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. O1 (the readiness timeout in the CI job) and O2 (whether `/ready` returns HTTP 200 or any 2xx status) block acceptance. Once `example-architect` answers both and signs off, set `Accepted` and add the Date heading.

The question from the meeting, whether to keep the binary as the entrypoint, isn't in the record. It's a defect, not a decision. The base image's README and the platform's guide for service images both say a service image keeps `/usr/bin/entrypoint.sh` and sets its binary as `CMD`. `build/token-admin/Dockerfile` does this. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]` instead, and no record or issue explains why. Because of that line, certificates under `/tmp/cert` are never added to the trust store. I suggest opening this issue:

- **Type**: Bug
- **Title**: token-gate image replaces the platform entrypoint, so certificates under `/tmp/cert` are not trusted
- **Body**: The README of `ghcr.io/example/platform-base` and the platform's guide for service images require service images to keep `/usr/bin/entrypoint.sh` and set the binary as `CMD`. `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so the base entrypoint never runs: a CA certificate mounted under `/tmp/cert` is not trusted, and the scripts in `/app/init.d` do not run. Fix: replace that line with `CMD ["/usr/local/bin/token-gate"]`, as `build/token-admin/Dockerfile` does. The chart runs the Pod with a read-only root file system, and the entrypoint writes to `/etc/ssl/certs` and `/usr/local/share/ca-certificates`. The same change therefore adds an `emptyDir` volume at each of those two paths in the chart under `helm/`.

Operators can only trust a private CA under Docker once this issue is fixed. If the `ENTRYPOINT` line is deliberate, tell me why and I'll add a rule for it.

I couldn't read the code, so I tagged R2 and R3 with `server`. If configuration loading or `main` lives outside `internal/server`, for example in `cmd/token-gate`, which path should the reading guide map, and to which layer? A1 is the status quo before the meeting; the notes didn't list any alternatives. Should I keep it?

## Request 2

### File: docs/adr/0007-refuse-tokens-that-name-none-or-an-hmac-algorithm.md

````markdown
# Refuse tokens whose header names the algorithm `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies the token's signature
with the `jwx` library. When `jwx` verifies a signature, it refuses a token whose `alg` is `none`. It accepts `HS256`,
`HS384`, and `HS512` when the key set holds a symmetric key. `internal/verify` passes `jwx` every key that the JWKS of
an issuer holds, so a symmetric key in an issuer's JWKS makes `jwx` accept HMAC tokens signed with that key.

An issuer serves its JWKS to every client that fetches it. Anyone who can read a symmetric key in a JWKS can sign tokens
that verify against it.

## Decision

We will refuse every token whose header names the algorithm `none`, `HS256`, `HS384`, or `HS512`, with HTTP 401 and a
reason code for each of the two cases.

### Terms

- **token**: the token that token-gate checks for a request before policy evaluation.
- **header algorithm**: the value of the `alg` parameter in the token's JOSE header, compared as a case-sensitive
  string, as RFC 7515, section 4.1.1, compares it.

### Rules

#### Unsigned tokens

- **R1** (`verify`, `server`). When the header algorithm of a token is `none`, token-gate refuses the request with HTTP
  401 and the reason code `TOKEN_ALG_NONE`. This reason code takes precedence over every other reason code that the
  token would also get.

#### Symmetric algorithms

- **R2** (`verify`, `server`). When the header algorithm of a token is `HS256`, `HS384`, or `HS512`, token-gate refuses
  the request with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`, whatever keys the JWKS of the issuer holds. This
  reason code takes precedence over every other reason code that the token would also get. No setting turns this
  refusal off.

### Implementation notes

Adds no requirement. Read the header algorithm from the protected header before calling `jwx`. Return a distinct error
for each rule, and let `internal/server` map each error to its status and reason code. As a second layer of defense,
drop keys whose `kty` is `oct` from the key set that `internal/verify` passes to `jwx`.

Cover both rules with a table test in `internal/verify`. Its cases are a token with `alg` set to `none`, and a token for
each of `HS256`, `HS384`, and `HS512` signed with a symmetric key that the test's JWKS holds. Add a test in
`internal/server` that checks the status and the reason code for each case.

### Justification

`jwx` refuses `none` already, but only as a failed verification. A reason code of its own lets an operator tell these
tokens apart from tokens whose signature does not match a key (R1). An HMAC key that an issuer publishes in its JWKS can
be read by anyone, so a token signed with it shows nothing about who issued it (R2). Each refusal takes precedence over
other reasons, so the reason code does not depend on the order in which the checks run (R1, R2).

### Alternatives considered

- **A1. Accept `HS256`, `HS384`, and `HS512` with a shared secret per issuer.** Rejected by R2: every holder of the
  shared secret, token-gate included, could sign tokens that the issuer never issued.

## Consequences

Negative:

- Once R2 ships, token-gate refuses every token from an issuer that signs with `HS256`, `HS384`, or `HS512` against a
  symmetric key in its JWKS, with `TOKEN_ALG_SYMMETRIC`. Before R2, `jwx` accepted those tokens.

Follow-ups:

- Announce R2 in the release notes as a breaking change for issuers that sign with HMAC.
- Before the release, check with the operators of each configured issuer whether its JWKS holds a symmetric key.

## Open points

- **O1.** The term **header algorithm** compares `alg` case-sensitively, so a token whose `alg` is `None` or `hs256`
  falls under neither R1 nor R2. Whichever check rejects an unknown algorithm refuses that token instead. The other
  answer under consideration compares case-insensitively, so those tokens get `TOKEN_ALG_NONE` or
  `TOKEN_ALG_SYMMETRIC`. `example-security-architect` decides. Affects R1 and R2.
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. O1 blocks acceptance: should `alg` be compared case-sensitively, as RFC 7515 does, or case-insensitively? Once `example-security-architect` answers and signs off, set `Accepted` and add the Date heading.

Both refusals are rules, even though `jwx` already refuses `none`. The security architect chose them, and the 401 status and the reason codes are new behavior. Context describes how `jwx` behaves and what `internal/verify` passes to it.

Questions:

- Does one of ADR-0001 to ADR-0006 define reason codes and where they appear in a response? If so, I'll add a **reason code** term that points to that record and a line under **Related ADRs**.
- I tagged both rules with `verify` and `server` without reading the code. Is the mapping from a verification error to a reason code in `internal/server`?
- The precedence sentence in R1 and R2 means a token with `alg: none` that's also expired gets `TOKEN_ALG_NONE`. Does that match what the security architect wants?
- The notes didn't say why A1 was rejected. The reason in A1 is a technical fact I added. Please confirm it.

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

token-gate opens TLS connections as a client, for example when it fetches the JWKS of an issuer over HTTPS. It uses
Go's `crypto/tls` and sets no minimum TLS version of its own. Since Go 1.18, a `crypto/tls` client whose
`Config.MinVersion` is zero uses TLS 1.2 as its minimum and refuses TLS 1.1 and older (the Go 1.18 release notes, and
the documentation of `tls.Config.MinVersion`). A `tls.Config` that sets `MinVersion` to a lower version, in token-gate's
code or in a library it uses, lowers that minimum for its connections. RFC 8996 deprecates TLS 1.0 and TLS 1.1.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection in which the token-gate process is the client, whether token-gate's own
  code opens it or a library opens it for token-gate.

### Rules

#### Protocol version

- **R1** (`verify`, `server`). token-gate completes the handshake of an outgoing TLS connection only at TLS 1.2 or
  later. When the server offers no version from TLS 1.2 up, the handshake fails, and token-gate sends no application
  data on that connection.

### Implementation notes

Adds no requirement. A `tls.Config` whose `MinVersion` is zero meets R1 on Go 1.18 and later, so existing code needs no
change. Where code or a library takes its own `tls.Config`, leave `MinVersion` unset or set it to `tls.VersionTLS12`.
Setting `tls.VersionTLS12` explicitly in a shared HTTP client constructor records the rule in the code. It also keeps
the minimum in place if a later Go release changes the default.

A test can start an `httptest` TLS server whose `MaxVersion` is `tls.VersionTLS11`, point the JWKS client at it, and
expect a handshake error.

### Justification

TLS 1.0 and TLS 1.1 are deprecated (RFC 8996). Go's default already meets the decision. A rule still makes a change that
lowers `MinVersion`, or adds a library that does, fail a check (R1).

### Alternatives considered

- **A1. Allow TLS 1.0 or TLS 1.1 through a setting, for a server that offers nothing newer.** Rejected by R1: the rule
  admits no setting that lowers the minimum below TLS 1.2.

## Consequences

Negative:

- token-gate cannot reach a server that offers only TLS 1.1 or older, such as an old identity provider or a proxy that
  terminates TLS (R1).
````

### Message to the user

I wrote the record as ADR-0007 with the status `Proposed`. It has no open points, so it can become `Accepted` once `example-security-architect` signs off; add the Date heading then.

R1 is a rule even though Go's default already meets it. The security architect made the decision, and the rule makes a future `MinVersion` below TLS 1.2 fail a check instead of passing unnoticed. Context states what Go guarantees and where it says so.

Questions:

- R1 depends on Go 1.18 or later for clients. Does `go.mod` require at least that version? If no layer in the reading guide covers `go.mod`, should it be mapped to one?
- I tagged R1 with `verify` and `server` without reading the code. Does any other code open outgoing TLS connections, for example an exporter or a client for policy evaluation? If so, which layer holds it?
- The record covers only the token-gate process. Should the decision also cover `token-admin`?
- The notes didn't list any alternatives. I added A1 as the obvious option the decision rules out. Keep it or remove it?
