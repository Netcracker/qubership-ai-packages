# Fix repository-specific CI

Fetch current workflow templates and paired `.properties.json` files from
[`Netcracker/.github/workflow-templates`](https://github.com/Netcracker/.github/tree/main/workflow-templates). Inspect
required inputs, secrets, permissions, and referenced action documentation before adapting them. Templates live in
`Netcracker/.github`; reusable actions live in
[`netcracker/qubership-workflow-hub`](https://github.com/netcracker/qubership-workflow-hub). Preserve working semantic
equivalents and never infer action identifiers or inputs from memory.

## `WF-003`: APM package updates

Fetch `apm-packages-update.yml` and its properties file. Netcracker provides `APM_UPDATE_TOKEN` as an organization-level
Actions secret. Use `secrets.APM_UPDATE_TOKEN` without asking the repository owner to create or provide a token, and
never read, copy, or invent its value.

An empty repository-level secret list or unavailable organization-secret listing does not mean the secret is missing.
Verify access for the target repository through organization-administrator evidence or an updater workflow run after
the workflow reaches the default branch. Only a run that cannot access the secret requires an organization
administrator to add the repository to the secret's selected repositories. Confirm any schedule change before writing
the workflow.

## `WF-004`: Build on push

Inspect the repository's actual build command and all workflows. Select a current template by purpose, show the source,
and ensure the adapted workflow triggers on `push` and executes that build.

## `WF-005`: Coverage generation

Read the test command, coverage tooling, and CI. Add the smallest step that generates a machine-readable report and
retains an accessible artifact or job result. Do not add a threshold or external publication. If the test command or
coverage format is unknown, list the missing input and keep remediation `UNAVAILABLE`.

## `WF-006`: Maven publication

Inspect every publishable POM, distribution management, settings use, and release workflow. Configure GitHub Packages,
not Maven Central, under this rule. Start from the current matching template and
[GitHub Maven registry instructions](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry).
List required secrets, variables, and permissions before applying. Require separate confirmation for coordinate or
release-strategy changes.

## `WF-007`: Dependency updater

Show existing integration evidence and ask the owner to choose Renovate or Dependabot; do not configure both. Limit
ecosystems and directories to repository manifests. Use the current [Renovate reference](https://docs.renovatebot.com/configuration-options/)
or [Dependabot reference](https://docs.github.com/code-security/dependabot/dependabot-version-updates/configuring-dependabot-version-updates)
and run the provider's validator when available.

## `WF-014`: External coverage publication

Activate this section only after the user selects the external coverage publication warning in the normal Apply flow.
Selecting other warnings or confirming critical fixes does not activate it. Reuse the provider choice if already given;
otherwise ask for Sonar, Codecov, or an equivalent provider. Configure only the selected provider. Keep unrelated
questions in the normal numbered list, with the choice to answer together or one at a time.

Choosing a provider is optional. Once chosen, finish its publication setup and verify delivery before reporting the
warning fixed. Coverage generation under `WF-005` remains independent. A local configuration or successful upload alone
is not proof of a processed coverage report.

### Organization credentials and variables

Netcracker provides organization-level Actions secrets for both services. Use the existing secrets without asking the
repository owner to create or paste tokens. Never read, copy, print, or invent their values. These are provider
credentials, not `GITHUB_TOKEN`, `APM_UPDATE_TOKEN`, or a GitHub personal access token.

| Setting | Scope and use |
| --- | --- |
| `secrets.SONAR_TOKEN` | Organization-managed Sonar analysis credential. Expose as `SONAR_TOKEN` to the scanner. |
| `vars.SONAR_PROJECT_KEY` | Repository Actions variable. Use the actual Sonar project key; for example, `Netcracker_qubership-logging-operator`. |
| `vars.SONAR_ORGANIZATION` | Organization Actions variable; the established SonarCloud organization is `netcracker`. |
| `vars.SONAR_HOST_URL` | Organization Actions variable; the established service is `https://sonarcloud.io`. |
| `secrets.CODECOV_TOKEN` | Organization-managed Codecov upload credential. Pass as the action's `token` input. |

Read effective variables and preserve existing valid overrides. A project key is not a secret. An empty repository
secret list does not prove that an inherited secret is missing; the repository's
`repos/{owner}/{repo}/actions/organization-secrets` endpoint can confirm inherited secret names without exposing values.
Unavailable metadata is not evidence that credentials are absent; follow the skill's permission boundary for failed
operations and continue independent work.

Use the established Netcracker setup assumption: the Codecov GitHub App covers the whole organization, including new
repositories, and the shared upload secret is available. Do not ask preliminary app-access or token-creation questions.
Investigate access only when an actual run reports an authentication or repository-access failure. For another
organization, use its documented setup or obtain the missing prerequisites.

### Sonar sequence

1. Find the target repository's project in the existing Sonar organization and confirm its GitHub repository binding.
   Read the actual project key; naming conventions alone do not prove that a project exists. If project creation,
   import, or binding is still needed, identify that prerequisite and obtain the necessary owner action or authorized
   access. Setting a GitHub variable alone does not prove Sonar project provisioning.
2. Set the confirmed key as the repository Actions variable `SONAR_PROJECT_KEY`. Read back its value. Use existing
   organization and host variables and the shared `SONAR_TOKEN`. Select CI-based analysis with GitHub Actions in Sonar;
   preserve an existing correct setup. Show proposed external changes before applying them under the normal Apply
   permission boundary.
3. Inspect the current central `go-build.yaml` template for Go projects. For reusable Go builds, inspect
   [`generic-go-build.yaml`](https://github.com/Netcracker/qubership-core-infra/blob/main/.github/workflows/generic-go-build.yaml)
   and its inputs. Use the
   [monitoring operator caller](https://github.com/Netcracker/qubership-monitoring-operator/blob/main/.github/workflows/test-sonar-go-coverage.yaml)
   as a working example. Resolve the selected workflow or action ref to a full commit SHA. For other stacks, use the
   matching build tool and current Sonar documentation; do not introduce a Go workflow.
4. Reuse the real test command and coverage scope. For Go, produce `coverage.out` and pass its actual scanner-side path
   through `sonar.go.coverage.reportPaths`. When tests and scanning run in different jobs, retain and download the
   coverage artifact first. Configure `sonar-project.properties` for the target source and tests; do not copy another
   repository's exclusions, rule suppressions, or coverage package list. Pass the confirmed project, organization,
   and host as scanner parameters. Pass `SONAR_TOKEN` explicitly to reusable workflows, or preserve working inheritance.
5. Keep tests running for bot and fork PRs. Inspect event and secret availability before enabling publication; preserve
   intentional supported-event restrictions and report skipped analysis separately. Never expose secrets to untrusted
   PR code to make scanning work. Verify delivery using the completion sequence below.

### Codecov sequence

1. Reuse the shared `CODECOV_TOKEN`. No Sonar-style project-key variable is needed for the established GitHub Actions
   integration. Use the normal repository and commit detection; inspect action documentation before adding overrides.
2. Inspect the target test tooling and the
   [profiler workflow](https://github.com/Netcracker/qubership-profiler-agent/blob/main/.github/workflows/build.yaml).
   It uploads Go coverage profiles, UI LCOV, and Java JaCoCo XML. Generate only the formats needed by the target
   repository and preserve its existing build. Do not copy the profiler's multi-language build into a single-stack repo.
3. Add `codecov/codecov-action` pinned to a verified full commit SHA after report generation. Pass
   `token: ${{ secrets.CODECOV_TOKEN }}`, explicit `files`, `disable_search: true`, and `fail_ci_if_error: true`.
   Make upload failures visible without introducing a minimum coverage threshold. Keep tests independent of upload
   eligibility for bots and forks; follow the selected action's supported authentication behavior for those events.
4. Add `codecov.yml` only when report grouping, path correction, or status policy needs it. The profiler uses language
   flags, path fixes, carryforward, and an expected upload count of three. Derive these from the target repository;
   never copy that count or carryforward policy blindly. Preserve existing status policy. Obtain a user decision
   before enabling blocking coverage thresholds or changing informational statuses.
5. Publish and verify the chosen setup using the completion sequence below. A new token, OIDC migration, or extra
   repository variable is not part of the default Netcracker setup.

### Completion and remaining questions

Use the normal Apply flow: make authorized local changes first and collect only missing facts or decisions. A selected
warning does not authorize unrelated provider configuration, quality fixes, or changes to merge requirements. When
publication or an external change still needs approval, present the concrete diff and targets before asking.

After authorized publication, verify a real eligible CI run, preferably a default-branch baseline and then a PR:

1. Record the analyzed commit SHA and confirm tests produced the expected coverage files.
2. Confirm the uploader or scanner read those files and successfully submitted them.
3. Confirm the provider processed that same SHA and shows coverage for the expected files or components. For multiple
   reports, check all expected uploads; carried-forward coverage does not prove a fresh upload.
4. Confirm the provider returned a GitHub check or commit status for that SHA. Report coverage and quality-gate results
   separately from successful delivery and from whether GitHub requires the check for merging.

Sonar can accept an analysis and return a failed Quality Gate while the scanner workflow succeeds. Codecov informational
statuses can succeed without satisfying a coverage threshold. Neither outcome alone means publication is broken.
Do not change thresholds, fix unrelated quality findings, or make a check required merely to finish this warning.

If a run is skipped, processing is pending, or no real run is authorized, report configuration as prepared and delivery
as unverified; keep the warning open. If an actual run fails on access, identify the affected service and ask the
organization administrator to correct that repository's access. Missing project prerequisites keep remediation
`UNAVAILABLE`; complete independent changes and present the remaining questions through the normal Apply flow.

Sources: [Netcracker secrets and variables](https://github.com/Netcracker/qubership-workflow-hub/blob/main/docs/secrets-and-vars.md),
[Sonar project setup](https://docs.sonarsource.com/sonarqube-cloud/managing-your-projects/administering-your-projects/setting-up-project),
[Sonar GitHub Actions](https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/ci-based-analysis/github-actions-for-sonarcloud),
[Codecov action](https://github.com/codecov/codecov-action), and
[Codecov tokens](https://docs.codecov.com/docs/codecov-tokens).
