### File: docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md

````markdown
# Retry failed calls to the policy service, and refuse the request with HTTP 503 when every attempt fails

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Platform team, `<GitHub team of the platform team>`: approves R1 to R3.

## Context

token-gate checks the token of each incoming request before policy evaluation. `internal/policyclient` calls the
policy service over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses.

The policy service runs as a separate service, so the HTTP call can fail. The connection can drop, the policy service
can restart, and a call can hang without an answer.

## Decision

We will retry a failed call to the policy service up to a fixed number of times, end each call after 5 seconds, and
refuse the incoming request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every attempt has failed.

### Terms

- **attempt**: one HTTP request that `internal/policyclient` sends to the policy service, from the moment it starts to
  connect until it has read the whole response body.
- **failed attempt**: an attempt that ends at the timeout of R1, that ends with a connection or transport error before
  the whole response arrives, or that receives a response with a 5xx status. Every other attempt is not a failed
  attempt.
- **retry**: an attempt that `internal/policyclient` sends for the same incoming request after an earlier attempt.

### Rules

#### Timeout

- **R1** (`policyclient`). `internal/policyclient` ends an attempt that has not finished 5 seconds after it started.
  The limit applies to each attempt on its own, and a retry starts with a full 5 seconds.

#### Retries

- **R2** (`policyclient`). `internal/policyclient` sends a retry only after a failed attempt, and sends at most
  `<retry count>` retries for one incoming request.

#### Refusal

- **R3** (`policyclient`, `handler`). When the first attempt and every retry that R2 allows for an incoming request are
  failed attempts, token-gate refuses that incoming request with HTTP status 503 and the reason code
  `POLICY_UNAVAILABLE` in `<reason code location>`.

### Implementation notes

Adds no requirement. Set the 5-second limit with `http.Client.Timeout`, or with `context.WithTimeout` around each
attempt, so that the limit also covers reading the response body. Let `internal/policyclient` return a sentinel error,
such as `ErrPolicyUnavailable`, once it stops retrying, and let `internal/handler` match it with `errors.Is`. Tests can
use `httptest.Server` with a handler that returns 500, closes the connection, or sleeps past the timeout, and count the
requests it receives.

### Justification

A connection that drops or a policy service that restarts often recovers within a few seconds, so a retry turns many
such failures into a normal answer (R2). A limit on the number of retries keeps a request from waiting without end
while the policy service is down (R2). A limit per attempt keeps one call that hangs from using up the time of every
retry (R1).

A request whose policy was not evaluated is refused, so an outage of the policy service never lets a request through
(R3). HTTP 503 tells a client that the failure is on the server side and temporary, and the reason code
`POLICY_UNAVAILABLE` sets this refusal apart from a refusal for a bad token (R3).

### Alternatives considered

- **A1. Let the incoming request through when every attempt has failed (fail open).** Rejected by R3: a request
  whose policy was not evaluated would reach the service behind token-gate.
- **A2. Refuse the incoming request after the first failed attempt.** A short restart of the policy service would then
  refuse every request that arrives during it.

## Consequences

Positive:

- A client can tell from the reason code `POLICY_UNAVAILABLE` that it may send the same request again later (R3).

Negative:

- An incoming request can wait up to (`<retry count>` + 1) × 5 seconds, plus any delay between attempts, before
  token-gate refuses it (R1, R2).
- While the policy service is down, token-gate refuses every request that needs policy evaluation (R3).
- A policy service that is overloaded receives up to `<retry count>` + 1 requests for each incoming request (R2).

## Open points

- **O1.** How many retries `internal/policyclient` sends after the first attempt. The meeting settled on "a few" and
  named no number. The team that made the decision chooses the number, with the platform team's approval. Affects R2
  and R3.
- **O2.** Which failures count as a failed attempt. The record assumes a timeout, a connection or transport error, and
  a 5xx status, and leaves every 4xx status out of the term. Other answers are to add 429, or to retry only timeouts
  and transport errors. The platform team decides. Affects the term **failed attempt**, R2, and R3.
- **O3.** Where the response carries the reason code `POLICY_UNAVAILABLE`: a field of the JSON response body, such as
  `reason`, or a response header. The platform team decides. Affects R3.
- **O4.** Whether `internal/policyclient` waits between attempts, with a fixed delay or with exponential backoff and
  jitter, and whether one deadline bounds all attempts for an incoming request. Until this is settled, no rule states
  it. The platform team decides. Affects R2.
````

### Message to the user

I wrote the record as `docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md`. Its status is `Proposed`, and open points O1 to O4 block acceptance:

- **O1:** how many retries ("a few" has no number).
- **O2:** which failures trigger a retry. I assumed timeouts, connection errors, and 5xx, but not 4xx.
- **O3:** where the reason code goes in the response.
- **O4:** whether there is a delay or backoff between attempts, and whether one deadline covers all attempts.

The rules contain visible placeholders (`<retry count>`, `<reason code location>`) until these are answered.

Questions for you:

1. Who owns the record? I need a GitHub account for **Owner**.
2. What is the platform team's GitHub team or account for **Participants and approvers**? Did anyone else take part who should be listed?
3. The meeting notes give no reasons and list no alternatives. I wrote the Justification and A1 (fail open) and A2 (refuse after the first failure) from what the decision implies. Do these match what the team discussed?
4. The repository has no reading guide for its records. Should I add `docs/adr/README.md` that maps `internal/policyclient` and `internal/handler` to layers? That commits the team to ending every commit message and pull request description that changes those paths with `Implements:` and `Defers:` trailers that name the rules.
