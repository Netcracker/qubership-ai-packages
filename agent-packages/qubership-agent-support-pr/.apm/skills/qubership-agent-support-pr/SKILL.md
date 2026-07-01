---
name: qubership-agent-support-pr
description: >
  Prepare a pull request that adds Qubership baseline agent support to a
  repository: install qubership-essentials, run apm install for
  repository-declared harnesses, commit generated agent assets, and configure
  generated-file attributes and Super-Linter exclusions.
---

# Qubership agent support PR

Use this skill when the user asks to onboard a repository to Qubership baseline
agent support, install `qubership-essentials`, or create a PR that adds
generated APM assets for Claude, Codex, Cursor, or another requested harness.

The PR should be small: APM configuration, generated assets, generated-file
metadata, linter exclusions, and validation evidence.

## Target selection

Default targets for a new repository are `claude`, `codex`, and `cursor`.

Treat an existing `apm.yml` `targets` list as repository intent only when the
repository already appears onboarded to APM, for example when it also has
`apm.lock.yaml`, committed/generated target assets (`.claude/`, `.codex/`,
`.cursor/`), or repository documentation that names the supported harnesses.

Do not treat a newly created or bootstrap-only `apm.yml` as a narrower harness
signal by itself. If the repository has no durable APM metadata and no clear
harness-specific signal, use the default targets: `claude,codex,cursor`.

If the repository has clear harness-specific signals such as `.codex/`,
`.claude/`, `.cursor/`, agent settings, or repository documentation that points
to a narrower harness set, preserve the detected harness set and ask the user
before adding or removing targets.

Ask the user before changing targets whenever durable target intent is ambiguous.
Do not silently broaden an existing onboarded single-harness setup to the
default target set.

## Repository read

Before editing, inspect the target repository:

```bash
git status --short --branch
git remote -v
if command -v rg >/dev/null 2>&1; then
  rg --files --hidden \
    -g '!.git/**' \
    -g '!node_modules/**' \
    -g 'apm.yml' \
    -g 'apm.lock.yaml' \
    -g '.gitattributes' \
    -g '.apm/**' \
    -g '.agents/**' \
    -g '.claude/**' \
    -g '.codex/**' \
    -g '.cursor/**' \
    -g '.github/super-linter.env' \
    -g '.github/linters/**' \
    -g '.github/workflows/**'
else
  find . \
    \( -path './.git' -o -path './node_modules' \) -prune -o \
    \( \
      -name 'apm.yml' -o \
      -name 'apm.lock.yaml' -o \
      -name '.gitattributes' -o \
      -path './.apm/*' -o \
      -path './.agents/*' -o \
      -path './.claude/*' -o \
      -path './.codex/*' -o \
      -path './.cursor/*' -o \
      -path './.github/super-linter.env' -o \
      -path './.github/linters/*' -o \
      -path './.github/workflows/*' \
    \) -print
fi
```

Also read readme files, validation docs, and repository-specific layout before
choosing checks. Preserve unrelated user edits and stage only onboarding files.
Pay attention to all repository checks and workflows. Do not assume a setting
for one tool affects another check unless the repository configuration shows
that connection.

## Branch

Create a dedicated branch unless the user already selected one:

```bash
git checkout -b chore/add-apm-agent-support
```

Use the repository's existing branch naming convention when one is obvious.

## Configure

Choose `TARGETS` from the Target selection rules above, then run the bundled
script from the repository root to create or update APM targets, generated-file
attributes, and Super-Linter exclusions:

```bash
CONFIGURE_APM_AGENT_SUPPORT_SCRIPT="$(find . \
  -path "*/skills/qubership-agent-support-pr/scripts/configure-apm-agent-support.sh" \
  -type f \
  | head -n 1)"
test -n "${CONFIGURE_APM_AGENT_SUPPORT_SCRIPT}"
"${CONFIGURE_APM_AGENT_SUPPORT_SCRIPT}" --targets "${TARGETS}"
```

Set `TARGETS` to `claude,codex,cursor` only for new repositories with no APM
metadata and no narrower harness signal, or when the user confirms that target
change.

The script updates:

- creates `apm.yml` with `apm init -y --target <targets>` when the repository
  does not have APM metadata yet;
- `apm.yml` `targets`;
- `.gitattributes` entries for generated APM install assets;
- `.github/super-linter.env` `FILTER_REGEX_EXCLUDE` for Super-Linter
  checks, including Markdown and natural-language linters.

Do not exclude `.apm/**`, docs, source code, roles, playbooks, workflows, or
handwritten repository configuration.
Do not automatically edit unrelated workflow or linter configuration. Inspect
failures first and choose the smallest repository-appropriate fix.

## Install

Install `qubership-essentials`, then rely on `apm.lock.yaml` for the resolved
revision:

```bash
apm install \
  Netcracker/qubership-ai-packages/agent-packages/qubership-essentials
```

Do not pass `--target` to `apm install`; targets belong in `apm.yml`, so future
bare installs remain reproducible.

Do not compact `apm.lock.yaml`. Transitive dependencies, `depth`, and
`resolved_by` entries are part of the lockfile and must remain. Keep generated
hooks for enabled harnesses.

## Generated assets

Commit generated assets produced for the configured targets. Typical paths are:

- `.agents/**`
- `.codex/**`
- `.claude/apm-hooks.json`
- `.claude/settings.json`
- `.claude/rules/**`
- `.claude/skills/**`
- `.cursor/hooks.json`
- `.cursor/rules/**`

Do not hand-edit dependency-generated skills, rules, hooks, or instructions.
Change the source package and reinstall instead.

## Local `.apm/instructions`

Create `.apm/instructions/<repository-name>.instructions.md` only when the
repository needs short native rules that should deploy into harness-specific APM
outputs through `apm install`.

Do not create the file just because APM exists. Keep local instructions short,
repository-specific, and action-oriented. Avoid duplicating readme content.

## Validation

Run checks that match the changed files:

```bash
apm targets
apm audit --ci
git diff --check
```

If `apm audit --ci` reports false Copilot instruction drift while Copilot is not
a target and `.github/` exists, check microsoft/apm#1924 before working around
it. Do not fix this by deleting transitive lockfile entries or allowed harness
hooks.

For Markdown changes, run the repository's markdownlint configuration when
available. For Super-Linter repositories, confirm `FILTER_REGEX_EXCLUDE` covers
generated APM install files. `FILTER_REGEX_EXCLUDE` only configures
Super-Linter. It does not configure independent repository checks unless those
checks explicitly load the same environment file. Inspect each failing check's
workflow, configuration, and logs before changing anything. If a check fails on
generated APM install files, decide whether the right fix is a
repository-specific exclude, a generated-file marker, a targeted content change,
or an issue against the linter or shared workflow.

Run repository-specific syntax or test commands discovered from workflows and
docs. Examples: Ansible syntax checks, Helm template checks, unit tests, or
workflow linting.

After creating or updating the pull request, wait for GitHub checks and inspect
failures before handing the PR back:

```bash
gh pr checks --watch
```

If `gh pr checks --watch` is unavailable, use the repository's GitHub checks UI
or the GitHub API. Do not report the PR as ready while any required or relevant
check is still pending or failing. If a check fails for a pre-existing or
unrelated reason, document the exact check name, failure reason, and evidence in
the PR body or final response.
If the failure looks like a tool or shared workflow bug, create or propose a
focused issue with the failing file path, check name, tool version, expected
behavior, actual behavior, and a minimal reproduction from the generated APM
file.

## PR

Before committing:

- Confirm `apm targets` matches the requested harnesses.
- Confirm generated hook files remain for enabled harnesses.
- Confirm `.github/instructions/**` exists only when Copilot is enabled.
- Confirm `apm.lock.yaml` keeps transitive dependencies.
- Confirm generated-file exclusions do not hide source files.
- Confirm all relevant PR checks and repository workflows have been inspected
  when they match generated APM install files.

Commit with a conventional message such as:

```text
chore: add APM agent support
```

In the PR body, summarize:

- Added `qubership-essentials`.
- Installed target harnesses and generated assets.
- Generated-file attributes and Super-Linter exclusions.
- Validation commands and results.
