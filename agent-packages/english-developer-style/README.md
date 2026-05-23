# english-developer-style

British-English-first style guidance for developer-facing text of any
length: Markdown docs and README content, code comments and docstrings
inside source files (`.go`, `.js`, `.ts`, `.py`, `.java`, `.rs`, `.kt`,
`.cs`, ...), commit messages, PR descriptions, changelog entries, UI
strings, error and log messages, and English-side localisation files
(`.po`, `.properties`, JSON i18n). Length does not matter — a one-line
`msgstr`, a `// FIXME: …` comment, or a three-word button label goes
through the same checklist as a multi-page README.

The skill fires on any task that touches English developer text:
writing, editing, rewriting, translating, localising, reviewing,
proofreading, verifying, auditing, double-checking, cross-checking, or
"checking the wording". If the request mentions English developer text,
the skill loads *before* the agent answers.

The skill encodes the judgement-based rules — voice, structure, AI-tell
avoidance, hedging, error-message empathy, dialect policy — that linters
cannot enforce reliably. Mechanical checks (dialect spelling,
terminology, inclusive-language substitutions, commit-message grammar)
belong in Vale, textlint, alex.js, or commitlint, not in this skill body.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/english-developer-style
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/english-developer-style@v1.0.0
```

Then run `apm install` and `apm compile` to merge the trigger into your
local `AGENTS.md` / `CLAUDE.md`.

## What you get

- A short instruction that fires on any task touching English
  developer text — writing, editing, translating, reviewing,
  proofreading, verifying. It tells the agent to load the
  `english-developer-style` skill instead of guessing.
- The skill itself
  ([`SKILL.md`](.apm/skills/english-developer-style/SKILL.md)) — voice,
  dialect policy, sentence craft, punctuation and AI-tell catalogue,
  hedging rules, per-surface modules for docs/comments/commits/PRs/
  changelogs/errors, a final-pass checklist, and an explicit
  "when to break the rules" clause.

## Pair with linters

The skill is deliberately silent on rules that machines do better.
Pair it with:

- **Vale** with the `Google` and `Microsoft` packages, plus a small
  project-local pack for GitLab-derived `FutureTense`, `CurrentStatus`,
  `SelfReferential`, and `SubstitutionWarning`.
- **Hunspell** `en_GB` (or `en_US`) for spelling, switched per project.
- **commitlint** with the Conventional Commits config.
- **alex.js** behind a per-project allowlist if you want inclusive-
  language hints; expect noise on technical vocabulary without one.

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.

## Background

Synthesised from a four-step editorial-research pipeline. The
[`research/english-developer-style/`](../../research/english-developer-style/)
folder has the prompts, candidate-source evaluations, and methodology
notes — useful if you want to adapt the skill to another dialect or
update it against new sources.
