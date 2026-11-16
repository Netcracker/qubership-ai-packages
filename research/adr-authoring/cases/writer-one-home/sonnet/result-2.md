## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Treat realm tokens with `ROLE_M2M` and all service account tokens as M2M tokens, and let only M2M tokens name any tenant

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- ADR-0003: the `TOKEN_ISSUER_UNKNOWN` response of ADR-0003 R4, cited in **Context**.
- ADR-0004: the providers file of ADR-0004 R1, and the checks of ADR-0004 R3 and ADR-0004 R5, cited in **Context** and
  **Justification**.

## Context

The service checks the token in `Authorization` of each request before policy evaluation. Two kinds of token reach it:
realm tokens and service account tokens. Some callers are machines that act for several tenants, and the other callers
act for one tenant.

In the mode `legacy` of the setting `M2M_AUTH_MODE`, the providers file holds no provider of service account tokens
(ADR-0004 R1). A service account token therefore gets HTTP 401 with `TOKEN_ISSUER_UNKNOWN` in that mode (ADR-0003 R4),
and no service account token is an M2M token there.

## Decision

We will treat a realm token that holds `ROLE_M2M`, and every service account token, as an M2M token. A request may name
a tenant other than the one in the `tenant-id` claim of its token only where that token is an M2M token.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **requested tenant**: the tenant that a request names, taken from `<source of the requested tenant>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its `realm_access.roles` holds `ROLE_M2M`,
  and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token may name any tenant. A request whose token
  is not an M2M token, and whose requested tenant differs from the value of the `tenant-id` claim of that token, gets
  HTTP 403 with `CALLER_TENANT_MISMATCH`; a token with no `tenant-id` claim differs from every requested tenant. Where
  the token fails a check of `verify`, the request gets the response of that check instead.

### Justification

A service account token needs no role check to count as an M2M token. ADR-0004 R3 refuses a service account token whose
`sub` does not start with `system:serviceaccount:`, and ADR-0004 R5 accepts one only from a namespace that the topology
file lists (R2). A realm token carries no such restriction, so it needs the explicit `ROLE_M2M` (R1). A token that is
not an M2M token stays within the tenant of its own `tenant-id` claim (R3).

## Consequences

Negative:

- A service account token from a listed namespace may name any tenant (R2, R3). Its tenant isolation rests on the
  checks of ADR-0004 R3 and ADR-0004 R5.
- A caller whose token is not an M2M token, and whose request names another tenant, gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` (R3).
- Anyone who can give a realm token the role `ROLE_M2M` can give that token access to every tenant (R1, R3).

## Open points

- **O1.** The notes do not say where a request names its tenant, such as the path, a header, or the body. The architect
  decides. It sets the value of **requested tenant** and affects R3.
- **O2.** Assumption: a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH` for
  every requested tenant. The architect confirms or names another outcome. It affects R3.
- **O3.** Assumption: the tenant check of R3 is part of `verify`, because it reads the claims of the token. If it
  belongs to `server`, the layer tag of R3 changes. The architect decides.
````

### Message to the user

I drafted ADR-0007 as `Proposed`. Open points O1 to O3 block acceptance.

- **Owner:** I left `<owner GitHub account>` in the record. Who is the owner? Is it you, or `example-architect`?
- **O1:** The notes don't say where a request names its tenant. The record has a visible placeholder in **Terms** for that.
- **O2 and O3:** These are assumptions. A non-M2M token with no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`, and the tenant check sits in `verify`.
- **Legacy mode:** The `TOKEN_ISSUER_UNKNOWN` sentence is not a rule. ADR-0004 R1 and ADR-0003 R4 already produce that outcome, so the record states it once as a fact in **Context**.
- **Links:** I couldn't see the filenames of ADR-0003 and ADR-0004. **Related ADRs** therefore lists them without links. Please add the links.
- **Terms:** The record defines "realm token" and "service account token" from your facts. If an existing record already owns either word, replace the definition with a pointer to it.
- **Existing records:** No accepted record needs an edit. The README layer map is unchanged.

## Request 2

### File: docs/adr/0007-reject-failed-token-checks-with-401-before-policy-evaluation.md

````markdown
# Reject a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- ADR-0003: the response of ADR-0003 R4 for an unknown issuer, cited in **Context**.
- ADR-0004: the responses and checks of ADR-0004 R3 and ADR-0004 R5, cited in **Context**; this record adds a requirement
  for the case of ADR-0004 R5 once O2 is answered.
