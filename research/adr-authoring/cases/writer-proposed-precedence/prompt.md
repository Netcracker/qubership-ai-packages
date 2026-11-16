# Task

The user sends two requests about the repository below. Handle each request on its own, starting from the repository as
it is described here, as if the other request did not exist.

For each request, give a heading `## Request 1` or `## Request 2`. Under it, give every file you would create or change
as a heading `### File: <path>`, followed by the file's full content in a fence of four backticks, and then a heading
`### Message to the user` with what you would tell the user. Ask nothing and wait for nothing: where you would ask the
user something, write the question in that message.

Request 1: "Add a record for what the service does when the policy store is unreachable: it answers HTTP 503 with the
reason code `POLICY_STORE_UNAVAILABLE` instead of evaluating the policy, and this wins over the 403 of ADR-0010."

Request 2: "Add a record: the service reads its configuration only from `/etc/token-gate/config.yaml`, and a missing
file stops the start."

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request and then asks policy evaluation
  whether to let the request through. Policy evaluation reads its policies from a policy store over the network.
- `docs/adr/` holds `0006-trusted-key-sources.md` (`Accepted`, about which key sources verify a token signature),
  `0010-refuse-what-policy-denies.md`, and `0011-reason-codes-in-error-responses.md`; the next free number is 0012.
  Its `README.md` is the reading guide, copied from `adr-authoring 2.0.0`: it maps the layer `verify` to
  `internal/verify`, `policy` to `internal/policy`, `api` to `internal/api`, and `config` to `internal/config`, and
  leaves the statuses that bind a change at the default.
- `docs/adr/0010-refuse-what-policy-denies.md` reads, in full:

````markdown
# Refuse every request that policy evaluation does not allow

## Status

Proposed

### Owner

@platform-architect

### Participants and approvers

- Platform architect, @platform-architect: approves the rules.

## Context

Policy evaluation decides, for each request with a verified token, whether the subject may call the endpoint. The
service forwards a request to its backend only after that decision.

## Decision

We will forward a request to the backend only where policy evaluation allows it.

### Rules

#### Decisions

- **R1** (`policy`). A request reaches the backend only where policy evaluation allows it.
- **R2** (`policy`). Policy evaluation reads the policies of the endpoint the request calls, and no other endpoint's.
- **R3** (`api`). A request that policy evaluation does not allow is refused with HTTP 403 and the reason code
  `POLICY_DENIED`.

### Justification

The backend trusts every request it receives, so the service is the only place where access is decided (R1, R3).
````

- `docs/adr/0011-reason-codes-in-error-responses.md` reads, in full:

````markdown
# Name the reason for every error response in a reason code

## Status

Proposed

### Owner

@api-owner

### Participants and approvers

- API owner, @api-owner: approves the rules.

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from one closed list.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, and `POLICY_DENIED`.

### Justification

A closed list lets a client handle every cause it can receive (R2).
````
