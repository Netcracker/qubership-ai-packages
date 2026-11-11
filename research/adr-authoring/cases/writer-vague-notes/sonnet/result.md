### File: docs/adr/0001-retry-policy-calls-and-refuse-with-503.md

````markdown
# Retry a failed policy service call, and refuse the request with HTTP 503 when every retry fails

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R4.

## Context

`token-gate` checks the token of each request before policy evaluation. `internal/policyclient` calls the policy
service over HTTP, and `internal/handler` turns the errors of `internal/policyclient` into responses. The policy service
can fail to answer a call. A call that never completes would hold the request open, and a request the service cannot
decide has no policy result.

## Decision

We will retry a failed policy call up to `<retry count>` times, each call with a timeout of 5 seconds. When every call
for a request has failed, we will refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.

### Terms

- **policy call**: one HTTP request that `internal/policyclient` sends to the policy service.
- **failed call**: a policy call that ends with a transport error, or that does not complete within the timeout of R1.
  O2 asks whether an HTTP error status also makes a call a failed call.
- **exhausted request**: a request for which the first policy call and all `<retry count>` retries are failed calls.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). Each policy call times out after 5 seconds, and a policy call that times out is a failed
  call.
- **R2** (`policyclient`). After a failed call, `internal/policyclient` retries the policy call for the same request,
  up to `<retry count>` retries, and stops retrying at the first policy call that is not a failed call.
- **R3** (`policyclient`). For an exhausted request, `internal/policyclient` returns an error to its caller.

#### Refusal

- **R4** (`handler`). For an exhausted request, `internal/handler` refuses the request with HTTP status 503 and the
  reason code `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. A test can run `internal/policyclient` against a fake policy service that hangs for longer than
5 seconds, and another test can drive `internal/handler` with the error of R3. Together they show R1 to R4.

### Justification

A bounded timeout and a bounded retry count limit how long one request waits for the policy service (R1, R2). A request
whose policy call cannot complete is refused, so that no request passes without a policy result (R3, R4).

### Alternatives considered

- **A1. Retry a failed policy call until it succeeds.** Rejected by R2: the retries stop after `<retry count>`.
- **A2. Allow the request when every policy call has failed.** Rejected by R4: an exhausted request is refused.

## Consequences

Negative:

- A request can wait for 5 seconds multiplied by `<retry count>` plus 1, before the refusal of R4. The delay between
  retries is not decided, and adds to that time.
- While the policy service fails every call, `internal/handler` refuses every request with 503 (R4).

## Open points

- **O1.** What is the retry count? The meeting notes say "a few times". The platform team decides. It affects R2, R3,
  R4, and the terms **exhausted request** and **failed call**.
- **O2.** Does a policy call that receives an HTTP error status, such as 500 or 429, count as a failed call and get
  retried? This record assumes that only a transport error or a timeout does. The platform team decides. It affects the
  term **failed call**, R2, R3, and R4.
- **O3.** Where does the response of R4 carry the reason code `POLICY_UNAVAILABLE`: a field of the response body, or a
  header? The platform team decides. It affects R4.
````

### Message to the user

I drafted `docs/adr/0001-retry-policy-calls-and-refuse-with-503.md` with the status `Proposed`. The repository has no records, so I used the default directory, filename pattern, and the full template.

Questions:

1. Who owns the record? The meeting notes leave it open, so the Owner field holds `<owner account>`. The platform team's account is also a placeholder, `<platform team account>`.
2. What is the retry count? The notes say "a few", and I did not invent a number. `<retry count>` is in R2 and the terms, and O1 asks for it.
3. Should an HTTP error status from the policy service, such as 500, be retried? I assumed that only a transport error or a timeout counts as a failed call (O2). Change it if you want error statuses retried.
4. Where does the response carry `POLICY_UNAVAILABLE`, in the body or in a header? O3 asks for it.
5. Should I add a reading guide, `docs/adr/README.md`? It would map the layers to paths and commit the team to ending each commit message and pull request description with `Implements:` and `Defers:` trailers for code under those paths. I did not add it. Until it exists, the layer tags `policyclient` and `handler` in R1 to R4 name `internal/policyclient` and `internal/handler`, and no layer map confirms them.

Other points:

- The notes give no reasons. The Justification and the two alternatives follow only from R2 and R4. Please confirm or correct them.
- The Date heading is left out until the record is accepted. The status stays `Proposed` until O1 to O3 are settled and the platform team signs off.
- There is no Confirmation section yet, because no checks exist. Add entries when tests land.
- I did not add the request timeout or the retry delay as rules, because the notes do not state them. The delay between retries is the implementer's choice, and the Consequences section mentions it.
