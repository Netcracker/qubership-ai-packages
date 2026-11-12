**Log and rethrow on the last attempt**

On the last attempt, the code logs the failure with `log.error` and then throws `PaymentException` with the same exception as its cause. The frame that handles the exception will usually record it again, so the failure appears twice. Sonar S2139 reports this pattern. That frame is the exception handler that maps `PaymentException` to 502. Please remove the `log.error` here. If the handler doesn't record `PaymentException` yet, add one record there and pass the exception object, so the record keeps the trace id.

**The warning on each attempt**

`log.warn` fires on every timed-out attempt inside one charge, and the code carries on normally after it. That puts a timeout the retry recovers from into the default production output, where nobody has to act. The per-attempt facts are already recorded. Every `gateway.charge` call records `http.client.requests` with `outcome` and `exception` tags, and each call has its own span in the request's trace. Please remove this line too.

**What's missing: one signal for the whole charge**

Neither of the existing signals answers questions about the whole charge. How many charges needed a retry? How many gave up after `MAX_ATTEMPTS` timeouts? How long does a charge take, retries included? An observation around the loop answers all three. The client calls are already observed, so this one fits the existing setup:

```java
public PaymentResult charge(Order order) {
  // payment.charge counts the charges that needed a retry and the ones that gave up after MAX_ATTEMPTS timeouts.
  Observation observation = Observation.createNotStarted("payment.charge", observationRegistry)
      .highCardinalityKeyValue("order.id", String.valueOf(order.id()));
  return observation.observe(() -> chargeWithRetries(order, observation));
}

private PaymentResult chargeWithRetries(Order order, Observation observation) {
  for (int attempt = 1; ; attempt++) {
    observation.lowCardinalityKeyValue("attempts", Integer.toString(attempt));
    try {
      return gateway.charge(order.id(), order.total());
    } catch (GatewayTimeoutException e) {
      if (attempt == MAX_ATTEMPTS) {
        throw new PaymentException(/* see below */, e);
      }
    }
  }
}
```

What this gives you:

- **A timer with bounded tags.** `payment.charge` gets `attempts` (values 1 to 3) and `error` (`none`, or the exception's class name). Failure rate and success-only latency both come from that one timer.
- **A consistent tag set.** The code sets `attempts` at the top of each iteration, so every path has it, including an exception other than a timeout. The Prometheus registry rejects a meter name whose tag keys differ between recordings.
- **`order.id` on the span only.** As a high-cardinality key, it goes on the span and not on the timer.
- **A parent span for the gateway calls.** `observe()` opens a scope, so the gateway call spans become its children. It marks the span as an error only when the exception leaves the loop, so an attempt the retry recovers from doesn't turn the charge red.

**The `PaymentException` message**

This text becomes the 502 response body. Whoever reads it has no access to the source and has one decision to make: retry, or not. `Payment gateway timed out 3 times for order 123` states what failed, but it doesn't say whether the order was charged, and a timeout doesn't tell the service that either.

Is `gateway.charge` idempotent on `order.id()`? The answer decides the message, and it also decides whether this loop is safe at all:

- **If the gateway charges an order at most once:**
  `Charging order 123 failed: the payment gateway timed out on all 3 attempts. Retrying is safe, because the gateway charges an order at most once.`
- **If it isn't idempotent:** the loop itself can charge the order twice, and that needs fixing before the wording does. The message then has to say that the outcome is unknown and how to check it, with the order id filled in:
  `Charging order 123 failed: the payment gateway timed out on all 3 attempts, and it may still have charged the order. Check the payment status with <endpoint or command> before you retry.`
  I don't know which endpoint or command shows the payment status. Please put the real one in the message.

Don't offer raising `MAX_ATTEMPTS` as a fix in the message: it's a private constant that no caller can set.

**`AGENTS.md`**

`AGENTS.md` doesn't name the logging and metrics stack. I suggest adding this line in this PR: `Logging: SLF4J API. Metrics and traces: Micrometer Observation, metrics exported to Prometheus.`

**Checklist**

- Mode: none. This is a service with its own `main`, and the diff makes no logging configuration call.
- Signal: `log.error` before the throw, and `log.warn` already covered by `http.client.requests` and the client spans. Both are covered above.
- Rate: `log.warn` fires once per attempt inside one charge. Covered above.
- Contents: none. Both lines carry `order.id()`, and Spring Boot's tracing puts the trace id in the MDC. Both lines go away anyway.
- Instrument: no signal covers the whole charge yet. The `payment.charge` observation above fixes that. `MAX_ATTEMPTS` controls the retries, not whether anything is emitted.
- Span: the exception is recorded on the frame that rethrows it, covered above. When the handler records it, check that the `GatewayTimeoutException` message can't include the request body or card data, because the cause's message is part of that record.
- Library: none. This is a service, not a library.
- Level: the `warn` is for a condition the retry recovers from (remove it). The `error` is on a frame that rethrows (move it to the handler).
- Context: none. The loop runs on the caller's thread, and `observe()` restores the previous scope when it exits.
- Caller's message: it doesn't say whether the order was charged or whether retrying is safe. Covered above, and it depends on the idempotency question.
