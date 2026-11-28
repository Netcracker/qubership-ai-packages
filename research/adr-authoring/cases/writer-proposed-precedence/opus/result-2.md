## Request 1

### File: docs/adr/0012-answer-503-when-the-policy-store-is-unreachable.md

````markdown
# Refuse a request with HTTP 503 when the policy store is unreachable

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <Role>, <GitHub account>: approves the rules.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R2 of this
  record wins over ADR-0010 R3 for a request where the policy store is unreachable, and ADR-0010 R3 carries the
  exception.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md): R2 of
  this record wins over ADR-0011 R2 for a request where the policy store is unreachable, and ADR-0011 R2 carries the
  exception. ADR-0011 R1 decides the body that carries the reason code.

## Context

The service checks the token of each request and then asks policy evaluation whether to let the request through.
Policy evaluation reads the policies of the endpoint the request calls from the policy store, over the network.

ADR-0010 R3 refuses every request that policy evaluation does not allow with HTTP 403 and the reason code
`POLICY_DENIED`. Under that rule alone, a request whose policies policy evaluation cannot read gets the same answer as a
request that a policy denies. Clients of the service branch on the reason code (ADR-0011).

## Decision

We will refuse a request with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE`, without evaluating any policy,
when the policy store is unreachable for that request.

### Terms

- **policy store**: the network service from which policy evaluation reads its policies.
- **policy store unreachable**: for one request, policy evaluation does not receive the policies of the endpoint the
  request calls from the policy store, because the connection to the policy store fails, because no complete response
  arrives within `<policy store timeout>`, or because the policy store returns an error response.

### Rules

#### A request where the policy store is unreachable

- **R1** (`policy`). For a request where the policy store is unreachable, policy evaluation evaluates no policy, either
  from the policy store or from a copy of its policies held anywhere else, such as a cache.
- **R2** (`api`). A request where the policy store is unreachable is refused with HTTP 503 and the reason code
  `POLICY_STORE_UNAVAILABLE`. For that request, this rule wins over ADR-0010 R3 and ADR-0011 R2.

### Implementation notes

Adds no requirement. Let `internal/policy` return a distinct error when the policy store is unreachable, separate from
the result that denies a request, and let `internal/api` map that error to the response R2 requires.

### Justification

A client that receives 403 with `POLICY_DENIED` concludes that the subject lacks access and has no reason to retry. An
unreachable policy store is a fault of the service, and 503 tells the client that the same request can succeed later
(R2). A distinct reason code also lets operators count outages of the policy store apart from denials (R2).

A copy of the policies can be older than the policies in the policy store, so evaluating it could let through a request
that a newer policy denies (R1).

### Alternatives considered

- **A1. Evaluate the request against the last policies cached from the policy store.** Rejected by R1: a cached policy
  can allow what the current policy denies.
- **A2. Refuse the request with 403 and `POLICY_DENIED`, as ADR-0010 R3 does alone.** Rejected by R2: the client cannot
  tell an outage from a denial.
- **A3. Forward the request to the backend while the policy store is unreachable.** Rejected by ADR-0010 R1: the
  backend trusts every request it receives.

## Consequences

Negative:

- While the policy store is unreachable, the service refuses every request that reaches policy evaluation, including
  requests that the policies would allow (R1, R2). The availability of the service is bounded by the availability of the
  policy store.
- Clients that branch on the reason code receive a value outside the list of ADR-0011 R2 and have to handle it (R2).

## Open points

- **O1.** The value of `<policy store timeout>` in the term **policy store unreachable**, as a duration. The owner of
  this record decides it. It affects R1 and R2.
- **O2.** The term **policy store unreachable** assumes that an error response from the policy store counts as
  unreachable. The answers are to keep it in the term, or to limit the term to a failed connection and a timeout, which
  leaves a request with an error response from the policy store to ADR-0010 R3 and its 403. The owner of this record
  decides it with @platform-architect, the owner of ADR-0010. It affects R1 and R2.
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

- [ADR-0012: Refuse a request with HTTP 503 when the policy store is unreachable](0012-answer-503-when-the-policy-store-is-unreachable.md):
  ADR-0012 R2 decides the response to a request where the policy store is unreachable, and R3 carries the exception.

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
  `POLICY_DENIED`, except a request that ADR-0012 R2 decides, for as long as ADR-0012 R2 binds the change.

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

- [ADR-0012: Refuse a request with HTTP 503 when the policy store is unreachable](0012-answer-503-when-the-policy-store-is-unreachable.md):
  ADR-0012 R2 decides the reason code of a response to a request where the policy store is unreachable, and R2 carries
  the exception.

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from one closed list.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, and `POLICY_DENIED`, except in
  a response that ADR-0012 R2 decides, for as long as ADR-0012 R2 binds the change.

### Justification

A closed list lets a client handle every cause it can receive (R2).
````

### Message to the user

I added `docs/adr/0012-answer-503-when-the-policy-store-is-unreachable.md` with the status `Proposed`. R1 stops policy evaluation from evaluating any policy, cached copies included, when the policy store is unreachable. R2 requires HTTP 503 with `POLICY_STORE_UNAVAILABLE` and states that it wins over ADR-0010 R3.

ADR-0011 R2 also conflicts with the new rule, because its closed list of reason codes doesn't include `POLICY_STORE_UNAVAILABLE`. ADR-0010 and ADR-0011 are both `Proposed`, so I edited them in this change:

- **ADR-0010 R3:** added an exception for a request that ADR-0012 R2 decides, valid only while ADR-0012 R2 binds. I also added a Related ADRs line.
- **ADR-0011 R2:** added the same kind of exception and a Related ADRs line.

The titles and Decision sentences of both records are still true, so I left them as they were.

Questions:

1. Who owns ADR-0012, and who approves it? This decision touches the rules of both @platform-architect (ADR-0010) and @api-owner (ADR-0011), so those two seem the likely approvers. For now the record has placeholders.
2. What should the policy store timeout be? It appears as `<policy store timeout>` in the term **policy store unreachable** (O1).
3. Should an error response from the policy store count as unreachable, as the term assumes (O2)? If it doesn't, such a request gets ADR-0010's 403.
4. Would @api-owner rather add `POLICY_STORE_UNAVAILABLE` to the list in ADR-0011 R2 directly instead of keeping the exception? ADR-0011 is still `Proposed`, so that edit is possible.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-etc-token-gate-config-yaml.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml`, and stop the start without it

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <Role>, <GitHub account>: approves the rules.

