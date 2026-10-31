**Instrumentation and error text in `PaymentService.charge`**

I'd remove both log calls and reword the exception message. Details below.

### `log.error` before the throw

The `log.error` on the last attempt records the same exception that the next line throws. The controller then maps that `PaymentException` to a 502, so the exception gets handled in two places. Sonar S2139 flags this pattern. Please delete the `log.error` and record the exception once, in the handler that maps `PaymentException` to 502. Log it there with the exception object, at the level the other handlers in that class use. If that handler already logs it, you don't need to add anything.

### `log.warn` on each attempt

Each timed-out attempt is already recorded twice:

- Each attempt gets its own `http.client.requests` sample, tagged with `outcome` and `exception=GatewayTimeoutException`. That's enough to answer "how often does the gateway time out".
- Each attempt also gets its own HTTP client span under the request's trace. That's enough to answer "what happened to this order".

There's a second problem with the line itself. It's a record inside a loop over the attempts of one charge, and the code continues normally after it, so warning is the wrong level. Each timeout puts a line in the default production output that nobody can act on. If the retry then succeeds, the operator sees warnings for a charge that went through.

If someone needs to know what share of charges succeed only on a retry, or how many fail after `MAX_ATTEMPTS`, `http.client.requests` can't tell them, because it counts attempts, not charges. In that case, wrap the loop in an `Observation` named for the charge and add `attempts` as a low-cardinality key (values 1–3). Write that question in a comment where the observation is defined. That gives you one timer with an outcome per charge, plus a parent span over the retried HTTP spans. If nobody needs that answer, add nothing.

### The exception message

The 502 response body shows this text to the API client: `Payment gateway timed out 3 times for order 42`. Two changes:

1. Start with what failed. The client called a charge endpoint, so state that the charge failed and then give the reason: `Charging order 42 failed: the payment gateway timed out on all 3 attempts`.
2. Tell the client whether retrying is safe. After a timeout, the gateway may have processed the charge without responding. If `gateway.charge` is idempotent by order ID, the message can say that retrying is safe. If it isn't, retrying risks a double charge, and the loop in this method already has that risk. Does the gateway deduplicate by order ID? Your answer decides the last sentence of the message, and maybe whether this method should retry at all, so the person who owns the gateway integration should confirm it.

Here is the method with both log calls removed and the new message. It doesn't include the retry-safety sentence, which depends on the answer to the question above:

```java
  public PaymentResult charge(Order order) {
    for (int attempt = 1; ; attempt++) {
      try {
        return gateway.charge(order.id(), order.total());
      } catch (GatewayTimeoutException e) {
        if (attempt == MAX_ATTEMPTS) {
          throw new PaymentException(
              "Charging order " + order.id() + " failed: the payment gateway timed out on all "
                  + attempt + " attempts", e);
        }
      }
    }
  }
```

I found nothing to fix in these areas: configuration calls (this is a service, and the diff adds none), joining identifiers (the order ID and the trace context from the request are present), metric label cardinality, span status, and context propagation (the diff starts no threads).
