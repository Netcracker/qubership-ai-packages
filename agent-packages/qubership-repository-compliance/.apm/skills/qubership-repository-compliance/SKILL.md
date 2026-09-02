---
name: qubership-repository-compliance
description: Audit or fix a Netcracker or Qubership GitHub repository for required files, workflows, Grand Report, APM Essentials, coverage, topics, and repository settings.
---

# Qubership repository compliance

## Prerequisite

Require `gh` on `PATH`. Derive the GitHub host from the target repository remote and require
`gh auth status --active --hostname <host>` to succeed. Never use `--show-token`. If `gh` is missing or authentication
fails, stop and tell the user to install or authenticate GitHub CLI.

Do not query the repository Actions-permissions API (`repos/{owner}/{repository}/actions/permissions*`); none of the
catalog checks depends on it. If a tool reports a `403` from this endpoint, ignore it and omit it from unavailable
evidence and the user report.

If any other `gh` operation fails because the active token lacks permission, stop that operation and tell the user
which repository operation needs additional access. Do not treat missing access as a compliance violation or request
broader permissions yourself.

## Permission boundary

Default to `Audit`. Audit is read-only: do not edit files, change GitHub settings, create pull requests, commit, push,
merge, or close anything.

`Apply` reuses a complete Audit from the current task and rechecks only confirmed checks; run a full Audit only when
none exists. Show the descriptive check names, exact targets, proposed file and external changes, and unavailable
prerequisites. Apply only the checks or batch the user confirms, even if the initial request says to fix everything.
Permission for a target repository does not cover `Netcracker/.github` or `Netcracker/qubership-workflow-hub`.

README remediation is always separate from other Apply work. Never include `FILE-001` in an Apply batch. When it
fails, ask whether the user wants the assistant to prepare a README change. After approval, edit only the README, show
its diff, and ask the user to accept or revert it before committing, publishing, or combining it with other changes.
If the user rejects it, revert only the assistant's README edit.

Keep finding IDs internal for catalog evaluation and fix routing. Outside the report table's `ID` column, use a clear
descriptive check name in the user's language in every report, question, status, and confirmation. Accept an ID supplied
by the user and map it to the descriptive name without asking them to remember the catalog.

Treat every existing file, workflow, configuration, and setting as maintained repository content. A finding authorizes
only the smallest change needed for that ID, never replacement with a central template. Do not change a working
semantic equivalent. Patch a failing artifact in place while preserving unrelated content and repository-specific
configuration; add the central file unchanged only when no equivalent exists. Before any full-file replacement,
deletion, rename, or command that may rewrite additional files, show the affected paths and diff and obtain separate
confirmation. Preview generators in an isolated temporary copy when necessary, apply only confirmed paths, and stop
on unexpected changes. Never discard existing dirty-worktree changes.

Never merge or close a pull request. Read back every external mutation and return its evidence or pull request URL.

## Fix routing

Do not read `references/fixes/` during Audit. After Apply confirmation, read only the matching heading or file:

| Finding IDs | Fix instructions |
| --- | --- |
| `FILE-001` to `FILE-004` | matching heading in `references/fixes/repository-files.md` |
| `FILE-005` to `FILE-009`, `WF-001`, `WF-002`, `WF-008` to `WF-013` | `references/fixes/central-files.md` |
| `WF-003` to `WF-007`, `WF-014` | matching heading in `references/fixes/project-ci.md` |
| `GH-001` to `GH-005` | matching heading in `references/fixes/github-settings.md` |

If a required source, permission, command, owner, secret, or provider choice is unavailable, mark remediation
`UNAVAILABLE`; do not invent a substitute.

## Audit

1. Resolve the exact checkout and `owner/repository`. Record the branch, dirty state, remotes, and default branch.
2. Read repository instructions, root files, manifests, build files, `.qubership/`, and every workflow. Detect workflow
   behavior from triggers, actions, commands, and referenced configuration, not filenames.
3. Treat a repository as a code repository only when it has maintained source and a build or test entry point. Assess
   coverage applicability separately: require coverage only when maintained executable source is a material repository
   deliverable. Do not use file count or lines of code alone. Small CI helpers, generators, examples, fixtures, tests,
   or scripts that only validate documentation or configuration do not make coverage applicable. Record the relevant
   source paths and their role. When no material executable source exists, mark `WF-005` and `WF-014` `NOT APPLICABLE`
   and do not propose coverage tooling or publication. Treat a repository as Maven only when it has a publishable Maven
   project, not an incidental fixture.
4. Use `gh` to inspect metadata, topics, rulesets or branch protection, workflow runs, and variables. Never expose
   secret values. Use GitHub's community-profile API and local paths for effective community files. Mark only evidence
   blocked by repository permissions as `UNAVAILABLE`.
5. Evaluate all 28 checks below in order.

Use `PASS`, `ERROR`, `CONDITIONAL ERROR`, `WARNING`, `UNAVAILABLE`, or `NOT APPLICABLE`. Overall status is
`NON-COMPLIANT` for any error, `INCOMPLETE` when only mandatory evidence is unavailable, and `COMPLIANT` otherwise.

