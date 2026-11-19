### File: docs/adr/0001-retry-policy-service-calls-then-refuse-with-503.md

````markdown
# Retry a failed policy service call, then refuse the request with HTTP 503

## Status

Proposed

### Owner

TBD (see O2)

### Participants and approvers

- Platform team, `<account>`: approves R1 to R4.

## Context

`token-gate` checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the
policy service. `internal/policyclient` makes that call, and `internal/handler` turns the errors of
`internal/policyclient` into responses.

## Decision

We will retry a failed call to the policy service, give each call a timeout of 5 seconds, and refuse the request with
HTTP 503 and the reason code `POLICY_UNAVAILABLE` when the first call and every retry have failed.

### Terms

- **policy call**: one HTTP request that `internal/policyclient` sends to the policy service.
- **failed policy call**: a policy call that times out under R1, or that ends with a transport error. O1 asks whether a
  response with an HTTP error status also counts.
- **retry**: a policy call made after a failed policy call for the same request. The first policy call is not a retry.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). Each policy call times out after 5 seconds.
- **R2** (`policyclient`). After a failed policy call, `internal/policyclient` makes a retry, up to `<retry count>`
  retries for one request. O3 asks for the value.
- **R3** (`policyclient`). When the first policy call and every retry of a request have failed, `internal/policyclient`
  returns an error to its caller.

#### Response to the client

- **R4** (`handler`). When `internal/policyclient` returns the error of R3, `internal/handler` refuses the request with
  HTTP status 503 and the reason code `POLICY_UNAVAILABLE`. O4 asks where the reason code appears.

## Consequences

Negative:

- A request can wait for the first policy call and every retry before the client gets the refusal. With the 5 second
  timeout of R1, the wait is at least `(<retry count> + 1) * 5` seconds in the worst case, plus any delay between calls.
- While the policy service is unavailable, a request is refused (R4), so the policy service is a hard dependency of
  every request.

## Open points

- **O1.** Does a policy service response with an HTTP error status, such as 500, count as a failed policy call? The
  platform team decides. It affects R2, R3, and R4. Until it answers, only a timeout or a transport error counts.
- **O2.** Who owns this record? The platform team approves it, but the meeting did not name an owner account.
- **O3.** What is the retry count? The meeting said "a few times". The platform team decides. It affects R2 and the
  waiting time under **Consequences**.
- **O4.** Where does the client see `POLICY_UNAVAILABLE`: in the response body, in a header, or in both? The platform
  team decides. It affects R4.
````

### Message to the user

I wrote the record as `Proposed`. It can't be `Accepted` while four open points remain.

Questions for you:

1. **Owner (O2):** Which GitHub account owns the record? The Owner field says `TBD` until you tell me.
2. **Approver account:** What is the platform team's GitHub account? I left `<account>` in **Participants and approvers**.
3. **Retry count (O3):** "A few times" is not a number, so R2 has the placeholder `<retry count>`. I didn't invent a value.
4. **Failed call (O1):** Does an HTTP error status from the policy service, such as 500, count as a failed call? I defined a failure as a timeout or a transport error only.
5. **Reason code (O4):** Where does the client see `POLICY_UNAVAILABLE`: in the body, in a header, or in both?
6. **Reading guide:** The repository has no `README.md` that describes records. I did not add a guide. A guide commits the team to ending every commit message and pull request description for code under the mapped paths with `Implements:` and `Defers:` trailers. It also needs a short paragraph in the agent instructions. Do you want me to add it? Until then, the rule tags `policyclient` and `handler` are my names for `internal/policyclient` and `internal/handler`.

I left out **Confirmation**, **Justification**, and **Alternatives considered**. The meeting notes name no check, no reasons, and no rejected options, and I didn't make any up. If you remember a test that covers these rules or an option the meeting rejected, send it and I'll add it.
