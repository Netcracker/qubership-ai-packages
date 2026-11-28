## Request 1

### File: docs/adr/0007-m2m-tokens-may-name-any-tenant.md

````markdown
# Let M2M tokens name any tenant and confine every other token to its own tenant

## Status

Proposed

### Owner

<GitHub account of the owner of this ADR>

### Participants and approvers

- Architect, `example-architect`: approves the decision and R1 to R4.

### Related ADRs

- ADR-0003: R4 gives `TOKEN_ISSUER_UNKNOWN` to a token whose `iss` names no provider. This record relies on it for
  service account tokens in the mode `legacy`.
- ADR-0004: R1 fixes which providers the providers file holds in each `M2M_AUTH_MODE`. R3 and R5 are part of the
  reason R2 of this record is safe.
- ADR-0012 of example/platform: R3 gives every service account token that a service of the platform requests the
  audience `netcracker`. It is part of the reason R2 of this record is safe.

## Context

token-gate checks the token in `Authorization` before policy evaluation. Two kinds of token reach it. Keycloak signs a
realm token for a realm, and the Kubernetes API server signs a service account token for a service account. Some
callers are services, not users, and need to act for any tenant. No record yet says which tokens belong to such callers
or which tenants a token may reach.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as M2M tokens, let an M2M token
name any tenant, and let every other token reach only the tenant of its own `tenant-id` claim.

### Terms

- **verified token**: a token in `Authorization` that no check rejects before policy evaluation, such as ADR-0003 R4
  and R9 and ADR-0004 R3 and R5.
- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a verified token that R1 or R2 makes an M2M token. No other token is an M2M token.
- **requested tenant**: the tenant that a request names. O1 asks how a request names it.
- **own tenant**: the tenant that the `tenant-id` claim of a token names.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A verified realm token is an M2M token when its `realm_access.roles` holds `ROLE_M2M`.
- **R2** (`verify`). A verified service account token is an M2M token.

#### Which tenants a token reaches

- **R3** (`verify`). A request whose token is an M2M token is not refused with `CALLER_TENANT_MISMATCH`, whichever
  tenant the request names.
