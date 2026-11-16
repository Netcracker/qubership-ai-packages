## Request 1

### File: docs/adr/0007-let-m2m-tokens-reach-any-tenant.md

````markdown
# Let an M2M token reach any tenant, and keep every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): the response to a token whose issuer names no provider, R4.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the providers of service account tokens in each mode, R1, the
  subject check, R3, and the namespace check, R5.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Keycloak signs realm tokens,
and the Kubernetes API server signs service account tokens. Some callers are services that act for every tenant, and
other callers act for a single tenant, which their `tenant-id` claim names.

The setting `M2M_AUTH_MODE` takes `legacy` or `k8s`. In the mode `legacy` the providers file holds no provider of
service account tokens (ADR-0004 R1). ADR-0003 R4 therefore gives a service account token `TOKEN_ISSUER_UNKNOWN` in
that mode, and the rules of this record about service account tokens have an effect only in the mode `k8s`.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as an M2M token, and let only an
M2M token reach a tenant other than the one its `tenant-id` claim names.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **target tenant**: the tenant that a request names in `<where a request names its tenant>`.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its claim `realm_access.roles` holds the
  string `ROLE_M2M`. A realm token whose `realm_access.roles` is missing or does not hold `ROLE_M2M` is not an M2M
  token.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` when the token's `tenant-id` claim is missing or differs from the target tenant of the
  request. A request whose token in `Authorization` is an M2M token gets no `CALLER_TENANT_MISMATCH` for any target
  tenant. Where another rule gives the token HTTP 401 or HTTP 503, that response takes precedence over
  `CALLER_TENANT_MISMATCH`.

### Justification

A realm decides which of its clients reach every tenant, because a realm token is an M2M token only where the realm
grants it the role `ROLE_M2M` (R1).

A service account token reaches every tenant without a role, and the subject and namespace checks of ADR-0004 bound
which workloads hold one. ADR-0004 R3 refuses a token whose `sub` is not the subject of a service account, and
ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists (R2).

A token that is not an M2M token reaches only the tenant that its `tenant-id` claim names, so a caller that acts for one
tenant cannot read or change the data of another (R3).

## Consequences

Negative:

- Every workload in a namespace that the topology file lists reaches every tenant (R2). Adding a namespace to the
  topology file grants that access, so a change to the file is a security change.
- A realm administrator who grants `ROLE_M2M` to a client grants that client access to every tenant (R1).
- A caller whose token is not an M2M token, and whose request names a tenant other than the token's `tenant-id` claim,
  gets HTTP 403 with `CALLER_TENANT_MISMATCH` (R3), whatever that caller got before.

## Open points

- **O1.** Where a request names its target tenant: a header, a path segment, or another place. The same answer settles
  what a request that names no tenant gets. `example-architect` decides. It affects the term **target tenant** and R3.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every target tenant. The other answer is that verification refuses such a token with
  HTTP 401 and a code of its own. `example-architect` decides. It affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0007-let-m2m-tokens-reach-any-tenant.md` with the status `Proposed`. O1 and O2 block acceptance.

Two items from the notes are not rules:

- **"A token that is not M2M never reaches another tenant."** This is the same requirement as the 403 rule, so R3 states it once.
- **"In the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`."** This already follows from ADR-0004 R1 (no provider of service account tokens in `legacy`) and ADR-0003 R4 (an unknown issuer gets 401 with `TOKEN_ISSUER_UNKNOWN`). A rule here would restate them, so I put the fact in **Context** instead.

I checked the two rules the notes give as the safety argument for service account tokens, ADR-0004 R3 and R5. They say what the notes claim, and they appear under **Justification**.

Questions:

1. **O1:** Where does a request name the tenant it wants to reach? I left the placeholder `<where a request names its tenant>` in the term **target tenant**. What does a request that names no tenant get?
2. **O2:** What does a token that is not M2M and has no `tenant-id` claim get? I assumed HTTP 403 with `CALLER_TENANT_MISMATCH`.
3. **Titles and filenames:** What are the titles and filenames of ADR-0003 and ADR-0004? I left placeholders in **Related ADRs**. I also assumed the filename pattern `NNNN-<kebab-case title>.md`, so please rename the file if the records use another pattern.
4. **Terms:** Does ADR-0003 or ADR-0004 already define "realm token" and "service account token"? If so, I'll replace my definitions with pointers to that record.
5. **Layer of R3:** I tagged R3 `verify`, as ADR-0003 R4 is tagged, without seeing the code. Does the tenant check belong in `internal/server` instead?
6. **Alternatives and approvers:** Which alternatives did the meeting reject? I left out **Alternatives considered** rather than invent any. Does anyone besides `example-architect` approve this record?

