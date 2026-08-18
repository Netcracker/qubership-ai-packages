# Best practices for `CLAUDE.md` and `AGENTS.md`

**Current as of July 30, 2026.** I compared the latest official guidance from Anthropic and OpenAI, real files from
Anthropic, OpenAI, and Ghostty repositories, recommendations from Mitchell Hashimoto, Martin Fowler/Birgitta Böckeler,
and Simon Willison, and research on the effectiveness of repository-level instruction files.

Apply the optimization guidance below to existing and new content. Keep an instruction only when it changes an agent's
decision and is not easy to recover from a nearby authoritative source. Authorship and uniqueness do not lower this bar.

## Main conclusion

Treat `CLAUDE.md` and `AGENTS.md` as a small set of non-obvious constraints. Add a command, route, scope note, or
completion gate only when it prevents a realistic repository-specific mistake. Do not duplicate the documentation.

On **July 24, 2026**, Anthropic reported removing more than 80% of the instructions from Claude Code's system prompt
with no measurable degradation in coding-evals.
According to its observations, accumulated instructions in the system prompt, `CLAUDE.md`, and Skills had begun to
overconstrain newer models and sometimes contradicted one another. Current guidance favors fewer rules, a minimal set
of important constraints, and progressive disclosure. ([Claude][1])

OpenAI gives similar guidance: **"give Codex a map, not a thousand pages of instructions."** A large `AGENTS.md`
quickly becomes outdated, consumes context, makes the truly important requirements hard to find, and becomes nearly
impossible to verify. ([OpenAI][2])

---

## Core best practices

### 1. Make the root file a map and contract, not an encyclopedia

The root `CLAUDE.md` or `AGENTS.md` should contain only information needed for **nearly every task** and not obvious
from nearby authoritative sources. Typical candidates are critical architectural constraints, non-obvious pitfalls,
unusual verification gates, and pointers to specialized guidance that agents would otherwise miss.

Detailed architecture, release procedures, data migration, security review, and other uncommon workflows should load
only when needed.

Anthropic recommends keeping the root `CLAUDE.md` lightweight and spending most of its tokens on genuinely non-obvious
gotchas. OpenAI recommends using `AGENTS.md` as a table of contents for a deeper documentation system. ([Claude][1])

---

### 2. Add only non-obvious, repository-specific information

A good test for each new line is:

> Would removing this line realistically cause an agent error?

If not, the line is unnecessary whether it is new or already present.

#### Useful

```md
- Do not edit files under `src/generated/`; run `pnpm generate`.
- Database migrations are append-only. Add a new migration instead of
  modifying one that has already been committed.
- Monetary amounts must use the `Money` value object; never use floating-point
  numbers for domain amounts.
```

#### Almost useless

```md
- Write clean code.
- Follow best practices.
- Be careful.
- Use meaningful variable names.
- Make sure the solution is production-ready.
```

Claude and Codex can infer standard language conventions from the surrounding code. The file should primarily convey
what the agent cannot reliably learn from the file system, tests, and existing code. Anthropic's official guidance
explicitly recommends excluding well-known conventions, long tutorial sections, detailed descriptions of every file,
and information that quickly becomes outdated. ([Anthropic][3])

---

### 3. Include only non-obvious command details

Do not write:

```md
Run the relevant tests.
```

Write an exact command only when the invocation has a repository-specific detail that agents may miss:

```md
- Run `pnpm verify` from `frontend/`; the root script skips browser tests.
```

Qualifying details include:

* the correct working directory;
* a required wrapper, order, or flag;
* a check omitted by the obvious task-runner target;
* special environment variables;
* platform flags;
* a non-obvious monorepo scope.

Do not copy a task runner's ordinary command catalog. Exact non-obvious invocations prevent agents from choosing the
wrong directory, scope, or gate. ([Claude][4])

---

### 4. Include only repository-specific completion gates

Generic expectations to test changes and report failures do not belong in repository instructions. Add a completion
gate only when the repository has a check or ordering requirement that an agent could plausibly miss.

Example:

```md
- Schema changes require `pnpm test:contract`; the ordinary test target does
  not run contract tests.
```

Both Anthropic and OpenAI emphasize executable feedback. Put ordinary verification in tooling or task workflows; keep
only the repository-specific exception in always-loaded instructions. ([Claude][4])

