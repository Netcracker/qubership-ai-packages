# qubership-development-practices

Qubership development workflow defaults for agent-assisted work in git
repositories: Conventional Commits, docs/test hygiene, and validation
before commits.

The package keeps the always-on instruction short and puts the detailed
workflow into skills:

- `conventional-commits` — focused Conventional Commit messages and
  commit preparation.
- `repo-quality-gate` — discover repository validation, check tests and
  docs, inspect GitHub Super-Linter configuration, and report skipped
  checks honestly.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/qubership-development-practices
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/qubership-development-practices@v1.0.0
```

Then run `apm install` and `apm compile` to merge the trigger into your
local `AGENTS.md` / `CLAUDE.md` and deploy the skills to the location
your agent reads.

## What this package does not replace

This package guides agents; it is not enforcement. Keep CI, pre-commit
hooks, commitlint, Super-Linter, and language-specific linters as the
mechanical source of truth.
