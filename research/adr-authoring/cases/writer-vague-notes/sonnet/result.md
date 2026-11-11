### File: docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md

````markdown
# Retry a failed policy service call, then refuse the request with 503 and `POLICY_UNAVAILABLE`

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Platform team, `<GitHub account or team of the platform team>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the
policy service, made by `internal/policyclient`. `internal/handler` turns the errors of `internal/policyclient` into
responses. The policy service can fail to answer, and until now the repository has recorded no decision on how long a
call waits, how often it is repeated, or what the caller of token-gate receives when the policy service stays down.

## Decision

We will retry a failed call to the policy service up to `<retry count>` times, with each call timing out after 5 seconds,
and we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every call has failed.

### Terms

- **policy call**: one HTTP call that `internal/policyclient` makes to the policy service for one request. The first
  call and each retry of it are separate policy calls.
- **failed policy call**: a policy call that ends without a usable answer from the policy service, as O2 defines.
- **retry**: a policy call that `internal/policyclient` makes for a request after a failed policy call for that request.

### Rules

#### Calling the policy service

- **R1** (`policyclient`). `internal/policyclient` ends a policy call that has not completed 5 seconds after it started,
  and counts it as a failed policy call.
- **R2** (`policyclient`). After a failed policy call, `internal/policyclient` makes a retry, until a policy call
  succeeds or `<retry count>` retries have failed. Each retry is subject to R1.

#### Refusing the request

- **R3** (`policyclient`, `handler`). When the first policy call for a request and all `<retry count>` retries have
  failed, `internal/policyclient` returns an error, and `internal/handler` refuses the request with HTTP status 503 and
  the reason code `POLICY_UNAVAILABLE`.

### Justification

A retry absorbs a failure that lasts for one call, such as a dropped connection (R2). The 5 second limit bounds how long
one call holds the request (R1). A fixed status and reason code let a caller tell an unavailable policy service from a
refusal by policy (R3).

## Consequences

Negative:

- A request can wait for `<retry count>` plus one policy calls of 5 seconds each, before it is refused (R1, R2).
- While the policy service is down, token-gate refuses every request that needs policy evaluation (R3).

## Open points

- **O1.** The number of retries. The meeting notes say "a few times". Who decides: the platform team. Affects R2, R3,
  and the first Negative item.
- **O2.** Which outcomes make a policy call fail. Assumption: a policy call fails when it times out (R1), when the
  connection cannot be made or breaks, or when the policy service returns an HTTP status of 500 or above. A policy
  service response that denies the request is not a failure, and neither is a 4xx status, so neither is retried. Who
  decides: the platform team. Affects R2, R3, and the definition of failed policy call.
- **O3.** Where the reason code `POLICY_UNAVAILABLE` appears in the 503 response, such as a body field or a header. Who
  decides: the platform team. Affects R3.
- **O4.** The owner of this record is not settled. Who decides: the platform team. Blocks the `Accepted` status.
````

### Message to the user

I wrote one record, `docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md`. The repository has no records, so I used the default location, filename pattern, and the whole template. The status is `Proposed`, and there is no Date heading until the team accepts it.

Questions I need answered before the record can be accepted:

1. **Owner.** Who owns the record? The notes say this is not settled, so the Owner field holds a placeholder. Please also give the GitHub account or team name of the platform team, which approves R1 to R3.
2. **Retry count.** "A few times" is not a value. I wrote `<retry count>` in R2 and R3 and added open point O1. What number should it be?
3. **What counts as a failure.** The notes say "the call fails". I assumed a timeout, a connection error, or an HTTP status of 500 or above. A policy denial and a 4xx status are not retried under that assumption. Please confirm this (O2).
4. **The reason code.** Is `POLICY_UNAVAILABLE` a field in the response body, a header, or something else (O3)?
5. **Reasons and alternatives.** The notes give no reasons or rejected options, so the Justification is short and I left out **Alternatives considered**. I did not invent any. If you want one recorded, such as allowing the request when the policy service is down, tell me what the team weighed.
6. **Reading guide.** The repository has no `README.md` that describes records, so I did not add one, and the rules use the component names `policyclient` and `handler` as layers. A guide would commit the team to ending every commit message and pull request description for code in the mapped paths with `Implements:` and `Defers:` trailers. It would also add a short paragraph to the agent instructions. Do you want me to add it, with that commitment?

I listed no checks under **Confirmation** because I know of no existing test for these rules. Once a test exists, such as one that fakes a failing policy service, it can be added.
