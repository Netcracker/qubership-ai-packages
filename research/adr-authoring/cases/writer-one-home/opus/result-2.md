## Request 1

### File: docs/adr/0007-m2m-tokens-may-name-any-tenant.md

````markdown
# Let an M2M token name any tenant, and limit every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003](0003-<slug>.md): the unknown-issuer check of ADR-0003 R4, which R3 leaves in force.
- [ADR-0004](0004-<slug>.md): the provider count of ADR-0004 R1, the `sub` check of ADR-0004 R3, and the namespace
  check of ADR-0004 R5, which the Justification of R2 relies on.
- [ADR-0005](0005-<slug>.md): the response to `TOKEN_KEYS_UNAVAILABLE` of ADR-0005 R2, which R3 leaves in force.

## Context

token-gate checks the token of each request before policy evaluation. A token in `Authorization` is either a realm
token, which Keycloak signs, or a service account token, which the Kubernetes API server signs. A realm token carries a
`tenant-id` claim. Some callers are services that act for every tenant, and the other callers act for one tenant.

The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`. Under the provider count of ADR-0004 R1 and the unknown-issuer
check of ADR-0003 R4, a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy`.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. An M2M
token may name any tenant, and any other token may name only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token is an M2M token.
- **requested tenant**: the tenant that a request names in `<tenant source>`.
- **verification**: the checks that the rules of ADR-0003 and ADR-0004 apply to a token in `Authorization`.

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its `realm_access.roles` claim is an array
  that holds the string `ROLE_M2M`. Any other realm token in `Authorization` is not an M2M token.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` when its requested tenant is not the tenant that the token's `tenant-id` claim names, or when
  the token has no `tenant-id` claim. A request whose token in `Authorization` is an M2M token never gets
  `CALLER_TENANT_MISMATCH`, whichever tenant it names. A request whose token in `Authorization` fails verification gets
  the response that ADR-0003, ADR-0004, and ADR-0005 give that failure, and not `CALLER_TENANT_MISMATCH`.

### Justification

The role `ROLE_M2M` lets the administrators of a realm mark a client as M2M without a change to token-gate (R1). A
service account token can be an M2M token without a role, because the `sub` check of ADR-0004 R3 and the namespace
check of ADR-0004 R5 limit which service accounts get past verification (R2). A caller that acts for one tenant can
reach only that tenant, so a token that is not M2M cannot read or change the data of another tenant (R3). A token that
fails verification is not trusted for any claim, so its tenant is never compared (R3).

### Alternatives considered

- **A1. Require `ROLE_M2M` in `realm_access.roles` on a service account token as well.** Rejected by R2: the
  Kubernetes API server issues no `realm_access` claim, so no service account token would be an M2M token.
- **A2. Let every verified token name any tenant, and leave the tenant check to policy evaluation.** Rejected by R3.

## Consequences

Positive:

- A service in a namespace that the topology file lists can call for any tenant without a realm client of its own (R2).

Negative:

- A leaked M2M token, or `ROLE_M2M` granted to the wrong client, reaches every tenant (R1, R2, R3).
- A realm token without a `tenant-id` claim reaches no tenant unless it holds `ROLE_M2M` (R3).

## Open points

- **O1.** Where a request names its tenant, such as a header, a path segment, or a query parameter, and what a request
  whose token is not an M2M token gets when the request names no tenant. `<tenant source>` in **requested tenant**
  holds the place of the answer. `example-architect` decides. Affects R3.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every requested tenant. The other answer is HTTP 401 with an error code of verification.
  `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It can't become `Accepted` until two open points are settled:

- **O1:** Where does a request name its tenant (a header, a path segment, or a query parameter)? And what happens to a request that names no tenant? R3 has the placeholder `<tenant source>` until we know.
- **O2:** Should a token that is not M2M and has no `tenant-id` claim get HTTP 403 with `CALLER_TENANT_MISMATCH`? I wrote R3 that way. The other option is HTTP 401 with an error code of verification.

Other points:

- **Legacy mode isn't a rule.** The notes say a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy`. That already follows from ADR-0004 R1 and ADR-0003 R4, so a new rule would only repeat them. I put it in Context as a fact.
- **Last tenant line isn't a rule.** "A token that is not M2M never reaches another tenant" repeats R3, so it has no rule of its own.
- **Terms may already exist.** Do ADR-0003 or ADR-0004 already define "realm token" or "service account token"? If so, I'll replace my definitions with pointers such as "as ADR-0004 defines it".
- **Layer tag is a guess.** I tagged R3 as `verify`. If `internal/server` will do the tenant comparison, the tag should be `server`.
- **Links need filling in.** I don't have the filenames of ADR-0003 to ADR-0005, so the links under Related ADRs use `<slug>` placeholders. Fill them in before merging.

