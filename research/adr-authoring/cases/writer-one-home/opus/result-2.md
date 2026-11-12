## Request 1

### File: docs/adr/0007-limit-tokens-that-are-not-m2m-tokens-to-their-own-tenant.md

````markdown
# Treat realm tokens with `ROLE_M2M` and all service account tokens as M2M tokens, and limit every other token to its own tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- ADR-0003: its rules make up verification, which R3 builds on.
- ADR-0004: its `sub` check (R3) and namespace check (R5) are the reason for R2.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. It accepts two kinds of
token: realm tokens, which Keycloak signs for a realm, and service account tokens, which the Kubernetes API server signs
for a service account. ADR-0003 and ADR-0004 decide which tokens pass verification. They do not decide which tenants a
token that passes verification may reach.

Some callers act for one tenant. Others are machine-to-machine (M2M) clients that act for any tenant. A realm token
carries the roles that Keycloak grants its client in the claim `realm_access.roles`, and it carries the tenant of its
caller in the claim `tenant-id`.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. A request
whose token is not an M2M token may reach only the tenant of the token's `tenant-id` claim.

### Terms

- **realm token**: a token in `Authorization` that Keycloak signs for a realm.
- **service account token**: a token in `Authorization` that the Kubernetes API server signs for a service account.
- **verification**: the checks that the rules of ADR-0003 and ADR-0004 make of a token in `Authorization`. A token
  passes verification when it fails none of them.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **own tenant**: the value of the `tenant-id` claim of a token in `Authorization`. A token without that claim has no
  own tenant.
- **target tenant**: the tenant that a request names in `<where a request names its tenant>`.

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token is an M2M token when its claim `realm_access.roles` holds the value `ROLE_M2M`. Any
  other realm token is not an M2M token.
- **R2** (`verify`). Every service account token is an M2M token.

#### Tenants

- **R3** (`verify`). A request whose token in `Authorization` passes verification and is not an M2M token gets HTTP 403
  with `CALLER_TENANT_MISMATCH` when its target tenant differs from the token's own tenant. Where that token has no own
  tenant, the request gets HTTP 403 with `CALLER_TENANT_MISMATCH` for every target tenant.
- **R4** (`verify`). No check before policy evaluation refuses a request because of its target tenant when the token in
  `Authorization` is an M2M token, whatever the token's own tenant is and whether it has one.

### Implementation notes

Adds no requirement. Decide whether a token is an M2M token once, after verification, and pass the result to the tenant
check together with the claims. A table test over realm tokens with and without `ROLE_M2M`, service account tokens, and
target tenants equal to, different from, and without an own tenant covers R1 to R4.

### Justification

The architect limited every caller except M2M clients to its own tenant, so that a tenant is reachable only by its own
callers and by M2M clients (R3, R4).

R1 makes the role `ROLE_M2M` the mark of an M2M realm token, so cross-tenant access for a realm client is granted and
withdrawn in Keycloak (R1).

A service account token needs no such mark. Verification applies the `sub` check of ADR-0004 R3 and the namespace check
of ADR-0004 R5 to every service account token, so each service account token that R4 lets reach any tenant has passed
both checks (R2, R4).

### Alternatives considered

- **A1. Require `ROLE_M2M`, or another mark, on a service account token before it counts as an M2M token.** Rejected by
  R2: the checks of ADR-0004 R3 and R5 already limit which service account tokens pass verification.
- **A2. Let every token that passes verification reach the target tenant its request names, and leave tenant limits to
  policy evaluation.** Rejected by R3: a token that is not an M2M token reaches no tenant other than its own tenant.

## Consequences

Positive:

- A realm administrator grants or withdraws cross-tenant access with the role `ROLE_M2M`, and token-gate needs no change
  (R1).

Negative:

- A client that sends a realm token without `ROLE_M2M` for a target tenant other than its own tenant gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` (R3). Where token-gate passes such a request to policy evaluation before this record, that
  client breaks on upgrade.
- Every service account token that passes verification reaches every tenant (R2, R4). An edit of the topology file,
  which the namespace check of ADR-0004 R5 reads, therefore also decides which workloads act across tenants.

Follow-ups:

- Grant `ROLE_M2M` in Keycloak to the clients that act for more than one tenant before R3 ships.

## Open points

- **O1.** Where a request names its target tenant, such as a header, a path segment, or a claim, and what a request that
  names no tenant gets. The architect, `example-architect`, decides. Affects R3, R4, and the term **target tenant**.
- **O2.** R3 assumes that verification comes before the tenant check, so a token that fails verification gets the
  response of the check it failed and never `CALLER_TENANT_MISMATCH`. The other answer is to check the tenant first. The
  architect decides. Affects R3.
- **O3.** R3 assumes that a request whose token is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every target tenant. The other answer is that verification refuses such a token with a
  code of its own, `<code for a missing tenant-id claim>`. The architect decides. Affects R3.
````

### Message to the user

I've written the record as `docs/adr/0007-limit-tokens-that-are-not-m2m-tokens-to-their-own-tenant.md`. It stays `Proposed` because open points O1 to O3 block acceptance:

- **O1:** where a request names its tenant. This is still the `<where a request names its tenant>` placeholder.
- **O2:** whether verification comes before the tenant check.
- **O3:** what happens to a token that isn't M2M and has no `tenant-id` claim.

Two statements from the notes have no rule of their own, because accepted rules already produce them:

- **"A token that is not M2M never reaches another tenant":** R3 already says this.
- **"In the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`":** ADR-0004 R1 and ADR-0003 R4 together already produce this outcome.

The architect's reason for treating service account tokens as M2M is under Justification. It cites ADR-0004 R3 and R5 by the checks they make and doesn't repeat their conditions.

