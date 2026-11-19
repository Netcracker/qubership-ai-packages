## Request 1

### File: docs/adr/0007-limit-non-m2m-tokens-to-their-own-tenant.md

````markdown
# Let only an M2M token reach a tenant other than the one in its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file name of ADR-0003>): the issuer check (R4), which Context cites to explain the
  mode `legacy`.
- [ADR-0004: <title of ADR-0004>](<file name of ADR-0004>): the providers of each mode (R1), which Context cites, and the
  subject check (R3) and the namespace check (R5), on which the Justification of R2 rests.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. It accepts realm tokens and
service account tokens. No accepted record limits which tenant a request reaches with a token that passes verification.

Some clients call other tenants on purpose: these are machine-to-machine (M2M) clients. Every other client acts for the
single tenant named in the `tenant-id` claim of its token.

In the mode `legacy`, a service account token fails verification. ADR-0004 R1, on the providers of each mode, leaves
that mode without a provider of service account tokens, and the issuer check of ADR-0003 R4 then refuses the token with
`TOKEN_ISSUER_UNKNOWN`. A service account token therefore passes verification only in the mode `k8s`, which is the only
mode where R2 has an effect.

## Decision

We will treat a realm token with the role `ROLE_M2M` and every service account token as M2M tokens. A request whose
token is not an M2M token can only reach the tenant in the token's `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **passes verification**: no check that the code of the layers `verify` and `keys` runs on the token refuses it.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token is one.
- **requested tenant**: the tenant that `<the part of the request that names the tenant>` names.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its claim `realm_access.roles` is an array
  that holds the string `ROLE_M2M`, compared case-sensitively. A realm token that lacks the claim, or whose claim holds
  no such element, is not an M2M token.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token.

#### The tenant a request reaches

- **R3** (`server`). This rule covers a request that names a requested tenant and whose token in `Authorization` passes
  verification and is not an M2M token. Such a request gets HTTP 403 with `CALLER_TENANT_MISMATCH` in two cases: the
  token has no `tenant-id` claim, or the requested tenant differs from the value of that claim. A request whose token in
  `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`.

### Implementation notes

Adds no requirement. Let `internal/verify` return whether the token is an M2M token together with its claims. Let
`internal/server` compare the requested tenant with the `tenant-id` claim after verification and before it calls policy
evaluation.

### Justification

A service account token can act for any tenant without a role, because only workloads in known namespaces hold one. The
subject check of ADR-0004 R3 refuses a token whose subject names no service account. The namespace check of ADR-0004 R5
accepts only namespaces that the topology file lists (R2). A realm token has no such limit, so the realm role `ROLE_M2M`
in Keycloak marks the clients that may call other tenants (R1).

R3 applies only to a token that passes verification. A client with a bad token therefore gets the error code of
verification, not `CALLER_TENANT_MISMATCH` (R3).

### Alternatives considered

- **A1. Let every token that passes verification reach any tenant.** Rejected by R3: a token that is not an M2M token
  would reach tenants other than the one in its `tenant-id` claim.

## Consequences

Negative:

- A client whose realm token lacks `ROLE_M2M` and that calls a tenant other than the one in its `tenant-id` claim gets
  HTTP 403 with `CALLER_TENANT_MISMATCH` once the code of R3 ships (R1, R3). No setting turns this off on upgrade.
- Every service account token from a namespace that the topology file lists reaches every tenant (R2). Adding a
  namespace to the topology file therefore gives that namespace access to every tenant.

Follow-ups:

- Grant `ROLE_M2M` in Keycloak to the clients that call other tenants before the code of R3 ships.

## Open points

- **O1.** Where a request names its requested tenant, for example a header or a path segment, and what a request that
  names no tenant gets. The term **requested tenant** holds a placeholder until this is settled. `example-architect`
  decides. Affects R3.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`
  for every requested tenant. The other answer is to refuse such a token in verification, with a code of its own.
  `example-architect` decides. Affects R3.
````

### Message to the user

I added ADR-0007 with the status `Proposed`. It can't be accepted until O1 and O2 are answered:

- **O1:** Where does a request name the tenant it calls? And what should a request that names no tenant get? The record has a placeholder for this in the term **requested tenant**.
- **O2:** I assumed that a token that is not M2M and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`. Is that right, or should verification refuse such a token with its own code?

The note about the mode `legacy` didn't get a rule. ADR-0003 R4 (the issuer check) and ADR-0004 R1 (the providers of each mode) already give a service account token `TOKEN_ISSUER_UNKNOWN` in that mode. A new rule would only repeat them, so the record states it in Context.

Some questions:

- Who else approves this record besides `example-architect`?
- I don't have the titles or file names of ADR-0003 and ADR-0004, so the links under **Related ADRs** are placeholders. Can you give me those?
- If ADR-0003 or ADR-0004 already defines "realm token" or "service account token", I'll replace my definitions with a pointer to that record.
- The notes give a reason only for R2. Did the meeting give reasons for R1 and R3, or discuss alternatives other than A1? If so, I'll add them.

