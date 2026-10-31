**Instrumentation and error text in `PaymentService.charge`**

There are three things to change: the method logs the exhausted case and also throws it, it logs a warning on every retry, and the exception text doesn't tell the client whether the order was charged. Details below, then the full checklist.

### 1. `log.error` and `throw` on the same path

The `log.error` line records the failure, and then the method throws the same failure as `PaymentException`. The controller maps that exception to a 502, so the failure gets recorded again wherever that mapping logs it. During a gateway outage, each failed request then leaves two error records and a stack trace. Sonar reports this as S2139.

Please remove the `log.error` call. The frame that handles the exception, which is the controller's 502 mapping, should record it once with the exception object attached. Please check that the mapping does log it. If it doesn't, add the record there, not here.

One related question: can the message of `GatewayTimeoutException` or of one of its causes contain card data or customer details? If it can, recording the exception object with its stack trace needs a redaction filter in the logging configuration. Without one, record only the exception type and the order ID.

### 2. `log.warn` on each retry

This line can fire twice for every charge. It also reports something the service already records: every `gateway.charge` call shows up in `http.client.requests` with its `exception` tag, and each call has its own span. So the per-attempt timeout is already counted and already traced. A retry that later succeeds is a normal path, so a warning would also be the wrong level for it.

What no existing signal tells you is how the whole charge ended. You can't tell "succeeded on attempt 2" apart from "gave up after 3 attempts". A parent observation around the retry loop covers that case. It gives you a timer with a bounded tag set, and its span becomes the parent of the HTTP spans:

```java
  // payment.charge answers how often a charge needs a retry and how often it gives up after MAX_ATTEMPTS,
  // which decides whether MAX_ATTEMPTS or the gateway timeout needs to change.
  public PaymentResult charge(Order order) {
    Observation observation = Observation.createNotStarted("payment.charge", observationRegistry)
        .highCardinalityKeyValue("order.id", String.valueOf(order.id()));
    return observation.observe(() -> {
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
    });
  }
```

- `attempts` can only be 1, 2, or 3.
- The `error` tag, which the observation sets from the thrown exception, keeps the latency of successful charges separate from the latency of failed ones.
- `order.id` goes only on the span, never on the metric.
- The span gets its error status only when the final attempt fails, so a recovered retry doesn't mark the charge as failed.

### 3. The text of `PaymentException`

The client of this API gets the message in the 502 body. Today it reads `Payment gateway timed out 3 times for order 42`. That says what failed, but it leaves out the one thing the client has to decide: is it safe to retry?

A timeout doesn't mean the gateway rejected the charge. It may have processed the charge and then timed out on the response. Whether a retry is safe depends on whether `gateway.charge` deduplicates by order ID. That question also applies to the loop in this method, which retries right away. Which of these is true?

- **If the gateway deduplicates by order ID:**
  ```text
  Charging order 42 failed: the payment gateway timed out on all 3 attempts. The gateway deduplicates charges by
  order ID, so retrying the charge for order 42 cannot charge it twice.
  ```
- **If it doesn't:**
  ```text
  Charging order 42 failed: the payment gateway timed out on all 3 attempts, and it may still have processed one of
  them. Before retrying, check whether order 42 was charged with <the endpoint or lookup that shows it>, and retry
  only if no payment exists.
  ```
  Please replace the placeholder with the real endpoint or lookup. I don't know which one shows the payment state. If none exists, the retry loop itself can double-charge, and that's a bigger problem than the text.

Some smaller points about the text and the status code:

- Build the count from `MAX_ATTEMPTS` rather than `attempt` so the message states the limit. `MAX_ATTEMPTS` is a private constant, so the message can't name a setting that changes it. If operators are expected to tune it, add a property such as `payments.gateway.max-attempts` and name that property in the message.
- An upstream timeout is a 504, not a 502. With a 504, a client can tell "the gateway did not respond" apart from "the gateway sent a bad response".

### 4. `AGENTS.md`

It doesn't name the telemetry stack. Please add a line such as `Logging: SLF4J API; metrics: Micrometer, exported to Prometheus; traces: Micrometer Observation` in this PR so the next change doesn't have to infer the stack from imports.

### Checklist

| Item | Finding |
| --- | --- |
| Mode | None. `orders-service` is a service with its own `main`, and the diff makes no logging configuration call. |
| Signal | The exhausted case is logged and thrown on the same path (point 1). `http.client.requests` and the HTTP spans already cover the per-attempt timeout (point 2). |
| Rate | `log.warn` fires once per retry inside one charge (point 2). |
| Contents | Both records carry the order ID. The recovered-retry and gave-up states have distinct texts, but both records go away under points 1 and 2. |
| Instrument | Nothing records how a charge ended. `payment.charge` adds that with tags `attempts` (1 to 3) and `error`. |
| Span | No span in the diff. The proposed parent span sets its error status only when the last attempt fails. Exception redaction is a question for the author (point 1). |
| Library | None. Not a library, and the gateway call runs on the caller's thread with its context. |
| Level | `warn` on a path that recovers should be at most informational. It goes away under point 2 anyway. |
| Context | None. The diff starts no thread and doesn't touch MDC. |
| Caller's message | The message doesn't say whether the order may already be charged, or whether a retry is safe (point 3). |
