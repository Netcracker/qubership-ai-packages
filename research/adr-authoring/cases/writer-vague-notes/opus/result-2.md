### File: docs/adr/0001-retry-policy-calls-then-refuse-with-503.md

````markdown
# Retry a failed call to the policy service, then refuse the request with HTTP 503

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team, `<platform team account>`: approves the decision.

## Context

token-gate checks the token of each incoming request before policy evaluation. To get a policy decision,
`internal/policyclient` calls the policy service over HTTP. `internal/handler` turns the errors that
`internal/policyclient` returns into HTTP responses.

A call to the policy service can fail. The service may not respond, the connection may break, or the service may return
a server error. token-gate needs a defined way to handle these failures: how long one call may take, whether it tries
again, and what the caller of token-gate gets when the policy service stays unavailable.

## Decision

We will retry a failed call to the policy service a fixed number of times, with a timeout of 5 seconds on each call. When
every call fails, token-gate refuses the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **policy call**: everything `internal/policyclient` does to get one policy decision for one incoming request. A
  policy call consists of one or more attempts.
- **attempt**: one HTTP request from `internal/policyclient` to the policy service. An attempt runs from the moment
  `internal/policyclient` starts sending it until it has read the full response or the attempt has failed.
- **failed attempt**: an attempt that ends in one of these ways:
  - the timeout of R1;
  - a transport error, such as a refused or reset connection, a DNS failure, or a failed TLS handshake;
  - a response with an HTTP status from 500 through 599.

  An attempt that ends with any other HTTP response is not a failed attempt.
- **policy service unavailable**: the outcome of a policy call in which every attempt that R2 allows was a failed
  attempt.

### Rules

#### Timeout

- **R1** (`policyclient`). `internal/policyclient` abandons an attempt when it has not read the full response 5 seconds
  after the attempt started, and that attempt is a failed attempt. Each attempt of a policy call gets its own 5
  seconds, counted from its own start.

#### Retries

- **R2** (`policyclient`). After a failed attempt, `internal/policyclient` starts another attempt of the same policy
  call, until it has made `<retry count>` attempts after the first one. A policy call therefore makes at most 1 +
  `<retry count>` attempts. `internal/policyclient` starts no further attempt of a policy call after an attempt that is
  not a failed attempt.

#### Response

