# Change analysis and coverage

## Exact target

Use the local exact diff between the complete `base_oid` and `head_oid` as the source of truth. Preserve complete OIDs
in every working record and handoff. Confirm that remote target metadata names the same revisions, but treat remote
file summaries as discovery aids because they may be truncated.

For a patch or uncommitted work, record the repository root, scope, initial status, and a patch identity or checksum
when practical.

## Diff classification

Classify changed files and behavior against these track triggers:

- Requirements and design: specifications, ADRs, issue acceptance criteria, behavior docs, screen designs, or a diff
  whose intended behavior is otherwise ambiguous.
- Backend and API: server logic, requests, responses, validation, error mapping, background processing, concurrency,
  or an API contract.
- UI and user surfaces: screens, routes, navigation, CLI commands, output, downloadable content, or other
  user-reachable behavior.
- Runtime and observability: service lifecycle, health, readiness, logging, metrics, events, retries, or operational
  failure behavior.
- Deployment and configuration: charts, manifests, images, generated assets, migrations, routes, secrets, defaults,
  values, or environment configuration.
- Documentation and tests: behavior documentation, migration guidance, examples, fixtures, or tests that changed or
  should change with the implementation.
- Security: trust boundaries, authentication, authorization, exposure, untrusted input, secrets, dependencies,
  images, downloads, or resource limits.
- Protocol compatibility: wire formats, parsers, decoders, frames, commands, acknowledgements, reconnect behavior,
  agents, ingest, or protocol documents.
- Data lifecycle: migrations, storage formats, WAL or manifests, retention, TTL, cleanup, compaction, upload, deletion,
  hot or cold reads, recovery, or late arrivals.
- Backward compatibility: any public or persisted API, CLI, configuration, deployment, storage, library, upgrade,
  rolling-deployment, migration, or documented legacy contract.

One changed area may trigger several tracks. Intended PR behavior remains the primary requirement; compatibility checks
determine whether existing consumers still work or have an explicit migration path.

## Required-by-diff coverage

Create a row for every triggered track before deep checks. Each row contains track, reason, required capability,
implementation, owner, planned evidence, status, and impact. Add user focus areas as rows or explicit priorities, but
do not remove diff-triggered rows.

Use these working statuses: `planned`, `ready`, `in progress`, `complete`, `partial`, `skipped`, and `blocked`. A track
becomes `ready` only when its target, inputs, capability implementation, permissions, and runtime decision are ready.
At completion, every required row must be `complete`, `partial`, or `skipped`, with impact recorded.

## Baseline smoke selection

Add a smoke check for each changed user-reachable surface before feature-specific checks:

- UI: normal entry point, deep link, reload, console, and network.
- API: startup or reachability, health, a representative valid request, and error format.
- CLI: invocation, help, representative command, output, and exit code.
- Library: import or link, minimal consumer, changed behavior, and compatibility.
- Deployment: render or install, startup, readiness, and configured external entry points.

Use the repository's normal entry point when documentation is absent, and record the documentation gap separately.
Do not invent a runtime requirement for a library when build, tests, and an executable minimal consumer provide the
required evidence.

## Requirements and old behavior

Anchor expected behavior in the PR requirements, specifications, contracts, tests, migration guidance, and explicit
user direction. Inspect the base revision and existing consumers for compatibility and regression context. Record
assumptions that need confirmation.

Validate intended new behavior before or alongside compatibility. Old behavior cannot override an explicit new
requirement, but a promised compatibility window requires preservation, an adapter, or a documented migration path.

## Candidate reconciliation

For each candidate, record source, decision, confidence, and evidence. Challenge it against requirements, contracts,
base behavior, tests, ADRs, documented limitations, accepted risks, and contradictory evidence. Merge duplicates and
split claims that can be fixed or retested independently.

Only `Confirmed` and `Strong static evidence` candidates enter main findings. Keep `Suspected` candidates in
follow-ups or limitations when useful. Preserve rejected or merged candidates when their decision prevents repeated
work.

## Previous-run reconciliation

When prior findings or checks are available, mark each one as reproduced, not reproduced, superseded, accepted or out
of scope, or not rechecked with the blocking constraint. Never silently drop a prior item or infer that an unexecuted
check is fixed.

## Final target delta

Re-resolve the target head before report completion. If it differs from the initial complete `head_oid`, record the new
complete OID and compute the exact delta. Add or reopen affected coverage rows and rerun checks when feasible. If the
delta cannot be reviewed, mark the report stale or preliminary and show both complete head OIDs.
