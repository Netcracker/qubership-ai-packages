## Request 1

### File: docs/adr/0007-let-only-m2m-tokens-reach-other-tenants.md

````markdown
# Let only M2M tokens reach a tenant other than the tenant in their `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): the issuer check of ADR-0003 R4, which **Context** cites for the
  mode `legacy`.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the `sub` check of ADR-0004 R3 and the namespace check of ADR-0004
  R5, on which R2 relies, and the providers rule of ADR-0004 R1, which **Context** cites for the mode `legacy`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. That token is a realm token
or a service account token, and `M2M_AUTH_MODE` takes `legacy` or `k8s`. A realm token carries its roles in
`realm_access.roles`, and a token carries its tenant in the claim `tenant-id`. No accepted record states which tokens
are M2M tokens, or which tenants a token may reach.

In the mode `legacy`, a service account token gets `TOKEN_ISSUER_UNKNOWN` through the providers rule of ADR-0004 R1 and
the issuer check of ADR-0003 R4. This record adds no rule for that case.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as M2M tokens. A token that is not
an M2M token will reach only the tenant in its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token in `Authorization` is an
  M2M token.
- **passes verification**: a token in `Authorization` passes verification when `verify` and `keys` give it none of the
  error codes that the rules of ADR-0003 and ADR-0004 state.
- **requested tenant**: the tenant that a request names in `<where a request names its tenant>`.
- **own tenant**: the tenant that the `tenant-id` claim of a token in `Authorization` names. A token without a
  `tenant-id` claim has no own tenant.

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its claim `realm_access.roles` holds
  `ROLE_M2M`. Otherwise it is not an M2M token.
- **R2** (`verify`). Every service account token in `Authorization` is an M2M token. ADR-0004 R3 refuses one whose
  `sub` does not start with `system:serviceaccount:`.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` passes verification and is not an M2M token gets HTTP 403
  with `CALLER_TENANT_MISMATCH` when the token has no own tenant, or when its own tenant is not the requested tenant. A
  request whose token in `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`, whatever the requested
  tenant is.

### Implementation notes

Adds no requirement. Let `internal/verify` decide whether a token that passes verification is an M2M token, and return
that result with the claims. The tenant check can then read one value instead of reading `realm_access.roles` again.

### Justification

A service account token needs no role to be an M2M token, because the `sub` check of ADR-0004 R3 and the namespace check
of ADR-0004 R5 already limit which service account tokens pass verification (R2). A realm token becomes an M2M token
only through a role that Keycloak grants, so the realm's administrators decide which clients may reach every tenant
(R1). A token that is not an M2M token stays in its own tenant, so a token from one tenant gives no access to another
tenant (R3).

### Alternatives considered

- **A1. Require `ROLE_M2M` in `realm_access.roles` of a service account token.** Rejected by R2: the Kubernetes API
  server puts no `realm_access` claim into a service account token, so no service account token could be an M2M token.
- **A2. Let every token name any tenant, and leave the tenant check to policy evaluation.** Rejected by R3: every
  policy would then have to keep a token that is not an M2M token in its own tenant.

## Consequences

Negative:

- A client that sends a token without `ROLE_M2M` to several tenants gets HTTP 403 for every tenant but its own (R3). It
  needs a token with `ROLE_M2M`.
- Anyone who can grant `ROLE_M2M` in a Keycloak realm can issue a token that reaches every tenant (R1).
- Every service account token that passes the namespace check of ADR-0004 R5 reaches every tenant (R2).

## Open points

- **O1.** Where does a request name its tenant? Possible answers are a header, a path segment, or a field of the
  request body. The answer replaces the placeholder in **requested tenant**. `example-architect` decides. Affects R3.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`
  for every requested tenant. The other answer is HTTP 401 with an error code of `verify`. `example-architect` decides.
  Affects R3.
- **O3.** No rule covers a request that names no tenant. Possible answers: a token that is not an M2M token gets
  `CALLER_TENANT_MISMATCH`, or the request goes on to policy evaluation. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It can't be accepted until O1 to O3 are answered:

