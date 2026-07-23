# API and compatibility

## Intended behavior first

Validate the intended PR behavior before evaluating compatibility impact. Anchor intent in requirements, contracts,
tests, migration guidance, and explicit user direction. Compatibility protects supported consumers; it does not
override an explicit behavior change, but the change still needs a migration path when a compatibility promise applies.

## Backend and API behavior

Check request parsing and validation for representative valid, boundary, and safely invalid inputs. Verify error
mapping across status or exit codes, response bodies, machine-readable fields, and logs. Exercise pagination cursors,
ordering, limits, partial results, and empty pages without sending stress-shaped traffic to a shared runtime.

Review timeout and retry ownership, retry safety, concurrency control, cancellation, duplicate delivery, and
idempotency. Check migrations and background jobs for ordering, partial failure, restart, observability, and safe
re-execution. Use representative requests whose size and cost stay within normal service limits. Expensive, malformed,
or disruptive cases require an isolated environment or explicit permission.

## Compatibility surfaces

Determine the supported compatibility window, then check every changed public or persisted contract that falls within
it:

- Exercise old clients against the new service and new clients against the old service when staggered rollout is
  supported.
- Preserve supported CLI flags, aliases, output contracts, and exit codes, or provide an explicit migration path.
- Compare configuration keys, types, defaults, precedence, validation, and unknown-key behavior.
- Render old deployment values against the new descriptors and check renamed, removed, and newly required values.
- Check serialized and wire formats for version negotiation, unknown fields or commands, ordering assumptions, and
  golden-fixture drift.
- Compile or execute representative consumers of changed library interfaces, including documented deprecations.
- Check data and schema migration in both clean-install and upgrade paths, including failure and safe retry behavior.
- Check rolling upgrade with mixed versions when the deployment contract permits version skew.

Record which version combinations were executed. When execution is unsafe or unavailable, identify the exact
compatibility claim supported by static contracts, fixtures, or tests and the runtime evidence that remains missing.
