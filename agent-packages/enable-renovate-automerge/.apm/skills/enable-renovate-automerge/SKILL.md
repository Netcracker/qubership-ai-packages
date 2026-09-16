---
name: enable-renovate-automerge
description: Set up or audit Renovate automerge on GitHub while preserving required review and real CI checks. Use when enabling dependency automerge, selecting required checks, or adding CI gates for Renovate updates.
---

# Enable Renovate automerge

Ordinary PRs require human approval. Eligible Renovate PRs receive approval from Renovate Approver and merge through
GitHub auto-merge only after required CI passes. Apply the checks below per repository; prove one pilot before rollout.

## Working mode and scope

A setup or fix request means: inspect each golden rule, preserve what passes, correct authorized deviations, and show
the changes. An audit or validation request uses the same rules read-only and reports remedies without editing files,
settings, or PRs.

Treat analysis, local preparation, publication, live settings, and runtime exercises as separate authorization stages.
Interpret intent from the request, not from exact keywords:

- An audit, inspection, or analysis request authorizes analysis only.
- A setup, fix, or implementation request also authorizes a verified local diff after the scope decision.
- A request for canonical automerge, the shared preset, or all non-major updates selects canonical scope and authorizes
  local preparation, but not publication or live changes.
- An explicit request to complete the work autonomously or end to end authorizes all in-scope stages, including needed
  publication, live settings, App access, and test PRs. It does not authorize manual approval or merge, bypassing
  protections, unrelated changes, or destructive actions.
- A request that names particular stages authorizes those stages without authorizing the others.

Without the matching authorization, do not commit, push, create or update a pull request, issue, or comment, change a
ruleset, repository setting, or App access, or create or close a test PR. Show the prepared result and exact external
writes before asking for the next authorization. Read-only confirmation after an authorized write belongs to that
write.

Separate mechanism requirements from owner policy. Required checks, review enforcement, and platform auto-merge make
the mechanism work. Eligible managers, packages, update types, and accepted post-merge risk are owner choices. Show
their exact behavior delta during analysis, including newly automatic updates, validation timing, recovery, and local
exceptions. End analysis with the owner's scope choice: canonical policy, current policy with mechanism fixes, or
canonical policy with explicit exceptions. A generic request to configure automerge does not select that scope. An
explicit request for canonical automerge, the shared preset, all non-major updates, or named selectors does. When
canonical scope is selected, record coverage gaps, residual risks, and recovery paths, then continue with local
preparation; do not reopen the scope decision unless new evidence requires a choice outside the canonical policy. Do
not prepare policy-changing source edits before the scope decision. Implement the owner's choice instead of converting
a coverage gap into a prohibition.

Record the repository, host from its remote, default branch, source SHA, dirty state, and observation time. Preserve
user changes. Use current evidence and refresh it when relevant state changes. Permissions and authorization are
distinct: without settings access, prepare source changes and exact owner actions. Missing evidence is unconfirmed, not
failure.

When an owner must inspect, confirm, or change a GitHub setting, include its exact UI navigation and a direct settings
URL when known. Do not leave the owner with only an API field or command.

For every shared Renovate preset, record its reference, observed repository SHA, and observation time. If Renovate logs
show the exact resolved SHA for the audited run, record it separately. Otherwise call the repository SHA observed, not
proof of the run's effective revision.

Keep changes within Renovate automerge. Installing Apps, expanding access, or creating/closing test PRs requires
explicit authorization for those actions. Preserve unrelated repository practices and merge methods. Archived
repositories remain excluded until unarchived and reassessed. Dependabot migration, new tests, Merge Queue, and changes
to Renovate validation modes are separate work. Never request credentials in chat.

## Repository requirements

### Requirement 1. Every allowed update has an explicit coverage and risk decision

**Target.** Map every update that the target policy would allow to its pre-merge checks and residual risk. The owner
decides whether post-merge detection is acceptable or whether the update needs more CI or a manual exception. If tests
already build or compile the project, a separate build workflow is unnecessary. Select the minimum useful workflows.

