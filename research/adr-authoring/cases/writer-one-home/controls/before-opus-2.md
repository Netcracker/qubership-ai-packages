## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let an M2M token reach any tenant, and limit every other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- ADR-0003: R4 gives a token whose `iss` names no provider HTTP 401 with `TOKEN_ISSUER_UNKNOWN`. This record uses
  that rule in its Context.
- ADR-0004: R1 sets which providers the providers file holds in each mode. R3 and R5 limit which service account
  tokens pass verification. R2 of this record depends on R3 and R5.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. It accepts realm tokens and
service account tokens. Some callers act for one tenant. Other callers are services that act for every tenant. No
accepted record says which tokens may reach which tenant.

These facts bear on the decision:

- ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists.
- ADR-0012 R3 of example/platform states that every service account token that a service of the platform requests
  carries the audience `netcracker`. That rule covers only the tokens that a service of the platform requests. No rule
  of this repository makes token-gate check the `aud` claim of a service account token (O1).
- In the mode `legacy`, ADR-0004 R1 leaves the providers file with no provider of service account tokens. So ADR-0003
  R4 gives every service account token HTTP 401 with `TOKEN_ISSUER_UNKNOWN`, and R2 of this record applies only in the
  mode `k8s`.

## Decision

We will treat a realm token that holds the role `ROLE_M2M`, and every service account token, as M2M tokens. An M2M
token may reach any tenant, and any other token may reach only the tenant of its own `tenant-id` claim.

### Terms

- **realm token**: a token that Keycloak signs for a realm.
- **service account token**: a token that the Kubernetes API server signs for a service account.
- **passes verification**: a token in `Authorization` passes verification when no rule of ADR-0003 or ADR-0004 refuses
  it or gives it an error code.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token.
- **target tenant**: the tenant that a request names in `<where a request names its tenant>` (O2).

### Rules

#### M2M tokens

- **R1** (`verify`). A realm token in `Authorization` that passes verification is an M2M token when its
  `realm_access.roles` claim holds the value `ROLE_M2M`. Any other realm token is not an M2M token.
- **R2** (`verify`). A service account token in `Authorization` that passes verification is an M2M token.

#### Tenant access

- **R3** (`verify`). A request with an M2M token in `Authorization` never gets `CALLER_TENANT_MISMATCH`, whatever its
  target tenant is. token-gate compares the target tenant of that request with no claim of the token.
- **R4** (`verify`). A request with a token in `Authorization` that passes verification and is not an M2M token gets
  HTTP 403 with `CALLER_TENANT_MISMATCH` before policy evaluation in two cases: the token has no `tenant-id` claim, or
  the value of its `tenant-id` claim differs from the target tenant of the request.

### Implementation notes

Adds no requirement. Let `verify` return whether the token is an M2M token along with its claims. The tenant check can
then read one flag, and it does not need to know which provider signed the token.

### Justification

A service that acts for every tenant needs one token that reaches all of them. With `ROLE_M2M`, a Keycloak
administrator can give a realm client that access without a new kind of token (R1). A service account token carries no
`tenant-id` claim, so under R4 it would reach no tenant unless it is an M2M token. ADR-0004 R3 and R5 limit the service
account tokens that pass verification to service accounts in namespaces that the topology file lists, so R2 extends
access to every tenant only to those service accounts (R2). token-gate compares `tenant-id` before policy evaluation,
so a token that is not an M2M token does not reach another tenant even where a policy leaves out the tenant check (R4).

### Alternatives considered

- **A1. Leave the tenant check of a token that is not an M2M token to policy evaluation.** Rejected by R4: a policy
  that leaves out the check would let that token reach another tenant.

## Consequences

Positive:

- A service in a namespace that the topology file lists can call any tenant with its own service account token, and
  needs no Keycloak client of its own (R2, R3).

Negative:

- A realm client that holds `ROLE_M2M` reaches every tenant. Granting the role in Keycloak grants access to the data of
  all tenants (R1, R3).
- Any service account in a listed namespace reaches every tenant, whatever audience its token carries, until O1 is
  settled (R2, R3).
- Policy evaluation can no longer give a token that is not an M2M token access to another tenant (R4).

## Open points

