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

- [ADR-0003: <title>](0003-<slug>.md): the response for a token whose issuer names no provider (used in **Implementation notes**).
- [ADR-0004: <title>](0004-<slug>.md): the subject check and the namespace check for service account tokens, and the providers of the mode `legacy`.
- [ADR-0012 of example/platform: <title>](https://github.com/example/platform/tree/main/docs/adr): the audience of the service account tokens that platform services request.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Two kinds of token reach it. Keycloak signs a realm token for a realm. The Kubernetes API server signs a service account token for a service account. A caller that acts for a machine rather than a user needs to name tenants other than its own, and the service needs one test that tells such a token from the others.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as an M2M token. An M2M token may name any tenant, and any other token may name only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes one.
- **requested tenant**: the tenant that a request names in `<where a request names its tenant>` (O1).

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its `realm_access.roles` claim holds `ROLE_M2M`. A realm token whose `realm_access.roles` claim lacks `ROLE_M2M`, or that has no such claim, is not an M2M token.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### Access to a tenant

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token is not refused on the ground of its requested tenant. A request whose token in `Authorization` is not an M2M token gets HTTP 403 with `CALLER_TENANT_MISMATCH`, unless the token has a `tenant-id` claim that equals the requested tenant. Where the token also gets an error code from token verification, the response for that code applies instead.

### Implementation notes

Adds no requirement. In the mode `legacy` the providers file has no provider of service account tokens, so the issuer of such a token matches no provider and the rule on an unknown issuer already gives it `TOKEN_ISSUER_UNKNOWN`. R2 needs no code for that case.

### Justification

A realm token needs an explicit role to be an M2M token, so a user token never gets access to every tenant (R1, R3). A service account token is safe to treat as an M2M token for these reasons (R2):

- The subject check refuses a token whose `sub` does not start with `system:serviceaccount:`.
- The namespace check accepts a token only from a namespace that the topology file lists.
- The audience rule of example/platform ADR-0012 gives `netcracker` to every service account token that a service of the platform requests.

Keeping the tenant check on the token class keeps it to one test for both token kinds (R3).

### Alternatives considered

- **A1. Treat only realm tokens with `ROLE_M2M` as M2M tokens.** Rejected by R2: the subject check and the namespace check already limit which service account tokens are accepted, so a service account would need a Keycloak role for no added safety.

## Consequences

Positive:

- A platform service reaches any tenant with its service account token and needs no role in Keycloak.

Negative:

- Every workload that holds a service account token from a listed namespace may name any tenant (R2). The audience rule of example/platform ADR-0012 covers tokens that platform services request, and no rule of this record checks the audience (O3).
- A realm token without `ROLE_M2M` that names another tenant gets HTTP 403 with `CALLER_TENANT_MISMATCH` (R3).

## Open points

- **O1.** Where does a request name its tenant (path, header, or body field)? The architect decides. It affects R3 and the term **requested tenant**.
- **O2.** The record assumes that a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH` for every tenant. The alternative is that such a token is refused with another code. The architect decides. It affects R3.
- **O3.** Does `verify` refuse a service account token whose audience is not `netcracker`? The answers are: no check, which relies on the audience rule of example/platform ADR-0012, or a new rule of `verify` that refuses the token. The architect decides. It affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance (O1 to O3).

Questions:
- Who is the owner? I left `<owner GitHub account>` in place. Are there other approvers besides @example-architect?
- Where does a request name its tenant (O1)? The notes don't say.
- Should a non-M2M token with no `tenant-id` claim get `CALLER_TENANT_MISMATCH` (O2)? I assumed yes.
- Does `verify` check the audience (O3)? The notes call service account tokens safe because of the platform's audience rule. That rule covers only tokens that platform services request, and none of the token-gate rules you gave checks the audience.

Choices I made:
- I did not write the `legacy` case as a rule. ADR-0003 R4 and ADR-0004 R1 already give `TOKEN_ISSUER_UNKNOWN`, so a rule would only repeat them. I mention it in **Implementation notes**.
- I tagged R1 to R3 with the layer `verify`. If the tenant check lives in `server`, change R3's tag.
- Link targets for ADR-0003, ADR-0004, and example/platform ADR-0012 are placeholders, because I don't know the file names or titles. The platform link points at the directory.
- A1 is my own inference, because the notes list no alternative. Please confirm or drop it.

No existing record changes, no `README.md` change is needed, and I found no defect to raise as an issue.

## Request 2

### File: docs/adr/0007-failed-token-verification-response.md

````markdown
# Answer a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title>](0003-<slug>.md): the error code `TOKEN_KEYS_UNAVAILABLE` for a token whose provider has had no keys since the start.
- [ADR-0004: <title>](0004-<slug>.md): the namespace check for service account tokens (O1).
- [ADR-0005: <title>](0005-<slug>.md): the retry response for a token that gets `TOKEN_KEYS_UNAVAILABLE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The accepted records give some of these checks their own error code, and one failure, `TOKEN_KEYS_UNAVAILABLE`, gets a response that tells the client to retry. No record states what a failed check gets in general, or that policy evaluation does not run for the request.

## Decision

We will refuse a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed, before policy evaluation. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the retry response instead.

### Terms

- **verification check**: a check that a rule of `verify` or `keys` applies to a token in `Authorization` and that can refuse the token with an error code.
- **fails verification**: a verification check refuses the token.

### Rules

#### Failed verification

- **R1** (`verify`, `server`). Policy evaluation does not run for a request whose token in `Authorization` fails verification.
- **R2** (`verify`, `server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the error code of the verification check that refused it. The exception is a token that gets `TOKEN_KEYS_UNAVAILABLE`: it gets the retry response and no HTTP 401.

### Justification

A request with an unverified token must not reach policy evaluation, because the caller is not known (R1). One status and one code per check lets a client tell which check refused its token (R2). A token that fails only because its provider has no keys may pass on a later attempt, so the client has to retry and must not treat the failure as final (R2).

### Alternatives considered

- **A1. Return one fixed code for every failed check.** Rejected by R2: the client could not tell which check refused its token.
- **A2. Return HTTP 401 for `TOKEN_KEYS_UNAVAILABLE` like any other failed check.** Rejected by R2: a 401 gives the client no sign that it should retry.

## Consequences

Positive:

- A check added later gets the 401 response and its code from R2, and needs no rule of its own for the response.

Negative:

- Every verification check must carry an error code (R2).

## Open points

- **O1.** The namespace check for service account tokens names no error code, so R2 gives no definite code for a token from an unlisted namespace. The architect decides which code it gets. The same question applies to any other verification check whose code no record names. It affects R2.
- **O2.** A token may fail more than one verification check. The answers under consideration are the code of the first failed check in a fixed order of the checks, or the code of a check with the highest priority. The architect decides, and the order has to be stated as a rule. It affects R2.
````

### Message to the user

I wrote ADR-0008 as `Proposed`, but the file is `0007-...`, since 0007 is the next free number. Two open points block acceptance (O1 and O2).

Questions:
- Who is the owner? I left `<owner GitHub account>` in place. Are there other approvers besides @example-architect?
- Which error code does the namespace check of ADR-0004 R5 give (O1)? The accepted rule names none, so "the code of the check that failed" has no value for it.
- When a token fails several checks, which code wins (O2)?

Choices I made:
- The exception for `TOKEN_KEYS_UNAVAILABLE` sits inside R2 and cites the retry response of ADR-0005 R2 by what it is about. It does not restate that rule.
- R2 overlaps the 401 responses that ADR-0003 R4 and ADR-0004 R3 already give for their own checks. I kept R2 general, so that a later check needs no rule for its response. If you want only the new content, tell me and I will narrow it.
- The layer tags `verify` and `server` are my reading of where the ordering and the response are produced. Please check them.
- A1 and A2 are my inference from the notes, because the notes list no alternatives. Please confirm or drop them.
- The link targets for ADR-0003, ADR-0004, and ADR-0005 are placeholders, because I don't know their file names or titles.

No existing record changes, no `README.md` change is needed, and I found no defect to raise as an issue.

In the message for Request 2 I wrote "ADR-0008" by mistake. The record is ADR-0007, since this request starts from the repository as described and 0007 is the next free number.
