# Axis: architecture

Is the change at the right layer, does it reuse what the repository and its dependencies already provide, and does it
compute each property it depends on rather than list the inputs it has met?

## Check

- **Layer.** Is the behavior implemented in the module that owns the concept, or bolted onto a caller, a shared utility,
  or a special case in a generic path? Would a fix one layer down remove the need for this one?
- **Existing helpers.** For every helper, utility, or non-trivial computation the change adds, search the repository and
  its declared dependencies (the language's standard library, the frameworks in the build file) for one that already
  does it. Name the existing one by its full name.
- **A case list in place of a computed property.** Where the change decides a property of its input (whether a value
  may be null, whether a caller holds a lock, whether a path stays inside a root) by listing the input's shapes, such as
  a chain of type tests on syntax nodes, a list of exemptions, or a walk that stops at hard-coded kinds of node, state
  the property in one sentence. Then try the neighbors of the listed shapes: the same input one level deeper, passed
  through a generic call or a wrapper, reached through a subtype or an inherited member, or combined with another listed
  shape. A neighbor that gets a different answer than the property gives is a failure of the list, and two or more show
  that the list approximates a property the code does not compute.
- **The fixes so far.** Where `input.md` names `families.json`, read every family whose `sites` the change touches. For
  a `recurring` family, or one whose latest fix is `adds_case`, try the neighbors of the inputs that fix named, as
  above: the family's next member is usually one of them.
- A refactor must reduce the number of concepts or branches a reader tracks, not merely move them.

Repeated conditionals, feature logic in shared modules, gratuitous casts or fallbacks, and growth of an already-large
file are inspection signals, not automatic findings. For each structural defect that creates a demonstrated failure or a
bounded maintainability cost, propose the smallest move that removes complexity rather than redistributing it.

A finding about a case list names, in `evidence`, the property, the sites that list cases, the failing neighbors, and
the family where `families.json` has one. Its `proposed_solution` is one of two outcomes, as `proposed_solution` in
`finding-rules.md` defines them: compute the property in the one place that owns it, saying what that place computes in
place of the list; or, where that is larger than the change, remove from the change every decision that depends on the
property, and leave the property to a change of its own. Another case is at most a stopgap, offered only where no
fix in the family added one; for a `recurring` family the outcome is never a rewrite of the walk at the family's
`sites`.

Duplication within the change, code that can be removed, and a simpler approach to the same behavior belong to the
simplicity axis, and a single failing input with no list behind it to the correctness axis; do not repeat them here.

## Severity

A reimplemented helper that already diverges from the original, or a fix at a layer that leaves the same defect
reachable elsewhere, is `major`. A case list with two or more failing neighbors, or a `recurring` family with a failing
neighbor, is `major` where a neighbor gives a wrong result, and one step above the neighbors' own severity where they
give a worse message or a missing detail. A case list with one failing neighbor takes that neighbor's severity. A real
but undemonstrated maintainability benefit is `minor` or `nit`.
