### File: docs/adr/0001-refuse-requests-with-503-when-the-policy-service-is-unavailable.md

````markdown
# Retry failed policy service calls, then refuse the request with HTTP 503 and `POLICY_UNAVAILABLE`

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R4.

## Context

token-gate checks the token of each request, then evaluates policy by calling the policy service over HTTP.
`internal/policyclient` makes that call, and `internal/handler` turns its errors into responses. The meeting that
produced this record agreed how a failing call is handled: it is retried, each attempt has a time limit, and a request
whose attempts all fail is refused.

## Decision

We will retry a failed call to the policy service up to `<retry count>` times, give each attempt 5 seconds, and refuse
the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every attempt has failed.

### Terms

- **attempt**: one HTTP call from `internal/policyclient` to the policy service for one request. The first call and
  each retry are each one attempt.
- **failed attempt**: an attempt that ends with a timeout, a connection error, or an HTTP 5xx response. An attempt that
  returns a policy decision, including a decision that denies the request, is not failed. O2 asks whether this extent is
  right.
- **retry**: an attempt made after a failed attempt for the same request.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). An attempt that has not received a complete response within 5 seconds is a failed attempt, and
  `policyclient` abandons it.
- **R2** (`policyclient`). After a failed attempt, `policyclient` makes a retry for the same request, up to `<retry
  count>` retries. It makes no further attempt for that request once an attempt has not failed.
- **R3** (`policyclient`). When the first attempt and every retry for a request have failed, `policyclient` returns an
  error to its caller.

#### Refusal

- **R4** (`handler`). When `policyclient` returns the error of R3 for a request, `handler` refuses the request with HTTP
  status 503 and the reason code `POLICY_UNAVAILABLE`.

### Justification

Retries let a request survive a short failure of the policy service (R2). The 5-second limit bounds the time a request
waits on one attempt (R1). A request that cannot get a policy decision is refused, so no request passes without policy
evaluation (R3, R4). Status 503 tells the caller that the service is temporarily unable to handle the request, and the
reason code `POLICY_UNAVAILABLE` names the cause (R4).

## Consequences

Negative:

- While the policy service is down, token-gate refuses every request that reaches policy evaluation (R4).
- A request can wait up to 5 seconds for each attempt before it is refused, so up to `<retry count>` + 1 attempts, plus
  any pause between retries (R1, R2).

## Open points

- **O1.** The number of retries is not decided: the notes say "a few times". The platform team decides. It sets
  `<retry count>` in R2 and the worst-case wait in Consequences.
- **O2.** The extent of a failed attempt is assumed, not decided. The assumption is a timeout, a connection error, or an
  HTTP 5xx response, with a policy denial excluded. The platform team decides whether HTTP 4xx responses count. It
  affects R1, R2, R3, and the term **failed attempt**.
- **O3.** The notes do not say whether retries wait between attempts, or for how long. The platform team decides. It
  affects R2.
````

### Message to the user

I wrote the record as `Proposed`. It stays that way until the open points are settled and the team signs off.

Questions:

1. **Owner.** Who owns the record? The meeting left this open. The Owner field holds `<owner GitHub account>`. The platform team's account is also a placeholder under **Participants and approvers**.
2. **Retry count (O1).** The notes say "a few times". I did not invent a number, so R2 holds `<retry count>`.
3. **What counts as a failed attempt (O2).** I assumed a timeout, a connection error, or an HTTP 5xx response. I assumed a policy denial is not a failure. Please confirm, and say whether 4xx responses count.
4. **Pause between retries (O3).** Is there a delay or backoff? The notes don't say, so no rule states one.
5. **Reading guide.** The repository has no records or guide yet. A `README.md` guide would commit every change to code under the mapped paths to end its commit message and PR description with `Implements:` and `Defers:` trailers. It would also need a short paragraph in `AGENTS.md`. Do you want that guide? I did not add one. Without it, the layer tags `policyclient` and `handler` in the rules name the packages `internal/policyclient` and `internal/handler`.

Other notes:

- I left out **Confirmation** because no test exists yet. R1 to R4 each need one, in `policyclient` and `handler`.
- I left out **Alternatives considered** because the notes record none. If the meeting rejected another design, such as admitting the request when policy is unreachable, tell me and I will add it with the rule that rejects it.
- The **Justification** is my reading of the decision. The notes give no reasons, so please check it.
- The notes don't say where the reason code appears in the 503 response, such as a body field or a header. R4 only requires that the response carries it. Say if you want the location fixed.
