## Request 1

### File: docs/adr/0007-let-m2m-tokens-reach-any-tenant.md

````markdown
# Let an M2M token reach any tenant and limit every other token to its own tenant

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003](0003-placeholder.md): the unknown-issuer response of R4 that Context cites.
- [ADR-0004](0004-placeholder.md): the provider rule R1 that Context cites, and the subject rule R3 and the namespace
  rule R5 that the Justification cites.

## Context

token-gate checks the token of each request before policy evaluation. The token is either a realm token or a service
account token. The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`. In the mode `legacy` the providers file holds no
provider of service account tokens (ADR-0004 R1), so a service account token there gets `TOKEN_ISSUER_UNKNOWN` (the
unknown-issuer response of ADR-0003 R4). A service account token is therefore a verified token only in the mode `k8s`.

token-gate needs one answer to the question of which callers may name a tenant other than their own.

## Decision

We will treat a verified realm token with the role `ROLE_M2M`, and every verified service account token, as an M2M
token. An M2M token may name any tenant, and every other token may name only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **verified token**: a token in `Authorization` that gets neither HTTP 401 nor HTTP 503 from the token checks that run
  before policy evaluation.
- **M2M token**: a verified token that R1 or R2 makes an M2M token.
- **requested tenant**: the tenant that a request names. `<the part of the request that names the tenant>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A verified realm token is an M2M token where its `realm_access.roles` claim holds `ROLE_M2M`, and
  is not an M2M token otherwise.
- **R2** (`verify`). A verified service account token is an M2M token.

#### Which tenants a token may reach

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`,
  whatever its requested tenant is.
- **R4** (`verify`). A request whose token in `Authorization` is a verified token that is not an M2M token gets HTTP
  403 with `CALLER_TENANT_MISMATCH` where the requested tenant differs from the value of the `tenant-id` claim of that
  token, or where that token has no `tenant-id` claim (O2).

### Justification

A service account token needs no role to be an M2M token, because ADR-0004 R3 refuses a token whose `sub` does not
start with `system:serviceaccount:`, and ADR-0004 R5 accepts a service account token only from a namespace that the
topology file lists (R2). A realm token needs the role `ROLE_M2M`, so that a realm token reaches another tenant only
where an operator granted it that role (R1, R3). A token that is not an M2M token has no way to reach another tenant
(R4).

### Alternatives considered

- **A1. Require `ROLE_M2M` for a service account token too.** Rejected by R2: ADR-0004 R3 and R5 already limit which
  service account tokens are verified tokens, so the role would add a second grant for the same caller.

## Consequences

Negative:

- Every service account in a namespace that the topology file lists reaches every tenant (R2, R3).
- A realm token with no `tenant-id` claim and no `ROLE_M2M` reaches no tenant, so it gets `CALLER_TENANT_MISMATCH` on
  every request (R4).

## Open points

- **O1.** Which part of a request names the requested tenant, such as a path segment, a header, or a body field.
  `example-architect` decides. It affects the term requested tenant, R3, and R4.
- **O2.** R4 assumes that a verified token that is not an M2M token and has no `tenant-id` claim gets
  `CALLER_TENANT_MISMATCH`. The other answer is that such a token gets a different refusal, with a code to be named.
  `example-architect` decides. It affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, because two open points block acceptance:

- **O1:** the notes don't say which part of a request names the tenant. The term "requested tenant" holds a placeholder.
- **O2:** the notes don't cover a token that is not M2M and has no `tenant-id` claim. I assumed it gets `CALLER_TENANT_MISMATCH`.

Questions and choices for you:

- Who owns this ADR? I left `Owner` as a placeholder. I also put `example-architect` as approver of R1 to R4, since they made the decision.
- I didn't see the existing records, so the Related ADRs links point to placeholder filenames. Replace them with the real paths of ADR-0003 and ADR-0004.
- If an earlier record already owns the terms "realm token" and "service account token", replace my definitions with a pointer to it.
- All four rules carry the `verify` layer. That is my reading of the code layout, so correct it if the tenant check lives in `server`.
- The last note, that a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy`, already follows from ADR-0003 R4 and ADR-0004 R1. It gets no rule and sits in Context as a fact.
- Alternative A1 is my inference from the note that service account tokens are safe as M2M tokens. Remove it if the meeting didn't consider it.

Code under `internal/verify` that implements these rules should end its commit message and pull request description with `Implements: ADR-0007 R1, R2, R3, R4`. The README guide needs no change.