- **R3** (`policyclient`, `handler`). When a policy call ends with the policy service unavailable, token-gate refuses
  the incoming request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`, and does not pass the request on.
  token-gate uses the reason code `POLICY_UNAVAILABLE` for no other outcome.

### Justification

Many failures of an HTTP call are transient, such as a dropped connection or a restarting instance of the policy
service. Another attempt often succeeds, so a short outage does not refuse requests that would otherwise pass (R2). A
fixed number of attempts bounds the work that one request can cause (R2).

A timeout on each attempt keeps a policy service that does not respond from holding a request open without limit (R1).
Giving each attempt its own 5 seconds means a slow first attempt does not leave a retry with less time than the first
attempt had (R1).

token-gate is a security check. When it cannot get a policy decision, it refuses the request rather than letting it
through without one (R3). HTTP 503 tells the caller that the failure is on the server side and temporary. The reason
code `POLICY_UNAVAILABLE` lets the caller and an operator tell this case apart from a refused token (R3).

### Alternatives considered

- **A1. Admit the request when the policy service is unavailable (fail open).** Rejected by R3: a request would pass
  the gate without a policy decision.
- **A2. Refuse the request after the first failed attempt, with no retry.** Rejected by R2: a single transient failure
  would refuse a request that a second attempt would have admitted.
- **A3. One 5-second deadline shared by all attempts of a policy call.** Rejected by R1: a retry after a slow first
  attempt would get little or no time.

## Consequences

Negative:

- When the policy service does not respond, a request waits up to (1 + `<retry count>`) × 5 seconds, plus any delay
  between attempts, before token-gate refuses it (R1, R2).
- Retries add load to a policy service that is already failing: one incoming request can cause up to 1 +
  `<retry count>` requests to the policy service (R2).
- While the policy service is unavailable, token-gate refuses every request, including requests with a valid token
  (R3).

Follow-ups:

- Document HTTP 503 with the reason code `POLICY_UNAVAILABLE` for the callers of token-gate.

## Open points

- **O1.** How many retries does a policy call make? The meeting settled on "a few" and named no number. The platform
  team decides. This affects R2, and through the term **policy service unavailable**, R3.
- **O2.** The term **failed attempt** assumes that a response with a status from 500 through 599 is a failed attempt,
  and that every other response is not. Two answers are under consideration: keep the term as written, or also count
  HTTP 429 and a 2xx response whose body `internal/policyclient` cannot parse as failed attempts. The owner of this
  record decides with the platform team. This affects R2 and R3.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. Each record states one decision, why we
made it, and the rules that the code must meet. Records are numbered in order: `0001-<title>.md`, `0002-<title>.md`, and
so on. A retired number is never reused.

The checking steps, the verdict table, and the three paragraphs after the table come word for word from the
`adr-authoring` skill, version `<skill version>`.

## How to read a record

The **Decision** section states the decision in one or two sentences. **Terms** defines the words whose extent a rule
depends on, and a rule uses each term in exactly that sense. **Rules** holds every requirement of the record as a
numbered rule, such as R1. Nothing outside **Rules** adds a requirement. **Justification** gives the reason for each
rule, and **Alternatives considered** names the designs the record rejects and the rule that rejects each one.
**Open points** lists the questions the record does not settle yet.

Outside its own record, a rule is always cited with its record, as `ADR-0001 R2`. A rule number never changes once the
record has merged or the number appears in an issue, a commit, or another pull request.

Anything that no rule states is the implementer's choice.

## Layers

Each rule names, in parentheses, the layer where its check runs. A checker looks there first.

| Layer | Role | Paths |
| --- | --- | --- |
| `policyclient` | Calls the policy service over HTTP. | `internal/policyclient/` |
| `handler` | Turns errors into HTTP responses. | `internal/handler/` |

A change that adds code under no mapped path extends this table.

## Trailers

A change to code that a record governs declares, at the end of its commit message and of its pull request description,
which rules it brings and which it leaves for a later change:

```text
Implements: ADR-0001 R1, R2
Defers: ADR-0001 R3 to #<issue>
```

`Implements` claims every case of a rule. A change that brings only some cases of a rule names it under `Defers`. A
`Defers` target is an issue or a pull request that exists. A change that brings no rule and leaves none out, such as a
refactoring, carries neither trailer.

## Which records bind a change

`Accepted` and `Proposed` records bind a change. `Superseded` and `Rejected` records do not.

## How to check a change

1. Read the two trailers in the pull request description. They are claims: `Implements` makes a rule touched, and
   `Defers` can make an untouched rule `Deferred`, but neither shows that the code meets a rule. An entry that names no
   rule of a binding record, or a `Defers` target that is not an existing issue or pull request, counts for nothing in
   steps 2 and 3, and the report lists it as a trailer error.
2. Walk every rule of a binding record that sits in a layer the change touches, every other rule of a binding record
   that the change touches, named or not, and every rule of a binding record that the change names under `Defers`. A
   change touches a layer when it adds, changes, or removes a file that the guide maps to that layer, and a changed file
   under no mapped path is a guide error that the report lists. Skip a rule whose
   own record names it as replaced under **Related ADRs**: that line, like the status `Superseded`, is added when the
   replacement is accepted. A rule of a `Proposed` record that replaces an accepted rule binds nothing until its record
   is accepted: the walk skips it, a trailer entry that names it counts for nothing, and the accepted rule governs until
   then. A binding record without numbered rules is not walked, and the
   report lists it as unchecked. A missing line of code shows in no diff, so this walk finds the rule a change forgot.
3. Give each rule one verdict, and group the rows by root cause, because one defect can break several rules. Report
   `Not touched` rules as a count.

| Verdict | Meaning |
| --- | --- |
| Conforms | The change touches the rule, and in the case it meets the rule under every reading and every answer an open point lists. |
| Violates | The change touches the rule, and in the case it fails the rule under every reading and every answer an open point lists. |
| Deferred | The change names the rule under `Defers` and does not touch it, and the rule is unmet under at least one reading or its outcome depends on an open point. |
| Not touched | The change does not touch the rule, and the rule is not `Deferred`. |
| Cannot tell | The change touches the rule, and in the case it meets the rule under one reading or answer and fails it under another, or the repository does not show the outcome. |

A case of a rule is one input or condition the rule describes, with the outcome the rule requires for it: a missing
value and an invalid value of one field are two cases of one rule, and each member of a set a rule covers, such as each
endpoint, is a case of its own. A case meets the rule only for every value of each setting and input the rule leaves
free. A judged case whose outcome the repository does not show, such as a limit a proxy enforces, gets `Cannot tell`,
and the report names what it could not see. A change touches a rule when it adds, changes, or removes code,
configuration, or a file in a way that alters the outcome of a case the rule describes, under any of its readings and
for any value of a setting or input, or when it names the rule under `Implements`. Without that name, a defect in
unchanged code that the change only moves or calls does not touch the rule, and the report names it apart.

Code that acts only in a case no rule describes touches no rule: that case is the implementer's choice. A word that
could reach the case, as `expired` reaches a token inside a clock-skew allowance, gives the rule two readings.

Judge each case whose outcome the change alters for any value of a setting or input, and every case of a rule the change
names under `Implements`, by the table against the code as it stands after the change. A touched rule gets `Violates` if
any of its judged cases gets `Violates`, otherwise `Cannot tell` if any gets `Cannot tell`, otherwise `Conforms`. A rule
named under `Defers` that the change also touches gets the verdict of a touched rule, and the report names the deferral
beside it.
````

### Message to the user

I wrote ADR-0001 in `docs/adr/0001-retry-policy-calls-then-refuse-with-503.md`. This is the repository's first record, so I also added a reading guide in `docs/adr/README.md`. The guide explains how to read a record, maps the layers `policyclient` and `handler` to their paths, and describes the `Implements` and `Defers` trailers and how to check a change.

The record stays `Proposed`. Two open points block acceptance:

- **O1:** the meeting said "a few" retries but gave no number, so R2 has the placeholder `<retry count>`.
- **O2:** I assumed that a timeout, a transport error, or an HTTP 5xx response counts as a failed attempt, and that a 4xx response, including 429, does not. Please confirm this or correct it.

Some questions:

1. Who owns the record? Please give me their GitHub account for **Owner**.
2. Which GitHub account or team handle should I list for the platform team under **Participants and approvers**?
3. Should there be a wait between retries, such as a fixed delay or exponential backoff? The record leaves this to the implementer, so it changes the worst-case latency listed under **Consequences**. If the team wants it fixed, I'll add a rule.
4. Which version of the `adr-authoring` skill does the repository pin? I found no `apm.yml` or lock file, so the guide has the placeholder `<skill version>`.
5. The layer map in the guide covers only `internal/policyclient/` and `internal/handler/`. Under the guide's checking steps, a change to any other path is reported as a guide error. Which other paths should the map include?
