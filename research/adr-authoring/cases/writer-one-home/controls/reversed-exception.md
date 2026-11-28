## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# Let an M2M token reach any tenant, and limit any other token to the tenant of its `tenant-id` claim

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.

### Related ADRs

- [ADR-0004: <title of ADR-0004>](<file of ADR-0004>): the subject check (R3) and the namespace check (R5) of a
  service account token. The Justification of R2 relies on both checks.
- [example/platform ADR-0012: <title of ADR-0012>](<link to example/platform ADR-0012>): the audience of the service
  account tokens that the platform's services request (R3). The Justification of R2 relies on it, and O3 asks how far.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Two kinds of token arrive
there. Keycloak signs a realm token for a realm, and the Kubernetes API server signs a service account token for a
service account. A realm token can carry realm roles in the claim `realm_access.roles`. A service account token
carries no realm roles, because Keycloak does not issue it.

A request names the tenant it acts on. No accepted record decides which tokens may act on a tenant other than their
own.

## Decision

We will treat a realm token with the role `ROLE_M2M`, and every service account token, as an M2M token that may act on
any tenant. Any other token may act only on the tenant that its claim `tenant-id` names.

### Terms

- **realm token**: a token in `Authorization` that Keycloak signs for a realm.
- **service account token**: a token in `Authorization` that the Kubernetes API server signs for a service account.
- **verified token**: a token in `Authorization` that no check of the `verify` and `keys` layers refuses.
- **M2M token**: a verified token that R1 or R2 makes an M2M token. Every other token in `Authorization` is not an M2M
  token.
- **requested tenant**: the tenant that a request names in `<where a request names its tenant>`.

### Rules

#### Which tokens are M2M tokens

- **R1** (`verify`). A verified realm token is an M2M token when its claim `realm_access.roles` holds the string
  `ROLE_M2M`. A verified realm token whose claim `realm_access.roles` does not hold that string, or that has no such
  claim, is not an M2M token.
- **R2** (`verify`). Every verified service account token is an M2M token.

#### Tenant access

- **R3** (`server`). A request whose verified token is not an M2M token gets HTTP 403 with `CALLER_TENANT_MISMATCH`
  when its requested tenant differs from the value of the token's claim `tenant-id`, or when the token has no claim
  `tenant-id`. A request whose token is an M2M token never gets `CALLER_TENANT_MISMATCH`, whatever its requested
  tenant.

### Implementation notes

Adds no requirement. Decide once, in `internal/verify`, whether a verified token is an M2M token, and pass that result
to `internal/server` together with the claims of the token. The tenant check in `internal/server` can then compare the
requested tenant with the claim `tenant-id` without reading roles itself.

### Justification

A service that acts for several tenants needs a token that is not bound to one tenant. A realm role lets the
administrators of the realm mark a client as M2M without a new kind of token (R1).

A service account token needs no such marker. Three things limit which service account tokens arrive: the subject check
of ADR-0004 R3, the namespace check of ADR-0004 R5, and the audience that example/platform ADR-0012 R3 sets for the
service account tokens of the platform's services (R2). The audience limits only the tokens that the platform's services
request, and O3 asks whether token-gate checks it.

A token that is not M2M acts for one tenant, so binding it to the tenant of its claim `tenant-id` keeps it from acting
on any other tenant (R3).

### Alternatives considered

- **A1. Let policy evaluation decide whether a token that is not M2M may act on a tenant other than its `tenant-id`.**
  Rejected by R3: a token that is not M2M never acts on another tenant, whatever a policy allows.
- **A2. Require a marker in a service account token, as `ROLE_M2M` marks a realm token.** Rejected by R2: the
  Kubernetes API server signs service account tokens without realm roles, and the checks named in the Justification
  already limit which service account tokens arrive.

## Consequences

Negative:

- Any workload that holds a service account token from a namespace that the topology file lists can act on every
  tenant (R2, R3).
- Anyone who can grant `ROLE_M2M` in the realm can give a client access to every tenant (R1, R3).
- A request with a token that is not M2M, and that names a tenant other than the token's `tenant-id`, now gets HTTP
  403 with `CALLER_TENANT_MISMATCH` (R3). No accepted record refused such a request before this one.