## Context

The service needs settings to run, such as the address of the policy store that policy evaluation reads its policies
from. A Go program can take a setting from a file, an environment variable, a command-line flag, or a network service.
With more than one source, the value that applies to a setting depends on which sources an installation sets and in
which order the code reads them.

## Decision

We will read the configuration of the service from the file `/etc/token-gate/config.yaml` alone, and stop the start
where that file is missing.

### Terms

- **configuration**: every setting that the service reads to decide its own behavior, such as a listen address, the
  address of the policy store, or a timeout. The policies that policy evaluation reads from the policy store are not
  configuration.
- **configuration source**: a file, an environment variable, a command-line flag, or a network service from which code
  reads a setting. A default value written in the code is not a configuration source.
- **stops the start**: the process exits with a non-zero status before it accepts a connection. A function in
  `internal/config` meets a rule that requires this outcome by returning an error to its caller.

### Rules

#### Source of the configuration

- **R1** (`config`). The service reads its configuration from the file `/etc/token-gate/config.yaml`, and no
  configuration source changes that path.
- **R2** (`verify`, `policy`, `api`, `config`). No code in this repository outside `_test.go` files reads a setting of
  the configuration from a configuration source other than `/etc/token-gate/config.yaml`.

#### A missing configuration file

- **R3** (`config`). Where `/etc/token-gate/config.yaml` does not exist when the service starts, or exists and cannot be
  read, the service stops the start.

### Implementation notes

Adds no requirement. Keep the path in one constant in `internal/config`. Let the loader take the path as a parameter so
that tests can pass a temporary file, and let the entry point pass the constant and exit with a non-zero status when the
loader returns an error.

### Justification

An operator who reads `/etc/token-gate/config.yaml` sees every setting that applies, and nothing set elsewhere changes
it without showing in that file (R1, R2). A missing file usually means a broken deployment. A service that started on
defaults would then run with settings that nobody chose for that installation (R3).

### Alternatives considered

- **A1. Let a `--config` flag or an environment variable such as `TOKEN_GATE_CONFIG` change the path of the file.**
  Rejected by R1: the path that applies would then depend on how the process was started.
- **A2. Let environment variables override single settings of the file.** Rejected by R2: the file would no longer show
  the value that applies.
- **A3. Start with the default of every setting when the file is missing.** Rejected by R3.

## Consequences

Negative:

- An installation that sets a setting through an environment variable or a flag loses that setting on upgrade (R2),
  and an installation without `/etc/token-gate/config.yaml` stops the start (R3).
- Two instances of the service that share one file system share one configuration (R1). Running the service locally
  takes the file at that absolute path, or a container that provides it.

## Open points

- **O1.** The term **configuration source** assumes that a setting the file leaves out takes the default value written
  in the code. The other answer is that every setting has to be in the file, and that a missing setting stops the start.
  The owner of this record decides it. It affects R2.
- **O2.** R3 assumes that a file that exists and cannot be read, such as one the service's user has no read permission
  for, stops the start just as a missing file does. The other answer is to limit R3 to a missing file. No rule decides
  a file that is read and does not parse as valid configuration. The answers are that it stops the start, or that the
  choice is left to the implementer. The owner of this record decides both questions. They affect R3.
- **O3.** R2 covers the code in this repository. Environment variables that the Go runtime and standard library read on
  their own, such as `GODEBUG`, `HTTP_PROXY`, and `SSL_CERT_FILE`, are outside it. The other answer is to require the
  code to turn off every such read that it can turn off, such as by giving its HTTP client a transport with no proxy
  from the environment. The owner of this record decides it. It affects R2.
````

### Message to the user

I added `docs/adr/0012-read-configuration-only-from-etc-token-gate-config-yaml.md` with the status `Proposed`. It has three rules:

- **R1:** the service reads its configuration from that one path, and nothing can change the path.
- **R2:** no code outside tests reads a setting from any other source. It's tagged with all four layers because a read of an environment variable or a flag could sit anywhere.
- **R3:** a missing or unreadable file stops the start.

ADR-0010 and ADR-0011 have no rules about configuration, so I left them unchanged.

Questions:

1. Who owns this record, and who approves it? For now it has placeholders.
2. I know only the title of ADR-0006. Do any of its rules read a key source, or the list of trusted key sources, from an environment variable, a flag, or a file other than `/etc/token-gate/config.yaml`? If so, that rule contradicts R2. ADR-0006 is `Accepted`, so that rule would have to be replaced by a new record, and the two records would need to be accepted together.
3. Where does the entry point that parses flags and exits live? If it's in a directory that the reading guide doesn't map, such as `cmd/`, the guide needs a layer for it before R2 and R3 can be checked there.
4. Please settle the three assumptions in O1–O3:
   - O1: settings the file leaves out use the defaults written in the code.
   - O2: an unreadable file stops the start just like a missing one, and nothing yet decides what happens to a file that doesn't parse.
   - O3: environment variables that the Go standard library reads on its own fall outside R2.
