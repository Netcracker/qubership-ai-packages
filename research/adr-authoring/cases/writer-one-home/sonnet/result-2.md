## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let only M2M tokens reach any tenant, and count a `ROLE_M2M` realm token and every service account token as M2M

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file name of ADR-0003>): the `TOKEN_ISSUER_UNKNOWN` response of R4.
- [ADR-0004: <title of ADR-0004>](<file name of ADR-0004>): the providers-file rule of R1, the `sub` check of R3, and the namespace check of R5.

## Context

token-gate checks the token in `Authorization` before policy evaluation. Two kinds of token reach it: tokens that
Keycloak signs for a realm, and tokens that the Kubernetes API server signs for a service account. Which of them act as
machine-to-machine (M2M) callers, and which tenants a token may reach, are not recorded.

The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`. In the mode `legacy` the providers file holds no provider of
service account tokens (ADR-0004 R1), so a service account token gets the `TOKEN_ISSUER_UNKNOWN` response of ADR-0003
R4 before any rule of this record applies.

## Decision

We will count a realm token with the role `ROLE_M2M` and every service account token as an M2M token, and we will let
only an M2M token reach a tenant other than the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **target tenant**: the tenant that a request names in `<where the request names its tenant>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its `realm_access.roles` holds `ROLE_M2M`,
  and is not an M2M token otherwise.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH`, unless its target tenant equals the value of the `tenant-id` claim of that token (O2, O3).
- **R4** (`verify`). A token in `Authorization` that any check other than R3 refuses gets the response of that check,
  and R3 does not apply to it (O3).

### Justification

A service account token can count as an M2M token because the `sub` check of ADR-0004 R3 refuses a token whose subject
is not a service account, and the namespace check of ADR-0004 R5 accepts a token only from a namespace that the
topology file lists (R2).

R4 settles the order of R3 and the other checks. In the mode `legacy` it leaves a service account token with the
`TOKEN_ISSUER_UNKNOWN` response of ADR-0003 R4 (R4).

### Alternatives considered

- **A1. Treat a service account token like any other token that is not M2M, so that it reaches only the tenant of its
  own `tenant-id` claim.** Rejected by R2: the checks of ADR-0004 R3 and R5 already limit which service account tokens
  are accepted.

## Consequences

Negative:

- Every service account token from a listed namespace reaches any tenant, and so does every realm token that holds
  `ROLE_M2M` (R1, R2).

## Open points

- **O1.** Where does a request name its target tenant: the path, a header, or a body field? `@example-architect`
  decides. It affects R3 and the term **target tenant**.
- **O2.** Assumption: a token that is not M2M and has no `tenant-id` claim equals no target tenant, so R3 refuses it.
  `@example-architect` confirms or names another result. It affects R3.
- **O3.** Assumption: the check of R3 runs in `verify`, after every other check of the token. `@example-architect`
  confirms, or names the layer and the order. It affects R3 and R4.
- **O4.** Does a caller today reach another tenant with a token that is not M2M? If so, a rule must state what an
  existing installation gets on upgrade. `@example-architect` decides. It affects R3.
````

### Message to the user

I wrote the record as `Proposed`. Four open points block acceptance.

Questions:
- Who owns this record? The owner field holds a placeholder.
- Which file names and titles do ADR-0003 and ADR-0004 have? I don't have them, so the links under Related ADRs are placeholders.
- O1 to O4 in the record: where a request names its tenant, what happens to a non-M2M token with no `tenant-id` claim, which layer runs the 403 check and in what order, and what upgrading installations get.

What I left out or kept thin:
- **`legacy` mode:** the notes say a service account token gets `TOKEN_ISSUER_UNKNOWN` there. ADR-0003 R4 and ADR-0004 R1 already imply that, so it has no rule and appears only as a fact in Context. R4 of this record makes sure the 403 check does not override it.
- **"Never reaches another tenant":** R3 already covers that sentence of the notes.
- **Justification and alternatives:** the notes give a reason only for counting service account tokens as M2M, so that is the only reason and the only alternative I wrote. If the meeting gave reasons for R1, R3, or other rejected options, send them.
- **Confirmation:** I named no checks because I know of none. Add them as tests land.

`docs/adr/README.md` needs no change, because the record uses the layer `verify`, which the guide already maps. Code that implements these rules should end its commit message and pull request description with the `Implements` trailer.

## Request 2

### File: docs/adr/0007-token-failures-get-401-before-policy-evaluation.md

````markdown
# Refuse a token that fails verification with HTTP 401 and the code of the failed check before policy evaluation

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file name of ADR-0003>): the `TOKEN_ISSUER_UNKNOWN` response of R4 and the `TOKEN_KEYS_UNAVAILABLE` response of R9.
- [ADR-0004: <title of ADR-0004>](<file name of ADR-0004>): the `TOKEN_SUBJECT_INVALID` response of R3 and the namespace check of R5.
- [ADR-0005: <title of ADR-0005>](<file name of ADR-0005>): the `Retry-After` response of R2.

## Context

token-gate checks the token in `Authorization` before policy evaluation. ADR-0003 R4 and ADR-0004 R3 give a refused
token HTTP 401 with an error code, and ADR-0005 R2 gives a token that gets `TOKEN_KEYS_UNAVAILABLE` an HTTP 503
response. The namespace check of ADR-0004 R5 names no response. No rule states that every refusal of a token gets
HTTP 401 with the code of its check, and no rule states that a refused token never reaches policy evaluation.

## Decision

We will refuse a token in `Authorization` that fails a verification check with HTTP 401 and the error code of that
check before policy evaluation, and we will give a token that gets `TOKEN_KEYS_UNAVAILABLE` the response of ADR-0005 R2
instead, so that the client retries.

### Terms

- **verification check**: a check in the layer `verify` or `keys` that refuses a token in `Authorization` because of
  the token or of its provider (O2).
- **error code of a check**: the identifier that the rule requiring the check names for its refusal, such as
  `TOKEN_ISSUER_UNKNOWN`. For the namespace check of ADR-0004 R5, R2 gives it.

### Rules

#### Response to a refused token

- **R1** (`verify`). A token in `Authorization` that a verification check refuses gets HTTP 401 with the error code of
  that check, except a token that R3 covers.
- **R2** (`verify`). The error code of the namespace check of ADR-0004 R5 is `<namespace error code>` (O1).
- **R3** (`server`). A token in `Authorization` that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2,
  and R1 does not apply to it.

#### Order

- **R4** (`server`). A request whose token in `Authorization` a verification check refuses is not passed to policy
  evaluation.

### Justification

A client that receives the error code of the failed check can tell which check refused its token (R1, R2). A client
that gets `TOKEN_KEYS_UNAVAILABLE` can succeed later without changing its token, so it gets the response that tells it
to retry (R3). A refused token never reaches policy evaluation (R4).

### Alternatives considered

- **A1. Give a token that gets `TOKEN_KEYS_UNAVAILABLE` HTTP 401 like every other refused token.** Rejected by R3: the
  client would treat the refusal as final and would not retry.

## Consequences

Positive:

- A verification check added later gets HTTP 401 with its own code, and its refusal happens before policy evaluation,
  with no rule of its own for either (R1, R4).

Negative:

- A later check that must answer with a status other than 401 needs a record that replaces R1 (R1).

## Open points

- **O1.** Which error code does a token get that the namespace check of ADR-0004 R5 refuses: a new code or an existing
  one? `@example-architect` decides. It affects R2.
- **O2.** Assumption: every check of the layers `verify` and `keys` that refuses a token, including any in ADR-0006,
  answers with HTTP 401 or, for `TOKEN_KEYS_UNAVAILABLE`, with the response of ADR-0005 R2. `@example-architect`
  confirms, or names the checks that answer otherwise. It affects R1 and the term **verification check**.
````

### Message to the user

I wrote the record as `Proposed`. Two open points block acceptance.

Questions:
- Who owns this record? The owner field holds a placeholder.
- Which file names and titles do ADR-0003, ADR-0004, and ADR-0005 have? I don't have them, so the links under Related ADRs are placeholders.
- O1: which error code does a token get when the namespace check of ADR-0004 R5 refuses it? That rule names no code, so R2 holds a placeholder.
- O2: does any check of the layers `verify` and `keys`, including those in ADR-0006, answer with a status other than 401? I assumed none does.

Much of your notes is already settled by existing records. ADR-0003 R4, ADR-0004 R3, and ADR-0005 R2 already give the 401 responses with codes and the 503 for `TOKEN_KEYS_UNAVAILABLE`. The record therefore adds only three things:
- **R1:** the general rule that any failed check gets 401 with its code.
- **R2:** the missing code for the ADR-0004 R5 refusal.
- **R4:** the ordering before policy evaluation.

R3 states the exception as a precedence over R1 and does not repeat the 503 response.

I named no checks under Confirmation because I know of none. `docs/adr/README.md` needs no change, because the record uses the layers `verify`, `keys`, and `server`, which the guide already maps.
