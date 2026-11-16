## Request 1

### File: docs/adr/0012-policy-store-unavailable-refusal.md

````markdown
# Refuse with HTTP 503 and `POLICY_STORE_UNAVAILABLE` where the policy store is unreachable

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- `<role>`, `<account>`: approves the rules.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R2 of this
  record wins over R3 of ADR-0010 for a request that R1 of this record leaves without a decision.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md): the
  response of R2 of this record carries a value of `reason` that R2 of ADR-0011 does not list, and takes it as an
  exception.

## Context

Policy evaluation reads the policies of the endpoint a request calls from a policy store over the network. When the
store cannot be reached, policy evaluation has no policies to evaluate. ADR-0010 R3 answers a request that policy
evaluation does not allow with HTTP 403 and `POLICY_DENIED`, and a client that receives it concludes that the policy
denied the request.

## Decision

We will refuse a request with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE`, without evaluating the policy,
where the policy store is unreachable.

### Terms

- **policy store**: the network service from which policy evaluation reads its policies.
- **unreachable**: the policy store is unreachable for a request when the read of the policies of the endpoint the
  request calls cannot open a connection to the policy store, or receives no response within
  `<policy store timeout>`.

### Rules

#### Policy store unavailable

- **R1** (`policy`). Where the policy store is unreachable for a request with a verified token, policy evaluation
  evaluates no policy for the request and returns no decision for it.
- **R2** (`api`). A request for which policy evaluation returns no decision under R1 is refused with HTTP 503 and the
  value `POLICY_STORE_UNAVAILABLE` in the field `reason` of the response body, and not with the HTTP 403 of ADR-0010
  R3.

### Justification

A client that receives 503 and `POLICY_STORE_UNAVAILABLE` can tell an outage from a denial, and can retry the request
(R2). A request without a decision is not allowed, so the backend, which trusts every request it receives, never gets
it (R1).

### Alternatives considered

- **A1. Refuse a request with HTTP 403 and `POLICY_DENIED` where the policy store is unreachable.** Rejected by R2: the
  client could not tell a denial from an outage, and a retry would look pointless.

## Consequences

Positive:

- A client can retry on `POLICY_STORE_UNAVAILABLE` and treat `POLICY_DENIED` as final.

Negative:

- While the policy store is unreachable, the service refuses every request with a verified token, including requests
  that policy would have allowed (R1, R2).

## Open points

- **O1.** What is the value of `<policy store timeout>`? The service owner decides. It affects the term **unreachable**,
  and with it R1 and R2.
- **O2.** Does a policy store that answers with an error response count as unreachable? Under consideration: yes, any
  failed read counts; or no, only a failed connection or a timeout counts, as the term now says. The service owner
  decides. It affects R1 and R2.
````

### File: docs/adr/0010-refuse-what-policy-denies.md

````markdown
# Refuse every request that policy evaluation does not allow

## Status

Proposed

### Owner

@platform-architect

### Participants and approvers

- Platform architect, @platform-architect: approves the rules.

### Related ADRs

- [ADR-0012: Refuse with HTTP 503 and `POLICY_STORE_UNAVAILABLE` where the policy store is unreachable](0012-policy-store-unavailable-refusal.md):
  R2 of ADR-0012 wins over R3 for a request that ADR-0012 R1 leaves without a decision.

## Context

Policy evaluation decides, for each request with a verified token, whether the subject may call the endpoint. The
service forwards a request to its backend only after that decision.

## Decision

We will forward a request to the backend only where policy evaluation allows it.

### Rules

#### Decisions

- **R1** (`policy`). A request reaches the backend only where policy evaluation allows it.
- **R2** (`policy`). Policy evaluation reads the policies of the endpoint the request calls, and no other endpoint's.
- **R3** (`api`). A request that policy evaluation does not allow is refused with HTTP 403 and the reason code
  `POLICY_DENIED`, except a request that ADR-0012 R2 refuses with HTTP 503. This exception holds only while ADR-0012 R2
  binds the change.

### Justification

The backend trusts every request it receives, so the service is the only place where access is decided (R1, R3).
````

### File: docs/adr/0011-reason-codes-in-error-responses.md

````markdown
# Name the reason for every error response in a reason code

## Status

Proposed

### Owner

@api-owner

### Participants and approvers

- API owner, @api-owner: approves the rules.

### Related ADRs

- [ADR-0012: Refuse with HTTP 503 and `POLICY_STORE_UNAVAILABLE` where the policy store is unreachable](0012-policy-store-unavailable-refusal.md):
  R2 of ADR-0012 adds the value `POLICY_STORE_UNAVAILABLE` to the list of R2.

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from one closed list. ADR-0012 adds one code to it, for
a policy store that is unreachable.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, and `POLICY_DENIED`, except in a
  response that ADR-0012 R2 requires, where it is `POLICY_STORE_UNAVAILABLE`. This exception holds only while ADR-0012
  R2 binds the change.

### Justification

A closed list lets a client handle every cause it can receive (R2).
````

### Message to the user

I added ADR-0012 as `Proposed`. It has two rules. R1 (`policy`) says policy evaluation evaluates nothing and returns no decision when the store is unreachable. R2 (`api`) says the request is refused with 503 and `reason` set to `POLICY_STORE_UNAVAILABLE`, and not with the 403 of ADR-0010 R3.

Your request also contradicts two Proposed records in the repository, so I edited them in this change:

- **ADR-0010:** R3 now has an exception for the case R2 of ADR-0012 covers, and I added a line under **Related ADRs**.
- **ADR-0011:** R2 now has the same kind of exception, because the new code is not in its closed list. I also changed its Decision sentence, which called the list closed, and added a line under **Related ADRs**.

Each exception holds only while ADR-0012 R2 binds the change. Until ADR-0012 is accepted, a checker enforces the 403 and the closed list as before.

Two open points keep the record `Proposed`:

- **O1:** I need the value of `<policy store timeout>`, which decides when the store counts as unreachable.
- **O2:** I assumed that a store that answers with an error response is not unreachable. Please confirm or reverse that.

Questions for you:

- Who is the owner, and who approves the rules? I left placeholders in **Owner** and **Participants and approvers**.
- I wrote no **Confirmation** entries, because no checks exist yet.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-etc-file.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml` and stop the start where it is missing

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- `<role>`, `<account>`: approves the rules.

