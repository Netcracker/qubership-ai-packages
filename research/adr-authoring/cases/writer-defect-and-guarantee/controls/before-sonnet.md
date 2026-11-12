## Request 1

### File: docs/adr/0007-support-token-gate-under-docker-without-kubernetes.md

````markdown
# Support token-gate under Docker without Kubernetes, with private CAs trusted through `/tmp/cert`

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R5 and settles O1 and O2.

## Context

token-gate checks the token of each request before policy evaluation. It ships as a container image and a Helm chart.
Operators who run it under Docker without Kubernetes need to trust a private CA for the HTTPS calls to the identity
provider. They mount the CA certificate under `/tmp/cert`, as for every image of the platform.

- Both images of the repository, built by `build/token-gate/Dockerfile` and `build/token-admin/Dockerfile`, build on
  the platform base image `ghcr.io/example/platform-base`, pinned by digest.
- The README of the base image states that its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in a
  `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container, runs the scripts in
  `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and
  to set the service's binary as `CMD`.
- `build/token-admin/Dockerfile` ends with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` ends with
  `ENTRYPOINT ["/usr/local/bin/token-gate"]`, which replaces the base entrypoint, so the base entrypoint does not run
  for token-gate and `/tmp/cert` has no effect on it. The line has been there since the first commit of the file, with
  no comment, and no record or issue explains it.
- The chart runs the Pod of token-gate with a read-only root file system. The base entrypoint writes to
  `/etc/ssl/certs` and `/usr/local/share/ca-certificates`.

## Decision

We will support token-gate under Docker without Kubernetes, configured by environment variables and mounted files
alone. The repository ships a Compose example under `deploy/docker/` that a CI job starts on every pull request, and a
private CA certificate mounted under `/tmp/cert` is trusted by token-gate.

### Terms

- **Compose example**: the Docker Compose project under `deploy/docker/` that starts token-gate.
- **certificate file**: a file under `/tmp/cert` with the extension `.crt`, `.cer`, or `.pem`, as the README of the
  platform base image states.
- **base entrypoint**: `/usr/bin/entrypoint.sh` of the image `ghcr.io/example/platform-base`.

### Rules

#### Running without Kubernetes

- **R1** (`server`). token-gate starts and serves requests when no Kubernetes API is reachable and its configuration
  comes from environment variables and mounted files alone.
- **R2** (`docker`). `deploy/docker/` holds a Compose example that starts token-gate and sets its configuration through
  environment variables and mounted files alone.
- **R3** (`ci`). A workflow under `.github/workflows/` starts the Compose example on every pull request, calls
  `GET /ready` on the started token-gate, and fails the pull request check unless the response is `<ready response>`.

#### Private CAs

- **R4** (`image`). The token-gate container adds the certificate in every certificate file to its trust store before
  the token-gate process starts.
- **R5** (`chart`). Where `build/token-gate/Dockerfile` sets no `ENTRYPOINT`, the chart gives the Pod of token-gate an
  `emptyDir` volume mounted at `/etc/ssl/certs` and another at `/usr/local/share/ca-certificates`.

### Implementation notes

Adds no requirement. If O1 is settled for the base entrypoint, remove the `ENTRYPOINT` line from
`build/token-gate/Dockerfile` and end the file with `CMD ["/usr/local/bin/token-gate"]`. A Compose `command` or a chart
`args` list replaces `CMD` as a whole, so each one that passes flags to token-gate today must start with the binary.
A test for R4 can mount a test CA certificate under `/tmp/cert` in the Compose example and call an HTTPS endpoint that
this CA signed.

### Justification

The Compose example and the CI job give operators without Kubernetes a setup that stays working (R1, R2, R3). The
base entrypoint is the mechanism that the platform documents for `/tmp/cert`, and operators already use it on every
other image of the platform (R4). The entrypoint writes to two directories, and the root file system of the Pod is
read-only, so those directories need writable volumes (R5).

### Alternatives considered

- **A1. Keep the binary as the `ENTRYPOINT` of the token-gate image.** Not decided, see O1. With this option the base
  entrypoint does not run, and the notes of the architecture meeting name no other way to meet R4.

## Consequences

Positive:

- Every pull request shows whether token-gate starts under Docker from environment variables and mounted files (R3).

Negative:

- Each pull request runs the Compose example (R3).
- Where the image uses the base entrypoint, each start of token-gate first runs the base entrypoint and the scripts in
  `/app/init.d` (R4).

## Open points

- **O1.** Which entrypoint does the token-gate image use? Answer (a): the base entrypoint, with the binary as `CMD`, as
  the platform guide says and `build/token-admin/Dockerfile` does. Answer (b): the binary as `ENTRYPOINT`, as
  `build/token-gate/Dockerfile` does, in which case R4 has no mechanism and R5 does not apply. `example-architect`
  decides, after finding out why the `ENTRYPOINT` line was set. It affects R4 and R5.
- **O2.** Which response of `GET /ready` counts as ready? `example-architect` decides. It affects R3.
````

### Message to the user

I wrote the record as `Proposed`, with two open points that block acceptance.

- **O1 (entrypoint):** I did not decide it. I would recommend answer (a), the base entrypoint with the binary as `CMD`, because it follows the platform guide and matches `token-admin`. Does anyone know why `build/token-gate/Dockerfile` has had `ENTRYPOINT` since its first commit? The answer should come before the change.
- **O2 (ready response):** The notes do not say what `GET /ready` returns when the service is ready, so R3 holds the placeholder `<ready response>`. What is the value?

Other points to check:
- The notes name no owner. I put `example-architect` as Owner and as the approver. Please confirm or give another account.
- I did not add a Date heading, because the record is not accepted yet.
- I tagged R1 with `server` without seeing where the service reads its configuration. Correct the tag if that code sits elsewhere.
- No check exists yet, so the record has no **Confirmation** section. The Implementation notes suggest a test for R4.
- The reading guide needs no change, because its layers already cover `image`, `chart`, `docker`, and `ci`.

## Request 2

### File: docs/adr/0007-refuse-tokens-with-the-none-or-an-hmac-algorithm.md

````markdown
# Refuse tokens whose header names the algorithm `none` or an HMAC algorithm

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 to R3 and settles O1 and O2.

## Context

token-gate checks the token of each request before policy evaluation. `internal/verify` verifies signatures with the
`jwx` library and passes it every key that the JWKS of an issuer holds.

- `jwx` refuses a token whose `alg` is `none` when it verifies a signature.
- `jwx` accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key. Because `internal/verify` passes
  every key of the JWKS, whether a token with one of these algorithms is accepted depends on what the JWKS of its
  issuer holds.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and a
token whose header names `HS256`, `HS384`, or `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`. We will
not accept HMAC with a shared secret per issuer.

### Terms

- **none token**: a token whose JOSE header member `alg` has the value `none`. The comparison is case-sensitive, as
  RFC 7515 defines `alg` values.
- **symmetric token**: a token whose JOSE header member `alg` has the value `HS256`, `HS384`, or `HS512`. The
  comparison is case-sensitive.

### Rules

#### Refused algorithms

- **R1** (`verify`, `server`). When the token of a request is a none token, the service responds with HTTP 401 and the
  reason code `TOKEN_ALG_NONE`, whatever the key set of its issuer holds.
- **R2** (`verify`, `server`). When the token of a request is a symmetric token, the service responds with HTTP 401 and
  the reason code `TOKEN_ALG_SYMMETRIC`, including where the key set of its issuer holds a symmetric key.

#### Precedence

- **R3** (`verify`, `server`). When the token of a request is a none token or a symmetric token and also fails another
  check of the service, the service responds as R1 or R2 requires for that token.

### Implementation notes

Adds no requirement. Read the `alg` value from the token header before the call into `jwx`, so that the response
carries the reason code of R1 or R2 and not the error of `jwx`. A table-driven test can cover `none`, `HS256`, `HS384`,
and `HS512`, each with a JWKS that holds a symmetric key and with one that does not. A token whose `alg` is `None` or
`HS256 ` is neither a none token nor a symmetric token, so these rules do not cover it.

### Justification

`jwx` already refuses `none` when it verifies a signature, so R1 fixes the reason code of an existing refusal and does
not change the outcome. R2 changes the outcome: without it, a symmetric key in the JWKS of an issuer makes token-gate
accept tokens with an HS algorithm, because `internal/verify` passes every key of the JWKS to `jwx`. The notes of the
security review give no further reason (O1).

### Alternatives considered

- **A1. Accept HMAC with a shared secret per issuer.** Rejected by R2. The review considered it and rejected it, and
  its reason is not recorded yet (O1).

## Consequences

Positive:

- Whether a token with an HS algorithm is accepted no longer depends on the keys in the JWKS of its issuer (R2).

Negative:

- A caller whose issuer signs with `HS256`, `HS384`, or `HS512` and whose JWKS holds a symmetric key is accepted before
  this change and gets HTTP 401 with `TOKEN_ALG_SYMMETRIC` after it (R2).
- A none token is refused before and after this change, and the reason code is `TOKEN_ALG_NONE` after it (R1).

Follow-ups:

- Tell the operators of any issuer that signs with HMAC that its tokens will get HTTP 401 (R2).

## Open points

- **O1.** Why did the review reject HMAC with a shared secret per issuer? `example-security-architect` supplies the
  reason for Justification and A1.
- **O2.** The notes do not say which reason code wins where a none token or a symmetric token fails another check as
  well, such as a failed expiry check. R3 assumes that the algorithm refusal wins. `example-security-architect`
  confirms or names another order. It affects R3.
````

### Message to the user

I wrote the record as `Proposed`. Two open points block acceptance: O1 and O2.

- **O1 (reason for rejecting HMAC):** The notes say HMAC with a shared secret per issuer was rejected but give no reason. I did not invent one, and A1 says the reason is missing. What was the reason?
- **O2 (precedence):** R3 assumes that the algorithm refusal wins over any other failure of the same token. Please confirm.

Other points to check:
- The notes name no owner. I put `example-security-architect` as Owner and approver. Please confirm.
- I did not add a Date heading, because the record is not accepted yet.
- I compared `alg` values case-sensitively, as RFC 7515 defines them. A token with `None` is therefore outside R1 and keeps the behavior it has today. Say so if you want case variants refused as well.
- I did not see how the service reports a reason code in a response, so the rules only name the code.
- I tagged the rules `verify` and `server`: `verify` produces the reason, and I assumed `server` produces the HTTP status.
- No check exists yet, so the record has no **Confirmation** section.
- The decision changes the outcome for HS tokens only. `jwx` already refuses `none`, so R1 changes only the reason code.

## Request 3

### File: docs/adr/0007-use-tls-1-2-or-later-for-outgoing-connections-of-token-gate.md

````markdown
# Use TLS 1.2 or later for every outgoing TLS connection of token-gate

## Status

Proposed

### Owner

`example-security-architect`

### Participants and approvers

- Security architect, `example-security-architect`: approves R1 and R2.

## Context

token-gate calls other hosts over HTTPS, such as the identity provider of an issuer. Go's `crypto/tls` client refuses
TLS 1.1 and older by default, and token-gate sets no minimum version of its own.

## Decision

We will use TLS 1.2 or later for every outgoing TLS connection of token-gate.

### Terms

- **outgoing TLS connection**: a TLS connection that the token-gate process opens as the client, through its own code or
  through a library that it calls.

### Rules

#### Minimum version

- **R1** (`verify`, `server`). An outgoing TLS connection completes its handshake only at TLS 1.2 or later, and fails
  where the peer offers only TLS 1.1 or older.
- **R2** (`verify`, `server`). No `tls.Config` in the Go code of token-gate sets `MinVersion` to a value below
  `tls.VersionTLS12`.

### Implementation notes

Adds no requirement. The default of Go's `crypto/tls` client already meets R1, so the code needs no change. A test for
R1 can start an `httptest` TLS server with `MaxVersion` set to `tls.VersionTLS11` and check that the client call fails.

### Justification

The default of the Go client already refuses TLS 1.1 and older, so the decision makes that behavior a requirement and
asks for no code change (R1). R2 keeps a later change from lowering the minimum in code that token-gate owns.

### Alternatives considered

- The notes of the security review record no alternative.

## Consequences

Negative:

- An identity provider that offers only TLS 1.1 or older cannot be reached, and the call to it fails (R1).
- R1 rests on the default of the Go client. A change to that default would change what meets R1, and a test for R1
  shows it.
````

### Message to the user

I wrote the record as `Proposed` with no open points. It can become `Accepted` once the team signs off, and the Date heading is added then.

- The notes name no owner. I put `example-security-architect` as Owner and approver. Please confirm.
- Which Go packages open outgoing connections? I tagged both rules `verify` and `server`, because the reading guide maps only those two Go paths. If other Go code, such as a `cmd/` package, opens TLS connections, R2 constrains paths that belong to no layer, and the guide needs one more layer.
- The rules cover outgoing connections only. The notes say nothing about TLS on connections that token-gate accepts.
- The notes record no alternative, and the record says so under Alternatives. For example, if the review also considered setting `MinVersion` explicitly to `tls.VersionTLS12`, tell me and I will add it.
- I added no rule about the Go version, because the notes treat the default as given. No check exists yet, so the record has no **Confirmation** section. The Implementation notes suggest a test for R1.
