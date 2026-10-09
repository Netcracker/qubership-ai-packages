# doc-updater

A skill that brings a repository's documentation in line with the code changes on the current branch. It classifies
each change, maps it to the page that documents it, and edits that page in the format the page already uses.

The skill is `doc-updater`. The user invokes it by name or asks to update or sync the documentation; it does not fire
on its own and does not run before a commit.

## What it does

1. Builds a documentation map from the repository: which page holds the parameter reference, the installation
   procedure, the architecture, monitoring, troubleshooting, security, and feature pages. No path is assumed, so the
   skill works with `docs/public/`, a flat `docs/`, or a root `README.md`.
1. Collects the changes the branch introduces since the default branch, plus the staged changes and new files.
1. Classifies each change (Helm parameters, CRD fields, features, monitoring, alerts, architecture, security,
   developer workflow) and maps it to a page through the documentation map.
1. Applies small edits directly and shows a plan for anything larger: new pages, removed rows, rewritten sections.
1. Writes in the target page's own format and verifies tables and links.

When a change needs a page the repository does not have, the skill proposes a path beside the existing documentation
and asks before it creates the page.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/doc-updater
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/doc-updater@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the location your agent reads (`.claude/skills/`,
`.cursor/`, ...).

## Requirements

- A Git repository with an `origin` remote. The skill takes the default branch from `origin/HEAD`, falls back to
  `origin/main` or `origin/master`, and asks for the base branch when neither settles it.
- An English style skill (`english-us-developer-style` or `english-uk-developer-style`) for the prose it writes. The
  skill tells you when neither is installed.

## Typical use

- "Update the documentation for the changes on this branch."
- "The docs are out of date; sync them with the code."
- "Run doc-updater."

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.
