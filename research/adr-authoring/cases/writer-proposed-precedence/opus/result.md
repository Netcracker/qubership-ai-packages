## Request 1

### File: docs/adr/0012-answer-503-when-the-policy-store-is-unreachable.md

````markdown
# Refuse a request with HTTP 503 when the policy store is unreachable

## Status

Proposed

### Owner

@platform-architect

### Participants and approvers

- Platform architect, @platform-architect: approves R1 and the exception it adds to ADR-0010 R3.
- API owner, @api-owner: approves the reason code in R1 and the exception it adds to ADR-0011 R2.

### Related ADRs

- [ADR-0010: Refuse every request that policy evaluation does not allow](0010-refuse-what-policy-denies.md): R1 of this
  record wins over ADR-0010 R3 when the policy store is unreachable, and ADR-0010 R3 carries the exception.
- [ADR-0011: Name the reason for every error response in a reason code](0011-reason-codes-in-error-responses.md): R1 of
  this record adds `POLICY_STORE_UNAVAILABLE` to the values of `reason` that ADR-0011 R2 lists, and ADR-0011 R2 carries
  the exception.

## Context

Policy evaluation decides, for each request with a verified token, whether the subject may call the endpoint. It reads
the policies for that decision from the policy store over the network, so the store can be unreachable while the service
runs.

The backend trusts every request it receives, and the service forwards a request only where policy evaluation allows it
(ADR-0010 R1). A request that policy evaluation does not allow is refused with HTTP 403 and the reason code
`POLICY_DENIED` (ADR-0010 R3). Without this record, that rule also covers a request whose policies policy evaluation
could not read. A client then gets the same answer for a policy that denies the subject as for an outage of the policy
store. Clients of the service branch on the cause of a refusal (ADR-0011).

## Decision

We will refuse a request with HTTP 503 and the reason code `POLICY_STORE_UNAVAILABLE` when the policy store is
unreachable, instead of evaluating its policy.

### Terms

- **verified token**: as ADR-0010 uses it.
- **policy store unreachable** for a request: while it decides the request, policy evaluation gets no policies for the
  endpoint from the policy store, because the connection to the store fails, the store returns an error, or no response
  arrives within `<policy store timeout>`.

### Rules

#### Requests while the policy store is unreachable

- **R1** (`policy`, `api`). A request with a verified token for which the policy store is unreachable is refused with
  HTTP 503 and the value `POLICY_STORE_UNAVAILABLE` in the field `reason` of its body. This rule wins over ADR-0010 R3.

### Implementation notes

Adds no requirement. Let `internal/policy` return a distinct error, such as `ErrStoreUnavailable`, when it cannot read
the policies, rather than a deny decision. Let `internal/api` map that error to the 503 response, and keep the mapping of
a deny decision to 403 as it is.

### Justification

HTTP 503 tells a client that the refusal is temporary and that the same request can succeed later. HTTP 403 tells it that
the subject may not call the endpoint, and a client that receives 403 stops retrying (R1). The reason code lets a client
that branches on `reason` tell an outage from a denial without parsing the status (R1). The request still does not reach
the backend, because the backend trusts every request it receives (ADR-0010 R1).

### Alternatives considered

- **A1. Refuse the request with HTTP 403 and `POLICY_DENIED`, as ADR-0010 R3 does for every request it does not
  allow.** Rejected by R1: the client cannot tell an outage from a denial.
- **A2. Evaluate a built-in default policy when the policy store is unreachable.** Rejected by R1: the request gets the
  result of the default policy, not 503.
- **A3. Forward the request to the backend when the policy store is unreachable.** The backend trusts every request it
  receives, and ADR-0010 R1 already forbids this.

## Consequences

Negative:

- A client that treats every refusal by policy as HTTP 403 gets HTTP 503 during an outage of the policy store, and a
  client that handles a closed set of `reason` values meets one it does not know yet (R1).
- Every request with a verified token fails while the policy store is unreachable, including requests to endpoints whose
  policies did not change.

