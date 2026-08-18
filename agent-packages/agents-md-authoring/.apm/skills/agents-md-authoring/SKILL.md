---
name: agents-md-authoring
description: >-
  Create, audit, or improve repository-root AGENTS.md and CLAUDE.md files. Use when the user wants minimal,
  evidence-backed instructions that emphasize non-obvious repository constraints and remove low-value context.
---

# Draft and audit repository agent instructions

## Goal

Create a repository-ready draft of root `AGENTS.md` and `CLAUDE.md` when the files are missing or sparse. When they
already contain useful guidance, audit them against the best and bad practices below and produce the smallest
evidence-backed revision.

The result must help supported agent harnesses choose the right files, commands, validation, and change boundaries
without copying general documentation or inventing repository rules.

Require verified checkout evidence for additions. Apply the same usefulness test to existing and new content.
Authorship, uniqueness, or prior inclusion does not make an instruction useful. An existing ambiguous high-impact
constraint may be preserved temporarily or escalated under the exception below even when the checkout cannot confirm it.

Always mine repository-scoped history for candidates before drafting. Historical evidence can reveal recurring user
corrections, agent failures, and maintainer feedback that a static checkout does not expose, but it is never sufficient
on its own for a new instruction. Revalidate every historical candidate against the current checkout before selection.

## Artifact contract

Maintain this canonical root state:

- `AGENTS.md` contains the canonical shared repository instructions needed by supported harnesses. Keep subtree-specific
  shared guidance at its applicable scope.
- `CLAUDE.md` is a regular file that imports `AGENTS.md` and contains only genuinely Claude-specific guidance, if any:

```markdown
@AGENTS.md
```

Treat guidance as Claude-specific only when it depends on a verified Claude Code-only capability, command,
configuration, or resource; treat all other repository guidance as shared. When root Claude-specific guidance exists,
keep it after the import in one short `## Claude Code` section. If none exists, `CLAUDE.md` contains exactly
`@AGENTS.md` and one final newline. Apply the same pairing to included nested scopes.

If the repository differs, bring it to this state. For example:

- If neither file exists, create `AGENTS.md` from repository evidence and add the minimal `CLAUDE.md` import.
- If only `AGENTS.md` exists, improve it as needed and add the minimal `CLAUDE.md` import.
- If only `CLAUDE.md` exists, move shared useful content into a new `AGENTS.md` and retain only Claude-specific guidance
  after the import.
- If both contain instructions, merge unique shared content into `AGENTS.md`, remove duplicates, and keep only
  Claude-specific guidance after the import in `CLAUDE.md`.

Before rewriting `CLAUDE.md`, account for every useful instruction as shared or Claude-specific. Stop for user direction
if that classification or a content conflict cannot be resolved from repository evidence.

Treat other active instruction sources as audit inputs, not implicit edit targets. Classify every useful instruction by
scope and harness: move shared guidance into the applicable root or nested `AGENTS.md`; keep Claude-specific guidance in
`CLAUDE.md` or path-scoped `.claude/rules`. Resolve unique content, conflicts, shadowing, and duplicates only when the
required files are within the requested scope. Otherwise, stop and request the smallest required scope expansion or
decision.

Before editing either root artifact, inspect generated-file markers and repository manifests. If an artifact is
generated, edit its authoritative source only when that source is unambiguous and within the requested scope; otherwise
stop and report the ownership boundary.

Keep subtree-specific guidance out of the root file. If useful existing guidance belongs in a nested instruction file
outside the requested scope, do not delete its current copy; stop and request the smallest scope expansion or decision
needed to move it safely. Create or edit nested instruction files only when the user includes them.

## Choose a strategy

Choose one strategy after the initial audit of existing instructions and their applicable hierarchy. Record the choice
and reason in the final report.

### Greenfield

Use greenfield when both artifacts are absent or their useful repository-specific content is too sparse to support an
incremental update. Treat a file as sparse when it contains mostly placeholders, generic advice, stale task notes, or
unsupported commands rather than durable repository guidance.

Greenfield allows a new structure. Use it for a long existing file when only a small part passes the usefulness test;
file length or maintainer authorship does not require an incremental rewrite. Record each existing instruction in the
content ledger before replacing the structure so useful non-obvious meaning is not lost accidentally.

### Preserve

Use preserve when enough existing instructions pass the usefulness test that the current file remains a practical
structural base. Do not choose preserve merely because the file is long, detailed, or maintainer-written.

