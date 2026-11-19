### File: docs/adr/0001-retry-failed-calls-to-the-policy-service.md

````markdown
# Retry a failed call to the policy service, and refuse the request with HTTP 503 when every attempt fails

## Status

Proposed

### Owner

`<owner>`

### Participants and approvers

- Platform team: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. `internal/policyclient` calls the policy service
over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses.

A call to the policy service can fail, or it can take long enough to hold the request. In either case, token-gate has
no policy decision for the request.

## Decision

We will bound each call to the policy service at 5 seconds and retry a failed call a fixed number of times. When every
attempt fails, we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **attempt**: one HTTP call from the policy client to the policy service for one request. The first call and each
  retry are each one attempt.
- **failed attempt**: an attempt that ends in one of these ways:
  - it times out under R1;
  - it gets no HTTP response, for example because the connection is refused or reset;
  - it gets a response with a status from 500 to 599.

  An attempt that gets any other response is not a failed attempt, and neither is an attempt that returns a policy
  decision that denies the request.
- **policy client**: the code under `internal/policyclient`.

### Rules

#### Attempts

- **R1** (`policyclient`). The policy client ends an attempt that has not received a full response within 5 seconds of
  its start. The ended attempt is a failed attempt.
- **R2** (`policyclient`). After a failed attempt, the policy client makes another attempt for the same request. It
  makes at most `<retry count>` retries per request, so at most `<retry count>` + 1 attempts in total. The policy
  client makes no further attempt for a request after an attempt that is not a failed attempt.

#### Refusal

- **R3** (`policyclient`, `handler`). When every attempt that R2 allows for a request is a failed attempt, token-gate
  refuses the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`, and the request does not proceed past
  the token check.

### Implementation notes

Adds no requirement. Give each attempt its own `context.WithTimeout` of 5 seconds, derived from the context of the
incoming request. Let the policy client return one sentinel error once it has made its last attempt, and let the handler
map that error to the response that R3 requires. A short backoff with jitter between attempts spreads the load on the
policy service. The delay between attempts is the implementer's choice. Test the attempt count and the refusal against
an `httptest.Server` that fails, hangs, or recovers after a given number of calls.

### Justification

Most failures of a call to the policy service are short, such as a restarted instance or a dropped connection, and a
retry often succeeds (R2). The timeout per attempt stops a slow policy service from holding a request for longer than
5 seconds per attempt (R1). HTTP 503 tells the caller that the failure is on the server side and temporary, so the
caller can retry later. The reason code tells the caller which dependency failed (R3). Without a policy decision,
token-gate cannot tell whether the request is allowed, so the request is refused (R3).

### Alternatives considered

- **A1. Let the request through when the policy service is unavailable.** Rejected by R3: a request would then pass
  without any policy decision.

## Consequences

Negative:

- A request whose attempts all time out waits up to (`<retry count>` + 1) × 5 seconds, plus the delays between
  attempts, before token-gate refuses it (R1, R2).
- When the policy service is overloaded, retries add calls to it (R2).
- While the policy service is unavailable, token-gate refuses every request that reaches policy evaluation (R3).

## Open points

- **O1.** How many retries does the policy client make per request? The meeting said "a few times" and gave no number.
  The platform team decides. This affects R2 and R3.
- **O2.** The record assumes that a failed attempt is a timeout, a call with no HTTP response, or a status from 500 to
  599, as **failed attempt** defines it. Other answers are to also retry a 429, or to retry only timeouts and calls with
  no response. The platform team decides. This affects R2 and R3.
````

### Message to the user

I wrote ADR-0001 in `docs/adr/`. The repository has no records yet, so this is the first one, and its status is `Proposed`. Before it can be `Accepted`, the platform team needs to sign off, and these questions need answers:

1. **Owner**: who owns this record? Please give me their GitHub account so I can replace `<owner>`. If you have the platform team's GitHub handle, I'll add it under **Participants and approvers** as well.
2. **Retry count (O1)**: the notes say "a few times". How many retries should there be after the first call? R2 and R3 use the placeholder `<retry count>` until you tell me.
3. **What counts as a failure (O2)**: I assumed a retry happens after a timeout, a call that gets no HTTP response, or a 5xx status. A 4xx status or a deny decision doesn't trigger a retry. Is that right, or should a 429 also be retried?
4. **Reasons and alternatives**: the notes didn't give reasons. I wrote the **Justification** and alternative A1 (letting the request through when the policy service is down). Please confirm both match what the meeting meant.
5. **Reading guide**: should I add a `docs/adr/README.md` that maps the rule layers (`policyclient`, `handler`) to paths? It would also need a paragraph in the agent instructions. This commits the team to a process: every change to code under those paths would end its commit message and pull request description with `Implements:` and `Defers:` trailers that name ADR rules. Without a guide, the record still has numbered rules, but no change has to carry those trailers.
