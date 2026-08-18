# Main takeaway

Keep `CLAUDE.md` and `AGENTS.md` as a **small, version-controlled, always-loaded layer of stable, non-obvious rules**
rather than a "README for a neural network," complete repository documentation, or a megaprompt. This layer should
contain rules that:

* apply to a significant share of tasks;
* cannot be reliably inferred from the code;
* prevent errors that have already occurred;
* are specific and verifiable;
* point to sources of more focused information.

Both Anthropic and OpenAI now explicitly recommend short, practical files refined through real work. OpenAI also
describes the failure of the "one large `AGENTS.md`" approach: the file displaced useful context, quickly became
outdated, and turned into an encyclopedia that was hard to verify. ([Claude Platform Docs][1])

Apply the checks below to existing and new content. Code discoverability, model inferability, duplication, and generic
structure are valid removal signals when the text adds no non-obvious operational constraint. Before removing ambiguous
content, check whether it protects data, compatibility, security, generated ownership, or an approval boundary.

---

## Differences between `CLAUDE.md` and `AGENTS.md`

### Claude Code

* Claude Code reads `CLAUDE.md` natively, but not `AGENTS.md`.
* All discovered parent `CLAUDE.md` files are **combined**; they do not have strict override semantics. A closer file
  appears later in the context, but Claude can still choose either rule arbitrarily when they conflict.
* Nested `CLAUDE.md` files load when Claude starts working with the corresponding subtree.
* `@docs/file.md` is **not a lazy reference**: the imported file is expanded and loaded into the context at startup.
* Use no line target. Keep each `CLAUDE.md` limited to instructions that pass the usefulness test.

### Codex

* Codex assembles a chain of `AGENTS.md` files from the root to the current directory.
* Closer instructions are considered more specific and take precedence.
* By default, the total size of project instructions is limited to 32 KiB through `project_doc_max_bytes`. This is a
  technical ceiling, not a recommended size.
* OpenAI recommends putting local rules in files closer to the code and moving long planning, review, or architecture
  instructions to separate documents. ([OpenAI Developers][2])

For compatibility, Anthropic's official recommendation is to make `AGENTS.md` the canonical shared file, import it
into `CLAUDE.md`, and add a small Claude-specific block if needed:

```md
@AGENTS.md

## Claude Code–specific

- Use plan mode before changing the billing protocol.
```

Another option is a symlink when tool-specific differences are unnecessary. ([Claude Platform Docs][1])

---

## Main anti-patterns

### 1. `Context Bloat`: turning the file into an encyclopedia

This anti-pattern puts the product overview, architecture, complete module list, every command, API documentation,
release runbook, PR process, style guide, and troubleshooting guidance into one file that is always loaded.

Why this is harmful:

* the content competes for context with the current task and code;
* the more rules declared important, the less clear the actual priorities become;
* a long document accumulates contradictions and outdated information faster;
* procedures needed for 2% of tasks consume tokens in 100% of sessions.

A study of popular open-source repositories found `Context Bloat` in many files. The largest `CLAUDE.md` reviewed was
very large and included product capabilities, an architecture overview, and API usage. The authors considered much of
this content ordinary documentation without enough value to justify permanent context.
([arXiv][3])

**Bad:**

```md
# Product overview
[All product capabilities]

# Complete architecture
[Description of every service and class]

# API reference
[All endpoints]

# Development workflows
[Release, deploy, migrations, incident response, review...]

# Style guide
[80 rules]
```

**Better:**

```md
## Build and verify

- Fast tests: `pnpm test --filter billing`
- Full check: `pnpm verify`
- Local API: `pnpm dev:api`

## Non-obvious invariants

- `packages/domain` must not import anything from `apps/`.
- Billing events are backward-compatible for two released versions.

## Routing

- For database migrations, read `docs/database-migrations.md`.
- For releases, invoke the `release` skill.
```

Do not copy another repository's file size or section structure. Select each instruction by utility in the target
repository.

---

### 2. Copying information that the agent can easily discover

Typical examples:

