### File: docs/adr/0001-retry-policy-calls-then-refuse-with-503.md

````markdown
# Retry a failed policy call, then refuse the request with 503 and `POLICY_UNAVAILABLE`

## Status

Proposed

### Owner

TBD

### Participants and approvers

- Platform team: approves R1 to R3.

## Context

`token-gate` checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the
policy service. `internal/policyclient` makes that call, and `internal/handler` turns its errors into responses.

## Decision

We will give each policy call a timeout of 5 seconds, retry a failed policy call, and refuse the request with HTTP 503
and the reason code `POLICY_UNAVAILABLE` when the first call and every retry have failed.

### Terms

- **policy call**: one HTTP request that `internal/policyclient` sends to the policy service. A retry is a policy call.
- **failed policy call**: a policy call that times out, or that ends with a connection error before a response arrives.
  O2 asks whether a response with an error status also counts.
- **retry**: a policy call that `internal/policyclient` sends for the same request after a failed policy call.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). Each policy call times out after 5 seconds.
- **R2** (`policyclient`). After a failed policy call, `internal/policyclient` sends a retry, up to `<retry count>`
  retries for one request.

#### Refusal

- **R3** (`handler`). Where the first policy call and every retry for a request have failed, `internal/handler` refuses
  the request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`. O3 asks where the response carries the
  reason code.

### Justification

R1 and R2 bound how long one request waits for the policy service: at most `<retry count>` plus one calls of 5 seconds
each, plus any delay between calls. R3 gives a client one stable status and reason code for this case, so that it can
tell an unavailable policy service from a refusal by policy.

### Consequences

Negative:

- During a policy service outage, every request that reaches policy evaluation waits for R1 and R2 to run out and is
  then refused (R3).
- A request can wait `<retry count>` plus one times 5 seconds, plus any delay between calls, before the client receives
  the 503 (R1, R2).

## Open points

- **O1.** The retry count. The meeting notes say "a few times". The team that owns the record decides the number, which
  R2 and the wait in **Negative** depend on. Two further values are not in the notes: the delay between retries and
  whether it grows. Both are left to the implementer unless the team decides them in a rule.
- **O2.** Which outcomes count as a failed policy call. This record assumes a timeout and a connection error. The
  answers under consideration: add every response with a 5xx status, or add every response that is not a success. The
  platform team decides. It affects R2 and R3.
- **O3.** Where the response carries the reason code `POLICY_UNAVAILABLE`, such as a field of the response body (with
  its name) or a header. The platform team decides. It affects R3.
````

### Message to the user

I wrote one record, `docs/adr/0001-retry-policy-calls-then-refuse-with-503.md`, with the status `Proposed`. The repository has no records, so I used the default directory, filename pattern, and the whole template. I did not add a reading guide or an `AGENTS.md` paragraph.

Questions:

1. **Owner.** The notes say the owner is not settled, so the Owner heading reads `TBD`. Who owns the record? I also listed the platform team as approver without an account name. What is the GitHub account?
2. **Retry count.** "A few times" is not a number, so R2 has the placeholder `<retry count>` and open point O1 asks for the value. Do you also want the delay between retries decided in the record?
3. **What counts as a failed call (O2).** I assumed a timeout or a connection error. Should an HTTP 5xx or other error status from the policy service also count?
4. **Reason code location (O3).** Does `POLICY_UNAVAILABLE` go in a body field (and what is its name) or in a header? R3 cannot be checked without this.
5. **Reasons and alternatives.** The notes give no reasons and no rejected options. The Justification only states what follows from the rules, and I left out **Alternatives considered**. Can you add the reasons the meeting gave and any options it dropped, such as failing open?
6. **Reading guide.** Do you want a `docs/adr/README.md` guide that maps layers to paths, plus an `AGENTS.md` paragraph? This commits the team to ending every commit message and pull request description for code under those paths with `Implements:` and `Defers:` trailers. Until you decide, the layer tags `policyclient` and `handler` follow the package names and may change to match the guide.

The record stays `Proposed` until O1 to O3 are settled and the team signs off. I left out the Date heading, which is added on acceptance. I also left out **Confirmation**, because the notes name no test for any rule.
