# UI and user surfaces

## Baseline smoke

Run baseline smoke before feature-specific checks for every changed user-reachable surface. Use an available capability
that exercises the real interface; no particular browser or automation product is required.

- UI: open the normal entry point and a changed deep link, reload each route, and inspect console and network activity.
- API: prove reachability or startup, check health when exposed, send a representative valid request, and inspect the
  error format with a safe invalid request.
- CLI: invoke the executable, read help, run a representative command, and verify output and exit code.
- Library: import or link it from a minimal consumer, exercise changed behavior, and check the supported compatibility
  boundary.
- Deployment: render or install through the repository's normal path, then verify startup, readiness, and configured
  external entry points.

When a surface cannot be executed, retain its coverage row and record the strongest safe substitute, missing evidence,
and impact.

## UI behavior

Exercise the changed workflow from both its normal entry point and a direct deep link. Check back and forward
navigation, reload, and state restoration where the product promises them. Inspect browser console errors, page errors,
failed requests, unexpected retries, and duplicate or expensive network calls.

Cover keyboard operation, focus order and visibility, accessible names, semantic roles, labels, error association, and
obvious contrast or scaling failures. Distinguish a standards violation from a tool-specific best-practice warning.
Check responsive behavior at representative narrow and wide layouts without assuming a specific device list.

Exercise loading, empty, partial, success, and error states that the changed flow can reach safely. Check that recovery
actions work and that stale or partial data is not presented as a completed result.

## Evidence

A screenshot proves visible state only. Support network, console, keyboard, accessibility, navigation, and application
state claims with matching evidence such as request records, console output, DOM or accessibility inspection, recorded
actions, or deterministic executable checks. Record the entry point, action, observed result, and relevant artifact for
each retained candidate.
