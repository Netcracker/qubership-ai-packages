# agents-md-authoring

A user-invoked skill for creating or improving repository-root `AGENTS.md` and `CLAUDE.md` files from verified checkout
evidence.

The skill makes `AGENTS.md` the canonical shared instruction file. `CLAUDE.md` imports it and may keep a small block of
genuinely Claude-specific guidance. Shared content is moved into `AGENTS.md` without keeping duplicate copies. It
supports two strategies:

- Greenfield creates a new structure when instruction files are absent or contain too little useful information.
- Preserve edits an existing useful structure in place, but applies the same selection test to old and new content.

The generated instructions prioritize non-obvious repository constraints whose absence could cause a wrong file,
command, validation choice, or change boundary. They omit information that an agent can recover quickly from nearby
authoritative sources, along with generic advice, copied documentation, task notes, unsupported rules, secrets, and
mechanically enforced style guidance. The skill uses no line target; every retained instruction must justify its place.

Before drafting, the skill searches repository-scoped session transcripts, agent memory, and pull-request reviews or
discussions for recurring mistakes and maintainer corrections. When read-only subagents are available, one researcher
handles each channel in parallel. The primary agent treats every result as a candidate, revalidates it against the
current checkout, and applies the same usefulness filter used for all other content.

After editing, a fresh-context reviewer evaluates the complete instruction diff against the bundled positive and
negative research. The author applies actionable findings and may run one final review, with a hard limit of two
cycles. After the second cycle, the author applies its findings, reports residual risk, and continues without a third
review. The skill then reports the selected strategy, created files, additions, rewrites, removals, preserved content,
concise historical findings, omitted facts, source mappings, and validation performed.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/agents-md-authoring
```

Or add the package to `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/agents-md-authoring
```

Then run `apm install` and `apm compile`. Ask the agent to create, audit, refresh, or update the repository's root
`AGENTS.md` and `CLAUDE.md`.
