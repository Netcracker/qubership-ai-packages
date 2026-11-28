### File: docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md

````markdown
# Retry failed calls to the policy service, and refuse the request with 503 when every retry fails

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP to the
policy service, made by `internal/policyclient`. `internal/handler` turns the errors of `internal/policyclient` into
responses. The policy service can be slow or unreachable, and a request cannot be evaluated without it.

## Decision

We will time out each call to the policy service after 5 seconds, retry a failed call a fixed number of times, and refuse
the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every retry has failed.

### Terms

- **policy service**: the service that `internal/policyclient` calls over HTTP for policy evaluation.
- **call**: one HTTP request that `internal/policyclient` sends to the policy service, whether it is the first attempt
  for a request or a retry.
- **failed call**: a call that times out under R1, ends with a connection error, or receives an HTTP response with a
  status from 500 to 599.
- **retry**: a call that `internal/policyclient` sends for the same request after a failed call.

### Rules

#### Calls to the policy service

- **R1** (`internal/policyclient`). Each call times out 5 seconds after it starts, and a call that times out is a failed
  call.
- **R2** (`internal/policyclient`). After a failed call, `internal/policyclient` sends a retry, up to `<retry count>`
  retries for one request.
- **R3** (`internal/policyclient`). Where the first call and every retry for one request have failed, `internal/policyclient`
  returns an error to its caller.

#### Refusing the request

- **R4** (`internal/handler`). Where `internal/policyclient` returns the error of R3, `internal/handler` refuses the
  request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`.

### Implementation notes

Adds no requirement. Test R2 to R4 with a fake policy service that fails every call, and check the number of calls it
receives and the response of `internal/handler`. Test R1 with a fake that responds after more than 5 seconds.

### Justification

The timeout and the retry limit bound how long one request waits for the policy service (R1, R2). A request that cannot
be evaluated gets a distinct refusal, so that a caller can tell an unavailable policy service from a denied request (R3,
R4).

## Consequences

Negative:

- While the policy service is down, token-gate refuses every request that needs policy evaluation (R4).
- A request can wait up to 5 seconds for each call, so up to `<retry count>` + 1 calls take that many times 5 seconds
  before the refusal (R1, R2).

## Open points

- **O1.** The number of retries is not settled; the meeting notes say "a few times". The platform team decides. It
  affects R2 and the second Negative item.
- **O2.** The record assumes that a connection error, a timeout, and an HTTP 5xx response are failed calls, and that an
  HTTP 4xx response is not. The platform team confirms or corrects this. It affects the definition of failed call and so
  R2 and R3.
- **O3.** The notes do not say where `POLICY_UNAVAILABLE` is carried. The record assumes the response body. The platform
  team decides. It affects R4.
- **O4.** The notes give no wait between retries. The platform team decides whether there is one, and its length. It
  would add a rule to R2's topic.
````

### Message to the user

I wrote the record as `docs/adr/0001-retry-policy-service-calls-and-refuse-with-503.md`. The repository has no records, so I used the default directory, numbering, and the full template. The status is `Proposed`, and the Date heading is left out until the team accepts it.

**Questions**
- Who owns the record? The notes leave this open, so `Owner` is the placeholder `<owner GitHub account>`. I also need the platform team's GitHub account for **Participants and approvers**.
- How many retries? The notes say "a few", and I did not invent a number. R2 carries `<retry count>`, and O1 asks for the value.
- Do you want a reading guide? A `docs/adr/README.md` would map layers to paths and commit you to ending every commit message and pull request description with the `Implements` and `Defers` trailers for code under those paths. I did not add one. Without it, the layer tags in the rules use the package names `internal/policyclient` and `internal/handler`.

**Assumptions to confirm**
- A failed call is a timeout, a connection error, or an HTTP 5xx response (O2). A 4xx response is not retried.
- `POLICY_UNAVAILABLE` is carried in the response body (O3).
- The notes give no wait between retries, so no rule sets one (O4).

**What the notes left out**
- The notes give no reasons and no rejected alternatives. The Justification is limited to what the rules imply, and I left out **Alternatives considered**. If the meeting discussed options, such as failing open when the policy service is down, send them and I'll add them.
- No tests exist yet, so **Confirmation** is absent. Add entries as they land.

The record stays `Proposed` until O1 to O4 are settled and the owner is named.
