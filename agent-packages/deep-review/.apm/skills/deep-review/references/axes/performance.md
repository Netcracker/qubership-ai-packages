# Axis: performance and scalability

Finding prefix: `PERF`.

Not micro-optimization. The question is whether the design has a scaling limit the users will hit, and whether anyone
would notice a regression before a customer did.

## What counts as a finding

- **A complexity cliff on a path that grows.** A linear scan inside a loop over the same collection, a list where a
  map belongs, a rebuild of a derived structure on every access. State the input size at which it starts to matter.
- **Allocation on the hot path** where the language makes it avoidable: per-message buffers, defensive copies of data
  that is never mutated, boxing in a tight loop, string concatenation in a formatter that is called for every event.
  Quantify — allocations per operation, not adjectives.
- **Contention.** A single lock, a single-threaded stage, or a shared counter on the path every request takes. Say
  what the ceiling is in concurrent callers.
- **Unbounded growth.** Memory that scales with something the operator does not control: number of peers, in-flight
  requests, retained history, cache with no eviction. This overlaps with `concurrency-lifecycle`; report the
  performance consequence here and cross-reference rather than duplicating.
- **Blocking where it costs a thread.** Synchronous I/O on an event loop, `Thread.sleep` in a retry, a blocking call
  inside a callback.
- **Per-call setup that should be per-instance.** Compiling a pattern, building a mapper, resolving a service, or
  reading configuration on every invocation.
- **No measurement.** No benchmarks, no load test, no regression gate in CI. For a library whose job is throughput,
  this is the top finding of the axis regardless of how fast the code currently is.

## Method

1. Find the hot paths honestly: the operations the profile says are per-message or per-request, not the ones that look
   interesting. `sb callers` on the entry points establishes what is really on the path.
2. Prefer measurement to reading. If the repository has benchmarks (JMH, `go test -bench`, `criterion`, `pytest-
   benchmark`), run them and report numbers. If it does not and one is cheap to write for the core operation, write
   it — a measured baseline is worth more to the maintainers than the finding it supports.
3. Where a profiler is available and the workload is easy to drive, profile rather than guess. Attach the top frames.
4. Distinguish "slow" from "does not scale". A constant factor is a `LOW`; a curve that bends is a `HIGH`.

## Rules

- Never report a performance finding without a magnitude: an operation count, an allocation count, a measured time, or
  an explicit complexity class. "This is inefficient" is not a finding.
- Do not propose an optimization that trades away clarity for an unmeasured gain. If you cannot say what it buys, it
  is not a finding.
