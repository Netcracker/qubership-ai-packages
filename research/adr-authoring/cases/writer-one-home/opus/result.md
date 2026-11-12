## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let an M2M token reach every tenant, and any other token only the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title>](0003-<slug>.md): the checks that make a token in `Authorization` a verified token, among them
  the issuer check of ADR-0003 R4.
- [ADR-0004: <title>](0004-<slug>.md): the checks that make a service account token a verified token, among them the
  `sub` check of ADR-0004 R3 and the namespace check of ADR-0004 R5, and the provider rule of ADR-0004 R1 for the modes
  of `M2M_AUTH_MODE`.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Two kinds of tokens reach it.
Keycloak signs realm tokens for a realm, and the Kubernetes API server signs service account tokens for a service
account. A realm token lists the realm roles of its caller in `realm_access.roles`, and a token names the tenant of its
caller in the `tenant-id` claim. A request names the tenant it targets in `<tenant source>`.

Some callers are services that act for every tenant. These callers need tokens that reach every tenant. Every other
caller acts for one tenant.

## Decision

We will treat a service account token, and a realm token whose `realm_access.roles` holds `ROLE_M2M`, as an M2M token
that may reach every tenant. Every other token reaches only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token is an M2M token.
- **verified token**: a token in `Authorization` that passes every check that the rules of ADR-0003 and ADR-0004 apply
  to it.
- **target tenant**: the tenant that a request names in `<tenant source>`.

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token in `Authorization` is an M2M token when its `realm_access.roles` claim holds
  `ROLE_M2M`. A realm token in `Authorization` whose `realm_access.roles` claim is missing or does not hold `ROLE_M2M`
  is not an M2M token.
- **R2** (`verify`). Every service account token in `Authorization` is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is a verified token and an M2M token gets no
  `CALLER_TENANT_MISMATCH`, whatever target tenant it names.
- **R4** (`verify`). A request whose token in `Authorization` is a verified token but not an M2M token gets HTTP 403
  with `CALLER_TENANT_MISMATCH` when it names a target tenant other than the token's `tenant-id` claim. The same
  applies when it names any target tenant and the token has no `tenant-id` claim.

### Implementation notes

Adds no requirement. Decide whether a token is an M2M token once, after verification. Then pass that result with the
verified claims to the tenant check.

### Justification

`ROLE_M2M` in `realm_access.roles` marks a realm token as an M2M token, so the administrators of the realm decide which
clients get one (R1).

A service account token is an M2M token without any role. R3 and R4 apply only to a verified token, and the `sub` check
of ADR-0004 R3 and the namespace check of ADR-0004 R5 limit which service account tokens are verified (R2, R3).

R2 needs no exception for the mode `legacy`. In that mode, under the provider rule of ADR-0004 R1, a service account
token fails the issuer check of ADR-0003 R4, so it never becomes a verified token.

R4 compares the target tenant with the token's own `tenant-id` claim, so a token that is not an M2M token reaches no
tenant other than its own.

### Alternatives considered

- **A1. Require `ROLE_M2M` or another role on a service account token before it counts as an M2M token.** Rejected by
  R2: the checks of ADR-0004 already limit which service account tokens are verified.
- **A2. Let every token reach only the tenant of its `tenant-id` claim, M2M tokens included.** Rejected by R3: a
  service that acts for every tenant would need a separate token for each tenant.

## Consequences

Negative:

- Every service account token that passes the checks of ADR-0004 reaches every tenant (R2, R3). A service account
  cannot be limited to one tenant.
- A client that uses a realm token to act for several tenants needs `ROLE_M2M`. Without it, every tenant other than
  the one in its `tenant-id` claim gets `CALLER_TENANT_MISMATCH` (R1, R4).