**Inspect.** Read effective Renovate configuration, inherited presets, rule ordering, groups, and exceptions. Search
open and recently closed repository issues for required CI gates, branch protection, workflow reliability, and Renovate
automerge. Incorporate relevant acceptance criteria and linked work into the coverage map and gate implementation, but
verify issue assumptions against the current workflows and repository settings. Trace all possible changed files through
actual workflow commands, reusable workflows, matrix jobs, and conditions. For GitHub Actions dependencies,
distinguish static checks such as YAML parsing, actionlint, and zizmor from execution of the changed action. Build this
map:

| Selector | Files | Workflows/jobs | Execution evidence | Gate | Applicability |
| --- | --- | --- | --- | --- | --- |
| Manager/package/update | Grouped files | Lint/build/test | Static or executed | Name | Run/skip conditions |

**Implement.** Identify the relevant lint and build/test workflows. Keep multiple lint gates when required linters live
in separate workflows. Add specialized checks when the owner chooses pre-merge coverage for an update class, such as
Helm validation.
PR titles, labeling, approval, release automation, and bare Docker builds do not establish test coverage.
Show the map and proposed changes. Resolve undecided coverage choices with the owner; use existing authorization to
prepare the concrete diff. Preserve actor exclusions: if Renovate is excluded from a relevant test, record that gap.

For a GitHub Action update, record whether the Renovate PR executes the changed action and whether PR inputs and
permissions differ from its normal use. Actions used only by release, schedule, manual, or default-branch workflows may
first run after merge. Explain the resulting failure-detection and recovery path. Let the owner choose among accepting
that post-merge feedback loop, adding a safe smoke or dry run, or keeping the action manual with a narrow local
exception. Never publish or mutate an external system merely to qualify an update for automerge.

**Confirm.** Every allowed selector, including all grouped members, appears in the coverage map with its residual risk
and the owner's decision. The shared Netcracker policy allows minor, patch, pin, digest, and pin-digest updates for
every manager, including GitHub Actions, Maven, Docker, Go modules, and non-major vulnerability fixes. Major updates
remain manual. A coverage gap is a policy delta to disclose, not an automatic reason to narrow the shared preset.

### Requirement 2. Required workflows always report meaningful gates

**Target.** Each selected workflow publishes a stable gate on every PR to the protected branch. Applicable validation
succeeds; inapplicable validation may skip while the final gate succeeds. Gates aggregate results without repeating CI.

**Inspect.** Read PR events, branch/path filters, actor exclusions, job conditions, detectors, and gate dependencies.
An absent workflow/check differs from an internal skipped job. Workflow filters can leave a required check pending.

**Implement.** Reuse gates or add an aggregator with `needs` on the relevant jobs and `if: always()`.
Move `on.pull_request.paths` and `paths-ignore` into an internal detector controlling validation jobs. Reuse an existing
detector; unconditional validation needs none. Preserve the actual validation steps and effective applicability.
Keep unrelated push, schedule, manual, and branch behavior; PR branch filters must include the protected branch.
Use detector outputs and `needs.*.result` in the gate rather than duplicating path matching.

Give each gate one stable check name. If a gate applies only to pull requests, keep the name constant and use a
job-level `if: ${{ always() && github.event_name == 'pull_request' }}` condition. Do not add event-specific names such
as `Gate (push)`: a successful push check with the same name and SHA does not replace a failed pull-request check.
Introduce different names only after reproducing a ruleset decision that incorrectly accepts the push check.

Keep the gate contract minimal: require the detector to succeed, require applicable validation jobs to succeed, and
otherwise let the gate succeed. Compare required results with `success`; this rejects failure, cancellation, timeout,
and unexpected skips without enumerating every terminal state. Do not require inapplicable jobs to have a specific
result because their internal skip behavior is not part of the merge contract.

For detector-controlled validation, fail closed with the smallest condition that expresses that contract:

