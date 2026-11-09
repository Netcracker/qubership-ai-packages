### File: docs/adr/0001-refuse-with-503-when-policy-service-calls-fail.md

````markdown
# We will retry a failed policy service call and refuse the request with HTTP 503 when every retry has failed

## Status

Proposed

### Owner

<owner GitHub account, not settled yet>

### Participants and approvers

- Platform team (`<platform team GitHub account>`): approves the decision.

## Context

`token-gate` checks the token of each request before policy evaluation. Policy evaluation runs in the policy service,
which `internal/policyclient` calls over HTTP. `internal/handler` turns the errors of `internal/policyclient` into
responses.

A call to the policy service can fail. The team decided how long one call may take, how often a failed call is tried
again, and what a caller receives when the policy service stays unavailable.

## Decision

We will bound each call to the policy service with a timeout of 5 seconds and retry a failed call a limited number of
times. When every retry has failed, we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **call**: one HTTP request from `internal/policyclient` to the policy service, from the moment it is sent until its
  response arrives, the call times out, or the connection fails.
- **failed call**: a call that times out or ends in a connection error. An HTTP response of any status is not a failed
  call (see O2).
- **retry**: a call made for the same request after a failed call of that request.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). Each call times out after 5 seconds, and the policy client counts a call with no response by
  then as a failed call.
- **R2** (`policyclient`). After a failed call, the policy client makes a retry, up to `<retry count>` retries for one
  request.
- **R3** (`policyclient`). When the first call for a request and all of its retries have failed, the policy client makes
  no further call for that request and returns an error to its caller.

#### Response to the caller

- **R4** (`handler`). When the policy client returns the error of R3 for a request, the handler refuses that request
  with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Justification

The timeout and the retry limit bound how long a request waits for the policy service (R1, R2, R3). A retry gives a
brief failure of the policy service a chance to pass before a caller sees an error (R2). A refusal with a fixed status
and reason code tells a caller that the policy service was unavailable (R4). The request is refused, not passed on
without policy evaluation (R4).

### Alternatives considered

- **A1. Give up after the first failed call.** Rejected by R2: a brief failure of the policy service would refuse
  requests that a retry would have served.
- **A2. Retry a failed call without a limit.** Rejected by R3: a request would wait for as long as the policy service is
  unavailable.
- **A3. Let the request through when the policy service is unavailable.** Rejected by R4: a request that no policy
  evaluation has judged is refused.

## Consequences

Negative:

- A request can wait up to (`<retry count>` + 1) × 5 seconds before the handler refuses it (R1, R2, R3).
- While the policy service is unavailable, the handler refuses every request that needs policy evaluation (R4).

Follow-ups:

- Settle the owner of this record and fill in **Owner**.
- Add the reading guide `docs/adr/README.md`, which this change introduces.

## Open points

- **O1.** The number of retries is not decided. The platform team decides it. It affects R2 and the worst-case wait in
  **Consequences**.
- **O2.** The notes say "the call fails" without naming the cases. This record assumes that a failed call is a timeout
  or a connection error, and that a response with any HTTP status ends the call without a retry. Another answer is that
  a response with a 5xx status is also a failed call. The platform team decides it. It affects R2, R3, and the term
  **failed call**.
- **O3.** The place that carries the reason code `POLICY_UNAVAILABLE` in the response is not decided: a field of the
  response body or a header. The platform team decides it. It affects R4.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of `example/token-gate`. Records are numbered
`NNNN-title.md`. A record states its requirements as numbered rules, such as `ADR-0001 R4`.

## Reading a record

A record has a status, a context, a decision, terms, numbered rules, a justification, alternatives, consequences, and
open points. Only the rules, together with the terms they use, state requirements. The justification and the
alternatives explain a rule and add none. Anything no rule states is the implementer's choice.

A rule names a layer in backticks, such as `policyclient`. The layer is the part of the system where the check runs.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `policyclient` | Calls the policy service over HTTP | `internal/policyclient/` |
| `handler` | Turns errors of the policy client into responses | `internal/handler/` |

A change that adds code under no mapped path extends this table.

## Statuses

`Accepted` and `Proposed` records bind a change. `Superseded` and `Rejected` records do not.

## Trailers

A change to code that a record with numbered rules governs declares delivery in two trailers at the end of its commit
message and of its pull request description:

```text
Implements: ADR-0001 R1, R2
Defers: ADR-0001 R4 to #<issue or pull request number>
```

`Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with the issue or pull
request that will bring it. A `Defers` target is an issue or a pull request that exists. A change that brings no rule
and leaves none out carries neither trailer.

## Checking a change

This section comes from the `adr-authoring` skill, version `<version, as pinned in apm.yml or the lock file>`.

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

I wrote ADR-0001 as `Proposed`, plus `docs/adr/README.md`. The repository had no records, so the README is the reading guide that the first record with numbered rules needs. You didn't ask for it, and I added it for that reason.

Questions and gaps:

1. **Owner.** Who owns the record? The `Owner` field holds a placeholder. I also need the GitHub account or team name of the platform team for **Participants and approvers**.
2. **Retry count (O1).** The notes say "a few". I did not invent a number, so R2 reads `<retry count>`. How many retries do you want?
3. **What counts as a failed call (O2).** I assumed that a timeout or a connection error is a failure and that any HTTP response ends the call. Should a 5xx response be retried too?
4. **Reason code placement (O3).** Is `POLICY_UNAVAILABLE` a field in the response body or a header?
5. **Skill version.** The README names the `adr-authoring` skill version as a placeholder, because the repository has no `apm.yml` or lock file. Please give me the version.
6. **Alternatives A1 to A3 and the Justification.** I inferred them from the rules, and the meeting did not discuss them. Please check them. The same goes for the worst-case wait in **Consequences**, which is (`<retry count>` + 1) × 5 seconds.
7. **Delay between retries.** The notes don't mention one, so I left it to the implementer.

The record stays `Proposed` until O1 to O3 are settled and the owner is named. When code for it lands, the pull request needs `Implements:` and `Defers:` trailers. A `Defers` target must be a real issue, so please open one for any rule you leave to a later change.
