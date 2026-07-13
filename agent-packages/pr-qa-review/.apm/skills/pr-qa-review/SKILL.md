---
name: pr-qa-review
description: Use only when the user explicitly asks to run pr-qa-review for a PR, branch, commit, or code change.
---

# PR QA review

Use this skill when the user wants a QA-style investigation of changed code or a pull request, especially when they ask
for confirmed bugs, design mismatches, runtime issues, UI defects, API defects, deployment gaps, or a saved report.

This is not a fix workflow. Do not modify product code, deployment state, or test data unless the user explicitly asks
for fixes or test setup changes. Read-only commands, local rendering, local browser checks, and log collection are in
scope when permitted.

## Operating model

Use this skill as the user-facing entry point and act as the orchestrator. Build a review plan, divide the investigation
into independent tracks, and keep the master report. The package-provided specialist agents are optional execution
roles, not a runtime dependency. Never create or edit agent definition files during a review.

Check whether sub-agent tools and package-provided named roles are available, including lazy-loaded tool discovery when
the harness supports it. The user's request to use this skill permits read-only delegation unless they explicitly forbid
sub-agents. Select the first available execution mode for each independent track:

1. Delegate to the matching package-provided specialist agent.
2. Delegate to a generic sub-agent with the same bounded track and response contract.
3. Review the track in the main thread.

Use this order for requirements, design, backend/API, UI/UX, runtime/observability, deployment/config, docs, security,
and diff-required tracks such as protocol compatibility or data lifecycle/retention. Do not let sub-agents write the
final report directly; integrate and deduplicate their findings. Record the orchestration mode in the report: which
named or generic sub-agents were used, which spawn attempts failed, which tracks fell back to the main thread, and any
coverage impact. Agent unavailability alone is not a reason to skip a required track.

Keep moving until the planned coverage is meaningful. Do not stop after the first few bugs. If you hit a blocker, try a
reasonable alternative, then ask the user for the missing environment detail or tool.

## Inputs to collect

Before deep analysis, identify as many of these as possible:

- Review target: PR URL, branch, commit range, uncommitted changes, or patch.
- Report path and artifact directory, defaulting to `reports/<target>-qa-review.md` and `reports/`.
- Whether product code or deployment may be changed. Default: no changes, read-only review.
- Available runtime: local dev server, Docker Compose, Kubernetes namespace, ingress URLs, API base URL, credentials.
- Required external tools: browser automation, cluster CLI, Helm, language test runners, linters, scanners.
- User focus areas, if any. Treat focus as prioritization, not as permission to skip required-by-diff tracks.
- Existing design, architecture, ADRs, API contracts, README, Helm chart docs, older implementation behavior.
- Previous QA reports or defect lists, when the user provides them or when they are already known from the current
  review context.

If the target is a public or remote PR and details are not present locally, use the repository's normal
GitHub tooling or browser access when available. For time-sensitive external data, verify from primary sources.

## Environment preparation

Before relying on runtime, UI, API, deployment, or security checks, inventory the available environment and tools.
Check only what is relevant to the target, for example browser automation, cluster CLI, Helm/Kustomize, language test
runners, linters, API clients, log access, and credentials.

Check whether the running stand matches the review target before using it as reproduction evidence. This applies to any
runtime: Kubernetes, Docker Compose, local processes, remote dev stands, or repository-specific launch scripts. Use the
strongest available proof, such as commit SHA, image digest, build metadata, chart/app version,
container labels, rendered values, process command line, health/version endpoints, or deployment timestamps.

If the stand is stale or cannot be proven current:

- Ask before updating it unless the user explicitly allowed update/setup work in the prompt.
- Prefer the repository's documented build/deploy/update path.
- Record every setup mutation: source checkout, build command, image/tag/digest, deploy command, rollout action,
  and failed setup attempts.
- After update/setup is complete, explicitly declare the review phase read-only and do not mutate source,
  deployment, data, or cluster state again unless the user gives new permission.
- Record the target revision and the observed runtime version proof in the report.
- If version alignment cannot be proven, mark runtime findings with that limitation.

Read-only does not mean risk-free. Before running checks that may create excessive load, trigger lifecycle transitions,
send malformed traffic, exercise TTL/cleanup/compaction, or simulate DoS conditions, obtain explicit user permission or
use an isolated disposable environment. Otherwise record the check as skipped or needs-confirmation. Prefer static
proof, tests, fixtures, rendered manifests, logs, metrics, or safe object counts for these scenarios.

