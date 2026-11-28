## Request 1

### File: docs/adr/0007-limit-tokens-that-are-not-m2m-to-their-own-tenant.md

````markdown
# Let M2M tokens name any tenant, and limit every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): R4 gives a token whose `iss` names no provider
  `TOKEN_ISSUER_UNKNOWN`, which **Context** relies on.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): R1 fixes which modes have a provider of service account tokens. R3
  and R5 limit which service account tokens pass verification, and R2 of this record relies on both.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Two kinds of tokens reach it:
realm tokens, which Keycloak signs for a realm, and service account tokens, which the Kubernetes API server signs for a
service account.

Some callers are services that act for more than one tenant. Other callers act for one tenant, and a realm token
carries that tenant in its `tenant-id` claim. token-gate has no rule yet that decides which tokens may name a tenant
other than their own.

ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`. ADR-0004 R5
accepts a service account token only from a namespace that the topology file lists.

In the mode `legacy`, the providers file holds no provider of service account tokens (ADR-0004 R1). A service account
token therefore gets `TOKEN_ISSUER_UNKNOWN` in that mode (ADR-0003 R4), and only the mode `k8s` lets one pass
verification.

## Decision

We will treat a realm token with the role `ROLE_M2M`, and every service account token, as M2M tokens that may name any
tenant. Every other token may name only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **verified token**: a token in `Authorization` that every check of a token in ADR-0003 and ADR-0004 accepts.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **named tenant**: the tenant that a request names in `<field that carries the tenant>`.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token where its `realm_access.roles` claim holds the
  string `ROLE_M2M`. A realm token whose `realm_access.roles` claim does not hold `ROLE_M2M`, or that has no
  `realm_access.roles` claim, is not an M2M token.
- **R2** (`verify`). A service account token in `Authorization` is an M2M token, whatever claims it holds.

#### The tenant a token may name

- **R3** (`server`). A request whose token in `Authorization` is a verified token but not an M2M token, and whose named
  tenant differs from the value of the token's `tenant-id` claim, gets HTTP 403 with `CALLER_TENANT_MISMATCH`, and
  policy evaluation does not run for the request. Where that token has no `tenant-id` claim, every named tenant differs
  from it. A request whose token in `Authorization` is an M2M token never gets `CALLER_TENANT_MISMATCH`, whichever
  tenant it names.

### Implementation notes

Adds no requirement. Let `internal/verify` return whether a verified token is an M2M token, together with its
`tenant-id` claim. `internal/server` can then compare the named tenant with that claim without reading
`realm_access.roles` a second time.

### Justification

A role in the realm lets the realm's administrators mark a client as M2M without a change to token-gate (R1). A
service account token passes verification only with a `sub` of a service account (ADR-0004 R3) and only from a
namespace that the topology file lists (ADR-0004 R5). Every service account token that passes verification is
therefore one that the cluster's own workloads hold, so token-gate can treat it as an M2M token (R2). A token that is
not an M2M token stays inside its own tenant, whatever policy evaluation would allow, because token-gate refuses the
request before policy evaluation runs (R3).

### Alternatives considered

- **A1. Leave the tenant check to policy evaluation, and pass every verified token on.** Rejected by R3: a policy that
  forgets the check would let a token that is not an M2M token reach every tenant.
- **A2. Treat a service account token as an M2M token only where it also carries a role, as a realm token does.** A
  service account token carries no realm roles, and ADR-0004 R5 already limits the namespaces it comes from.

## Consequences

Negative:

- Whoever can grant `ROLE_M2M` in a Keycloak realm can let a client reach every tenant (R1).
- Every service account in a namespace that the topology file lists can reach every tenant, so adding a namespace to
  that file also grants that access (R2).
- A caller that acts for several tenants with a token that is not an M2M token gets `CALLER_TENANT_MISMATCH` for every
  tenant except its own, and needs `ROLE_M2M` or one token per tenant (R3).

## Open points

- **O1.** Which field of the request carries the named tenant, such as a header, a path segment, or a claim of the
  request body, and what a request that names no tenant gets. The architect decides. Affects R3 and the term **named
  tenant**.
- **O2.** R3 assumes that a request that gets `CALLER_TENANT_MISMATCH` does not reach policy evaluation. The other
  answer is that token-gate runs policy evaluation and then replaces its result with HTTP 403. The architect decides.
  Affects R3.
- **O3.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`
  for every named tenant. The other answer is that verification refuses such a token with a code of its own. The
  architect decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance, and they are questions for @example-architect:

