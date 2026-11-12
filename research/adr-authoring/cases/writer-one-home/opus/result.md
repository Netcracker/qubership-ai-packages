## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Treat service account tokens and realm tokens with `ROLE_M2M` as M2M tokens, and hold every other token to its own tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- [ADR-0003](0003-<title-slug>.md): the issuer check of R4, which a service account token meets in the mode `legacy`
  before it can reach R2 of this record.
- [ADR-0004](0004-<title-slug>.md): the `sub` check of R3 and the namespace check of R5, which the Justification of R1
  relies on, and the provider-count rule of R1, which limits service account tokens to the mode `k8s`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. A request names the tenant it
acts on, and a token of a caller carries the caller's tenant in its `tenant-id` claim. Machine-to-machine (M2M) callers
act on more than one tenant. A realm token can carry roles in its `realm_access.roles` claim.

In the mode `legacy`, a service account token gets `TOKEN_ISSUER_UNKNOWN` from the issuer check of ADR-0003 R4, because
of the provider-count rule of ADR-0004 R1. A service account token can reach the tenant check of R2 only in the mode
`k8s`.

## Decision

We will treat every service account token, and every realm token that holds the role `ROLE_M2M`, as an M2M token that
may act on any tenant. Every other token may act only on the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 makes an M2M token.
- **verified token**: a token in `Authorization` that every check of the layers `verify` and `keys` accepts, apart from
  the tenant check of R2.
- **requested tenant**: the tenant that a request names in `<tenant source>`.

### Rules

#### M2M tokens

- **R1** (`verify`). A token in `Authorization` is an M2M token where it is a service account token, or where it is a
  realm token whose `realm_access.roles` claim holds the value `ROLE_M2M`. No other token in `Authorization` is an M2M
  token.

#### Tenant access

- **R2** (`verify`). A request gets HTTP 403 with `CALLER_TENANT_MISMATCH` where its verified token is not an M2M token
  and either has no `tenant-id` claim or has a `tenant-id` claim whose value differs from the requested tenant. A request
  whose verified token is an M2M token gets no `CALLER_TENANT_MISMATCH`, whatever its requested tenant.

### Implementation notes

Adds no requirement. Decide whether a token is an M2M token in one function, after the token is verified, and let the
tenant check call it, so that R1 has one implementation.

### Justification

A service account token needs no role to be an M2M token. The `sub` check of ADR-0004 R3 and the namespace check of
ADR-0004 R5 already limit which service accounts get a verified token (R1). A realm token becomes an M2M token only
where the realm grants it `ROLE_M2M`, so a realm token without that role stays bound to its tenant (R1, R2). Comparing
the requested tenant with the `tenant-id` claim keeps every token that is not an M2M token inside its own tenant (R2).

### Alternatives considered

- **A1. Let every verified token act on the tenant that the request names.** Rejected by R2: a token that is not an M2M
  token could then act on another tenant.

## Consequences

Positive:

- In the mode `k8s`, a workload in a namespace that the topology file lists can act on any tenant with its service
  account token, without a realm token from Keycloak (R1).

Negative:

- A realm that grants `ROLE_M2M` to a client lets every token of that client act on every tenant (R1, R2).
- A token that is not an M2M token gets `CALLER_TENANT_MISMATCH` where the request names a tenant other than the one in
  its `tenant-id` claim, or where it has no `tenant-id` claim (R2).
- In the mode `legacy`, no service account token reaches any tenant, as **Context** states.

## Open points

- **O1.** Where a request names its tenant (`<tenant source>`), such as a header, a path segment, or a query
  parameter, and what a request that names no tenant gets. `example-architect` decides. Affects the term
  **requested tenant** and R2.
- **O2.** R2 assumes that the tenant check applies only to a verified token. A token that another check refuses gets
  that check's response and never `CALLER_TENANT_MISMATCH`. The other answer is to run the tenant check first.
  `example-architect` decides. Affects R2.
- **O3.** R2 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH`. The other answer is HTTP 401 with a code of its own from `verify`. `example-architect`
  decides. Affects R2.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. Open points O1 to O3 block acceptance:

- **O1:** where a request names its tenant.
- **O2:** whether the tenant check runs only after every other check accepts the token.
- **O3:** what a token that is not M2M gets when it has no `tenant-id` claim.

The record has no rule saying that a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy`. ADR-0003 R4 and ADR-0004 R1 already produce that result, so a rule here would repeat them. **Context** states it as a fact instead. "A token that is not M2M never reaches another tenant" also has no rule of its own, because R2 already covers it.

Questions:

