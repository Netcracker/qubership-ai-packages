## Request 1

### File: docs/adr/0012-answer-503-when-policy-store-is-unreachable.md

````markdown
# Answer HTTP 503 with `POLICY_STORE_UNAVAILABLE` where the policy store is unreachable

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1 to R3.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R2 of this
  record takes precedence over ADR-0010 R3 for a request whose policy store is unreachable.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md): R3 of
  this record adds one value to the list in ADR-0011 R2. ADR-0011 R1 applies to the response of R1.

## Context

Policy evaluation reads the policies of an endpoint from a policy store over the network. ADR-0010 R3 refuses a request
that policy evaluation does not allow with HTTP 403 and the reason code `POLICY_DENIED`. A request whose policies
cannot be read has no policy decision, so it is neither allowed nor denied by a policy. Clients branch on the reason
code of a refusal (ADR-0011), and a 403 from an outage would look to them like a denial.

## Decision

We will answer a request with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE`, and not evaluate the policy,
where the policy store is unreachable. This answer takes precedence over the 403 of ADR-0010 R3.

### Terms

- **policy store**: the network service from which policy evaluation reads policies.
- **unreachable**: the connection to the policy store cannot be established, or the policy store sends no response
  within `<policy store timeout>`. O1 and O2 ask what else counts.

### Rules

#### Response to an unreachable policy store

- **R1** (`policy`, `api`). Where the policy store is unreachable when policy evaluation reads the policies of the
  endpoint a request calls, the service answers the request with HTTP 503 and a JSON body whose `reason` is
  `POLICY_STORE_UNAVAILABLE`, and does not evaluate the policy.

#### Precedence

- **R2** (`api`). Where R1 applies to a request, ADR-0010 R3 does not apply to it, and the service does not answer it
  with HTTP 403.
- **R3** (`api`). `POLICY_STORE_UNAVAILABLE` is a value of `reason` that ADR-0011 R2 allows, in addition to the values
  it lists.

### Justification

A client that receives 503 and `POLICY_STORE_UNAVAILABLE` can tell an outage from a denial and retry later, which a
403 with `POLICY_DENIED` would not let it do (R1, R2). Policy evaluation reads no policy while the store is unreachable,
so the service has nothing to evaluate (R1). ADR-0011 R2 lists the allowed reason codes as a closed set, so the new code
needs a rule that admits it (R3).

### Alternatives considered

- **A1. Answer 403 with `POLICY_DENIED` where the policy store is unreachable.** Rejected by R2: a client could not
  tell an outage from a denial.
- **A2. Evaluate the policy from a default or an earlier copy where the policy store is unreachable.** Rejected by R1:
  the service would decide a request without reading the policies of its endpoint.

## Consequences

Negative:

- A clearer outage signal costs availability: every request that needs a policy decision fails with 503 while the
  policy store is unreachable (R1).
- A client that handles only the reason codes of ADR-0011 R2 meets a new value (R3).

Follow-ups:

- The API owner decides whether ADR-0011 R2 is amended in place, since both records are `Proposed`, so that its list
  names `POLICY_STORE_UNAVAILABLE`.

## Open points

- **O1.** Which value `<policy store timeout>` takes. The owner decides. It affects R1.
- **O2.** Whether a policy store that answers with an error status, or with policies that cannot be read, counts as
  unreachable. The answers: it counts, or it keeps the behavior of ADR-0010. The owner decides. It affects R1 and R2.
- **O3.** The record assumes that policy evaluation keeps no copy of earlier policies, so that every read of an
  unreachable store ends in R1. If a copy exists, R1 needs a limit. The owner decides. It affects R1.
````

### Message to the user

I wrote the record as `Proposed`. Questions before it can move on:

- Who is the owner, and who approves it? I left `<owner account>` and `<role>, <account>` as visible placeholders.
- What is the timeout after which the policy store counts as unreachable (O1)?
- Does a store that answers with an error, or with unreadable policies, count as unreachable (O2)?
- Does policy evaluation cache policies (O3)? I assumed it does not.

ADR-0010 and ADR-0011 are untouched. ADR-0011 R2 is a closed list, so R3 adds the new code from this record. I put a follow-up for the API owner to decide whether to amend that list in place. ADR-0010, ADR-0011, and this record are all `Proposed`, so none of them binds a change yet, and no trailers are owed. I listed no **Confirmation** entries because I know of no test for these rules.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-one-file.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml` and stop the start where it is missing

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1 and R2.

## Context

The service takes its settings through its `config` layer (`internal/config`). Where the settings come from decides
what an operator has to provide to start the service and where the operator looks to find the value of a setting.

## Decision

We will read the configuration of the service only from the file `/etc/token-gate/config.yaml`, and we will stop the
start where that file is missing.

### Terms

- **configuration source**: anything from which the service takes the value of a setting. A file, an environment
  variable, a command-line flag, and a remote service are each a configuration source.
- **stops the start**: the process exits before it serves a request. A configuration loader meets it by returning an
  error to its caller.

### Rules

#### Source of the configuration

- **R1** (`config`). The service takes the value of every setting only from the file `/etc/token-gate/config.yaml`.
  No other file, environment variable, command-line flag, or remote service is a configuration source.
- **R2** (`config`). Where the file `/etc/token-gate/config.yaml` does not exist, the service stops the start.

### Justification

One fixed path gives an operator one place to find the value of any setting (R1). A missing file stops the start, so
the service never runs with settings that nobody provided (R2).

### Alternatives considered

- **A1. Let environment variables or command-line flags override the values of the file.** Rejected by R1: the value
  of a setting would then have more than one source.
- **A2. Start with built-in defaults where the file is missing.** Rejected by R2: the service would run without the
  configuration an operator meant to provide.

## Consequences

Negative:

- An installation that has no file at `/etc/token-gate/config.yaml` stops the start after the upgrade (R2).
- An installation that sets a value through an environment variable or a flag loses that value, because the service no
  longer reads it (R1).
- A test or a local run needs a file at that absolute path, since R1 allows no other path.

## Open points

- **O1.** Whether a test or a local run may name another path. The record assumes it may not, as R1 reads. The owner
  decides. It affects R1.
- **O2.** What the service does where the file exists but cannot be read or is not valid YAML. The answers: it stops
  the start like R2, or the case stays the implementer's choice. The owner decides. It affects R2.
- **O3.** Whether a file that a setting of `config.yaml` names, such as a key file, is a configuration source. The
  record assumes that its content is data and not a setting. The owner decides. It affects R1.
````

### Message to the user

I wrote the record as `Proposed`. Questions before it can move on:

- Who is the owner, and who approves it? I left placeholders.
- Should a test or a local run be able to name another path (O1)? As written, R1 allows no other path.
- What happens when the file exists but is unreadable or not valid YAML (O2)? You only named the missing file, so I wrote no rule for that case.
- Does a file named by a setting, such as a key file, count as a configuration source (O3)? I assumed it does not.

I wrote the Context and Justification from what you told me, so please correct them if the real reasons differ. The Negative consequences name what an existing installation gets on upgrade: it stops the start without the file, and it loses any value set through an environment variable or a flag. The `config` layer is already mapped in the reading guide, so the guide needs no change. The record is `Proposed`, so no trailers are owed yet.