- **O1:** Where does a request name its tenant? R3 has a placeholder until you tell me.
- **O2:** R3 assumes that a token that is not M2M and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`. Is that right?
- **O3:** What happens to a request that names no tenant?

Two items from the notes are not rules:

- **Service account tokens in the mode `legacy`:** they already get `TOKEN_ISSUER_UNKNOWN` through ADR-0004 R1 and ADR-0003 R4. A rule here would only repeat those, so the record mentions it in Context.
- **"A token that is not M2M never reaches another tenant":** R3 already says this, so it is not repeated as a rule.

The safety argument for service account tokens is in the Justification. It cites ADR-0004 R3 and R5 without repeating what they require.

Questions:

1. Should `example-architect` be the owner, and should anyone else approve?
2. What are the titles and filenames of ADR-0003 and ADR-0004? The links under **Related ADRs** have placeholders until I have them.
3. The meeting notes list no rejected alternatives. Did the meeting discuss A1 and A2, or other options?
4. Do ADR-0003 or ADR-0004 already define "realm token" and "service account token"? If so, the Terms should point to those definitions.
5. I tagged R3 as `verify`. Should it be `server` instead, if the tenant check will live in `internal/server`?

## Request 2

### File: docs/adr/0007-refuse-a-token-that-fails-verification-with-http-401.md

````markdown
# Refuse a token that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): the issuer check of ADR-0003 R4, and `TOKEN_KEYS_UNAVAILABLE` of
  ADR-0003 R9, which R1 excepts.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the `sub` check of ADR-0004 R3, and the namespace check of ADR-0004
  R5, which R2 gives an error code.
- [ADR-0005: <title of ADR-0005>](0005-<slug>.md): the response of ADR-0005 R2, which R1 gives to a token that gets
  `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The issuer check of ADR-0003 R4
and the `sub` check of ADR-0004 R3 state HTTP 401 and an error code. ADR-0003 R9 states the code
`TOKEN_KEYS_UNAVAILABLE` and no status, and ADR-0005 R2 states the response for that code. The namespace check of
ADR-0004 R5 states neither a status nor an error code.

## Decision

We will refuse a token that fails verification with HTTP 401 and the error code of the failed check before policy
evaluation. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

### Terms

- **check of verification**: a check of a token in `Authorization` that a rule in the layer `verify` or `keys` of an
  accepted record states.
- **fails verification**: a token in `Authorization` fails verification when it fails at least one check of
  verification.

### Rules

#### Response to a failed check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails verification does not reach policy
  evaluation. It gets HTTP 401 with the error code of the first check of verification that the token fails, in the
  order in which `verify` runs the checks. A request whose token gets `TOKEN_KEYS_UNAVAILABLE` gets HTTP 503 with
  `Retry-After: 5` instead of HTTP 401.

#### Error code of the namespace check

- **R2** (`verify`). A service account token in `Authorization` that the namespace check of ADR-0004 R5 does not accept
  gets the error code `<error code of the namespace check>`.

### Implementation notes

Adds no requirement. Let `internal/verify` return the error code of the first failed check. Let `internal/server` map
every code except `TOKEN_KEYS_UNAVAILABLE` to HTTP 401 before it calls policy evaluation.

### Justification

The error code shows a client and an operator which check refused the token (R1, R2). HTTP 401 shows the client that
the token itself is the problem, so sending the same token again gives the same result (R1). `TOKEN_KEYS_UNAVAILABLE`
means that the keys of the token's provider are missing, not that the token is wrong. The response of ADR-0005 R2 makes
the client retry, and a retry can succeed once the keys arrive (R1).

### Alternatives considered

- **A1. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** Rejected by R1: a client that
  gets HTTP 401 does not retry, even after the keys arrive.
- **A2. Pass a token that fails verification to policy evaluation, and let the policy refuse it.** Rejected by R1:
  every policy would then have to handle claims that no check has verified.

## Consequences

Negative:

- Any caller, including one without a valid token, learns from the error code which check its token failed (R1, R2).
- A token that fails several checks gets the code of the first failed check only (R1).

## Open points

- **O1.** Which error code does the namespace check of ADR-0004 R5 give? The meeting named none. The answer replaces
  the placeholder in R2. `example-architect` decides. Affects R2.
- **O2.** R1 assumes that the code comes from the first failed check, in the order in which `verify` runs the checks,
  and leaves that order to the implementer. The other answer is a fixed order of checks that a rule states.
  `example-architect` decides. Affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It can't be accepted until O1 and O2 are answered:

- **O1:** ADR-0004 R5 names no error code, so R2 has a placeholder. Which code should the namespace check give?
- **O2:** When a token fails more than one check, R1 assumes that the response carries the code of the first failed check, in the order `verify` runs the checks. Is that right, or should a rule fix the order?

R1 does not repeat the exception for `TOKEN_KEYS_UNAVAILABLE`. It cites ADR-0005 R2, which already defines that response.

Questions:

1. I could only see the rules of ADR-0003 to ADR-0005 that your notes mention. Does any other rule in 0001 to 0006 give a failing token a status other than HTTP 401? If so, this record replaces that part of the rule and must name it under **Related ADRs**.
2. What should a request with no token in `Authorization` get? The notes don't cover that case, and neither does R1.
3. Should `example-architect` be the owner, and should anyone else approve?
4. What are the titles and filenames of ADR-0003, ADR-0004, and ADR-0005? The links under **Related ADRs** have placeholders until I have them.
5. The meeting notes list no rejected alternatives. Did the meeting discuss A1 and A2?