```yaml
- name: Require validation when applicable
  if: >-
    needs.changes.result != 'success' ||
    (needs.changes.outputs.run != 'false' && needs.validation.result != 'success')
  run: exit 1
```

The `!= 'false'` comparison treats a missing or unknown detector output as requiring validation. The validation job then
cannot be skipped without failing the gate. Extend the final parenthesized clause when the detector controls several
validation jobs; do not add inverse checks that require each job to be `skipped` when validation is inapplicable.

**Confirm.** Compare applicable and inapplicable PR changes: validation keeps its intended conditions and gates report
in both cases. Read exact check names and producer integration IDs on the candidate SHA; reusable workflows may report
compound names. Avoid duplicate contexts. Preserve extra gates and required checks until a reporting replacement proves
equivalent coverage. Default-branch runs alone do not establish PR or bot behavior.

See [GitHub required checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging).

### Requirement 3. Effective protection enforces required CI and review

**Target.** Effective default-branch protection has the following settings, with bypass governed by requirement 4. One
ruleset is the recommended end state because it makes the policy easier to inspect and maintain.

| Setting | Target |
| --- | --- |
| Required status checks | Verified gates selected under requirement 1 and requirement 2 |
| `strict_required_status_checks_policy` | `true` |
| Require a pull request | Enabled |
| `required_approving_review_count` | `1` |
| `require_code_owner_review` | `false` |
| `dismiss_stale_reviews_on_push` | `true` |
| `required_review_thread_resolution` | `true` |

**Inspect.** Fetch full repository and inherited rulesets plus classic branch protection. Evaluate their combined
effect; multiple rulesets alone are not a defect. List responses may omit rules and bypass actors; do not interpret
omissions as empty settings. Save the previous state and compare every target field. Inspect effective `rebaseWhen`,
`schedule`, `updateNotScheduled`, `automergeSchedule`, timezone, and the actual Renovate runner cadence. A Renovate
schedule limits when work is allowed; it does not trigger a run, so never infer runner cadence from it. Record the
owner-approved maximum convergence latency.

```sh
gh api repos/<owner>/<repo>/rulesets
gh api repos/<owner>/<repo>/rulesets/<id>
gh api repos/<owner>/<repo>/branches/<branch>/protection
```

**Implement.** After gates report reliably, register their exact names and producer IDs and apply the review settings.
Recommend one ruleset and show the owner a candidate policy that preserves the effective checks, review settings,
bypasses, deletion and force-push restrictions, and unrelated protections. Consolidate only after the owner agrees.
Add and verify combined requirements before retiring redundant rules; never leave the branch unprotected.

Set strict required checks to `true`. Explain that after one PR changes the default branch, other open Renovate PRs must
update from it, rerun CI, and regain an approval dismissed as stale. Report the resulting rebase and CI cost rather than
weakening the policy. Preserve existing required checks unless replaced with verified equivalent coverage under
requirement 2. Identify owner action if inherited or classic policy prevents convergence. Source-controlled changes go
through an ordinary reviewed PR.

**Confirm.** Re-read effective protection and compare it with the saved state. Use requirement 7 for enforcement
evidence; stored JSON alone does not prove enforcement. If runner cadence or the convergence target is unknown, mark
operational readiness unconfirmed.

### Requirement 4. Preserve unrelated bypass; remove bypass for automerge participants

**Target.** Renovate, Renovate Approver, and other direct automerge participants have no review or CI bypass.
Human and unrelated bypass actors retain their effective scope and mode.

**Inspect.** Identify all actors in repository/inherited rulesets and classic bypass lists, including repository roles,
organization roles, teams, and integrations. GitHub represents the built-in Maintain role as `RepositoryRole` with
`actor_id: 2`; treat it as an identified human bypass and preserve it. For another unexplained numeric ID, provide the
owner with `Repository Settings > Rules > Rulesets > <ruleset> > Bypass list` and the direct
`https://github.com/<owner>/<repo>/settings/rules/<ruleset-id>` URL, then ask them to identify the displayed actor.