## Request 2

### File: docs/adr/0007-refuse-tokens-that-fail-verification-before-policy-evaluation.md

````markdown
# Refuse a token that fails verification with HTTP 401 before policy evaluation, except where the client should retry

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003](0003-placeholder.md): the unknown-issuer rule R4 and the keys rule R9 that Context cites.
- [ADR-0004](0004-placeholder.md): the subject rule R3 that Context cites, and the namespace rule R5 that O1 cites.
- [ADR-0005](0005-placeholder.md): R2, the response that R1 uses for a token that gets `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token of each request before policy evaluation. Some checks already name an outcome for a failed
token: ADR-0003 R4 gives `TOKEN_ISSUER_UNKNOWN`, ADR-0004 R3 gives `TOKEN_SUBJECT_INVALID`, and ADR-0003 R9 gives
`TOKEN_KEYS_UNAVAILABLE`. No rule states one outcome for every failed check, or states that policy evaluation does not
run for a token that failed.

## Decision

We will refuse a token in `Authorization` that fails verification with HTTP 401 and the error code of the failed
check, and we will not run policy evaluation for it. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of
ADR-0005 R2 instead, so that the client retries.

### Terms

- **failed check**: a token in `Authorization` fails a check when a rule of an accepted ADR in the layer `verify` or
  `keys` refuses the token and names an error code for it. The error code of that rule is the error code of the failed
  check.

### Rules

#### Response to a failed check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a check gets HTTP 401 with the error code
  of the check that fails first, in the order that `verify` runs the checks (O2). The exception is a token that gets
  `TOKEN_KEYS_UNAVAILABLE`: it gets the response of ADR-0005 R2, not HTTP 401.

#### Policy evaluation

- **R2** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails a check.

### Justification

A client that gets 401 with the code of the failed check can tell which check refused its token (R1). A client that
gets the response of ADR-0005 R2 for `TOKEN_KEYS_UNAVAILABLE` knows that the failure is on the service side and retries
(R1). A request with a failed token never reaches policy evaluation, so policy never sees a token that was not
verified (R2).

### Alternatives considered

- **A1. Give `TOKEN_KEYS_UNAVAILABLE` HTTP 401 like every other failed check.** Rejected by R1: the client would treat a
  failure of the service as a bad token and would not retry.

## Consequences

Negative:

- A token that the namespace rule of ADR-0004 R5 refuses is not a failed check until O1 is settled, so R1 and R2 do not
  reach it.

Follow-ups:

- Settle O1 in a record that replaces ADR-0004 R5, if the answer adds an error code to that rule.

## Open points

- **O1.** ADR-0004 R5 names no error code for a token from a namespace that the topology file does not list, so that
  token is not a failed check. The answers: a record that replaces ADR-0004 R5 and names a code, or a code that this
  record names for that case. `example-architect` decides. It affects R1 and R2.
- **O2.** R1 assumes that a token that fails several checks gets the error code of the check that `verify` runs first.
  The other answer is a fixed order of the checks stated as a rule. `example-architect` decides. It affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, because two open points block acceptance:

- **O1:** ADR-0004 R5 names no error code, so a token from an unlisted namespace is not a "failed check" under my definition. The decision needs a code for that case, and I did not invent one. The clean fix is a record that replaces ADR-0004 R5. Do you want that record?
- **O2:** the notes don't say which code wins when a token fails several checks. I assumed the check that `verify` runs first.

Questions and choices for you:

- Who owns this ADR? I left `Owner` as a placeholder. I also put `example-architect` as approver of R1 and R2.
- I didn't see the existing records, so the Related ADRs links point to placeholder filenames. Replace them with the real paths of ADR-0003, ADR-0004, and ADR-0005.
- I did not restate the 503 and `Retry-After: 5` of ADR-0005 R2. R1 points at that rule instead, so the response stays defined in one place.
- I read the notes as skipping policy evaluation for the `TOKEN_KEYS_UNAVAILABLE` case too, because a 503 response ends the request. R2 covers it, since the term "failed check" includes that code. Correct this if the meeting meant otherwise.
- R1 overlaps with ADR-0003 R4 and ADR-0004 R3 for the two checks that already name 401. The record gives the general default for every check and does not replace those rules.
- The tags `verify` and `server` for R1 and the tag `server` for R2 are my reading of the layer map. Correct them if the code lives elsewhere.

Code that implements these rules should end its commit message and pull request description with `Implements: ADR-0007 R1, R2`. The README guide needs no change.