Questions:

1. Is `example-architect` the owner of this record, and does anyone besides the architect approve it?
2. What are the filenames and titles of ADR-0003 and ADR-0004? I listed them under **Related ADRs** without links because I don't have those details.
3. I tagged R3 and R4 `verify` without reading the code. If the tenant check will live in `internal/server`, should I change the tag to `server`?
4. I used the filename pattern `NNNN-slug.md`. Does that match the existing records?

## Request 2

### File: docs/adr/0007-refuse-tokens-that-fail-verification-before-policy-evaluation.md

````markdown
# Answer a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- ADR-0003: its rules make up verification and name most of the codes that R2 returns.
- ADR-0004: its rules make up verification. R3 gives a code to its namespace check (R5).
- ADR-0005: R2 of this record keeps the response of ADR-0005 R2 for `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The rules of ADR-0003 and
ADR-0004 make these checks and give most of them a code, such as `TOKEN_ISSUER_UNKNOWN` (ADR-0003 R4) and
`TOKEN_SUBJECT_INVALID` (ADR-0004 R3). Some of these rules name an HTTP status, and others name only the code, such as
the keys check of ADR-0003 R9. The namespace check of ADR-0004 R5 names neither. ADR-0005 R2 gives the response for
`TOKEN_KEYS_UNAVAILABLE`.

## Decision

We will answer a request whose token in `Authorization` fails verification with HTTP 401 and the code of the failed
check, before policy evaluation. A request whose token gets `TOKEN_KEYS_UNAVAILABLE` keeps the response of ADR-0005 R2.

### Terms

- **verification**: the checks that the rules of ADR-0003 and ADR-0004 make of a token in `Authorization`. A token
  fails verification when it fails at least one of them.
- **code of a check**: the error code that the rule of a check, or R3, names for a token that fails the check.

### Rules

#### Requests whose token fails verification

- **R1** (`server`). A request whose token in `Authorization` fails verification does not reach policy evaluation.
- **R2** (`server`). A request whose token in `Authorization` fails a check of verification gets HTTP 401 with the code
  of that check. Where the token fails several checks, the request gets the code of one of them. The exception is a
  request whose token gets `TOKEN_KEYS_UNAVAILABLE`: it gets the response of ADR-0005 R2, also where the token fails
  other checks.

#### Codes

- **R3** (`verify`). A token in `Authorization` that fails the namespace check of ADR-0004 R5 gets the code
  `<namespace code>`.

### Implementation notes

Adds no requirement. Map each code to its response in one table in `internal/server`. In that table,
`TOKEN_KEYS_UNAVAILABLE` maps to the response of ADR-0005 R2, and every other code maps to HTTP 401. Return the response
before the call to policy evaluation. A table test over every code of ADR-0003, ADR-0004, and R3 then covers R2.

### Justification

token-gate can't trust the claims of a token that fails verification, so policy evaluation never gets them (R1). With
one status for every failed check, a client can treat each failure as a bad token, and the code tells it which check
failed (R2, R3). `TOKEN_KEYS_UNAVAILABLE` reports a state of token-gate rather than a bad token. The response of
ADR-0005 R2 makes the client retry, so R2 keeps that response.

### Alternatives considered

- **A1. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** Rejected by R2: the client
  would not retry a request that can pass once the keys load.
- **A2. Pass a token that fails verification to policy evaluation together with its code, and let the policy decide.**
  Rejected by R1.

## Consequences

Negative:

- Where token-gate answers a failed check with another status before this record, its clients get HTTP 401 instead
  (R2).
- Under the assumption of O2, a token that gets `TOKEN_KEYS_UNAVAILABLE` and also fails a check that no retry can pass
  gets the response of ADR-0005 R2. The client then retries a request that fails again (R2).

## Open points

- **O1.** The code for a token that fails the namespace check of ADR-0004 R5. That rule names no code, so R3 holds the
  placeholder `<namespace code>`. The architect, `example-architect`, decides. Affects R2 and R3.
- **O2.** R2 assumes two things about a token that fails several checks. First, the response of ADR-0005 R2 wins over
  HTTP 401 whenever the token gets `TOKEN_KEYS_UNAVAILABLE`. Second, among the other failed checks, the code of any one
  of them is enough. The other answers are HTTP 401 for any token that also fails a check other than the keys check, and
  a fixed order of the checks that picks the code. The architect decides. Affects R2.
````

### Message to the user

I've written the record as `docs/adr/0007-refuse-tokens-that-fail-verification-before-policy-evaluation.md`. It stays `Proposed` because two open points block acceptance:

- **O1:** the code for a token that fails the namespace check of ADR-0004 R5. That rule names no code, so R3 holds the placeholder `<namespace code>`.
- **O2:** which response and code a token gets when it fails several checks. R2 assumes that the `TOKEN_KEYS_UNAVAILABLE` response wins, because ADR-0005 R2 requires that response for every token that gets this code.

The exception in R2 points at ADR-0005 R2 and doesn't copy its status or its `Retry-After` value.

Questions:

1. Does any rule of ADR-0003, ADR-0004, or ADR-0006 that I haven't seen name a status other than HTTP 401 for a failed token check? If so, R2 changes an accepted rule. The new record then has to name that rule as replaced under **Related ADRs**, and the old rule stays in force until this record is accepted.
2. Do other accepted records also make checks of the token? The term **verification** covers only the checks of ADR-0003 and ADR-0004.
3. Is `example-architect` the owner, and does anyone else approve the record?
4. What are the filenames and titles of ADR-0003 to ADR-0005? I listed them under **Related ADRs** without links.
5. I tagged R1 and R2 `server` and R3 `verify` without reading the code. Do those tags match where the code lives?