**Implement.** Remove bypass only after identifying its actor as a direct automerge participant. Preserve human roles,
teams, and unrelated App bypasses through consolidation without narrowing or broadening scope or mode.
Identify unknown actors before changing their bypass. Never grant bypass to make automerge work.

**Confirm.** Compare effective actors and modes before and after. Only identified automerge participants lose bypass.
Human bypass remains repository policy and is not used to complete the pilot.

### Requirement 5. GitHub and the Apps can perform their roles

**Target.** Renovate can open/update PRs, Renovate Approver can approve eligible PRs, and GitHub allows platform
auto-merge.

**Inspect.** Read `allow_auto_merge`, allowed merge methods, permissions, App access, and observed bot activity.
Missing installation-list permissions mean unconfirmed access, not an absent App. Verify through accessible settings,
owner evidence, or actual activity. Check hosted Approver compatibility with self-hosted Renovate or another bot
identity.

**Implement.** Once gates and protection work, enable repository auto-merge:

```sh
gh api -X PATCH repos/<owner>/<repo> -F allow_auto_merge=true
```

Resolve missing App access within explicit authorization or report the exact owner action. Use an already allowed merge
method; do not change allowed methods.

**Confirm.** Read back the setting and verify App activity in requirement 7. Approver can approve before CI completes
because required checks hold the merge.

