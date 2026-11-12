## Request 1

### File: docs/adr/0007-treat-realm-role-and-service-account-tokens-as-m2m-and-limit-other-tokens-to-their-tenant.md

````markdown
# Treat a realm token with the role `ROLE_M2M` and every service account token as an M2M token, and limit every other token to its own tenant

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title>](0003-<slug>.md): the issuer check of R4 gives `TOKEN_ISSUER_UNKNOWN`.
- [ADR-0004: <title>](0004-<slug>.md): the provider rule of R1, the `sub` check of R3, and the namespace check of R5
  limit which service account tokens reach R2 of this record.

## Context

token-gate checks the token of each request before policy evaluation. A token in `Authorization` is a realm token or a
service account token. The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`. Until now no record says which of these
tokens come from a machine caller, or which tenants a token may reach.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. An M2M
token may name any tenant, and every other token may reach only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **target tenant**: the tenant that a request names in <the field or path of the request that names the tenant>. O1
  asks which.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its `realm_access.roles` holds `ROLE_M2M`,
  and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenants

- **R3** (`verify`). A token in `Authorization` that passes verification and is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` where its `tenant-id` claim is missing or names a tenant other than the target tenant. An M2M
  token gets no such response, whatever its target tenant.

### Justification

R2 needs no check of its own on the token. The `sub` check of ADR-0004 R3 and the namespace check of ADR-0004 R5 already
limit which service account tokens reach it (R2). A service account token reaches R2 only in the mode `k8s`: the
provider rule of ADR-0004 R1 leaves the mode `legacy` without a provider for it, so the issuer check of ADR-0003 R4
gives it `TOKEN_ISSUER_UNKNOWN` (R2). The role in `realm_access.roles` marks a realm token as an M2M token (R1), and
every token that is not an M2M token stays within its own tenant (R3).

### Alternatives considered

- **A1. Make a service account token an M2M token only after a further check in this record.** Rejected by R2: the
  checks of ADR-0004 R3 and ADR-0004 R5 already apply to every service account token.
- **A2. Treat every realm token as an M2M token.** Rejected by R1: a realm token without `ROLE_M2M` would then name any
  tenant, where R3 limits it to its own.

## Consequences

Negative:

- A realm token that holds `ROLE_M2M`, and a service account token from a namespace that the topology file lists, can
  name any tenant. A leaked one reaches every tenant (R1, R2, R3).
- A token that is not an M2M token and has no `tenant-id` claim reaches no tenant (R3).

## Open points

- **O1.** Where does a request name its target tenant: a path segment, a header, a body field, or another place? The
  architect, `example-architect`, decides. It affects R3 and the term **target tenant**.
- **O2.** The record assumes that a token that is not an M2M token and has no `tenant-id` claim gets
  `CALLER_TENANT_MISMATCH` for every target tenant. The architect, `example-architect`, confirms or names another
  outcome. It affects R3.
- **O3.** The record assumes that a token that fails verification gets the response of the failed check, and never
  reaches R3. The architect, `example-architect`, confirms or names another order. It affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance, and I need these answers:

1. Who owns the record? I left `<GitHub account of the owner>` in the Owner field.
2. Where does a request name its target tenant (O1)? The notes say "any tenant" but not how a request names one, so I left a visible placeholder in the term.
3. Please confirm two assumptions I wrote into R3 (O2, O3):
   - A non-M2M token with no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`.
   - A token that fails verification gets its own failure response first.

Two notes from the meeting are not rules:

- **`legacy` mode:** the `TOKEN_ISSUER_UNKNOWN` outcome for a service account token already follows from ADR-0004 R1 and ADR-0003 R4. I put it in the Justification instead of restating it.
- **"Never reaches another tenant":** this restates R3, so I left it out.

Other choices to check:

- **Layer tags:** I tagged R1 to R3 `verify`, assuming the token classification and the tenant check live in `internal/verify`. If the tenant check lives in `server`, change the tag on R3.
- **Related ADR links:** I couldn't see the filenames or titles of ADR-0003 and ADR-0004, so those links are placeholders to fill in.
- **Confirmation:** I left the section out because no test or check exists yet. Add entries as checks land.
- **Reading guide:** no change needed, because all the layers already exist.

## Request 2

### File: docs/adr/0007-refuse-a-token-that-fails-verification-before-policy-evaluation.md

````markdown
# Refuse a token in `Authorization` that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title>](0003-<slug>.md): R9 defines `TOKEN_KEYS_UNAVAILABLE`.
- [ADR-0004: <title>](0004-<slug>.md): R5 is the namespace check, and O1 asks about its error code.
- [ADR-0005: <title>](0005-<slug>.md): R2 gives the response to a token that gets `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token of each request before policy evaluation. The issuer check of ADR-0003 R4 and the `sub`
check of ADR-0004 R3 each state their own HTTP 401 and error code. The namespace check of ADR-0004 R5 states no
response. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2, which tells the client to retry.