Use the existing `AGENTS.md` as the structural base only while that helps produce the smallest useful result. If only
a substantive `CLAUDE.md` exists, create `AGENTS.md` and map qualifying shared content by meaning while retaining
qualifying Claude-specific guidance. Replace mechanically enforced prose and copied procedures with a concise
operational pointer only when the pointer itself changes an agent's decision.

## Audit existing content

Treat the selected source state as audit input, not protected output. The selected state is the checkout or tree named
by the user, or otherwise the task-start worktree including uncommitted changes.

Apply the same selection test to every existing and proposed instruction. Keep a statement only when it is durable,
repository-specific, actionable, non-obvious from nearby authoritative sources, and likely to prevent a wrong file,
command, validation choice, or change boundary. Unique wording and maintainer authorship are not selection criteria.

Remove, shorten, or route content that merely summarizes the repository, repeats documentation, inventories visible
paths, restates commands without a non-obvious invocation detail, gives generic advice, or describes a rare procedure
better kept behind a link. A specific bad-practice classification is useful evidence, but it is not required when the
content plainly fails the selection test.

Preserve or ask about an ambiguous instruction only when it may encode a high-impact constraint that the checkout
cannot confirm, such as data safety, compatibility, security, generated ownership, or an approval boundary. Omit
low-risk unverifiable guidance and report the omission.

Assess each removal or material rewrite separately in the private content ledger and summarize the reasons in the final
report. Do not put the ledger or removal rationale in `AGENTS.md` or `CLAUDE.md`.

## Select useful content

Use these pairs when selecting and writing instructions:

| Topic | Best practice | Good example | Bad practice | Bad example |
| --- | --- | --- | --- | --- |
| Always-on content | Keep only non-obvious repository facts whose absence could cause an error. | `- Do not edit src/generated/; run pnpm generate.` | Add generic advice or facts obvious from the code. | `- Write clean code.` |
| Context placement | Keep shared rules at root, local rules near their code, and rare procedures behind links. | `services/payments/AGENTS.md`: `- Verify with pnpm --filter payments test.` | Load every subsystem and rare workflow into the root file. | `AGENTS.md`: `## Payments`<br>`## Mobile`<br>`## Release` |
| Commands | Keep only commands with a non-obvious wrapper, directory, order, flag, or scope. | `- From frontend/, run pnpm verify; the root script skips browser tests.` | Copy every task-runner command or make the agent guess a non-obvious invocation. | `- Install: pnpm install` |
| Completion gates | Keep only repository-specific checks whose omission could produce a false success. | `- Schema changes require pnpm test:contract.` | Restate generic testing expectations or use quality claims. | `- Make sure it is production-ready.` |
| Actionable constraints | State the scope, reason, safe alternative, and verification. | `- Committed migrations are append-only. Add a new one; run pnpm db:migrate:test.` | Give a vague warning or prohibition with no safe path. | `Be careful with migrations.` |
| Corrective rule lifecycle | Turn an observed mistake into a rule only when it could recur; generalize the invariant and remove obsolete rules. | `- Import domain types from @acme/domain; do not recreate them.` | Preserve one incident or a speculative concern as a permanent rule. | `- Yesterday Claude imported Foo incorrectly.` |
| Historical candidates | Search repository-scoped sessions, memory, and review discussions; revalidate every candidate against the current checkout. | A repeated wrong test invocation is confirmed by the current task runner before becoming a concise command rule. | Promote an anecdote, stale memory, transient tool failure, or reviewer preference directly into instructions. | `- A previous agent timed out, so never run integration tests.` |
| Deterministic enforcement | Put objective restrictions in tooling and name the relevant check. | `- Import constraints are enforced by ESLint; run pnpm lint.` | Rely only on Markdown for a mechanically checkable rule. | `- Never use a forbidden import.` |
| Model judgment | Let the agent follow surrounding code; document only verified local exceptions. | `- In legacy/, keep callbacks; its runtime does not support async functions.` | Micromanage style with universal rules. | `- Always comment every function.` |
| Canonical instructions | Keep shared guidance in `AGENTS.md`; let `CLAUDE.md` import it and add only Claude-specific guidance. | `@AGENTS.md`<br>`## Claude Code`<br>`- Use Claude Code's /verify-change command for non-trivial checks.` | Maintain two copies of shared instructions that can diverge. | `CLAUDE.md`: `<copy of AGENTS.md>` |

Apply this test to existing and new guidance: "Would omitting this instruction plausibly cause an agent to choose the
wrong file, command, validation, or change boundary in this repository?" Omit it when the answer is no. Prefer
non-obvious constraints over repository description.

## Use this example structure

