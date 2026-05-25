# qubership-ai-packages

## APM Quick Start Guide

**Agent Package Manager (APM)** is a package manager for AI agents. It lets you install, create, and share
instructions, skills, prompts, and MCP servers for agents like GitHub Copilot, Claude Code, and Cursor.

**Why APM?** See the [package-manager evaluation](research/apm-research/) for the comparison against other
open-source skill / MCP / AGENTS.md managers.

---

## Installation

**macOS / Linux:**

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

**Windows (PowerShell):**

```powershell
irm https://aka.ms/apm-windows | iex
```

**Homebrew:**

```bash
brew install microsoft/apm/apm
```

**pip:**

```bash
pip install apm-cli
```

Verify installation:

```bash
apm --version
```

---

## Initialize a Project

```bash
apm init
```

Creates a minimal `apm.yml` in the current directory:

```yaml
name: my-project
version: 1.0.0
```

---

## Package Structure

```text
my-package/
├── apm.yml                          # Manifest (required)
└── .apm/
    ├── instructions/
    │   └── go.instructions.md       # Rules applied automatically by the agent
    ├── skills/
    │   └── my-skill/
    │       └── SKILL.md             # Skill / how-to guide for the agent
    └── prompts/
        └── my-prompt.prompt.md      # Slash command / prompt template
```

---

## Primitives

### Instructions (`.instructions.md`)

Rules the agent applies automatically to matching files via `applyTo` glob.

```markdown
---
description: Go coding standards
applyTo: "**/*.go"
---

Only use github.com/my-org/logger. Never use fmt.Println or log.
```

### Skills (`SKILL.md`)

A guide that tells the agent what a package does and how to use it.

```markdown
---
name: my-skill
description: When to invoke and what this skill does
---

## Steps
1. Do this first
2. Then do that
```

### Prompts (`.prompt.md`)

Slash commands available in the agent chat.

```markdown
---
name: review-pr
description: Review a pull request for style and correctness
---

Review the following code: $SELECTION
```

---

## Installing Packages

Install a package from GitHub:

```bash
apm install owner/repo
```

Install a specific version:

```bash
apm install owner/repo@v1.2.0
```

Install a skill from a monorepo subdirectory:

```bash
apm install owner/repo/path/to/skill
```

Install all dependencies declared in `apm.yml`:

```bash
apm install
```

---

## Managing Dependencies

Add a dependency to `apm.yml` manually:

```yaml
dependencies:
  apm:
    - owner/coding-standards@v1.0.0
    - owner/security-rules@v2.1.0
  mcp:
    - https://mcp.example.com/sse
```

Then run `apm install` to apply.

Show installed dependencies:

```bash
apm deps list
```

Show full dependency tree:

```bash
apm deps tree
```

Check for outdated dependencies:

```bash
apm outdated
```

Update dependencies:

```bash
apm deps update
```

Remove a package:

```bash
apm uninstall owner/repo
```

---

## Compilation

For agents that read a single root file (`AGENTS.md`, `CLAUDE.md`), compile all primitives into one file:

```bash
apm compile
```

Agents like GitHub Copilot, Claude Code, and Cursor read deployed files natively — no compilation needed for them.

---

## Creating and Publishing a Package

Pack your package into a portable bundle:

```bash
apm pack
```

Publish by pushing to a GitHub repository and tagging a version:

```bash
git tag v1.0.0
git push origin main --tags
```

Others can then install it with:

```bash
apm install your-org/your-package@v1.0.0
```

---

## Key CLI Commands

| Command | Description |
| --- | --- |
| `apm init` | Initialize a new APM project |
| `apm install` | Install all dependencies and deploy local content |
| `apm install owner/repo` | Install a specific package |
| `apm uninstall owner/repo` | Remove a package |
| `apm deps list` | List installed dependencies |
| `apm deps tree` | Show dependency tree |
| `apm outdated` | Check for available updates |
| `apm compile` | Compile all primitives into AGENTS.md / CLAUDE.md |
| `apm pack` | Bundle the package for distribution |
| `apm audit` | Scan for hidden or malicious Unicode characters |

---

## `apm.yml` Reference

```yaml
name: my-package          # Required — package identifier
version: 1.0.0            # Required — semver

description: ""           # Optional — short human-readable description
author: ""                # Optional — author or organization
license: MIT              # Optional — SPDX license identifier

dependencies:
  apm:                    # APM packages (instructions, skills, agents)
    - owner/repo@v1.0.0
  mcp:                    # MCP servers
    - https://mcp.example.com/sse

scripts:                  # Named shell commands, run via `apm run <name>`
  lint: "eslint ."
```
