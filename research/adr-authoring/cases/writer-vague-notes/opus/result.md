### File: docs/adr/0001-retry-policy-calls-then-refuse-with-503.md

````markdown
# Retry a failed policy call a fixed number of times, then refuse the request with HTTP 503

## Status

Proposed

### Owner

Not settled yet.

### Participants and approvers

- Platform team: approves R1 to R3.

## Context

token-gate is a Go service that checks the token of each request before policy evaluation. `internal/policyclient`
calls the policy service over HTTP. `internal/handler` turns the errors that `internal/policyclient` returns into
responses.

No rule in the repository sets how long one call to the policy service may take, whether token-gate repeats a call that
failed, or what the caller gets when the policy service gives no usable answer. This record sets all three. It is the
first decision record in the repository.

## Decision

We will give each call to the policy service a timeout of 5 seconds and retry a failed call up to a fixed number of
times. When every call for a request has failed, token-gate refuses the request with HTTP 503 and the reason code
`POLICY_UNAVAILABLE`.

### Terms

- **policy call**: one HTTP request that token-gate sends to the policy service to evaluate policy for one incoming
  request. The first call and every retry are each one policy call.
- **failed policy call**: a policy call that ends in a transport error, such as a refused connection or a reset, that
  reaches the timeout of R1, or that receives a response with a 5xx status. A policy call that receives any other
  response, including a 4xx status, is not a failed policy call.
- **retry**: a policy call that token-gate sends again for the same incoming request after a failed policy call.

### Rules

#### Timeout

- **R1** (`policyclient`). `policyclient` ends each policy call that has not received a complete response within
  5 seconds of the moment the call started. The limit applies to each policy call on its own, the first call and every
  retry alike.

#### Retries

- **R2** (`policyclient`). After a failed policy call, `policyclient` sends a retry, up to `<retry count>` retries for
  one incoming request. `policyclient` sends no retry after a policy call that is not a failed policy call.

#### Refusal

- **R3** (`policyclient`, `handler`). When the first policy call for an incoming request and all `<retry count>`
  retries are failed policy calls, token-gate refuses the incoming request with HTTP status 503 and the reason code
  `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. In `internal/policyclient`, derive a new `context.Context` with `context.WithTimeout(ctx,
5*time.Second)` for each policy call, so that a retry gets its own 5 seconds (R1). Return a sentinel error, such as
`policyclient.ErrUnavailable`, once the retries for a request are used up, and let `internal/handler` map it with
`errors.Is` to the 503 response (R3). The delay between retries is the implementer's choice; a short exponential
backoff with jitter keeps the retries of many requests from reaching the policy service at the same moment.

A table test in `internal/policyclient` with a fake policy service can cover each kind of failed policy call, a 4xx
response, and a call that never answers. A test in `internal/handler` can check the status and the reason code of R3.

### Justification

A single dropped connection or a restart of one instance of the policy service would otherwise refuse requests that a
second call would have served (R2). A limit per policy call keeps one call that never answers from holding the request
until the client gives up (R1). A 4xx response describes the request rather than the state of the policy service, so a
retry would get the same answer (R2). HTTP 503 tells the caller that the refusal is temporary and that the request
itself may be valid. The reason code `POLICY_UNAVAILABLE` lets the caller and the logs tell an outage of the policy
service from a refusal by policy (R3).

### Alternatives considered

- **A1. Refuse the request at the first failed policy call.** Rejected by R2: a short outage of the policy service
  would refuse every request that reaches token-gate during it.
- **A2. Let the request through when the policy service does not answer (fail open).** Rejected by R3: a request would
  pass with no policy evaluation.

## Consequences

Negative:

- An incoming request can wait up to `1 + <retry count>` times 5 seconds, plus the delays between retries, before
  token-gate refuses it under R3. A client whose own timeout is shorter gives up before it receives the 503 response.
- While the policy service is down, each incoming request sends up to `1 + <retry count>` policy calls to it (R2),
  which adds load to a service that is already failing.

Follow-ups:

- Tell the clients of token-gate about the 503 response and the reason code `POLICY_UNAVAILABLE` (R3).

## Open points

- **O1.** How many retries does `policyclient` send for one incoming request? The meeting settled on "a few" and no
  number. The platform team decides. Affects R2, R3, and the wait named under **Negative**.
- **O2.** Which results count as a failed policy call? The record assumes a transport error, the timeout of R1, and a
  5xx status. Other answers are to add HTTP 429, or to leave out 5xx statuses and retry only transport errors and
  timeouts. The platform team decides. Affects R2 and R3 through the term **failed policy call**.
- **O3.** Where does the response of R3 carry the reason code? The record assumes that token-gate already puts a reason
  code in its refusals and that `POLICY_UNAVAILABLE` goes in the same place. If no such place exists, the record has to
  name one, such as a field of the JSON body or a response header. The owner of this record decides with the platform
  team. Affects R3.
````

### Message to the user

I wrote the record as `docs/adr/0001-retry-policy-calls-then-refuse-with-503.md`. Its status is `Proposed`, because three open points block acceptance:

- **O1:** how many retries. The notes only say "a few", so R2 and R3 use the placeholder `<retry count>`.
- **O2:** which results count as a failed call. I assumed transport errors, the 5-second timeout, and 5xx responses, so a 4xx is never retried.
- **O3:** where the 503 response carries `POLICY_UNAVAILABLE`. I assumed token-gate already has a place for a reason code in its refusals.

Questions:

1. Who owns this record? Please give their GitHub account for the Owner field.
2. What is the platform team's GitHub team handle for the approvers line?
3. What are your answers to O1, O2, and O3?
4. The meeting notes give no reasons and no alternatives. Can you confirm the reasons I wrote under Justification? Did the meeting actually consider A1 (refuse at the first failure) and A2 (fail open)?
5. Should the record fix the delay between retries? It leaves that to the implementer for now.

The repository has no reading guide, so no change owes the `Implements` and `Defers` trailers. Changes are checked only against `Accepted` records, and only for the rules a change touches. Would you like me to add a guide in `docs/adr/README.md`? If you do, every change to code under the mapped paths, such as `internal/policyclient` and `internal/handler`, has to end its commit message and pull request description with those trailers.