- **O1.** The audience of a service account token. ADR-0012 R3 of example/platform covers only the tokens that a
  service of the platform requests, and token-gate checks no `aud` claim. So a pod in a listed namespace can present a
  service account token with another audience, such as the default audience of the API server, and R2 makes it an M2M
  token. The answers under consideration:
  - (a) R2 as written: every service account token that passes verification is an M2M token.
  - (b) A service account token is an M2M token only when its `aud` claim holds `netcracker`. Any other service account
    token falls under R4, which gives it HTTP 403 because it has no `tenant-id` claim.
  - (c) As in (b), but a service account token whose `aud` claim does not hold `netcracker` fails verification with
    HTTP 401 and a code of its own.

  `example-architect` decides. Affects R2 and R4.
- **O2.** Where a request names its target tenant: a header, a path segment, or a field of the policy input.
  `example-architect` decides. Affects the term **target tenant**, and through it R3 and R4.
- **O3.** A token that is not an M2M token and has no `tenant-id` claim. R4 assumes that it gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every target tenant. The other answer is that it fails verification with HTTP 401 and a
  code of its own, because it lacks a claim that token-gate needs. `example-architect` decides. Affects R4.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Three open points block acceptance:

- **O1 (audience).** The notes say ADR-0012 R3 of example/platform gives every service account token the audience `netcracker`. That rule only covers tokens that a platform service requests, though, and token-gate doesn't check `aud`. As drafted, R2 makes any service account token from a listed namespace an M2M token, whatever its audience. That includes the default token of an API server. Should R2 require `aud` to hold `netcracker`? And if it doesn't, should such a token get 403 (answer b) or 401 (answer c)?
- **O2 (target tenant).** Where does a request name the tenant it wants to reach? I used a visible placeholder in the term **target tenant**.
- **O3 (no `tenant-id`).** Should a non-M2M token with no `tenant-id` claim get 403 `CALLER_TENANT_MISMATCH`, as R4 assumes, or 401 with its own code?

There's no rule for the note "in the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`." ADR-0004 R1 together with ADR-0003 R4 already produces that result, so the record states it as a fact in Context.

Questions:

- Who besides `example-architect` approves this record, such as a security owner or the owner of the Keycloak realms?
- The filename `0007-m2m-tokens-and-tenant-access.md` assumes the `NNNN-slug.md` pattern. Does that match records 0001 to 0006?
- Under **Related ADRs**, ADR-0003 and ADR-0004 have no titles or links because I don't have their filenames. Can you add them, or send me the filenames?
- Which layer produces the HTTP 403 today? I tagged R3 and R4 `verify`, but if `server` produces the response, the tag should change.

## Request 2

### File: docs/adr/0007-failed-token-verification-gets-http-401.md

````markdown
# Answer a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 and R2.

### Related ADRs

- ADR-0003: R4 and R9 are checks whose failure R1 of this record answers.
- ADR-0004: R3 and R5 are checks whose failure R1 of this record answers. R2 of this record gives R5 an error code.
- ADR-0005: R2 gives the response to a request whose token gets `TOKEN_KEYS_UNAVAILABLE`, and R1 of this record leaves
  that response in place.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. ADR-0003 and ADR-0004 state
the checks. Some of them name a status and a code:

- ADR-0003 R4 gives a token whose `iss` names no provider HTTP 401 with `TOKEN_ISSUER_UNKNOWN`.
- ADR-0004 R3 gives a service account token whose `sub` does not start with `system:serviceaccount:` HTTP 401 with
  `TOKEN_SUBJECT_INVALID`.
- ADR-0003 R9 gives a token whose provider has had no keys since the start `TOKEN_KEYS_UNAVAILABLE`. ADR-0005 R2 gives
  a request with that code HTTP 503 with `Retry-After: 5`.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists. It names no status
  and no code for a token from another namespace.

No accepted record states one status for every failed check, or says that a request with a failed token stops before
policy evaluation.

## Decision

We will answer a token in `Authorization` that fails verification with HTTP 401 and the code of the failed check, before
policy evaluation. The exception is a token that gets `TOKEN_KEYS_UNAVAILABLE`, which keeps the response of ADR-0005 R2.

