## Request 1

### File: docs/adr/0007-tenant-access-of-m2m-tokens.md

````markdown
# Let an M2M token address any tenant and keep every other token to its own tenant

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- ADR-0003: R4 gives a token whose `iss` names no provider the code `TOKEN_ISSUER_UNKNOWN`.
- ADR-0004: R1 fixes the providers per mode, R3 and R5 limit a service account token. This record changes none of them.
- ADR-0012 of example/platform: R3 gives the audience of a service account token that a service of the platform requests.

## Context

token-gate checks the token in `Authorization` before policy evaluation. Two kinds of token reach it. A realm token is
a token that Keycloak signs for a realm. A service account token is a token that the Kubernetes API server signs for a
service account.

Three rules limit a service account token before this record applies. ADR-0004 R3 refuses one whose `sub` does not
start with `system:serviceaccount:`. ADR-0004 R5 accepts one only from a namespace that the topology file lists.
ADR-0012 R3 of example/platform gives the audience `netcracker` to every service account token that a service of the
platform requests. token-gate does not enforce ADR-0012 R3, and none of the rules cited here makes `verify` check the
audience.

In the mode `legacy`, the providers file holds no provider of service account tokens (ADR-0004 R1). A service account
token therefore gets `TOKEN_ISSUER_UNKNOWN` in that mode (ADR-0003 R4) and never reaches R2.

## Decision

We will treat an accepted realm token that holds the role `ROLE_M2M`, and every accepted service account token, as an
M2M token. An M2M token may address any tenant, and every other token may address only the tenant of its own
`tenant-id` claim.

### Terms

- **accepted token**: a token in `Authorization` that no rule of the `verify` layer or the `keys` layer refuses.
- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: an accepted token that R1 or R2 names.
- **addressed tenant**: the tenant that a request names in `<where a request names its tenant>` (O2).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). An accepted realm token is an M2M token where its `realm_access.roles` holds `ROLE_M2M`, and is
  not an M2M token otherwise.
- **R2** (`verify`). An accepted service account token is an M2M token.

#### Tenant access

- **R3** (`server`). A request whose token in `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`,
  whatever its addressed tenant.
- **R4** (`server`). A request whose token in `Authorization` is not an M2M token, and whose addressed tenant differs
  from the `tenant-id` claim of that token, gets HTTP 403 with `CALLER_TENANT_MISMATCH`. A token with no `tenant-id`
  claim differs from every tenant.

### Justification

A service account token needs no role to be an M2M token, because three rules already limit who holds one: the subject
check (ADR-0004 R3), the namespace check (ADR-0004 R5), and the audience that the platform gives (ADR-0012 R3 of
example/platform) (R2). A realm token carries no such limit, so it needs the explicit role `ROLE_M2M` (R1). A token that
is not an M2M token never reaches another tenant, which keeps a caller of one tenant out of the data of the others (R4).

### Alternatives considered

- **A1. Let every accepted token address any tenant.** Rejected by R4: a token of an ordinary caller would reach every
  tenant.
- **A2. Require `ROLE_M2M`, or a similar marker, of a service account token too.** Rejected by R2: ADR-0004 R3 and
  ADR-0004 R5 already limit who holds such a token, so a second marker adds no protection.

## Consequences

Negative:

- A service account token from any namespace that the topology file lists can address every tenant (R2, R3). Adding a
  namespace to the topology file now also grants this access.
- In the mode `legacy`, no token is an M2M service account token, because a service account token gets
  `TOKEN_ISSUER_UNKNOWN` there. Only a realm token with `ROLE_M2M` can address any tenant in that mode (R1).

## Open points

- **O1.** Whether `verify` must also refuse a service account token whose audience is not `netcracker`. Answers: add a
  rule to this record, or leave the audience to the platform. `example-architect` decides. Affects R2.
- **O2.** What in a request names the addressed tenant (a path segment, a header, or another field), and whether the
  layer that reads it is `server`, as R3 and R4 assume. `example-architect` decides. Affects R3 and R4.
- **O3.** Whether R4 changes what an existing caller gets today. If a caller with a token that is not an M2M token
  reaches another tenant now, an upgrade rule and a Negative entry are needed. `example-architect` decides. Affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has no Date heading, and the open points block acceptance.

Questions:

- Who owns the record? I left `<GitHub account of the owner>` in the Owner field. I put `example-architect` under approvers.
- O2: what in a request names the tenant? The notes don't say. R3 and R4 depend on the answer, and I tagged them `server` on that assumption.
- O1: should `verify` check that a service account token has the audience `netcracker`? ADR-0012 R3 binds the platform's services, not token-gate. As far as the cited rules go, nothing in token-gate enforces the audience. The safety of R2 rests partly on it.
- O3: does R4 change what callers get today? I can't tell without the code.

