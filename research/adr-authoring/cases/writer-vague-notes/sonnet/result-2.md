### File: docs/adr/0001-retry-policy-calls-and-refuse-with-503.md

````markdown
# Retry failed calls to the policy service, and refuse the request with 503 when every attempt fails

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team, `<account>`: approves R1 to R3.

## Context

`token-gate` checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the
policy service, made by `internal/policyclient`. `internal/handler` turns the errors of `internal/policyclient` into
responses. A call to the policy service can fail, and the meeting that preceded this record settled how many times the
call is repeated, how long one call may take, and what a request receives when the policy service stays unavailable.

## Decision

We will repeat a failed call to the policy service up to `<retry count>` times, give each call a timeout of 5 seconds,
and refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every call has failed.

### Terms

- **attempt**: one HTTP call that `internal/policyclient` makes to the policy service for one request.
- **failed attempt**: an attempt that ends in a connection error, in a timeout under R2, or in a response with an HTTP
  status from 500 to 599.
- **retry**: an attempt that follows a failed attempt for the same request.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). After a failed attempt, `internal/policyclient` makes a retry, until an attempt is not a
  failed attempt or `<retry count>` retries have been made for that request.
- **R2** (`policyclient`). `internal/policyclient` ends an attempt as a failed attempt when the policy service has not
  completed its response within 5 seconds (5000 milliseconds) of the start of that attempt.

#### Refusing the request

- **R3** (`policyclient`, `handler`). When the attempt and every retry for a request are failed attempts,
  `internal/policyclient` returns an error to `internal/handler`, and `internal/handler` refuses the request with HTTP
  status 503 and the reason code `POLICY_UNAVAILABLE`.

### Justification

R1 and R2 bound the time that a request waits for the policy service: at most `<retry count>` + 1 attempts of 5 seconds
each, plus any delay between attempts. R3 gives a request that has no policy decision a refusal with one fixed reason
code, so that a client can tell an unavailable policy service from a refusal by policy.

## Consequences

Negative:

- While the policy service is unavailable, every request that reaches policy evaluation is refused (R3).
- A request can wait for the policy service for up to (`<retry count>` + 1) × 5 seconds before it is refused (R1, R2).

## Open points

- **O1.** Who owns this record? The platform team approves the decision, and the meeting did not name an owner. The
  platform team decides. It affects the Owner field, not a rule.
- **O2.** What is the retry count? The meeting said "a few times". The platform team decides. It affects R1 and R3.
- **O3.** Which outcomes make an attempt a failed attempt? The record assumes a connection error, a timeout, or an
  HTTP status from 500 to 599, so that a 4xx response is not retried. The alternative is to retry on every response that
  is not a success. The platform team decides. It affects R1, R2, and R3.
- **O4.** Where does `internal/handler` put the reason code `POLICY_UNAVAILABLE` in the response, for example in a
  body field or in a header? The platform team decides. It affects R3.
- **O5.** Does the client wait between retries, and for how long? The meeting did not mention a delay, and no rule
  requires one. The platform team decides. If a delay is required, it adds a rule and changes the worst-case wait in
  **Consequences**.
- **O6.** Why did the platform team choose to refuse the request, and is there an alternative that was rejected? The
  meeting notes record the decision and no reasons. The platform team decides. It affects **Justification** and
  **Alternatives considered**, which the record does not have yet.
````

### Message to the user

I wrote `docs/adr/0001-retry-policy-calls-and-refuse-with-503.md` with the status `Proposed`. The repository has no records, so I used the default location, filename pattern, and the whole template. I made these choices and left these gaps:

- **Owner and approver account.** Please tell me who owns the record, and the GitHub account of the platform team's approver. Both are placeholders for now (O1).
- **Retry count.** The notes say "a few times", so R1 and R3 carry `<retry count>` until you give a number (O2).
- **What counts as a failed attempt.** The notes don't say. I assumed a connection error, a timeout, or a 5xx response, so a 4xx response is not retried. Please confirm or correct this (O3).
- **Placement of `POLICY_UNAVAILABLE`.** Is it a body field, a header, or something else? R3 doesn't say yet (O4).
- **Delay between retries.** The notes don't mention one, so I added no rule for it (O5).
- **Reasons and alternatives.** The notes give the decision but not why the team chose it. The Justification covers only what follows from the rules. I left out **Alternatives considered**. Please send the reasons and any rejected options (O6).

The status stays `Proposed` until the platform team signs off and the open points are settled. I left out **Confirmation** because no test or lint check exists yet.

I did not add a reading guide `README.md` or an agent-instructions paragraph. A guide commits the team to ending every commit message and pull request description with `Implements:` and `Defers:` trailers for code under the paths it maps. Do you want that? If so, I would map `internal/policyclient` and `internal/handler` as the layers `policyclient` and `handler`.
