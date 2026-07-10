# PR QA review checklist

Use this checklist as coverage guidance, not as a rigid script.

## Intake

- Identify review target and base revision.
- Check working tree status and avoid overwriting user changes.
- Confirm whether product code or runtime may be changed. Default: read-only.
- Choose report path and artifact directory.
- Capture runtime URLs, namespace, credentials, known constraints, and user focus areas.
- Treat user focus as emphasis, not a limit; it does not remove required-by-diff tracks.
- Check for sub-agent tooling, including lazy-loaded tool discovery when available.
- Record orchestration mode: which sub-agents were used, or why sub-agents were unavailable or not used,
  and what coverage impact that creates.
- If the user provides a previous report or defect list, or prior findings are already known from the current review
  context, plan explicit reconciliation before starting deep checks.
- After reading the PR diff, create a Required-By-Diff Coverage table before delegating or deep-testing.
- Classify the diff into required tracks and delegate or explicitly review every required track, even if it was not
  named in the user's focus list.
- Record the owner for every required track: specialist sub-agent, main thread, or skipped.
- If a dedicated specialist exists but is not used for a required track, explain why.
- Record any required track that is skipped or only partially covered. Mark a track partial unless the report shows
  equivalent evidence for that track.

## Environment and tools

- Identify available runtime, URLs, namespace, credentials, and read/write constraints.
- Check relevant tools: browser automation, cluster CLI, Helm/Kustomize, language test runners, linters, API clients,
  log access, and security scanners.
- Check whether the runtime stand matches the review target using the strongest available proof: commit SHA, image
  digest, build metadata, chart/app version, container labels, process command line, or version endpoint.
- For Kubernetes-like stands, prefer PR SHA, built image digest, loaded/pushed digest, pod image IDs, Helm revision,
  rollout status, and rendered values. Use equivalent proof for Docker Compose or local-process stands.
- Ask before updating a stale stand unless the user explicitly allowed setup/update work.
- Record setup mutations, failed setup attempts, and the exact point where read-only review mode begins.
- After setup/update, return to the requested review mode and avoid further runtime changes unless allowed.
- Do not run checks that may create excessive load, trigger lifecycle transitions, send malformed traffic, exercise
  TTL/cleanup/compaction, or simulate DoS conditions without explicit permission or an isolated disposable environment.
- If traffic generation is degraded, use existing runtime data only when relevant and record the confidence limit.
- For user-requested focus areas, ask about missing critical tools before silently downgrading coverage.
- Record skipped or weakened coverage when a missing tool, access path, or unproven runtime version matters.

## Previous-run reconciliation

- If a previous report or defect list is provided, or prior findings are already known from the current review context,
  review each prior finding.
- Mark each prior item as reproduced, not reproduced, superseded, accepted/out of scope, or not rechecked.
- Explain not-rechecked items, especially when read-only constraints prevent reproduction.
- Do not mark reconciliation as not applicable when prior findings are available.

## Diff-driven required tracks

- Design/docs/spec changes -> run design reconciliation.
- Protocol/parser/decoder/frame/command/ack/reconnect/agent/ingest changes -> run protocol compatibility review.
- Seal/upload/compact/delete/TTL/retention/S3 layout/manifest/WAL/hot/cold/maintain changes -> run data lifecycle
  and retention review.
- UI/screen-spec changes -> run UI/UX and design review.
- Chart/manifest/route/ingress/secret/TLS/image changes -> run deployment/config review.
- Auth/untrusted rendering/download/query-limit/dependency/image/secret changes -> run security review.

## Change analysis

- Read diff and touched file list.
- Read PR description, linked issues, and comments when available.
- Identify generated files, migrations, dependencies, charts, docs, and tests.
- Compare changed behavior with old code and design docs.

## Design

- Compare implementation with changed design docs, screen specs, ADRs, API contracts, and old behavior.
- Identify design gaps that make expected behavior or QA ambiguous.

## Protocol compatibility

- Check old client with new server and new client with old server when staggered rollout is possible.
- Do not run malformed/stress protocol cases against live shared services unless disruptive checks are explicitly
  allowed.
- Check handshake, version negotiation, unknown commands, ack/error behavior, reconnect, resend, partial frames,
  malformed frames, and golden fixtures.
- Check real-agent or real-client E2E coverage and whether it blocks CI.

## Data lifecycle and retention

- Check WAL/segment -> sealed parquet -> uploaded -> compacted -> deleted transitions.
- Check TTL boundaries, grace periods, reader safety, late arrivals, failed upload, partial compaction, idempotency,
  hot/cold overlap, manifest cleanup, and safe runtime object/log/metric evidence.
- Prefer static proof, unit/integration tests, object counts, logs, metrics, and disposable environments over live
  cleanup/retention experiments unless explicitly allowed.

## Backend/API

- Validate request parsing, invalid inputs, limits, pagination, partial results, retries, concurrency,
  storage lifecycle, migrations, background jobs, and compatibility.
- Exercise normal and safe negative API requests when runtime exists. Use static proof or isolated environments for
  DoS-shaped, huge-range, malformed, or expensive requests unless the user allows disruptive checks.
- Check error status codes and response bodies.

## UI/UX

- Exercise main workflows, filters, tables, detail pages, modals, downloads, back/forward/reload, empty/loading/error
  states, responsiveness, accessibility, and keyboard use.
- Capture screenshots for confirmed visual/UX issues.
- Inspect browser console, page errors, failed requests, and duplicate/expensive requests.
- If UI is in scope and browser automation or UI dependencies are unavailable, ask whether to install or enable them
  before falling back to source/API-only review.
- If browser setup is declined, forbidden, or fails, record a UI/browser coverage limitation.

## Runtime/observability

- Inspect pod/process status, restarts, events, logs, metrics, health/readiness, background job output,
  storage state, and retention behavior.
- Check whether log levels separate expected lifecycle noise from actionable failures.

## Deployment/config

- Render Helm/Kustomize/manifests with realistic production and dev values.
- Compare rendered manifests or values across defaults, documented local/dev values, and existing stand values when
  compatibility is relevant.
- Check ingress/routes, TLS, external dependencies, secrets, probes, resource limits, startup ordering, retention, and
  documentation.

## Security

- Check secrets in code, rendered manifests, logs, screenshots, and docs.
- Check auth/authz, unsafe downloads, XSS in rendered external data, injection risks, SSRF-like behavior,
  path traversal, secret handling, transport security, and denial-of-service risks from unbounded work.
- Check query size guards, dependency/image changes, Kubernetes privileges, and sensitive logging.
- Look for repo-native dependency, license, secret, image, or manifest scanners. Run them when feasible, or record that
  scanner coverage was not available.

## Documentation/tests

- Check docs and examples for drift.
- Identify missing tests for changed or defective behavior.

## Report quality

- Each finding has severity, classification, code/design links, reproduction, actual result, expected result,
  and evidence.
- Pre-existing issues are marked as existing.
- Unconfirmed risks are either omitted or clearly marked as not fully reproduced.
- Screenshots and log snippets are saved next to the report.