### Terms

- **fails verification**: a token in `Authorization` fails verification when a rule of ADR-0003 or ADR-0004 refuses it
  or gives it an error code.

### Rules

#### Response to a failed verification

- **R1** (`verify`, `server`). A request whose token in `Authorization` fails verification gets HTTP 401 with the error
  code of a check that the token failed, and token-gate does not pass that request to policy evaluation. The exception
  is a request whose token gets `TOKEN_KEYS_UNAVAILABLE`, which gets the response of ADR-0005 R2 instead of HTTP 401.

#### Error codes

- **R2** (`verify`). A service account token in `Authorization` that ADR-0004 R5 refuses gets the error code
  `<code for a namespace that the topology file does not list>`.

### Implementation notes

Adds no requirement. Let each check in `verify` return its error code, and let `server` map codes to statuses in one
place: `TOKEN_KEYS_UNAVAILABLE` to the response of ADR-0005 R2, and every other code to HTTP 401. A table test over
every code then covers R1.

### Justification

HTTP defines 401 as the status for a request without valid credentials. It tells the client to get a new token rather
than send the same one again (R1). The code tells the client and the operator which check failed, such as an unknown
issuer or an unlisted namespace (R1, R2). Stopping the request before policy evaluation means that policy never reads
the claims of a token that token-gate did not verify (R1). `TOKEN_KEYS_UNAVAILABLE` describes the state of token-gate,
not of the token, and it clears once the provider's keys load. So the client gets HTTP 503 and retries (R1, ADR-0005
R2).

### Alternatives considered

- **A1. Return HTTP 403 for a token whose signature is valid but whose claims fail a check, such as `sub` or the
  namespace.** Rejected by R1: every failed check gets one status, and the code identifies the check.
- **A2. Pass a token that fails verification to policy evaluation with a flag, and let policy decide.** Rejected by R1.
- **A3. Return HTTP 401 for `TOKEN_KEYS_UNAVAILABLE` too.** Rejected by R1 and ADR-0005 R2: the client would discard a
  valid token instead of retrying.

## Consequences

Negative:

- A service account token from a namespace that the topology file does not list gets HTTP 401 although the token itself
  is valid. A new token does not fix it, and only an entry in the topology file does (R1, R2).
- Under the reading of R1 that O2 names, a token that fails another check and also gets `TOKEN_KEYS_UNAVAILABLE` may get
  HTTP 503. The client then retries a token that will fail once the keys load (R1).

## Open points

- **O1.** The error code of R2. ADR-0004 R5 names no code for a service account token from a namespace that the
  topology file does not list. `example-architect` decides. Affects R2.
- **O2.** A token that fails more than one check. R1 assumes that token-gate reports the code of any one of them. The
  answers under consideration:
  - (a) Any one of them, as R1 reads.
  - (b) A code other than `TOKEN_KEYS_UNAVAILABLE` wins, so a token that will fail anyway gets HTTP 401 and no retry.
  - (c) `TOKEN_KEYS_UNAVAILABLE` wins, so the client always retries while keys are missing.

  `example-architect` decides. Affects R1.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Two open points block acceptance:

- **O1.** ADR-0004 R5 rejects a service account token from a namespace that isn't listed, but it names no error code, so "the code of the check that failed" doesn't exist for that check yet. What code should it be? R2 holds a visible placeholder until you decide.
- **O2.** What happens when a token fails more than one check, and one of them is `TOKEN_KEYS_UNAVAILABLE`? Should it get 401 or 503? R1 currently lets token-gate report any one of the failed codes.

ADR-0003, ADR-0004, and ADR-0005 stay as they are. The new record only adds to them, and R1 matches the 401 responses that ADR-0003 R4 and ADR-0004 R3 already give.

Questions:

- Who besides `example-architect` approves this record?
- The filename `0007-failed-token-verification-gets-http-401.md` assumes the `NNNN-slug.md` pattern. Does that match records 0001 to 0006?
- Under **Related ADRs**, the records have no titles or links because I don't have their filenames. Can you add them, or send me the filenames?
- The notes don't cover a request with no token in `Authorization`, so no rule here covers it. Is that settled elsewhere, or should this record cover it?