* the complete directory tree;
* a list of all dependencies;
* a summary of `package.json`;
* a description of every component;
* "the project is written in TypeScript" when an obvious `tsconfig.json` exists;
* "tests are in `tests/`";
* a file-by-file architecture map.

Architecture information can still be useful, but keep it to a **short map of non-obvious boundaries and reasons**
rather than a file inventory.

One 2026 study found that popular repository overviews did not help agents solve tasks on average, even though the
agents followed the instructions they contained and spent more time exploring the repository. OpenAI expresses the
same principle as "give the map, not a thousand-page manual." ([arXiv][4])

**Bad:**

```md
- `src/` contains source code.
- `tests/` contains tests.
- React components are in `src/components/`.
- The project uses PostgreSQL, Redis, React and TypeScript.
```

**Better:**

```md
- Domain logic belongs in `packages/domain`, not in route handlers:
  the same code is reused by the HTTP API and background workers.

- `legacy-auth/` is read-only compatibility code. New authentication
  behavior must be implemented in `identity/`.
```

A good official example is the concise `CLAUDE.md` in the `anthropics/claude-code-action` repository. It contains exact
commands, a concise execution flow, and genuinely non-obvious pitfalls such as the token lifecycle and integration
testing details. ([GitHub][5])

---

### 3. `Skill Leakage`: narrow multistep procedures in an always-on file

Releases, deployments, database migrations, adding a new adapter, incident investigations, creating a new package, or
a complete code review workflow are rarely needed in every session. Putting them in the root file turns a conditional
procedure into a permanent instruction.

The configuration smells study found 35 potential cases of `Skill Leakage`, 29 of which were confirmed manually. One
real example is a five-step procedure for adding a new operating system to `quickemu`: most tasks do not need it, so
the authors recommend a separate skill or document. Testing workflows, PR and review procedures, scaffolding, and
infrastructure instructions were the most common leaks. ([arXiv][3])

**Bad:**

```md
## Releasing

1. Update all package versions.
2. Regenerate the changelog.
3. Build every image.
4. Push the release branch.
5. Create tags.
6. Publish packages.
7. Update documentation.
8. Notify downstream teams.
```

**Better:**

```md
- For a release, invoke `/release`.
- Release workflow source: `.claude/skills/release/SKILL.md`.
```

In Anthropic and OpenAI terminology:

* `CLAUDE.md` / `AGENTS.md`: conventions that always apply;
* `SKILL.md`: a conditionally loaded procedure or specialized knowledge;
* workflow/script: a deterministic sequence of actions. ([Claude][6])

---

### 4. `Lint Leakage`: rewriting linter configuration in natural language

Typical lines:

```md
- Use two spaces.
- Sort imports.
- Maximum line length is 80.
- Use snake_case for functions.
- All files must end with a newline.
```

If these requirements are already expressed through ESLint, Ruff, Prettier, Biome, Clippy, formatter configuration,
or pre-commit, duplicating them creates two problems:

1. it consumes permanent context;
2. over time, it diverges from the machine-readable source of truth.

`Lint Leakage` was the most common smell in the June 2026 study: 62 cases were detected, and 58 were confirmed
manually. The authors cite the long Python style guide in `google/adk-python` as an example; maintainers later moved
that section from `AGENTS.md` to a separate skill. ([arXiv][3])

**Bad:**

```md
- Use 88-character lines.
- Sort imports alphabetically.
- Use double quotes.
- Do not leave trailing whitespace.
```

**Better:**

```md
- Run `ruff check --fix && ruff format` for changed Python files.
- Do not hand-format files under `generated/`.
- The formatter configuration is the source of truth.
```

HumanLayer states this especially directly: Claude is not a linter; formatting and mechanical rules belong in
formatters, linters, and hooks. ([HumanLayer][7])

However, an **unusual architectural convention** that a linter cannot express deserves a place in the file:

```md
- Public API DTOs must not expose database model types.
```

---

### 5. Using Markdown instructions as an enforcement mechanism

`CLAUDE.md` and `AGENTS.md` influence model behavior but provide no guarantees. Constructs like these are especially
dangerous:

```md
- NEVER read `.env`.
- NEVER write to `migrations/`.
- NEVER push to `main`.
- ALWAYS run the security scanner.
```

Claude can forget an instruction, misjudge when it applies, or violate it during a long session. Anthropic officially
describes `CLAUDE.md` as context, not enforced configuration. For actual boundaries, it recommends permissions, a
sandbox, `PreToolUse` hooks, and CI. ([Claude][8])

**A better allocation of responsibility:**

```text
Do not read .env             -> permission deny rule
Do not modify migrations/    -> PreToolUse hook / filesystem permission
Do not push main             -> branch protection / hook
Always run the formatter     -> PostToolUse hook / pre-commit
Do not merge when CI fails   -> required GitHub check
```

A short explanation in `CLAUDE.md` can still help the model choose the correct path, but it should supplement the
enforcement mechanism:

```md
- Migration files are generated and must not be edited manually.
  Use `pnpm db:migration:create <name>`.
```

---

### 6. Unverifiable slogans instead of operational instructions

Almost useless wording:

```md
- Act as a senior engineer.
- Write clean and maintainable code.
- Follow best practices.
- Be careful about security.
- Test thoroughly.
- Keep files organized.
```

They have no observable completion criterion. The model does not know exactly what counts as "clean," "thorough," or
"organized."

Anthropic recommends verifiable instructions: an exact command instead of "test it," and a specific directory instead
of "keep things organized." OpenAI likewise recommends stating the goal, constraints, and `done when` criteria
explicitly. ([Claude Platform Docs][1])

**Bad:**

```md
- Test your changes thoroughly.
```

**Better:**

```md
- For a bug fix, add a regression test that fails before the fix.
- Run the smallest affected test suite, then `pnpm typecheck`.
- If a required check cannot run, report the command and reason.
```

---

### 7. Step-by-step micromanagement when a goal and boundaries are enough

Another extreme is dictating every research and implementation step to the agent:

```md
1. Open `src/index.ts`.
2. Search for `createClient`.
3. Open `config.ts`.
4. Copy the existing implementation.
5. Edit the third argument.
6. Run command X.
7. Open log Y.
```

Such an instruction:

* quickly becomes outdated after refactoring;
* blocks better solution paths;
* forces the agent to perform steps that may not apply to the current task;
* mixes an invariant with an implementation recipe.

In a recent talk, Claude Code creator Boris Cherny advised against micromanaging modern models with step-by-step
directions and recommended specifying the expected outcome and boundaries instead. OpenAI recommends the same
structure: the goal, relevant context, constraints, and completion criteria. ([Business Insider][9])

**Bad:**

```md
- When fixing authentication, first open A, then copy B,
  edit C, and finally execute D.
```

**Better:**

```md
- Preserve compatibility with tokens issued by the previous two releases.
- Do not change the public `Session` schema.
- Done when old-token and new-token integration tests pass.
```

When the sequence is truly mandatory, for example, for a release or data migration, that usually argues for a skill,
script, or executable workflow rather than a large root file.

---

### 8. A prohibition without a safe alternative

