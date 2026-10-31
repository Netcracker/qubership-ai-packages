**Review of the instrumentation and error text in `PaymentService.charge`**

**1. Remove the `log.error` before the throw.** (`Charging order {} failed after {} attempts`)

- That path logs the exception and then throws it. Sonar S2139 reports this pattern.
- `PaymentException` leaves `charge`, so it goes to the caller's channel. The controller maps it to 502, and the controller is the frame that handles it.
- Record the exception once there, with the order id and the cause. If the controller doesn't already log `PaymentException`, that's a separate small change.
- Logging here as well gives one failure two error records.

**2. Remove the per-attempt `log.warn`, or move it to `info`.**

- The log call sits inside the attempt loop. It is neither interval progress nor a transition record, so it breaks the one-record-per-unit rule.
- `gateway` already records each timed-out call in the `http.client.requests` timer, with `outcome` and `exception` tags. It also records a span for each call. A timeout rate and a retry rate can be read from those without this line.
- The code continues normally after a recovered attempt, so `warn` is the wrong level. It puts a condition nobody has to act on in the default production output.
- If you want one record per order for retried charges, emit a single `info` record after the loop. Give it the order id and the attempt count, and log it only when the charge succeeds after more than one attempt.
- I'd add no new counter. If someone needs "charges that succeed only after a retry", name that question where the instrument is defined and add it then.

**3. The `PaymentException` message needs work.** It goes to API clients in the 502 body, and today it reads `Payment gateway timed out 3 times for order 42`. A client holding only that text can't decide whether to wait or intervene:

- **Charge outcome:** it doesn't say whether the order was charged. A timeout doesn't prove the gateway did nothing, and a client that resubmits could charge the customer twice.
- **Why it retries:** it doesn't say the service retries a timed-out charge up to `MAX_ATTEMPTS` times.
- **Where to change it:** it doesn't name a setting. `MAX_ATTEMPTS` is a private constant, so a reader can't set it. If the gateway read timeout is a property, name it in the message with its value.
- **What to do next:** it gives no way out.

Suggested text, with the property name and way to confirm the charge filled in by whoever knows them:

```text
Charging order 42 timed out on all 3 attempts, so the gateway may have charged it. Confirm with the gateway whether order 42 was charged before you submit the charge again.
```

**4. Question on correctness, outside the instrumentation.** The call is `gateway.charge(order.id(), order.total())`, and the loop retries it after a timeout. Does the gateway deduplicate by order id? If it doesn't, retrying after a timeout can charge the customer twice. If it does, say so in a comment on the loop, because the message wording in item 3 depends on the answer.

**Checked, nothing to report:**

- **Mode:** the service has its own `main`, and the diff makes no configuration calls.
- **Span:** the diff adds no span, and the HTTP span already exists.
- **Context:** the diff starts no threads.
- **Joining id:** every record carries `order.id()`.

No reference file covered Spring `RestClient` beyond the JVM file, and `AGENTS.md` names no logging stack, so I took SLF4J and Micrometer from the PR description.
