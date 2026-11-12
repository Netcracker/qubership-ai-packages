# Task

The user sends three requests, each with its own meeting notes. Handle each request on its own, starting from the
repository as it is described here, as if the other request did not exist.

For each request, give a heading `## Request 1`, `## Request 2`, or `## Request 3`. Under it, give every file you would
create or change as a heading `### File: <path>`, followed by the file's full content in a fence of four backticks, and
then a heading `### Message to the user` with what you would tell the user. Ask nothing and wait for nothing: where you
would ask the user something, write the question in that message.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation. It
  ships as a container image and a Helm chart.
- `docs/adr/` holds records 0001 to 0006 in the template of `adr-authoring`, with numbered rules, and a `README.md`
  that is the reading guide. The next free number is 0007. The guide maps the layer `image` to `build/`, `chart` to
  `helm/`, `docker` to `deploy/docker/`, `ci` to `.github/workflows/`, `verify` to `internal/verify`, and `server` to
  `internal/server`. No record mentions the entrypoint of an image.
- Both images of the repository, built by `build/token-gate/Dockerfile` and `build/token-admin/Dockerfile`, build on the
  platform base image `ghcr.io/example/platform-base`, pinned by digest.
- The README of the base image states its contract: its entrypoint, `/usr/bin/entrypoint.sh`, adds every certificate in
  a `.crt`, `.cer`, or `.pem` file under `/tmp/cert` to the trust store of the container, runs the scripts in
  `/app/init.d`, and then runs its arguments. The platform's guide for service images says to keep that entrypoint and
  to set the service's binary as `CMD`.
- `build/token-admin/Dockerfile` ends with `CMD ["token-admin"]`. `build/token-gate/Dockerfile` ends with
  `ENTRYPOINT ["/usr/local/bin/token-gate"]`, a line it has had since its first commit, with no comment; no record or
  issue explains it.
- The chart runs the Pod of token-gate with a read-only root file system.
- `internal/verify` verifies signatures with the `jwx` library. `jwx` refuses a token whose `alg` is `none` when it
  verifies a signature. It accepts `HS256`, `HS384`, and `HS512` when the key set holds a symmetric key, and
  `internal/verify` passes it every key that the JWKS of an issuer holds.

## Request 1

"Write an ADR from these notes of the architecture meeting."

- The architect, @example-architect, decided: token-gate is supported under Docker without Kubernetes, configured by
  environment variables and mounted files alone. The repository ships a Compose example under `deploy/docker/`, and a
  CI job starts it on every pull request and calls `GET /ready`.
- Under Docker, operators need to trust a private CA for the HTTPS calls to the identity provider. They mount its
  certificate under `/tmp/cert`, as for every image of the platform.
- For `/tmp/cert` to work, token-gate has to run behind the platform entrypoint. Open question: keep the binary as the
  entrypoint, or switch to the base entrypoint with the binary as `CMD`?
- With the base entrypoint, the chart needs `emptyDir` volumes at `/etc/ssl/certs` and
  `/usr/local/share/ca-certificates`, because the entrypoint writes there and the root file system is read-only.

## Request 2

"Write an ADR from these notes of the security review."

- The security architect, @example-security-architect, decided: the service refuses a token whose header names the
  algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and refuses a token signed with `HS256`,
  `HS384`, or `HS512` with HTTP 401 and the reason code `TOKEN_ALG_SYMMETRIC`. Accepting HMAC with a shared secret per
  issuer was considered and rejected.

## Request 3

"Write an ADR from these notes of the security review."

- The security architect, @example-security-architect, decided: the outgoing TLS connections of token-gate use TLS 1.2
  or later. Go's `crypto/tls` client already refuses TLS 1.1 and older by default, and token-gate sets no minimum
  version of its own.