Use this structure as a menu, not a template. Include a section only when at least one instruction passes the selection
test. Remove empty headings and placeholders. Do not create sections merely to describe the repository comprehensively.

```markdown
# Repository agent instructions

## Commands
- Run `<command>` from `<directory>` because <non-obvious prerequisite or scope>.

## Non-obvious invariants
- <Scope, reason, safe alternative, and verification for a repository-specific rule.>

## Context routing
- Before changing <area>, read `<document>` for <information not discoverable from nearby code>.
```

Keep the heading language consistent with the existing developer documentation. Use sentence-case headings,
repository-relative paths, exact commands, and one instruction per bullet. Add `Workflow` only for a non-obvious,
repository-wide sequence. Add `Escalation` only for a verified approval boundary.

## Build each section from repository evidence

Build a private evidence ledger with these fields: original source span and meaning, target section, proposed
instruction, exact evidence path, status (`qualifying`, `unresolved`, `conflicting`, or `omit`),
action (`add`, `preserve`, `rewrite`, `move`, or `remove`), and destination or replacement when applicable. Do not write
the ledger into `AGENTS.md` or `CLAUDE.md`.

### Historical evidence

Always attempt a repository-scoped search across all three channels before drafting:

- Prior agent-session transcripts: find repeated user requests or corrections and recurring tool failures while work
  was attributed to this repository. Read enough surrounding context to distinguish a repository trap from an agent
  mistake, sandbox restriction, network failure, or one-off environment problem.
- Agent memory: search by the repository's absolute path, remote identity, and stable names. Treat summaries and learned
  rules as leads, not corroboration; follow their raw source when available and guard against circular evidence copied
  from an earlier instruction file.
- Pull-request review comments and repository discussions: use available authorized read-only access to find recurring
  maintainer corrections, rejected approaches, and non-obvious validation or change boundaries. Distinguish a current
  maintained decision from a personal reviewer preference, unresolved proposal, or comment about code that no longer
  exists.

When read-only subagent delegation is available, assign one fresh-context researcher to each channel and run the three
searches in parallel. Give each researcher the selected repository identity, channel-specific access boundary, and a
request for source pointers, surrounding context, recurrence or impact, and candidate wording. Do not ask researchers
to edit instruction artifacts or make final best-practice, bad-practice, or inclusion decisions. If delegation is not
available, the primary agent performs the same three searches directly.

Record each relevant hit as a candidate, not as an instruction. Extend the private evidence ledger with the historical
source, recurrence or impact, generalized candidate, exact current-checkout evidence, revalidation status (`current`,
`stale`, `unverifiable`, or `conflicting`), and final disposition. Do not copy names, secrets, session narratives, or PR
discussion into the artifacts.

The primary agent must inspect the returned evidence and revalidate every historical candidate separately against
current code, configuration, task runners, CI, generated-file markers, or another authoritative source in the selected
checkout. The primary agent then applies the same best-practice, bad-practice, and omission tests used for all other
content. Only a `current` candidate with exact checkout evidence can qualify as a new instruction. Omit `stale` and
`unverifiable` candidates; resolve or report `conflicting` candidates without turning them into rules. Repetition
increases discovery priority but never lowers the selection bar.

Attempt all three searches even when they return no useful candidates. If a channel does not exist or authorized
read-only access is unavailable, record it as unavailable and continue; never silently substitute assumptions or broad
unscoped history searches.

### Scope

Read the root README, repository manifest, workspace configuration, and primary entry points. Add a scope statement only
when the repository purpose or boundary is easy to misunderstand and that misunderstanding would send an agent to the
wrong area. Do not restate the README or explain that root instructions are repository-wide.

### Repository map

Inspect manifests, stable top-level directories, module boundaries, generated-file headers, and code generation
configuration. Include a path only when knowing it changes where an agent should work. Keep ownership, generated-file
restrictions, and other behavioral rules under `Non-obvious invariants`.

### Commands

Inspect task runners such as `Makefile`, package scripts, build manifests, contributor documentation, and CI steps.
Record a command only when choosing or invoking it requires a non-obvious wrapper, directory, order, flag, prerequisite,
or scope. Prefer repository wrappers over reconstructed invocations. Do not copy a complete command catalog that is easy
to locate in a task runner or contributor guide, and do not claim a command works merely because it is defined.

### Non-obvious invariants

Inspect contributor policies, generated markers, schema or API generation, ownership, existing instructions, and
maintained troubleshooting notes. Keep only repository-specific boundaries or traps that prevent a realistic mistake.
State each rule's scope, reason, safe alternative, and verification or enforcement mechanism. Route subtree-specific
rules to their correct nested target. When tooling already enforces a rule, keep only the operational pointer or
command.