- A verified token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH` for every target
  tenant (R4).

## Open points

- **O1.** Where does a request name its target tenant: in a header, in a path segment, or somewhere else?
  `<tenant source>` stays a placeholder until `example-architect` decides. Affects the term **target tenant**, R3, and R4.
- **O2.** R4 assumes that a verified token with no `tenant-id` claim and no M2M status gets `CALLER_TENANT_MISMATCH`.
  The other answer is HTTP 401 with a verification code. `example-architect` decides. Affects R4.
- **O3.** R3 and R4 assume that verification runs before the tenant check. Under that assumption, a token that fails
  verification gets the response of the check it failed, not `CALLER_TENANT_MISMATCH`. The other answer lets
  `CALLER_TENANT_MISMATCH` win. `example-architect` decides. Affects R3 and R4.
````

### Message to the user

I wrote ADR-0007 at `docs/adr/0007-m2m-tokens-and-tenant-access.md` with the status `Proposed`. The open points O1 to O3 block acceptance:

- **O1:** Where does a request name its target tenant? Is it a header, a path segment, or somewhere else? Until you decide, the rules use the placeholder `<tenant source>`.
- **O2:** Should a verified token that is not M2M and has no `tenant-id` claim get `CALLER_TENANT_MISMATCH` (my assumption), or HTTP 401?
- **O3:** Should verification run before the tenant check, so that a token that fails verification never gets `CALLER_TENANT_MISMATCH` (my assumption)?

Two statements from the notes have no rule of their own. The rules already produce both outcomes, and a second rule would state the same requirement twice:

- "A token that is not M2M never reaches another tenant" follows from R4.
- "In the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`" follows from ADR-0004 R1 and ADR-0003 R4. The Justification explains why R2 needs no exception for that mode.

The notes justify the service account case with ADR-0004 R3 and R5. The record cites those checks by number and subject only, so their conditions stay in ADR-0004.

Please check:

- **Owner:** I set it to `example-architect` because they made the decision. Is that right, and should anyone else approve?
- **Links:** Under **Related ADRs**, the titles and filenames of ADR-0003 and ADR-0004 are placeholders. Please give me the real ones.
- **Terms:** I defined **realm token** and **service account token** here. If ADR-0003 or ADR-0004 already defines them, which record is it? I'd replace my definitions with a pointer to it.
- **Layers:** I tagged R3 and R4 `verify` because the existing 401 rules sit there. If the tenant check belongs in `internal/server`, the tag should be `server`.
- **Reasons:** The reasons in **Justification** and **Alternatives considered** are mine, not from the notes. Please confirm them with `example-architect`.

## Request 2

### File: docs/adr/0007-http-401-for-failed-token-verification.md

````markdown
# Answer a token in `Authorization` that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title>](0003-<slug>.md): checks of verification, among them the keys check of ADR-0003 R9, which R1
  excepts.
- [ADR-0004: <title>](0004-<slug>.md): checks of verification. R2 adds an error code to the namespace check of
  ADR-0004 R5.
- [ADR-0005: <title>](0005-<slug>.md): R1 gives a token that gets `TOKEN_KEYS_UNAVAILABLE` the response of ADR-0005 R2.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. The rules of ADR-0003 and
ADR-0004 state these checks. Some of the rules name an HTTP status and an error code, such as the issuer check of
ADR-0003 R4 and the `sub` check of ADR-0004 R3. The namespace check of ADR-0004 R5 names neither. The keys check of
ADR-0003 R9 names an error code, and ADR-0005 R2 states the response for that code.

## Decision

We will answer a token in `Authorization` that fails verification with HTTP 401 and the code of the failed check,
before policy evaluation. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead.

### Terms

- **service account token**: a token that the Kubernetes API server signs for a service account.
- **verification**: the checks that the rules of ADR-0003 and ADR-0004 apply to a token in `Authorization`. A rule
  that applies to the providers file at the start, such as the provider rule of ADR-0004 R1, is not a check of
  verification.

### Rules

#### Response to a failed check

- **R1** (`verify`). A token in `Authorization` that fails a check of verification gets HTTP 401 with the error code
  that the rule of that check names. A token in `Authorization` that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of
  ADR-0005 R2 instead.
- **R2** (`verify`). A service account token in `Authorization` that fails the namespace check of ADR-0004 R5 gets the
  error code `<namespace error code>`.