1. **O1:** Which field of a request names the tenant? R3 has the placeholder `<field that carries the tenant>` until
   that's answered. Also, what does a request that names no tenant get?
2. **O2:** Does `CALLER_TENANT_MISMATCH` stop the request before policy evaluation runs? I assumed yes.
3. **O3:** Does a token that isn't M2M and has no `tenant-id` claim get `CALLER_TENANT_MISMATCH` for every tenant? I
   assumed yes.

Two items from the notes have no rule of their own:

- **Service account tokens in the mode `legacy`:** that they get `TOKEN_ISSUER_UNKNOWN` already follows from ADR-0004
  R1 and ADR-0003 R4, so I stated it in **Context** as a fact.
- **"A token that is not M2M never reaches another tenant":** R3 already states this, so it isn't repeated.

There are also gaps I couldn't fill without the repository:

- **Links:** I didn't have the titles or filenames of ADR-0003 and ADR-0004, so their links under **Related ADRs** are
  placeholders.
- **Filename:** I named the file after the skill's default pattern. Please rename it if your records use a different
  one.
- **Layer tags:** I couldn't read the code. I tagged the M2M rules `verify` and the tenant check `server`. Tell me if the
  tenant check lives in `internal/verify`.
- **Term owner:** if an existing record already defines "realm token" or "service account token", I'll replace my
  definitions with pointers to it.
- **Alternatives:** the notes listed none. A1 and A2 are my wording, so the architect should confirm them.
- **Upgrade:** does token-gate already let a token that isn't M2M reach other tenants? If it does, R3 changes what those
  callers get, and **Negative** should name that case and the test that shows it.

## Request 2

### File: docs/adr/0007-refuse-tokens-that-fail-verification-before-policy-evaluation.md

````markdown
# Refuse a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](0003-<slug>.md): R4 and R9 are verification checks that R1 and R2 cover.
- [ADR-0004: <title of ADR-0004>](0004-<slug>.md): R3 and R5 are verification checks that R1 and R2 cover. R3 of this
  record names the code for ADR-0004 R5.
- [ADR-0005: <title of ADR-0005>](0005-<slug>.md): R2 states the response to `TOKEN_KEYS_UNAVAILABLE`, which R2 of this
  record excepts.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The accepted records state
these checks one by one, and only some of them state the response a failing token gets.

- ADR-0003 R4 and ADR-0004 R3 each give a failing token HTTP 401 with a code.
- ADR-0003 R9 names the code `TOKEN_KEYS_UNAVAILABLE`, and ADR-0005 R2 gives a request whose token gets that code HTTP
  503 with `Retry-After: 5`.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists, and names neither a
  code nor a status for a token it refuses.

No record states whether policy evaluation runs for a request whose token fails a check.

## Decision

We will refuse a request whose token in `Authorization` fails verification before policy evaluation, with HTTP 401 and
the code of the failed check. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

### Terms

- **verification check**: a rule of an `Accepted` record, tagged `verify` or `keys`, that refuses a token in
  `Authorization` or gives it an error code, such as ADR-0003 R4, ADR-0003 R9, ADR-0004 R3, and ADR-0004 R5. ADR-0004 R1
  checks the providers file at the start, not a token, and is not a verification check.
- **code of a verification check**: the error code that the rule of the check names. For ADR-0004 R5, the code is the
  one that R3 names.

### Rules

#### Requests whose token fails verification

