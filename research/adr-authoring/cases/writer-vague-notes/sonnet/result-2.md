### File: docs/adr/0001-refuse-request-with-503-when-policy-service-fails-after-retries.md

````markdown
# Refuse a request with 503 and `POLICY_UNAVAILABLE` when every call to the policy service has failed

## Status

Proposed

### Owner

TBD

### Participants and approvers

- Platform team (`<account>`): approves the decision.

## Context

`token-gate` checks the token of each request before policy evaluation. Policy evaluation runs in the policy service,
which `internal/policyclient` calls over HTTP. `internal/handler` turns the errors of `internal/policyclient` into
responses.

A call to the policy service can fail. Before this record, the repository had no written decision on how long a call
waits, whether a failed call is repeated, or what the caller of `token-gate` receives when the policy service stays
unreachable.

## Decision

We will time out each call to the policy service after 5 seconds, retry a failed call a fixed number of times, and refuse
the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every call has failed.

### Terms

- **policy service**: the service that `internal/policyclient` calls over HTTP to evaluate policy.
- **call**: one HTTP request from the policy client to the policy service, from the moment it is sent until its response
  is read or it ends in an error.
- **failed call**: a call that ends in a transport error or reaches the timeout of R1.
- **retry**: a further call to the policy service for the same request, made after a failed call.

### Rules

#### Calls to the policy service

- **R1** (`policy client`). Each call to the policy service times out after 5 seconds.
- **R2** (`policy client`). After a failed call, the policy client makes a retry, up to `<retry count>` retries for one
  request, and uses the response of the first call that does not fail.
- **R3** (`policy client`). When the first call for a request and all of its retries have failed, the policy client
  returns an error to its caller and returns no policy decision.

#### Response to the caller

- **R4** (`handler`). When the policy client returns the error of R3, the handler refuses the request with HTTP status
  503 and the reason code `POLICY_UNAVAILABLE`.

### Justification

The notes of the meeting record the decision and not its reasons, so the reasons below are inferred and need
confirmation (O4).

- A retry lets a request survive a short failure of the policy service (R2). The limit on retries bounds the work done
  for one request (R2, R3).
- The timeout bounds how long one call can hold a request (R1).
- A 503 with its own reason code tells the caller that the policy service could not be reached, and keeps that outcome
  apart from a refusal by policy (R4).

### Alternatives considered

- **A1. Let the request through when every call has failed.** Rejected by R4: the request is refused, so a request
  without a policy decision never passes the token check.
- **A2. Refuse the request after the first failed call.** Rejected by R2: a failed call is retried before the request is
  refused.

## Consequences

Negative:

- A request can wait up to (`<retry count>` + 1) × 5 seconds for the policy service before it is refused (R1, R2).
- While the policy service is unreachable, `token-gate` refuses every request that needs a policy decision (R4).

## Open points

- **O1.** The retry count is not set; the notes say "a few times". The platform team decides. It affects R2 and the
  worst-case wait in Consequences.
- **O2.** The notes say "the call fails" and do not say whether a response with an HTTP error status, such as 5xx or
  429, is a failed call. The answers under consideration are: only transport errors and timeouts (the current definition
  of **failed call**), or also 5xx responses, or also 5xx and 429 responses. The platform team decides. It affects R2,
  R3, and R4.
- **O3.** The notes do not say where the response carries `POLICY_UNAVAILABLE`. The answers under consideration are a
  field in the response body, or a response header. The platform team decides. It affects R4.
- **O4.** The notes give no reasons and no rejected designs. The Justification and A1 and A2 are inferred from the
  decision. The platform team confirms or corrects them. It affects the Justification and the Alternatives.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of `example/token-gate`. Records are numbered in the order
they are added, as `NNNN-title.md`.

## How to read a record

A record states its decision in **Decision** and its requirements as numbered rules under **Rules**. Each rule has a
number such as `R4` and a layer tag such as `(handler)`. Outside its record, cite a rule with the record number, as
`ADR-0001 R4`. **Terms** defines each word that a rule depends on, and a rule uses the word with that definition only.
The reasons for the decision are in **Justification**. **Open points** lists the questions the record does not settle.

The record states a rule once. A requirement stated nowhere in the rules is the implementer's choice.

## Layers

Each layer is named by its role and mapped to the paths of its code.

| Layer | Paths |
| --- | --- |
| `policy client` | `internal/policyclient/` |
| `handler` | `internal/handler/` |

A change that adds code under no mapped path extends this map.

## Trailers

A change to code that a record with numbered rules governs names the rules it brings and the rules it leaves out in two
trailers at the end of its commit message and of its pull request description:

```text
Implements: ADR-0001 R1, R2
Defers: ADR-0001 R4 to #<issue or pull request number>
```

A `Defers` target is an issue or a pull request that exists. A change that brings no rule and leaves none out, such as a
refactoring, carries neither trailer. In a pull request with several commits, each commit carries the trailers of its own
part, and the description carries them for the whole change.

## Which statuses bind a change

Records with the status `Accepted` or `Proposed` bind a change. Records with the status `Superseded` or `Rejected` do
not.

## How to check a change

These steps come from version `<version of the adr-authoring skill>` of the `adr-authoring` skill, as `apm.yml` or the
lock file pins it.

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

I wrote ADR-0001 as `Proposed` and added `docs/adr/README.md`, the reading guide that the first record with numbered rules needs. The guide maps two layers: `policy client` to `internal/policyclient/` and `handler` to `internal/handler/`. I tagged each rule from the repository facts you gave, without reading the code. Please check the tags and the paths.

Questions I need answered:

1. **Owner.** The notes say the owner is not settled, so **Owner** reads `TBD`. Which GitHub account owns the record? I also need the account of the platform team's approver for **Participants and approvers**, which shows `<account>`.
2. **Skill version.** The guide must name the `adr-authoring` version that `apm.yml` or the lock file pins. I had no repository, so it shows `<version of the adr-authoring skill>`. Which version is pinned?
3. **Open points.** Each blocks acceptance, and the status stays `Proposed` until all are closed.
   - **O1:** How many retries? The notes say "a few times", so R2 shows `<retry count>`.
   - **O2:** Is an HTTP error status from the policy service, such as 5xx or 429, a failed call? I assumed only transport errors and timeouts count.
   - **O3:** Where does the response carry `POLICY_UNAVAILABLE`, in the body or in a header?
   - **O4:** The notes give no reasons or rejected designs. I inferred the Justification and the two alternatives (fail open, no retry) from the decision. Please confirm or correct them.

I did not set a delay between retries, since the notes do not mention one. It is the implementer's choice until a rule says otherwise.

No `Date` heading is present, because it is added on acceptance. The change that implements these rules should carry `Implements: ADR-0001 R1, R2, R3, R4` in its commit message and pull request description. It should carry `Defers` only for a rule that waits on an existing issue or pull request. If you want to defer a rule, open an issue for it first and give me the number.
