# Axis: correctness

Does the code do what its contract and its tests say, on every path?

## Check

Trace every path the change reaches, failure and concurrent ones included, against the contract.

Where the change fixes a symptom, check the other paths that show the same symptom, which a search for the changed
helper does not find: a twin build target, the other major version of a tool, the other operating system, the sibling
overload or visitor method that handles the same construct. A path the fix leaves out is a finding.

Where you can run the code cheaply (a unit test, a compiler on a snippet), do it and record the command and its output
as a `fact`; a trace through the code is an `inference` until run. Where `<work>/measure/` holds a diff coverage report,
trace every changed branch it lists as unexecuted by hand: no test the tools ran has run it.

## Severity

A path the fix leaves out is `major` when it shows the same symptom the change claims to fix.
