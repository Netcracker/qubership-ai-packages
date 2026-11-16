## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Treat a realm token with `ROLE_M2M` and every service account token as an M2M token that may name any tenant

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0004: service account tokens](0004-service-account-tokens.md): R3 and R5 limit which service account tokens are accepted, and R2 relies on them.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Two kinds of token reach it. Keycloak signs realm tokens, and the Kubernetes API server signs service account tokens. A caller that acts for a tenant and a machine caller that acts for many tenants both send such tokens, and the records so far do not say which tokens may name a tenant other than their own.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token that may name any tenant, and we will limit every other token to the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token that R1 or R2 names. Any other token is not an M2M token.
- **accepted token**: a token in `Authorization` that gets neither HTTP 401 nor HTTP 503 for the token itself.
- **target tenant**: the tenant that a request names, in `<where a request names its tenant>`.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token is an M2M token where its `realm_access.roles` holds `ROLE_M2M`.
- **R2** (`verify`). A service account token is an M2M token.

#### Access to a tenant

- **R3** (`server`). A request whose accepted token is an M2M token gets no `CALLER_TENANT_MISMATCH`, whatever its target tenant and whatever the `tenant-id` claim of the token holds.
- **R4** (`server`). A request whose accepted token is not an M2M token gets HTTP 403 with `CALLER_TENANT_MISMATCH` where its target tenant is not the tenant of the `tenant-id` claim of that token.

### Justification

A service account token is safe to treat as an M2M token, because ADR-0004 R3 refuses one whose `sub` does not start with `system:serviceaccount:`, and ADR-0004 R5 accepts one only from a namespace that the topology file lists (R2). A token that is not an M2M token never reaches another tenant, so a stolen or misused ordinary token cannot cross a tenant boundary (R4).

## Consequences

Negative:

- A service account token from any namespace that the topology file lists may reach every tenant (R2, R3).
- A realm token without `ROLE_M2M` gets HTTP 403 for every tenant other than its own (R4).

## Open points

- **O1.** Where does a request name its target tenant, such as a path segment, a header, or a body field? The architect decides. It affects R3 and R4 and fills the placeholder in the term **target tenant**.
- **O2.** Assumption: a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with `CALLER_TENANT_MISMATCH` for every target tenant. The architect confirms or names another outcome. It affects R4.
- **O3.** Assumption: the classification of R1 and R2 lives in the layer `verify`, and the tenant check of R3 and R4 lives in the layer `server`. The owner confirms after reading the code. It affects the layer tags of R1 to R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It is one decision, so it is one record.

- **Owner:** the notes name no owner, so the field holds the placeholder `<owner GitHub account>`. Who owns it? I listed `example-architect` as the approver of R1 to R4.
- **Open points that block acceptance:**
  - O1: the notes do not say how a request names its tenant.
  - O2: what happens to a non-M2M token with no `tenant-id` claim.
  - O3: whether the layer tags are right.
- **Left out on purpose:** the last note, that in the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`, has no rule. It already follows from ADR-0004 R1 (no service account provider in `legacy`) and ADR-0003 R4 (an unknown `iss` gets `TOKEN_ISSUER_UNKNOWN`). A rule would state it a second time.
- **Also left out:** the note "a token that is not M2M never reaches another tenant" is the same requirement as R4, so it appears only in the Justification.
- **Alternatives considered:** the notes name no rejected option, so I left the section out rather than invent one. Tell me if the meeting discussed any.
- **ADR-0004:** it stays as it is. The record cites its R3 and R5 only as reasons.

## Request 2

### File: docs/adr/0007-token-verification-failure-response.md

````markdown
# Reject a token that fails verification with HTTP 401 and the code of the failed check before policy evaluation

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: token verification and keys](0003-token-verification-and-keys.md): R4 gives one check its 401 and code, and R9 gives `TOKEN_KEYS_UNAVAILABLE`.
- [ADR-0004: service account tokens](0004-service-account-tokens.md): R3 gives one check its 401 and code.
- [ADR-0005: server responses](0005-server-responses.md): R2 gives the response that R1 uses for `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The records of single checks give each one its own response: ADR-0003 R4 and ADR-0004 R3 give HTTP 401 with a code, and ADR-0005 R2 gives HTTP 503 with `Retry-After: 5` for a token that gets `TOKEN_KEYS_UNAVAILABLE`. A client has to tell a token that is wrong from a token that cannot be checked yet, because only the second case is worth a retry.

## Decision

We will reject a token in `Authorization` that fails a verification check with HTTP 401 and the code of that check before policy evaluation, and a token that gets `TOKEN_KEYS_UNAVAILABLE` will get the response of ADR-0005 R2 instead, so that the client retries.

### Terms

- **verification check**: a check that the layers `verify` and `keys` apply to a token in `Authorization`, and that reports its failure with an error code such as `TOKEN_ISSUER_UNKNOWN`.

### Rules

#### Response to a failed token

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with the code of that check. A request whose token gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.
- **R2** (`server`). A request whose token in `Authorization` fails a verification check does not reach policy evaluation.

### Justification

A client that gets HTTP 503 with `Retry-After` retries, and a client that gets HTTP 401 with a code knows that its token is wrong. The exception of R1 keeps a temporary lack of keys from looking like a bad token. Rejecting the request before policy evaluation means that policy evaluation sees only tokens that passed every check (R2).

## Consequences

Negative:

- A client that treats every token failure as HTTP 401 gets HTTP 503 for a token that gets `TOKEN_KEYS_UNAVAILABLE` (R1).

## Open points

- **O1.** Assumption: every check of ADR-0003 and ADR-0004, and every check that a later record adds in the layers `verify` and `keys`, is a verification check. The architect confirms or lists the checks that are not. It affects R1 and R2.
- **O2.** Assumption: a request whose token gets `TOKEN_KEYS_UNAVAILABLE` also does not reach policy evaluation, since it gets the response of ADR-0005 R2. The architect confirms. It affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, with two rules.

- **Owner:** the notes name no owner, so the field holds the placeholder `<owner GitHub account>`. Who owns it? I listed `example-architect` as the approver of R1 and R2.
- **Open points that block acceptance:** O1 asks whether every check in `verify` and `keys` counts as a verification check. O2 asks whether the 503 case also stays out of policy evaluation.
- **Overlap to review:** R1 states the 401 for every check, so it includes the cases that ADR-0003 R4 and ADR-0004 R3 already settle. It does not contradict them. I did not restate the 503 response, because R1 points to ADR-0005 R2 for it. Tell me if you would rather scope R1 to checks that no earlier rule covers.
- **Layer tags:** R1 and R2 are tagged `verify`, `server` and `server` without having seen the code. Please confirm them.
- **Alternatives considered:** the notes name no rejected option, so I left the section out rather than invent one.
- **Earlier records:** ADR-0003, ADR-0004, and ADR-0005 stay as they are.
