### File: docs/adr/0001-retry-policy-calls-then-refuse-with-503.md

````markdown
# Retry a failed call to the policy service, then refuse the request with HTTP 503

## Status

Proposed

### Owner

Not assigned yet.

### Participants and approvers

- Platform team: approves the decision.

## Context

token-gate checks the token of each request before policy evaluation. `internal/policyclient` calls the policy service
over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses.

A call to the policy service can fail. The connection can fail, the policy service can respond slowly or not at all, and
it can return a server error. Many of these failures are transient, so a later call to the policy service often
succeeds.

A request that token-gate cannot evaluate against policy has no policy decision. Forwarding such a request would let it
skip policy evaluation.

## Decision

We will retry a failed call to the policy service a fixed number of times, with a timeout of 5 seconds on each call.
When every call for a request has failed, we will refuse the request with HTTP 503 and the reason code
`POLICY_UNAVAILABLE`.

### Terms

- **policy request**: all the calls that `internal/policyclient` makes to the policy service to evaluate one incoming
  request.
- **attempt**: one HTTP call that `internal/policyclient` makes to the policy service as part of a policy request.
- **failed attempt**: an attempt that ends in a transport error (such as a refused connection, a reset connection, or a
  failed DNS lookup), that reaches the timeout of R1, or that receives a response with an HTTP status from 500 to 599.
- **policy unavailable**: the outcome of a policy request in which every attempt is a failed attempt.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). An attempt that has not received a complete response 5 seconds after it starts is cancelled,
  and it is a failed attempt.
- **R2** (`policyclient`). After a failed attempt, the policy client makes another attempt, up to `<retry count>`
  attempts after the first, so a policy request makes at most 1 + `<retry count>` attempts. The policy client makes no
  further attempt after an attempt that is not a failed attempt, and it returns the outcome of that attempt.
- **R3** (`policyclient`). When a policy request ends as policy unavailable, the policy client returns an error that
  identifies the outcome as policy unavailable and that differs from every other error the policy client returns.

#### Response to the caller

- **R4** (`handler`). When the policy client returns the policy unavailable error of R3, the handler refuses the
  incoming request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`, and token-gate does not forward the incoming
  request.

### Justification

Most failures of the policy service are transient, so another attempt often gets a policy decision where the first
attempt did not (R2). The timeout on each attempt bounds how long a slow policy service holds an incoming request, and it
turns a hung call into a failed attempt that R2 can retry (R1).

Refusing a request that has no policy decision keeps every forwarded request subject to policy evaluation (R4). HTTP 503
tells the caller that the failure is on the server side and may pass, and the reason code tells the caller and the
operator that the policy service caused it, as opposed to the token (R3, R4).

### Alternatives considered

- **A1. Forward the incoming request when the policy service is unavailable (fail open).** Rejected by R4: a forwarded
  request would skip policy evaluation.
- **A2. Refuse the incoming request after the first failed attempt.** Rejected by R2: a transient failure of the policy
  service would refuse requests that a second attempt would have evaluated.
- **A3. Give an attempt no timeout of its own, and let the deadline of the incoming request bound it.** Rejected by R1:
  one hung attempt would use the whole deadline and leave no time for another attempt.
- **A4. Return HTTP 500 or HTTP 502 when the policy service is unavailable.** Rejected by R4: the caller and the
  operator could not tell this outcome from other server errors.

## Consequences

Negative:

- A policy request that ends as policy unavailable takes up to (1 + `<retry count>`) × 5 seconds, plus any delay between
  attempts, before token-gate refuses the incoming request (R1, R2).
- While the policy service is down, token-gate refuses every incoming request that needs a policy decision, including
  requests with a valid token (R4).
- Each retry adds a call to the policy service while it is failing, which adds load to it (R2).

## Open points

- **O1.** How many retries follow the first attempt. The meeting agreed on "a few" and named no number. The platform
  team decides. Affects R2.
- **O2.** Which outcomes are failed attempts. The record assumes transport errors, the timeout of R1, and HTTP statuses
  from 500 to 599. The other answer under consideration adds HTTP 429. The platform team decides. Affects R2, R3, and
  the term **failed attempt**.
- **O3.** Where the response of R4 carries the reason code `POLICY_UNAVAILABLE`. The answers under consideration are a
  field in a JSON response body and a response header. The platform team decides. Affects R4.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. Each record states one decision, the
reasons for it, and numbered rules that code can be checked against.

## How to read a record

- **Rules** state the requirements. Each rule has a number, such as R2, and a layer tag that names where its check runs.
  Outside its record, a rule is cited with its record, as `ADR-0001 R2`.
- **Terms** define the words that the rules depend on. A word in a rule has the extent its definition gives.
- **Justification**, **Alternatives considered**, and **Consequences** give the reasons and the accepted costs. They
  add no requirement.
- **Open points** list questions the record does not settle yet. A record stays `Proposed` until the list is empty.

Anything that no rule states is the implementer's choice.

## Status

`Accepted` and `Proposed` records bind a change. `Superseded` and `Rejected` records do not. A rule that a later
record names as replaced under **Related ADRs** binds nothing once that later record is accepted.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `policyclient` | Calls the policy service over HTTP. | `internal/policyclient/` |
| `handler` | Turns the errors of the policy client into responses. | `internal/handler/` |

A change that adds code under no path in this table extends the table.

## Trailers

A change to code that a record governs names the rules it brings and the rules it leaves out. Two trailers at the end
of its commit message and of its pull request description do this:

```text
Implements: ADR-0001 R1, R2
Defers: ADR-0001 R4 to #123
```

`Implements` claims every case of a rule. A change that brings only some cases of a rule names it under `Defers`, with
the issue or pull request that brings the rest. A `Defers` target is an issue or a pull request that exists. A change
that brings no rule and leaves none out carries neither trailer.

## How to check a change

The steps, the table, and the three paragraphs after the table come from the `adr-authoring` skill, version
`<skill version>`.

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

I wrote ADR-0001 in `docs/adr/0001-retry-policy-calls-then-refuse-with-503.md` with the status `Proposed`. Because this is the repository's first record with numbered rules, I also added a reading guide in `docs/adr/README.md`. The guide maps the layer `policyclient` to `internal/policyclient/` and the layer `handler` to `internal/handler/`.

The record can't be accepted until three open points are settled:

- **O1:** How many retries should follow the first attempt? The meeting said "a few", so R2 has the placeholder `<retry count>`.
- **O2:** Which outcomes count as a failed attempt? I assumed transport errors, the 5-second timeout, and HTTP 500–599. Should HTTP 429 count too?
- **O3:** Where should the 503 response carry `POLICY_UNAVAILABLE`: in a JSON body field or in a response header?

I also have these questions:

- Who owns the record? The Owner field says "Not assigned yet". Please give me the GitHub account to put there.
- Which GitHub account or team handle should stand for the platform team under "Participants and approvers"?
- Which version of the `adr-authoring` skill does the repository pin? The README has the placeholder `<skill version>` because I had no `apm.yml` or lock file to read it from.

The meeting didn't set a delay between retries, so the record leaves it to the implementer. If the platform team wants a backoff policy, it needs a rule of its own.
