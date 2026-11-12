### File: docs/adr/0001-refuse-requests-with-503-when-the-policy-service-is-unavailable.md

````markdown
# Retry failed policy calls, then refuse the request with 503 `POLICY_UNAVAILABLE`

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation is a call over HTTP from
`internal/policyclient` to the policy service. `internal/handler` turns the errors of `internal/policyclient` into
responses. The policy service can be slow or unreachable, so a call to it can fail.

## Decision

We will time out each call to the policy service after 5 seconds, retry a failed call up to `<retry count>` times, and
refuse the request with HTTP 503 and the reason code `POLICY_UNAVAILABLE` when every attempt has failed.

### Terms

- **attempt**: one HTTP request that `internal/policyclient` sends to the policy service. The first call and each retry
  are one attempt each.
- **failed attempt**: an attempt that ends in a transport error or reaches the timeout of R1. An attempt that receives
  an HTTP response is not a failed attempt, whatever the status code of the response is.
- **exhausted call**: a call to the policy service in which the first attempt and all `<retry count>` retries are failed
  attempts.

### Rules

#### Calls to the policy service

- **R1** (`policyclient`). `internal/policyclient` ends each attempt as a failed attempt when the attempt has received
  no HTTP response 5 seconds after it was sent.
- **R2** (`policyclient`). After a failed attempt, `internal/policyclient` sends another attempt, up to `<retry count>`
  retries per call. It stops at the first attempt that is not a failed attempt and returns the result of that attempt.
- **R3** (`policyclient`). For an exhausted call, `internal/policyclient` returns an error that `internal/handler` can
  tell apart from every other error of `internal/policyclient`.

#### Response to the request

- **R4** (`handler`). When the call to the policy service for a request is an exhausted call, `internal/handler`
  refuses the request with HTTP status 503 and the reason code `POLICY_UNAVAILABLE`, and the request does not proceed.

### Justification

The timeout and the retry limit bound how long a request waits for the policy service (R1, R2). A request whose policy
cannot be evaluated is refused instead of admitted, so no request passes without a policy decision (R4). A distinct
error lets `internal/handler` give this case its own status and reason code (R3, R4).

### Alternatives considered

- **A1. Admit the request when the policy service is unavailable.** Rejected by R4: the request would pass without a
  policy decision.

## Consequences

Negative:

- While the policy service is unavailable, every request is refused with 503 (R4).
- A refused request can wait up to (`<retry count>` + 1) × 5 seconds for the 503 (R1, R2). The record sets no pause
  between attempts (O1).

## Open points

- **O1.** The retry count: the notes say "a few times" and give no number, and nobody has yet said whether a pause
  separates the attempts. The platform team decides. Affects R2, R4, and the decision sentence.
- **O2.** Which outcomes of an attempt are failures. The notes say "the call fails". This record assumes a transport
  error or a timeout. The answer under consideration is that an HTTP 5xx response from the policy service also counts
  as a failed attempt. The platform team decides. Affects the definition of **failed attempt**, and R2 to R4.
- **O3.** The owner of this record is not settled. Affects the Owner field only.
````

### Message to the user

I drafted the record as `Proposed`. Four things need your input before it can be `Accepted`.

1. **Owner.** The notes say the owner is not settled, so the Owner field holds `<owner account>`. Which GitHub account owns this record? I also need the GitHub account of the platform team, for the approvers line.
2. **Retry count.** "A few times" is not a number, so R2 holds `<retry count>` and O1 asks for the value. Is there a pause between attempts?
3. **What counts as a failed call.** I assumed a transport error or a timeout. Should an HTTP 5xx response from the policy service be retried as well (O2)?
4. **Wording I added.** The notes give no rationale, so I wrote the Justification, Alternative A1 (admit the request when the policy service is unavailable), and the Negative consequences from the decision itself. Please check them. I also assumed that `internal/policyclient` returns a distinguishable error for the exhausted case (R3). The notes do not say where the reason code goes in the 503 response, for example a body field or a header. R4 does not state it. Tell me if the record should.

The repository has no records and no guide, so I created none. I used the paths `docs/adr/` and number `0001`, and left out the Date heading until acceptance. I left out Confirmation because no check exists yet. Do you want a `docs/adr/README.md` reading guide? It would commit the team to ending each commit message and pull request description with `Implements:` and `Defers:` trailers for code under `internal/policyclient` and `internal/handler`. It would also need a short paragraph in the agent instructions.
