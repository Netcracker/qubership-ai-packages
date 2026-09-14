# enable-renovate-automerge

Configure Renovate automerge on GitHub while ordinary PRs still require human approval. Eligible Renovate PRs receive
approval from Renovate Approver and merge through GitHub after required tests and applicable style checks pass.

The skill activates when you enable or audit Renovate automerge, select required checks, or add gates for dependency
updates. It applies per repository and verifies one pilot before a broader rollout.

## What it does

1. Reads effective Renovate configuration, GitHub protection, App access, PR evidence, and existing CI behavior.
2. Maps allowed updates to the minimum lint and build/test workflows and prepares changes within the requested scope.
   For GitHub Actions, it distinguishes static checks from real execution and keeps release-only actions manual unless a
   safe smoke or dry run covers them. It asks the owner only for unresolved choices that affect coverage or scope.
3. Makes each required workflow report on every PR. It moves `pull_request.paths` decisions into the workflow so
   inapplicable validation jobs can skip while the final gate succeeds.
4. Evaluates the combined protection policy, recommends one strict ruleset, and shows a candidate consolidated policy.
   Consolidation happens only after agreement and preserves human bypass actors and modes.
5. Compares the current effective Renovate policy with `github>Netcracker/renovate-config:automerge`, including the
   exact visible change in automerge scope. The owner decides whether to adopt the centralized policy.
6. Enables repository auto-merge and verifies Renovate Approver on an eligible PR.
7. Checks successful merge, failed/missing-check blocking, ordinary review enforcement, and approval after rebases.

The full procedure and exception handling live in the [skill](.apm/skills/enable-renovate-automerge/SKILL.md).
Each golden rule contains its target, inspection, implementation, and confirmation steps. Setup requests proceed through
the needed changes; audit requests evaluate the same rules read-only.
Human and other unrelated bypass rules remain repository policy outside Renovate automerge. The skill removes no bypass
unless its actor is identified as a direct automerge participant, and grants none to Renovate or Renovate Approver.
Merge Queue and new test workflows are separate work.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/enable-renovate-automerge
```

Then run `apm install` and `apm compile` as required by your consuming APM project. Development changes become available
through this command only after publication; editing the source package does not update an installed skill.

## Requirements

- GitHub access through an authenticated `gh` CLI, with authority to enable auto-merge and change protection rulesets.
  Without that authority, the skill prepares source changes and settings instructions for the owner.
- Renovate, a compatible Renovate Approver installation, and real PR test/style coverage for eligible updates.
- Authority to run the pilot's test PRs and change the target protection policy. Read-only audits report gaps without
  activation.
