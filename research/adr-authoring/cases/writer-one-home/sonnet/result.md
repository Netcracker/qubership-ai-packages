## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Treat realm tokens with `ROLE_M2M` and service account tokens as M2M tokens, and limit every other token to its own tenant

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title>](<link>): the unknown-issuer result for a token whose provider is not in the providers file (R4).
- [ADR-0004: <title>](<link>): the providers of each `M2M_AUTH_MODE` (R1), the subject check (R3), and the namespace check (R5) for a service account token.

## Context

token-gate checks the token of each request before policy evaluation. Two kinds of token reach it: a realm token and a
service account token. A request names a tenant, and a token that is not allowed to reach that tenant must not reach it.

In the mode `legacy`, the providers file holds no provider of service account tokens. A service account token therefore
fails the unknown-issuer check and never becomes a verified token there.

## Decision

We will treat a verified realm token with the role `ROLE_M2M` and every verified service account token as an M2M token.
An M2M token may name any tenant, and every other token may reach only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **verified token**: a token in `Authorization` that fails no verification check of the `verify` and `keys` layers.
- **M2M token**: a token that R1 or R2 declares an M2M token.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A verified realm token is an M2M token when its `realm_access.roles` claim holds `ROLE_M2M`. A
  verified realm token whose `realm_access.roles` claim lacks `ROLE_M2M`, or that has no such claim, is not an M2M
  token.
- **R2** (`verify`). A verified service account token is an M2M token.

#### Tenant access

- **R3** (`verify`). A request whose token in `Authorization` is an M2M token may name any tenant, and the request gets
  no `CALLER_TENANT_MISMATCH` for the tenant it names.
- **R4** (`verify`). A request whose verified token is not an M2M token, and that names in <tenant source> a tenant
  other than the value of the `tenant-id` claim of that token, gets HTTP 403 with `CALLER_TENANT_MISMATCH`. A token with
  no `tenant-id` claim has no tenant of its own, so every tenant that its request names is another tenant.

### Justification

A service account token can be an M2M token without further checks (R2), because the subject check of ADR-0004 R3 refuses
a token whose `sub` is not a service account, and the namespace check of ADR-0004 R5 accepts a token only from a listed
namespace. A realm token marks itself as an M2M token through the role that Keycloak puts in `realm_access.roles` (R1).
A token that is not an M2M token carries one tenant in its `tenant-id` claim, and limiting it to that tenant keeps it
from reaching any other (R3, R4).

### Alternatives considered

- **A1. Limit every token to the tenant of its `tenant-id` claim, M2M tokens included.** Rejected by R3: an M2M token
  must be able to name any tenant.
- **A2. Treat only a realm token with `ROLE_M2M` as an M2M token, so that a service account token is limited to a
  tenant.** Rejected by R2: the checks of ADR-0004 R3 and R5 already limit which service account tokens are accepted.

## Consequences

Negative:

- A realm token that holds `ROLE_M2M`, and any service account token from a listed namespace, can reach every tenant, so
  granting either is a grant over all tenants (R1, R2, R3).

## Open points

- **O1.** Where does a request name its tenant (a header, a path segment, or a request field)? `example-architect`
  decides. The answer fills the placeholder in R4.
- **O2.** Assumption in R4: a token that is not an M2M token and has no `tenant-id` claim gets `CALLER_TENANT_MISMATCH`
  for every tenant. The alternative is another response for that token. `example-architect` decides. This affects R4.
- **O3.** Assumption: the `verify` layer produces the 403 of R4 and decides which token is an M2M token. The alternative
  is that the `server` layer applies the tenant check after verification. The maintainer of `internal/verify` and
  `internal/server` decides. This affects the layer tags of R1 to R4.
````

### Message to the user

I wrote `docs/adr/0007-m2m-tokens-and-tenant-access.md` with the status `Proposed`. It has no Date heading and has open points, so it stays `Proposed` until they are settled and the team signs off.

- **Legacy mode needs no rule.** A service account token in the mode `legacy` gets `TOKEN_ISSUER_UNKNOWN` through ADR-0003 R4 and ADR-0004 R1. I recorded that as a fact in Context. I also suggest a test for it.
- **Open points.** O1 is the question I need answered: where does a request name its tenant? The notes don't say, so R4 holds a visible placeholder, `<tenant source>`. O2 and O3 are assumptions: how a token with no `tenant-id` claim is handled, and which layer produces the 403. Without the code I tagged R1 to R4 `verify`.
- **Placeholders.** I don't have the titles or filenames of ADR-0003 and ADR-0004, so the Related ADRs links are `<title>` and `<link>` placeholders. Please fill them in.
- **Terms.** I defined "realm token" and "service account token" here. If an earlier record already owns them, replace the definitions with a pointer to that record.
- **Alternatives and reasons.** The notes gave no alternatives, and the only reason they gave was the safety of service account tokens (the Justification for R2). A1 and A2 are derived from the decision. Please confirm them, or give me the tenant-limit reasons the meeting discussed.
- **Existing behavior.** Does R4 change what any existing caller gets? If it does, I'll add a rule for upgrading installations and cite it under Negative.
- **Other records.** I changed no other file. ADR-0003 and ADR-0004 stay as they are. The reading guide needs no edit. Code that implements this record must end its commit message and pull request description with the `Implements` trailer.

