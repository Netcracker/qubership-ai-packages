# Axis: reliability

## Check

Timeouts, retries, recovery, failure isolation, resource cleanup, and safe operator controls. What the change logs,
measures, or traces, and the text of its errors, belong to the telemetry axis, except what a replaced mechanism prints
when it fails, which the check below compares.

For each limit the change sets or exposes, find the other limits on the same work in the caller or the wrapper, in what
the code starts, and in the environment; a limit on one operation inside that work, or on work that only overlaps it,
does not count, and an enclosing limit that starts earlier does, with the time spent before this work starts taken from
its budget. Raise each documented setting just past each other limit, not only at its default, and flag one that a limit
fixed elsewhere caps, and an inner limit that does not fire first at the defaults. For a limit in a program outside the
repository, ask for the line that sets it or a run that reaches it.

Where the change replaces a mechanism (a build target, a wait, a client, a deployment step), take the fault the old one
met most often, which its error handling or the CI history shows, and, where the new one waits in a loop, the fault on
which one attempt waits longest. For each, say from both versions of the code how long each takes to fail and what each
prints. On the second fault, count each attempt at its call's own timeout, the default its help text or source states
where nothing sets one, and a call with no timeout as never returning. Count a deadline checked before each attempt as
overrun by up to one attempt and one sleep. A replacement that fails later or prints less is a finding unless the change
accepts the slower or quieter failure in writing. Ask for a run of that fault on the new mechanism, with its duration
and output. For a later failure, also ask for a deadline that bounds the whole wait, last attempt included, at the old
mechanism's time to fail; for a quieter one, the old output.

## Severity

A replacement whose new time to fail reaches a limit that encloses it, such as the CI job's timeout, or whose wait
nothing bounds, is `major`.
