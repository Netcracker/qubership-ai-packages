# Axis: concurrency and resource lifecycle

Finding prefix: `CONC`.

Two subjects that share a root cause: something is used after its owner stopped guaranteeing it. For a transport or
connection library this is usually the axis with the most severe findings.

## Concurrency

- **State the model, then check it.** For every public type: is it thread-safe, and where is that documented? An
  undocumented threading contract is a finding on its own — callers will guess, and half will guess wrong.
- **Shared mutable state.** Every field reachable from two threads: what guards it? Look for the partial cases — a
  guarded write with an unguarded read, a lock held for one field of an invariant that spans two, a `volatile` /
  atomic that makes a single access safe but not a check-then-act.
- **Check-then-act.** `if (map.get(k) == null) map.put(k, v)`, lazy initialization, "is it still open" followed by a
  use. These are the most common real races.
- **Lock ordering.** Two locks acquired in different orders on two paths is a deadlock, however unlikely. List every
  path that holds more than one lock.
- **Blocking under a lock.** I/O, a `get()` on a future, or a callback invoked while holding a lock. Callbacks
  invoked under a lock are a design defect: the caller's code can now deadlock you.
- **Executors and threads.** Who creates them, who owns them, who shuts them down, and what happens to queued work at
  shutdown. Unbounded queues, unbounded thread creation, and `newFixedThreadPool` sized by a constant that assumes a
  machine size are all findings.
- **Callback and listener threads.** Which thread runs user code, is it documented, and can slow user code stall the
  I/O loop?
- **Async composition.** Futures that drop exceptions, `whenComplete` without a return, unhandled rejection,
  a `CompletableFuture` completed twice, a callback that can fire after cancellation.

## Lifecycle

- **Ownership.** For every resource — socket, channel, file, buffer, thread, timer, subscription, native handle —
  name the owner and the point of release. A resource with two owners or none is a finding.
- **Close semantics.** Is `close()` idempotent, is it safe to call concurrently with use, does it wait or abandon,
  does it release everything on the failure path? What does a use-after-close do: a clear error, a hang, or undefined
  behavior?
- **Construction failure.** A constructor or factory that fails halfway: what leaks?
- **Leaks under stress.** Retry loops that create a new connection each attempt, caches with no eviction, maps keyed
  by a request id with no removal on the failure path, listeners registered and never removed.
- **Backpressure.** When the peer is slower than the producer, what grows? Find the unbounded queue, the unbounded
  buffer, or the unbounded in-flight map — there is almost always one.
- **Timeouts.** Every blocking operation should have one. List the ones that do not, and say what an unresponsive peer
  does to the caller.

## Method

Run the race detector or the concurrency lint the ecosystem provides (`go test -race`, `-Djava.util.concurrent`
stress tests, ThreadSanitizer, Loom-based tests) and report both what it found and what it cannot reach. A quiet race
detector proves the tests did not exercise the path, not that the path is safe — say which it was.

Where a race is plausible but unproven, write the stress test. A hundred iterations with a barrier is usually enough
to make it reproduce, which turns a `traced` finding into an `executed` one — and that is what the verifier needs
before it can call the finding `CONFIRMED`.
