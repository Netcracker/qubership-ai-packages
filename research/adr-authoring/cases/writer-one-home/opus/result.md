## Request 1

### File: docs/adr/0007-let-only-m2m-tokens-reach-other-tenants.md

````markdown
# Let only M2M tokens reach a tenant other than the tenant of their own `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file of ADR-0003>): the checks whose response R3 lets win over
  `CALLER_TENANT_MISMATCH`, and `TOKEN_ISSUER_UNKNOWN` of ADR-0003 R4, which a service account token gets in the mode
  `legacy`.
- [ADR-0004: <title of ADR-0004>](<file of ADR-0004>): the providers per mode of ADR-0004 R1, and the limits on service
  account tokens of ADR-0004 R3 and R5, which R2 relies on.

## Context

token-gate checks the token of each request before policy evaluation. Two kinds of token arrive in `Authorization`:
realm tokens, which Keycloak signs for a realm, and service account tokens, which the Kubernetes API server signs for a
service account. A realm token of a user carries a `tenant-id` claim. Some callers are services that act for every
tenant, and they need to name any tenant in a request.

ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`. ADR-0004 R5
accepts a service account token only from a namespace that the topology file lists.

In the mode `legacy`, ADR-0004 R1 leaves the providers file without a provider of service account tokens. A service
account token then gets `TOKEN_ISSUER_UNKNOWN` under ADR-0003 R4, so R2 has an effect only in the mode `k8s`.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token that may
name any tenant. Every other token in `Authorization` may name only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. Every other token in `Authorization` is
  not an M2M token.

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its `realm_access.roles` claim holds the
  string `ROLE_M2M`, and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenant of a request

- **R3** (`verify`). When a request names a tenant in `<tenant input>`, a token in `Authorization` that is not an M2M
  token gets HTTP 403 with `CALLER_TENANT_MISMATCH` unless that tenant equals the value of the token's `tenant-id`
  claim. A token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with `CALLER_TENANT_MISMATCH` for
  every tenant. An M2M token gets no `CALLER_TENANT_MISMATCH`, whichever tenant the request names. A token that a check
  of ADR-0003 or ADR-0004 refuses gets the response of that check instead of `CALLER_TENANT_MISMATCH`.

### Justification

A service that acts for every tenant needs a token that names any tenant, and the role `ROLE_M2M` lets the Keycloak
administrators grant that to a realm client in one place (R1). A service account token can be an M2M token without a
role, because ADR-0004 R3 limits it to the subjects of Kubernetes service accounts and ADR-0004 R5 limits it to the
namespaces that the topology file lists (R2). A user's token stays inside the user's own tenant, so a user of one tenant
cannot read or change the data of another (R3). The response of a failed token check wins over
`CALLER_TENANT_MISMATCH`, because the claims of a refused token cannot be trusted (R3).

### Alternatives considered

- **A1. Let every token in `Authorization` name any tenant, and leave the tenant check to policy evaluation.** Rejected
  by R3: every policy would have to repeat the check, and a policy that missed it would open every tenant to every user.
- **A2. Require `ROLE_M2M` in `realm_access.roles` of a service account token too.** Rejected by R2: the Kubernetes API
  server does not put `realm_access` into the tokens it signs, so no service account token could ever be an M2M token.

## Consequences

Positive:

- A service that calls token-gate for many tenants needs one token, not one token per tenant (R1, R2).

Negative:

- A Keycloak administrator who grants `ROLE_M2M` lets the tokens of that client or user name any tenant, so the role
  has to be granted as carefully as access to every tenant (R1, R3).
- Every service account in a namespace that the topology file lists can name any tenant in the mode `k8s` (R2, R3).
- A user who works for several tenants needs a token per tenant, since a token carries one `tenant-id` claim (R3).

## Open points

- **O1.** Which input of a request names the tenant that R3 compares, such as a header or a path segment, and what a
  request that names no tenant gets. `example-architect` decides. Affects R3.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every tenant. The other answer is HTTP 401 with an error code of its own, as a token that
  fails verification. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. Two open points block acceptance:

- **O1:** which input of the request names the tenant. R3 holds the placeholder `<tenant input>` until that's decided.
- **O2:** what a token that isn't M2M and has no `tenant-id` claim gets. R3 assumes HTTP 403 with `CALLER_TENANT_MISMATCH`.

The notes say that in the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`. I didn't make that a rule. ADR-0004 R1 and ADR-0003 R4 already produce that result, so a new rule would only repeat them. The record explains it in its Context instead.

Questions for you:

