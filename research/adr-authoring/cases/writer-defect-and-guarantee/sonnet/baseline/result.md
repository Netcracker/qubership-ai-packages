## Request 1

### File: docs/adr/0007-support-docker-without-kubernetes.md

````markdown
# 0007. Support token-gate under Docker without Kubernetes

- Status: Proposed. The entrypoint question under "Open question" is not decided.
- Date: 2026-11-11
- Deciders: @example-architect
- Layers: `image`, `chart`, `docker`, `ci`

## Context

token-gate ships as a container image and a Helm chart. Operators now also want to run the image under Docker without
Kubernetes.

Under Docker, operators need to trust a private CA for the HTTPS calls from token-gate to the identity provider. Every
image of the platform handles this the same way. The entrypoint of the base image, `/usr/bin/entrypoint.sh`, adds every
certificate in a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container, runs the scripts
in `/app/init.d`, and then runs its arguments.

The token-gate image sets `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so the base entrypoint does not run and a
certificate mounted under `/tmp/cert` is not added to the trust store. The `token-admin` image keeps the base entrypoint
and ends with `CMD ["token-admin"]`, which is what the platform guide for service images prescribes. The `ENTRYPOINT`
line of token-gate has been there since its first commit, and no record or issue gives a reason for it.

The chart runs the Pod of token-gate with a read-only root file system. The base entrypoint writes to
`/etc/ssl/certs` and `/usr/local/share/ca-certificates`.

## Decision

1. token-gate is supported under Docker without Kubernetes. Operators configure it with environment variables and
   mounted files alone.
2. The repository ships a Compose example under `deploy/docker/`.
3. A CI job starts the Compose example on every pull request and calls `GET /ready`.
4. Operators trust a private CA by mounting its certificate under `/tmp/cert`, as for every image of the platform.
5. The token-gate image runs behind the platform entrypoint, so that rule 4 works.

## Open question

How does the token-gate image run behind the platform entrypoint? There are two options.

- Keep the binary as the entrypoint. The base entrypoint does not run, so rule 4 does not hold.
- Switch to the base entrypoint and set the binary as `CMD`. This matches the platform guide and the `token-admin`
  image. The chart then needs `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, because
  the base entrypoint writes there and the root file system is read-only.

The second option is the only one that satisfies rule 4 and follows the platform guide. This record will be accepted
once the architect confirms it, and rule 5 will then name the switch.

## Consequences

- Operators get a documented Docker path that CI exercises on every pull request.
- If the entrypoint switches, `build/token-gate/Dockerfile` drops its `ENTRYPOINT` line and ends with a `CMD` that
  starts the binary. The scripts in `/app/init.d` then also run in the token-gate container.
- If the entrypoint switches, the chart mounts the two `emptyDir` volumes in the Pod of token-gate.
````

### Message to the user

I wrote ADR 0007 with status Proposed, because the notes leave the entrypoint question open and I did not decide it for the architect. Rules 1 to 4 record what the notes decided. Rule 5 states only the requirement, and the two options sit under "Open question".

Questions:
1. Can @example-architect confirm the switch to the base entrypoint with the binary as `CMD`? I recommend it: it is the only option that makes `/tmp/cert` work, and it matches the platform guide and `token-admin`. Once confirmed, I would set the status to Accepted and turn rule 5 into the switch.
2. Does anyone know why `build/token-gate/Dockerfile` has had `ENTRYPOINT ["/usr/local/bin/token-gate"]` since its first commit? Nothing in the repository explains it.

I did not touch `docs/adr/README.md`, because I don't have its content. It may need a row for this record. The `Layers` line and the section order follow my reading of the `adr-authoring` template, which I could not open here. Please compare them with records 0001 to 0006.

## Request 2

### File: docs/adr/0007-refuse-none-and-hmac-token-algorithms.md

````markdown
# 0007. Refuse tokens signed with `none` or HMAC algorithms

- Status: Accepted
- Date: 2026-11-11
- Deciders: @example-security-architect
- Layers: `verify`, `server`

## Context

`internal/verify` verifies token signatures with the `jwx` library. `jwx` refuses a token whose `alg` header is `none`
when it verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key.
`internal/verify` passes `jwx` every key that the JWKS of an issuer holds. If a JWKS holds a symmetric key, a token
signed with an HMAC algorithm therefore verifies against it.

Token-gate has no use for HMAC. A symmetric key is a shared secret, so any holder of it can mint tokens for the issuer.

## Decision

1. The service refuses a token whose header names the algorithm `none` with HTTP 401 and the reason code
   `TOKEN_ALG_NONE`.
2. The service refuses a token signed with `HS256`, `HS384`, or `HS512` with HTTP 401 and the reason code
   `TOKEN_ALG_SYMMETRIC`.
3. HMAC with a shared secret per issuer is not supported. It was considered and rejected.

## Consequences

- `internal/verify` has to read the `alg` header before it calls `jwx`. The library already refuses `none`, but it does
  not report either reason code, so the service has to produce them itself.
- A token signed with HMAC is refused even when the JWKS of its issuer holds a matching symmetric key.
- An issuer that signs with HMAC cannot be used with token-gate. It has to switch to an asymmetric algorithm.
````

### Message to the user

I wrote ADR 0007 with status Accepted, recording the decision as stated in the notes. The context says that `jwx` already refuses `none` but accepts HMAC against a symmetric key in a JWKS. That is why the HMAC rule is a real change, and why the service needs its own check to emit both reason codes.

Questions:
1. Should the service also drop symmetric keys from the JWKS before it calls `jwx`? The notes don't say, so the ADR doesn't decide it.
2. Does `TOKEN_ALG_NONE` also apply to spellings such as `None` or `NONE`? The ADR names only `none`.

I did not touch `docs/adr/README.md`, because I don't have its content. The section order follows my reading of the `adr-authoring` template, which I could not open here. Please compare it with records 0001 to 0006.

## Request 3

### File: docs/adr/0007-require-tls-1-2-for-outgoing-connections.md

````markdown
# 0007. Require TLS 1.2 or later for outgoing connections

- Status: Accepted
- Date: 2026-11-11
- Deciders: @example-security-architect

## Context

token-gate makes outgoing TLS connections. The `crypto/tls` client of Go refuses TLS 1.1 and older by default, and
token-gate sets no minimum version of its own. The requirement therefore holds today because of the Go default, and no
setting in token-gate enforces it.

## Decision

1. The outgoing TLS connections of token-gate use TLS 1.2 or later.

## Consequences

- No code change is needed now, because the Go default already meets the requirement.
- A peer that offers only TLS 1.1 or older cannot be reached.
- If the default of `crypto/tls` changed, token-gate would follow it, because it sets no minimum version.
````

### Message to the user

I wrote ADR 0007 with status Accepted. It records the decision and says plainly that the Go default meets it and token-gate enforces nothing itself. No code change is part of it.

Question: should token-gate set `MinVersion: tls.VersionTLS12` explicitly on its outgoing connections? Without it, a later change to the Go default, or a `GODEBUG` setting, could lower the minimum without anyone noticing. If you want it, I would add a rule to this record and make the code change separately.

I left out the `Layers` line because the notes don't say which package makes the outgoing connections. I did not touch `docs/adr/README.md`, because I don't have its content. The section order follows my reading of the `adr-authoring` template, which I could not open here. Please compare it with records 0001 to 0006.