## Decision

We will refuse every token in `Authorization` that fails verification with HTTP 401 and the error code of the check
that refused it, except a token that gets `TOKEN_KEYS_UNAVAILABLE`. No such token reaches policy evaluation.

### Terms

- **fails verification**: a token in `Authorization` fails verification when a check of the layer `verify` or the layer
  `keys` refuses it.

### Rules

#### The response

- **R1** (`verify`). A token in `Authorization` that fails verification gets HTTP 401 with the error code of the check
  that refused it. The exception is a token that gets `TOKEN_KEYS_UNAVAILABLE`, which gets the response of ADR-0005 R2.

#### The order

- **R2** (`server`). A request whose token in `Authorization` fails verification is not passed to policy evaluation,
  whether the token gets HTTP 401 or the response of ADR-0005 R2.

### Justification

A client can tell from the response whether a retry helps. HTTP 401 with the error code of the failed check means the
token is wrong, and the response of ADR-0005 R2 means the keys may arrive later (R1). Policy evaluation then reads only
tokens that passed verification (R2).

### Alternatives considered

- **A1. Answer a token that gets `TOKEN_KEYS_UNAVAILABLE` with HTTP 401 like every other failed check.** Rejected by
  R1: the client would not retry, although the keys may arrive later.
- **A2. Pass a token that fails verification to policy evaluation and let the policy refuse it.** Rejected by R2: policy
  evaluation would then run on a token that no check accepted.

## Consequences

Negative:

- A client whose token gets `TOKEN_KEYS_UNAVAILABLE` sees the retry response for as long as the keys stay missing, also
  where the token would fail a later check (R1).

## Open points

- **O1.** The namespace check of ADR-0004 R5 states no error code. Which code does a service account token from a
  namespace that the topology file does not list get under R1? The architect, `example-architect`, decides. It affects
  R1.
- **O2.** Which code does a token get when more than one check refuses it, and where does `TOKEN_KEYS_UNAVAILABLE`
  rank among them? The architect, `example-architect`, decides. It affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance, and I need these answers:

1. Who owns the record? I left `<GitHub account of the owner>` in the Owner field.
2. What error code does the namespace check of ADR-0004 R5 give (O1)? As the records state it, that rule has no response, so "the code of the check that failed" has no value for it. The decision for that case belongs to the architect.
3. Which code wins when more than one check refuses a token (O2)? This also settles where `TOKEN_KEYS_UNAVAILABLE` ranks among them.

Choices to check:

- **No restated rules:** I did not restate ADR-0005 R2. R1 cites it, and R1 carries the exception so the 401 rule does not conflict with ADR-0003 R9.
- **Layer tags:** R1 is tagged `verify` and R2 is tagged `server`. I assumed the call to policy evaluation sits in `internal/server`. Change the tag if it sits elsewhere.
- **Related ADR links:** I couldn't see the filenames or titles of ADR-0003, ADR-0004, and ADR-0005, so those links are placeholders to fill in.
- **Confirmation:** I left the section out because no test or check exists yet. Add entries as checks land.
- **Reading guide:** no change needed, because all the layers already exist.
