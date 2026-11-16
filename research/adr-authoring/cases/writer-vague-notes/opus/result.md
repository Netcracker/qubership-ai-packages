### File: docs/adr/0001-retry-failed-policy-service-calls.md

````markdown
# Retry failed calls to the policy service, and refuse the request with 503 when every attempt fails

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/policyclient` calls the policy service
over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses.

A call to the policy service can fail. The service can be slow, the connection can be refused, or the service can
return a server error. Without a decision, a single failed call decides the outcome of the request. In addition, the
time a request waits for the policy service has no agreed limit, and callers of token-gate have no agreed response that
tells them the policy service was unavailable.

## Decision

We will retry a failed call to the policy service a fixed number of times, each attempt limited to 5 seconds. When every
attempt fails, token-gate refuses the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **attempt**: one HTTP request that `internal/policyclient` sends to the policy service for one policy evaluation.
- **failed attempt**: an attempt that times out under R1, that ends with a transport error such as a refused connection
  or a reset connection, or that receives an HTTP status from 500 to 599. An attempt that receives any other status is
  not a failed attempt, also where the policy service denies the request.
- **retry**: an attempt after the first one for the same policy evaluation.

### Rules

#### Attempts

- **R1** (`policyclient`). An attempt times out when `internal/policyclient` has not received its complete response 5
  seconds after the attempt started, and `internal/policyclient` then abandons the attempt. Each attempt has its own 5
  seconds, counted from its own start.
- **R2** (`policyclient`). After a failed attempt, `internal/policyclient` sends a retry for the same policy evaluation,
  up to `<retry count>` retries for that evaluation. `internal/policyclient` sends no retry after an attempt that is not
  a failed attempt.

#### Response when every attempt fails

- **R3** (`policyclient`, `handler`). When the first attempt and all `<retry count>` retries for a policy evaluation are
  failed attempts, token-gate refuses the request that needed the evaluation with HTTP status 503 and the reason code
  `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. Give each attempt its own context with a 5-second timeout, derived from the context of the incoming
request, so that a client that disconnects also stops the retries. Let `internal/policyclient` return one error value
that tells `internal/handler` that every attempt failed, such as a sentinel error that `errors.Is` matches, and let
`internal/handler` map that error to the response that R3 requires. Tests can use an `httptest.Server` that delays its
response past 5 seconds, closes the connection, or returns a 5xx status, and count the attempts it receives.

### Justification

A failure of the policy service is often short, such as a restart or a lost connection, so a few retries let most
requests through without the caller doing anything (R2). A limit per attempt keeps one slow response from using up the
whole wait, so the retries still get a chance (R1). An answer from the policy service, including a denial, is a valid
result, and retrying it would only repeat it (R2). A denial or a request error from the policy service says nothing
about its availability, so only timeouts, transport errors, and 5xx statuses count as failures (**failed attempt**).

HTTP 503 tells the caller that the failure is temporary and on the server side, and the reason code
`POLICY_UNAVAILABLE` tells it apart from a rejected token (R3). Refusing the request keeps token-gate from letting a
request through without a policy evaluation (R3).

### Alternatives considered

- **A1. Fail the request on the first failed attempt.** Rejected by R2: a short outage of the policy service would
  refuse every request that arrives during it.
- **A2. One 5-second timeout that covers the first attempt and all retries.** Rejected by R1: a slow first attempt would
  use up the whole time, and no retry would run.
- **A3. Let the request through when the policy service is unavailable (fail open).** Rejected by R3: requests would
  pass without a policy evaluation.
- **A4. Refuse the request with HTTP 500 or 502 when every attempt fails.** Rejected by R3: callers could not tell an
  unavailable policy service from an error in token-gate or a bad answer from the policy service.

## Consequences

Positive:

- Callers can retry a request that token-gate refused with `POLICY_UNAVAILABLE`, because the status 503 marks the
  failure as temporary.

Negative:

- A request can wait up to (1 + `<retry count>`) × 5 seconds before token-gate refuses it under R3.
- Retries add load to a policy service that is already failing, by up to `<retry count>` extra attempts per policy
  evaluation (R2).

## Open points

- **O1.** How many retries `internal/policyclient` sends after the first attempt. The meeting said "a few times", with
  no number. The platform team decides. Affects R2 and R3.
- **O2.** Which outcomes count as a failed attempt. This record assumes timeouts, transport errors, and HTTP statuses
  from 500 to 599. Other answers include adding HTTP 429, or counting only timeouts and transport errors. The platform
  team decides. Affects the term **failed attempt**, R2, and R3.
- **O3.** Whether a retry waits before it starts. The meeting set no delay, so this record leaves it to the
  implementation. The answers under consideration are no delay, a fixed delay, or exponential backoff with jitter. Any
  answer other than leaving it to the implementation adds a rule. The platform team decides. Affects R2.
````

### Message to the user

I wrote the record as `docs/adr/0001-retry-failed-policy-service-calls.md`. The repository has no records yet, so it uses `docs/adr/` and the full template. Its status is `Proposed`, and three open points block acceptance:

- **O1:** the number of retries. The notes only say "a few times", so the rules use the placeholder `<retry count>` instead of a number I made up.
- **O2:** which failures trigger a retry. I assumed timeouts, transport errors, and HTTP 5xx responses. A policy denial or a 4xx response is not retried.
- **O3:** whether a retry waits before it starts. The meeting set no delay.

I also need these answers to fill in the metadata:

1. Who owns this record? Please give me their GitHub account for the Owner field, which shows `<owner>` for now.
2. What is the platform team's GitHub account or team handle for the approver line, which shows `<platform team account>` for now?
3. R1 gives each attempt its own 5 seconds. Is that what the meeting meant, or should one 5-second limit cover the first attempt and all retries together?
4. Do you want a reading guide (a `docs/adr/README.md` that maps `internal/policyclient` and `internal/handler` to layers)? If you add one, every commit and pull request that changes code under those paths has to end with `Implements:` and `Defers:` trailers that name the rules it covers. Without the guide, the records still have numbered rules, but no change has to carry the trailers.