## Open points

- **O1.** Where does a request name its tenant: a header, a path segment, or another input? `example-architect`
  decides. Affects R3 and the term **requested tenant**.
- **O2.** R3 assumes that a token that is not M2M and has no claim `tenant-id` gets HTTP 403 with
  `CALLER_TENANT_MISMATCH`. The other answer under consideration is that `verify` refuses such a token with HTTP 401
  and a code of its own. `example-architect` decides. Affects R3.
- **O3.** Does `verify` refuse a service account token whose `aud` does not hold `netcracker`? example/platform
  ADR-0012 R3 governs the audience that the platform's services request. It does not make token-gate refuse a token with
  another audience, such as a token that a workload in a listed namespace requests for itself. The answers under
  consideration are (a) a new rule in this record that refuses such a token, with a code still to be named, and (b) no
  check, so that R2 rests on ADR-0004 R3 and R5 alone and the Justification drops the audience. `example-architect`
  decides. Affects R2.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Open points O1, O2, and O3 block acceptance.

I left one note out of the record: "in the mode `legacy` a service account token gets `TOKEN_ISSUER_UNKNOWN`". Two accepted rules already produce that result. ADR-0004 R1 allows no service account provider in the mode `legacy`, and ADR-0003 R4 answers a token from an unknown issuer. A new rule would only repeat them, and both records stay as they are.

The main thing to settle is the audience in the Justification (O3). Platform ADR-0012 R3 controls what the platform's own services request. It does not stop token-gate from accepting a service account token with another audience. Because R2 makes every service account token an M2M token, any such token from a listed namespace can reach every tenant. Should `verify` require `aud` to hold `netcracker`? If so, which code should it use?

Other questions:

- Where does a request name its tenant (O1)? R3 has a placeholder for it.
- Should a token that is not M2M and has no `tenant-id` claim get 403 `CALLER_TENANT_MISMATCH` (my assumption, O2), or a 401 from `verify`?
- Who else approves the record besides `example-architect`, for example a security owner?
- What are the titles and filenames of ADR-0004 and platform ADR-0012? The links under **Related ADRs** are placeholders.
- Do the records follow the filename pattern `NNNN-<slug>.md`? I assumed they do.
- Does an existing record already define "realm token" and "service account token"? If so, I'll change those Terms to point at it.
- Is the tenant check going into `internal/server`, as I tagged R3? I tagged R1 and R2 as `verify`.

## Request 2

### File: docs/adr/0007-respond-401-to-failed-token-verification.md

````markdown
# Answer a token that fails verification with HTTP 401 and the code of the failed check, before policy evaluation

## Status

Proposed

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R4.

### Related ADRs

- [ADR-0003: <title of ADR-0003>](<file of ADR-0003>): the issuer check of a token (R4), an example of a check whose
  rule names a response and a code.
- [ADR-0004: <title of ADR-0004>](<file of ADR-0004>): the namespace check of a service account token (R5), which R4
  gives a code.
- [ADR-0005: <title of ADR-0005>](<file of ADR-0005>): the response to a token whose keys are unavailable (R2), which
  R2 keeps for that case.

## Context

token-gate checks the token in `Authorization` of each request before policy evaluation. Some rules for these checks
name a response and a code, such as the issuer check of ADR-0003 R4. The rule for the namespace check of a service
account token, ADR-0004 R5, names neither. No accepted record decides the response for a failed check in general, or
whether a request with a failed token reaches policy evaluation.

## Decision

We will answer a token in `Authorization` that fails verification with HTTP 401 and the code of the check that failed,
before policy evaluation. A token whose keys are unavailable keeps the response that makes the client retry.

### Terms

- **verification**: the checks that the `verify` and `keys` layers make on a token in `Authorization`. A token fails
  verification when one of those checks refuses it.

### Rules

#### Response to a failed token

