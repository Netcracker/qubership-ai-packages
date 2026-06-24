---
name: markdown-line-length-120
description: Apply Markdown drafting and validation rules for Qubership repositories that pin markdownlint `MD013.line_length` to 120. Use when editing `*.md`, checking Markdown CI failures, or touching docs in repositories with Qubership markdownlint configuration.
---

# Markdown drafting and validation rules

Build every `.md` file with the non-autofixable rules in mind from the
first draft. Pasting in a long paragraph and rewrapping it afterwards is
wasted work.

Before editing or validating Markdown, first discover the repository's
actual markdownlint configuration instead of assuming defaults:

1. Inspect repository-local config paths such as
   `.github/linters/.markdownlint.yaml`,
   `.github/linters/.markdownlint.yml`,
   `.github/linters/.markdownlint.json`, `.markdownlint.yaml`,
   `.markdownlint.yml`, `.markdownlint.json`,
   `.markdownlint-cli2.yaml`, `.markdownlint-cli2.yml`, and
   `.markdownlint-cli2.json`.
2. If CI uses Super-Linter, inspect `.github/workflows/*` and
   `.github/super-linter.env`. Qubership workflows often download common
   configs from `netcracker/.github/config/linters` into `.github/linters`
   before running Super-Linter.
3. Prefer the same config path CI uses. If CI downloads a common config that
   is not present locally, fetch or copy that config when network access is
   available; otherwise state that local validation used the closest
   available config.

Run `markdownlint-cli2 --fix` only after selecting the repository config.
Then run markdownlint without `--fix` on the changed files before finishing,
for example:

```bash
npx markdownlint-cli2 --config .github/linters/.markdownlint.yaml docs/installation.md
```

For CI failures, reproduce the failing markdownlint command and config from
the workflow logs before patching content. Do not rely on `git diff --check`
or a pre-commit run as a replacement for markdownlint.

## Wrap body lines at 120 characters (`MD013`)

Plan the sentence around the wrap, not the other way round. Break at word
boundaries; never split `` `inline code` `` or a `[link](url)` span across
lines. List-item continuations indent by two spaces to line up with the
bullet content. Exempt from the limit: YAML frontmatter, fenced code blocks,
and pipe tables — do not reformat them to fit 120.

## One H1 per document (`MD025`)

The first heading is the title (`#`). All later sections are `##` or deeper.
A section break never gets promoted back to `#`, even when the document is
long.

## Named links, not bare URLs (`MD034`)

Write `[the SDK reference](https://example.com/sdk)`, not
`https://example.com/sdk` on its own. When the URL really is the link text
(citations, release notes), wrap it in angle brackets:
`<https://example.com/sdk>`.

## Language tag on every fenced code block (`MD040`)

`` ```yaml ``, `` ```bash ``, `` ```text ``, `` ```diff `` — always pick
one. Use `text` for plain output, directory listings, ASCII diagrams, or
fixtures with no syntax to highlight.

## Table column style (`MD060`)

Treat pipe tables as tool-verified content. Hand-formatting is easy to get
wrong, especially when cells contain escaped pipes such as `\|`.

When touching tables, run markdownlint with the discovered repository config.
If the project enables `MD060`, keep each column's pipe separators aligned
according to that rule and preserve escaped pipes inside cell text.
