## Request 1

### File: docs/adr/0012-refuse-with-503-while-the-policy-store-is-unreachable.md

````markdown
# Refuse a request with HTTP 503 while the policy store is unreachable

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1 and R2.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R3 gains
  an exception that points at R2 of this record.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md): R2 gains
  an exception that points at R2 of this record.

## Context

Policy evaluation reads the policies of the endpoint a request calls from a policy store over the network (ADR-0010
R2). ADR-0010 R3 refuses a request that policy evaluation does not allow with HTTP 403 and the reason code
`POLICY_DENIED`. Where the policy store cannot be reached, policy evaluation has no policy to evaluate, and ADR-0010
does not say what the service sends back.

## Decision

We will refuse a request with a verified token with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE` where the
policy store is unreachable, and we will not evaluate a policy for it.

### Terms

- **policy store unreachable**: for one request, the read of the policies of the endpoint that the request calls ends
  with no response from the policy store, or has not ended after `<policy store timeout>`.

### Rules

#### Policy store outage

- **R1** (`policy`). Where the policy store is unreachable for a request with a verified token, policy evaluation
  evaluates no policy for that request.
- **R2** (`api`). Where the policy store is unreachable for a request with a verified token, the service refuses the
  request with HTTP 503 and the value `POLICY_STORE_UNAVAILABLE` in the field `reason` of the response body. It does not
  refuse the request with the HTTP 403 and the reason code `POLICY_DENIED` of ADR-0010 R3.

### Justification

A client that receives 503 can tell an outage from a denial. A 403 would report a denial that no policy has decided
(R2). Evaluating no policy keeps the service from deciding without the policies it was built to read (R1).

### Alternatives considered

- **A1. Refuse the request with HTTP 403 and `POLICY_DENIED` where the policy store is unreachable.** Rejected by R2:
  this reverses ADR-0010 R3 for the case of an outage, because a client cannot tell the outage from a denial.

## Consequences

Positive:

- A client can retry on 503 and give up on 403, because the status separates an outage from a denial.

Negative:

- While the policy store is unreachable, the service refuses every request with a verified token (R2).
- A client that handles every value of the closed list in ADR-0011 R2 must also handle `POLICY_STORE_UNAVAILABLE`.

## Open points

- **O1.** The value of `<policy store timeout>` in the term **policy store unreachable**. The platform architect
  decides. It affects R1 and R2.
- **O2.** Whether a response from the policy store that carries an error, such as an HTTP 500, counts as unreachable.
  This record assumes it does not, so R1 and R2 leave that case to the implementer. The answers are "counts" and "does
  not count". The platform architect decides. It affects R1 and R2.
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
  `POLICY_DENIED`. Exception: a request to which ADR-0012 R2 applies is refused as that rule says, and only while
  ADR-0012 R2 binds the change.

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

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from a closed set.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, and `POLICY_DENIED`.
  Exception: in a response that ADR-0012 R2 describes, the value is `POLICY_STORE_UNAVAILABLE`, and only while
  ADR-0012 R2 binds the change.

### Justification

A closed set lets a client handle every cause it can receive (R2).
````

### Message to the user

I added ADR-0012 as `Proposed`. It has two rules: R1 (`policy`) says no policy is evaluated, and R2 (`api`) says the response is 503 with `POLICY_STORE_UNAVAILABLE` in `reason`, not the 403 of ADR-0010 R3.

I also edited two records, both `Proposed` on this branch:
- **ADR-0010 R3:** it gets an exception for the case ADR-0012 R2 covers. The exception holds only while ADR-0012 R2 binds. The title and the Decision sentence of ADR-0010 stay true.
- **ADR-0011 R2:** this one you didn't mention. The closed list in R2 does not contain `POLICY_STORE_UNAVAILABLE`, so a checker would flag every 503. I added an exception that points at ADR-0012 R2. I changed "one closed list" to "a closed set" in its Decision and Justification, because the list is no longer in one place.

Questions:
1. Who is the owner of ADR-0012, and who approves it? I left placeholders. The owners of ADR-0010 (@platform-architect) and ADR-0011 (@api-owner) should probably approve, since their records changed.
2. What is `<policy store timeout>` (open point O1)?
3. Does an error response from the store, such as an HTTP 500, count as unreachable (O2)? I assumed it does not.

The record stays `Proposed` until O1 and O2 are settled. It has no **Confirmation** section yet because no check exists. Code that implements R1 and R2 should end its commit message and pull request description with `Implements: ADR-0012 R1, R2`. The trailers count for nothing until the record is accepted.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-one-file.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml`

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1 and R2.

## Context

The service reaches the policy store over the network, so it needs settings before it serves its first request.

## Decision

We will read the configuration of the service only from `/etc/token-gate/config.yaml`, and we will stop the start where
that file is missing.

### Terms

- **setting**: a value that code of this repository reads to choose the behavior of the service. A value that the Go
  runtime or a library reads on its own, such as `GOMAXPROCS`, is not a setting.
- **missing**: the path `/etc/token-gate/config.yaml` does not name an existing file.
- **stops the start**: the process exits before it serves a request. A library below the entry point meets this by
  returning an error that the entry point turns into the exit.

### Rules

#### Source of the configuration

- **R1** (`config`). The service reads every setting from the file `/etc/token-gate/config.yaml` and from no other
  source, such as another file, an environment variable, a command-line argument, or a remote service.

#### Missing file

- **R2** (`config`). Where `/etc/token-gate/config.yaml` is missing, the service stops the start, and it does not
  replace the file with default settings.

### Justification

One file puts every setting in one place, so a reader finds the whole configuration of an instance there (R1). A
service that starts without its file would run on settings that nobody chose, so a deployment without the file stops
at once (R2).

### Alternatives considered

- **A1. Read a setting from an environment variable or a command-line argument.** Rejected by R1: the configuration
  would then sit in several places.
- **A2. Start with built-in default settings where the file is missing.** Rejected by R2.

## Consequences

Negative:

- A deployment must provide the file at `/etc/token-gate/config.yaml`, such as a mounted volume in a container (R1). A
  different path takes a new record.
- A development machine without that file cannot start the service (R2).

## Open points

- **O1.** This record assumes that the service reads no setting from an environment variable or a command-line
  argument. The answers are "no setting from them" and "some settings, such as a secret, may come from the
  environment". The owner decides. It affects R1.
- **O2.** What the service does where the file exists but cannot be read or parsed. The answers are "stops the start"
  and "left to the implementer". The owner decides. It affects R2.
````

### Message to the user

I added ADR-0012 as `Proposed`, with R1 (the only source is the file) and R2 (a missing file stops the start). Both rules are tagged `config`, which maps to `internal/config`.

Questions:
1. Who is the owner, and who approves? I left placeholders.
2. Open point O1: is the file really the only source? I read "only" to exclude environment variables and flags too. If a secret may come from the environment, R1 needs an exception.
3. Open point O2: should an unreadable or invalid file also stop the start? You only named a missing file, so R2 covers only that case.
4. Please confirm the reasons in the Justification and the two alternatives. You gave none, so I wrote the obvious ones.

I judged precedence against ADR-0006 only from its summary, because I can't see its rules. If ADR-0006 says where key sources are configured, check that its rules fit R1.

The record stays `Proposed` until O1 and O2 are settled. Code that implements it should end its commit message and pull request description with `Implements: ADR-0012 R1, R2`. The trailers count for nothing until the record is accepted.
