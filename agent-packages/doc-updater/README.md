# doc-updater

Keep project documentation in sync with code changes. This skill analyzes staged git changes, determines which
documentation files need creating or updating, and applies the changes following established project conventions.

This skill is **user-invoked** — it runs only when you explicitly ask to update or sync documentation, mention that docs
are outdated, or use a command like `/doc-updater`. It does NOT run automatically before commits.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/doc-updater
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/doc-updater@v1.0.0
```

Then run `apm install` and `apm compile`.

## What you get

A skill that analyzes code changes and updates documentation accordingly. The skill follows these steps:

1. **Discover** the project's doc structure
2. **Analyze** the staged diff and classify documentation impact
3. **Plan and confirm** (for major changes) or auto-apply (for small updates)
4. **Write** the documentation following existing conventions
5. **Verify** the result

## Typical use

Ask your agent:

- "Update the documentation to reflect these changes"
- "The docs are outdated, sync them with the code"
- "Run /doc-updater"

The skill adapts to your project structure and creates a `docs/README.md` index on first run if one does not exist.

## Self-Adaptation

On first invocation, the skill detects your repository layout and creates a navigable `docs/README.md` index that maps
all documentation files. Subsequent runs use this index to understand your documentation structure.

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.
