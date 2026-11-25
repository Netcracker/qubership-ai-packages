## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let an M2M token reach any tenant, and keep every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003](0003-<slug>.md): R4 gives HTTP 401 with `TOKEN_ISSUER_UNKNOWN` to a token whose `iss` names no provider.
  Its rules and the rules of ADR-0004 decide which tokens are verified tokens.
- [ADR-0004](0004-<slug>.md): R1 decides in which mode the providers file holds a provider of service account tokens.
  R3 and R5 limit which service account tokens pass verification.
- [example/platform ADR-0012](<link to example/platform ADR-0012>): R3 gives the audience `netcracker` to the service
  account tokens that services of the platform request.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. It handles two kinds of
token. Keycloak signs realm tokens for a realm, and the Kubernetes API server signs service account tokens for a service
account. The accepted records decide which tokens pass verification. None of the rules that this record builds on
decides which tenants a verified token may reach.

Verification already limits service account tokens in these ways:

- ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists.
- ADR-0012 R3 of example/platform gives the audience `netcracker` to every service account token that a service of the
  platform requests. It does not cover other service account tokens that the API server signs for a service account in
  a listed namespace. For example, a token from `kubectl create token`, or one that a workload outside the platform
  requests, carries the audience its requester chose. None of the rules that this record builds on makes token-gate
  check `aud` (O3).

In the mode `legacy`, ADR-0004 R1 keeps every provider of service account tokens out of the providers file. A service
account token therefore gets HTTP 401 with `TOKEN_ISSUER_UNKNOWN` under ADR-0003 R4 and never becomes a verified token.
R2 has an effect only in the mode `k8s`.

## Decision

We will treat every service account token, and every realm token that holds the role `ROLE_M2M`, as an M2M token. An M2M
token may name any tenant. Any other token reaches only the tenant of its `tenant-id` claim.

### Terms

- **realm token**: a token in `Authorization` that Keycloak signs for a realm.
- **service account token**: a token in `Authorization` that the Kubernetes API server signs for a service account.
- **verified token**: a token in `Authorization` that gets no error code from any rule of ADR-0003 or ADR-0004.
- **M2M token**: a verified token that R1 or R2 makes an M2M token.
- **non-M2M token**: a verified token that is not an M2M token.
- **requested tenant**: the tenant that a request names in `<tenant source>` (O1).

### Rules

#### M2M tokens

- **R1** (`verify`). A verified realm token is an M2M token when its claim `realm_access.roles` holds the string
  `ROLE_M2M`. A verified realm token is a non-M2M token when it has no claim `realm_access.roles`, or when that claim
  does not hold `ROLE_M2M`.
- **R2** (`verify`). Every verified service account token is an M2M token.

#### Tenant access

- **R3** (`verify`). token-gate never refuses a request because of its requested tenant when the token in
  `Authorization` of that request is an M2M token.