Follow-ups:

- Tell the clients that branch on `reason` about `POLICY_STORE_UNAVAILABLE` before a release brings R1.

## Open points

- **O1.** How long policy evaluation waits for the policy store before the store counts as unreachable:
  `<policy store timeout>`. The platform architect decides. Affects the term **policy store unreachable** and R1.
- **O2.** The term **policy store unreachable** assumes that an error returned by the policy store, such as an HTTP 5xx
  status, counts as unreachable, like a failed connection. The other answer is that only a failed connection and a
  timeout count, and an error from the store needs a rule of its own. The platform architect decides. Affects R1.
- **O3.** R1 assumes that policy evaluation reads the policies from the policy store for every request and evaluates no
  copy that it read earlier. The other answer is that policy evaluation may evaluate a copy up to a maximum age, which
  then needs a rule with that age. The platform architect decides. Affects the term **policy store unreachable** and R1.
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
  ADR-0012 R1 wins over R3 when the policy store is unreachable.

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
  `POLICY_DENIED`. Exception: while ADR-0012 R1 binds a change, a request that ADR-0012 R1 covers is refused as
  ADR-0012 R1 states.

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
  ADR-0012 R1 adds the value `POLICY_STORE_UNAVAILABLE`, and R2 carries the exception.

## Context

Clients of the service branch on the cause of a refusal, and the HTTP status alone does not tell an expired token from
a denied policy.

## Decision

We will name the cause of every error response in a reason code from one closed list.

### Rules

#### Error responses

- **R1** (`api`). Every response with an HTTP status of 400 or higher has a JSON body with the field `reason`.
- **R2** (`api`). The value of `reason` is one of `TOKEN_EXPIRED`, `TOKEN_KID_MISSING`, and `POLICY_DENIED`.
  Exception: while ADR-0012 R1 binds a change, the value is `POLICY_STORE_UNAVAILABLE` in a response that ADR-0012 R1
  requires.

### Justification

A closed list lets a client handle every cause it can receive (R2).
````

### Message to the user

I added ADR-0012 (`Proposed`). It has one rule, R1, tagged `policy` and `api`: a request with a verified token for which the policy store is unreachable gets HTTP 503 with `reason` set to `POLICY_STORE_UNAVAILABLE`. The request still never reaches the backend, because ADR-0010 R1 already covers that.

Two other `Proposed` records had rules that conflict with the new one, so I edited them:

- **ADR-0010 R3:** It would also refuse this case with 403 and `POLICY_DENIED`. It now has an exception that points at ADR-0012 R1 and applies only while that rule binds.
- **ADR-0011 R2:** Its closed list of `reason` values would forbid `POLICY_STORE_UNAVAILABLE`. It now has a matching exception.

I also added a line under **Related ADRs** in both records. Their titles and Decision sentences still hold, so I didn't change them. The 503 response still needs the `reason` body that ADR-0011 R1 requires, and ADR-0012 R1 provides it.

Questions:

1. **Owner and approvers:** I made @platform-architect the owner and added @api-owner as an approver for the reason code, since they own the two rules that get exceptions. Is that right?
2. **O1:** How long should policy evaluation wait for the policy store before the store counts as unreachable? R1 uses the placeholder `<policy store timeout>` until you give a value.
3. **O2:** Should an error response from the policy store, such as an HTTP 5xx, count as unreachable, the same as a failed connection or a timeout? The draft assumes it does.
4. **O3:** May policy evaluation use a copy of the policies it read earlier while the store is down? The draft assumes it may not.

ADR-0012 stays `Proposed` until O1–O3 are answered.

## Request 2

### File: docs/adr/0012-read-configuration-only-from-etc-token-gate-config-yaml.md

````markdown
# Read the configuration only from `/etc/token-gate/config.yaml`, and stop the start when the file is missing

## Status

Proposed

### Owner

@<owner>

### Participants and approvers

- <role>, @<account>: approves R1 and R2.

## Context

