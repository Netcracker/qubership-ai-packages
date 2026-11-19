# Axis: intent and scope

Does the change solve the stated problem, and only that? Read the description, the linked issue, and the commit messages
in `input.md` as the claim, and the diff as what was done.

## Check

- The change solves the stated problem: the symptom the issue describes no longer happens on the path it names, and the
  fix reaches the cause rather than making the symptom rarer.
- No missing consumer of a new API or option, no accidental generated output, no refactoring mixed with separable
  feature work.
- A hunk that changes behavior, a version, or a dependency beyond what the claimed change needs is a finding however
  small, where no sentence of the description or a commit message claims it: a version bump carried over from another
  branch, a dependency moved in a file the change otherwise leaves alone. The tests of a claimed change, and the
  generated or lock output it produces, are claimed with it. Ask for a sentence that claims it, with the run that checks
  it, or for the hunk to move to its own change.
- Where the change fixes or extends a behavior, the cases next to it: the same input on a path that shares the changed
  code or that the change's claim names, and the changed code meeting a configuration, a state, or a caller it did not
  consider. Record such a case whether or not it failed before the change, and say in `evidence` whether the
  description, a commit message, or the linked issue claims it: the verifier decides from that whether the author
  handles it here or a follow-up issue does.

## Not a finding

A hunk outside the claimed scope that changes no behavior, such as a fixed typo, needs no claim, and the review does not
mention it.

## Severity

An unclaimed hunk that changes runtime behavior or a dependency version is `major`. A fix that does not reach the stated
problem is `major`.