- ADR-0005: the response of ADR-0005 R2 for a token whose keys are unavailable, used in R1.

## Context

The service checks the token in `Authorization` of each request before policy evaluation. Existing records give a
response to some failed checks: ADR-0003 R4 and ADR-0004 R3 each give HTTP 401 with the code of their check. ADR-0005 R2
gives a token whose keys are unavailable a response that tells the client to retry. ADR-0004 R5 names no response and
no code for a namespace that the topology file does not list. No record states the response for the other checks, or
states that policy evaluation does not run after a failed check.

## Decision

We will answer a request whose token in `Authorization` fails a verification check with HTTP 401 and the code of that
check, and run no policy evaluation for it. A token whose keys are unavailable gets the response of ADR-0005 R2
instead, so that the client retries.

### Terms

- **verification check**: a check that the layers `verify` and `keys` make on a token in `Authorization` and that has
  its own error code, for example `TOKEN_ISSUER_UNKNOWN`, `TOKEN_SUBJECT_INVALID`, and `TOKEN_KEYS_UNAVAILABLE`.

### Rules

#### Response to a failed check

- **R1** (`verify`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with the error
  code of the check that failed. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

#### Policy evaluation

- **R2** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails a verification
  check, including a token that gets `TOKEN_KEYS_UNAVAILABLE`.

### Justification

A client that receives the code of the failed check can tell which check failed, and 401 tells it that the token is
refused (R1). A missing key set is a temporary condition and not a fault of the token, so that case gets the response
that makes the client retry (R1). Policy evaluation decides on the claims of a token, so it runs only on a token that
passed every verification check (R2).

### Alternatives considered

- **A1. Give every failed check HTTP 401, including `TOKEN_KEYS_UNAVAILABLE`.** Rejected by R1: a 401 tells the client
  that the token is refused, so it does not retry, although a later request can succeed once the keys are available.

## Consequences

Positive:

- A client gets the code of the failed check for every verification check, including a check that a later record adds.

Negative:

- A verification check added later gets HTTP 401 under R1. A check whose failure is temporary needs a rule of its own
  that excepts it from R1.
- The namespace check of ADR-0004 R5 has no error code, so it is not a verification check and R1 gives its failure no
  response until O2 is answered.

Follow-ups:

- When O2 is answered, state the code of the namespace check in a record that replaces ADR-0004 R5.

## Open points

- **O1.** Assumption: R2 also applies to a token that gets `TOKEN_KEYS_UNAVAILABLE`, because the response of ADR-0005 R2
  ends the request. The architect confirms or names another outcome. It affects R2.
- **O2.** ADR-0004 R5 names no error code for a token from a namespace that the topology file does not list. The
  architect names a code, or decides that the check has no code and names its response. It affects R1 and R2.
- **O3.** The notes do not say which code a token gets when it fails more than one verification check. The architect
  decides, for example the check that runs first. It affects R1.
- **O4.** Assumption: the ordering of R2 belongs to `server`, which calls policy evaluation. If another layer calls it,
  the layer tag of R2 changes. The architect decides.
````

### Message to the user

I drafted ADR-0007 as `Proposed`. Open points O1 to O4 block acceptance.

- **Owner:** I left `<owner GitHub account>` in the record. Who is the owner? Is it you, or `example-architect`?
- **O2:** ADR-0004 R5 names no error code for a namespace that the topology file doesn't list. R1 covers only checks that have a code, and I did not invent one. Which code should it get? Because ADR-0004 is accepted, the code needs a later record that replaces R5 whole. I listed that as a follow-up.
- **O1, O3, O4:** O1 and O4 are assumptions. R2 covers the `TOKEN_KEYS_UNAVAILABLE` case too, and policy evaluation is called from `server`. O3 asks which code wins when a token fails more than one check.
- **Overlap with existing rules:** ADR-0003 R4 and ADR-0004 R3 already give 401 with their codes. R1 is the general rule for every check with a code, so the overlap is consistent and I left those records unchanged. If you want a single home for the status, I can draft records that replace those parts.
- **Links:** **Related ADRs** lists ADR-0003, ADR-0004, and ADR-0005 without links, because I couldn't see their filenames. Please add the links.
- **Existing records:** No accepted record needs an edit now. The README layer map is unchanged.
