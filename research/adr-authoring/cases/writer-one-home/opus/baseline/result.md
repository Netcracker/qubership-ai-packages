## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# 0007. M2M tokens and tenant access

- Status: Proposed
- Date: November 12, 2026
- Deciders: @example-architect

## Context

token-gate checks the token in `Authorization` before policy evaluation. Most callers act for one tenant, which the
`tenant-id` claim of their token names. Some callers are services that act for every tenant. No existing record says
which tokens may reach a tenant other than their own.

Two kinds of token reach token-gate. Keycloak signs a realm token for a realm. The Kubernetes API server signs a service
account token for a service account. ADR-0004 R3 and ADR-0004 R5 already limit which service account tokens pass
verification:

- ADR-0004 R3 refuses a service account token whose `sub` does not start with `system:serviceaccount:`.
- ADR-0004 R5 accepts a service account token only from a namespace that the topology file lists.

## Decision

This record calls a token that may reach every tenant an M2M token. Rules R3 and R4 apply only to a token that has
passed verification under ADR-0003 and ADR-0004. A token that fails verification gets the response that those records
set.

- **R1 (`verify`).** A realm token is an M2M token when its `realm_access.roles` claim holds `ROLE_M2M`. Any other realm
  token is not an M2M token.
- **R2 (`verify`).** A service account token is an M2M token.
- **R3 (`server`).** A request with an M2M token may target any tenant.
- **R4 (`server`).** A request with a token that is not an M2M token may target only the tenant that the `tenant-id`
  claim of its token names. A request that targets any other tenant gets HTTP 403 with `CALLER_TENANT_MISMATCH`.

## Consequences

- Under R4, a token that is not an M2M token reaches no tenant other than its own.
- R2 relies on ADR-0004 R3 and ADR-0004 R5 to limit which service account tokens are M2M tokens. A change to either rule
  changes which callers may reach every tenant. Review this record together with any such change.
- In the mode `legacy`, ADR-0004 R1 keeps every provider of service account tokens out of the providers file. A service
  account token therefore gets HTTP 401 with `TOKEN_ISSUER_UNKNOWN` under ADR-0003 R4, and R2 never applies to it.
- In the mode `k8s`, every service account token that passes ADR-0004 R3 and ADR-0004 R5 may target any tenant.

## Open questions

- Where does a request name the tenant it targets: a header, the path, or a claim? R3 and R4 assume the request names
  it, and R4 compares that tenant with the `tenant-id` claim.
- What does a request with a token that is not an M2M token get when the token has no `tenant-id` claim?
- What does a request that targets no tenant get?
- Do R3 and R4 belong to `server` or to `verify`?
````

### Message to the user

I wrote ADR-0007 from the notes. I left its status at `Proposed` because the notes leave four points open, and I listed them in the record under "Open questions". Once @example-architect answers them, the status can change to `Accepted`.

**Questions for @example-architect:**

1. **Where does the target tenant come from?** The notes say an M2M token "may name any tenant", but they don't say where a request names its tenant. It could be a header, the path, or a claim. R3 and R4 assume the request names it, and I didn't make up a header or claim name.
2. **What happens to a non-M2M token with no `tenant-id` claim?** R4 compares the target tenant with that claim. A realm token that has neither `ROLE_M2M` nor `tenant-id` falls outside every rule.
3. **What happens to a request that targets no tenant?** The notes also say a token that is not M2M "never reaches another tenant". That holds only if every request targets a tenant and token-gate always makes the comparison, so questions 2 and 3 decide whether it's true.
4. **Which layer runs R3 and R4?** I put them in `server` because the target tenant comes from the request, not the token. If `verify` should run them, the layer tags need to change.
5. **Is the safety argument for service account tokens strong enough?** ADR-0004 R3 checks only the `sub` prefix, and ADR-0004 R5 checks only the namespace. Neither limits which service account the token belongs to. Every service account in a listed namespace becomes an M2M token and can reach every tenant, including the `default` service account of that namespace. Is that the intent, or should R2 apply only to service accounts that a list names?

The legacy-mode point isn't a new rule. It follows from ADR-0004 R1 and ADR-0003 R4, so I recorded it under "Consequences" and cited those rules.

**Not done:**

- I didn't update the reading guide in `docs/adr/README.md` because I don't have its contents. It needs an entry for 0007.
- I didn't have the `adr-authoring` template itself, so I inferred its structure from the description of records 0001 to 0006. Check the headings and the file name slug against those records.

## Request 2

### File: docs/adr/0007-response-to-failed-token-verification.md

````markdown
# 0007. Response to a token that fails verification

- Status: Accepted
- Date: November 12, 2026
- Deciders: @example-architect

## Context

token-gate checks the token in `Authorization` before policy evaluation. Each check of `verify` and `keys` reports its
own code when it fails. The existing records set the HTTP status for some of those codes:

- ADR-0003 R4 gives `TOKEN_ISSUER_UNKNOWN` HTTP 401.
- ADR-0004 R3 gives `TOKEN_SUBJECT_INVALID` HTTP 401.
- ADR-0005 R2 gives `TOKEN_KEYS_UNAVAILABLE` HTTP 503 with `Retry-After: 5`.

No record sets the status for every failed check, so a new check has no status until a record gives it one.

## Decision

- **R1 (`server`).** A request whose token in `Authorization` fails a check of `verify` or `keys` gets HTTP 401 with the
  code of the check that failed. token-gate sends this response before policy evaluation, and policy evaluation does not
  run for the request. R2 states the one exception.
- **R2 (`server`).** A request whose token gets `TOKEN_KEYS_UNAVAILABLE` gets the response that ADR-0005 R2 sets, HTTP
  503 with `Retry-After: 5`, so that the client retries.

## Consequences

- The statuses of ADR-0003 R4, ADR-0004 R3, and ADR-0005 R2 stay the same.
- A check added to `verify` or `keys` gets HTTP 401 under R1 without a new record. A check that needs another status
  needs a record that amends R1.
- A token with no keys available is the only failed token that a client retries. Every other failed token gets HTTP 401,
  and the client needs a different token before it retries.
````

### Message to the user

I wrote ADR-0007 from the notes. Both rules are in the `server` layer, the same layer as ADR-0005 R2.

**Questions for @example-architect:**

1. **What code does ADR-0004 R5 report?** That's the check that accepts a service account token only from a listed namespace. R1 gives that failure HTTP 401 with "the code of the check that failed", but I don't know the code. If ADR-0004 doesn't give it one, R5 needs one.
2. **Which code wins when a token fails more than one check?** For example, a token could have an unknown `iss` and also a `sub` without `system:serviceaccount:`. If `verify` stops at the first failed check, the order of the checks sets the code, and the record should say so. ADR-0003 R9 runs only for a provider that `iss` names, so `TOKEN_KEYS_UNAVAILABLE` can't occur together with `TOKEN_ISSUER_UNKNOWN`. The other pairs aren't covered.
3. **What does a request with no token in `Authorization` get?** The notes cover a token that fails verification, but not a missing token.

**Not done:**

- I didn't update the reading guide in `docs/adr/README.md` because I don't have its contents. It needs an entry for 0007.
- I didn't have the `adr-authoring` template itself, so I inferred its structure from the description of records 0001 to 0006. Check the headings and the file name slug against those records.
