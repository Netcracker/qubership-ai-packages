# qubership-common-essentials

APM package with the part of the Qubership agent setup that a repository and a developer machine share. Do not install
it on its own: install [`qubership-repo-essentials`](../qubership-repo-essentials/) in a repository, or
[`qubership-user-essentials`](../qubership-user-essentials/) on a developer machine. Both depend on this package.

## What it includes

The package requires Conventional Commits and an `Assisted-by:` trailer in commit messages, and includes these
dependencies:

- [`apm-authoring`](../apm-authoring/): guidelines for authoring APM packages (instructions, skills, prompts, agents,
  hooks).
- [`english-us-developer-style`](../english-us-developer-style/): American-English style for developer-facing text.
- [`markdown-line-length-120`](../markdown-line-length-120/): Markdown drafting rules for repositories that pin
  markdownlint `MD013.line_length` to 120.
- [`change-description-authoring`](../change-description-authoring/): structure and content rules for commit messages,
  pull request descriptions, and changelog entries.
- [`docs-page-authoring`](../docs-page-authoring/): structure and content rules for README files and other
  documentation pages.
- [`qubership-workflow-hub-usage`](https://github.com/Netcracker/qubership-workflow-hub/tree/main/agent-packages/qubership-workflow-hub-usage):
  conventions for GitHub Actions workflows built on qubership-workflow-hub.

## Adding a package to the bundle

A package that belongs both in a repository and on a developer machine goes here. Add the dependency to `apm.yml` and
bump the version of this package and of both umbrellas that depend on it.