## Context

The service reads settings that an operator chooses for each deployment. Without a fixed source, an operator has to
check the environment, the command line, and files to learn which settings a running instance uses.

## Decision

We will read the configuration of the service only from the file `/etc/token-gate/config.yaml`, and we will stop the
start where that file is missing.

### Terms

- **configuration**: the settings whose values an operator chooses for a deployment of the service. Policies read from
  the policy store, tokens, and request data are not configuration.
- **missing**: no file exists at the path `/etc/token-gate/config.yaml`.
- **stops the start**: the process exits before it serves a request. A library below the entry point meets a rule that
  requires it by returning an error to its caller.

### Rules

#### Source of the configuration

- **R1** (`config`). The service reads its configuration only from the file `/etc/token-gate/config.yaml`, and from no
  environment variable, command-line argument, or other file.

#### Missing file

- **R2** (`config`). Where `/etc/token-gate/config.yaml` is missing at start, the service stops the start.

### Justification

One source leaves an operator one place to read what a deployment runs with (R1). A start without the file would run on
settings that nobody chose for the deployment (R2).

### Alternatives considered

- **A1. Let an environment variable or a command-line argument override a value of the file.** Rejected by R1: the
  configuration would then have more than one source.
- **A2. Start with built-in defaults where the file is missing.** Rejected by R2.

## Consequences

Negative:

- Every deployment of the service, including a local run and a test that starts the service, needs the file at
  `/etc/token-gate/config.yaml` (R1, R2).
- An operator cannot change one setting through an environment variable or a command-line argument (R1).

## Open points

- **O1.** Does a file that exists at the path but cannot be read or parsed also stop the start? Under consideration: yes,
  any file the service cannot load stops the start; or no, only a missing file does, and the implementer chooses the
  rest. The service owner decides. It affects R2.
````

### Message to the user

I added ADR-0012 as `Proposed`, with two rules in the `config` layer. R1 reads the configuration only from `/etc/token-gate/config.yaml`. R2 stops the start where that file is missing. I defined "configuration" so that policies, tokens, and request data are outside it. Environment variables and command-line arguments are inside it, so R1 excludes them. Tell me if you want an exception for either.

One open point keeps the record `Proposed`. **O1** asks whether a file that exists but cannot be read or parsed also stops the start. You only named a missing file, so R2 covers only that case.

I saw only the title and status of ADR-0006, so I could not check it for rules on configuration. If it names another configuration source, such as a key-source setting, that rule contradicts R1. It would need an exception that points at R1.

Questions for you:

- Who is the owner, and who approves the rules? I left placeholders in **Owner** and **Participants and approvers**.
- I wrote no **Confirmation** entries, because no checks exist yet.
