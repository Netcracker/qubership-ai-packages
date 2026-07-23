# UI and user surfaces

## Baseline smoke

Create required evidence slots before asking for execution permission. Use an approved implementation that exercises
the real interface; no browser or automation product is universally required.

- Web UI: normal entry point, changed workflow or deep link, reload, console, and network.
- API: reachability or startup, health when exposed, representative valid request, and safe invalid request.
- CLI: executable invocation, help, representative command, output, and exit code.
- Library: import or link from a minimal consumer, changed behavior, and supported compatibility boundary.
- Deployment: repository-native render or install, startup, readiness, and configured external entry points.

When access or execution is denied, retain the slots and record the missing evidence and impact.

## Web UI evidence slots

For a changed web UI, create these required slots:

- `entry-wide`: normal entry point at a representative wide viewport;
- `changed-wide`: changed workflow or deep link at a representative wide viewport;
- `entry-narrow`: normal entry point at a representative narrow viewport;
- `changed-narrow`: changed workflow or deep link at a representative narrow viewport;
- `console`: console and page-error summary;
- `network`: request, failure, retry, and duplicate-call summary;
- `accessibility`: DOM or accessibility snapshot, names, roles, labels, focus, and obvious contrast or scaling issues;
  and
- `keyboard`: recorded keyboard path, focus order, focus visibility, and result.

Each visual slot retains a screenshot, URL, viewport, actions, and observed result. Additional screenshots support
visual findings. Use `not_applicable` only when an observable product property removes a slot, such as a surface with
no distinct deep link; record that property as the reason. `Screenshot not captured` is not a reason.

Save screenshots directly under the review package. If an adapter writes only to an ephemeral location, copy and
validate the file immediately before continuing. A screenshot left under `/tmp` does not satisfy a slot.

## Approved fallback loop

Try implementations in the recorded order, commonly:

1. repository-native E2E or browser harness;
2. approved browser MCP or harness adapter;
3. approved installed browser automation framework; and
4. another approved browser adapter.

This is a fallback order, not a requirement to run every implementation. If one fails, record the adapter failure and
use the next approved candidate. Return to the access-permission gate before using a candidate that the user did not
approve. Mark browser evidence unavailable only after all approved candidates fail.

## Interaction coverage

Exercise the changed workflow from its normal entry point and direct link. Check back and forward navigation, reload,
and promised state restoration. Exercise loading, empty, partial, success, error, and recovery states that are safe
under the permission and action budgets.

Support console, network, keyboard, accessibility, navigation, and state claims with their matching evidence. A
screenshot proves visible state only. Record the entry point, action, observed result, and artifact for every retained
candidate and meaningful negative result.