- **R3** (`verify`). A token in `Authorization` that fails more than one check of verification gets the response that
  R1 gives for one of the failed checks.

#### Policy evaluation

- **R4** (`server`). A request whose token in `Authorization` fails a check of verification does not reach policy
  evaluation.

### Implementation notes

Adds no requirement. Let each check in `internal/verify` return its error code, and let `internal/server` map the code
to the response. `TOKEN_KEYS_UNAVAILABLE` maps to the response of ADR-0005 R2, and every other code maps to HTTP 401.

### Justification

The error code tells a client which check its token failed, so the client can fix the token (R1, R2). A token that
gets `TOKEN_KEYS_UNAVAILABLE` can pass once the keys of its provider load. That token gets the response of ADR-0005
R2, so the client retries instead of discarding the token (R1). Policy evaluation sees only tokens that passed every
check of verification (R4).

### Alternatives considered

- **A1. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** Rejected by R1: the client
  would treat the token as invalid and would not retry.
- **A2. Pass a request whose token fails verification to policy evaluation, and let the policy deny it.** Rejected by
  R4: the policy would then decide on claims that no check confirmed.

## Consequences

Negative:

- A service account token that fails the namespace check of ADR-0004 R5 gets HTTP 401 with `<namespace error code>`
  (R1, R2). ADR-0004 R5 states no response for that token, so a client that handles the response it gets today has to
  handle this one.
- A token that fails several checks can get a different error code after a change to the order of the checks (R3).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0004 that names R2 of this record as adding the
  error code of ADR-0004 R5. Also add a line to ADR-0003 and ADR-0004 that names R1 of this record as adding the HTTP
  status of their checks.

## Open points

- **O1.** Which error code does a service account token get when it fails the namespace check of ADR-0004 R5?
  `example-architect` decides. Until then, R2 holds the placeholder `<namespace error code>`. Affects R2.
- **O2.** Does any other check of ADR-0003 or ADR-0004 name no error code? Each such check needs a code in a rule like
  R2, or R1 has no code to send for it. `example-architect` decides. Affects R1.
- **O3.** R3 assumes that a token that fails several checks may get the response of any one of them. Other answers
  are a fixed order of the checks, or `TOKEN_KEYS_UNAVAILABLE` winning over every other code, or losing to every other
  code. `example-architect` decides. Affects R3.
````

### Message to the user

I wrote ADR-0007 at `docs/adr/0007-http-401-for-failed-token-verification.md` with the status `Proposed`. The open points O1 to O3 block acceptance:

- **O1:** Which error code should a token get when it fails the namespace check of ADR-0004 R5? That rule names no code, so R2 uses the placeholder `<namespace error code>`.
- **O2:** Do any other checks in ADR-0003 or ADR-0004 lack an error code? I can see only the rules the notes cite. Each such check needs a code before R1 is complete.
- **O3:** Which response should a token get when it fails several checks? R3 assumes any one of the failed checks may supply it.

ADR-0004 is accepted, so it stays as it is. R2 of the new record adds the error code for ADR-0004 R5. After acceptance, ADR-0004 gets only a line under **Related ADRs**, and ADR-0003 gets one for R1, as **Follow-ups** describes.

R1 states the exception for `TOKEN_KEYS_UNAVAILABLE` as "gets the response of ADR-0005 R2". It doesn't repeat the status or the `Retry-After` value, so those stay in ADR-0005.

R4 says that a failed token never reaches policy evaluation. I took "before policy evaluation" in the notes to mean that, and to cover the 503 case as well.

Please check:

- **Owner:** I set it to `example-architect` because they made the decision. Is that right, and should anyone else approve?
- **Links:** The titles and filenames under **Related ADRs** are placeholders. Please give me the real ones.
- **Terms:** I defined **service account token** here. If ADR-0004 already defines it, I'd replace my definition with a pointer.
- **Reasons:** The reasons in **Justification** and in A2 are mine, not from the notes. Please confirm them with `example-architect`.