- **R4** (`verify`). A request with a requested tenant and a non-M2M token in `Authorization` gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` when that token has no `tenant-id` claim, or when its `tenant-id` claim is not equal, as a
  string, to the requested tenant. token-gate does not pass such a request to policy evaluation.

### Implementation notes

Adds no requirement. Decide whether a token is an M2M token once, after the checks of ADR-0003 and ADR-0004 have
passed, and run the tenant check of R4 on that result. In the mode `legacy`, no service account token reaches R2
(**Context**).

### Justification

R1 uses a role that Keycloak already puts into the token. A realm client becomes an M2M client through a role
assignment in the realm, with no change to token-gate (R1).

R2 relies on the limits that verification already puts on a service account token. ADR-0004 R3 refuses a token whose
`sub` names no service account. ADR-0004 R5 accepts a token only from a namespace that the topology file lists. The
meeting also relied on ADR-0012 R3 of example/platform for the audience `netcracker`. That rule covers only the tokens
that services of the platform request, and O3 asks whether token-gate checks the audience (R2).

R4 keeps a token issued for one tenant away from every other tenant. token-gate enforces this before policy
evaluation, so the isolation does not depend on each policy repeating the check (R3, R4).

### Alternatives considered

- **A1. Leave the tenant check to policy evaluation.** Rejected by R4: a policy that omits the check would let a
  non-M2M token reach another tenant.
- **A2. Make a service account token an M2M token only when it holds `ROLE_M2M`.** Rejected by R2: a service account
  token carries no `realm_access` claim, so no service account token would ever be an M2M token.

## Consequences

Positive:

- In the mode `k8s`, a service reaches any tenant with the service account token that Kubernetes gives it. It needs no
  Keycloak client of its own (R2, R3).

Negative:

- In the mode `k8s`, any workload whose service account is in a namespace that the topology file lists can act on every
  tenant (R2, R3). Adding a namespace to the topology file grants that access.
- Anyone who can assign the role `ROLE_M2M` in a Keycloak realm can grant access to every tenant (R1, R3).
- A client that today sends a realm token without `ROLE_M2M` for a tenant other than its `tenant-id` claim gets HTTP 403
  with `CALLER_TENANT_MISMATCH` after this change (R4).

## Open points

- **O1.** Which part of a request names the requested tenant: a header, a path segment, or a field that an existing
  record already defines. `example-architect` decides. Affects R3, R4, and the term **requested tenant**.
- **O2.** What a non-M2M token without a `tenant-id` claim gets. R4 assumes HTTP 403 with `CALLER_TENANT_MISMATCH` for
  every requested tenant, because a non-M2M token never reaches another tenant. The other option is HTTP 401 with a new
  code for a missing claim. `example-architect` decides. Affects R4.
- **O3.** Whether a service account token needs the audience `netcracker` to be an M2M token. ADR-0012 R3 of
  example/platform covers only the tokens that services of the platform request, and token-gate does not check `aud`.
  The options are:
  - (a) R2 as written: every verified service account token is an M2M token.
  - (b) A service account token is an M2M token only when its `aud` holds `netcracker`. Any other service account token
    is a non-M2M token, and R4 then refuses it for every requested tenant.
  - (c) A service account token without that audience gets HTTP 401 with a new code.

  `example-architect` decides. Affects R2.
````

### Message to the user

I drafted ADR-0007 from the meeting notes as `docs/adr/0007-m2m-tokens-and-tenant-access.md` with the status `Proposed`. It can't move to `Accepted` until the architect settles three open points:

- **O1: where the request names its tenant.** The notes don't say, so R3 and R4 use the placeholder `<tenant source>`. If an existing record already defines this, tell me which one and I'll point the term at it.
- **O2: a non-M2M token with no `tenant-id` claim.** I assumed it gets 403 `CALLER_TENANT_MISMATCH`, because the notes say such a token never reaches another tenant.
- **O3: the audience check.** The notes say ADR-0012 R3 of example/platform gives every service account token the audience `netcracker`. That rule only covers tokens that platform services request. Also, none of the rules I was given makes token-gate check `aud`, so that part of the safety argument doesn't hold yet. Should token-gate require `aud` to hold `netcracker`?

Other points:

- **No rule for the `legacy` note.** "In `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`" is already decided by ADR-0004 R1 together with ADR-0003 R4. A second rule would state the same requirement twice, so the record states it in Context as a fact.
- **Records left unchanged.** This record adds rules but replaces none, so it changes no accepted record and the reading guide needs no change.
- **Layer tags.** I tagged every rule `verify`, following ADR-0003 R4 and ADR-0004 R5. I had no code to check this against. If the 403 comes from `internal/server`, R4 should carry `server`.
- **Links and terms.** I don't know the filenames of ADR-0003, ADR-0004, or ADR-0012 of example/platform, so the links hold `<slug>` placeholders to fill in. If ADR-0003 or ADR-0004 already defines "realm token" and "service account token", the terms should point there instead.
- **Approvers.** Who else approves besides `example-architect`? R2 relies on a rule of example/platform, so should the platform team approve it?

## Request 2

### File: docs/adr/0007-answer-failed-tokens-before-policy-evaluation.md

````markdown
# Answer a token in `Authorization` that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003](0003-<slug>.md): R4 and R9 give a token in `Authorization` the codes `TOKEN_ISSUER_UNKNOWN` and
  `TOKEN_KEYS_UNAVAILABLE`.
- [ADR-0004](0004-<slug>.md): R3 gives a token in `Authorization` the code `TOKEN_SUBJECT_INVALID`. R3 of this record adds
  a code to the refusal of R5.
- [ADR-0005](0005-<slug>.md): R2 names the HTTP status for `TOKEN_KEYS_UNAVAILABLE`, so R2 of this record does not apply
  to that code.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The accepted records name the
response for some failed checks and not for others:

- ADR-0003 R4 gives HTTP 401 with `TOKEN_ISSUER_UNKNOWN`, and ADR-0004 R3 gives HTTP 401 with `TOKEN_SUBJECT_INVALID`.
- ADR-0003 R9 gives `TOKEN_KEYS_UNAVAILABLE`. ADR-0005 R2 answers that code with HTTP 503 and `Retry-After: 5`, so that
  the client retries.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists. It names neither a
  code nor an HTTP status for a token it refuses.

None of these rules says whether a request with a token that fails verification reaches policy evaluation.

## Decision

We will answer a request whose token in `Authorization` fails verification before policy evaluation. The response is
HTTP 401 with the code of the check that failed, except where another rule names the status for that code, as ADR-0005
R2 does for `TOKEN_KEYS_UNAVAILABLE`.

### Terms

- **verification code**: an error code that a rule tagged `verify` or `keys`, in this record or in another accepted
  record, gives a token in `Authorization`. Examples: `TOKEN_ISSUER_UNKNOWN` (ADR-0003 R4), `TOKEN_KEYS_UNAVAILABLE`
  (ADR-0003 R9), `TOKEN_SUBJECT_INVALID` (ADR-0004 R3), and the code of R3.

### Rules

#### Policy evaluation

- **R1** (`server`). token-gate does not pass a request to policy evaluation when the token in `Authorization` of that
  request gets a verification code. This holds for every verification code, `TOKEN_KEYS_UNAVAILABLE` included.

#### Response

- **R2** (`server`). A request gets HTTP 401 with the code when the token in `Authorization` of that request gets a
  verification code for which no rule of an accepted record names an HTTP status. ADR-0005 R2 is one such rule: it names
  a status for `TOKEN_KEYS_UNAVAILABLE`, so R2 does not apply to that code.

#### Codes

- **R3** (`verify`). A service account token in `Authorization` that ADR-0004 R5 refuses gets the code
  `<code for ADR-0004 R5>` (O1).

### Implementation notes

Adds no requirement. Map verification codes to responses in one place in `internal/server`. Use HTTP 401 as the default,
and add an entry for each code that a rule gives another status, such as `TOKEN_KEYS_UNAVAILABLE` under ADR-0005 R2. A
table test that sends one token for each verification code and checks the status and the code covers R2. The same test
covers R1 when it also checks that the policy evaluation stub receives no call.

### Justification

Policy evaluation receives only requests whose token passed every check, so no policy has to deal with an unverified
token (R1).

One status for every failed check lets a client tell a refused credential from other errors without knowing each code.
The code names the check that failed, for the operator (R2).

`TOKEN_KEYS_UNAVAILABLE` reports a state of token-gate, not a fault of the token: the same token can pass once the keys
load. ADR-0005 R2 answers that code so that the client retries, and R2 leaves that answer in place. The request still
stops before policy evaluation, because its token has not passed verification (R1).

ADR-0004 R5 gives no code to a token it refuses, and R2 can answer the refusal only with a code (R3).

### Alternatives considered

- **A1. Pass a request with a token that fails verification to policy evaluation, and let the policy refuse it.**
  Rejected by R1: a policy that misses the case would act on an unverified token.
- **A2. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401 like the other codes.** The client would treat a key outage as a
  refused credential and would not retry.

## Consequences

Positive:

- A check that a later record adds in `verify` or `keys` gets HTTP 401 with its code without a rule of its own for the
  status (R2).

Negative:

- A service account token from a namespace that the topology file does not list gets HTTP 401 with the code of R3. A
  client that handles the response it gets today for such a token gets a different answer (R2, R3).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0004 that names R3 of this record as an
  addition to ADR-0004 R5.

## Open points

- **O1.** The code that a service account token gets when ADR-0004 R5 refuses it, such as `TOKEN_NAMESPACE_UNLISTED`. If
  another record already names a code for that refusal, R3 is dropped. `example-architect` decides. Affects R3.
````

### Message to the user

I drafted ADR-0007 from the meeting notes as `docs/adr/0007-answer-failed-tokens-before-policy-evaluation.md` with the status `Proposed`. Open point O1 blocks acceptance: what code does a service account token get when ADR-0004 R5 refuses it? R5 names no code, so the record can't answer that refusal "with the code of the check that failed" until one exists. R3 holds the placeholder `<code for ADR-0004 R5>` until then. Do the other records have more checks without a code? If so, each one needs a code the same way.

Other points:

- **R2 is a default.** It covers only codes that no other rule gives an HTTP status. This keeps it from repeating ADR-0003 R4 and ADR-0004 R3, which already say 401. ADR-0005 R2 falls outside R2 for the same reason, so the exception for `TOKEN_KEYS_UNAVAILABLE` needs no separate precedence clause.
- **R1 covers the 503 case too.** I read "instead" as replacing only the response, so a `TOKEN_KEYS_UNAVAILABLE` request also stops before policy evaluation. Please confirm this with the architect.
- **No rule for a missing token.** The notes cover only a token that is in `Authorization`, so the record has no rule for a request without a token.
- **Records left unchanged.** ADR-0004 stays as it is. Once this record is accepted, ADR-0004 gains a line under **Related ADRs** (listed in Follow-ups). The reading guide needs no change.
- **Layer tags.** I tagged R1 and R2 `server`, following ADR-0005 R2, and R3 `verify`, following ADR-0004 R5. I had no code to check this against, so please confirm where the responses are built.
- **Links.** I don't know the filenames of ADR-0003, ADR-0004, or ADR-0005, so the links hold `<slug>` placeholders to fill in.
- **Approvers.** Who else approves besides `example-architect`?