## Request 2

### File: docs/adr/0007-token-verification-failure-response.md

````markdown
# Refuse a token in `Authorization` that fails verification with HTTP 401 before policy evaluation, except where the client should retry

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0003: <title>](<link>): the unknown-issuer result (R4), as one check that gives a response of its own.
- [ADR-0004: <title>](<link>): the subject check (R3), as one check that gives a response of its own.
- [ADR-0005: <title>](<link>): the response to a request whose token gets `TOKEN_KEYS_UNAVAILABLE` (R2).

## Context

Each verification check gives a failing token an error code. The records state the response to a failure check by check:
ADR-0003 R4 and ADR-0004 R3 give HTTP 401, and ADR-0005 R2 gives a response that makes the client retry when a provider
has no keys. A token can fail more than one check.

## Decision

We will refuse a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed,
before policy evaluation. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead, so that
the client retries.

### Terms

- **verification check**: a check that code in the `verify` or `keys` layer applies to a token in `Authorization`, and
  for which an accepted record names an error code.

### Rules

#### Response to a failed verification check

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails a verification check does not reach
  policy evaluation.
- **R2** (`verify`, `server`). A request whose token in `Authorization` fails a verification check gets HTTP 401 with
  the error code of that check, except where the error code is `TOKEN_KEYS_UNAVAILABLE`. The response to a request whose
  token gets `TOKEN_KEYS_UNAVAILABLE` is the one that ADR-0005 R2 gives.
- **R3** (`verify`, `keys`). A request whose token in `Authorization` fails more than one verification check gets the
  error code of <the check that takes precedence>.

### Justification

A token that fails verification is not trusted, so no request that carries it may reach policy evaluation (R1). The
client can fix a rejected token only by sending another, so it gets the code of the failed check with HTTP 401 (R2). A
provider without keys is a condition that can pass, so the client gets the response that makes it retry, and a 401 would
tell it to give up (R2). Two failed checks give two codes, and one response needs one of them (R3).

### Alternatives considered

- **A1. Send HTTP 401 for every failed verification check, `TOKEN_KEYS_UNAVAILABLE` included.** Rejected by R2: the
  client would not retry when the keys return.

## Consequences

Negative:

- ADR-0003 R4 and ADR-0004 R3 already give a 401 for their own checks, so R2 states that result a second time for
  those checks. A later change to the status of a 401 needs a record that replaces R2 and those two rules.

## Open points

- **O1.** Which error code does a token get when it fails more than one verification check: the code of the first check
  in the order of the code, the code of a fixed order of checks, or `TOKEN_KEYS_UNAVAILABLE` before any other? Where it
  comes first, the client retries a token that another check would also refuse. `example-architect` decides. The answer
  fills the placeholder in R3.
- **O2.** Assumption in the definition of verification check: every check of `verify` and `keys` has an error code in an
  accepted record. A check with no recorded code is outside R2 and R3. The alternative is a generic code for such a
  check. `example-architect` decides. This affects R2 and R3.
````

### Message to the user

I wrote `docs/adr/0007-token-verification-failure-response.md` with the status `Proposed`. It has open points, so it stays `Proposed` until they are settled and the team signs off.

- **Question for the architect (O1).** The notes don't say which code wins when a token fails two checks, for example the subject check and the keys check. R3 holds a visible placeholder until they answer. O2 asks whether every check has a recorded code.
- **Overlap with existing rules.** ADR-0003 R4 and ADR-0004 R3 already give a 401 for their checks, and ADR-0005 R2 already gives the retry response. R2 is the general form of that result, and it cites ADR-0005 R2 only as its exception. I listed the overlap under Negative. If you prefer one home, the alternative is to limit R2 to checks whose own rule gives no response. Tell me and I'll rewrite it.
- **Layers.** Without the code, I tagged R1 and R2 `verify` and `server`, and R3 `verify` and `keys`. Please confirm them.
- **Placeholders.** I don't have the titles or filenames of ADR-0003, ADR-0004, and ADR-0005, so the Related ADRs links are `<title>` and `<link>` placeholders. Please fill them in.
- **Alternatives.** The notes gave no alternative, so A1 is derived from the exception. Please confirm it.
- **Other records.** I changed no other file. The existing records stay as they are, and the reading guide needs no edit. Code that implements this record must end its commit message and pull request description with the `Implements` trailer.
