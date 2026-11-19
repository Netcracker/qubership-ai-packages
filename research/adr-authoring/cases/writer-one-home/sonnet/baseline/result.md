## Request 1

### File: docs/adr/0007-m2m-tokens-and-tenant-access.md

````markdown
# ADR-0007: M2M tokens and tenant access

- Status: Accepted
- Date: 2026-11-12
- Deciders: @example-architect
- Related: ADR-0003, ADR-0004

## Context

token-gate accepts two kinds of token in `Authorization`. A realm token is signed by Keycloak for a realm. A service
account token is signed by the Kubernetes API server for a service account. `M2M_AUTH_MODE` selects `legacy` or `k8s`,
and ADR-0004 R1 allows a provider of service account tokens only in the mode `k8s`.

Some callers are machines that act for many tenants, and the rest are bound to one tenant. token-gate needs a rule for
which tokens are M2M tokens and which tenants each kind of token may reach.

## Decision

- R1 (`verify`). A realm token is an M2M token when `realm_access.roles` holds `ROLE_M2M`.
- R2 (`verify`). A service account token is an M2M token.
- R3 (`verify`). An M2M token may reach any tenant.
- R4 (`verify`). A token that is not M2M may reach only the tenant of its own `tenant-id` claim. A request for any
  other tenant gets HTTP 403 with `CALLER_TENANT_MISMATCH`.

## Consequences

- In the mode `legacy`, a service account token gets HTTP 401 with `TOKEN_ISSUER_UNKNOWN` under ADR-0003 R4, because
  ADR-0004 R1 keeps every provider of service account tokens out of the providers file. R2 therefore takes effect only
  in the mode `k8s`.
- R2 relies on two earlier rules. ADR-0004 R3 refuses a service account token whose `sub` does not start with
  `system:serviceaccount:`, and ADR-0004 R5 accepts a service account token only from a namespace that the topology file
  lists. Neither rule limits which service account in a listed namespace presents the token, so every service account in
  a listed namespace may reach any tenant. The topology file is the control on that access.
- A realm token reaches more than one tenant only through `ROLE_M2M`. The assignment of that role in Keycloak is the
  control on that access.
````

### Message to the user

I wrote ADR-0007 from the meeting notes. These points need your attention:

1. **The "That is safe" claim is not in the ADR.** ADR-0004 R3 checks only the `sub` prefix, and ADR-0004 R5 checks only the namespace. Together they don't limit which service account in a listed namespace gets cross-tenant access. The ADR records this as a consequence instead. Please confirm that @example-architect accepts this.
2. **I assigned R1 to R4 to the layer `verify`.** The notes name no layer. If the 403 for `CALLER_TENANT_MISMATCH` belongs in `server`, I'll move R4. Which layer do you want?
3. **The notes leave one case open.** What does a realm token get when it has no `ROLE_M2M` and no `tenant-id` claim? R4 doesn't cover it, so the ADR is silent. Is it `CALLER_TENANT_MISMATCH`, or another code?
4. **I didn't touch `docs/adr/README.md`.** I can't see it. Add 0007 to its index, and to the `verify` layer if the guide lists records per layer.
5. **I assumed the template of `adr-authoring`.** I couldn't read it, so the section names and the header fields are a guess. Please check them against the template.

## Request 2

### File: docs/adr/0007-failed-token-verification-response.md

````markdown
# ADR-0007: Response to a token that fails verification

- Status: Accepted
- Date: 2026-11-12
- Deciders: @example-architect
- Related: ADR-0003, ADR-0004, ADR-0005

## Context

token-gate verifies the token of each request before policy evaluation. Earlier records give some failed checks their own
response: ADR-0003 R4 and ADR-0004 R3 return HTTP 401 with a code, and ADR-0005 R2 returns HTTP 503 with `Retry-After: 5`
for `TOKEN_KEYS_UNAVAILABLE`. No rule states the response for a failed check in general, or that such a request never
reaches policy evaluation.

## Decision

- R1 (`server`). A token in `Authorization` that fails verification gets HTTP 401 with the code of the check that
  failed. The request gets this response before policy evaluation.
- R2 (`server`). A token that gets `TOKEN_KEYS_UNAVAILABLE` gets the response of ADR-0005 R2 instead of the response of
  R1, so that the client retries.

## Consequences

- A check added to `verify` later gets HTTP 401 with its own code, with no further rule, unless a record makes it an
  exception as R2 does.
- `TOKEN_KEYS_UNAVAILABLE` is the only code that R1 does not turn into HTTP 401. Its cause is a provider that has had no
  keys since the start (ADR-0003 R9), not a defect of the token, and a client may succeed on a later attempt with the
  same token.
````

### Message to the user

I wrote ADR-0007 from the meeting notes. These points need your attention:

1. **Please confirm the status codes for failed checks.** ADR-0004 R5 refuses a service account token from a namespace that the topology file doesn't list. The rule states no code for that failure. R1 says it gets HTTP 401 with the code of the check, so please tell me the code. I didn't invent one.
2. **I assigned R1 and R2 to the layer `server`.** The notes name no layer, and this layer sends the response and runs before policy evaluation. If you want them in `verify`, I'll change it.
3. **The notes leave one case open.** Does a request that gets `TOKEN_KEYS_UNAVAILABLE` also skip policy evaluation? I assume it does, because it has failed verification, but R2 doesn't say so. Please confirm.
4. **I didn't touch `docs/adr/README.md`.** I can't see it. Add 0007 to its index.
5. **I assumed the template of `adr-authoring`.** I couldn't read it, so the section names and the header fields are a guess. Please check them against the template.
