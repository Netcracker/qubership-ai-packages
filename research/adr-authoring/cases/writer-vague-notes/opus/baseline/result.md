### File: docs/adr/0001-retry-policy-service-calls.md
````markdown
# 1. Retry failed calls to the policy service, then refuse with 503

- Status: Accepted
- Date: November 9, 2026
- Deciders: platform team
- Owner: TBD

## Context

token-gate checks the token of each request before policy evaluation. To evaluate policy, it calls the policy service
over HTTP through `internal/policyclient`. `internal/handler` turns the errors from `internal/policyclient` into HTTP
responses.

A call to the policy service can fail. Before this decision, no rule defined how long token-gate waits for a call, how
often it tries again, or which response the client receives when the policy service can't be reached.

## Decision

Each call to the policy service times out after 5 seconds. The timeout applies to each attempt, so a retry gets a new
5-second limit.

When a call fails, `internal/policyclient` retries it. The number of retries is TBD. The delay between attempts and the
set of failures that count as retryable are also TBD.

When every retry has failed, `internal/policyclient` returns an error that `internal/handler` maps to HTTP 503 with the
reason code `POLICY_UNAVAILABLE`.

## Consequences

- A request can wait longer than 5 seconds for its response. The upper bound is the number of attempts times 5 seconds,
  plus any delay between attempts.
- A short failure of the policy service doesn't refuse a request, as long as one retry succeeds.
- Each retry adds a call to the policy service. While the service is failing, token-gate sends it more calls than it
  receives requests.
- A client can tell an unreachable policy service from a refused token by the 503 status and the reason code
  `POLICY_UNAVAILABLE`.
- The retry count, the delay between attempts, and the set of retryable failures need to be settled before the
  implementation is complete. This record is updated when they are.
````

### Message to the user
I wrote the record as `docs/adr/0001-retry-policy-service-calls.md`. The repository has no records yet, so this file also sets the location and naming scheme: `docs/adr/`, a four-digit number, and a short title. The fields are Status, Date, Deciders, and Owner.

The meeting notes left some things open. I marked them TBD in the record rather than guess at them:

1. **Owner:** Who owns this record?
2. **Retry count:** The notes say "a few". What is the number?
3. **Delay between attempts:** Is it fixed, exponential backoff, or exponential backoff with jitter?
4. **Retryable failures:** Which failures are retried? For example, timeouts and connection errors only, or HTTP 5xx from the policy service as well? Is a 4xx ever retried?
5. **Overall deadline:** Is there a limit on the total time across all attempts, or only the 5 seconds per attempt?
6. **`Retry-After`:** Should the 503 response set a `Retry-After` header?
7. **Response field:** Which field of the response body carries `POLICY_UNAVAILABLE`?

I made three assumptions that you should check:

- **Where the logic lives:** I put the retries in `internal/policyclient` and the mapping to 503 in `internal/handler`. The notes don't say which package retries.
- **Timeout scope:** I read the 5-second timeout as applying to each attempt.
- **Date:** I used today's date, November 9, 2026. If the record should carry the date of the meeting, I need that date.
