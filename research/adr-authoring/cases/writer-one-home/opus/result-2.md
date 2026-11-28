## Request 1

### File: docs/adr/0007-let-m2m-tokens-reach-any-tenant.md

````markdown
# Let M2M tokens reach any tenant, and other tokens only the tenant of their `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0004: <title>](./0004-<slug>.md): the subject check (R3) and the namespace check (R5) for service account
  tokens, which the Justification of R2 relies on.
- [example/platform ADR-0012: <title>](https://github.com/example/platform/blob/main/docs/adr/0012-<slug>.md): the
  audience of the service account tokens that services of the platform request (R3), which the Justification of R2 and
  O3 cite.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. That token is a realm token or
a service account token. Some callers are services that act for every tenant. Other callers act for one tenant, and
their token carries that tenant in its `tenant-id` claim. No record decides which tokens may address a tenant other
than the one in their `tenant-id` claim.

## Decision

We will treat a realm token with the realm role `ROLE_M2M`, and every service account token, as an M2M token that may
address any tenant. Every other token may address only the tenant of its `tenant-id` claim.

### Terms

- **realm token**: a token in `Authorization` that Keycloak signs for a realm.
- **service account token**: a token in `Authorization` that the Kubernetes API server signs for a service account.
- **verification**: every check that `verify` and `keys` run on a token in `Authorization`. A token passes
  verification when it fails none of them.
- **M2M token**: a token in `Authorization` that R1 or R2 makes an M2M token. No other token is an M2M token.
- **target tenant**: the tenant that a request names in `<where a request names its tenant>`. A request that names no
  tenant there has no target tenant.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A realm token is an M2M token when its claim `realm_access.roles` is an array with an element equal
  to `ROLE_M2M`, compared case-sensitively. A role in any other claim, such as `resource_access`, does not make a realm
  token an M2M token.
- **R2** (`verify`). Every service account token is an M2M token.

#### Tenant access

- **R3** (`verify`). token-gate answers HTTP 403 with `CALLER_TENANT_MISMATCH` to a request that has a target tenant
  when its token in `Authorization` passes verification, is not an M2M token, and either has no `tenant-id` claim or
  has a `tenant-id` claim that differs from the target tenant.
- **R4** (`verify`). token-gate refuses no request because of its target tenant when the token in `Authorization` of
  the request passes verification and is an M2M token.

### Justification

A service that acts for every tenant needs a token that reaches each of them. A token that is not an M2M token belongs
to one tenant and must never reach another one (R3, R4).

R2 relies on the subject check of ADR-0004 R3 and the namespace check of ADR-0004 R5. Together they limit service
account tokens to workloads in the namespaces that the topology file lists. The audience rule of example/platform
ADR-0012 R3 binds the services of the platform. O3 asks whether token-gate also checks that audience.

## Consequences

Negative:

- Anyone who can assign the realm role `ROLE_M2M` in a Keycloak realm can give a token access to every tenant (R1).
  Assigning that role becomes a permission across tenants.
- Every workload in a namespace that the topology file lists reaches every tenant, including a workload that acts for
  one tenant (R2). Adding a namespace to the topology file grants that access.
- A client that addresses another tenant with a token that is not an M2M token gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` (R3). The same applies to a token that is not an M2M token and has no `tenant-id` claim.
  Clients that token-gate passed on to policy evaluation in these cases before now fail.

## Open points

- **O1.** Where does a request name its target tenant: a header, a path segment, or a field of the policy input? The
  term **target tenant** holds a placeholder until `example-architect` decides. This affects R3 and R4.
- **O2.** R3 assumes that a token that is not an M2M token and has no `tenant-id` claim gets HTTP 403 with
  `CALLER_TENANT_MISMATCH` for every target tenant. The other answer is HTTP 401 with a code of verification.
  `example-architect` decides. This affects R3.
- **O3.** The rules that R2 relies on do not check the `aud` claim of a service account token. The audience rule of
  example/platform ADR-0012 R3 binds the services of the platform, but not every workload that can get a service
  account token in a listed namespace. The answers under consideration are:
  - Add a rule that `verify` refuses a service account token whose `aud` lacks `netcracker`. It would go in this record
    or in a record that supersedes part of ADR-0004.
  - Base R2 on the subject check and the namespace check alone, and remove the audience from the Justification.

  `example-architect` decides. This affects R2.
````

### Message to the user

I wrote the record as `docs/adr/0007-let-m2m-tokens-reach-any-tenant.md`. Its status is `Proposed`, and three open points block acceptance:

- **O1:** the notes don't say where a request names its tenant. The term **target tenant** has a placeholder until you decide.
- **O2:** I assumed that a token that isn't M2M and has no `tenant-id` claim gets HTTP 403 with `CALLER_TENANT_MISMATCH`.
- **O3:** the notes say service account tokens are safe partly because of the `netcracker` audience. But no rule of token-gate that the notes mention checks `aud`. Also, example/platform ADR-0012 R3 binds only the platform's own services, not every workload in a listed namespace. Should token-gate require that audience, or should R2 rely only on the subject and namespace checks?

The statement that a service account token gets `TOKEN_ISSUER_UNKNOWN` in the mode `legacy` has no rule. It already follows from the provider count of ADR-0004 R1 and the unknown-issuer rule of ADR-0003 R4, so a rule here would only repeat them.

Questions:

1. Who else approves this record besides `example-architect`? For example, someone who owns example/platform or the topology file.
2. What are the titles and filenames of ADR-0004 and example/platform ADR-0012? I left placeholders in their links under **Related ADRs**.
3. Does an existing record already define "realm token" and "service account token"? If so, the terms here should point to it instead of defining them again.
4. I couldn't read the code, so I tagged every rule `verify`. Does the tenant comparison live in `internal/verify`, or in `internal/server`?

## Request 2

### File: docs/adr/0007-answer-a-token-that-fails-verification-with-http-401.md

````markdown
# Answer a token that fails verification with HTTP 401 before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title>](./0003-<slug>.md): the unknown-issuer check (R4), whose rule sets its own response, which R2
  leaves out.
- [ADR-0004: <title>](./0004-<slug>.md): the subject check (R3), whose rule sets its own response, which R2 leaves out,
  and the namespace check (R5), which R3 gives a code.
- [ADR-0005: <title>](./0005-<slug>.md): the response to `TOKEN_KEYS_UNAVAILABLE` (R2), which R2 of this record leaves
  out.

## Context

token-gate verifies the token in `Authorization` of each request, and policy evaluation then decides on the request.
Some checks of verification have a recorded response: the unknown-issuer check of ADR-0003 R4, the subject check of
ADR-0004 R3, and the missing keys of ADR-0003 R9, whose response ADR-0005 R2 sets. Other checks have none, such as the
namespace check of ADR-0004 R5.

## Decision

We will answer a request whose token in `Authorization` fails verification with HTTP 401 and the code of the check that
failed, before policy evaluation. The one exception is a token that gets `TOKEN_KEYS_UNAVAILABLE`, which keeps its own
response so that the client retries.

### Terms

- **verification**: every check that `verify` and `keys` run on a token in `Authorization`, including the checks of
  ADR-0003 and ADR-0004.

### Rules

#### Where a failed token stops

- **R1** (`verify`, `server`). token-gate does not pass a request to policy evaluation when the token in
  `Authorization` of the request fails a check of verification.

#### The response to a failed token

- **R2** (`verify`, `server`). A request whose token in `Authorization` fails a check of verification gets HTTP 401
  with the code of that check. R2 does not cover a token that gets `TOKEN_KEYS_UNAVAILABLE`, whose response ADR-0005
  R2 sets. It also does not cover a token that fails the unknown-issuer check of ADR-0003 R4 or the subject check of
  ADR-0004 R3, because those rules set their own response.
- **R3** (`verify`). A token in `Authorization` that the namespace check of ADR-0004 R5 refuses gets the code
  `<code for a namespace that the topology file does not list>`.
- **R4** (`verify`, `server`). A request whose token in `Authorization` fails more than one check of verification gets
  the response for the first check that fails, in the order in which verification runs them.

### Implementation notes

Adds no requirement. Let each check in `internal/verify` and `internal/keys` return an error that carries its code. Let
`internal/server` map each such error to HTTP 401, and map `TOKEN_KEYS_UNAVAILABLE` as ADR-0005 R2 requires.

### Justification

Policy evaluation sees only tokens that passed every check (R1). The code tells the client which check its token failed
(R2, R3). One response per request needs one check to decide it (R4).

R2 leaves out a token that gets `TOKEN_KEYS_UNAVAILABLE` because that failure is on token-gate's side, and the response
of ADR-0005 R2 makes the client retry. R2 leaves out the unknown-issuer and subject checks because their own rules
already set the response.

### Alternatives considered

- **A1. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** HTTP 401 tells the client that
  its token is bad. The client then does not retry a request that would succeed once the keys load.

## Consequences

Negative:

- A token that the namespace check of ADR-0004 R5 refuses gets HTTP 401 (R2, R3). A client that gets a new token on
  every HTTP 401 does so here, and the new token fails the same check.
- For every check of verification whose rule sets no HTTP status, clients now get HTTP 401 (R2). This changes the
  answer for clients wherever token-gate answered such a check with another status before.

## Open points

- **O1.** Which code does a token get when the namespace check of ADR-0004 R5 refuses it? R3 holds a placeholder.
  If an existing record already names a code for this check, R3 goes. `example-architect` decides. This affects R3.
- **O2.** R4 assumes that the code chooses the order in which the checks of verification run. The other answer is a
  fixed order in this record, such as issuer, keys, signature, then claims. `example-architect` decides. This affects
  R4.
````

### Message to the user

I wrote the record as `docs/adr/0007-answer-a-token-that-fails-verification-with-http-401.md`. Its status is `Proposed`, and two open points block acceptance:

- **O1:** the code for a token that the namespace check of ADR-0004 R5 refuses. The notes say every failed token gets the code of its check, but that rule names no code, so R3 has a placeholder.
- **O2:** which check decides the response when a token fails more than one.

Three existing rules already cover part of what the meeting decided: ADR-0003 R4 (unknown issuer, 401), ADR-0004 R3 (invalid subject, 401), and ADR-0005 R2 (503 for `TOKEN_KEYS_UNAVAILABLE`). R2 leaves those cases out instead of stating them a second time. This means the `TOKEN_KEYS_UNAVAILABLE` exception from the notes has no rule of its own. Those accepted records stay as they are.

Questions:

1. Who else approves this record besides `example-architect`?
2. What are the titles and filenames of ADR-0003, ADR-0004, and ADR-0005? I left placeholders in their links under **Related ADRs**.
3. The notes cover a token that fails verification, but not a request with no token in `Authorization`. Should that request get HTTP 401 too, and with which code? As written, no rule covers it, so the code decides.
