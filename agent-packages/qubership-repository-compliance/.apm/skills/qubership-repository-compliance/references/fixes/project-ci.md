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

This fix is optional. Ask the user to choose Sonar, Codecov, or an equivalent provider, then verify its organization
integration, variables, and secrets. Do not add dummy keys, tokens, or upload steps. Keep the warning and report setup
steps when prerequisites are absent. Publication is never required when `WF-005` passes.

Do not recreate a workflow from memory.
