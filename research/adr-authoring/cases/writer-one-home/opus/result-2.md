## Request 1

### File: docs/adr/0007-limit-tokens-that-are-not-m2m-to-their-own-tenant.md

````markdown
# Let M2M tokens name any tenant, and limit every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): the issuer check of R4, which a service account token fails in the
  mode `legacy`, and the error codes that take precedence in R4 of this record.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the providers of R1, the subject check of R3, and the namespace check
  of R5, which the Justification of R2 relies on, and the error codes that take precedence in R4 of this record.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Keycloak signs realm tokens
for a realm, and the Kubernetes API server signs service account tokens for a service account. A request names the
tenant it acts on, and a token can carry the tenant of its holder in the claim `tenant-id`. Some callers act for every
tenant, such as services that call token-gate on behalf of other services. Every other caller acts within one tenant.

In the mode `legacy`, the providers file holds no provider of service account tokens (ADR-0004 R1). A service account
token then names an issuer that no provider has, and gets `TOKEN_ISSUER_UNKNOWN` under ADR-0003 R4. So in that mode
every token that reaches the tenant check is a realm token.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. We will
let a request with an M2M token name any tenant, and refuse with HTTP 403 a request with any other token that names a
tenant other than the token's `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. Every other token in `Authorization` is
  not an M2M token.
- **requested tenant**: the tenant that a request names in `<the part of the request that names the tenant>`.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its claim `realm_access.roles` is an array
  that holds the string `ROLE_M2M`, matched exactly. No other realm token is an M2M token.
- **R2** (`verify`). Every service account token in `Authorization` is an M2M token.

#### Tenants

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`,
  whatever its requested tenant is.
- **R4** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` where its requested tenant differs from the value of the token's `tenant-id` claim, or where
  the token has no `tenant-id` claim. Where the token also gets an error code under a rule of ADR-0003 or ADR-0004, the
  request gets the response of that code instead.

### Implementation notes

Adds no requirement. Decide whether a token is an M2M token once, after verification accepts the token, and let the
tenant check read that result rather than the claims.

### Justification

A service account token needs no role to be an M2M token (R2). The subject check of ADR-0004 R3 refuses a token whose
`sub` is not a service account subject, and the namespace check of ADR-0004 R5 accepts one only from a namespace that
the topology file lists. So only workloads in listed namespaces hold an M2M token of this kind.

A realm token becomes an M2M token only through the role `ROLE_M2M` (R1), so the role assignment in Keycloak decides
which realm clients act for every tenant.

A token that is not an M2M token never reaches a tenant other than its own (R4). A token without a `tenant-id` claim has
no tenant of its own, so it reaches none (R4). An M2M token reaches every tenant, so a service that acts for all tenants
needs one token rather than one per tenant (R3).

### Alternatives considered

- **A1. Treat a service account token as an M2M token only where it carries a role or a claim that marks it.**
  Rejected by R2: the subject and namespace checks of ADR-0004 already limit which workloads hold such a token.
- **A2. Let every token name any tenant, and leave the tenant to policy evaluation.** Rejected by R4: a token that is
  not an M2M token would then reach another tenant wherever a policy left the tenant out.

## Consequences

Negative:

- Granting `ROLE_M2M` to a Keycloak client or user lets its realm tokens name every tenant (R1, R3).
- In the mode `legacy`, a workload that acts for every tenant needs a realm token with `ROLE_M2M`, because its service
  account token gets `TOKEN_ISSUER_UNKNOWN` before the tenant check.
- A caller whose token is not an M2M token, and that sends requests for a tenant other than its `tenant-id` claim, gets
  HTTP 403 with `CALLER_TENANT_MISMATCH` once R4 lands.

## Open points

- **O1.** Which part of the request names the requested tenant: a request header or a segment of the request path.
  `example-architect` decides. Affects R3 and R4.
- **O2.** What a request gets where its token in `Authorization` is not an M2M token and the request names no tenant:
  the request passes to policy evaluation, or it gets HTTP 403 with `CALLER_TENANT_MISMATCH`. `example-architect`
  decides. Affects R4.
- **O3.** R4 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH`. The other answer under consideration is HTTP 401 with a code of its own.
  `example-architect` decides. Affects R4.
- **O4.** R4 assumes that the error code a token gets under ADR-0003 or ADR-0004 takes precedence over
  `CALLER_TENANT_MISMATCH`. `example-architect` confirms. Affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Four open points block acceptance:

- **O1:** where the request names its tenant. This one has a visible placeholder in the term **requested tenant**.
- **O2:** a request that names no tenant.
- **O3:** a token that is not M2M and has no `tenant-id` claim.
- **O4:** whether verification errors take precedence over `CALLER_TENANT_MISMATCH`.

The record has no rule for "In the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`". ADR-0004 R1 and ADR-0003 R4 already require that outcome, so a rule would only repeat them. I stated it in **Context** as a fact and listed what it costs under **Negative**. The sentence "A token that is not M2M never reaches another tenant" is part of R4, not a separate rule.

Questions:

