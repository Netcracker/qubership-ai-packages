## Request 1

### File: docs/adr/0012-refuse-with-503-when-policy-store-unreachable.md

````markdown
# Refuse a request with HTTP 503 when the policy store is unreachable

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- `<role>`, `<GitHub account>`: approves R1 and R2.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R1 of
  this record wins over ADR-0010 R3 for a request for which the policy store is unreachable. ADR-0010 R2 names the
  policies that a read covers.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md):
  ADR-0011 R1 gives the 503 response of R1 its `reason` field, and ADR-0011 R2 lists `POLICY_STORE_UNAVAILABLE`.

## Context

Policy evaluation reads the policies of the endpoint that a request calls from the policy store over the network
(ADR-0010 R2). Without this record, a request whose policies cannot be read is not allowed by policy evaluation, so
ADR-0010 R3 refuses it with HTTP 403 and `POLICY_DENIED`. A client then gets the same response for an outage of the
policy store as for a subject that lacks access. ADR-0011 records that clients of the service branch on the cause of a
refusal.

## Decision

We will refuse a request with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE` when its policies cannot be read
from the policy store, and policy evaluation will evaluate no policy for that request.

### Terms

- **policy store**: the network service from which policy evaluation reads its policies.
- **policy store unreachable**: for a request, the read of the policies that ADR-0010 R2 names for it ends in one of
  three ways: the connection to the policy store fails, the read ends under R2, or the policy store returns an error in
  place of the policies. A read that returns policies, an empty set of policies included, leaves the policy store
  reachable for that request.

### Rules

#### Outage of the policy store

- **R1** (`policy`, `api`). A request for which the policy store is unreachable is refused with HTTP 503 and the reason
  code `POLICY_STORE_UNAVAILABLE`, and policy evaluation evaluates no policy for that request. R1 wins over ADR-0010
  R3.
- **R2** (`policy`). Policy evaluation ends a read of policies from the policy store that has not completed
  `<policy store timeout>` after the read started.

### Implementation notes

Adds no requirement. Let the read in `internal/policy` return an error type of its own for the three outcomes that
**policy store unreachable** lists, separate from a deny decision, and let `internal/api` map that error to the 503
response. A test can run a stub of the policy store that refuses the connection, sends no response, or returns an
error, and check the status and the `reason` of each response.

### Justification

With a 403, a client cannot tell an outage of the policy store from a denial. A 503 with its own reason code separates
the two cases, so a client can retry the request after the outage (R1). Evaluating no policy keeps the service from
deciding access on policies it could not read for the request (R1). The timeout bounds how long a request waits for a
policy store that sends no response, and turns that case into one that R1 covers (R2).

### Alternatives considered

- **A1. Refuse with HTTP 403 and `POLICY_DENIED` when the policy store is unreachable.** Rejected by R1: a client
  cannot tell this response from a denial. This record reverses the result that ADR-0010 R3 gave for this case.
- **A2. Evaluate the request against policies read before the outage, such as a cached copy.** Rejected by R1: access
  would be decided on policies that may have changed since the copy was read.
- **A3. Forward the request to the backend while the policy store is unreachable.** Rejected by R1: the backend trusts
  every request it receives.

## Consequences

Negative:

- While the policy store is unreachable, every request that reaches policy evaluation is refused, also a request that
  its policies would allow (R1). The availability of the service is bounded by the availability of the policy store.
- A request whose policies cannot be read got HTTP 403 with `POLICY_DENIED` under ADR-0010 R3, and gets HTTP 503 with
  `POLICY_STORE_UNAVAILABLE` under R1. A client that handles only the earlier reason codes receives a value it does not
  handle.
- A request to an unresponsive policy store waits up to `<policy store timeout>` before it is refused (R2).

Follow-ups:

- Tell the clients of the service about the new status and reason code.

## Open points

- **O1.** The value of `<policy store timeout>` in R2. The owner of this record decides; no value is proposed yet.
  Affects R2, and R1 through **policy store unreachable**.
- **O2.** This record assumes that an error the policy store returns in place of the policies makes the policy store
  unreachable. The other answer counts only a failed connection and a read ended under R2, and leaves an error
  response from the policy store to ADR-0010 R3. The owner of this record decides. Affects R1.
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

- [ADR-0012: Refuse a request with HTTP 503 when the policy store is unreachable](0012-refuse-with-503-when-policy-store-unreachable.md):
  ADR-0012 R1 sets the response for a request whose policies cannot be read from the policy store, and wins over R3.

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
  `POLICY_DENIED`, except where ADR-0012 R1 applies.

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

- [ADR-0012: Refuse a request with HTTP 503 when the policy store is unreachable](0012-refuse-with-503-when-policy-store-unreachable.md):
  ADR-0012 R1 uses `POLICY_STORE_UNAVAILABLE`, which R2 lists.

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from one closed list.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, `POLICY_DENIED`, and
  `POLICY_STORE_UNAVAILABLE`.

### Justification

A closed list lets a client handle every cause it can receive (R2).
````

### Message to the user

I added ADR-0012 as `Proposed`. It has two rules:

- **R1:** a request whose policies can't be read from the policy store gets HTTP 503 with `POLICY_STORE_UNAVAILABLE`. Policy evaluation evaluates no policy for that request, and R1 wins over ADR-0010 R3.
- **R2:** a read from the policy store has a timeout, so that a store that never responds also counts as unreachable.

I also changed two other records:

- **ADR-0010 R3:** I added "except where ADR-0012 R1 applies". Without it, R3 still reads as unconditional.
- **ADR-0011 R2:** I added `POLICY_STORE_UNAVAILABLE` to the closed list. Otherwise the new 503 response would break ADR-0011 R2.

Both records are `Proposed`, so I edited them in place. @platform-architect and @api-owner each need to approve the change to their record.

Questions:

1. Who owns ADR-0012, and who approves it? I left placeholders. I'd suggest @platform-architect as owner, with @api-owner approving the reason code.
2. What should the policy store timeout in R2 be (O1)?
3. Should an error that the policy store returns instead of the policies also count as unreachable (O2)? I assumed yes. If not, that case keeps the 403 from ADR-0010 R3.
4. Should the 503 response carry a `Retry-After` header? No rule covers that yet.

ADR-0012 stays `Proposed` until O1 and O2 are settled.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-etc-file.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml`

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- `<role>`, `<GitHub account>`: approves R1 and R2.

