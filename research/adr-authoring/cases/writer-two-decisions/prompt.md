# Task

The user sends two requests, each with its own meeting notes. Handle each request on its own, starting from the
repository as it is described here, as if the other request did not exist.

For each request, give a heading `## Request 1` or `## Request 2`. Under it, give every file you would create or change
as a heading `### File: <path>`, followed by the file's full content in a fence of four backticks, and then a heading
`### Message to the user` with what you would tell the user. Ask nothing and wait for nothing: where you would ask the
user something, write the question in that message.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- `docs/adr/` holds records 0001 to 0005 in the template of `adr-authoring`, with numbered rules, and a `README.md`
  that is the reading guide. The next free number is 0006. The guide maps the layer `verify` to `internal/verify`,
  `keys` to `internal/keys`, and `server` to `internal/server`.

## Request 1

"Write an ADR from these notes."

- The security architect decided: the service verifies the signature of every token before policy evaluation, and
  refuses a token whose signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.
- The platform team decided: the service answers `GET /healthz` with HTTP 200 while its process runs, so that
  Kubernetes can restart it when it stops answering.

## Request 2

"Write an ADR from these notes."

- The security architect decided, for token verification: the service takes signing keys from the JWKS of each trusted
  key source; it holds a loaded key set for 5 minutes; and it refuses a token whose header has no `kid` with HTTP 401
  and the reason code `TOKEN_KID_MISSING`.
- All three choices change together when the key handling changes.
