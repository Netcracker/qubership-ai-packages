# markdown-line-length-120

Short Markdown drafting instruction for repositories pinning
markdownlint `MD013.line_length` to 120 — the Qubership default in
[netcracker/.github](https://github.com/netcracker/.github/blob/main/config/linters/.markdownlint.json).

It covers the four rules an autofixer cannot resolve, so the agent has
to build them into the first draft:

- `MD013` — wrap body lines at 120 characters
- `MD025` — one top-level `#` heading per document
- `MD034` — write URLs as `[link text](url)`, never bare
- `MD040` — every fenced code block declares a language

Everything else (`MD022`, `MD032`, `MD060`, `MD029`, `MD026`, `MD047`,
trailing whitespace, ...) goes through `markdownlint-cli2 --fix` in a
pre-commit hook — the agent should not spend tokens on what tooling
already handles.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/markdown-line-length-120
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/markdown-line-length-120@v1.0.0
```

Then run `apm install` and `apm compile` to merge the trigger
instruction into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body to the location your agent reads (`.github/skills/...`,
`.cursor/rules/...`, etc.).

## Pair with autofix

Wire the autofixable rules into pre-commit so the agent never has to
think about blank lines around headings, ordered-list prefixes, table
column spacing, trailing newlines, and so on:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/DavidAnson/markdownlint-cli2
  rev: v0.18.1  # illustrative — pin to the latest tag from the upstream releases page
  hooks:
    - id: markdownlint-cli2-fix
```

Or run it on demand:

```sh
npx markdownlint-cli2 --fix '**/*.md'
```

## A different line-length budget

The `120` is hard-coded — it is in the package name and in every rule
description. Projects on a different limit (80, 100, ...) should fork
this package, rename it, and update the skill body. Mixing limits
across one repository is not the use case.