### Related ADRs

- [ADR-0006: Trusted key sources](0006-trusted-key-sources.md): the keys read from the key sources it trusts are not
  configuration under this record.

## Context

The service reads values at start that set its behavior, and the code that reads them belongs to the `config` layer,
`internal/config`. The service also reads data that sets no behavior of its own: policy evaluation reads its policies
over the network from the policy store, and token verification uses keys from the key sources that ADR-0006 trusts.

## Decision

We will read the configuration of the service from the file `/etc/token-gate/config.yaml` and from no other source,
and stop the start where that file is missing.

### Terms

- **configuration**: every value that the code of the service reads to set its own behavior, such as an address, a
  timeout, or a switch. The policies that policy evaluation reads from the policy store, the keys read from a key source
  that ADR-0006 trusts, and the environment variables that the Go runtime reads itself, such as `GOMAXPROCS`, are not
  configuration.
- **stops the start**: the process exits with a nonzero status before it accepts a connection. Code in
  `internal/config` meets a rule that requires this outcome by returning an error to its caller.

### Rules

#### Source of the configuration

- **R1** (`verify`, `policy`, `api`, `config`). The service reads its configuration only from the file
  `/etc/token-gate/config.yaml`: no environment variable, command-line flag, or other file sets a value of the
  configuration or changes the path of that file.
- **R2** (`config`). Where the file `/etc/token-gate/config.yaml` does not exist or the service cannot read it, the
  service stops the start.

### Implementation notes

Adds no requirement. Let the loader in `internal/config` take the path as a parameter, and let the entry point pass the
path from R1 as a constant. A test can then pass a path in a temporary directory, and check that the loader returns an
error where no file exists at that path.

### Justification

With one fixed file, an operator sees every value of the configuration in one place, and no environment variable or
flag sets a value that the file does not show (R1). A service that started without its file would run with values that
no operator chose. For a service that decides access, a stopped start is safer than such a run (R2).

### Alternatives considered

- **A1. Override a value of the file with an environment variable.** Rejected by R1: the running value would differ
  from the value in the file.
- **A2. Take the path of the file from a command-line flag, such as `--config`.** Rejected by R1: the path in use would
  depend on how each installation starts the process.
- **A3. Start with values built into the service where the file is missing.** Rejected by R2: the service would run
  with values that no operator chose.

## Consequences

Negative:

- An installation that sets the configuration through environment variables, flags, or a file at another path loses
  those values on upgrade (R1). Where it has no file at `/etc/token-gate/config.yaml`, the service stops the start
  (R2).
- Running the service on a developer machine needs the file at `/etc/token-gate/config.yaml`, which usually takes root
  access or a container (R1).
- Two instances on one host need separate filesystems, such as containers, to run with different configuration (R1).

## Open points

- **O1.** This record assumes that a file the service cannot read, such as one without read permission for the user the
  service runs as, stops the start like a missing file. The other answer leaves an unreadable file to the implementer.
  The owner of this record decides. Affects R2.
- **O2.** The service could meet a file that exists but lacks a value or holds an invalid one. It could stop the start,
  or use a value built into the service. The owner of this record decides, and the answer would add a rule to this
  record.
````

### Message to the user

I added ADR-0012 as `Proposed`. It has two rules:

- **R1:** the configuration comes only from `/etc/token-gate/config.yaml`. No environment variable, flag, or other file sets a value or changes the path.
- **R2:** if that file is missing or can't be read, the service stops the start.

R1 can be broken in any package, so it carries all four layer tags. The record defines "configuration" so that it leaves out the policies from the policy store, the keys from the ADR-0006 key sources, and Go runtime variables such as `GOMAXPROCS`.

Questions:

1. Who owns this record, and who approves it? I left placeholders.
2. Should a file that exists but can't be read stop the start like a missing one (O1)? I assumed yes.
3. If the file exists but a value is missing or invalid, should the start stop, or should the service use a built-in value (O2)? Your answer would add a rule.
4. Where is the entry point that exits the process? The reading guide maps only `internal/verify`, `internal/policy`, `internal/api`, and `internal/config`. If the entry point is somewhere else, such as `cmd/`, the guide needs to map that path to a layer.

The record stays `Proposed` until O1 and O2 are settled.
