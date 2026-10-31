**Instrumentation and error text in `PaymentService.charge`**

The method has two logging problems: it logs the final timeout and then throws it, and it logs every failed attempt. The exception message also doesn't tell the caller whether the order was charged. Existing signals already cover the logs, so this PR doesn't need new metrics or spans.

### Logging and throwing the same failure

```java
log.error("Charging order {} failed after {} attempts", order.id(), attempt, e);
throw new PaymentException(...);
```

This path logs the timeout and then throws it, and Sonar reports that as S2139. The controller handles `PaymentException` because it maps it to 502. So the controller's exception handler should record the failure, once, with the exception object. Then the stack trace and the trace context come with it.

As written, every failed charge produces two error records with two stack traces, and the second record comes from the handler if it logs. Please remove the `log.error` call. If the controller's handler doesn't record `PaymentException` yet, add that there instead.

### Logging every retry

```java
log.warn("Gateway timeout charging order {}, attempt {} of {}", order.id(), attempt, MAX_ATTEMPTS);
```

Please remove this line as well. Signals we already export cover what it reports:

- **How often the gateway times out:** `http.client.requests` already counts each `gateway.charge` call with its `outcome` and `exception` tags. A timeout that a retry recovers from is in that metric.
- **How often we give up:** `http.server.requests` on the charge endpoint records the 502 with `exception=PaymentException`. Your new exception message carries the attempt count to the caller.
- **What happened to one order:** each `gateway.charge` call has its own client span under the request's trace. A sampled trace shows each attempt and how long it took.

The level is also wrong for this case. After a recovered timeout the code continues normally, and nobody has to act. A warning puts the line in default production output on every slow gateway response.

### The exception message

```text
Payment gateway timed out 3 times for order 123
```

The controller returns this text to the API client, and the client has to decide whether to retry the charge. The message doesn't say whether the order was charged. A timeout doesn't mean the gateway rejected the charge, so any of the three attempts may have charged the order. The loop itself sends the same charge again after each timeout.

**I need someone who knows the gateway contract to answer this:** does the gateway deduplicate charges by order ID?

- **If it does,** retrying is safe, and the message should say so:
  `Payment gateway did not respond to 3 charge attempts for order 123. The gateway charges an order at most once, so retrying the request is safe.`
- **If it doesn't,** this loop can charge an order twice. That needs fixing before merge, apart from the wording. The message also has to tell the client that the charge may have gone through, and how to check that before retrying.

The `3` is fine to print, but nobody outside this class can change `MAX_ATTEMPTS`. Don't make the message suggest that the limit can be raised.

### Checked, nothing found

Mode (this is a service, and the PR adds no configuration calls), log volume apart from the retry line, new metrics and labels, spans, library rules, and thread context.