1. Is `example-architect` the owner, and does anyone else approve the record?
2. What are the file names of ADR-0003 and ADR-0004? I need them to fill in the `<title-slug>` links.
3. Do ADR-0003 or ADR-0004 already define "realm token" or "service account token"? If they do, I'll point **Terms** at those definitions instead of defining the words again.
4. I couldn't read the code. Is `verify` the right layer for the M2M decision and the tenant check, or does `server` hold them?
5. Did the meeting reject any designs that should go under **Alternatives considered**?

## Request 2

### File: docs/adr/0007-http-401-for-tokens-that-fail-verification.md

````markdown
# Refuse a token in `Authorization` that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003](0003-<title-slug>.md): the keys check of R9, whose `TOKEN_KEYS_UNAVAILABLE` R2 treats as an exception.
- [ADR-0004](0004-<title-slug>.md): the namespace check of R5, which R3 gives an error code.
- [ADR-0005](0005-<title-slug>.md): the response of R2 for `TOKEN_KEYS_UNAVAILABLE`, which R2 of this record uses.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The issuer check of ADR-0003
R4 and the `sub` check of ADR-0004 R3 each name an HTTP status and an error code. The keys check of ADR-0003 R9 names
an error code, and ADR-0005 R2 names the response for it. The namespace check of ADR-0004 R5 names neither a status nor
an error code.

## Decision

We will refuse a token in `Authorization` that fails verification with HTTP 401 and the error code of the failed check,
before policy evaluation runs. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets a response that tells the client to
retry.

### Terms

- **fails verification**: a token in `Authorization` fails verification when a check of the layer `verify` or `keys`
  does not accept it.

### Rules

#### Order

- **R1** (`server`). Policy evaluation does not run for a request whose token in `Authorization` fails verification.

#### Response

- **R2** (`verify`). A request whose token in `Authorization` fails verification gets HTTP 401 with the error code of a
  check that did not accept the token. The exception is a request whose token gets `TOKEN_KEYS_UNAVAILABLE` from the keys
  check of ADR-0003 R9. That request gets the response of ADR-0005 R2, also where another check did not accept the token.
- **R3** (`verify`). A service account token that the namespace check of ADR-0004 R5 does not accept gets the error code
  `<namespace error code>`.

### Implementation notes

Adds no requirement. Let the verifier return the error code of the failed check, and let the server map that code to
its response in one place before the server calls policy evaluation.

### Justification

Policy evaluation then sees only tokens that every check accepted (R1). The error code shows the client which check
refused its token (R2, R3). `TOKEN_KEYS_UNAVAILABLE` reports a state that ends once the provider's keys arrive, so the
client retries instead of giving up (R2).

### Alternatives considered

- **A1. Pass a token that fails verification to policy evaluation, and let the policy refuse it.** Rejected by R1.
- **A2. Return HTTP 401 for every failed check, `TOKEN_KEYS_UNAVAILABLE` included.** Rejected by R2: the client would
  not retry, although the keys can arrive later.
- **A3. Return one error code for every failed check.** Rejected by R2: the client could not tell which check refused
  its token.

## Consequences

Negative:

- A client that sends a service account token from a namespace that the topology file does not list gets HTTP 401 with
  `<namespace error code>` (R2, R3).
- A client whose token fails several checks sees the error code of only one of them (R2).

## Open points

- **O1.** The error code that a service account token gets from the namespace check of ADR-0004 R5
  (`<namespace error code>`). No name was proposed. `example-architect` decides. Affects R3.
- **O2.** R2 assumes two things about a token that several checks refuse. The response carries the error code of any
  one of those checks. Where one of the codes is `TOKEN_KEYS_UNAVAILABLE`, the response of ADR-0005 R2 wins. The other
  answers are a fixed order of checks stated in a rule, or HTTP 401 winning over the retry response. `example-architect`
  decides. Affects R2.
````

### Message to the user

I wrote ADR-0007 with the status `Proposed`. Open points O1 and O2 block acceptance:

- **O1:** the error code for a token that fails the namespace check of ADR-0004 R5. That rule names no code, and the decision requires the code of the failed check.
- **O2:** which response a token gets when several checks refuse it.

R2 is consistent with the 401 codes in ADR-0003 R4 and ADR-0004 R3. R3 adds a code without changing ADR-0004, so every existing record stays as it is.

Questions:

1. Is `example-architect` the owner, and does anyone else approve the record?
2. What are the file names of ADR-0003, ADR-0004, and ADR-0005? I need them to fill in the `<title-slug>` links.
3. I could only see the rules quoted in your notes. Does any rule in ADR-0001 to ADR-0006 give a failing token a status other than 401? If one does, R2 replaces part of that rule, and the record has to name it under **Related ADRs**.
4. What should a request get when it has no token in `Authorization`, or when the header isn't a token at all? No rule covers either case, so as it stands the implementer chooses.
5. I couldn't read the code. Is `server` the right layer for R1 and `verify` the right layer for R2 and R3?
