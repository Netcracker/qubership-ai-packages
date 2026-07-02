# apm-authoring

Authoring conventions for APM packages — instructions, skills, prompts,
agents, hooks, `apm.yml` — distilled from real agent-package reviews.
Apply them when you create or edit a `.apm/` tree.

This package is **for authors and maintainers** of APM packages. End
consumers of a library do not need it: the rules concern how you
*write* a skill, not how you *use* one. Install it as a
**devDependency** so it never ships in `apm pack` output and never
reaches downstream services.

## Install

```sh
apm install --dev Netcracker/qubership-ai-packages/agent-packages/apm-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
devDependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/apm-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to
pin, for example `v1.0.0`.

Then run `apm install`. It deploys the package and runs compile internally
for generated root context files and harness rules.

## What you get

- A short instruction that fires when the agent edits anything under
  `.apm/`, `apm.yml`, `*.agent.md`, `AGENTS.md`, `CLAUDE.md`. It tells
  the agent to load the `apm-authoring` skill instead of guessing.
- The skill itself
  ([`SKILL.md`](.apm/skills/apm-authoring/SKILL.md)) — package layout,
  the instruction-vs-skill decision, frontmatter rules, version
  policy, common authoring pitfalls.

## Typical use

1. `apm install --dev …` once per repo.
2. Open a `SKILL.md` (or create a new `agent-packages/<name>/`) and
   the agent picks up the rules automatically — no manual prompting
   needed.

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.
