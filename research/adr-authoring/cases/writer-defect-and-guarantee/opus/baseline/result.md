## Request 1

### File: docs/adr/0007-support-token-gate-under-docker.md

````markdown
# 0007. Support token-gate under Docker without Kubernetes

- Status: Proposed
- Date: November 11, 2026
- Deciders: @example-architect
- Layers: `docker`, `ci`, `image`, `chart`

## Context

token-gate ships as a container image and a Helm chart. Some operators run it under Docker without Kubernetes, so
they have no chart values to configure it with.

Under Docker, an operator whose identity provider uses a certificate issued by a private CA has to add that CA to the
trust store of the container. Otherwise the HTTPS calls to the identity provider fail. Every image of the platform
builds on `ghcr.io/example/platform-base`. That image's entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in
a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store. It then runs the scripts in `/app/init.d` and,
last, its own arguments. The platform's guide for service images says to keep that entrypoint and to set the service's
binary as `CMD`.

`build/token-admin/Dockerfile` follows the guide and ends with `CMD ["token-admin"]`. `build/token-gate/Dockerfile`
ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, which replaces the base entrypoint. The line has been there since
the file's first commit, and no record or issue explains it. As a result, the base entrypoint never runs in the
token-gate image, and a certificate mounted under `/tmp/cert` is not added to the trust store.

The chart runs the Pod of token-gate with a read-only root file system. The base entrypoint writes to `/etc/ssl/certs`
and `/usr/local/share/ca-certificates`.

## Decision

1. (`docker`) token-gate is supported under Docker without Kubernetes. Environment variables and mounted files are
   enough to configure it, and no setting requires the chart.
2. (`docker`) The repository ships a Compose example under `deploy/docker/`.
3. (`ci`) A job under `.github/workflows/` starts the Compose example on every pull request and calls `GET /ready`.
   The job fails if the call does not succeed.
4. (`image`) To trust a private CA, an operator mounts the CA's certificate under `/tmp/cert`, as for every other image
   of the platform.

## Open question: the entrypoint of the token-gate image

Rule 4 holds only if token-gate runs behind the base entrypoint. This record stays proposed until one of these options
is chosen.

### Option A: keep the binary as the entrypoint

`build/token-gate/Dockerfile` keeps `ENTRYPOINT ["/usr/local/bin/token-gate"]`. The base entrypoint does not run, so
rule 4 does not hold. This record would then need some other way to trust a private CA under Docker.

### Option B: keep the base entrypoint and set the binary as `CMD`

`build/token-gate/Dockerfile` drops its `ENTRYPOINT` line and ends with `CMD ["/usr/local/bin/token-gate"]`, as the
platform guide says.

- The base entrypoint adds the certificates under `/tmp/cert` and runs the scripts in `/app/init.d` before it starts
  token-gate.
- (`chart`) The chart mounts `emptyDir` volumes at `/etc/ssl/certs` and `/usr/local/share/ca-certificates`, because
  the root file system is read-only and the entrypoint writes to both paths.
- An `emptyDir` volume starts empty and hides whatever the image has at that path. Before this option is accepted,
  someone has to check that the base entrypoint writes the full trust store to `/etc/ssl/certs`, public CAs included,
  and not only the certificates from `/tmp/cert`.
- Arguments given to `docker run` after the image name, and `args` in a Kubernetes container spec, replace `CMD`.
  Under option A, token-gate receives them as flags. Under option B, they replace the binary, so every such invocation
  has to start with `/usr/local/bin/token-gate`. That includes any `args` set by the chart.

## Consequences

- Each new setting needs an environment variable or a mounted file, so that it works without the chart.
- The Compose example becomes a supported artifact. A change that breaks it fails the CI job of rule 3.
- Every pull request starts the Compose example, which makes CI take longer.
````

### Message to the user

I added `docs/adr/0007-support-token-gate-under-docker.md` with the status "Proposed". The meeting left the entrypoint question open, and rule 4 depends on how that question is answered.

**Mounting a certificate under `/tmp/cert` has no effect on token-gate today.** `build/token-gate/Dockerfile` ends with `ENTRYPOINT ["/usr/local/bin/token-gate"]`, so the base image's `/usr/bin/entrypoint.sh` never runs. Rule 4 holds only with option B.

I recommend option B. It's what the platform guide says to do, and `token-admin` already works that way. Two things need checking before you accept it:

- **The `emptyDir` volume at `/etc/ssl/certs`:** it hides the CA bundle that ships in the image. If the base entrypoint writes only the private CAs there, and not the full bundle, token-gate will stop trusting public CAs under the chart.
- **Arguments:** with the binary in `CMD`, arguments passed to `docker run` and `args` in the chart replace the binary instead of being passed to it as flags. Any existing `args` in the chart, and any Docker command line that passes flags, has to start with the binary path.

Questions for @example-architect:

1. Which option do you choose, A or B? Once that's decided I'll update the record and set it to "Accepted".
2. Do you know whether the `ENTRYPOINT` line in `build/token-gate/Dockerfile` was added on purpose, for example to skip the scripts in `/app/init.d`? Nothing in the repository explains it.

I haven't updated `docs/adr/README.md`. I don't have its current content, and the new record still needs an entry there. I also didn't create the Compose example, the CI job, or any Dockerfile or chart changes, because the request was for the record only.

## Request 2

### File: docs/adr/0007-refuse-unsigned-and-hmac-signed-tokens.md

