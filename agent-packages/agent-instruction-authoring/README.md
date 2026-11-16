# agent-instruction-authoring

An APM package that helps agents write and change the text another agent follows: a `SKILL.md`, an `AGENTS.md` or
`CLAUDE.md`, a rules file, an agent persona, a review checklist, or a reusable brief for a subagent. Its rules keep each
instruction true for a class of situations and give it the condition under which it does not apply. Its main use is the
moment a skill is changed after a failed case or eval run: the skill has the agent name the class of the failure and fix
the rule that already governs it, keep the case's names out of the text, check the change on an input from another
domain and on one where it must stay quiet, and have a reviewer who has not seen the case name the class each new
sentence addresses. The rules hold in any harness (Claude Code, Codex, Cursor, Copilot), with or without APM.

Package layout, frontmatter, and installation are [`apm-authoring`](../apm-authoring/); wording is the developer-style
skill of the language the text is written in.

## Contents

- `.apm/instructions/agent-instruction-authoring.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/agent-instruction-authoring/SKILL.md`: the eight rules, each with its reason and its boundary.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/agent-instruction-authoring
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/agent-instruction-authoring#<ref>
```

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md`.