- **R1** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails a verification
  check, including a token that gets `TOKEN_KEYS_UNAVAILABLE`.
- **R2** (`server`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with the code of
  that verification check. A request whose token gets `TOKEN_KEYS_UNAVAILABLE` is excepted, and gets the response that
  ADR-0005 R2 states.

#### The code for an unlisted namespace

- **R3** (`verify`). A service account token in `Authorization` that ADR-0004 R5 refuses gets the code
  `<code for a namespace that the topology file does not list>`.

### Implementation notes

Adds no requirement. Map each code of a verification check to its response in one place in `internal/server`, so that
a new verification check gets HTTP 401 without a change to the mapping, and `TOKEN_KEYS_UNAVAILABLE` stays the only
entry with another response.

### Justification

Policy evaluation then sees only tokens that passed every verification check, so no policy has to handle a token that
failed one (R1). The code tells the client and the operator which check failed, without a look at the logs of
token-gate (R2, R3). A token that gets `TOKEN_KEYS_UNAVAILABLE` may be valid, because its provider's keys are only
missing for now, so the client gets a response that makes it retry instead of HTTP 401 (R2).

### Alternatives considered

- **A1. Pass a request whose token failed verification to policy evaluation, with the failure as an input.** Rejected
  by R1: every policy would have to refuse the request itself, and one that forgets would let the request through.
- **A2. Answer HTTP 401 to `TOKEN_KEYS_UNAVAILABLE` too.** Rejected by R2: a client that gets HTTP 401 treats its token
  as invalid and does not retry.
- **A3. Answer HTTP 401 with no code.** Rejected by R2: neither the client nor the operator could tell which check
  failed.

## Consequences

Positive:

- A client can tell a retryable failure, HTTP 503, from a token it has to replace, HTTP 401 (R2).

Negative:

- The code shows a caller with a forged or stolen token which check its token failed (R2).

## Open points

- **O1.** Which code a service account token from a namespace that the topology file does not list gets. The architect
  decides. Affects R3, and through it R2.
- **O2.** R2 assumes that a token that fails more than one verification check may get the code of any of them. The
  other answer is a fixed order of the checks that the record lists, with the code of the first check that fails. The
  architect decides. Affects R2, and also ADR-0005 R2 where `TOKEN_KEYS_UNAVAILABLE` is one of the failed checks.
- **O3.** R1 assumes that policy evaluation does not run for a request whose token gets `TOKEN_KEYS_UNAVAILABLE`. The
  notes state "before policy evaluation" only for the HTTP 401 case. The architect decides. Affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance, and they are questions for @example-architect:

1. **O1:** What code does a token refused under ADR-0004 R5 get? That rule names none, so "the code of the check that
   failed" has nothing to report for it. R3 has a placeholder until that's answered.
2. **O2:** A token can fail several checks. Which code does it get then? I assumed any one of them.
3. **O3:** Does `TOKEN_KEYS_UNAVAILABLE` also stop the request before policy evaluation runs? I assumed yes.

The exception for `TOKEN_KEYS_UNAVAILABLE` is already settled by ADR-0005 R2. R2 of the new record points at that rule
and doesn't restate the 503 response. ADR-0003, ADR-0004, and ADR-0005 stay as they are. This record adds rules and
replaces none of them.

There are also gaps I couldn't fill without the repository:

- **Links:** I didn't have the titles or filenames of ADR-0003 to ADR-0005, so their links are placeholders.
- **Filename:** I named the file after the skill's default pattern. Please rename it if your records use a different
  one.
- **Layer tags:** I couldn't read the code. I tagged R1 and R2 `server`, as ADR-0005 R2 is, and R3 `verify`.
- **Other statuses:** I knew only the rules you quoted. Does any other rule in ADR-0003 or ADR-0004 give a failing token
  a status other than HTTP 401? If one does, R2 needs to say which rule wins.
- **No `Authorization` header:** R2 covers only a token that is present. If no existing record says what a request
  without `Authorization` gets, should this record decide it?
