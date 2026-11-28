# Axis: performance

## Check

N+1 access, unbounded fetches, blocking work on concurrent paths, hot-path I/O and allocation. A linear scan inside a
loop over the same collection, and a recursion that revisits the same subtree or type, are quadratic or exponential:
give the input size at which it matters.

## Not a finding

A cost with no realistic input that reaches it. State the input shape and size, or drop it.

## Severity

Super-linear work on input a user controls or a real codebase contains is `major`.
