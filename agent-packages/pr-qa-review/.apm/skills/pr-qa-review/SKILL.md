---
name: pr-qa-review
description: Use only when the user explicitly asks to run pr-qa-review for a PR, branch, commit, or code change.
---

# PR QA review

## Review contract

Remain the root orchestrator. This is a review workflow, not a fix workflow. Keep product source, deployment state, and
test data read-only unless the user grants the applicable mutation permission. Save the report incrementally and
preserve user edits in an existing report.

Maintain one working coverage table with these fields: track, reason, required capability, implementation, owner,
planned evidence, status, and impact. Use only `planned`, `ready`, `in progress`, `complete`, `partial`, `skipped`, and
`blocked` as working statuses. User focus areas set priority but never remove tracks required by the diff.

Keep severity, finding confidence, evidence source, and check outcome independent. Finding confidence is `Confirmed`,
`Strong static evidence`, or `Suspected`. Main findings contain only `Confirmed` and `Strong static evidence`
candidates. Keep suspected candidates in follow-ups or limitations when they help the next reviewer.

## Phase 1: Identify the target

Record the target kind, repository, requested scope, report path, artifact directory, user focus, and previous review
material. For a PR, include the repository and PR number; for local changes, include the repository root and
index/worktree scope.

**Exit:** The requested target, output locations, focus, and prior-review inputs are recorded or explicitly absent.

## Phase 2: Establish permissions

Record separate permissions for source and report writes; project dependencies; external tools; service startup,
restart, deployment, or update; test and persistent data; and disruptive, malformed, cleanup, retention, or stress
traffic. Read-only delegation is allowed unless the user forbids sub-agents, but delegated tasks remain explicitly
read-only.

**Exit:** Every action class that the review may use has an allowed, denied, or unresolved boundary.

## Phase 3: Resolve exact revisions

Resolve the comparison locally and record complete `base_oid` and `head_oid` values. These values identify the initial
target and must remain complete in working state, coverage records, delegation context, reports, and final checks. Do
not abbreviate a supplied or resolved OID. Confirm that local revisions match the requested target before using the
exact local diff. Remote metadata and file summaries support discovery, but never replace the exact local diff.

For patches or uncommitted changes, record a stable patch identity or checksum when practical and capture the initial
status and scope.

**Exit:** The initial target has complete, locally verified revision identities and an exact diff source.

## Phase 4: Build required-by-diff coverage

Read [change analysis](references/change-analysis.md). Classify the exact diff and add every triggered track to the
coverage table before deep checks or runtime-dependent delegation. Include intended behavior before compatibility
checks. Add baseline smoke for each changed user-reachable surface. Mark a track not applicable only when the diff does
not trigger it.

**Exit:** Every changed domain, public or persisted contract, focus area, and baseline smoke need maps to a coverage
row with all required fields.

## Phase 5: Inventory capabilities

Derive capabilities from the coverage rows, then apply the discovery order in
[runtime and environment](references/runtime-and-environment.md). Record the selected implementation for each required
capability. Tool absence is not capability absence. Check repository-native setup, harness-native implementations,
existing runtime access, and reasonable visible alternatives before declaring a capability unavailable.

Inventory named package agents, generic sub-agents, and main-thread execution. Agent availability changes ownership,
not required coverage.

**Exit:** Each required capability has a selected implementation or a material evidence gap, and each track has a
viable execution mode or recorded impact.

## Phase 6: Align the runtime

For every runtime-dependent track, prove whether the runtime matches the complete `head_oid` and all changed deployment
layers. Select a strategy using [runtime and environment](references/runtime-and-environment.md). Obtain permission
before material direct or indirect mutations. If a missing decision materially changes required evidence, ask one
bounded user question that states the alternatives, side effects, cleanup or rollback, and evidence unlocked.

Runtime-dependent delegation waits for alignment. Independent static-ready tracks may start earlier. Do not treat an
unaligned or unproven runtime as regression evidence.

**Exit:** Each runtime-dependent track is aligned and `ready`, safely degraded to `partial` or `skipped` with impact,
or `blocked` on one explicit material decision.

## Phase 7: Delegate ready tracks

Choose the first available owner for each track: a matching package specialist, a generic sub-agent, or the main
thread. Use no more than three concurrent leaf agents and respect lower harness limits. Delegate only independent
`ready` tracks. Leaf agents do not delegate, rediscover the full target, mutate state outside granted permissions, or
write the final report.