---

### 5. Add instructions after an observed error, not "just in case"

Good reasons to add a rule:

* the agent runs the wrong command a second time;
* code review repeatedly finds the same architectural error;
* the agent regularly edits generated code;
* the agent does not know about a nonstandard test structure;
* several developers have to repeat the same correction.

Bad reasons:

* "the agent could theoretically do this one day";
* "I saw a similar rule in someone else's repository";
* "more context can't hurt";
* "the `/init` generator wrote it."

Anthropic recommends updating the file when the same error recurs or when review reveals missing repository-specific
knowledge. OpenAI also recommends using recurring errors and PR feedback as signals to change the harness.
([Claude Platform Docs][5])

Mitchell Hashimoto describes a similar approach for Ghostty: agent instructions grew out of real agent mistakes. For
more complex problems, he creates programmable tools rather than adding prompt paragraphs, including fast test
commands, screenshot tooling, and other forms of automated verification. ([Mitchell Hashimoto][6])

However, do not automatically preserve every correction. Generalize it first:

```md
Bad:
- Yesterday Claude imported Foo from the wrong package.

Better:
- Domain types must be imported from `@acme/domain`; do not recreate or
  re-export them from feature packages.
```

---

### 6. Use progressive disclosure

Place information at the narrowest level where it is actually needed.

| Information type                               | Appropriate location                                      |
| ---------------------------------------------- | --------------------------------------------------------- |
| Always relevant repository-wide information   | Root `AGENTS.md` or `CLAUDE.md`                           |
| Rule for a specific directory                  | Nested `AGENTS.md`, `CLAUDE.md`, or Claude Rule           |
| Rare multistep procedure                       | Skill or specialized document                            |
| Plan for a complex, multiday task              | `PLANS.md` / ExecPlan                                     |
| Formal architectural description               | `docs/architecture/...`                                   |
| Deterministic prohibition                      | Hook, CI, linter, permissions, or sandbox                 |
| A developer's personal preferences             | Global or local unpublished file                          |

Claude supports path-scoped rules in `.claude/rules/`. Codex supports nested `AGENTS.md` and `AGENTS.override.md`.
Both ecosystems support Skills or separate workflow documents for complex procedures. ([Claude Platform Docs][5])

#### Claude Rule example

```md
---
paths:
  - "services/payments/**/*.ts"
  - "services/payments/**/*.tsx"
---

# Payments rules

- Represent domain amounts using `Money`; do not pass floating-point amounts.
- Applied migrations are append-only. Create a new migration.
- Verify changes with `pnpm --filter payments test`.
```

This rule does not consume context when work involves an unrelated frontend component.

---

### 7. Place a local rule next to the code it governs

In a monorepo, avoid collecting rules for every application in the root file.

Better:

```text
AGENTS.md
apps/
  web/
    AGENTS.md
  mobile/
    AGENTS.md
services/
  payments/
    AGENTS.md
  search/
    AGENTS.md
```

The root provides the shared rules and structure. `services/payments/AGENTS.md` describes only the commands,
constraints, and tests for the payments service.

Anthropic recommends a similar layered structure: the root file contains an overview and critical gotchas, while
subprojects get local files or path-scoped Rules. For large monorepos, Anthropic also recommends starting the agent in
the relevant subproject's directory. ([Claude][7])

---

### 8. Write each rule as "action + reason + safe path + verification"

#### Weak instruction

```md
Be careful with database migrations.
```

#### Strong instruction

```md
- Migrations under `db/migrations/` are append-only because production keeps
  audited checksums. Do not modify a committed migration; add a new one.
  Verify with `pnpm db:migrate:test`.
```

A good rule answers four questions:

1. What behavior is expected?
2. Where does it apply?
3. Why does it matter?
4. What should the agent do instead of the prohibited action?

For prohibitions, a standalone `NEVER do X` often leaves the agent without an acceptable way to complete the task.

In its guidance for code-review instructions, OpenAI recommends describing both the behavior to flag and a safe path
or acceptable exception. Anthropic's newer guidance similarly moves away from overly rigid absolute rules toward
explaining intent and using the model's judgment. ([OpenAI Developers][8])

---

### 9. Do not try to micromanage the style of newer Claude models

For modern models, Anthropic recommends fewer absolute rules such as:

```md
- Always add a comment above every function.
- Never use helper functions.
- All variable names must contain the domain prefix.
```

Such instructions often make the model ignore local code idioms or create artificial constructs. Prefer:

```md
- Match the naming, decomposition, and comment density of the surrounding code.
- Introduce a new abstraction only when existing nearby code does not provide
  an appropriate pattern.
```

Reserve absolute `always` and `never` rules for true invariants:

* do not modify generated files;
* do not log secrets;
* do not edit applied migrations;
* do not run destructive production commands;
* do not change a public API without explicit instruction.

Anthropic explicitly describes this as a shift from rules to judgment: newer models are better at learning comment
density, naming, and local idioms from the surrounding code. ([Claude][1])

---

### 10. Use examples sparingly

An example is useful when a format is difficult to describe unambiguously:

* a nonstandard API response;
* an internal dependency-injection pattern;
* a specific migration format;
* the expected PR summary format;
* the local error format.

However, many examples can unintentionally narrow the solution space: the model begins copying the example's surface
structure even when a different approach is needed.

Prefer:

* one short rule;
* one canonical file in the repository;
* when necessary, one positive and one negative example.

```md
- Follow the error-mapping pattern in
  `services/payments/src/handlers/create-payment.ts`.
```

This is usually better than inserting a long block of copied code into `AGENTS.md`. Anthropic's latest guidance
explicitly
warns that too many examples can constrain the exploration of solutions. ([Claude][1])

---

### 11. Link to the source of truth instead of copying it

Do not duplicate the following in the instruction file:

* all architectural documentation;
* the API schema;
* a list of every service;
* the release manual;
* the coding standard;
* dependency versions;
* a description of every file.

Provide routes:

```md
## Sources of truth

- Architecture decisions: `docs/architecture/index.md`
- API contracts: `openapi/api.yaml`
- Database conventions: `docs/database.md`
- Complex implementation plans: `.agent/PLANS.md`
```

This reduces the risk that documentation will diverge.

#### Claude import behavior

In `CLAUDE.md`, this entry:

```md
@docs/architecture.md
```

is not a regular link but an **import**: the file's contents are expanded and loaded into context. Use `@` only for a
document that truly needs to be always on.

For lazy routing, write:

```md
- For architectural changes, read `docs/architecture.md`.
```

Claude imports can be recursive, with a maximum depth of four levels. A large number of `@` imports does not save
context. ([Claude Platform Docs][5])

---

### 12. Move deterministic requirements from Markdown into tools

A Markdown instruction is probabilistic: the agent may overlook it, misinterpret it, or yield to a higher-priority
instruction.

Therefore:

| Requirement                         | Best mechanism                     |
| ----------------------------------- | ---------------------------------- |
| Formatting                          | Formatter                          |
| Prohibited import                   | ESLint/Biome rule                  |
| Architectural dependency            | Dependency/structure test          |
| Secrets must not be committed       | Secret scanner / pre-commit        |
| Every handler must have a test      | Structural test / CI               |
| Destructive commands are prohibited | Hook, permissions, sandbox         |
| A schema change requires a migration | CI check                           |
| UI work requires a screenshot        | Verification Skill or scripted tool |

Anthropic explicitly says that `CLAUDE.md` is context, not enforced configuration; guaranteed blocking requires hooks
or other control mechanisms. Böckeler and Fowler describe the same model as a combination of **feedforward**, provided
by instructions and Skills, and **feedback** from tests, linters, a type checker, and structural checks.
([Claude Platform Docs][5])

Practical rule:

> If a requirement can be checked programmatically, cheaply, and unambiguously, it should not exist only in
> `CLAUDE.md` or `AGENTS.md`.

---

### 13. Separate team, personal, and machine-specific instructions

For Claude:

* `~/.claude/CLAUDE.md`: personal instructions for all projects;
* `./CLAUDE.md` or `./.claude/CLAUDE.md`: team instructions for the project;
* `./CLAUDE.local.md`: local instructions for an individual developer, usually gitignored;
* managed instructions: centrally managed organizational policy.

Do not put the following in a team file:

* your preferred response style;
* a local path to an SDK;
* a personal alias;
* machine-specific details;
* temporary debugging settings.

This creates noise for the entire team and can break other developers' environments. The official Claude documentation
distinguishes these levels explicitly. ([Claude Platform Docs][5])

