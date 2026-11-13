# Axis: architecture

Is the change at the right layer, and does it reuse what the repository and its dependencies already provide?

## Check

- **Layer.** Is the behavior implemented in the module that owns the concept, or bolted onto a caller, a shared utility,
  or a special case in a generic path? Would a fix one layer down remove the need for this one?
- **Existing helpers.** For every helper, utility, or non-trivial computation the change adds, search the repository and
  its declared dependencies (the language's standard library, the frameworks in the build file) for one that already
  does it. Name the existing one by its full name.
- A refactor must reduce the number of concepts or branches a reader tracks, not merely move them.

Repeated conditionals, feature logic in shared modules, gratuitous casts or fallbacks, and growth of an already-large
file are inspection signals, not automatic findings. For each structural defect that creates a demonstrated failure or a
bounded maintainability cost, propose the smallest move that removes complexity rather than redistributing it.

Duplication within the change, code that can be removed, and a simpler approach to the same behavior belong to the
simplicity axis; do not repeat them here.

## Severity

A reimplemented helper that already diverges from the original, or a fix at a layer that leaves the same defect
reachable elsewhere, is `major`. A real but undemonstrated maintainability benefit is `minor` or `nit`.
