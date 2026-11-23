# Task

The user sends two requests, each with its own meeting notes. Handle each request on its own, starting from the
repository as it is described here, as if the other request did not exist.

For each request, give a heading `## Request 1` or `## Request 2`. Under it, give every file you would create or change
as a heading `### File: <path>`, followed by the file's full content in a fence of four backticks, and then a heading
`### Message to the user` with what you would tell the user. Ask nothing and wait for nothing: where you would ask the
user something, write the question in that message.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation. It
  ships as a container image and a Helm chart.
- `docs/adr/` holds records 0001 to 0006 in the template of `adr-authoring`, with numbered rules, and a `README.md`
  that is the reading guide. Every record is `Accepted`, and the next free number is 0007. The guide maps the layer
  `verify` to `internal/verify`, `keys` to `internal/keys`, `server` to `internal/server`, and `startup` to
  `cmd/token-gate`.
- A realm token is a token that Keycloak signs for a realm. A service account token is a token that the Kubernetes API
  server signs for a service account. The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`.
- These rules of the existing records are the ones the notes below refer to, as the records state them:
  - ADR-0003 R4 (`verify`). A token whose `iss` names no provider of the providers file gets HTTP 401 with
    `TOKEN_ISSUER_UNKNOWN`.
  - ADR-0003 R9 (`keys`). A token whose provider has had no keys since the start gets `TOKEN_KEYS_UNAVAILABLE`.
  - ADR-0004 R1 (`keys`). In the mode `legacy` the providers file holds no provider of service account tokens, and in
    the mode `k8s` it holds exactly one. Anything else stops the start.
  - ADR-0004 R3 (`verify`). The `sub` of a service account token starts with `system:serviceaccount:`, or the token
    gets HTTP 401 with `TOKEN_SUBJECT_INVALID`.
  - ADR-0004 R5 (`verify`). A service account token is accepted only from a namespace that the topology file lists.
  - ADR-0005 R2 (`server`). A request whose token gets `TOKEN_KEYS_UNAVAILABLE` gets HTTP 503 with `Retry-After: 5`.

## Request 1

"Write an ADR from these notes of the architecture meeting."

- The architect, @example-architect, decided which tokens in `Authorization` are M2M tokens, and what that changes:
  - A realm token is an M2M token when `realm_access.roles` holds `ROLE_M2M`.
  - A service account token is an M2M token. That is safe: ADR-0004 R3 refuses one whose `sub` does not start with
    `system:serviceaccount:`, and ADR-0004 R5 accepts one only from a namespace that the topology file lists.
  - An M2M token may name any tenant. A token that is not M2M may reach only the tenant of its own `tenant-id` claim,
    and any other tenant gets HTTP 403 with `CALLER_TENANT_MISMATCH`. A token that is not M2M never reaches another
    tenant.
  - In the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`, since that mode has no provider for it.

## Request 2

"Write an ADR from these notes of the architecture meeting."

- The architect, @example-architect, decided: a token in `Authorization` that fails verification gets HTTP 401 before
  policy evaluation, with the code of the check that failed. The exception is a token that gets
  `TOKEN_KEYS_UNAVAILABLE`, which gets the response of ADR-0005 R2 instead, so that the client retries.
