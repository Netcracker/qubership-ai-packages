## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Treat realm tokens with `ROLE_M2M` and service account tokens as M2M tokens, and let only M2M tokens name any tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title>](<link>): the `sub` and issuer checks that a token passes before R1 and R2 apply (R4 of ADR-0003).
- [ADR-0004: <title>](<link>): the `sub` check (R3) and the namespace check (R5) that the Justification of R2 relies on.

## Context

The service handles two kinds of token in `Authorization`: realm tokens and service account tokens. The architecture
meeting settled which of them are M2M tokens, and which tenants a token that is not M2M may reach.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as an M2M token, and we will let
only an M2M token name any tenant.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 names as M2M.
- **target tenant**: the tenant that a request names in `<tenant source>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` that passes verification is an M2M token when its
  `realm_access.roles` holds `ROLE_M2M`, and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` that passes verification is an M2M token.

#### Which tenants a token may reach

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token gets no `CALLER_TENANT_MISMATCH`,
  whichever tenant is its target tenant.
- **R4** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` when its target tenant is not the tenant of the `tenant-id` claim of that token, or when
  that token has no `tenant-id` claim (O2).

### Justification

A service account token needs no tenant limit (R2), because the `sub` check of ADR-0004 R3 and the namespace check of
ADR-0004 R5 already restrict which service account tokens the service accepts. A token without the role `ROLE_M2M` is
tied to the tenant of its own `tenant-id` claim (R1, R4), so only a caller that holds M2M standing can act across
tenants (R3).

### Alternatives considered

- **A1. Treat a service account token as not M2M, so that it reaches only the tenant of its `tenant-id` claim.**
  Rejected by R2: the checks of ADR-0004 R3 and R5 already limit who can present one.
- **A2. Let a token that is not M2M name another tenant.** Rejected by R4: such a token never reaches another tenant.

## Consequences

Negative:

- A service account token from a listed namespace can name any tenant (R2, R3). A leaked one therefore exposes every
  tenant, and the checks of ADR-0004 R3 and R5 are the only limit.
- A realm token without `ROLE_M2M` is refused for every tenant but its own (R1, R4).

## Open points

- **O1.** Where does a request name its target tenant: a path segment, a header, or a body field? The architect decides.
  It affects R3 and R4.
- **O2.** Assumption: a token that is not M2M and has no `tenant-id` claim reaches no tenant, so it gets the response of
  R4. The architect confirms or changes this. It affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance:

- **O1:** the notes do not say where a request names its tenant. R3 and R4 use the placeholder `<tenant source>` until you tell me.
- **O2:** I assumed that a token that is not M2M and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`. Please confirm.

I left two statements of the notes out of the rules:

- **`legacy` mode:** the case where a service account token gets `TOKEN_ISSUER_UNKNOWN` follows from ADR-0003 R4 and ADR-0004 R1, so a rule would restate them.
- **Non-M2M tokens:** "never reaches another tenant" restates R4.

Questions for you:

- **Owner:** I put `example-architect` as owner. Is that right?
- **Links:** I could not see the titles and filenames of ADR-0003 and ADR-0004, so the Related ADRs entries hold `<title>` and `<link>` placeholders. Please fill them in.
- **Terms:** I defined "realm token" and "service account token" in this record. If an earlier record already owns them, replace the definitions with a pointer to it.
- **Layer:** I tagged R1 to R4 `verify`. If the tenant check runs in `internal/server`, R3 and R4 need the `server` tag.
- **Existing behavior:** what does a token that is not M2M get today when it names another tenant? If the answer differs from R4, Consequences needs a Negative entry for that case.

The README guide needs no change, because the record adds no new paths. The code change that implements these rules ends its commit message and pull request description with `Implements: ADR-0007 R1, R2, R3, R4`.

## Request 2

### File: docs/adr/0007-token-verification-failure-response.md

````markdown
# Reject a token that fails verification with HTTP 401 and the code of the failed check before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title>](<link>): the `TOKEN_ISSUER_UNKNOWN` check (R4) and the `TOKEN_KEYS_UNAVAILABLE` outcome (R9) that R2 covers.
- [ADR-0004: <title>](<link>): the `sub` check (R3) and the namespace check (R5) that R2 covers.
- [ADR-0005: <title>](<link>): the response to `TOKEN_KEYS_UNAVAILABLE` (R2) that R2 of this record uses.

## Context

The service checks the token of each request before policy evaluation. Existing records give some checks their own
HTTP status and error code, such as the issuer check of ADR-0003 R4 and the `sub` check of ADR-0004 R3. The namespace
check of ADR-0004 R5 names no status or code. No record states one response for every check.

## Decision

We will answer a request whose token fails a verification check with HTTP 401 and the error code of that check, before
policy evaluation, except where the token gets `TOKEN_KEYS_UNAVAILABLE`.

### Terms

- **verification check**: a check that the service runs on a token in `Authorization` before policy evaluation, and
  whose failure rejects the token. The outcome `TOKEN_KEYS_UNAVAILABLE` is the failure of one such check.

### Rules

#### Response to a failed check

- **R1** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails a verification
  check.
- **R2** (`verify`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with the error
  code of the check that failed. A request whose token gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2
  instead (O1).

### Justification

A client that gets HTTP 401 with the error code of the failed check can tell which part of its token to correct (R2).
A request whose token gets `TOKEN_KEYS_UNAVAILABLE` fails because the service has no keys, not because of the token,
so the client has to retry. It therefore gets the response of ADR-0005 R2 and not a 401 (R2). Stopping every failed
request before policy evaluation keeps an unverified token out of it (R1).

### Alternatives considered

- **A1. Answer HTTP 401 for `TOKEN_KEYS_UNAVAILABLE` too.** Rejected by R2: a 401 tells the client that its token is
  wrong, so the client does not retry.
- **A2. Answer one generic HTTP 401 for every failed check.** Rejected by R2: the client cannot tell which check
  failed.

## Consequences

Positive:

- A client tells a rejected token (HTTP 401) from a temporary lack of keys (the response of ADR-0005 R2).

Negative:

- Every verification check needs its own error code (R2). The namespace check of ADR-0004 R5 has none in the records
  yet (O1).

## Open points

- **O1.** Which error code does the namespace check of ADR-0004 R5 give, and does any other verification check lack an
  error code? The architect decides. It affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. One open point blocks acceptance:

- **O1:** the notes say the response carries "the code of the check that failed". ADR-0004 R5, the namespace check, names no code in the records I have. Which code should it give? If other checks have no code either, please list them.

I put the exception for `TOKEN_KEYS_UNAVAILABLE` inside R2. ADR-0005 R2 already fixes that response, so R2 only cites it.

Questions for you:

- **Owner:** I put `example-architect` as owner. Is that right?
- **Links:** I could not see the titles and filenames of ADR-0003, ADR-0004, and ADR-0005, so the Related ADRs entries hold `<title>` and `<link>` placeholders. Please fill them in.
- **Layers:** I tagged R1 `server` because it is about ordering before policy evaluation, and R2 `verify`. Please correct the tags if the code sits elsewhere.
- **Existing behavior:** what does a request that fails the namespace check get today? If it is not a 401, Consequences needs a Negative entry for that case, with the test that shows it.

The README guide needs no change. The code change that implements these rules ends its commit message and pull request description with `Implements: ADR-0007 R1, R2`.