1. Does token-gate check the tenant of a request today? If a user's token can reach another tenant now, R3 changes the answer existing callers get. I'd then add that case and its test under Negative.
2. What are the titles and file names of ADR-0003 and ADR-0004? The links under **Related ADRs** hold placeholders for them.
3. Do ADR-0003 or ADR-0004 already define "realm token" and "service account token"? If so, I'll replace my definitions with pointers to those records.
4. Is `verify` the right layer for R3? I tagged all three rules `verify` without seeing the code. If the tenant check belongs in `server`, I'll change the tag.

## Request 2

### File: docs/adr/0007-answer-a-failed-token-with-401-before-policy-evaluation.md

````markdown
# Answer a token that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file of ADR-0003>): checks that make up verification, such as ADR-0003 R4, and the
  code `TOKEN_KEYS_UNAVAILABLE` of ADR-0003 R9, which R2 excepts.
- [ADR-0004: <title of ADR-0004>](<file of ADR-0004>): checks on service account tokens that make up verification, such
  as ADR-0004 R3 and R5.
- [ADR-0005: <title of ADR-0005>](<file of ADR-0005>): the response of ADR-0005 R2, which R2 gives a token that gets
  `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The records give a response
for some checks only. ADR-0003 R4 and ADR-0004 R3 give HTTP 401 with their codes. ADR-0005 R2 gives HTTP 503 with
`Retry-After: 5` to a token that gets `TOKEN_KEYS_UNAVAILABLE`. ADR-0004 R5 accepts a service account token only from a
namespace that the topology file lists, and names neither a status nor a code for a token it refuses. No record states
whether policy evaluation runs for a request whose token a check has refused.

## Decision

We will answer a request whose token in `Authorization` fails verification without running policy evaluation, with HTTP
401 and the code of the failed check. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2
instead, so that the client retries.

### Terms

- **verification**: the checks that the rules of ADR-0003 and ADR-0004 make on a token in `Authorization`.
- **fails verification**: a token in `Authorization` fails verification when at least one check of verification
  refuses it.

### Rules

#### Policy evaluation

- **R1** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails verification.

#### Response

- **R2** (`verify`, `server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the error
  code that the rule of the failed check names. Where the token fails more than one check, the response carries the
  code of the first check that fails, in the order the checks run. A request whose token gets `TOKEN_KEYS_UNAVAILABLE`
  as the code of the first failed check gets the response of ADR-0005 R2 instead of HTTP 401.

### Implementation notes

Adds no requirement. Return the code of the failed check from `internal/verify` and `internal/keys` as an error value,
and map that value to the response in one place in `internal/server`. A new check then needs no change in
`internal/server`.

### Justification

Policy evaluation reads the claims of the token, and the claims of a refused token cannot be trusted, so a request with
such a token stops before policy evaluation (R1). One status for every refused token lets a client tell a token problem
from any other failure, and the code tells it which check to look at (R2). A token that gets `TOKEN_KEYS_UNAVAILABLE`
may be valid, and its provider's keys may arrive in a moment. HTTP 401 would tell the client to get a new token, while
the response of ADR-0005 R2 tells it to retry the same token (R2).

### Alternatives considered

- **A1. Pass a request whose token fails verification to policy evaluation, and let the policy refuse it.** Rejected by
  R1: every policy would have to check the result of verification, and a policy that missed it would accept a refused
  token.
- **A2. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other code.** Rejected by R2: a client would discard a
  token that may be valid and would not retry.

## Consequences

Positive:

- Policies can rely on every token they see having passed verification (R1).

Negative:

- A token that fails several checks reports only the first, so a client may need several attempts to find every fault
  (R2).

Follow-ups:

- Write a record that replaces ADR-0004 R5 whole and names the error code of a service account token from a namespace
  that the topology file does not list.

## Open points

- **O1.** R2 assumes that a token that fails several checks gets the code of the first check that fails, in the order
  the checks run. The other answer is a fixed order of codes that the record lists. `example-architect` decides.
  Affects R2.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. Open point O1 blocks acceptance: when a token fails several checks, which code does the response carry? R2 assumes the code of the first check that fails, in the order the checks run.

ADR-0004 R5 names no error code, so R2 can't tell which code a service account token from an unlisted namespace gets. That gap belongs in ADR-0004 R5 itself. ADR-0004 is accepted, so filling it takes a new record that replaces ADR-0004 R5 whole. I listed that record as a follow-up and didn't write it.

Questions for you:

1. Should I write the record that replaces ADR-0004 R5? If so, which error code should a token from an unlisted namespace get?
2. A request with no `Authorization` header, or with a header that holds no token, falls under neither rule. Should it get HTTP 401 too? If so, with which code?
3. What are the titles and file names of ADR-0003, ADR-0004, and ADR-0005? The links under **Related ADRs** hold placeholders for them.
4. Are the layer tags right? I tagged R1 `server` and R2 `verify` and `server` without seeing the code.
