---
name: apm-authoring
description: How to author APM packages — skills, instructions and prompts — for the Qubership platform. Use when creating a new agent-package, editing an existing `SKILL.md` or `*.instructions.md`, or reviewing changes under `agent-packages/` or `.apm/`.
---

# Authoring APM packages for Qubership

APM (https://github.com/microsoft/apm) is a package manager for AI-agent
primitives: **instructions** (auto-applied rules), **skills** (how-to guides
the agent invokes on demand), and **prompts** (slash-commands). The Qubership
platform ships its conventions as APM packages so service developers receive
them as `apm dependencies` and agents like Claude Code, Copilot and Cursor
pick them up natively.

This skill is the contract between platform-library authors and the agents
that read their packages. Apply it whenever you touch `apm.yml`, a
`SKILL.md`, an `*.instructions.md`, or set up a new `agent-packages/<name>/`.

## Package layout

A library repo can host one or more APM packages. Each one lives under
`agent-packages/<package-name>/` so the path itself is the disambiguator:

```
agent-packages/
└── <package-name>/                  # = `name:` in apm.yml; matches the skill
    ├── apm.yml
    └── .apm/
        ├── instructions/
        │   └── <package-name>.instructions.md
        ├── skills/
        │   └── <package-name>/
        │       └── SKILL.md
        └── prompts/                 # optional
            └── <name>.prompt.md
```

Rules:

- `<package-name>` is descriptive and unique (`context-propagation-go-usage`,
  `qubership-dockerfile-usage`), **not** a generic placeholder like
  `user-guide`. Multiple packages can sit side-by-side in one repo, so the
  directory name has to identify the package on its own.
- A package holds a **coherent set** of skills, instructions and prompts
  that share an audience and a trigger surface (e.g. `<lib>-usage` for
  day-to-day code; a separate `<lib>-troubleshooting` if the failure-mode
  catalogue is large enough to deserve its own activation). Bundle by
  topic, not by file count — a one-skill package and a five-skill package
  are both fine if each set is internally coherent.
- Every skill needs a paired instructions file that triggers it.
  Without the trigger merged into `AGENTS.md` / `CLAUDE.md` the agent
  has no signal to pull the skill in. Keep names aligned so the link
  is obvious from the tree. The reverse is **not** required: a small
  always-true rule may ship as a standalone instruction with no skill
  behind it (see next section).

The host repo itself is also an APM project: its own AGENTS.md / CLAUDE.md
must be **rendered by `apm compile`** from a local `.apm/` package plus
declared dependencies. Do not hand-author AGENTS.md / CLAUDE.md — `apm
compile` overwrites it.

## Choosing between an instruction and a skill

Everything an APM package ships lands in one of two contexts:

- **Persistent.** Instructions are merged into the agent's root file
  (`AGENTS.md` / `CLAUDE.md`) by `apm compile` and live in session
  context on every turn. Cost: tokens × every consumer × every turn.
- **On-demand.** `SKILL.md` is loaded only after the agent decides
  the skill is relevant. Cost is paid only when the skill activates.

When you author a new package, decide for each piece of guidance
which side it belongs on:

- **Persistent (instruction)** — rules the agent should follow on
  **every turn regardless of which files are open**, plus the
  trigger phrase that names a skill. The best instructions are
  *nudges*: cases where the LLM already knows how to do the task
  but defaults to a sub-optimal flavour of it.
    - "Pass `--batch --quiet` when invoking Maven" — saves tokens
      by suppressing chatty output. The LLM already knows Maven; the
      instruction only steers the flag.
    - "Place new ADRs under `docs/adr/<NNNN>-<slug>.md`" — repo-wide
      directory convention the LLM cannot guess.
    - "Use the `gh` CLI for all GitHub operations" — picks the right
      tool regardless of what file the agent is touching.
- **On-demand (`SKILL.md`)** — anything tied to a specific file
  type, library, or task: setup checklists, multi-step how-tos,
  code templates, library-specific call patterns, failure-mode
  catalogues. The paired instruction-trigger fires only when the
  agent reaches a relevant file, so the body never pollutes
  unrelated turns (codebase exploration, bug triage, CI debugging
  on another stack). Counter-examples — these look like instruction
  material but belong in a skill:
    - "Use `logger.InfoC(ctx, …)` in `*.go` handlers" → ships in a
      `go-authoring` (or logging-specific) skill, triggered on
      `**/*.go`. Loading it on every turn would pay tokens for it
      while reading SQL, editing YAML, or reviewing CI logs.
    - "Dockerfiles use `USER 10001:10001` and `--chown=10001:0`"
      → ships in `qubership-dockerfile-usage`, triggered on
      `**/{Dockerfile,Dockerfile.*,*.Dockerfile}`.

Heuristic: an instruction earns its place only if the agent
benefits from it on **every** turn, not just when working on a
specific stack. "Always true, short, *and* cross-cutting" is an
instruction; "true when working on X" is a skill triggered by X.
If an instructions file grows past a paragraph, or starts referring
to a specific language or file type, the overflow probably wants
to move into a `SKILL.md` and be replaced by a one-line trigger.

## What an instructions file is for

Two things only: a narrow `applyTo:` and a short trigger body. Both
land in the merged `AGENTS.md` / `CLAUDE.md`, so every byte costs
tokens on every turn for every consumer.

`applyTo:` is a *placement heuristic*, not a runtime gate. `apm
compile` uses it to decide which subdirectory's root file the
instruction lands in (e.g. `applyTo: "frontend/**/*.tsx"` may land
in `frontend/CLAUDE.md` instead of the repo root). Placement is
best-effort; behaviour is steered by the trigger phrase, not by
`applyTo`. So state the file scope in the trigger sentence as well —
"When editing `*.go` …" — so the agent picks up the rule wherever
the merged file ended up.

Rules for the file:

- Use a narrow `applyTo:` mask (`**/*.go`,
  `**/{Dockerfile,Dockerfile.*,*.Dockerfile}`, `**/pom.xml`) so APM can
  place the instruction near the code it governs. `**/*` is fine only
  for umbrella packages where the rule really is universal.
- The body says **what the user is doing** when the skill should
  activate — a verb phrase, ideally with the file mask — not "when the
  user works with library X". The library name is bookkeeping; the
  verb is the trigger.

```markdown
---
description: Go coding standards for Qubership context propagation.
applyTo: "**/*.go"
---

## Skill trigger: `context-propagation-go-usage`

When editing `*.go` and propagating request context (X-Request-Id,
X-Version, headers, etc.) between Qubership microservices, apply the
`context-propagation-go-usage` skill.
```

Avoid in the trigger:

- `When the user works with github.com/.../<long-import-path> library — registering providers, initializing context, propagating headers, writing custom providers, working with snapshots …`
  This is the skill body, not a trigger. Pick the user-facing verb.
- Negative scope (`Do NOT use for the X operator`). If a different repo
  must not pick up your skill, that repo's own scope handles it. Don't
  fight other packages from yours.
- Padding the trigger with "or reviewing code that does …". The verb
  phrase already covers both creation and review; adding the second
  half just inflates the persistent-context cost.

## What a SKILL.md is for

The skill is what the agent reads **after** it decides to engage. Its job
is to teach the agent things it cannot infer from imports, types, or
generic documentation. Three rules:

### 1. Encode platform-specific knowledge, nothing else

Include only what the agent cannot reasonably know:

- **Required ordering** of init steps (`configloader.Init` before
  `logging.GetLogger`; `serviceloader.Register` before
  `fiberserver.Process`).
- **Side-channel contracts** (env vars, `application.yaml` files that
  must exist, k8s projected volumes that must be mounted).
- **Failure modes that look fine in code** (`Process()` panics if the
  security middleware was not registered; `AllowedHeader` silently
  no-ops without `HEADERS_ALLOWED`).
- **Helpers that replace ad-hoc work** (`ctxhelper.AddSerializableContextData`
  instead of manual header copying).
- **Conventions a reviewer would otherwise have to memorize**
  (`USER 10001:10001`, `--chown=10001:0`, `appuser`).

Leave out everything else. In particular, don't include:

- Generic ecosystem knowledge — `go get`, adding to `pom.xml`, Dockerfile
  multi-stage basics, how `CGO_ENABLED=0` produces a static binary. The
  agent already knows. Stating it dilutes the signal of what is
  Qubership-specific.
- Material that belongs in the library's own API docs. Languages publish
  generated docs (godoc → pkg.go.dev, javadoc, rustdoc, pydoc) and the
  agent can fetch them when needed. Repeating method signatures and
  parameter prose in the skill creates a second source of truth that
  drifts.
- Implementation-detail asides ("returns an interface with level-based
  methods", "does not override GOMEMLIMIT if already set"). If the
  developer doesn't act on it, the skill doesn't need it.

### 2. One canonical example per concern

State the rule, then show one concrete example. Do not show two examples
that vary in trivial ways — a reviewer rightly asks "is this any
different from the previous example?". If a real variant exists (Quarkus
fast-jar vs Spring Boot uber-jar; net/http vs Fiber middleware), show it
once and label what makes it different.

When listing pitfalls, prefer **rule + brief reason** over a wall of
`// WRONG: …` snippets. Negative examples without the matching positive
flow leave the reader guessing what was supposed to happen. A
"Common pitfalls" section is fine — keep each entry to a one-line cause
and one-line fix.

### 3. Don't separate "create" and "review"

The skill should make the same recommendation whether the agent is
writing new code or reviewing existing code. Avoid a dedicated
"Reviewing an existing X" section that restates the same rules in
checklist form — that's two sources to keep in sync. Express the rules
once, in active voice, and let them apply to both directions.

## Frontmatter and formatting

- YAML frontmatter starts at column 0. Do not indent its keys or content
  body. (Indented frontmatter renders as a blockquote inside `<pre>` and
  may not be parsed as frontmatter at all.)
- Use plain Markdown source for tables, lists and code fences. Do not
  paste rendered ASCII boxes (`┌──┬──┐`) — they are unreadable in the
  source view, agents process them poorly, and they don't survive edits.
- Code blocks specify the language (` ```go `, ` ```dockerfile `,
  ` ```yaml `).
- Skill `description:` is the field the agent uses to decide whether
  the skill is relevant. Make it a verb-led sentence describing the
  user task, not a feature list of the library.

## Versions

Do not hard-code library or image versions in skills.

- The repository's own `go.mod`, `pom.xml`, existing Dockerfile, etc. is
  the source of truth for the version a service uses. The skill should
  point the agent at that, not at a number that will be stale next
  quarter.
- Where the skill must mention a version (e.g., a base-image migration
  story), make it clear that the value is illustrative and direct the
  agent to the upstream release page.
- Distribution names should be precise or omitted. Don't write
  "OpenJDK" when you mean "Eclipse Temurin" or just "Java 21" — be
  specific or generic, never sloppy.

The skill itself is versioned in `apm.yml`. Bump that when the contract
changes (new required step, breaking rename), not on every prose edit.

## apm.yml

Minimal valid manifest for a leaf package:

```yaml
name: <package-name>           # matches agent-packages/<package-name>/
version: 1.0.0
description: One-sentence purpose.
author: Qubership
```

Umbrella / aggregator packages declare dependencies and nothing else
substantive — the umbrella's instructions file should be a one-line
"all platform rules apply" pointer, like
[go-microservice-dev-kit.instructions.md](agent-packages/go-microservice-dev-kit/.apm/instructions/go-microservice-dev-kit.instructions.md).

```yaml
name: go-microservice-dev-kit
version: 1.0.0
description: Umbrella package for Qubership Go microservices.
author: Qubership
dependencies:
  apm:
    - Netcracker/<repo>/<path>/agent-packages/<package>#<ref>
```

Conventions for the dependency list:

- Pin to a tag (`@v1.2.0`) for stable consumers; pin to a branch
  (`#feat/agent-packages`) only while a feature is still in review.
- Each dependency line resolves to one `agent-packages/<name>/` folder,
  so the suffix in the URL must end in the package directory — never
  the repo root.

## Reference: the umbrella pattern

A platform with several libraries should expose **one umbrella** package
for service developers to depend on, plus one leaf package per library
hosted alongside that library's source. The umbrella's only job is the
dependency list and a near-empty instructions file. Don't duplicate
library content in the umbrella; transitive resolution is what makes the
model work.

## Common authoring pitfalls

- **Trigger sentence is a feature list.** Replace with a one-verb
  description of the user task.
- **Skill restates language docs.** Drop the prose that simply mirrors
  godoc; link or trust the agent to fetch.
- **Multiple near-identical examples.** Collapse to one and explain the
  axis of variation if a second is genuinely different.
- **Tables drawn with box-drawing characters.** Convert to Markdown
  table syntax or to a bullet list.
- **Hard-coded versions in the skill body.** Defer to the consumer's
  manifest or to the upstream release page.
- **Generic wisdom mixed with platform rules.** If a paragraph could
  appear unchanged in any tutorial on the topic, it doesn't belong here.
- **Negative-only checklists.** Pair each `WRONG` with the positive
  flow, or replace with a one-line rule plus reason.
- **`agent-packages/user-guide/` as a directory name.** Use the
  package's actual name; multiple packages collide otherwise.
- **Hand-edited AGENTS.md / CLAUDE.md in a repo that already uses
  APM.** Edit the local `.apm/` package and re-run `apm compile`.
