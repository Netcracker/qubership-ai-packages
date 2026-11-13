### File: docs/adr/0001-retry-failed-policy-calls-and-refuse-with-503.md

````markdown
# Retry failed calls to the policy service, then refuse the request with HTTP 503

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. The policy service runs policy evaluation, and
`internal/policyclient` calls it over HTTP. `internal/handler` turns the errors of `internal/policyclient` into
responses.

No record settles three questions yet: how long one call to the policy service may take, whether token-gate retries a
call that fails, and what the client receives when no call succeeds.

## Decision

We will time out each call to the policy service after 5 seconds and retry a failed call up to `<retry count>` times.
When every call for a request has failed, we will refuse the request with HTTP 503 and the reason code
`POLICY_UNAVAILABLE`.

### Terms

- **policy call**: one HTTP request that `internal/policyclient` sends to the policy service, the first one or a retry.
- **failed policy call**: a policy call that ends in one of these outcomes: a transport error, such as a refused
  connection or a reset; the timeout of R1; or a response with an HTTP status from 500 to 599. A response with any
  other status is not a failed policy call.
- **retry**: a policy call for a request that follows a failed policy call for the same request.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). `internal/policyclient` cancels a policy call that has not received a response 5 seconds
  after it was sent, and the policy call counts as a failed policy call.
- **R2** (`policyclient`). After a failed policy call, `internal/policyclient` sends a retry, up to `<retry count>`
  retries for one request. `internal/policyclient` sends no retry after a policy call that is not a failed policy call.

#### Response when the policy service is unavailable

- **R3** (`policyclient`, `handler`). When the first policy call for a request and all `<retry count>` retries are
  failed policy calls, token-gate responds to the request with HTTP status 503 and the reason code
  `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. Give each policy call its own `context.WithTimeout` of 5 seconds, derived from the request
context, so that one slow call does not shorten the next. The wait between retries is the implementer's choice; a short
backoff with jitter keeps the retries of many requests from reaching the policy service at the same moment. Let
`internal/policyclient` return a sentinel error, such as `ErrPolicyUnavailable`, once the last retry has failed, and
let `internal/handler` match it with `errors.Is` and write the 503 response. An `httptest.Server` that sleeps longer
than 5 seconds, returns 503, or closes the connection covers R1 to R3 in tests.

### Justification

A call that hangs would otherwise hold the request open for as long as the policy service takes; 5 seconds caps the
wait for one policy call (R1). A short outage or a restart of the policy service often fails only one policy call, and
a retry lets the request succeed without the client noticing (R2). A response from the policy service that is not a
failed policy call carries a decision or a client error, and a retry would produce the same response (R2). HTTP 503
tells the client that the failure is temporary and that it can try again later. The reason code separates this case
from a refusal for a bad token (R3). Refusing the request keeps token-gate from letting a request through that policy
evaluation never checked (R3).

### Alternatives considered

- **A1. Let the request through when the policy service cannot be reached.** Rejected by R3: a request would pass
  without policy evaluation for as long as the outage lasts.
- **A2. Respond with HTTP 503 after the first failed policy call, without retries.** Rejected by R2: a single dropped
  connection would refuse a request that a retry would have served.
- **A3. One deadline for the first policy call and all retries together, instead of a timeout for each policy call.**
  A slow first call would leave no time for the retries.

## Consequences

Negative:

- A request can wait up to (`<retry count>` + 1) × 5 seconds, plus the wait between retries, before token-gate
  responds with HTTP 503 (R1, R2, R3).
- During an outage, each request sends up to `<retry count>` + 1 policy calls, which adds load to a policy service that
  is already failing (R2).
- While the policy service is unavailable, token-gate refuses every request that needs policy evaluation (R3).

## Open points

- **O1.** How many retries does `internal/policyclient` send? The meeting settled "a few" and no number. The platform
  team decides. Affects R2 and R3.
- **O2.** Which outcomes count as a failed policy call? The record assumes transport errors, the timeout of R1, and HTTP
  statuses from 500 to 599. Other answers under consideration are adding HTTP 429, or counting only transport errors
  and timeouts. The platform team decides. Affects R2 and R3.
- **O3.** Where does the response carry the reason code `POLICY_UNAVAILABLE`? The record assumes the field that
  carries the reason code in the error body that `internal/handler` already writes for other refusals. The other answer
  under consideration is a response header. The platform team decides. Affects R3.
````

### Message to the user

I drafted ADR-0001 at `docs/adr/0001-retry-failed-policy-calls-and-refuse-with-503.md`. It's the first record in the repository, so it uses the default layout under `docs/adr/`. Its status is `Proposed`, and three open points block acceptance:

- **O1:** the meeting didn't give a retry count, so R2 and R3 use the placeholder `<retry count>`.
- **O2:** the notes don't say which failures count. I assumed transport errors, the 5-second timeout, and HTTP 5xx responses, and wrote the rules on that basis.
- **O3:** I assumed `POLICY_UNAVAILABLE` goes in the field that holds the reason code in the error body `internal/handler` already writes. I couldn't check this without the code.

The meeting notes give no reasons, so I wrote the Justification and the Alternatives considered myself. Please check them with the platform team.

Questions:

1. Who owns this record? Which GitHub account should replace `<owner>`?
2. What GitHub account or team handle should replace `<platform team account>` under Participants and approvers?
3. Do you want a reading guide in `docs/adr/README.md`? With a guide, every change under `internal/policyclient` and `internal/handler` must end its commit message and pull request description with `Implements:` and `Defers:` trailers that name the rules it brings or leaves out. I didn't add one because that commits the team to this process.