See [Renovate Approver](https://github.com/renovatebot/renovate-approve-bot).

### Requirement 6. Renovate delegates the owner-selected updates to platform auto-merge

**Target.** Recommend that Netcracker repositories opt in through
`github>Netcracker/renovate-config:automerge`. The preset enables GitHub platform auto-merge for all non-major update
types. Major updates remain manual. A deliberately narrower local policy may remain after the owner reviews the exact
change in scope. GitHub configuration contains no `autoApprove`; approval comes from Renovate Approver.

**Inspect.** Determine whether the shared preset is used, at the revision recorded in working mode. Compare its
effective policy with the repository's current effective package rules, including inherited/global automerge, rule
ordering, schedules, groups, manual exceptions, and `vulnerabilityAlerts` overrides.

**Implement.** If the shared preset is absent, report that centralized automerge configuration is not used and recommend
migration. Absence alone is not a repository defect. Show the exact user-visible delta before changing configuration:

| Policy area | Current behavior | Shared preset behavior | Behavior change or risk |
| --- | --- | --- | --- |
| Managers, packages, update types, files | Automatic and manual scope | Automatic and manual scope | Newly automatic updates |
| Validation and recovery | Pre-merge and post-merge checks | Checks that apply to the new scope | Detection timing and recovery path |
| Vulnerability updates | Effective update-type behavior and overrides | Non-major automatic; major manual | Newly automatic fixes |
| Local rules | Existing exceptions and duplicate rules | Rules removed, retained, or added | Preserved or removed exceptions |
| Other behavior | Groups, schedules, minimum release age, and other presets | Changed or unchanged | Operational effect |

Let the owner decide whether the difference is acceptable and whether to migrate. An explicit request to adopt the
canonical policy, shared preset, all non-major updates, or named selectors is that decision; do not ask for it again. A
generic request to configure automerge is not. Otherwise, do not widen an intentionally narrow scope until the owner
chooses. After migration is chosen, preserve the existing `extends` entries and add the shared preset:

```json
{
  "extends": [
    "github>Netcracker/renovate-config:automerge"
  ]
}
```

Do not repeat `automergeType`, `platformAutomerge`, or the shared non-major package rule in repository-local
configuration. Do not add a `vulnerabilityAlerts.automerge` override: non-major vulnerability fixes already match the
shared package rule, while major vulnerability fixes remain manual. Keep only repository-specific exceptions and other
capability presets locally. Remove obsolete duplicate automerge rules and `autoApprove`. For repositories outside
Netcracker, use an equivalent local rule only when the shared preset is unavailable.

Prepare configuration with CI changes when useful. Put the review and required-check protections in place before
activation unless the owner explicitly accepts a different order. Coverage gaps do not veto the owner's selected
automerge scope: record the affected updates, when failures would be detected, and how they would be recovered. If
automerge is already active with an unreviewed gap, show the same choices and implement the owner's selected policy.

**Confirm.** Run existing Renovate validation and policy tests; preserve standalone and installation-specific modes.
Verify effective selectors rather than syntax alone. Confirm the real auto-merge request in requirement 7.

See [Renovate platform automerge](https://docs.renovatebot.com/configuration-options/#platformautomerge).

### Requirement 7. A real PR proves automatic operation

**Target.** An eligible Renovate PR receives approval and merges through GitHub platform auto-merge after required CI.
Ordinary unapproved PRs and failed/missing-check PRs remain blocked on the ordinary merge path.

**Inspect.** Record author, files, exact head SHA, automerge marker, reviews, checks, auto-merge request, and timeline.
Prefer a fresh eligible PR opened by Renovate. Human imitations, old merged PRs, or PRs marked
`Automerge: Disabled by config` are not positive pilots.

**Implement.** Observe without manually approving, merging, or bypassing protection. Do not widen scope to manufacture
a pilot. Approver reacts to PR opening and qualifying dismissal of its own review. Installing it later, editing the
body, or reopening an old PR alone does not prove approval will occur. Verify approval restoration after a Renovate
update/rebase dismisses stale reviews. After one eligible PR merges, observe another eligible PR that is behind the
default branch. Record timestamps for the base merge, Renovate rebase, restored approval, and required checks on the
new head SHA.

For explicitly authorized negative test PRs, arrange the blocking condition before any auto-merge request. Satisfy other
merge prerequisites to isolate the check: a red PR also lacking approval does not prove CI enforcement.
Before cleanup makes a test mergeable, close it or disable auto-merge within that authorization. Never break the default
branch for a test. Missing authority blocks only the affected scenario.

**Confirm.** Record evidence for each outcome:

| Scenario | Required evidence |
| --- | --- |
| Eligible Renovate PR | `**Automerge**: Enabled`, effective Approver approval, GitHub auto-merge request |
| Required checks pass | Platform merge, checks and approval on the exact SHA, corroborating timeline |
| Required check fails or is absent | Other prerequisites satisfied; PR remains blocked by that check |
| Ordinary PR without human approval | CI passes, no bot approval, review blocks merge |
| Renovate updates the branch | Next-run timestamps for rebase, fresh approval, and required checks on the new SHA meet the convergence target |

Capture the auto-merge request before merge. A bot in `merged_by` or green checks alone cannot distinguish direct merge
from platform auto-merge. If no eligible PR or event is available, report configured with runtime pending.
Keep missing scenarios explicit rather than treating them as passed. If actual runner cadence or convergence latency
is not confirmed, report operational readiness as unconfirmed.

## Application order

1. Inspect the starting state, build requirement 1's coverage and risk map, and check requirement 4's bypass inventory
   and requirement 5's prerequisites early.
2. Show requirement 6's exact policy delta and obtain the owner's scope decision unless the request already states it.
3. Prepare and verify the selected configuration plus any requirement 2 workflow changes locally.
4. When publication is authorized, commit, push, and open or update an ordinary reviewed PR. Confirm gates on PR runs.
5. When live settings are authorized, apply requirement 3 and requirement 4 protection. Activate requirement 5 and
   requirement 6 only after protection works.
6. When live exercises are authorized, verify requirement 7 in one repository before broader rollout. Recheck each
   repository's policy and CI; a sample does not prove fleet completion.

## Result

Show the coverage map and report each golden rule as met, unmet, or unconfirmed, with evidence and the remaining action.
Distinguish source changes prepared, live settings applied, and runtime verified. Link the diff/source PR and settings
evidence separately. Name remaining owner actions, missing events, and the next authorization stage. Audit requests
report remedies. Setup requests prepare and verify local changes, then continue only through explicitly authorized
publication, live-setting, and runtime stages.
