# Axis: simplicity

Could the change reach the same behavior with less code?

## Check

- **A simpler approach.** State in one sentence what the change has to achieve, then look for a shorter route to it: an
  existing mechanism the change could extend instead of adding a parallel one, a data structure that makes a branch
  unnecessary, a narrower change that handles the same cases. Name the alternative concretely enough for the author to
  judge it: the code it touches and the added code it removes. An alternative that drops a case the change handles is
  not simpler. Where the description already rejects this alternative with a reason, the finding answers that reason.
- **Duplication.** Blocks the change adds that repeat each other, or repeat code the change touches, and differ only in
  a value or a type. Name both places and the parameter that would merge them.
- **Code that can go.** A parameter every caller passes the same value to, a branch no input reaches, a check for a
  state the caller's contract already excludes, a wrapper that only forwards, a member nothing uses. Show why it can go:
  the callers, the contract, or the search that found no use. This applies only where every caller is in the repository:
  a member of the public API, or a check at a trust boundary or a public entry point, stays.

The layer the change sits at, and a reimplementation of a helper the repository or its dependencies already have, belong
to the architecture axis; do not repeat them here.

## Not a finding

A shorter form of the same logic that is no easier to read. Two or three repeated lines whose merged form needs a
parameter the reader must trace.

## Severity

A simpler approach is `major` where the finding shows that it handles every case the change handles and removes most of
the added code, and the description gives no reason against it; otherwise it is `minor`. Duplication and removable code
are `minor`. Copies that already differ in a way that is a bug are a correctness finding.