If a useful tool or access path is missing:

- Explain what additional evidence that tool would unlock for this specific review.
- If the tool is needed for a user-requested focus area, ask the user whether to install or enable it before
  downgrading that track to static or API-only review.
- Ask the user before installing tools, changing configuration, starting services, or modifying a cluster.
- Suggest repository-native or low-impact options first.
- Continue with static analysis, rendered manifests, API calls, logs, or manual browser checks when possible only after
  the user declines setup, setup fails, the tool is nonessential, or the user has already forbidden environment changes.
- Record skipped or weakened coverage in the report when the missing tool materially affects confidence.

Handle degraded test traffic explicitly. If generated traffic fails, use existing runtime data only when it is still
relevant to the target and record the limitation. Do not silently treat stale or unrelated data as reproduction
evidence.

For UI work, distinguish source/static checks from real browser checks. If UI is a requested focus area and browser
tooling or dependencies such as Playwright, node_modules, or browser binaries are missing, ask whether to install or
enable them so the review can capture screenshots, console errors, network evidence, and browser reproduction. If the
user declines, setup fails, or installation is forbidden, add a UI/browser coverage limitation and continue with
the best available source/API/static checks.

For security work, check whether repo-native scanners exist, for example dependency, license, secret, container image,
or manifest scanners. If they are absent or not run, record that scanner coverage limitation separately from manual
security review.

## Diff-driven required tracks

After reading the PR diff, create a Required-By-Diff Coverage table before delegating or deep-testing. Classify the
diff by changed domains. User-provided focus areas are emphasis, not a limit: every required-by-diff track must be
delegated or explicitly reviewed, even if it was not named in the user's focus list. Required tracks must be run or
explicitly reported as partial or skipped with coverage impact. For every required track, record the owner: a
specialist sub-agent, the main thread, or skipped. If a dedicated specialist exists but is not used, explain why. Mark
the track `partial` unless the report shows equivalent evidence for that track. Examples:

- Design or documentation changes require design reconciliation against implementation and old behavior.
- Protocol, parser, decoder, frame, command, ack, reconnect, agent, or ingest changes require protocol compatibility.
- Seal, upload, compaction, retention, TTL, cleanup, S3 layout, manifest, WAL, hot/cold read, or maintain changes
  require data lifecycle and retention review.
- UI or screen-spec changes require UI/UX and design review.
- Chart, manifest, route, ingress, secret, TLS, or image changes require deployment/config review.
- Auth, untrusted data rendering, downloads, query limits, dependency, image, or secret changes require security review.

## Review tracks

Use `references/pr-qa-checklist.md` as the expanded coverage checklist.

Use these tracks as a coverage checklist. Add or skip tracks based on the project and explain skipped
important tracks in the report or final summary.

1. Change and requirements analysis
   - Read the diff, PR description, linked issues, comments, tests, migrations, and generated files.
   - Find explicit and implicit requirements from design docs, old code, user stories, and release notes.
   - Compare implementation against the required behavior and compatibility expectations.

2. Project, architecture, and design analysis
   - Discover the project shape: services, UI, API, storage, deployment, background jobs, generated code.
   - Locate design docs, ADRs, API contracts, charts, local run instructions, and test harnesses.
   - Compare implementation against changed design docs, screen specs, contracts, and old behavior.
   - Mark assumptions that need user confirmation.

3. Protocol compatibility analysis
   - Run when the diff touches wire formats, agent/server protocol, ingest, parsers, decoders, frames, commands,
     acknowledgements, reconnects, or protocol docs.
   - Check old/new client compatibility, handshake/version behavior, malformed input, golden fixtures, and real-agent
     E2E coverage.

4. Data lifecycle and retention analysis
   - Run when the diff touches seal, upload, compaction, deletion, TTL, retention classes, S3 layout, manifests, WAL,
     hot/cold reads, or cleanup jobs.
   - Check state transitions, grace periods, late arrivals, failed uploads, idempotency, hot/cold overlap, and safe
     runtime evidence such as logs, metrics, and object counts.

5. Backend and API analysis
   - Review input validation, error mapping, partial results, pagination, limits, concurrency, retries,
     storage semantics, migrations, background jobs, and compatibility.
   - Exercise APIs with normal, boundary, and invalid requests when a runtime is available.

