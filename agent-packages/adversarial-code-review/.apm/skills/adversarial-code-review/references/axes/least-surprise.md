# Axis: least surprise

Would a user or caller who knows the previous version, or the convention of the ecosystem, be surprised by what the
change does?

## Check

- A new behavior that differs from the closest existing one without saying why: a sibling option, method, or diagnostic
  that handles the same case another way.
- A new option whose default is not what most users want.
- A behavior that depends on something the user does not see or set: the order of declarations, a file's location, an
  unrelated option.
- Asymmetry in new behavior: the change handles one direction, one overload, or one syntax form and not its twin, with
  nothing saying the other is intended. A path a fix leaves out belongs to correctness.

Write each as the input, what a user would expect, and what happens. The expectation must come from somewhere a reader
can check: the previous version, a sibling feature, the documentation, the specification, a common convention.

Changed defaults and new errors on input that used to pass belong to compatibility.

## Not a finding

A surprise the description announces and justifies. A behavior that matches the specification the project implements,
even if a user might expect otherwise; then the finding, if any, is missing documentation.

## Severity

An unexplained asymmetry is `minor`.