I left `docs/adr/README.md` unchanged, because the record adds no layer or path.

## Request 2

### File: docs/adr/0007-refuse-unverified-tokens-before-policy-evaluation.md

````markdown
# Refuse a token in `Authorization` that fails verification before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file name of ADR-0003>): the code `TOKEN_KEYS_UNAVAILABLE` (R9), which R2 makes an
  exception for, and the issuer check (R4), which Context cites as an example.
- [ADR-0004: <title of ADR-0004>](<file name of ADR-0004>): the namespace check (R5), whose rule names no response.
- [ADR-0005: <title of ADR-0005>](<file name of ADR-0005>): the response to `TOKEN_KEYS_UNAVAILABLE` (R2), which R2 of
  this record uses.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Some checks name their response
in their own rule, such as the issuer check of ADR-0003 R4. Others name none: the namespace check of ADR-0004 R5 names
neither a status nor a code. No accepted record says whether a request whose token fails verification reaches policy
evaluation.

`TOKEN_KEYS_UNAVAILABLE` reports a missing key, not a bad token. ADR-0005 R2 gives it a response that tells the client
when to retry.

## Decision

We will answer a request whose token in `Authorization` fails verification before policy evaluation runs. The response
is HTTP 401 with the code of the failed check, except for `TOKEN_KEYS_UNAVAILABLE`, which keeps the response of
ADR-0005 R2.

### Terms

- **verification**: the checks that the code of the layers `verify` and `keys` runs on a token in `Authorization`.
- **fails verification**: a check of verification refuses the token.
- **first failing check**: the first check that refuses the token, in the order in which verification runs its checks.

### Rules

#### Requests whose token fails verification

- **R1** (`server`). A request whose token in `Authorization` fails verification gets its response without policy
  evaluation running for it.
- **R2** (`server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the error code that
  the rule of the first failing check names. The exception is a request whose first failing check gives
  `TOKEN_KEYS_UNAVAILABLE`: it gets the response of ADR-0005 R2 instead of HTTP 401.

### Implementation notes

Adds no requirement. Let `internal/verify` return the error code of the first failing check. Let `internal/server` map
that code to the response and return before it calls policy evaluation.

### Justification

Policy evaluation only reads the claims of a token that passed every check (R1). The code of the failed check tells the
client what to fix (R2). A missing key is a transient fault, so the client should retry. The response of ADR-0005 R2
tells it when to retry, where HTTP 401 would tell it that the token is bad (R2).

### Alternatives considered

- **A1. Pass a token that fails verification to policy evaluation, and let the policy refuse it.** Rejected by R1.
- **A2. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401 like every other failed check.** Rejected by R2: the client
  would treat its token as bad and would not retry.

## Consequences

Positive:

- A policy needs no rule for a token that failed verification (R1).

Negative:

- A check whose rule names no status, such as the namespace check of ADR-0004 R5, now answers with HTTP 401 (R2).

Follow-ups:

- Write a record that replaces ADR-0004 R5 and names the error code of the namespace check. Until that record exists,
  R2 gives such a request no code.

## Open points

- **O1.** R1 assumes that a request whose token gets `TOKEN_KEYS_UNAVAILABLE` also gets its response without policy
  evaluation running. The notes place "before policy evaluation" only on the HTTP 401 response. `example-architect`
  decides. Affects R1.
- **O2.** R2 assumes that, where several checks would refuse one token, the first failing check sets the response. The
  other answer is a fixed precedence among the codes, for example `TOKEN_KEYS_UNAVAILABLE` before every other code.
  `example-architect` decides. Affects R2.
````

### Message to the user

I added ADR-0007 with the status `Proposed`. It can't be accepted until O1 and O2 are answered:

- **O1:** Does a request whose token gets `TOKEN_KEYS_UNAVAILABLE` also skip policy evaluation? I assumed it does.
- **O2:** When several checks would refuse the same token, which code does the response carry? I assumed the code of the first check that fails. The other option is a fixed precedence, such as `TOKEN_KEYS_UNAVAILABLE` before every other code.

There's a gap that this record can't close. ADR-0004 R5 (the namespace check) names no error code. That means R2 gives such a request HTTP 401 with no code. This has to be settled in ADR-0004 R5 itself, and since that record is accepted, the fix is a new record that replaces ADR-0004 R5. Should I write it, and which code should the namespace check return?

ADR-0003 R4 and ADR-0004 R3 already give HTTP 401 with their own codes. This record agrees with them, and those records stay as they are.

Two more questions:

- Who else approves this record besides `example-architect`?
- I don't have the titles or file names of ADR-0003, ADR-0004, and ADR-0005, so the links under **Related ADRs** are placeholders. Can you give me those?
