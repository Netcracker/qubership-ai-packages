**Review: instrumentation and error text in `PaymentService.charge`**

Three findings: drop both log calls, add the outcome to the exception message, and check whether retrying a charge is safe. I'd also add nothing new for metrics or spans.

**1. Remove `log.error` before the throw**

`log.error(...)` and `throw new PaymentException(...)` are on the same path, so one failure produces two records (Sonar S2139). `charge` doesn't handle the error. The controller does, and it maps `PaymentException` to a 502 with the message in the body. `PaymentException` already carries the order id and the cause `e`, so the controller's handler is where it should be recorded, once.

**2. Remove the `log.warn` inside the loop**

- **Wrong place:** it fires once per attempt, inside a loop that belongs to one unit of work.
- **Wrong level:** the code continues normally after it. The reader can't act on a retry that may still succeed, so a warning is too high.
- **Already recorded:** the `gateway` client's `http.client.requests` timer records every timed-out attempt with its `outcome` and `exception` tags, and each call has a span. "How often does the gateway time out" is answered there. A second signal for the same fact adds nothing.
- **Little to join on:** the line omits the cause, and `attempt 1 of 3` can't tell a retry that will succeed from one that won't.

If you want to know which orders needed a retry, emit one `info` record after a successful call with `attempt > 1`, carrying the order id and the attempt count. I'd leave it out unless someone will use it.

**3. Say what the caller can't tell from the message**

The message is `Payment gateway timed out 3 times for order 42`. It names the order and the count, but the client reading the 502 can't tell whether the order was charged. A timeout on a charge doesn't say the gateway did nothing. I suggest this wording, which also uses `MAX_ATTEMPTS` instead of the loop variable:

```java
throw new PaymentException(
    "Payment gateway timed out on all " + MAX_ATTEMPTS + " attempts to charge order "
        + order.id() + "; the gateway may have processed a charge", e);
```

**4. For a person to decide: is the retry safe?**

I can't see `gateway.charge`. As called, it takes only `order.id()` and `order.total()`. If it sends no idempotency key, retrying after a timeout can charge the customer twice. If it does send one, ignore this point. The message in finding 3 is only accurate if the key makes the retry safe or the caller is told the outcome is unknown.

**No new instruments or spans needed**
- Final failures after retries should appear as 502s in the controller's `http.server.requests` timer, if that is enabled. Please confirm it is before relying on it.
- A span around the retry loop would be valid as a parent span, but it needs a question that something will answer.

**Checked, nothing found:** mode (service code, no configuration calls), span status, context propagation, library rules, and cardinality (no new instruments).