### Repository files

| ID and violation | Inspect and applicability | Source |
| --- | --- | --- |
| `FILE-001` README: missing or smaller than 1024 bytes `ERROR` | Match the root README case-insensitively and measure its file size in bytes, as Grand Report C023 does. A README of at least 1024 bytes passes without content scoring, authoring advice, or confirmation. | [Grand Report C023](https://github.com/exadmin/opensource_team_monitor/blob/d2e7ede1c90fcce9bfbff2d467f9dddd100fb171/src/main/java/com/github/exadmin/ostm/collectors/impl/repos/devops/ReadmeFilePresence.java#L17-L40) |
| `FILE-002` Apache 2.0 `LICENSE`: `ERROR` | Compare normalized root `LICENSE` text with the official license; accept another license only with a documented legal exception. | [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt), Grand Report C022 |
| `FILE-003` CODEOWNERS: `ERROR` | Accept `.github/CODEOWNERS`, root `CODEOWNERS`, or `docs/CODEOWNERS`; verify syntax and report unresolved owners when the API permits. | [GitHub CODEOWNERS](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), Grand Report C025 |
| `FILE-004` `qubership-repo-essentials`: `ERROR` | Require a direct root dependency, `claude`, `codex`, and `cursor` targets, a resolved lock entry, committed generated assets for every target, and successful `apm audit --ci --no-policy`; organization policy discovery is outside this check. Nonempty `apm.yml` alone fails. | [Package manifest](https://github.com/Netcracker/qubership-ai-packages/blob/94b47bfd4171396bcacdb2d6c534470d60b1230f/agent-packages/qubership-repo-essentials/apm.yml), Grand Report C050 |
| `FILE-005` `.qubership/grand-report.json`: `ERROR` | Require valid JSON at the exact path; `{}` passes. Do not confuse it with central Grand Report overrides. | [Broadcast configuration](https://github.com/Netcracker/.github/blob/main/.github/broadcast-files-config.yaml), Grand Report C045 |
| `FILE-006` effective `CONTRIBUTING.md`: `ERROR` | Accept a usable local file or GitHub-inherited Netcracker default; record the effective source URL. A local file overrides the default. | [GitHub default community files](https://docs.github.com/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), [Netcracker default](https://github.com/Netcracker/.github/blob/main/.github/CONTRIBUTING.md) |
| `FILE-007` effective `SECURITY.md`: `ERROR` | Accept a usable local policy or inherited Netcracker default; require a vulnerability-reporting path and never invent contacts. | [GitHub security policy](https://docs.github.com/code-security/getting-started/adding-a-security-policy-to-your-repository), [Netcracker default](https://github.com/Netcracker/.github/blob/main/.github/SECURITY.md) |
| `FILE-008` effective `CODE-OF-CONDUCT.md`: `ERROR` | Accept a usable local file or inherited Netcracker default; never invent enforcement contacts. | [GitHub default community files](https://docs.github.com/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), [Netcracker default](https://github.com/Netcracker/.github/blob/main/.github/CODE-OF-CONDUCT.md) |
| `FILE-009` `.editorconfig` and `.gitattributes`: `WARNING` | Check presence only. Existing contents may be repository-specific; when either file is missing, offer the corresponding central file without treating a local override as a violation. | [Broadcast configuration](https://github.com/Netcracker/.github/blob/main/.github/broadcast-files-config.yaml) |

### Workflows

| ID and violation | Inspect and applicability | Source |
| --- | --- | --- |
| `WF-001` CLA enforcement: `ERROR` | Detect active CLA enforcement by behavior, not only `cla.yaml`. | [CLA template](https://github.com/Netcracker/.github/blob/main/workflow-templates/cla.yaml), Grand Report C024 |
| `WF-002` Conventional Commits: `ERROR` | Accept the central template or an active semantic equivalent for commits or PR titles. | [Conventional Commits template](https://github.com/Netcracker/.github/blob/main/workflow-templates/pr-conventional-commits.yaml), Grand Report C026 |
| `WF-003` APM package updates: `ERROR` | Require a scheduled updater that can open a pull request. Netcracker provides `APM_UPDATE_TOKEN` as an organization-level secret; verify only that the target repository can use it. | [APM update template](https://github.com/Netcracker/.github/blob/main/workflow-templates/apm-packages-update.yml) |
| `WF-004` build on `push`: `CONDITIONAL ERROR` for code repositories | Inspect all triggers and build steps; a workflow name does not prove a build. | [Netcracker workflow templates](https://github.com/Netcracker/.github/tree/main/workflow-templates), Grand Report C034 |
| `WF-005` CI coverage generation: `CONDITIONAL ERROR` when coverage applies | Require tests to generate coverage and retain an accessible CI result; do not require a percentage threshold or external publisher. Mark `NOT APPLICABLE` when executable code is only incidental repository tooling. | [GitHub workflow artifacts](https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts), Grand Report C020 |
| `WF-006` allowed Maven publication: `CONDITIONAL ERROR` for Maven repositories | Inspect publishable POMs and workflows. Maven Central fails this rule; GitHub Packages passes. | [GitHub Maven registry](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry), Grand Report C056 |
| `WF-007` dependency updater: `CONDITIONAL ERROR` for code repositories | Require one working Renovate or Dependabot configuration and evidence the selected service can run; do not require both. | [Renovate](https://docs.renovatebot.com/configuration-options/), [Dependabot](https://docs.github.com/code-security/dependabot/dependabot-version-updates/configuring-dependabot-version-updates) |
| `WF-008` Super-Linter: absent `WARNING`; broken `ERROR` | Accept working central or intentional custom configurations. Verify workflow and referenced configuration; byte differences from central are not a failure. | [Super-Linter template](https://github.com/Netcracker/.github/blob/main/workflow-templates/super-linter.yaml), Grand Report C027 |
| `WF-009` automatic PR labeler: `WARNING` | Inspect active labeler behavior, its configuration, and only labels referenced there. | [Labeler template](https://github.com/Netcracker/.github/blob/main/workflow-templates/automatic-pr-labeler.yaml), Grand Report C028 |
| `WF-010` PR title lint: `WARNING` | Inspect active PR-title enforcement; the central workflow is recommended, not mandatory. | [Title-lint template](https://github.com/Netcracker/.github/blob/main/workflow-templates/pr-lint-title.yaml), Grand Report C029 |
| `WF-011` profanity filter: `WARNING` | Inspect active filtering; teams may decline it. | [Profanity template](https://github.com/Netcracker/.github/blob/main/workflow-templates/profanity-filter.yaml), Grand Report C030 |
| `WF-012` broken-link checker: `WARNING` | Inspect active link checking and its last available run; a configured but failing checker remains a warning with evidence. | [Link-checker template](https://github.com/Netcracker/.github/blob/main/workflow-templates/link-checker.yaml), Grand Report C032 |
| `WF-013` PR assigner: `WARNING` | Inspect whether pull requests are assigned from `CODEOWNERS`; repositories may operate without automatic assignment. | [PR assigner template](https://github.com/Netcracker/.github/blob/main/workflow-templates/pr-assigner.yml) |
| `WF-014` external coverage publication: `WARNING` when coverage applies | Validate an existing Sonar, Codecov, or equivalent uploader. Do not require publication when `WF-005` passes. Mark `NOT APPLICABLE` with `WF-005` when the repository has no material executable source. | [Sonar coverage](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/test-coverage-parameters), [Codecov upload](https://docs.codecov.com/docs/codecov-uploader), Grand Report C020 |

Keep `WF-005` coverage generation separate from optional `WF-014` publication.

### GitHub parameters

| ID and violation | Inspect and applicability | Source |
| --- | --- | --- |
| `GH-001` default branch `main`: `ERROR` | Read GitHub's default branch; before proposing a rename, inspect branch references, workflows, badges, and release automation. | [Reference main ruleset](https://github.com/Netcracker/.github/blob/main/config/Protect-main-branch.json) |
| `GH-002` registered `qubership-*` topic: `ERROR` | Compare GitHub repository topics with the exact repository entry in the central registry; this is not an issue or PR label. | [Topic registry](https://github.com/Netcracker/.github/blob/main/config/topics.json), Grand Report C018 |
| `GH-003` nonempty description: `ERROR` | Read GitHub metadata; ground proposed public text in the README and require owner confirmation. | [GitHub repository API](https://docs.github.com/rest/repos/repos#get-a-repository) |
| `GH-004` public and nonarchived: `WARNING` | Report private or archived state as a possible deliberate exception; never change either during general Apply. | [Repository visibility](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility), [archiving](https://docs.github.com/repositories/archiving-a-github-repository/archiving-repositories) |
| `GH-005` direct commits to `main` blocked: `WARNING` | Inspect rulesets or branch protection for a pull-request requirement on the default branch; a single-maintainer exception remains a warning. | [Reference main ruleset](https://github.com/Netcracker/.github/blob/main/config/Protect-main-branch.json), [GitHub rulesets](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) |

## Report

Start with `COMPLIANT`, `NON-COMPLIANT`, or `INCOMPLETE` and one sentence explaining why. Return all 28 checks in a
localized Markdown table with exactly these columns: `ID`, `Status`, `Check and evidence`, `Minimal remediation`.
Render row statuses as `ERROR`, `WARNING`, `INFO`, or `PASS`; map unavailable, not-applicable, and inapplicable
conditional checks to `INFO`. Sort rows in that order and preserve catalog order within each status. Put applicability,
evidence, source, and reason in `Check and evidence`. List unavailable evidence only when any exists. Then list proposed
Apply batches by descriptive check name, excluding `FILE-001`. If `FILE-001` is an error, follow the batches with its
separate README-remediation question. Do not read fix references until the user confirms a batch or README remediation.

Do not add findings for open pull request count; email or CyberFerret scanning; language versions; pull request
templates; universal release, SBOM, license, Release Drafter, security scan, or OSSF workflows; mandatory Sonar or
Codecov; unrelated labels; merge methods; Homepage; `.gitignore`; a compliance CI gate; subjective documentation
scores; or minimum coverage.