Codex similarly supports a user-level `~/.codex/AGENTS.md` or `AGENTS.override.md` and a project file hierarchy.
([OpenAI Developers][8])

---

### 14. Use one source of truth for Claude and Codex

Claude Code itself reads `CLAUDE.md`, while Codex reads `AGENTS.md`. Maintaining two complete, nearly identical files is
usually a poor choice because they quickly diverge.

A practical arrangement:

#### `AGENTS.md`

Contains the portable repository contract.

#### `CLAUDE.md`

```md
@AGENTS.md

## Claude Code

- Path-scoped constraints live in `.claude/rules/`.
- For non-trivial verification, use the `verify-change` skill.
```

Anthropic officially recommends importing `AGENTS.md` into `CLAUDE.md` or using a symlink when a single source of
instructions is required. ([Claude Platform Docs][5])

However, `AGENTS.md` should remain compact enough because importing it through `@AGENTS.md` makes its contents always on
for Claude.

---

### 15. Treat the instruction file like code

Useful organizational practices:

* keep the team file in Git;
* change it through a pull request;
* assign an owner or CODEOWNERS;
* explain in the PR which observed error the new rule addresses;
* check for contradictions;
* remove outdated instructions;
* review the file after a significant model update;
* do not commit `/init` output without manual editing.

Anthropic recommends assigning an owner and reviewing `CLAUDE.md` like code. Both Anthropic and OpenAI treat `/init` as
only an initial scaffold that must be reviewed, shortened, and adapted. ([Claude][9])

---

## What to include and exclude

| Include                                      | Exclude                                            |
| -------------------------------------------- | -------------------------------------------------- |
| Exact build/test/lint commands               | "Write high-quality code"                          |
| Non-obvious architectural invariants         | Standard language rules                            |
| Generated files and their regeneration command | The complete file tree                           |
| Nonstandard environment quirks               | A long onboarding tutorial                         |
| Key directories and their purposes           | A copy of the README                               |
| Canonical implementations to follow          | Large code snippets                                |
| Definition of Done                           | Rapidly changing statuses and versions             |
| The correct focused-test workflow            | Every possible project command                     |
| Prohibitions with a safe alternative         | Prohibitions without an explanation or safe path   |
| Pointers to specialized documents            | The complete contents of those documents           |
| Repeated agent failure modes                 | Hypothetical errors included "just in case"        |
| PR/review expectations                       | Rules already enforced by a formatter              |
| Required security constraints                | Secrets, tokens, and credentials                    |

This distinction matches the official Anthropic and OpenAI lists: instructions should contain commands, conventions,
workflow, constraints, and verification, but not generic advice, long documentation, or information that can be easily
inferred from the repository. ([Anthropic][3])

---

## Technical differences between `CLAUDE.md` and `AGENTS.md`

| Property                 | Claude Code                                                             | Codex                                                                    |
| ------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Primary file             | `CLAUDE.md`                                                             | `AGENTS.md`                                                              |
| Global file              | `~/.claude/CLAUDE.md`                                                   | `~/.codex/AGENTS.md`                                                     |
| Project file             | `./CLAUDE.md` or `./.claude/CLAUDE.md`                                 | `AGENTS.md` in the project tree                                          |
| Local private file       | `CLAUDE.local.md`                                                       | Usually global config/instructions or an unpublished override            |
| Nested instructions      | A nested `CLAUDE.md` loads when files in its subtree are accessed       | The chain from project root to the current working directory loads       |
| Path-scoped rules        | `.claude/rules/*.md` with `paths` frontmatter                           | Usually a nested `AGENTS.md`                                             |
| Override                 | Closer instructions are added later                                    | `AGENTS.override.md` takes precedence over `AGENTS.md` in the same dir   |
| Imports                  | `@path/to/file` expands the contents                                    | No special equivalent is usually needed; regular links are used          |
| Size                    | No line target; keep only useful, non-obvious instructions             | The platform applies a total project-instruction byte limit              |
| Loading verification    | `/context`, `/doctor`                                                   | Ask Codex to list active instructions and check logs                     |
| Strict enforcement      | Hooks, permissions, CI                                                  | Sandbox, approvals, CI, tooling                                          |