- **R1** (`server`). A request whose token in `Authorization` fails verification does not reach policy evaluation.
- **R2** (`verify`, `server`). A token in `Authorization` that fails verification gets HTTP 401 with the code of the
  check that refused it. A token that gets `TOKEN_KEYS_UNAVAILABLE` gets HTTP 401 as well.
- **R3** (`verify`). A token in `Authorization` that more than one check of verification refuses, where one of those
  checks gives `TOKEN_KEYS_UNAVAILABLE`, gets HTTP 401 with the code of one of the other checks.

#### Codes

- **R4** (`verify`). A service account token in `Authorization` that the namespace check of ADR-0004 R5 refuses gets
  the code `<code for a namespace that the topology file does not list>`.

### Implementation notes

Adds no requirement. Let `internal/verify` return the code of the check that refused a token. Let `internal/server`
map each code to its response in one place, so that `TOKEN_KEYS_UNAVAILABLE` is the only code with a response other
than HTTP 401. To meet R3, run the checks that need no keys even when the keys of the token's provider are unavailable.

### Justification

A token that fails verification gives policy evaluation no identity it can trust, so the request stops before policy
evaluation (R1). A code for each check shows the client's developer which check to fix (R2, R4).

Unavailable keys are a fault of token-gate or of the provider, not of the token, and they can resolve within seconds. A
token that gets `TOKEN_KEYS_UNAVAILABLE` therefore keeps the response that makes the client retry (R2). Where another
check also refuses the token, a retry cannot succeed, so the client gets the final answer (R3).

### Alternatives considered

- **A1. Answer `TOKEN_KEYS_UNAVAILABLE` with HTTP 401, like every other failed check.** Rejected by R2: a client
  treats HTTP 401 as final and does not retry, although the keys may arrive seconds later.
- **A2. Pass a request with a failed token to policy evaluation, and let the policy decide.** Rejected by R1.

## Consequences

Negative:

- The code in an HTTP 401 shows any caller which check refused its token, such as whether token-gate knows an issuer
  (R2).
- A check whose failure gets a response other than HTTP 401 today gets HTTP 401 after this record (R2). The namespace
  check of ADR-0004 R5 is such a case if it answers with another status today, and its callers also see a new code
  (R4).

## Open points

- **O1.** Which code does a service account token from a namespace that the topology file does not list get?
  `example-architect` decides. Affects R4.
- **O2.** R3 assumes that HTTP 401 wins when a token gets `TOKEN_KEYS_UNAVAILABLE` and another check also refuses it.
  The other answer under consideration is that `TOKEN_KEYS_UNAVAILABLE` wins, so the token gets the response of
  ADR-0005 R2 and R3 is dropped. `example-architect` decides. Affects R2 and R3.
````

### Message to the user

I wrote ADR-0007 as `Proposed`. Open points O1 and O2 block acceptance.

Two rules already give a 401 with a code for their own checks: ADR-0003 R4 (unknown issuer) and ADR-0004 R3 (invalid subject). R2 of the new record agrees with both, and both records stay as they are. The new record mainly matters for checks whose rules don't name a response, and for the order relative to policy evaluation.

Questions:

- **Namespace code (O1).** ADR-0004 R5 refuses a service account token from a namespace the topology file doesn't list, but it names no code. The decision requires "the code of the check that failed", so R4 has a placeholder. Which code should it be? Does that check answer with a status other than 401 today? If it does, existing callers will see a change. Is there a test I should name for it?
- **Two failures at once (O2).** A token can fail on `TOKEN_KEYS_UNAVAILABLE` and on another check at the same time. I assumed the 401 wins (R3), because a retry can't succeed. Should the 503 win instead?
- **Other checks.** I only know the rules you listed. Do ADR-0003 or ADR-0004 have other token checks that name no code or a status other than 401? R2 changes their response too, and each one without a code needs a placeholder like R4.
- **No token.** A request with no token in `Authorization` falls outside this record. Should it get a 401 as well?
- **Approvers.** Who else approves the record besides `example-architect`?
- **Links and filenames.** What are the titles and filenames of ADR-0003, ADR-0004, and ADR-0005? The links under **Related ADRs** are placeholders. I also assumed the filename pattern `NNNN-<slug>.md`.
