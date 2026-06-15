---
name: enable-renovate-automerge
description: Set up Renovate so dependency-update PRs merge themselves once CI passes. Use when enabling automerge in renovate.json, deciding which GitHub status checks to mark as required so a green PR means the tests actually ran, or adding a CI-gate job that folds several test jobs into one required check.
---

# Enable Renovate automerge

Turn on Renovate automerge for a repository so dependency PRs merge
themselves once CI is green — without lowering the bar for what "green"
means.

Automerge is only as safe as the checks that gate it. The work here is
mostly about the gate: making sure a green PR means real tests and style
checks ran and passed, and registering exactly those checks as required.
Flipping `automerge: true` is the last and smallest step.

Apply this whether you configure one repository or sweep several: run the
steps per repository.

## Policy (read first)

- Automerge only behind a real gate. A green merge must mean tests
  (and style, where present) actually ran and passed. Never enable it
  where the only required checks are a PR-title linter, Conventional
  Commits, or a Docker-build smoke test.
- Renovate only. Dependabot has no platform-side automerge, so it is out
  of scope here; note it and move on, or treat migration to Renovate as
  separate work.
- Verify check names, don't guess them. A required status check matches
  the check-run name GitHub reports exactly, and reusable workflows
  report a compound `<caller-job> / <inner-job>` name.

## Step 1. Confirm the prerequisites

- **Bot is Renovate.** Look for `renovate.json`, `.github/renovate.json`,
  or a `renovate` key in `package.json`. If the repository runs
  Dependabot (`.github/dependabot.yml`) instead, stop and report it as
  out of scope.
- **You have admin.** Editing rulesets and repository settings needs it:

  ```sh
  gh api repos/<owner>/<repo> --jq .permissions
  ```

  Without `admin`, prepare the changes as a PR plus a written ruleset
  instruction for the org owner instead of applying them.
- **A real PR-triggered check exists.** List the workflows that run on
  `pull_request` and find the jobs that run actual tests or style checks
  — not title validation, not a bare Docker build. If none exist, there
  is nothing to gate on: stop and report it. Creating a test workflow is
  separate work, out of scope here.

## Step 2. Decide the required check(s)

The aim: every gating workflow contributes a check that ends up in the
ruleset, so a green PR is a tested PR.

**Several gating jobs in one workflow file** — add a single aggregating
job and require that one check:

```yaml
ci-gate:
  name: CI Gate
  needs: [test, lint, build]   # every gating job in this file
  if: always()                 # run even when a dependency fails
  runs-on: ubuntu-latest
  steps:
    - name: Fail if any dependency failed
      if: contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')
      run: exit 1
```

Register one required check, `CI Gate`, for that workflow.

**Gating checks spread across separate workflow files** — a reusable
gate workflow and a status-polling job are both rejected here: the
reusable form mixes step output and constrains the workflow, and polling
is fragile. Instead, register each check as its own required check. Where
a job or workflow name is long or noisy
(`Go test with Sonar / Build and test with coverage`), shorten the job
name first so the ruleset list stays short and the check name stays
stable.

Three traps to check before you settle on a check:

- **Name mismatch.** Read the name GitHub actually reports, from a recent
  run on the default branch:

  ```sh
  gh api repos/<owner>/<repo>/commits/<branch>/check-runs --jq '.check_runs[].name'
  ```

- **Bot-excluded checks.** A job guarded by
  `if: github.actor != 'renovate[bot]'` is skipped on a Renovate PR, so a
  required check built on it stays pending forever and blocks automerge.
  Drop the exclusion or pick a different check.
- **Skipped or neutral checks block the merge.** That is why the gate job
  uses `if: always()` and resolves explicitly to success or failure
  rather than being skipped.

## Step 3. Register the required checks in the ruleset

With admin, add the chosen check(s) to the branch ruleset for the default
branch:

```sh
gh api repos/<owner>/<repo>/rulesets --jq '.[] | {id, name}'
gh api repos/<owner>/<repo>/rulesets/<id>          # inspect current rules
```

Patch the `required_status_checks` rule so it lists each chosen check by
its exact name (and its integration ID, where the API expects one). Keep
"Require branches to be up to date" in mind: with it on, Renovate must
rebase before merge, which is the normal automerge flow.

## Step 4. Enable automerge in renovate.json

Scope automerge to the update types you trust, and let GitHub's native
auto-merge wait for the required checks:

```json
{
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch", "pin", "digest"],
      "automerge": true
    }
  ],
  "platformAutomerge": true
}
```

`platformAutomerge` makes Renovate set GitHub's auto-merge on the PR, so
the required checks from step 3 are what actually hold the merge. Enable
the repository setting it depends on:

```sh
gh api -X PATCH repos/<owner>/<repo> -f allow_auto_merge=true
```

Open the renovate.json change as a PR; don't widen the update types
beyond what the gate can vouch for.

## Step 5. Pilot and verify

Test on one Renovate PR before trusting the repository to merge on its
own:

- Confirm automerge merges the PR once `CI Gate` (or each required check)
  is green.
- Make a required check go red once and confirm the PR does **not**
  merge.

Watch for a repository that already has `automerge: true` with no real
gate — fix it as part of the rollout rather than leaving it.

## Step 6. Report

A table: repo | bot | gate check(s) | ruleset updated | renovate
automerge | verified.

Below it, list the PRs you opened and any repository still missing a real
gate.