Shrivu Shankar identifies this practical anti-pattern separately: a `Never X` rule can leave the agent stuck when it
does not know the permitted path. The agent then either violates the prohibition or stops even though the task is
solvable. ([Shrivu's Substack][10])

**Bad:**

```md
- Never add dependencies.
```

**Better:**

```md
- Prefer existing dependencies and standard-library functionality.
- If a new production dependency is necessary, stop before editing
  the lockfile and explain:
  1. why existing options are insufficient;
  2. proposed package and license;
  3. runtime or bundle-size impact.
```

Other examples:

```md
# Bad
- Never edit generated files.

# Better
- Do not edit generated files directly.
  Change `schemas/*.json` and run `pnpm generate`.
```

```md
# Bad
- Never catch exceptions here.

# Better
- Let domain errors propagate to `requestBoundary()`,
  which maps them to the public error response.
```

---

### 9. Conflicting instructions

A conflict can occur:

* within a single file;
* between root and nested files;
* among `CLAUDE.md`, `.claude/rules/`, and the user's `~/.claude/CLAUDE.md`;
* between `AGENTS.md` and its copy for another tool;
* between Markdown and the actual formatter or CI configuration.

The official Claude documentation warns that Claude may choose either instruction arbitrarily when they conflict. In
the smells study, one real file simultaneously required creating components in `packages/ui/components` and
`packages/components`. Of 28 automatically detected conflicts, 16 were confirmed manually. The problem is real,
although it remains difficult to detect automatically. ([Claude Platform Docs][1])

**Bad:**

```md
- New components belong in `packages/ui/components`.

...

- Create every component under `packages/components`.
```

**Better:**

```md
# Root AGENTS.md
- Shared UI rules are defined by `packages/ui/AGENTS.md`.

# packages/ui/AGENTS.md
- New reusable UI components belong in `src/components/`.
```

A useful maintenance check:

```text
For every MUST/NEVER/path/command:
1. Find every other mention of the same entity.
2. Compare it with the actual configuration and filesystem.
3. Keep one source of truth.
```

---

### 10. A rule is in the wrong scope

A service-specific instruction at the root applies to unrelated tasks. A personal habit in a repository file is
imposed on the entire team. A global instruction can conflict with the local architecture.

**Bad at the monorepo root:**

```md
- Run the full payments end-to-end suite after every change.
- All entities must use `PaymentId`.
```

This is unnecessary when changing documentation, the frontend, or an unrelated service.

**Better:**

```text
services/payments/AGENTS.md
.claude/rules/payments.md
```

```md
- Applies only to `services/payments/**`.
- Run `pnpm test:e2e:payments` when payment behavior changes.
- Public payment identifiers use the `PaymentId` branded type.
```

Anthropic provides nested `CLAUDE.md` files and path-scoped rules; Codex provides nested `AGENTS.md` files where the
closer instruction takes precedence. Personal settings belong in user-level or local files, not in the shared
repository. ([Claude Platform Docs][1])

---

### 11. `Blind Reference`: a link without explaining when or why to read it

It is not enough to write:

```md
- See `docs/plugin-reorg.md`.
- Architecture is described in `docs/architecture.md`.
```

The agent does not know:

* whether the document applies to the current task;
* which part of the document to look for;
* whether it is the current source of truth;
* whether it must be read before changing the code.

The smells study found 16 blind references, 14 of which were confirmed manually. One real example simply directed the
agent to `docs/plugin-reorg.md` "for details" without explaining the document's purpose. ([arXiv][3])

**Better:**

```md
- Before changing plugin discovery or marketplace metadata,
  read `docs/plugin-reorg.md`: it defines the target v5 layout
  and compatibility guarantees that are not yet visible in code.
```

Shrivu Shankar recommends this exact kind of conditional routing: provide not only a path, but also the reason and the
trigger that makes the document relevant. ([Shrivu's Substack][10])

---

### 12. Using `@imports` as false progressive disclosure

This mistake is especially common in Claude Code:

```md
@README.md
@docs/architecture.md
@docs/api.md
@docs/release-runbook.md
@docs/troubleshooting.md
```

The main file looks small, but Claude expands all these imports at startup. The context cost is almost the same as if
the content had been copied into `CLAUDE.md`. Imports help organize content but do not provide lazy loading.
([Claude Platform Docs][1])

**Bad:**

```md
# More context
@docs/everything.md
```

**Better:**

```md
- For public API compatibility changes, read
  `docs/public-api-contract.md` before implementation.

- For production incident investigation, invoke
  the `troubleshoot-production` skill.
```

For true progressive disclosure in Claude, use:

* path-scoped `.claude/rules/`;
* skills whose full contents load when they are applied;
* nested files;
* subagents for extensive research.

---

### 13. Independent copies of `CLAUDE.md` and `AGENTS.md`

This approach almost inevitably causes drift:

```text
CLAUDE.md - updated test command
AGENTS.md - old test command

CLAUDE.md - new component path
AGENTS.md - path from before the refactoring
```

Anthropic's official pattern is to import `AGENTS.md` from `CLAUDE.md` or use a symlink. Peter Steinberger also uses a
symlink but specifically warns that different models can respond differently to the same wording.
([Claude Platform Docs][1])

The most sustainable option is therefore:

```md
# AGENTS.md
[Shared, neutrally worded repository contract]
```

```md
# CLAUDE.md
@AGENTS.md

## Claude Code–specific

- For multi-service changes, enter plan mode before editing.
```

In other words, use **one shared canonical core plus a small tool-specific delta**, not two complete copies.

---

### 14. Blind `/init`: generate, commit, and forget

Distinguish between two actions:

* using `/init` to obtain a draft;
* treating the output of `/init` as a finished contract.

Anthropic and OpenAI call `/init` a starting point and explicitly advise editing its output to reflect the team's
actual commands and practices. HumanLayer takes a stricter position and advises against automatically generating such
a high-impact file at all without careful line-by-line work. ([Claude Platform Docs][1])

Research confirms the risk:

* in one experiment, LLM-generated context files did not improve the success rate on average and increased inference
  cost by more than 20%;
* in the smells study, 24 of 100 files had only one commit despite continued active development of the corresponding
  repositories; this smell was named `Init Fossilization`. ([SRI Lab][11])

**Bad process:**

```text
/init
git add CLAUDE.md
git commit
[the file is never changed again]
```

**Better process:**

```text
1. Use /init as a discovery draft.
2. Remove the obvious directory tree and summaries of configuration files.
3. Verify every command locally.
4. Keep only non-obvious invariants, gotchas, and verification guidance.
5. Run several typical tasks.
6. Add rules after recurring mistakes.
7. Remove rules that no longer prevent a mistake.
```

---

### 15. Frequently changing and local information in a shared file

Poor candidates for shared repository instructions:

```md
- Current release branch is `release/4.8`.
- Production incident INC-1842 is still active.
- Use database at `10.0.4.17`.
- My repositories are under `/Users/alice/work/`.
- The current on-call engineer is Bob.
```

They quickly become outdated, do not apply to every developer, or should be read from the actual system.

**Where to move them:**

* personal paths and preferences -> `CLAUDE.local.md`, `~/.claude/CLAUDE.md`, or `~/.codex/AGENTS.md`;
* current incident or release status -> issue tracker, monitoring tool, or MCP;
* runtime configuration -> configuration or environment tooling;
* generated schema or status -> an automatically updated document;
* one-time constraint -> the current task prompt.

Anthropic specifically provides `CLAUDE.local.md` for uncommitted project preferences. OpenAI recommends MCP when
data lives outside the repository or changes frequently. ([Claude Platform Docs][1])

---

### 16. Missing a non-obvious feedback gate

A repository-specific gate can be worth permanent context when the obvious test target does not run it. Do not turn
this into a generic Definition of Done that repeats ordinary engineering expectations.

Simon Willison emphasizes not the volume of instructions but the tests, development server, CLI, and interactive
verification available to the agent. Anthropic calls executable verification one of the most important ways to close
the loop: without verification, the agent stops when the work merely "looks done." ([Simon Willison's Weblog][12])

**Bad:**

```md
- Implement features correctly.
```

**Better:**

```md
- API schema changes require `pnpm test:contract`; the ordinary test target
  does not run contract tests.
```

---

## What the research actually shows

To date, the data **supports neither the claim that "`AGENTS.md` always helps" nor the claim that "such files are
always harmful."**

### ETH Zürich / MemAgents study

In the revised June 2026 version, repository context files generally did not improve task success and increased
inference cost by more than 20%. The instructions were followed; the problem was that additional requirements often
made the agent do unnecessary work. Repository overviews also showed no benefit. ([arXiv][4])

### Efficiency study across 10 repositories and 124 PRs

Another study found the opposite effect on operational efficiency: the presence of `AGENTS.md` was associated with a
28.64% reduction in median runtime and a 16.58% reduction in output tokens, with comparable task completion behavior.
([arXiv][13])

### Probe-and-Refine

Guidance iteratively tuned against real failure modes achieved a 33.0% resolve rate, compared with 28.3% for the
original static knowledge base and 25.5% without guidance in a specific SWE-bench/Qwen configuration. The improvement
came mainly from the agent finding the correct files more often, not from producing better patches after finding them.
([arXiv][14])

### Factorial study of file structure

Across 1,650 Claude Code sessions, the researcher found no statistically distinguishable effect from four isolated
factors: file size, instruction position, splitting content across files, and an adjacent conflict. However, the study
tested a trivial annotation instruction on two TypeScript codebases, so it does not prove that structure never matters.
It does show the danger of cargo-cult optimizations such as "move the rule into the first ten lines, and compliance
will increase." ([arXiv][15])

### Analysis of 15,549 agent-generated PRs

Before and after instruction files appeared, results were mixed: the merge rate increased by at least 20% for 27.7%
of projects and decreased by at least that much for 26.35%. The mere presence of a file therefore guarantees almost
nothing. ([arXiv][16])

**Practical conclusion from the research as a whole:**

> The benefit comes not from the mere presence of a Markdown file, but from a small set of relevant, stable,
> failure-informed instructions validated on typical tasks for a specific repository and agent harness.

---

## Where to put different types of information

### In `CLAUDE.md` / `AGENTS.md`

* exact, non-obvious commands;
* stable architectural invariants;
* repository-specific gotchas;
* a concise definition of done;
* conditional pointers;
* constraints the agent must consider when making decisions;
* rules that apply to most tasks in the given scope.

### In a nested file or path-scoped rule

* rules for a specific service, language, package, or directory subtree.

### In `SKILL.md`

* release;
* deployment;
* code review;
* migration;
* incident investigation;
* creating a new module;
* any repeatable but conditional multistep procedure.

### In a hook, permissions, or CI

* anything that must run without exception;
* security boundaries;
* restrictions on file access;
* a mandatory formatter;
* generated-file checks;
* restrictions on dangerous commands;
* required tests.

### In `docs/`, `PLANS.md`, or a design document

* detailed architecture;
* rationale and decision history;
* API reference;
* feature specification;
* implementation plan;
* long tutorial.

### In local or user-level instructions

* personal communication style;
* local paths;
* preferred package manager;
* a personal workflow that is not a team rule.

### In MCP or another tool

* tickets;
* the current on-call engineer;
* incident status;
* live metrics;
* deployment status;
* frequently changing external data.

This allocation matches the current separation of mechanisms in Claude Code and Codex: instructions are for stable
conventions, skills for conditional procedures, hooks and permissions for enforcement, and MCP for current external
context. ([Claude][17])

---

## Minimal practical example

This is a menu of qualifying instruction types, not a required structure. Omit every section whose content is obvious
from nearby sources.

```md
# Repository guidance

## Commands

- Run `pnpm verify` from `frontend/`; the root script skips browser tests.

## Non-obvious architecture

- Domain packages must not import from application packages.
- Public event schemas are backward-compatible for two released versions.
- Generated files under `src/generated/` must not be edited directly.

## Definition of done

- Schema changes require `pnpm test:contract` in addition to the ordinary test target.

## Routing

- Before changing database schemas, read `docs/database-migrations.md`;
  it defines the required expand/migrate/contract sequence.
- For releases, invoke the `release` skill because the required signing sequence is not documented elsewhere.

## Escalation

- Before adding a production dependency, changing a public API,
  or deleting stored data, explain the options and request approval.
```

---

## Line-by-line audit of an existing file

Use these questions as selection tests for existing and new content. A failed test justifies removal or routing when the
audit confirms that no non-obvious high-impact constraint would be lost.

1. **What recurring error does this line prevent?**
   If none is known, investigate its purpose before adding or changing it.

2. **Is it needed in most sessions within this scope?**
   If not, move it to a skill, nested rule, or separate document.

3. **Can the agent reliably learn this from the code or configuration?**
   If so, remove or route the copy unless it contains a non-obvious high-impact constraint.

4. **Is the information stable?**
   If it changes every week, use a dynamic source.

5. **Is the instruction specific and verifiable?**
   "Write high-quality code" is not. "Run `pnpm test:contract`" is.

6. **Does a linter, formatter, hook, or CI already enforce it?**
   If so, keep at most a short operational pointer.

7. **Is the scope correct?**
   A payments-only rule should not be at the monorepo root.

8. **Are there conflicting mentions in other instruction files?**

9. **Does a prohibition provide an acceptable alternative?**

10. **Does a link explain when and why to read the document?**

11. **Can the line's usefulness be tested on several real tasks?**

12. **Is this line an "organizational scar" whose cause no longer exists?**

---

## Sources worth starting with

* Official Claude Code documentation on loading, hierarchy, imports, size, and compatibility with `AGENTS.md`.
  ([Claude Platform Docs][1])
* Official Claude Code best practices for verification, hooks, and skills. ([Claude][6])
* Official Codex best practices: `AGENTS.md` content, nested scopes, repeated mistakes, and the definition of done.
  ([OpenAI Developers][18])
* OpenAI Harness Engineering, a practical analysis of the failure of a "large encyclopedic `AGENTS.md`." ([OpenAI][19])
* `Configuration Smells in AGENTS.md Files`, a catalog of six named smells with real examples. This is a recent
  preprint, and some detection heuristics have limited precision, so treat the figures as signals rather than absolute
  statistics. ([arXiv][3])
* ETH Zürich's `Evaluating AGENTS.md`, the most direct experiment on the benefits and costs of repository context
  files. ([arXiv][4])
* HumanLayer on "less is more," progressive disclosure, and criticism of automatic generation. ([HumanLayer][7])
* Shrivu Shankar on guardrails instead of a manual, conditional references, and prohibitions with alternatives.
  ([Shrivu's Substack][10])

[1]: https://docs.anthropic.com/en/docs/claude-code/memory
  "https://docs.anthropic.com/en/docs/claude-code/memory"
[2]: https://developers.openai.com/codex/agent-configuration/agents-md
  "https://developers.openai.com/codex/agent-configuration/agents-md"
[3]: https://arxiv.org/html/2606.15828v2
  "https://arxiv.org/html/2606.15828v2"
[4]: https://arxiv.org/abs/2602.11988
  "https://arxiv.org/abs/2602.11988"
[5]: https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md
  "https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md"
[6]: https://code.claude.com/docs/en/best-practices
  "https://code.claude.com/docs/en/best-practices"
[7]: https://www.humanlayer.dev/blog/writing-a-good-claude-md
  "https://www.humanlayer.dev/blog/writing-a-good-claude-md"
[8]: https://code.claude.com/docs/en/memory
  "https://code.claude.com/docs/en/memory"
[9]: https://www.businessinsider.com/anthropic-claude-code-prompting-tips-boris-cherny-micromanaging-ai-2026-7
  "https://www.businessinsider.com/anthropic-claude-code-prompting-tips-boris-cherny-micromanaging-ai-2026-7"
[10]: https://blog.sshh.io/p/how-i-use-every-claude-code-feature
  "https://blog.sshh.io/p/how-i-use-every-claude-code-feature"
[11]: https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd
  "https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd"
[12]: https://simonwillison.net/2025/Oct/25/coding-agent-tips/
  "https://simonwillison.net/2025/Oct/25/coding-agent-tips/"
[13]: https://arxiv.org/abs/2601.20404
  "https://arxiv.org/abs/2601.20404"
[14]: https://arxiv.org/abs/2606.20512
  "https://arxiv.org/abs/2606.20512"
[15]: https://arxiv.org/abs/2605.10039
  "https://arxiv.org/abs/2605.10039"
[16]: https://arxiv.org/html/2606.13449v1
  "https://arxiv.org/html/2606.13449v1"
[17]: https://code.claude.com/docs/en/agent-sdk/claude-code-features
  "https://code.claude.com/docs/en/agent-sdk/claude-code-features"
[18]: https://developers.openai.com/codex/learn/best-practices
  "https://developers.openai.com/codex/learn/best-practices"
[19]: https://openai.com/index/harness-engineering/
  "https://openai.com/index/harness-engineering/"