Other notes:

- The notes' last point is a consequence of ADR-0003 R4 and ADR-0004 R1, so I cited both in Context and Negative and did not make it a rule.
- I used no links. I don't know the filenames of ADR-0003 and ADR-0004, and I have no URL for example/platform's ADR-0012. Add them under Related ADRs.
- I wrote the "token with no `tenant-id` claim" case in R4 as an assumption. Correct it if the architect meant otherwise.
- The accepted records and the README guide stay as they are.

## Request 2

### File: docs/adr/0007-response-to-a-token-that-fails-verification.md

````markdown
# Reject a token in Authorization that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- ADR-0003: R4 and R9 each name a check of a token and its code.
- ADR-0004: R3 and R5 each name a check of a service account token.
- ADR-0005: R2 gives the response to a token that gets `TOKEN_KEYS_UNAVAILABLE`. R1 of this record defers to it.

## Context

token-gate checks the token of each request before policy evaluation. Several records each refuse a token for one
reason: ADR-0003 R4 gives HTTP 401 with `TOKEN_ISSUER_UNKNOWN`, and ADR-0004 R3 gives HTTP 401 with
`TOKEN_SUBJECT_INVALID`. ADR-0004 R5 refuses a token from a namespace that the topology file does not list and names no
result. ADR-0003 R9 gives `TOKEN_KEYS_UNAVAILABLE` to a token whose provider has had no keys since the start, and
ADR-0005 R2 answers that code with HTTP 503 and `Retry-After: 5`. No record states what a token that fails any check
gets by default.

## Decision

We will answer a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed,
before policy evaluation, except a token that gets `TOKEN_KEYS_UNAVAILABLE`, which gets the response of ADR-0005 R2 so
that the client retries.

### Terms

- **token in Authorization**: the token that a request carries in its `Authorization` header.
- **check**: a rule of an `Accepted` record, in the layer `verify` or `keys`, under which a token in `Authorization` is
  refused.
- **fails verification**: a check refuses a token in `Authorization`. The code of that token is the code that the rule
  of the check names.

### Rules

#### Response

- **R1** (`verify`). A token in `Authorization` that fails verification gets HTTP 401 with the code of the check that
  failed, except a token whose code is `TOKEN_KEYS_UNAVAILABLE`, which ADR-0005 R2 governs.

#### Order

- **R2** (`server`). A request whose token in `Authorization` fails verification reaches no policy evaluation, also
  where its code is `TOKEN_KEYS_UNAVAILABLE`.

### Justification

A code in the 401 tells the client which check failed (R1). A token that cannot be checked because the provider has no
keys is a fault that may pass, so it gets the response that makes the client retry, not a 401 that ends the request
(R1). A token that fails verification is not trusted, so no policy decision may rest on it (R2).

### Alternatives considered

- **A1. Answer every failure, including `TOKEN_KEYS_UNAVAILABLE`, with HTTP 401.** Rejected by R1: the client would
  treat a lack of keys, which may pass, as a final refusal and would not retry.

## Consequences

Negative:

- A check added later gets HTTP 401 with its own code unless its rule or a later record says otherwise (R1).
- The 401 of ADR-0003 R4 and ADR-0004 R3 now also follows from R1. Their results do not change.

## Open points

- **O1.** The code of the check in ADR-0004 R5, which names none. Answers: an existing code, a new code such as
  `<code of the namespace check>`, or a rule in a record that amends ADR-0004 R5. `example-architect` decides. Affects R1.
- **O2.** Whether a request whose token gets `TOKEN_KEYS_UNAVAILABLE` also reaches no policy evaluation. R2 assumes
  that it reaches none. `example-architect` decides. Affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. It has no Date heading, and the open points block acceptance.

Questions:

- Who owns the record? I left `<GitHub account of the owner>` in the Owner field. I put `example-architect` under approvers.
- O1: what code does the check of ADR-0004 R5 (unlisted namespace) return? The existing records name none. Without a code, R1 can't give that failure one. I left a visible placeholder and did not invent a value.
- O2: does a request that gets `TOKEN_KEYS_UNAVAILABLE` also skip policy evaluation? The notes say only that it gets the response of ADR-0005 R2. I assumed it skips evaluation.

Other notes:

- R1 overlaps with the 401 results in ADR-0003 R4 and ADR-0004 R3. I kept the overlap because the notes make 401 the default for every check, including future ones. Those records stay as they are, and Negative says their results don't change.
- I cite ADR-0005 R2 by number in R1 and do not restate its response, so the 503 and `Retry-After: 5` stay stated in one place.
- I used no links, because I don't know the filenames of the existing records. Add them under Related ADRs.
- The accepted records and the README guide stay as they are.