For Claude, parent files relative to the starting directory load at startup, while nested files may load as the agent
works with their corresponding files. Codex builds a chain from the project root to the **current working directory**,
so the directory where the session starts matters. ([Claude Platform Docs][5])

Codex uses `AGENTS.override.md` instead of the regular `AGENTS.md` in the same directory, but higher levels of the
hierarchy still remain in the combined instruction set. By default, the total project-instruction size is limited to
32 KiB. ([OpenAI Developers][8])

---

## Minimal selection example

This is a menu, not a required structure. Each line earns its place by preventing a non-obvious mistake:

```md
# Repository agent instructions

## Commands

- Run `pnpm verify` from `frontend/`; the root script skips browser tests.

## Non-obvious invariants

- Do not edit files under `src/generated/`; run `pnpm generate`.
- Database migrations are append-only. Add a new migration instead of
  modifying a committed one.
- Domain monetary amounts use `Money`; do not use floating-point numbers.

## Context routing

- Before changing database schemas, read `docs/database.md` for the required
  expand/migrate/contract sequence.
```

### What matters in this example

* the command contains a non-obvious working-directory rule;
* the invariants are repository-specific;
* the route points to a procedure that agents would otherwise miss;
* ordinary setup, testing, navigation, and workflow prose is absent.

---

## Example of splitting out a complex procedure

Instead of a long release procedure in `AGENTS.md`:

```md
## Release

For release work, use the `release` skill and follow
`docs/releasing/release-checklist.md`.
```

The Skill or separate document then contains:

* preflight checks;
* versioning;
* the changelog;
* the release branch;
* artifact verification;
* rollback;
* post-release validation.

For complex features and significant refactoring, OpenAI suggests a similar one-line route to `PLANS.md`:

```md
# ExecPlans

When implementing complex features or significant refactors, use an ExecPlan
as described in `.agent/PLANS.md`.
```

The main file states **when** a plan is needed without loading the entire planning workflow in every session.
([OpenAI Developers][10])

---

## Examples from real repositories

### Anthropic: `claude-code-action`

Anthropic's actual `CLAUDE.md` is concise. It contains:

* exact commands;
* a brief explanation of the project's purpose;
* the high-level execution flow;
* a few key concepts;
* a "Things That Will Bite You" section;
* only specific code conventions.

This matches the recommended structure: a brief overview plus operational gotchas, not a complete development guide.
([GitHub][11])

### Ghostty

The local `src/inspector/AGENTS.md` in Ghostty is very short. It states:

* the subsystem's purpose;
* where to find the generated C API;
* where the canonical widget examples are located;
* which macOS build flag is required;
* that this subsystem has no regular unit tests.

This is a good example of a local file: it contains no general philosophy, only information that directly prevents
errors in a specific directory. Mitchell Hashimoto connects these instructions to previously observed agent mistakes.
([GitHub][12])

### OpenAI Codex

The Codex root `AGENTS.md` is much larger. It contains many concrete, repository-specific rules: sandbox details, test
and formatting commands, architectural constraints, and review criteria. ([GitHub][13])

This does not make its size a recommendation. The example shows that:

* project complexity can sometimes justify the size;
* even a long file should be specific;
* localizing rules remains preferable to unbounded root-file growth;
* OpenAI's file remains below Codex's standard combined 32 KiB limit;
* an official repository is not necessarily the ideal universal template.

---

## What practitioners say

### Mitchell Hashimoto

Hashimoto calls this **harness engineering**: after an agent makes a mistake, change the execution environment as well
as the prompt. A simple recurring error may result in a rule in `AGENTS.md`; a more complex one may lead to a new tool,
a focused-test command, a screenshot workflow, or a programmatic check. ([Mitchell Hashimoto][6])

### Birgitta Böckeler and Martin Fowler

They recommend growing rules gradually, removing outdated ones as models improve, and combining instructions with
feedback mechanisms. They also warn that copying someone else's large setup files creates duplicates and contradictions
and produces an "illusion of control." ([martinfowler.com][14])

### Simon Willison

Good automated tests, focused-test commands, linters, a type checker, an accessible development server, and informative
errors contribute most to agentic coding quality. In other words, the best instruction file cannot compensate for a
repository that cannot be run and verified quickly. ([Simon Willison’s Weblog][15])

---

## Important limitation: `AGENTS.md` alone does not guarantee improvement