1. Who else approves this record besides `example-architect`?
2. Do ADR-0003 or ADR-0004 already define "realm token" and "service account token"? If they do, the terms here should point to those definitions instead of defining them again.
3. What are the titles and filenames of ADR-0003 and ADR-0004? I left placeholders in the links.
4. The notes don't list any alternatives. I wrote A1 and A2 myself. Were these discussed in the meeting, or should I replace them?
5. I tagged R3 and R4 `verify`, but I couldn't see the code. Should the 403 response be tagged `server` instead?
6. What does a non-M2M token that names another tenant get today? If something other than HTTP 403, the **Negative** entry for R4 should name that case and the test that shows it.

## Request 2

### File: docs/adr/0007-answer-a-token-that-fails-verification-with-http-401.md

````markdown
# Answer a token in `Authorization` that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): the issuer check of R4 and the keys check of R9, which are
  verification checks.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the subject check of R3, which is a verification check. R2 of this
  record replaces R5.
- [ADR-0005: <title of ADR-0005>](0005-<slug>.md): R1 of this record makes an exception for the response of R2.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The issuer check of ADR-0003 R4
and the subject check of ADR-0004 R3 each give a failed token a status and a code. The keys check of ADR-0003 R9 gives
`TOKEN_KEYS_UNAVAILABLE`, and the response of ADR-0005 R2 to that code lets the client retry. The namespace check of
ADR-0004 R5 gives neither a status nor a code. None of these rules states whether a request whose token fails a check
reaches policy evaluation.

## Decision

We will answer a request whose token in `Authorization` fails a verification check with HTTP 401 and the code of the
check, before policy evaluation, except where the token gets `TOKEN_KEYS_UNAVAILABLE`.

### Terms

- **verification check**: a check on a token in `Authorization` that a rule with the layer `verify` or `keys` states,
  in this record or in another. The issuer check of ADR-0003 R4, the keys check of ADR-0003 R9, the subject check of
  ADR-0004 R3, and the namespace check of R2 are verification checks.

### Rules

#### Response to a failed verification check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with
  the code of a check that the token failed, and token-gate does not pass the request to policy evaluation. Where the
  token gets `TOKEN_KEYS_UNAVAILABLE`, the request gets the response of ADR-0005 R2 instead of HTTP 401.

#### Namespace of a service account token

- **R2** (`verify`). A service account token in `Authorization` from a namespace that the topology file does not list
  gets `<code for an unlisted namespace>`.

### Implementation notes

Adds no requirement. Let each check in `internal/verify` and `internal/keys` return its code as an error. Then let
`internal/server` map the error to the response before it calls policy evaluation.

### Justification

One rule gives every verification check its status and its place before policy evaluation. So a new check needs only a
code (R1). Policy evaluation then reads the claims only of a token that passed every verification check (R1).

`TOKEN_KEYS_UNAVAILABLE` reports that token-gate has no keys for the provider, not that the token is invalid. The client
retries on the response of ADR-0005 R2, and the same token can pass once the keys load (R1).

R2 gives the namespace check the code that R1 needs. It replaces ADR-0004 R5 whole, so the check and its code live in
one rule.

### Alternatives considered

- **A1. Pass a request whose token failed a verification check to policy evaluation, and let the policy refuse it.**
  Rejected by R1.
- **A2. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** Rejected by R1: a client does
  not retry HTTP 401, although the keys can load later.

## Consequences

Negative:

- A check that a later record adds with the layer `verify` or `keys` gets HTTP 401 unless that record makes an
  exception to R1.
- A service account token from a namespace that the topology file does not list gets HTTP 401 with the code of R2. A
  client that handled an earlier response to that case has to handle this one (R1, R2).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0004 that names R5 as replaced by R2 of this
  record.

## Open points

- **O1.** Which code a service account token from a namespace that the topology file does not list gets. The meeting
  named none. `example-architect` decides. Affects R2, and R1 for that check.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Open point O1 blocks acceptance. R1 says "with the code of the check that failed", but the namespace check of ADR-0004 R5 has no code. R2 therefore gives that check a code, written as the placeholder `<code for an unlisted namespace>`.

ADR-0004 is accepted, so R2 replaces ADR-0004 R5 in full instead of narrowing it from this record. ADR-0004 stays as it is until this record is accepted. Then it gets a line under **Related ADRs**, which is listed as a follow-up.

The 401 responses of ADR-0003 R4 and ADR-0004 R3 and the 503 response of ADR-0005 R2 stay in their own records. R1 adds HTTP 401 for every other verification check, keeps failed requests out of policy evaluation, and makes the exception that refers to ADR-0005 R2.

Questions:

1. Which code should a service account token from a namespace that the topology file doesn't list get (O1)?
2. Do ADR-0001 to ADR-0006 contain any other checks on a token that give no code? R1 needs a code for each of them too.
3. What does a token from an unlisted namespace get today? The **Negative** entry should name that case and the test that shows it.
4. Who else approves this record besides `example-architect`?
5. What are the titles and filenames of ADR-0003, ADR-0004, and ADR-0005? I left placeholders in the links.
6. I wrote A1 and A2 myself because the notes don't list any alternatives. Were these discussed in the meeting?
7. R1 lets the code come from any check the token failed when more than one fails. Should a fixed order decide which code the request gets?