Each delegated context contains complete exact revisions, bounded files and directories, authoritative requirements,
capability implementations, runtime proof, permissions, planned evidence, and the response contract. The response
contract requires findings and negative results with evidence, limitations and impact, candidate confidence, and any
missing or contradictory context.

**Exit:** Every ready track has a prepared owner and context packet, and every non-ready track retains its blocking
condition in the coverage table.

## Phase 8: Run checks

Run baseline smoke, then static, build, test, browser, API, runtime, deployment, and scanner checks selected by the
coverage map. Prefer repository-native commands and deterministic executable evidence. Record commands, versions,
URLs, resources, outputs, artifacts, negative results, mutations, side effects, and cleanup. Never turn predicted
behavior into an observed result.

Continue independent safe work while a material question is pending only when the harness can receive the answer in
the same turn. Otherwise save a preliminary report and return the question.

**Exit:** Every executable planned check has evidence or a recorded constraint and coverage impact.

## Phase 9: Reconcile candidates

Read [report quality](references/report-quality.md) before classifying any candidate or admitting it to main findings.
Challenge each candidate against intended requirements, contracts, old behavior, tests, ADRs, documented limitations,
accepted risks, and contradictory evidence. Merge duplicates and split independently fixable claims. Reconcile prior
findings as reproduced, not reproduced, superseded, accepted or out of scope, or not rechecked with the constraint.

Classify retained candidates as `Confirmed`, `Strong static evidence`, or `Suspected`. Only the first two enter main
findings. Preserve useful rejected and merged decisions outside the main count.

**Exit:** Every candidate and applicable previous finding has an evidence-backed decision and no suspected candidate
appears in the main finding list.

## Phase 10: Recheck the target

Re-resolve the complete target head. If it still equals the initial `head_oid`, record the verification. If it changed,
record the new complete OID, compute the exact delta, identify affected tracks, and review or rerun them. If the new
delta cannot be reviewed, mark the report stale or preliminary and include both complete old and new head OIDs.

**Exit:** The report either covers the rechecked head or explicitly identifies its stale or preliminary target delta.

## Phase 11: Write and validate the report

Reuse [report quality](references/report-quality.md) to validate the report. Include exact target revisions and recheck
result; permissions; runtime strategy and proof; the coverage table; orchestration; main findings; suspected follow-ups
and limitations; useful rejected or merged candidates; previous-run reconciliation; negative results; and artifact and
code links. Make every finding self-contained with severity, classification, confidence, evidence source, problem,
anchors, reproduction, actual and expected behavior, scope, supported fix direction, and retest criteria.

Validate report counts, required fields, links, and coverage statuses. Do not silently finalize while a material
permission or runtime decision remains unresolved.

**Exit:** The saved report passes structural and link checks and every required track has a terminal status and impact.

## Reference routing

- Always read [change analysis](references/change-analysis.md).
- Read [runtime and environment](references/runtime-and-environment.md) when any required track needs setup, tools,
  access, runtime evidence, deployment, or a potentially mutating action.
- Read [UI and user surfaces](references/ui-and-user-surfaces.md) when the diff changes a user-reachable surface.
- Read [API and compatibility](references/api-and-compatibility.md) when the diff changes backend behavior or a public
  or persisted contract.
- Read [data lifecycle](references/data-lifecycle.md) when the diff changes migrations, retention, storage lifecycle,
  cleanup, compaction, upload, or deletion.
- Read [deployment and configuration](references/deployment-and-configuration.md) when deployable behavior changes.
- Read [security](references/security.md) when the diff changes trust boundaries, dependencies, images, secrets,
  exposure, auth, or untrusted input handling.
- Always read [report quality](references/report-quality.md) before confirming findings or finalizing the report.

## Completion gate

Finish only when every required track is `complete`, `partial`, or `skipped` with impact recorded. A required track may
not disappear because tooling, runtime access, credentials, or sub-agent support is unavailable. Do not finish with a
track `planned`, `ready`, `in progress`, or `blocked`, or with an unanswered material permission question.

The final response states finding counts by confidence, the report and artifact paths, checks run, meaningful negative
results, partial or skipped coverage and impact, mutations and cleanup, and the final target-recheck result.
