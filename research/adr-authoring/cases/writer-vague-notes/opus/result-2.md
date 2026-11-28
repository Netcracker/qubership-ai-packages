### File: docs/adr/0001-policy-service-retries.md

````markdown
# Retry failed calls to the policy service, and refuse the request with HTTP 503 when every attempt fails

## Status

Proposed

### Owner

`<GitHub account>`

### Participants and approvers

- Platform team, `<GitHub team or account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/policyclient` calls the policy service
over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses.

A call to the policy service can end in a connection error, a response that does not arrive, or a server error. When
that happens, token-gate has no policy decision for the request. A short outage of the policy service, such as a
restart, ends within seconds.

## Decision

We will retry a failed call to the policy service a fixed number of times, and limit each attempt to 5 seconds. When
every attempt fails, we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **policy call**: the work `internal/policyclient` does to get the policy decision for one incoming request. A policy
  call is made of one or more attempts.
- **attempt**: one HTTP request from `internal/policyclient` to the policy service. It starts when the request starts
  and ends when the response body has been read or the request has failed.
- **failed attempt**: an attempt that ends in a connection error, in the cancellation of R2, or in a response with an
  HTTP status from 500 to 599. A response with any other status, a policy decision that denies the request included,
  is not a failed attempt.

### Rules

#### Attempts

- **R1** (`policyclient`). After a failed attempt, `internal/policyclient` starts a new attempt for the same policy
  call, up to `<retry count>` attempts after the first one. An attempt that is not a failed attempt ends the policy
  call with its response, and `internal/policyclient` starts no further attempt for that policy call.
- **R2** (`policyclient`). `internal/policyclient` cancels an attempt that has not ended 5 seconds after it started.

#### Refusal

- **R3** (`policyclient`, `handler`). When every attempt that R1 allows for a policy call is a failed attempt,
  token-gate refuses the incoming request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`, and does not
  evaluate policy for it. `internal/handler` writes `POLICY_UNAVAILABLE` in the same place as the reason code of every
  other refusal.

### Implementation notes

Adds no requirement. Set `http.Client.Timeout` to 5 seconds, or give each attempt its own `context.WithTimeout`,
because both cover the whole attempt, including the read of the response body. Create the context of each attempt
from the context of the incoming request. When the last attempt fails, return an error that wraps an exported
sentinel, such as `policyclient.ErrUnavailable`, and let `internal/handler` match it with `errors.Is`.

### Justification

A short outage of the policy service should not refuse every request that arrives during it, so a failed attempt is
retried (R1). An attempt that ends with a response, a deny decision included, gives token-gate a result, and repeating
it would not change the result (R1). The per-attempt limit puts an upper bound on how long a request waits for one
attempt to the policy service (R2). Without a policy decision, token-gate refuses the request instead of letting it
through (R3). Status 503 marks the refusal as temporary, which a 401 or a 403 would not. The reason code lets a client
and an operator tell a policy outage apart from a refused token (R3).

### Alternatives considered

- **A1. Let the request through when the policy service is unavailable (fail open).** Rejected by R3: a request
  would pass without policy evaluation for as long as the outage lasts.
- **A2. Refuse the request after the first failed attempt.** Rejected by R1: a restart of the policy service would
  refuse every request that arrives during it.
- **A3. Refuse the request with HTTP 500.** Rejected by R3: 500 reports a fault in token-gate itself, and a client
  does not know that it can try the request again.

## Consequences

Positive:

- A client or a load balancer that retries on 503 retries a request that was refused during a policy outage.

Negative:

- When the policy service accepts connections and does not answer, a request waits up to (1 + `<retry count>`) × 5
  seconds before token-gate refuses it (R1, R2).
- During an outage, the policy service receives up to 1 + `<retry count>` attempts for each incoming request (R1).

## Open points

- **O1.** How many attempts follow the first failed attempt, the `<retry count>` of R1. The notes say "a few". The
  platform team decides. Affects R1.
- **O2.** Whether `internal/policyclient` waits between attempts. The answers under consideration: no wait, which leaves
  the choice to the code; a fixed delay; or exponential backoff with jitter. The platform team decides. A wait would
  become a rule of its own and would lengthen the worst case under **Negative**. Affects R1.
- **O3.** This record assumes that a failed attempt covers connection errors, the cancellation of R2, and statuses from
  500 to 599, and that it does not cover 429 or any other 4xx status. The other answer under consideration counts 429 as
  a failed attempt too. The platform team decides. Affects R1 and R3.
````

### Message to the user

I've written the record as `docs/adr/0001-policy-service-retries.md`. Its status is `Proposed`, because three open points still block acceptance:

- **O1:** How many retries does the platform team want? The notes only say "a few", so R1 uses the placeholder `<retry count>`.
- **O2:** Should `internal/policyclient` wait between attempts? The options are no wait, a fixed delay, or exponential backoff with jitter.
- **O3:** I assumed that a failed attempt means a connection error, the 5-second timeout, or a 5xx response, and that 4xx responses are not retried. Should 429 be retried too?

I also have some questions that don't belong in the record:

1. **Owner:** Who owns this record? Please give me their GitHub account for the `<GitHub account>` placeholder.
2. **Approver:** What is the platform team's GitHub team or account? It goes in the `<GitHub team or account>` placeholder.
3. **Reading guide:** The repository has no guide for its records. Should I add one in `docs/adr/README.md`, plus a paragraph in the agent instructions? The guide would map `policyclient` and `handler` to their paths. It would also commit the team to ending the commit message and pull request description of every change to that code with `Implements:` and `Defers:` trailers that name the rules. Without a guide, the rules still apply once the record is accepted, but no change needs the trailers.

When the open points are settled and the team signs off, the status changes to `Accepted` and a Date heading is added.