- **R4** (`verify`). A request whose token is a verified token and not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` when the requested tenant differs from the own tenant of the token, or when the token has no
  `tenant-id` claim.

### Justification

R2 is safe for these reasons. ADR-0004 R3 refuses a service account token whose `sub` does not start with
`system:serviceaccount:`. ADR-0004 R5 accepts a service account token only from a namespace that the topology file
lists. ADR-0012 R3 of example/platform gives every service account token that a service of the platform requests the
audience `netcracker`. O3 asks whether token-gate must check that audience itself.

R1 limits the realm tokens that name any tenant to those that carry the role `ROLE_M2M`. R4 keeps every other token
inside its own tenant.

### Alternatives considered

- **A1. Let every verified token name any tenant.** Rejected by R4: a token that is not an M2M token must never reach
  another tenant.

## Consequences

Negative:

- A verified realm token without `ROLE_M2M` cannot reach another tenant (R4). A caller that needs to must get the role
  in its realm.
- In the mode `legacy`, R2 has no effect. ADR-0004 R1 leaves the providers file without a provider of service account
  tokens, so ADR-0003 R4 gives such a token `TOKEN_ISSUER_UNKNOWN`.

## Open points

- **O1.** How does a request name its tenant: a path segment, a header, a body field, or another way? The architect
  decides. It affects R3 and R4.
- **O2.** This record assumes that a verified token that is not an M2M token and has no `tenant-id` claim reaches no
  tenant, so R4 refuses it. The architect confirms or changes this. It affects R4.
- **O3.** ADR-0012 R3 of example/platform binds the platform's services when they request a token. No rule of
  token-gate requires the audience `netcracker`. Either R2 stays as written and relies on ADR-0004 R5 and the platform
  rule, or a rule of `verify` requires the audience on a service account token. The architect decides. It affects R2.
````

### Message to the user

I wrote the record as `Proposed`, because three open points block acceptance. Three things need an answer from you:

- **Owner:** who owns the ADR? I left the placeholder `<GitHub account of the owner of this ADR>` in the record. I listed `example-architect` as approver only.
- **O1:** how does a request name its tenant? R3 and R4 depend on it, and the notes don't say.
- **O3:** the notes call service account tokens safe because ADR-0012 R3 of example/platform gives them the audience `netcracker`. That rule binds the platform's services when they request a token. None of the token-gate rules you gave me checks the audience. So a service account token from a listed namespace with another audience would still be an M2M token. Should token-gate check the audience?

I also made two choices of my own:

- **O2:** I assumed that a non-M2M token with no `tenant-id` claim gets 403.
- **A1:** the notes list no rejected options, so I inferred this one from "a token that is not M2M never reaches another tenant". Please confirm it or remove it.

The legacy-mode note adds no rule. ADR-0004 R1 and ADR-0003 R4 already produce that result, so I recorded it as an accepted consequence.

Some other points about the record:

- **Links:** I cited ADR-0003, ADR-0004, and ADR-0012 without links, because I don't have their filenames. Add the links when you merge.
- **Layer:** I tagged all rules `verify`. If the tenant check lives in `internal/server`, change R3 and R4 to `server`.
- **Confirmation:** the section is empty, because I know of no existing test for these rules.
- **README and existing records:** `docs/adr/README.md` needs no change, and I edited no existing record.
- **Trailers:** the change that implements these rules ends its commit message and pull request description with `Implements: ADR-0007 R1, R2, R3, R4`.

## Request 2

### File: docs/adr/0007-reject-a-token-that-fails-verification-with-401.md

````markdown
# Reject a token that fails verification with HTTP 401 and the code of the failed check

## Status

Proposed

### Owner

<GitHub account of the owner of this ADR>

### Participants and approvers

- Architect, `example-architect`: approves the decision and R1 to R3.

### Related ADRs

- ADR-0003: R4 and R9 are checks that this record covers. R4 gives `TOKEN_ISSUER_UNKNOWN`, and R9 gives
  `TOKEN_KEYS_UNAVAILABLE`.
- ADR-0004: R3 and R5 are checks that this record covers. R3 gives `TOKEN_SUBJECT_INVALID`.
- ADR-0005: R2 states the response to a token that gets `TOKEN_KEYS_UNAVAILABLE`, which R2 of this record keeps.

## Context

token-gate checks the token in `Authorization` before policy evaluation. The existing records give a response to some
checks one by one. ADR-0003 R4 and ADR-0004 R3 give HTTP 401 with a code. ADR-0005 R2 gives HTTP 503 with
`Retry-After: 5` for `TOKEN_KEYS_UNAVAILABLE`. ADR-0004 R5 states no code and no response. No record states what any
other failed check gets, or that a token that fails never reaches policy evaluation.

## Decision

We will reject a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed,
before policy evaluation, except that a token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 so
that the client retries.

### Terms

- **verification**: every check that the code runs on a token in `Authorization` before policy evaluation and that can
  reject the token. ADR-0003 R4 and R9 and ADR-0004 R3 and R5 are such checks.
- **fails verification**: a check of verification rejects the token. A token that gets `TOKEN_KEYS_UNAVAILABLE` fails
  verification.
- **code**: the error code that a check gives a token, such as `TOKEN_ISSUER_UNKNOWN`.

### Rules

#### Response to a token that fails verification

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the code
  of the check that failed, unless R2 applies to it.
- **R2** (`server`). A request whose token in `Authorization` gets `TOKEN_KEYS_UNAVAILABLE` gets the response that
  ADR-0005 R2 states, and not the response of R1.

#### Policy evaluation

- **R3** (`server`). A request whose token in `Authorization` fails verification is not passed to policy evaluation.

### Justification

A client that gets the code of the failed check can tell which check rejected its token (R1). A token that gets
`TOKEN_KEYS_UNAVAILABLE` is not wrong. The service has no keys for its provider yet, so the client gets a response that
tells it to retry (R2). A token that failed a check must not influence a policy decision (R3).

### Alternatives considered

- **A1. Give a token that gets `TOKEN_KEYS_UNAVAILABLE` HTTP 401 like every other failed check.** Rejected by R2: a
  401 gives the client no reason to retry, and the keys may load a moment later.

## Consequences

Positive:

- A client tells a rejected token (HTTP 401) from a service that cannot verify yet (HTTP 503).

Negative:

- A client must treat HTTP 503 from token-gate as a signal to retry and HTTP 401 as final.

## Open points

- **O1.** ADR-0004 R5 gives no code to a token from a namespace that the topology file does not list, so R1 has no code
  to return for it. The architect names the code. If other checks of verification have no code either, the architect
  names theirs too. It affects R1.
- **O2.** A token can fail more than one check. The notes do not say which code it gets, or whether
  `TOKEN_KEYS_UNAVAILABLE` wins over another code. Either a rule fixes one order of the checks, or the first check that
  fails decides. The architect decides. It affects R1 and R2.
````

### Message to the user

I wrote the record as `Proposed`, because two open points block acceptance. Three things need an answer from you:

- **Owner:** who owns the ADR? I left the placeholder `<GitHub account of the owner of this ADR>` in the record. I listed `example-architect` as approver only.
- **O1:** which code does the namespace check of ADR-0004 R5 give? The rules I had for ADR-0004 R5 state no code and no response. R1 says "the code of the check that failed", so it has nothing to return for that check. I did not invent a code.
- **O2:** when a token fails more than one check, which code does it get? Does `TOKEN_KEYS_UNAVAILABLE` win over the others?

I also made two choices of my own:

- **A1:** the notes list no rejected options, so I derived this one from "so that the client retries". Please confirm it or remove it.
- **R3:** I read "before policy evaluation" as a rule that a failed token never reaches policy evaluation. That includes the 503 case.

Some other points about the record:

- **Overlap with existing records:** R1 generalizes the 401 responses that ADR-0003 R4 and ADR-0004 R3 already give. I did not restate their conditions. If you want one home for each response, the old records could be superseded later.
- **Links:** I cited ADR-0003, ADR-0004, and ADR-0005 without links, because I don't have their filenames. Add the links when you merge.
- **Layers:** I tagged R1 `verify` and `server`, and R2 and R3 `server`, because I don't know which package maps a failed check to the response. Please correct this if the code differs.
- **Confirmation:** the section is empty, because I know of no existing test for these rules.
- **README and existing records:** `docs/adr/README.md` needs no change, and I edited no existing record.
- **Trailers:** the change that implements these rules ends its commit message and pull request description with `Implements: ADR-0007 R1, R2, R3`.
