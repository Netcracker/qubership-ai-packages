### File: docs/adr/0001-retry-failed-policy-service-calls-then-refuse-with-503.md
````markdown
# Retry failed calls to the policy service, then refuse the request with HTTP 503

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team, `<GitHub team>`: approves R1 to R5.

## Context

token-gate checks the token of each request before policy evaluation. To do that, `internal/policyclient` calls the
policy service over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses. The policy
service can fail to answer. Its connection can break, a call can hang, or it can return a server error. Each of these
failures leaves token-gate with no policy result for the request.

## Decision

We will time out each call to the policy service after 5 seconds and retry a failed call a fixed number of times. When
every attempt has failed, we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **incoming request**: one HTTP request that token-gate receives and checks.
- **attempt**: one HTTP request that `policyclient` sends to the policy service for one incoming request.
- **failed attempt**: an attempt that `policyclient` cancels under R1, an attempt that ends in a transport error such as
  a refused connection, a reset connection, or a failed DNS lookup, or an attempt that receives a response with an HTTP
  status from 500 to 599. An attempt that receives a response with any other status is not a failed attempt.

### Rules

#### Timeout

- **R1** (`policyclient`). `policyclient` cancels an attempt when the attempt has not received a complete response 5
  seconds after it started.

#### Retries

- **R2** (`policyclient`). After a failed attempt, `policyclient` sends a new attempt for the same incoming request,
  until it has sent `<retry count>` attempts after the first attempt.
- **R3** (`policyclient`). After an attempt that is not a failed attempt, `policyclient` sends no further attempt for
  the same incoming request.
- **R4** (`policyclient`). When the last attempt that R2 allows for an incoming request is a failed attempt,
  `policyclient` returns an error that `handler` can tell apart from every other error that `policyclient` returns.

#### Response

- **R5** (`handler`). When `policyclient` returns the error of R4, `handler` refuses the incoming request with HTTP
  status 503 and the reason code `POLICY_UNAVAILABLE`. `handler` uses the reason code `POLICY_UNAVAILABLE` for no other
  outcome.

### Implementation notes

Adds no requirement. Give each attempt its own `context.WithTimeout` of 5 seconds, derived from the context of the
incoming request, so that a client that disconnects also stops the remaining attempts. Return a sentinel error such as
`ErrPolicyUnavailable` from `policyclient` for R4, wrapped with the error of the last attempt, and match it in `handler`
with `errors.Is`. Test R1 to R4 against an `httptest.Server` that hangs, closes the connection, returns 503, and
returns a 4xx status. Test R5 with a fake `policyclient` that returns the sentinel error.

### Justification

A short outage or a single broken connection to the policy service fails one attempt, and a retry often succeeds (R2).
A response outside the 5xx range is an answer from the policy service, and repeating the attempt would return the same
answer (R3). The timeout puts an upper bound on how long one attempt can hold an incoming request (R1). HTTP 503 tells
the client that the refusal is temporary and that it can try again later. The reason code lets the client and the
operators tell an unavailable policy service apart from a policy decision (R4, R5).

### Alternatives considered

- **A1. Let the request through when the policy service does not answer (fail open).** Rejected by R5: a request would
  then pass without a policy decision.
- **A2. Refuse the request after the first failed attempt.** Rejected by R2: a short outage would then refuse every
  incoming request it overlaps.

## Consequences

Negative:

- In the worst case, one incoming request waits 5 seconds for each of the `<retry count>` + 1 attempts, plus any wait
  between attempts, before `handler` refuses it (R1, R2).
- While the policy service is failing, each incoming request sends up to `<retry count>` + 1 attempts to it, which adds
  load to a service that is already failing (R2).

## Open points

- **O1.** How many attempts does `policyclient` send after the first attempt? The meeting agreed on "a few" retries.
  The platform team decides. Affects R2.
- **O2.** Which attempts count as failed? This record assumes a timeout, a transport error, and a 5xx status, and
  treats every 4xx status, 429 included, as an answer. The answers under consideration are this set, this set with 429
  added, or only timeouts and transport errors. The platform team decides. Affects **failed attempt**, R2, R3, and R4.
- **O3.** Where does the response of R5 carry the reason code? This record assumes the place that token-gate already
  uses for reason codes in its other error responses. Other possible answers are a named field in a JSON body or a
  response header. The platform team decides. Affects R5.
````

### Message to the user

I've drafted the record as `docs/adr/0001-retry-failed-policy-service-calls-then-refuse-with-503.md`. The repository had no records yet, so it uses the default location and starts at number 0001. Its status is `Proposed` and it should stay that way until the open points are closed.

Things I need from you:

1. **Owner:** who owns this record? Please give me their GitHub account so I can fill in `<owner>`.
2. **Platform team:** what is the team's GitHub handle? I'll use it to replace `<GitHub team>`.
3. **Retry count (O1):** the notes say "a few times". I used the placeholder `<retry count>` rather than guess a number. It appears in R2 and in the Negative consequences.
4. **What counts as a failed call (O2):** I assumed a timeout, a transport error, or a 5xx status, and no 4xx status (429 included). Is that right?
5. **Where the reason code goes (O3):** I assumed it goes wherever token-gate already puts reason codes in its error responses. If there is no such place yet, which field or header should carry it?
6. **Wait between attempts and an overall deadline:** the notes didn't mention either, so the rules leave both to whoever writes the code. With the timeout at 5 seconds, a request could wait 5 seconds × (retries + 1). Do you want a backoff or a total time limit as a rule?
7. **Justification and alternatives:** the notes gave no reasons, and I wrote the Justification and the two alternatives (fail open, no retry) myself. Please remove any alternative the team didn't actually discuss, and correct the reasons if they don't match yours.
8. **Reading guide:** should I add a `docs/adr/README.md` guide that maps the layers `policyclient` and `handler` to their paths? Adding it commits the team to ending every commit message and pull request description that touches those paths with `Implements:` / `Defers:` trailers that name the rules of this record. Without the guide, the record still binds code once it is accepted, but no change has to carry the trailers.