## Request 2

### File: docs/adr/0007-answer-a-token-that-fails-verification-with-http-401.md

````markdown
# Answer a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): the namespace check, R5, which names no code.
- [ADR-0005: <title of ADR-0005>](0005-<slug>.md): the response to `TOKEN_KEYS_UNAVAILABLE`, R2.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The rules of the accepted
records state these checks one by one, and they differ in what they say about the response. Most name a code. For
`TOKEN_KEYS_UNAVAILABLE`, ADR-0005 R2 sets the response so that the client retries. The namespace check of ADR-0004 R5
names neither an HTTP status nor a code.

## Decision

We will answer a request whose token in `Authorization` fails verification with HTTP 401 and the code of the failed
check, and policy evaluation will not run for that request. A token whose provider has no keys is the exception and
keeps the response that makes the client retry.

### Terms

- **verification**: the checks that the rules of accepted records make on a token in `Authorization` to decide whether
  the service accepts the token. A check on the configuration at the start, such as the one on the providers file, is
  not part of verification.
- **fails verification**: a token in `Authorization` fails verification when at least one check of verification refuses
  it.
- **code of a check**: the error code that the rule of the check names for a token it refuses, such as
  `TOKEN_ISSUER_UNKNOWN`.

### Rules

#### Order

- **R1** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails verification.

#### Response

- **R2** (`verify`, `server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the code
  of the first check that refuses the token, in the order in which the service runs the checks. A request whose token in
  `Authorization` gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

### Justification

Policy evaluation receives only tokens that passed verification, so a policy can rely on a token's claims (R1).

A client that gets HTTP 401 with the code of the failed check can tell which check refused its token without the
service's logs (R2). The client cannot fix a missing signing key, and that key can appear while the service runs, so a
token that gets `TOKEN_KEYS_UNAVAILABLE` keeps the response that makes the client retry (R2).

## Consequences

Negative:

- Any caller learns which check refused its token. For example, `TOKEN_ISSUER_UNKNOWN` shows that the providers file
  names no provider for the issuer of a token (R2).

## Open points

- **O1.** ADR-0004 R5 names no code for a service account token from a namespace that the topology file does not list,
  so R2 gives that token HTTP 401 with no code. One answer is a new record that replaces ADR-0004 R5 and names a code,
  `<code for a namespace the topology file does not list>`. The other is to accept HTTP 401 with no code for that check.
  `example-architect` decides. It affects R2.
````

### Message to the user

I wrote the record as `docs/adr/0007-answer-a-token-that-fails-verification-with-http-401.md` with the status `Proposed`. O1 blocks acceptance.

The exception for `TOKEN_KEYS_UNAVAILABLE` is already decided: ADR-0005 R2 gives that response. R2 therefore cites ADR-0005 R2 as an exception rather than restating the 503 and `Retry-After`. Without that citation, the general 401 would conflict with ADR-0005 R2.

For the issuer check (ADR-0003 R4) and the subject check (ADR-0004 R3), R2 gives the same 401 and code that those rules already give. I kept R2 general because the architect decided the response for every check of verification.

Questions:

1. **O1:** ADR-0004 R5 names no code, so R2 has no code for a token from a namespace that the topology file does not list. ADR-0004 is accepted, so the fix belongs in a new record that replaces ADR-0004 R5, not in this one. Should I write that record? If so, which code should it use?
2. **Other checks:** I only saw the rules that the notes refer to. Does any other check in ADR-0001 to ADR-0006 refuse a token in `Authorization` with a status other than 401, or with no code? Each of those cases needs the same answer as O1.
3. **Order of checks:** R2 takes the code of the first check that refuses the token, in the order the service runs the checks, and leaves that order to the code. Did the meeting fix an order?
4. **Titles and filenames:** What are the titles and filenames of ADR-0004 and ADR-0005? I left placeholders in **Related ADRs**. I also assumed the filename pattern `NNNN-<kebab-case title>.md`.
5. **Alternatives and approvers:** Which alternatives did the meeting reject? I left out **Alternatives considered** rather than invent any. Does anyone besides `example-architect` approve this record?
