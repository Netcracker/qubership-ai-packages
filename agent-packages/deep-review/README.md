# deep-review

A user-invoked skill that reviews a whole repository as several independent axes rather than one pass. Each axis
carries its own filter for what counts as a finding, every finding is attacked before it survives, and the axes that
synthesize — architecture, API UX — run on prompts distilled from what the evidence axes actually found.

Use it for a library, a service, or an operator you want examined end to end. It is not a pull-request reviewer: a
single diff has no archetype to classify and no surface to profile, so reach for the PR review skills there.

## How a run is shaped

1. **Profile.** Read the build files, the public surface, and the layout, classify the repository against
   `references/archetypes.md`, and list the surfaces it exposes — `kubernetes`, `cli`, `helm`, and so on. The archetype
   selects the axes; the surfaces decide what counts as a breaking change.
1. **Agree the focus.** The skill writes a questions file with its own answers pre-filled, and you edit it in place:
   which axes run, what is out of scope, how deep to go, whether the axes may touch a runtime. That file, resolved,
   is what every agent reads.
1. **Run the pipeline.** A dynamic workflow fans out scout axes, then evidence axes, then a refutation pass over every
   finding, then synthesis, then consolidation with a completeness critic.

The unit of work is a **dossier** — a directory under the reviewed repository holding the profile, the agreed focus,
the generated prompts, the per-axis reports, and a normalized findings file. Nothing passes between stages as chat
text, so any stage can be re-run on its own, and a review survives the session that started it.

Eighteen axis definitions ship with the skill, covering correctness, tests, concurrency and lifecycle, the error model,
API compatibility and API UX, protocol conformance, security, performance, data lifecycle, dependencies, build and
release, deployment config, observability and operability, runtime verification, upgrade and migration, docs and
onboarding, and architecture. Six surface packs cover `cli`, `helm`, `helm-qubership`, `kubernetes`,
`gitops-argocd`, and `mcp`.

## Install

```bash
apm install deep-review@qubership-ai-packages
```

Invoke it by name — `/deep-review`, or by asking for a deep or multi-axis review of a repository.

The package declares `targets: [claude]`, because other agents have no `Workflow` tool to run its pipeline. APM 0.27.0
and later deploy the skill to Claude Code only; an older APM ignores the field and copies the skill to every target.

## Requirements

- Claude Code v2.1.154 or later with [dynamic workflows](https://code.claude.com/docs/en/workflows) enabled: the
  pipeline is a workflow script, and the skill calls it with `Workflow({ scriptPath })`. On Pro, turn workflows on in
  `/config` → **Dynamic workflows**.
- A shell, `git`, and whatever the repository under review needs to build and test. The profile step runs those
  commands and records the ones that work, so the axes do not each rediscover them.
- Optional: a structural-search CLI such as `sb` for the surface and cycle summaries in the profile step. Without it,
  read the source roots directly.

A real run is large — a twelve-axis review spends its budget across scout, evidence, refutation, synthesis, and
consolidation stages, and the verifiers alone took 35% of it in the run the skill's model guidance is based on. Start
with a narrow axis list, and default every phase to a cheaper model while you are still shaping the run.

## Reports

The reports are written in Russian. The instructions are in English, but the headings and labels the reports must carry
are Russian wherever they are named: in `workflow/deep-review.js`, `references/report-format.md`,
`references/axes/architecture.md`, and `SKILL.md`. Rename them in all four to change the report language.

## Paths

`SKILL.md` refers to its own files through `${CLAUDE_SKILL_DIR}`, which Claude Code replaces with the directory the
skill was loaded from: `~/.claude/skills/deep-review` for a user-level install, `<repo>/.claude/skills/deep-review` for
a project-level one. The session passes the same directory to the workflow as `args.skill`, and every axis prompt points
its agent at the reference packs under it. The script throws when `args.skill` is missing, because an axis that cannot
read its reference pack reviews from memory and does not report that it did.
