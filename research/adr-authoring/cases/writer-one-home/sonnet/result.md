## Request 1

### File: docs/adr/0007-treat-realm-and-service-account-tokens-as-m2m-and-limit-other-tokens-to-their-own-tenant.md

````markdown
# Treat realm tokens with ROLE_M2M and all service account tokens as M2M tokens, and let only M2M tokens name any tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0004: <title>](<link>): the `sub` check of R3 and the namespace check of R5 bound who can hold a service account token (see Justification).

## Context

token-gate checks the token of each request before policy evaluation. Two kinds of token reach it: realm tokens, which
Keycloak signs, and service account tokens, which the Kubernetes API server signs. The setting `M2M_AUTH_MODE` takes
`legacy` or `k8s`. Until now no record says which of these tokens come from a machine caller, or which tenants a caller
may reach.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as an M2M token, let only an M2M
token name any tenant, and refuse any other tenant to a token that is not M2M.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **named tenant**: the tenant that a request addresses, as `<tenant source>` gives it (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token is an M2M token when its `realm_access.roles` holds `ROLE_M2M`, and is not an M2M
  token otherwise.
- **R2** (`verify`). A service account token is an M2M token.

#### Tenant access

- **R3** (`server`). A request whose token in `Authorization` has passed the `verify` layer and is an M2M token may name
  any tenant, and the tenant check does not give it `CALLER_TENANT_MISMATCH`.
- **R4** (`server`). A request whose token in `Authorization` has passed the `verify` layer and is not an M2M token gets
  HTTP 403 with `CALLER_TENANT_MISMATCH` when its named tenant differs from the value of the `tenant-id` claim of the
  token, or when the token has no `tenant-id` claim.

### Justification

A service account token needs no further condition to count as M2M, because the `sub` check of ADR-0004 R3 and the
namespace check of ADR-0004 R5 already limit who can hold one (R2). A realm token already carries its roles in
`realm_access.roles`, so R1 adds no new claim. An M2M token acts for a machine and not for one tenant, so it may name
any tenant (R3). Every other token stays inside the tenant of its own `tenant-id` claim (R4).

### Alternatives considered

- **A1. Let a token that is not M2M name a tenant other than its own.** Rejected by R4: the architect decided that a
  token that is not M2M never reaches another tenant.

## Consequences

Negative:

- A service account token from a namespace that the topology file lists may name any tenant (R2, R3).

## Open points

- **O1.** How a request names its tenant, such as a path segment, a header, or a body field, and which component reads
  it. The architect decides. It affects R3 and R4, and the layer tag of both.
- **O2.** Assumption: a token that is not M2M and has no `tenant-id` claim gets the response of R4, since every tenant
  differs from a missing one. The architect confirms or names another outcome. It affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, because two open points block acceptance:

- **O1.** The notes don't say how a request names its tenant. R3 and R4 use the placeholder `<tenant source>`, and I tagged both rules `server` on the assumption that this layer reads it.
- **O2.** The notes don't cover a token that is not M2M and has no `tenant-id` claim. R4 refuses it, and I recorded that as an assumption for the architect to confirm.

I left out the note that a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy`. ADR-0004 R1 and ADR-0003 R4 already produce that result together, and restating it would drift from them.

Placeholders and assumptions to check:

- **Related ADRs:** the title and link of ADR-0004 are placeholders, because I could not see the record's filename.
- **Owner and approver:** I set `example-architect` for both. Tell me if the owner should be someone else.
- **Terms:** I defined "realm token" and "service account token" here from the repository facts. If an earlier record already owns them, replace them with a pointer to that record.

No accepted record changes. Nothing else changes either, including the guide: there is no code yet, so the record has no **Confirmation** entries.

## Request 2

### File: docs/adr/0007-reject-a-token-that-fails-verification-before-policy-evaluation.md

````markdown
# Reject a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0005: <title>](<link>): R2 gives the response for a token that gets `TOKEN_KEYS_UNAVAILABLE`, and R2 of this record points at it.
- [ADR-0003: <title>](<link>): R4 and R9 name codes of checks that R2 of this record covers.
- [ADR-0004: <title>](<link>): R3 and R5 are checks that R2 of this record covers.

## Context

token-gate checks the token of each request before policy evaluation. Several accepted rules already give a failing
token its response: the `iss` check of ADR-0003 R4 and the `sub` check of ADR-0004 R3 give HTTP 401 with a code, and
ADR-0005 R2 gives the response for `TOKEN_KEYS_UNAVAILABLE`. The namespace check of ADR-0004 R5 names no status and no
code. No accepted rule says that a failing token never reaches policy evaluation, or what status a failing check gets
where its rule names none.

## Decision

We will reject a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed,
before policy evaluation, except that a token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2
instead, so that the client retries.

### Terms

- **verification**: the checks that the `verify` layer and the `keys` layer apply to a token in `Authorization`. A token
  fails verification when one of these checks refuses it.
- **check code**: the error code that the rule of a check names for a token that the check refuses, such as
  `TOKEN_ISSUER_UNKNOWN`.

### Rules

#### Rejecting a failing token

- **R1** (`server`). Policy evaluation of a request with a token in `Authorization` starts only after the token passes
  verification.
- **R2** (`verify`, `server`). A token in `Authorization` that fails verification gets HTTP 401 with the check code of
  the check that refused it, except a token that gets `TOKEN_KEYS_UNAVAILABLE`, which gets the response of ADR-0005 R2
  instead.

### Justification

Policy evaluation then never decides on the claims of a token that failed a check (R1). The client learns which check
failed from the code, and the status is the same for every failing check unless R2 names an exception (R2). A token
whose provider has no keys fails for a reason that may pass, so the client gets the response that tells it to retry
(R2).

### Alternatives considered

- **A1. Evaluate policy on a token that fails verification.** Rejected by R1: policy would decide on claims that no
  check has confirmed.
- **A2. Give a token that gets `TOKEN_KEYS_UNAVAILABLE` HTTP 401 like any other failing check.** Rejected by the
  exception in R2: the client would not retry.

## Consequences

Negative:

- A token that a check refuses without a check code has no code to return, so R2 cannot give its case a result until
  O1 is settled.

Follow-ups:

- When O1 is settled, update ADR-0004 or add a record that names the code for the namespace check of ADR-0004 R5.

## Open points

- **O1.** The code that a token gets when the namespace check of ADR-0004 R5 refuses it, because R5 names none. Answers:
  a new code, `<code>`, named in a record that the architect approves, or an existing code. The architect decides. It
  affects R2.
- **O2.** Which check code a token gets when more than one check would refuse it. Answers: the first check in the
  order that the `verify` and `keys` layers run, with the order named in a rule, or no defined order. The architect
  decides. It affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`, with two open points that block acceptance.

Most of the notes are already settled by accepted records:

- ADR-0003 R4 and ADR-0004 R3 already give HTTP 401 with a code.
- ADR-0003 R9 and ADR-0005 R2 already give the `TOKEN_KEYS_UNAVAILABLE` response.

So the record states only what no rule settles yet:

- **R1:** a failing token never reaches policy evaluation.
- **R2:** a general rule that a failing check gets 401 with its code, with the ADR-0005 R2 exception. The exception has to be in R2, because the general rule would otherwise give `TOKEN_KEYS_UNAVAILABLE` a 401.

Open points:

- **O1.** ADR-0004 R5 names no error code. What code does a token from an unlisted namespace get? The architect decides.
- **O2.** The notes don't say which code wins when two checks would both refuse a token. The architect decides.

Other things to check:

- **Related ADRs:** the titles and links are placeholders, because I could not see the filenames.
- **Owner and approver:** I set `example-architect` for both. Tell me if the owner should be someone else.
- **Layer tags:** I tagged R2 `verify` and `server` because the check code comes from `verify` and the status from `server`. I could not check this against code.

No accepted record changes. Nothing else changes either, including the guide, and the record has no **Confirmation** entries because no check exists yet.