````markdown
# 0007. Refuse unsigned and HMAC-signed tokens

- Status: Accepted
- Date: November 11, 2026
- Deciders: @example-security-architect
- Layers: `verify`, `server`

## Context

`internal/verify` uses the `jwx` library to verify the signature of each token. `jwx` refuses to verify a token whose
`alg` header is `none`, but the service has no reason code that tells this case apart from any other failed
verification.

`jwx` accepts `HS256`, `HS384`, and `HS512` when the key set contains a symmetric key, and `internal/verify` passes it
every key in the issuer's JWKS. So if an issuer's JWKS publishes a symmetric key, token-gate accepts tokens signed with
that key using HMAC. A JWKS is usually served without authentication, which means anyone who can fetch it can sign
tokens that token-gate accepts.

## Decision

1. (`verify`) A token whose JOSE header sets `alg` to `none` is refused with the reason code `TOKEN_ALG_NONE`.
2. (`verify`) A token whose JOSE header sets `alg` to `HS256`, `HS384`, or `HS512` is refused with the reason code
   `TOKEN_ALG_SYMMETRIC`, regardless of which keys the issuer's JWKS contains.
3. (`verify`) The checks in rules 1 and 2 read the header before signature verification. The reason code therefore
   depends only on `alg`, and not on the key set or on the error that `jwx` returns.
4. (`server`) The service responds to a token refused under rule 1 or rule 2 with HTTP 401 and the token's reason code.

## Alternatives considered

### Accept HMAC with a shared secret per issuer

Each issuer would share a secret with token-gate, and token-gate would verify `HS256`, `HS384`, and `HS512` tokens
with that secret. The security review considered and rejected this option.

## Consequences

- An issuer that signs tokens with HMAC can no longer authenticate to token-gate. Its tokens get HTTP 401 with
  `TOKEN_ALG_SYMMETRIC`.
- `jwx` alone does not meet rule 2. `internal/verify` needs its own header check before it calls `jwx`.
````

### Message to the user

I added `docs/adr/0007-refuse-unsigned-and-hmac-signed-tokens.md` with the status "Accepted". The record describes behavior the code doesn't have yet. Today, `jwx` refuses `none` without a separate reason code. It also accepts `HS256`, `HS384`, and `HS512` whenever an issuer's JWKS contains a symmetric key, because `internal/verify` passes it every key. Rules 1–3 need a header check in `internal/verify`, and rule 4 needs the response mapping in `internal/server`. I didn't change any code.

Questions for @example-security-architect:

1. Why was HMAC with a shared secret per issuer rejected? The notes don't give a reason, so the "Alternatives considered" section only says the review rejected it. I'll add the reason once I have it.
2. Should rule 1 also cover `alg` values that differ from `none` only in case, such as `None` or `NONE`? `jwx` refuses them as unknown algorithms, but under the current wording they wouldn't get `TOKEN_ALG_NONE`.
3. Should `internal/verify` also drop symmetric (`kty` `oct`) keys from each JWKS before it passes the key set to `jwx`? That would refuse HMAC a second time, independent of the header check.
4. Does any issuer in use today sign with HMAC? If so, rule 2 is a breaking change for that issuer.

I haven't updated `docs/adr/README.md`. I don't have its current content, and the new record still needs an entry there.

## Request 3

### File: docs/adr/0007-require-tls-1-2-for-outgoing-connections.md

````markdown
# 0007. Require TLS 1.2 or later for outgoing connections

- Status: Accepted
- Date: November 11, 2026
- Deciders: @example-security-architect
- Layers: `verify`

## Context

token-gate opens outgoing TLS connections, for example to fetch an issuer's JWKS. When `tls.Config.MinVersion` is
zero, Go's `crypto/tls` client uses TLS 1.2 as the minimum version, and it refuses TLS 1.1 and older. This has been
the default since Go 1.18. token-gate sets no `MinVersion` of its own, so its outgoing connections use TLS 1.2 or later.

## Decision

1. Every outgoing TLS connection of token-gate uses TLS 1.2 or later.
2. token-gate relies on the `crypto/tls` default to meet rule 1 and sets no `MinVersion` of its own.

## Consequences

- An identity provider that supports only TLS 1.1 or older is unreachable, because the handshake fails.
- Rule 1 holds only while the default of `crypto/tls` does, so token-gate has to be built with Go 1.18 or later.
- A change that sets `MinVersion` below `tls.VersionTLS12` on an outgoing connection breaks rule 1.
````

### Message to the user

I added `docs/adr/0007-require-tls-1-2-for-outgoing-connections.md` with the status "Accepted". No code change is needed. `crypto/tls` has defaulted to a client minimum of TLS 1.2 since Go 1.18, and token-gate doesn't override it. I didn't have a checkout, so I couldn't confirm the Go version in `go.mod`. I also couldn't check every outgoing connection for its own `tls.Config`, so I listed only the `verify` layer.

Questions for @example-security-architect:

1. Rule 1 depends on a default of the toolchain. Setting `MinVersion: tls.VersionTLS12` explicitly on token-gate's outgoing `tls.Config` would make the rule independent of the Go version, and a test could check it. Do you want that instead of rule 2? If so, I'll update the record and make the code change.
2. Do any outgoing TLS connections live outside `internal/verify`? If they do, I'll add their layers to the record.

I haven't updated `docs/adr/README.md`. I don't have its current content, and the new record still needs an entry there.