The **Evaluating AGENTS.md** study, revised in June 2026, found no universal improvement in task success from
repository-level context files. However, these files increased inference cost by more than 20% on average: agents
followed the instructions and explored the repository more, but the additional requirements often made the task harder
to complete. Minimal human-written instructions about nonstandard practices proved most justified, rather than
automatically generated general overviews. ([arXiv][16])

The study supports a narrower conclusion:

> A file's usefulness is determined not by its presence or length, but by the ratio of prevented errors to the cost of
> always-on context.

This is consistent with the official "give it a map" recommendation: the map should help the agent choose the correct
directory, command, or source of truth instead of reciting the repository's structure for the sake of an overview.

---

## Recommended maintenance loop

1. **Observe:** record a recurring error or unnecessary investigation.
2. **Classify:** is this an instruction, procedure, tool, or verification problem?
3. **Choose a mechanism:**

   * always-on knowledge → root file;
   * local knowledge → nested file / Rule;
   * uncommon procedure → Skill;
   * formally verifiable condition → CI/linter/hook;
   * complex project → ExecPlan.
4. **Make the smallest change:** add one rule instead of a new page-long section.
5. **Verify on a real task:** has the original error stopped occurring?
6. **Review through a PR:** are there any contradictions or duplication?
7. **Remove:** delete or route existing text when it fails the same usefulness test as new content. Check that an
   apparently obvious rule does not encode a non-obvious high-impact constraint before removing it.
8. **Verify loading:** use `/context` and `/doctor` for Claude; request the list of active instructions and logs for
   Codex. ([Claude][1])

---

## Final standard

For most repositories, a reasonable starting configuration looks like this:

* one compact team `AGENTS.md`;
* a small `CLAUDE.md` that imports `AGENTS.md`;
* a root file containing only commands, routes, gotchas, or completion gates that are non-obvious and broadly relevant;
* local rules that live next to the code;
* uncommon procedures moved into Skills and documents;
* complex tasks that use `PLANS.md`;
* formatting and architectural prohibitions enforced by tools;
* new instructions that come from real recurring errors;
* outdated instructions that are removed regularly.

Do not use a line target. Retain the minimum amount of always-on context without which the agent begins to make
repository-specific mistakes.

[1]: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models "The new rules of context engineering for Claude 5 generation models | Claude by Anthropic"
[2]: https://openai.com/index/harness-engineering/ "Harness engineering: leveraging Codex in an agent-first world | OpenAI"
[3]: https://www.anthropic.com/engineering/claude-code-best-practices "Best practices for Claude Code - Claude Code Docs"
[4]: https://claude.com/blog/building-verification-loops-in-claude-code-with-skills "Building verification loops in Claude Code with skills | Claude by Anthropic"
[5]: https://docs.anthropic.com/en/docs/claude-code/memory "How Claude remembers your project - Claude Code Docs"
[6]: https://mitchellh.com/writing/my-ai-adoption-journey "My AI Adoption Journey – Mitchell Hashimoto"
[7]: https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start "How Claude Code works in large codebases: Best practices and where to start | Claude by Anthropic"
[8]: https://developers.openai.com/codex/agent-configuration/agents-md "Custom instructions with AGENTS.md | ChatGPT Learn"
[9]: https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more "Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents | Claude by Anthropic"
[10]: https://developers.openai.com/cookbook/articles/codex_exec_plans "Using PLANS.md for multi-hour problem solving"
[11]: https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md "claude-code-action/CLAUDE.md at main · anthropics/claude-code-action · GitHub"
[12]: https://github.com/ghostty-org/ghostty/blob/ca07f8c3f775fe437d46722db80a755c2b6e6399/src/inspector/AGENTS.md "ghostty/src/inspector/AGENTS.md at ca07f8c3f775fe437d46722db80a755c2b6e6399 · ghostty-org/ghostty · GitHub"
[13]: https://github.com/openai/codex/blob/-/AGENTS.md "codex/AGENTS.md at main · openai/codex · GitHub"
[14]: https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html "Context Engineering for Coding Agents"
[15]: https://simonwillison.net/2025/Oct/25/coding-agent-tips/ "Setting up a codebase for working with coding agents"
[16]: https://arxiv.org/abs/2602.11988 "[2602.11988] Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
