# Axis: correctness

Finding prefix: `CORR`.

The general adversarial pass: defects that make the code do the wrong thing. Everything the specialized axes own —
concurrency, error semantics, protocol conformance, compatibility — belongs to them. What is left is still the largest
axis: state machines, boundary conditions, data mapping, algorithmic logic, and the paths nobody exercises.

## Where to spend the budget

- **State machines.** Draw each one: states, triggers, transitions, terminal states, and what happens on a trigger
  that no transition covers. Defects hide in the transitions nobody drew.
- **Idempotency and restart.** For every operation with an external effect, ask what a duplicate delivery does, and
  what a process kill between step N and step N+1 leaves behind. Then ask what recovers it.
- **Boundaries.** Empty, one, many, maximum. Zero-length input, single-element collection, exactly-at-the-limit,
  one-over. Off-by-one in offsets, lengths, and slice bounds.
- **Data mapping.** Every conversion between representations: types that do not round-trip, precision loss (integers
  through floating point, timestamps through seconds), null versus absent versus empty, case and Unicode
  normalization, ordering assumptions between an ordered and an unordered container, key collisions when two
  namespaces are flattened into one map.
- **Arithmetic.** Overflow, unsigned wraparound, division by a value that can be zero, duration arithmetic across
  units, and any place a signed and an unsigned quantity meet.
- **Partial application.** An operation that touches three things and fails at the second: what is the state
  afterwards, and does anything know?
- **Dead and unreachable branches.** A branch that cannot be taken usually means a condition elsewhere is wrong.

## Method

1. Read the profile and the `tests` report first. Start with the areas the suite is blind to — that is where defects
   survive.
2. Pick the five or six most load-bearing units by fan-in (`sb callers`, `sb impact`) and read them completely, not by
   sampling.
3. Generate adversarial inputs before reading the implementation of a function, so its code does not anchor you on
   what it handles.
4. Where the repository builds, write the throwaway test. A reproduction is the difference between a finding that
   gets fixed and one that gets argued about, and it is the only thing that lets the verifier mark the finding
   `CONFIRMED` — report it as `method: executed` with the command and its decisive output.

## Out of scope for this axis

Thread-safety and lifecycle (`concurrency-lifecycle`), exception hierarchy and retry signaling (`error-model`),
wire-format conformance (`protocol-conformance`), anything that is a design decision rather than a defect
(`architecture`). Note them in *Cross-axis notes* and move on.
