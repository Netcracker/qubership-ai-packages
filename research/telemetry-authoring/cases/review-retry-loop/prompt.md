`orders-service` is a Spring Boot service with its own `main`. It logs through SLF4J (`org.slf4j.Logger`) and exports
Micrometer metrics to Prometheus. Its `AGENTS.md` says nothing about logging or metrics. The payment gateway client
`gateway` is a Spring `RestClient` with Micrometer's observation enabled, so every call to `gateway.charge` already
records the `http.client.requests` timer with `outcome` and `exception` tags, and a span for the HTTP call.

A pull request adds this method to `PaymentService`. `MAX_ATTEMPTS` is a `private static final int` equal to `3`, and
`PaymentException` is the service's own unchecked exception, which the controller maps to HTTP 502 with its message in
the response body.

```diff
+  public PaymentResult charge(Order order) {
+    for (int attempt = 1; ; attempt++) {
+      try {
+        return gateway.charge(order.id(), order.total());
+      } catch (GatewayTimeoutException e) {
+        if (attempt == MAX_ATTEMPTS) {
+          log.error("Charging order {} failed after {} attempts", order.id(), attempt, e);
+          throw new PaymentException(
+              "Payment gateway timed out " + attempt + " times for order " + order.id(), e);
+        }
+        log.warn("Gateway timeout charging order {}, attempt {} of {}", order.id(), attempt, MAX_ATTEMPTS);
+      }
+    }
+  }
```

Review the instrumentation and the error text in this diff. Your final message is the review comment to post on the pull
request.
