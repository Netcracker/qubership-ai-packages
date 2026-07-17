# Runtime and environment

## Capability definitions

- Tool: an external program or service used to perform a check.
- Project dependency: a dependency installed through the repository's normal setup or build process.
- Runtime access: access to an existing application, cluster, virtual machine, namespace, or remote environment.
- Adapter or binding: the interface used to call a capability implementation.

Derive capabilities from required coverage. A named tool is one possible implementation, not the capability itself.

## Discovery order

For each required capability, check these sources in order and record the selected implementation:

1. Repository-native commands, setup paths, dependencies, test harnesses, and documented workflows.
2. Harness-native tools, services, adapters, and bindings.
3. Existing local or remote runtime access, including URLs, credentials, logs, and metrics.
4. Reasonable alternative tools, adapters, or bindings visible in the environment.

Do not perform an unbounded search. Do not declare a capability unavailable because one familiar tool is absent. For
example, a harness-native remote browser can implement browser interaction when Playwright and local browser binaries
are absent.

## User question gate

Ask one bounded user question only when missing evidence materially changes a required track or explicit focus area.
First state the evidence the capability or decision unlocks, repository-native and reasonable visible alternatives,
side effects, scope, and coverage impact.

Group related choices into one question. Keep the affected track `blocked` until the user approves, declines, or an
approved setup fails with recorded evidence. Continue independent safe tracks when the harness can receive the answer
in the same turn. Otherwise save a preliminary report and return the question.

Do not ask for a runtime when the target has no runtime-dependent track. Do not ask to install a familiar tool when an
available implementation already provides the required evidence.

## Runtime alignment strategies

Prove alignment with the complete `head_oid` using the strongest available evidence: build metadata, image digest,
chart or application version, container labels, rendered values, process command line, a version endpoint, or
deployment timestamps.

Choose one strategy for each runtime-dependent track:

- Use an aligned runtime without changes.
- Update through the repository's documented path when the runtime is stale and the user permits the effects.
- Use an isolated disposable deployment for destructive, disruptive, or state-sensitive checks.
- Limit evidence and mark the track `partial` or `skipped` when alignment or permission is unavailable.

Do not use an unaligned or unproven runtime as regression evidence. Runtime-dependent delegation waits until strategy,
permissions, execution, and version proof are resolved. Independent static-ready tracks may start earlier.

## In-place update and clean deployment

When a stale runtime contains important state, compare both strategies before asking the user:

- In-place update preserves state but may trigger migrations, cleanup, recovery, retries, or background jobs. It can
  hide clean-install and setup defects and needs a verified snapshot and rollback plan when state is at risk.
- Clean deployment tests setup from scratch and isolates existing state, but it may require copied fixtures, new
  resources, more time, and explicit cleanup. Never remove or replace shared state without permission.

Ask one strategy question that names the target environment, changed layers, expected state effects, snapshot or copy
plan, rollback and cleanup, and evidence each choice produces. Do not perform either strategy before approval when its
effects exceed existing permission.

## Changed deployment layers

Alignment covers every changed layer that affects deployed behavior: application artifacts, configuration, deployment
descriptors, migrations, generated assets, and relevant external dependency versions or contracts. Record proof for
each layer. Treat a layer that cannot be aligned as an explicit coverage limitation.

## Direct and indirect mutations

Direct mutations include source edits, dependency or tool installation, service startup or restart, deployment
changes, cluster writes, and test-data changes. Material indirect mutations include actions that can trigger migrations,
recovery, cleanup, compaction, retention, lifecycle transitions, uploads, retries, background jobs, persistent cache or
index rebuilds, shared-state changes, or irreversible effects.

Require permission for the affected action and environment unless the user already granted it. State expected impact,
commands or action types, rollback or cleanup, and evidence unlocked. After setup, declare when the review returns to
read-only mode. Record actual mutations, side effects, failed attempts, and cleanup.

Normal local build caches, temporary files, report artifacts, and safe read-only requests do not need an extra gate
unless repository instructions say otherwise.

## Safe degradation

When the user declines, setup fails, credentials are unavailable, or mutation is forbidden, use the strongest safe
evidence that remains: exact static analysis, tests, executable examples, fixtures, rendered manifests, logs, metrics,
API calls, or safe object counts. Never describe static evidence as an observed runtime result.

Set the affected row to `partial` or `skipped` and record the missing evidence and impact. Capability, runtime, or agent
unavailability never removes a required track; assign safe work to another implementation or the main thread.
