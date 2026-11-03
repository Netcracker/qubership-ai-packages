**Review: instrumentation and error text in `PaymentService.charge`**

I'd remove both log calls and change the exception message.

**1. Remove the `log.error` before the `throw`.**
- The same failure goes to the caller twice. `PaymentException` reaches the controller, which maps it to a 502, and `log.error` also records it with the full stack trace. Sonar S2139 reports this pattern.
- `charge` only rethrows. It is not the frame that handles the error, so it should record nothing.
- If the controller's exception handler doesn't already log `PaymentException` with the exception object, that handler is where the single record belongs. I couldn't see it from this diff.

**2. Remove the per-attempt `log.warn`.**
- `gateway` is a `RestClient` with observation enabled, so every attempt already appears in `http.client.requests` (with the `outcome` and `exception` tags) and gets its own HTTP span. The warning adds nothing the aggregate or the trace lacks.
- It sits inside a retry loop and fires once per attempt. Records for work inside one unit belong after the loop, not in it.
- The level is wrong anyway. The code continues normally after a timeout, and nobody has to act on it, so it would be info at most.
- I don't think this change needs a new counter or span. Add one only if someone has a question the existing timer can't answer, for example how often a charge needs a retry. The retry loop would then be a legitimate parent span.

**3. The exception text leaves out the charge state.**
- `Payment gateway timed out 3 times for order 42` names the failure and the order, but it doesn't say whether the order was charged.
- A timeout on a charge call doesn't tell you whether the gateway processed it. The reader of the 502 body (an API client or an on-call engineer) has to decide whether to retry. They can't decide that from this text.
- Suggested text. Replace the last sentence with whatever check the team actually has for payment status:

```java
  public PaymentResult charge(Order order) {
    for (int attempt = 1; ; attempt++) {
      try {
        return gateway.charge(order.id(), order.total());
      } catch (GatewayTimeoutException e) {
        if (attempt == MAX_ATTEMPTS) {
          throw new PaymentException(
              "Charging order " + order.id() + " failed: the payment gateway timed out on all "
                  + MAX_ATTEMPTS + " attempts. The gateway may have processed a charge, so check "
                  + "the payment status of the order before charging it again.", e);
        }
      }
    }
  }
```

**Question for you (needs a person):** does the gateway deduplicate `charge` calls by `order.id()`, or does it take an idempotency key? If it doesn't, retrying after a timeout can charge the customer twice. The loop is then a correctness problem, not a telemetry one.

Checked with nothing found: mode (no logging configuration call), new instruments, new spans, thread context.
