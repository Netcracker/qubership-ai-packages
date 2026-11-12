## Request 1

### File: docs/adr/0007-m2m-tokens-name-any-tenant.md

````markdown
# Let an M2M token name any tenant and bind every other token to its own tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003](0003-token-verification.md): R4 gives a token whose provider is unknown the code `TOKEN_ISSUER_UNKNOWN`.
- [ADR-0004](0004-service-account-tokens.md): R1 fixes which providers the mode allows, and R3 and R5 limit which service account tokens pass verification.

## Context

The service checks the token in `Authorization` of each request before policy evaluation. It accepts two kinds of
token: a realm token and a service account token.

ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`, and ADR-0004 R5
accepts a service account token only from a namespace that the topology file lists.

In the mode `legacy`, the providers file holds no provider of service account tokens (ADR-0004 R1). A service account
token therefore gets `TOKEN_ISSUER_UNKNOWN` (ADR-0003 R4), so R2 applies only in the mode `k8s`.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. An M2M
token may name any tenant, and every other token may reach only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **requested tenant**: the tenant that a request names in `<tenant source>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` that passes verification is an M2M token where its
  `realm_access.roles` claim holds `ROLE_M2M`, and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` that passes verification is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token is not refused because of its requested
  tenant, whichever tenant that is.
- **R4** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` where its requested tenant differs from the `tenant-id` claim of that token, or where that
  token has no `tenant-id` claim.

### Justification

ADR-0004 R3 and R5 already limit which service account tokens pass verification, so treating every one that passes as an
M2M token is safe (R2). A token that is not M2M never reaches a tenant other than its own (R4).

### Alternatives considered

- **A1. Let every token name any tenant.** Rejected by R4: a token that is not M2M would then reach tenants other than
  its own.

## Consequences

Negative:

- A realm token with `ROLE_M2M`, and every service account token that passes verification, may name any tenant, and the
  tenant check adds no limit for them (R1 to R3).

## Open points

- **O1.** Where does a request name its tenant, such as in the path, a header, or the body? `@example-architect` decides.
  It affects R3 and R4, and the term **requested tenant**.
- **O2.** Assumption: a token that is not M2M and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH` (R4). The
  alternative is another status or code. `@example-architect` decides. It affects R4.
- **O3.** Assumption: the tenant check lives in `verify`. The alternative is `server`, because the requested tenant
  belongs to the request and not to the token. `@example-architect` decides. It affects the layer tag of R1 to R4.
````

### Message to the user

The record is `Proposed`, because three open points block acceptance:

- **O1:** where a request names its tenant. The notes don't say, so the term holds the placeholder `<tenant source>`.
- **O2:** what happens to a token that is not M2M and has no `tenant-id` claim. I assumed `CALLER_TENANT_MISMATCH`.
- **O3:** the layer tag. I assumed `verify`.

What I left out or changed:

- **The `legacy` case has no rule.** ADR-0003 R4 and ADR-0004 R1 already give a service account token `TOKEN_ISSUER_UNKNOWN` in that mode. I recorded it as a fact in Context.
- **The "never reaches another tenant" line has no rule of its own.** It repeats R4, so I put it in the Justification.
- **A1 is the only alternative.** The notes name no other. Tell me if the meeting rejected others.

Two questions:

1. Does any approver besides `@example-architect` need listing under Participants and approvers?
2. Do callers whose token is not M2M and who name another tenant get through today? If so, they get 403 after this change. I would then add a rule for what an existing installation gets on upgrade, and cite it under Negative.

The record needs no change to the reading guide, since it adds no path or layer.

## Request 2

### File: docs/adr/0007-failed-token-verification-gets-401-before-policy-evaluation.md

````markdown
# Give a token that fails verification an HTTP 401 with the code of the failed check before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003](0003-token-verification.md): R4 and R9 give codes to two failed checks, and R1 below is consistent with both.
- [ADR-0004](0004-service-account-tokens.md): R3 gives a code to a failed check, and R5 states no code (O1).
- [ADR-0005](0005-error-responses.md): R2 states the response that R1 below names as its exception.

## Context

The service checks the token in `Authorization` of each request before policy evaluation. Accepted records give a
status and a code to some failed checks: ADR-0003 R4 gives HTTP 401 with `TOKEN_ISSUER_UNKNOWN`, ADR-0004 R3 gives HTTP
401 with `TOKEN_SUBJECT_INVALID`, and ADR-0003 R9 gives `TOKEN_KEYS_UNAVAILABLE`, which ADR-0005 R2 turns into HTTP 503
with `Retry-After: 5`. ADR-0004 R5 refuses a token from a namespace that the topology file does not list, and states no
status and no code for it.

## Decision

We will answer every token in `Authorization` that fails verification with HTTP 401 and the code of the failed check,
and never evaluate policy for it, except that a token which gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005
R2, so that the client retries.

### Terms

- **fails verification**: a token in `Authorization` fails verification when a check in `verify` or `keys` refuses it
  with a code, `TOKEN_KEYS_UNAVAILABLE` included.

### Rules

#### Response to a failed verification

- **R1** (`verify`, `server`). A token in `Authorization` that fails verification gets HTTP 401 with the code of the
  check that failed. Where the code is `TOKEN_KEYS_UNAVAILABLE`, the request gets the response that ADR-0005 R2 states
  and no HTTP 401.
- **R2** (`verify`, `server`). A request whose token in `Authorization` fails verification, with any code, reaches no
  policy evaluation.

### Justification

A client that gets `TOKEN_KEYS_UNAVAILABLE` has a valid token that the service cannot check for now. An HTTP 401 would
tell the client to replace the token, so that code gets the response of ADR-0005 R2 and the client retries (R1).

### Alternatives considered

- **A1. Give `TOKEN_KEYS_UNAVAILABLE` an HTTP 401 like every other failed check.** Rejected by R1: the client would
  replace a valid token and not retry.

## Consequences

Negative:

- A check that states no code, such as the namespace check of ADR-0004 R5, cannot meet R1 until it has one (O1).

## Open points

- **O1.** Which code does each check have that no accepted record gives a code, such as the namespace check of ADR-0004
  R5? `@example-architect` decides. It affects R1.
````

### Message to the user

The record is `Proposed`, because O1 blocks acceptance. ADR-0004 R5 states no status and no code, so R1 can't name the code of that check yet. Please name the code for it and for any other check without one. I did not invent them.

Most of the notes restate accepted rules:

- **The 401s:** ADR-0003 R4 and ADR-0004 R3 already give the 401 with a code for two checks.
- **The exception:** ADR-0003 R9 and ADR-0005 R2 already give the `TOKEN_KEYS_UNAVAILABLE` response.

The record cites ADR-0005 R2 and does not restate it. The new content is the general rule R1, which covers every failed check, and R2, which fixes the order before policy evaluation.

The accepted records stay as they are, since R1 changes none of their rules.

Three more points:

- **Layer tags:** R1 and R2 carry both `verify` and `server`. I assumed `verify` produces the code and `server` maps it to the response, as ADR-0005 R2 does for the 503. Correct me if the code differs.
- **Missing `Authorization`:** the notes cover only "a token in `Authorization`", so a request with no token is out of scope. Say if it belongs in this record.
- **Justification:** it explains only R1, because the notes give no reason for R2. Add one if the meeting gave it.

Also confirm that `@example-architect` is the only approver.
