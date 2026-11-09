### File: docs/adr/0001-retry-and-refuse-when-policy-service-fails.md

````markdown
# 1. Retry failed policy service calls, then refuse the request with 503

- Status: Accepted
- Date: November 9, 2026
- Approved by: platform team
- Owner: TBD

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the policy service, made by `internal/policyclient`. `internal/handler` turns the errors of that client into responses.

The policy service can fail or respond slowly. token-gate needs one defined behavior for that case.

## Decision

- When a call to the policy service fails, `internal/policyclient` retries it. The retry count is TBD (see "Open items").
- Each call to the policy service times out after 5 seconds.
- When every retry has failed, `internal/handler` refuses the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

## Consequences

- A request is never evaluated without a policy decision. When the policy service stays unavailable, the request is refused.
- A client can tell a refusal caused by an unavailable policy service from other refusals by the reason code `POLICY_UNAVAILABLE`.
- Retries add latency to a request that is eventually refused. Because the timeout applies to each call, the worst case is the 5 second timeout multiplied by the number of attempts.

## Open items

- The number of retries and any delay between them are not fixed in the meeting notes. Fill them in before this record is merged.
- The owner of this record is not settled.
````

### Message to the user

I wrote the ADR as `docs/adr/0001-retry-and-refuse-when-policy-service-fails.md`. The repository has no ADR directory or convention, so the path and the `0001` numbering are my choice. Tell me if you prefer `docs/decisions/`.

Questions before it merges:

1. How many retries? The notes say "a few times", and I did not turn that into a number. The ADR says "TBD" and lists it under open items.
2. Is there a delay or backoff between retries? The notes don't say, so the ADR doesn't mention one.
3. Who owns the record? The notes say this is not settled, so the ADR says `Owner: TBD`.

I could not read the code, so the ADR describes the decision from the meeting notes and does not claim that `internal/policyclient` or `internal/handler` already behave this way. Check that against the code, or tell me and I'll adjust the wording.

I set the status to Accepted because the platform team approves. I used today's date, November 9, 2026, since the notes give no meeting date. Change either if they're wrong.