### Completion gates

Inspect CI workflows, test configuration, and task runners. Add completion criteria only for non-obvious repository
gates, generated outputs, compatibility checks, or required ordering. Do not restate the generic expectation to run
relevant tests or report checks. Keep exact commands only when their choice or invocation is not obvious.

### Context routing

Choose maintained documents or skills for details that do not belong in always-on context. Add a route only when an
agent is unlikely to find the source at the point of need. State when and why to follow it. Use normal path references;
apart from the canonical `@AGENTS.md`, do not add eager `@imports` to either root artifact.

### Optional sections

Add `Workflow` only for a concise, non-obvious sequence that applies repository-wide. Route rare multi-step procedures
to a skill or maintained document. Add `Escalation` only when repository evidence defines an approval boundary.

## Workflow

1. Resolve the repository root and requested scope. Inspect `git status`, generated-file markers, manifests, and source
   artifacts. Preserve unrelated worktree changes. Resolve artifact ownership before editing; stop if the authoritative
   source is ambiguous or outside scope.
2. Discover root and nested `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, and `.claude/rules/*.md`. Read the root
   artifacts and every instruction file whose scope overlaps proposed root guidance. Record the correct shared or
   Claude-specific target for every useful instruction, plus precedence, unique content, conflicts, shadowing, and
   duplicates. Before editing, capture immutable complete before snapshots of all overlapping instruction artifacts
   outside the repository and identify the selected source state.
3. Mine repository-scoped agent-session transcripts, agent memory, and pull-request review comments or discussions as
   described above. When delegation is available, use one read-only researcher per channel in parallel; otherwise search
   directly. Attempt every channel, record unavailable access, and add relevant hits to the ledger as candidates.
4. As the primary agent, inspect the historical evidence and revalidate each candidate separately against the selected
   checkout. Apply the same usefulness test and best-practice and bad-practice filters to existing, proposed, and
   historical content. Mark qualifying non-obvious rules, stale or unverifiable candidates, low-value material,
   conflicts, duplicates, wrongly scoped guidance, and material gaps.
5. Choose greenfield or preserve from that audit. Resolve material conflicts from authoritative checkout evidence.
   When an unverified existing instruction may encode a high-impact constraint, preserve it temporarily or stop for
   user direction as defined above. Omit low-risk unresolved guidance and report it instead of inventing support.
6. Build each target section from checkout evidence using the section-specific rules above.
7. Draft the smallest complete result:
   - For greenfield, create `AGENTS.md` from the example structure and create the minimal `CLAUDE.md` import, adding a
     Claude-specific block only when checkout evidence justifies it.
   - For preserve, use the existing `AGENTS.md` only as a practical editing base. Apply the same selection test to its
     content, add missing non-obvious instructions, and remove or route low-value material.
   - For a populated `CLAUDE.md`, move useful shared content into `AGENTS.md`, retain only useful Claude-specific
     guidance after `@AGENTS.md`, and account for every original block without duplication.
   - For useful wrongly scoped guidance outside the requested edit scope, stop before deleting its current copy or
     rewriting a containing `CLAUDE.md`; report the correct target and request the smallest necessary decision.
8. If a target artifact is generated, edit its authoritative source and run the documented safe generation or
   compilation command. If that command is unavailable, unsafe, or unauthorized, stop before changing source or output.
9. Review the result instruction by instruction. Confirm that each retained or added line passes the selection test and
   each deletion has a stated reason. Remove sections that exist only for structural completeness. Do not ask for
   separate approval when the user already requested the local edit and the result is unambiguous.
10. Run the independent research validation below for every created or modified instruction artifact. Apply actionable
   findings from each review, but run no more than two review cycles.
11. Validate both artifacts after the independent review work is complete and produce the detailed user report below.

During this workflow, use remote access only for the repository-scoped read-only review and discussion search above; do
not browse for other repository facts. Do not install dependencies or run deployment, migration, credential, release,
or production commands. Do not commit, push, or open a pull request unless the user separately requests it.

## Run independent research validation

- For each created or modified instruction artifact, launch a neutral fresh-context reviewer before completion. Cover
  both the source and destination when content moves between instruction files.
- Give it the neutral task request, requested scope, relevant explicit user decisions, selected source-state identity,
  immutable complete before snapshots, complete after content, both references in full, the full diff, overlapping
  active instructions, and read-only checkout access.
- Give it the neutral selection contract: existing and new content must pass the same usefulness test. It must flag
  obvious, duplicated, descriptive, generic, or easily discoverable content that remains, and confirm that removed text
  did not contain a non-obvious high-impact constraint. Require evidence for both retention and removal decisions.
- Do not give it this skill, the author's ledger, conclusions, suspected defects, or proposed fixes.
- Compare every removal and material rewrite with the source content and diff. Return `CHANGES_REQUIRED` when a useful
  non-obvious instruction was lost or when low-value existing content was retained without passing the selection test.
- Check additions for evidence, utility, exactness, scope, conflicts, placeholders, and empty or generic lines.
- Require file and hunk coverage, evidence-backed findings, and `PASS`, `CHANGES_REQUIRED`, or `REVIEW_INCOMPLETE`.
- Finish after a first-cycle `PASS`. Otherwise, apply the findings and run one fresh review. After cycle two, apply all
  actionable findings and validate the corrected result, but do not run a third review. Report the task incomplete only
  when a material finding cannot be resolved or the corrected result fails validation.
- If no independent cycle can run, report the blocker and leave the task incomplete.

## Validate the result

Complete this checklist with read-only checks and `git diff --check`:

- [ ] **Instruction files:** root `AGENTS.md` is the canonical shared file and has exactly one level-one heading. Every
  edited `CLAUDE.md` is a regular file, starts with `@AGENTS.md`, and ends with one newline. Shared guidance exists only
  in `AGENTS.md`; any Claude-specific guidance appears once under `## Claude Code`. Applicable nested instructions and
  `.claude/rules` contain no same-scope conflicts or duplicated guidance.
- [ ] **Evidence and scope:** every new repository fact maps to an exact checkout source. Every instruction is durable,
  actionable, and placed at the narrowest applicable scope. Each command exists in the repository, and each prohibition
  names its scope, reason, safe alternative, and verification or enforcement mechanism.
- [ ] **Historical evidence:** repository-scoped transcripts, agent memory, and review discussions were each searched
  or explicitly recorded as unavailable. Every historical candidate has an individual current-checkout revalidation
  result and disposition; only `current` candidates with exact checkout evidence became new instructions. The user
  report lists historical findings separately and identifies each source channel.
- [ ] **Minimality:** every retained or added instruction passes the omission test. Existing and new text use the same
  bar. No section exists only because it appeared in the example structure, and no prose restates information that an
  agent can find quickly and unambiguously in a nearby authoritative source.
- [ ] **Source comparison:** compare the immutable before snapshots with the complete result. Account for every removal
  or material rewrite and confirm that no non-obvious high-impact constraint was lost.
- [ ] **Content hygiene:** no placeholders, copied documentation, unsupported commands, task notes, secrets, local
  settings, or trailing whitespace remain.
- [ ] **Checks:** run relevant safe repository checks and record their results. Distinguish facts established by source
  inspection from commands actually executed.
- [ ] **Independent review:** the content received one or two review cycles and all actionable findings were applied.
  After cycle two, validate the corrections without a third review. Any unresolved material finding leaves the task
  incomplete.

## Report to the user

Return a detailed, concrete comment after editing. Include:

1. Strategy: `greenfield` or `preserve`, with the evidence that determined the choice.
2. Created: each new artifact and why it was needed.
3. Changed: each material addition or rewrite, its source file and exact line range, original meaning, target section,
   exact evidence, destination or replacement, and why the result passes the usefulness test.
4. Removed: each deleted block or instruction, its source file and exact line range, the failed selection criterion,
   supporting evidence, and any destination when moved. Never reproduce a removed secret.
5. Preserved: each retained instruction, its source file and exact line range, its destination in the result, and why it
   qualifies. Group adjacent source lines only when they share the same disposition and evidence.
6. Historical findings: add a separate concise section. For each historical finding that became an instruction, give
   only the finding, why it was added including the plausible wrong choice if omitted, and its source (`transcript`,
   `memory`, or `GitHub`) with an exact pointer. State that no historical findings qualified when none were included,
   and note unavailable channels in one sentence. Keep rejected historical candidates in the omitted summary rather
   than listing them individually here. Do not expose secrets, personal details, or session narratives.
7. Omitted or unresolved: non-blocking missing facts, rejected candidates, and wrongly scoped guidance with its correct
   destination. Do not finish an edit with an unresolved material instruction or precedence conflict.

If cycle two did not return `PASS`, add one short notification that its findings were applied but the corrected result
did not receive another independent review. Do not include the review history or reviewer details.