## Request 2

### File: docs/adr/0007-refuse-a-token-that-fails-verification-with-http-401.md

````markdown
# Refuse a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003](0003-<slug>.md): the unknown-issuer check of ADR-0003 R4 and the keys check of ADR-0003 R9, whose
  error codes R1 uses.
- [ADR-0004](0004-<slug>.md): the `sub` check of ADR-0004 R3, whose error code R1 uses, and the namespace check of
  ADR-0004 R5, which R2 gives an error code.
- [ADR-0005](0005-<slug>.md): the response to `TOKEN_KEYS_UNAVAILABLE` of ADR-0005 R2, which takes precedence over R1.

## Context

token-gate checks the token of each request before policy evaluation. The checks of verification are spread over
several records, and they name their outcomes in different ways. The unknown-issuer check of ADR-0003 R4 and the `sub`
check of ADR-0004 R3 name an HTTP status and an error code. The keys check of ADR-0003 R9 names an error code, and
ADR-0005 R2 gives the response to that code. The namespace check of ADR-0004 R5 names neither a status nor an error code.

## Decision

We will refuse a token in `Authorization` that fails verification with HTTP 401 and the error code of the failed check,
before policy evaluation. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

### Terms

- **verification**: the checks that the rules of `Accepted` records apply to a token in `Authorization` in the layers
  `verify` and `keys`.
- **error code of a check**: the code that the rule of a check of verification names for a token that fails it, such as
  `TOKEN_ISSUER_UNKNOWN`, or the code that R2 names.

### Rules

#### Response to a failed check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a check of verification gets HTTP 401
  with the error code of one check that the token fails, and policy evaluation does not run for that request. A request
  whose token in `Authorization` gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead of HTTP 401.

#### Error codes

- **R2** (`verify`). A service account token in `Authorization` that the namespace check of ADR-0004 R5 refuses gets the
  error code `<namespace error code>`.

### Justification

One status for every failed check lets a client treat each refusal of its token the same way, and the error code tells
it which check failed (R1, R2). Policy evaluation never sees a token that token-gate has not verified (R1). A token whose
provider has no keys may still be valid, and the fault lies with token-gate rather than the client, so that client gets
the response of ADR-0005 R2 and retries (R1).

### Alternatives considered

- **A1. Refuse a token whose provider has no keys with HTTP 401 and `TOKEN_KEYS_UNAVAILABLE`.** Rejected by R1: a
  client treats HTTP 401 as final and does not retry, although the same token may pass once keys arrive.
- **A2. Pass a token that fails verification on to policy evaluation, and let the policy refuse it.** Rejected by R1.

## Consequences

Negative:

- The error code tells any caller which check its token failed, such as an unknown issuer or an unlisted namespace
  (R1, R2).

## Open points

- **O1.** The error code for a service account token that the namespace check of ADR-0004 R5 refuses.
  `<namespace error code>` in R2 holds the place of the answer. `example-architect` decides. Affects R2.
- **O2.** R1 assumes that a token that fails several checks gets the error code of any one of them. The other answer is
  a fixed order of the checks, so that such a token always gets the code of the first one in that order.
  `example-architect` decides. Affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It can't become `Accepted` until two open points are settled:

- **O1:** What error code should a service account token from a namespace outside the topology file get? ADR-0004 R5 names none, so R2 has the placeholder `<namespace error code>`.
- **O2:** When a token fails several checks, can it get the code of any one of them, as I wrote R1? Or should the checks have a fixed order, so it always gets the code of the first one that fails?

Other questions:

- **Other checks without a code.** I only know the rules of ADR-0003 to ADR-0006 that your notes quote. Does any other rule there refuse a token without naming an error code? If so, each one needs a code in this record, the way R2 gives one for ADR-0004 R5.
- **No token at all.** Should a request with no token in `Authorization` get the same treatment? R1 covers only a token that fails a check, so for now that case is the implementer's choice.
- **Layer tags.** I tagged R1 with `verify` and `server`, because ADR-0003 R4 gives its HTTP status in `verify` and ADR-0005 R2 gives its status in `server`. Change the tags if one layer produces every response.
- **Links need filling in.** I don't have the filenames of ADR-0003 to ADR-0005, so the links under Related ADRs use `<slug>` placeholders. Fill them in before merging.
