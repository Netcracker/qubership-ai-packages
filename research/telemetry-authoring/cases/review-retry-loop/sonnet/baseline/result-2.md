Two changes requested: remove the `log.error`, and rework the `PaymentException` message. The `log.warn` is a smaller change. I read the diff against the telemetry and wording guidelines for a JVM service.

## `log.error` before the throw

Remove the `log.error` on `PaymentService.java` (the line above `throw new PaymentException`). The exception leaves `charge`, and the controller maps it to a 502 and puts the message in the response body. The caller handles this error, so `charge` should not also log it. Logging here and throwing the same exception records the failure twice (Sonar S2139 flags this pattern). `charge` rethrows and does not handle the error.

The exception already carries the order id and the attempt count, and `e` as its cause. Whatever frame turns it into the 502 should record it once, with the stack trace.

## `log.warn` inside the retry loop

I would remove it, or replace it with one record after the loop. There are two problems:

- **It sits in a loop and fires once per attempt.** A loop within one unit of work should be counted and recorded once after it, not logged on each iteration.
- **The level is wrong.** If a later attempt succeeds, the code continues normally and nobody has to act, so `warn` pushes a harmless event into default production output. That is informational at most.

`gateway` already records every attempt in `http.client.requests`, with `outcome` and `exception` tags. Timeouts per attempt and their rate are therefore already available, and I would not add a counter or timer. Exhausted retries show up as 502s in the server-side request metrics.

What the metrics cannot tell you is which order needed a retry. If you want that, emit one `info` record after the loop, only when `attempt > 1`. It should carry the order id and the attempt count as fields, not interpolated into the text. Otherwise emit nothing.

## `PaymentException` message

The current text is `Payment gateway timed out 3 times for order 42`. This text goes to the API client, who has no source access and has to decide whether to retry. It leaves out the fact that matters most. A timeout means the gateway sent no answer, so the charge may still have been applied. A client who resubmits on a 502 could charge the customer twice.

I would write something like this:

```text
Payment gateway timed out on 3 of 3 attempts to charge order 42, so it is unknown whether the customer was charged.
Check the payment status of order 42 at the gateway before submitting the charge again, because a second charge can
duplicate the first.
```

That text still needs the following from you, since I can't see this part of the code:

- **Status lookup.** The exact command or endpoint for checking an order's payment status at the gateway. Without it, "check the status" gives the reader no way to do it.
- **Idempotency.** Whether `gateway.charge(order.id(), order.total())` is idempotent for a repeated `order.id()`. If it is, say so in the message, because then retrying is safe. If it is not, the retry loop itself can double-charge on a timeout. That is a design question for a person to settle before this merges, not only a wording one.
- **Retry limit.** The message prints the count but does not name a setting, because `MAX_ATTEMPTS` is a private constant that nobody can change at runtime. If operators should be able to change it, make it a property and name the property in the message.

## Checked, nothing else to report

- **Mode:** this is a service with its own `main`, and the diff makes no configuration calls.
- **Spans:** no new span. The HTTP call already has one.
- **Context:** no threads are started.
- **Instruments:** none added.
