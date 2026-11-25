## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let an M2M token name any tenant and keep every other token to its own tenant

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003](0003-placeholder.md): the unknown-issuer refusal (R4), which a service account token gets in the mode `legacy`.
- [ADR-0004](0004-placeholder.md): the providers of each mode (R1), the subject check of a service account token (R3), and its namespace check (R5).
- [example/platform ADR-0012](https://github.com/example/platform): the audience of the service account tokens that platform services request (R3).

## Context

The service accepts two kinds of token in `Authorization`, a realm token and a service account token. A caller
reaches a tenant by naming it in the request. The service has to decide which tokens may name any tenant, and which
tokens are limited to one.

A service account token passes two checks before this decision applies: the subject check and the namespace check of
ADR-0004. The platform sets the audience of every service account token that one of its services requests, in
example/platform ADR-0012 R3.

## Decision

We will treat a realm token that holds the role `ROLE_M2M` and every service account token as an M2M token. An M2M
token may name any tenant, and every other token is limited to the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token is one.
- **target tenant**: the tenant that a request addresses, as `<source of the target tenant>` defines. O1 asks for it.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its `realm_access.roles` holds `ROLE_M2M`,
  and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Which tenants a token may reach

- **R3** (`server`). A request whose token in `Authorization` is an M2M token may name any tenant as its target
  tenant.
- **R4** (`server`). A request whose token in `Authorization` is not an M2M token, and whose target tenant is not the
  tenant of the `tenant-id` claim of that token, gets HTTP 403 with `CALLER_TENANT_MISMATCH`.

### Justification

A service account token may reach any tenant (R2, R3) because the subject check and the namespace check of ADR-0004
limit who can hold one, and because the platform sets the audience of the service account tokens that its services
request. A realm token proves the same trust only through the role `ROLE_M2M` (R1). Every other token stays in its own
tenant, so a token that is not M2M never reaches another tenant (R4).

## Consequences

Negative:

- Any service account token that passes the checks of ADR-0004 may name any tenant (R2, R3). The record relies on
  those checks and on the platform's audience rule, and O2 asks whether `token-gate` also checks the audience.
- In the mode `legacy`, a service account token is never M2M, because the unknown-issuer refusal of ADR-0003 stops it
  and that mode has no provider for it (ADR-0004 R1).
- A request whose token is not M2M and that names another tenant gets `CALLER_TENANT_MISMATCH` (R4).

## Open points

- **O1.** How a request names its target tenant (a path segment, a header, or a body field), which fills the placeholder
  in the term **target tenant**. The architect decides. It affects R3 and R4.
- **O2.** Whether `token-gate` must check that a service account token carries the audience `netcracker` before R2
  makes it an M2M token. The platform rule governs the tokens that platform services request, and no rule of ADR-0004
  makes `token-gate` check the audience. The answers are to rely on the platform rule alone, or to add a rule to this
  record. The architect decides. It affects R2.
- **O3.** Assumption: a token that is not M2M and has no `tenant-id` claim reaches no tenant, so R4 gives it
  `CALLER_TENANT_MISMATCH`. The architect confirms it. It affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance:

- **O1:** the notes don't say how a request names its target tenant. The rules use a placeholder for it.
- **O2:** the safety argument for service account tokens rests on example/platform ADR-0012 R3. That rule covers the tokens platform services request. Nothing in ADR-0004 makes `token-gate` check the audience. Decide whether to rely on the platform alone or to add an audience rule to this record.
- **O3:** I assumed that a non-M2M token with no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`. Please confirm.

What I left out of the record or couldn't fill in:

- I wrote no rule for "in `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`". ADR-0003 R4 and ADR-0004 R1 already settle it, so it appears as a consequence.
- The notes give no rejected alternative, so the record has no **Alternatives considered** section. Tell me if the meeting rejected a design.
- Please give me the owner's GitHub account, which I left as a placeholder.
- I copied the metadata block from the template, because I couldn't read the existing records. Check it against 0001 to 0006. The same goes for the links to ADR-0003 and ADR-0004, where `0003-placeholder.md` and `0004-placeholder.md` need their real filenames. The link to example/platform points at the repository root. Replace it with the link to ADR-0012.
- The layer tags are my guess. I tagged R1 and R2 `verify`, because they read token claims, and R3 and R4 `server`, because they produce the HTTP response. Please confirm them.

No existing record changes.

## Request 2

### File: docs/adr/0007-refuse-unverified-tokens-before-policy-evaluation.md

````markdown
# Refuse a token that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Architect, `example-architect`: approves R1.

### Related ADRs

- [ADR-0003](0003-placeholder.md): the unknown-issuer refusal (R4) and the keys-unavailable outcome (R9) are checks under R1.
- [ADR-0004](0004-placeholder.md): the subject check (R3) is a check under R1.
- [ADR-0005](0005-placeholder.md): the keys-unavailable response (R2), which R1 uses as its exception.

## Context

The accepted records give some checks a response of their own, such as the unknown issuer in ADR-0003 R4 and the
invalid subject in ADR-0004 R3. A client that sends a token in `Authorization` has to learn from the response which
check failed. A client also has to know whether to retry. A token whose provider has had no keys since the start fails
for a reason that lies with the service, not with the token.

## Decision

We will refuse every token that fails a verification check with HTTP 401 and the code of that check, before policy
evaluation. The one exception is a token that gets `TOKEN_KEYS_UNAVAILABLE`, whose request gets the keys-unavailable
response of ADR-0005, so that the client retries.

### Terms

- **verification check**: a check in the layer `verify` or `keys` that a token in `Authorization` must pass and that
  names an error code for the token that fails it.

### Rules

#### Response to a failed verification check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with
  the error code of that check, and policy evaluation does not run for the request. The exception is a token that gets
  `TOKEN_KEYS_UNAVAILABLE`: its request gets the response of the keys-unavailable rule of ADR-0005 R2 and no HTTP 401.

### Justification

A client that receives the code of the failed check can tell which check refused its token, and no policy decision is
made on a token that failed verification (R1). A key outage is a fault of the service, so HTTP 401 would tell the client
that its token is bad and that a retry is pointless. The response of the keys-unavailable rule of ADR-0005 lets the
client retry (R1).

### Alternatives considered

- **A1. Return HTTP 401 with `TOKEN_KEYS_UNAVAILABLE` like every other failed check.** Rejected by R1: a client reads a
  401 as a final refusal of its token and does not retry.

## Consequences

Positive:

- A client reads the failed check from the error code of every 401 from token verification.

Negative:

- A client has to handle two kinds of response to a failed verification: the 401 of R1, and the response of the
  keys-unavailable rule for `TOKEN_KEYS_UNAVAILABLE`.

## Open points

- **O1.** Which code a request gets where its token fails more than one verification check. The answers are the code of
  the first failing check in the order that `verify` runs the checks, or the code of a fixed order that this record
  lists. The architect decides. It affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. O1 blocks acceptance: the notes don't say which code a token gets when it fails several checks. Decide between the first failing check in the order `verify` runs them and a fixed order.

I treated the decision as one rule. It repeats part of ADR-0003 R4 and ADR-0004 R3 (a 401 with a specific code) and generalizes them to every verification check. It supersedes neither. The specific rules stay, and nothing in them conflicts with R1. The rule cites ADR-0005 R2 by topic and doesn't restate its status code or its `Retry-After`.

Other points to settle:

- Please give me the owner's GitHub account, which I left as a placeholder.
- The layer tags `verify` and `server` are my guess, because I couldn't read the code. Please confirm them.
- I copied the metadata block from the template, because I couldn't read the existing records. Check it against 0001 to 0006. The links to ADR-0003, ADR-0004, and ADR-0005 use `0003-placeholder.md`, `0004-placeholder.md`, and `0005-placeholder.md`, which need the real filenames.
- I assumed the term **verification check** covers checks in `verify` and `keys`. Please confirm that no other layer produces a token error code.

No existing record changes.
