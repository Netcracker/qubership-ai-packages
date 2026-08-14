# Axis: error model

Finding prefix: `ERR`.

How this code tells a caller that something went wrong, and whether the caller can act on it. For a library this is
part of the public API and changing it later is a breaking change; for a service it decides whether an incident is
five minutes or an hour.

**Check the surface packs first.** How a failure is signalled is form-specific and this file is not: HTTP status plus
a problem document, a gRPC status code, a Kubernetes condition with a `reason`, an exception hierarchy, a dead-letter
topic. `references/surfaces/<form>.md` names the convention and the normative source for the forms this repository
exposes, and its ownership table says which parts of the error surface are yours.

## Questions

**Classification.** Can a caller distinguish, from the error alone and without string matching: my input was wrong
versus the peer failed; retry will help versus retry will never help; the operation definitely did not happen versus
it may have happened. If the answer requires parsing a message, that is a finding — the message is not a contract.

**Hierarchy.** Is there one, is it shallow enough to be usable, and does each type carry the data a handler needs
(the offending value, the peer, the status code, the attempt count)? Are there types nobody can catch usefully because
everything throws the same one? Are there types so specific that a caller must enumerate twenty to be safe?

**Causes.** Is the original failure preserved and reachable, or swallowed and replaced? Look for: caught and logged
then rethrown as something new without a cause; caught and returned as a boolean or a null; caught and ignored;
`catch (Exception)` / bare `except` / `_ = err` at a boundary that hides real defects.

**Partial failure.** An operation that half-succeeded: is that a distinct outcome, or does it look like total failure?
Callers that retry a half-succeeded operation cause the interesting incidents.

**Timeouts and cancellation.** Is a timeout an error, and does it say whether the work was abandoned or is still in
flight? Is cancellation propagated, and is a cancelled operation distinguishable from a failed one?

**Retry ownership.** Who retries — this code, the caller, or both? Both is a finding: retries multiply. If this code
retries internally, is the total time bounded, is there jitter, and can the caller opt out?

**Messages.** Reason, action, consequence, in that order. The offending value or identifier must appear so it can be
grepped. Check for: the message that only restates the type; the message that dumps a raw upstream body or a stack
trace; the message that changes on every call (a timestamp, a UUID) so identical failures never look identical.

**Consistency.** Two functions in the same package that fail differently for the same reason is a finding, even if
each is defensible on its own. The caller has to learn one model, not five.

## Method

Inventory every error type, error code, and error-returning boundary in the public surface — `sb digest` plus a grep
for the language's error constructors. Then pick the six most likely real failures (peer down, peer slow, malformed
input, resource exhausted, cancelled, misconfigured) and trace each from origin to the caller, writing down exactly
what the caller receives. That table is the core of your report.
