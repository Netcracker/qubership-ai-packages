---
name: repo-quality-gate
description: Discover and run repository validation before commits or completion. Use after code, config, docs, workflow, dependency, or build changes.
---

# Repository quality gate

Before committing or reporting completion in a git repository, verify the
change with the checks the repository already defines. Prefer local,
repo-native commands over inventing new validation commands.

## Discover validation entry points

Inspect the repository before choosing commands:

- `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, and docs that
  describe build, test, lint, or commit conventions.
- `package.json`, `Makefile`, `justfile`, `Taskfile.yml`, `mvnw`,
  `gradlew`, `go.mod`, `pyproject.toml`, `tox.ini`, `pytest.ini`,
  `pom.xml`, and similar language-specific entry points.
- `.pre-commit-config.yaml`, `.editorconfig`, `.gitattributes`, and
  formatter or linter configs in the repo root.
- `.github/workflows/*` for CI commands and required checks.
- `.github/linters/*` for GitHub Super-Linter configuration.

Use the narrowest command that covers the changed surface. Run broad
suite commands only when the change is cross-cutting or no narrower
command exists.

## Tests and docs

For every code or behavior change:

- Check whether tests need to be added or updated.
- Run the relevant existing tests.
- If tests are not changed, be ready to explain why existing coverage is
  enough or why the change is not testable locally.

For user-facing, API, CLI, configuration, build, chart, workflow, or
operational changes:

- Check whether docs, examples, changelogs, or generated references need
  updates.
- If docs are not changed, be ready to explain why.

## Linters and formatters

Run the repo's existing lint or format-check path before committing:

- Prefer scripts such as `npm run lint`, `npm test`, `make lint`,
  `make test`, `go test ./...`, `mvn test`, `./gradlew test`,
  `pre-commit run --files ...`, or documented equivalents.
- Respect `.editorconfig` and language formatter configs. Do not reformat
  unrelated files.
- If a formatter has a check mode, use check mode unless the user asked
  for formatting or the repo convention is to autoformat before commit.

## GitHub Super-Linter

When the repository uses Super-Linter, treat its workflow and config as
the source of truth:

1. Inspect `.github/workflows/*` for `super-linter`,
   `github/super-linter`, `super-linter/super-linter`, or inherited
   Qubership workflow usage.
2. Read settings such as `LINTER_RULES_PATH`, `VALIDATE_*`,
   `FILTER_REGEX_INCLUDE`, `FILTER_REGEX_EXCLUDE`, `DEFAULT_BRANCH`,
   and `VALIDATE_ALL_CODEBASE`.
3. Read config files under `.github/linters/`, such as
   `.yaml-lint.yml`, `.markdownlint.json`, `.eslintrc*`,
   `.jscpd.json`, and language-specific configs.
4. Prefer repo-native commands that use the same configs when they exist.
5. Run Super-Linter locally only when practical for the repository and
   environment. It commonly requires Docker, network access, and CI-like
   environment variables, so do not make it the first choice when a
   focused native command covers the changed files.

If local Super-Linter execution is needed, derive the command from the
workflow configuration instead of guessing. Keep the run scoped to the
changed files when the workflow supports that mode.

## Before final response

Report:

- validation commands run and their results
- docs decision
- tests decision
- any skipped checks and the reason

Do not claim validation passed unless the command actually completed
successfully in the current workspace.