6. UI and UX analysis
   - Exercise core workflows, empty/loading/error states, back/forward/reload, filters, tables, modals,
     downloads, links, responsiveness, accessibility, and console/network errors.
   - Use screenshots for visual evidence. Prefer Playwright or the repository's existing browser test harness when
     available.

7. Runtime and observability analysis
   - Inspect logs, restarts, events, metrics, readiness/liveness, background jobs, storage side effects, and degraded
     states. Distinguish real defects from expected dev-stand noise.
   - Check whether log severity helps operators find real issues.

8. Deployment and configuration analysis
   - Render Helm/Kustomize/manifests with realistic values. Check external dependencies, ingress, TLS, secrets, resource
     limits, probes, startup ordering, retention, and configuration docs.
   - Verify that chart values expose the knobs needed for production and development stands.

9. Security analysis
   - Check secrets handling, auth/authz, unsafe downloads, XSS in rendered data, injection risks,
     wide-query/size guards, dependency and image changes, Kubernetes privileges, and sensitive logging.
   - Report evidence-backed security defects, not generic hardening wishes.

10. Documentation and tests
    - Identify documentation drift and missing operational instructions.
    - Identify missing tests for behavior that changed or defects found during review.

## Previous-run reconciliation

If the user provides a previous report or defect list, asks to compare with an earlier run, or prior findings are
already known from the current review context, reconcile them explicitly. For each prior finding or important prior
check, mark one status with a short reason:

- Reproduced.
- Not reproduced.
- Superseded by a new finding.
- Accepted or out of scope for this review.
- Not rechecked, with the constraint that prevented recheck.

Do not write `not applicable` when prior findings are available. Do not silently drop prior findings. If rechecking
would require mutating a read-only stand, missing browser tooling, disruptive runtime traffic, or unavailable
credentials, say that and keep the item as not rechecked rather than treating it as fixed.

## Evidence rules

A finding should normally have at least two anchors: code/design evidence and runtime/static reproduction evidence. Good
evidence includes:

- File links with line numbers and a short explanation of why each line matters.
- Exact commands, URLs, UI paths, API requests, or Kubernetes resources used to reproduce.
- Actual output snippets, logs, metrics, screenshots, rendered manifests, browser console/network evidence.
- Expected behavior from design docs, API contracts, old implementation, or user-confirmed expectations.

Do not include long raw logs or full copyrighted material. Quote only short relevant excerpts. Store larger artifacts as
files and link them.

## Finding classification

Use classifications that help triage. Suggested values:

- PR regression
- Existing issue
- Design mismatch
- Implementation gap
- Backend
- API
- UI/UX
- Accessibility
- Runtime
- Observability
- Deployment/config
- Security
- Documentation
- Test gap

If a problem existed before the PR, still include it when useful, but mark it as `Existing issue`.

## Report format

Use `references/report-template.md` as the default shape, but adapt it when the project needs more detail.
Every confirmed finding should include:

- Short title.
- Severity.
- Classification.
- Problem description.
- Relevant code/design links.
- Reproduction steps.
- Actual result.
- Expected result.
- Evidence: logs, screenshots, command output, metrics, rendered manifests, or API responses.
- Affected behavior or scope.
- A fix direction when the evidence supports one, without presenting an unverified patch as fact.
- Retest criteria that let a fixing agent verify the defect is resolved.

Treat the report as the handoff contract for the next fixing agent. Make each finding self-contained and actionable
without requiring access to the review conversation. Separate confirmed facts from suspected root cause and suggested
remediation.

Save the report and artifacts incrementally. Preserve user edits in an existing report: append new findings to the end
unless the user asks for restructuring.

## Tooling guidance

Prefer repository-native tools first. Useful tools often include:

- Fast search: `fff`, `rg`, `git grep`.
- PR metadata: `gh`, repository remotes, local branch diff.
- UI: Playwright or the existing browser test harness.
- API: `curl`, generated clients, repository integration tests.
- Runtime: `kubectl`, `helm`, `docker compose`, logs, metrics endpoints.
- Security: existing dependency scanners, secret scanners, lint rules, rendered manifest review.

If an important tool is missing, explain why it matters and ask the user whether to install it. Do not install tools or
change the environment without permission.

## Stop conditions

Stop when one of these is true:

- The planned tracks have been covered enough for the target risk.
- A blocker prevents meaningful progress and the user must provide access, credentials, or a running environment.
- The user asks to pause.

The final response should summarize new findings, report path, artifacts created, checks run, and notable
checks that did not find defects.