The service needs settings when it starts, such as where the policy store is. Its configuration code lives in
`internal/config`. Each source a service reads its settings from is one more place an operator has to check to know what
an installation runs with.

## Decision

We will read the configuration of the service only from the file `/etc/token-gate/config.yaml`, and the service stops the
start when that file is missing.

### Terms

- **configuration**: every value that an operator sets for one installation of the service.
- **stops the start**: the process exits with a nonzero status before it serves a request. `internal/config` meets this
  by returning an error from the function that loads the configuration, and the entry point of the program exits on that
  error.

### Rules

#### Source of the configuration

- **R1** (`config`). The service reads its configuration from the file `/etc/token-gate/config.yaml` and from no other
  source: no other file, no environment variable, and no command-line flag. No setting changes the path of that file.

#### Missing file

- **R2** (`config`). Where `/etc/token-gate/config.yaml` does not exist or cannot be read when the service starts, the
  service stops the start.

### Implementation notes

Adds no requirement. Keep the path as one constant in `internal/config`. Return an error that names the path and the
cause, such as `read config '/etc/token-gate/config.yaml': no such file or directory`, so that the error the process
logs before it exits tells the operator which file to provide. In tests, use a loader that takes the file contents, so
that a test does not need a file under `/etc`.

### Justification

With one file as the only source, an operator who reads that file knows every setting of the installation, and no
environment variable or flag changes it without a trace in the file (R1). A service that starts without its file would
run on built-in values that no operator chose, so the service stops the start instead (R2).

### Alternatives considered

- **A1. Let environment variables override settings in the file.** Rejected by R1.
- **A2. Take the path of the file from a command-line flag such as `--config`.** Rejected by R1.
- **A3. Start with built-in default values when the file is missing.** Rejected by R2.

## Consequences

Negative:

- An installation that sets any configuration through an environment variable or a command-line flag loses that setting
  on upgrade, and where it has no `/etc/token-gate/config.yaml`, the upgraded service stops the start (R1, R2).
- Running the service on a developer machine or in an integration test needs a file at `/etc/token-gate/config.yaml`,
  such as one mounted into a container (R1).
- Credentials the service needs, such as for the policy store, are part of the configuration and sit in the same file
  (R1).

## Open points

- **O1.** R2 assumes that a file the service cannot read, such as one without read permission for the service user,
  stops the start like a missing file. The other answer is that only a missing file stops the start, and an unreadable
  file needs a rule of its own. The owner also decides whether a file with invalid YAML stops the start, which would be
  a new rule. Affects R2.
- **O2.** The term **configuration** assumes that credentials count as configuration, so R1 puts them in the file. The
  other answer is that credentials come from another source, such as a mounted secret file, which R1 would then name.
  The owner decides. Affects the term **configuration** and R1.
````

### Message to the user

I added ADR-0012 (`Proposed`) with two rules, both tagged `config`:

- **R1:** The service reads its configuration only from `/etc/token-gate/config.yaml`. It reads no other file, no environment variable, and no command-line flag, and no setting changes the path.
- **R2:** A missing file stops the start. The draft also treats an unreadable file as missing.

The record defines "stops the start" as the process exiting before it serves a request. `internal/config` meets that by returning an error.

Questions:

1. **Owner and approvers:** Who owns this record, and who approves it? The metadata has placeholders until you tell me.
2. **Current configuration:** How is the service configured today? If installations use environment variables or flags, they lose those settings on upgrade. Without the file, the upgraded service won't start. **Negative** lists this, and I'd like to confirm the case is real.
3. **ADR-0006:** Does the accepted ADR-0006 name a key source that comes from somewhere other than this file, such as an environment variable? If so, it conflicts with R1. Because ADR-0006 is accepted, that part would need a superseding record rather than an edit.
4. **O1:** Should an unreadable file stop the start the same way a missing file does? Should invalid YAML stop the start too?
5. **O2:** Do credentials belong in the file, or should they come from another source?

ADR-0012 stays `Proposed` until O1 and O2 are answered.
