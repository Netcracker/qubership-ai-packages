### File: docs/adr/0001-retry-failed-policy-service-calls.md

````markdown
# Retry failed calls to the policy service, and refuse the request with 503 when every attempt fails

## Status

Proposed

### Owner

`<GitHub account of the owner, not settled yet>`

### Participants and approvers

- Platform team, `<GitHub team of the platform team>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/policyclient` calls the policy service
over HTTP for each evaluation, and `internal/handler` turns the errors of `internal/policyclient` into responses.

A call to the policy service can fail because the connection fails, because the policy service does not respond in
time, or because it returns a server error. Many of these failures are short-lived, so a second call often succeeds.
token-gate cannot finish policy evaluation without an answer from the policy service.

## Decision

We will retry a failed call to the policy service a fixed number of times, with a timeout of 5 seconds on each call. We
will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every attempt has failed.

### Terms

- **attempt**: one HTTP request that `internal/policyclient` sends to the policy service, from the start of the request
  until the response body has been read in full or the request ends with an error.
- **evaluation**: the attempts that `internal/policyclient` makes for the policy evaluation of one incoming request.
- **failed attempt**: an attempt that ends in a connection error, that ends because of the timeout of R1, or that
  receives a response with an HTTP status from 500 to 599. An attempt that receives any other status is not a failed
  attempt, and neither is an attempt that ends because the incoming request was canceled.
- **refuse**: token-gate sends the response that the rule names to the client and does not pass the incoming request on.

### Rules

#### Attempts

- **R1** (`policyclient`). `internal/policyclient` ends each attempt that has not finished 5 seconds after it started,
  and the attempt counts as a failed attempt.
- **R2** (`policyclient`). After a failed attempt, `internal/policyclient` makes a new attempt for the same evaluation,
  until `<retry count>` attempts after the first one have been made. `internal/policyclient` makes no new attempt for an
  evaluation after an attempt that is not a failed attempt.

#### Refusal

- **R3** (`policyclient`, `handler`). When every attempt of an evaluation is a failed attempt and R2 allows no further
  attempt, token-gate refuses the incoming request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. Give each attempt its own `context.WithTimeout` of 5 seconds, derived from the context of the
incoming request, so that the cancellation of the incoming request also ends the attempt. Let `internal/policyclient`
return a sentinel error, such as `ErrPolicyUnavailable`, once it has made the last attempt that R2 allows, and let
`internal/handler` match it with `errors.Is` to build the response of R3. A short wait between attempts, with jitter,
spreads the load on the policy service when many evaluations fail at once.

### Justification

A short-lived failure of the policy service, such as a restart or a dropped connection, refuses no request when a later
attempt succeeds (R2). A timeout on each attempt keeps one slow response from using up the time of the whole evaluation
(R1). A fixed number of attempts bounds the time a request waits and the extra load on the policy service (R2). A
request that token-gate cannot evaluate is refused, because passing it on would skip policy evaluation (R3). HTTP 503
tells the client that the failure is temporary, and `POLICY_UNAVAILABLE` lets the client and the operators tell this
refusal apart from a policy denial (R3).

### Alternatives considered

- **A1. Make one attempt per evaluation and refuse the request when it fails.** Rejected by R2: a single dropped
  connection would refuse a request that a second attempt would have evaluated.
- **A2. Pass the request on without policy evaluation when the policy service is unavailable (fail open).** Rejected by
  R3: a request would reach the upstream service without a policy decision.
- **A3. Retry until a deadline for the whole evaluation passes, with no limit on the number of attempts.** The number of
  attempts, and so the load on a failing policy service, would depend on how fast each attempt fails.

## Consequences

Positive:

- Operators can count refusals caused by the policy service by the reason code `POLICY_UNAVAILABLE`, apart from policy
  denials.

Negative:

- While the policy service does not respond, a request waits up to 5 seconds for each of the `<retry count>` + 1
  attempts of R1 and R2, plus any wait between attempts, before token-gate refuses it.
- Retries add load to a policy service that is already failing, up to `<retry count>` + 1 attempts per evaluation (R2).
- Every request is refused with HTTP 503 while the policy service is unavailable (R3).

## Open points

- **O1.** How many attempts does `internal/policyclient` make after the first one? The notes say "a few times" and give
  no number. The platform team decides. Affects R2.
- **O2.** The definition of **failed attempt** assumes that only connection errors, the timeout of R1, and HTTP statuses
  from 500 to 599 are retried, and that HTTP 429 and other statuses from 400 to 499 are not. The alternative under
  consideration is to retry HTTP 429 as well. The platform team decides. Affects R1 to R3.
- **O3.** R3 assumes that `internal/handler` returns `POLICY_UNAVAILABLE` in the same field of the response body that
  carries the reason code of its other refusals. The alternative under consideration is a dedicated response header.
  The platform team decides. Affects R3.
````

### Message to the user

I drafted the record as `docs/adr/0001-retry-failed-policy-service-calls.md`. The repository had no records yet, so it starts the `docs/adr/` directory. Its status is `Proposed`, and it stays that way until O1 to O3 are closed and the platform team signs off.

Things I need from you:

1. **Owner:** who owns this record? The notes leave it open, so the Owner field holds a placeholder.
2. **Platform team account:** which GitHub team should be listed as the approver?
3. **Retry count (O1):** the notes say "a few times" but give no number. I didn't guess one, so R2 has a placeholder `<retry count>`.
4. **Retried failures (O2):** I assumed only these are retried: connection errors, the 5-second timeout, and HTTP 500–599. HTTP 429 and other 4xx responses are not. Is that right?
5. **Reason code location (O3):** I assumed `POLICY_UNAVAILABLE` goes in the same response-body field that `internal/handler` already uses for its other reason codes. Is that where it belongs?
6. **Reading guide:** do you want a reading guide added in `docs/adr/README.md`, with a pointer in the agent instructions? If you add it, every change to code under the mapped paths (for example `internal/policyclient` and `internal/handler`) must end its commit message and PR description with `Implements:` and `Defers:` trailers that cite the record's rules. I didn't add it, because it commits the team to that process.
