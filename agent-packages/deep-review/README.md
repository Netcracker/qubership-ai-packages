# deep-review

A user-invoked skill that reviews a repository, a microservice, or a system of interacting components as several
independent axes rather than one pass. Each axis carries its own filter for what counts as a finding, every finding is
attacked before it survives, and the `architecture` axis runs on a prompt distilled from what the evidence axes
actually found.

Use it for a coarse review of a service, an operator, a library, or a system of services you want examined end to
end: component boundaries, contracts, dependencies, ownership, and failure domains, with the implementation read as
far as a finding needs it. The smallest target is a repository or a deployable. A single class, function, file, or
diff has no archetype to classify and no surface to profile, so reach for `adversarial-code-review` (a pull request
or merge request), `codex-review` (a branch diff or a commit), or a direct review there.

## How a run is shaped

1. **Profile.** Read the build files, the public surface, and the layout, classify the target against
   `references/archetypes.md`, and list the surfaces it exposes — `kubernetes`, `cli`, `helm`, and so on. For a
   system, list the components with their checkouts and revisions, and the interactions between them. The archetype
   selects the axes; the surfaces decide what counts as a breaking change.
1. **Agree the focus.** The skill writes a questions file with its own answers pre-filled, and you edit it in place:
   which axes run, what is out of scope, the depth (`coarse`, the default, executes only what already exists and
   reports at the level of contracts and boundaries; `deep` adds reproduction tests, mutation runs, and stress tests),
   whether the axes may touch a runtime. Every agent reads the resolved file.
1. **Run the pipeline.** A dynamic workflow fans out scout axes, then evidence axes, each followed by its own
   refutation pass as soon as it finishes, then synthesis, then consolidation with a completeness critic.

The unit of work is a **dossier** — a directory under the reviewed repository holding the profile, the agreed focus,
the generated prompts, the per-axis reports, and a normalized findings file. Nothing passes between stages as chat
text, so any stage can be re-run on its own, and a review survives the session that started it.

Twenty-four axis definitions ship with the skill, covering correctness, tests and test levels, concurrency and
lifecycle, the error model, API compatibility, internal contracts between components, API UX, protocol conformance,
security, performance, data lifecycle, dependencies, build and release, deployment config, telemetry, observability and
operability, runtime verification, upgrade and migration, docs and onboarding, documentation pages, frontend web, least
surprise, and architecture. Seven surface packs cover `cli`, `helm`, `helm-qubership`, `kubernetes`, `gitops-argocd`,
`mcp`, and `rest-http`.

On a monorepo, or any repository whose parts differ in language, runtime, or owner, an axis can run as several slices,
one agent per part (`paths`) or per join between parts (`seams`). The questions file proposes the slices, each slice
gets its own report and verifier, and a digest per sliced axis feeds the consolidator.

## Install

```bash
apm install deep-review@qubership-ai-packages
```

Invoke it by name — `/deep-review`, or by asking for a deep or multi-axis review of a repository, a service, or a
system.

The package declares `targets: [claude]`, because other agents have no `Workflow` tool to run its pipeline. APM 0.27.0
and later deploy the skill to Claude Code only; an older APM ignores the field and copies the skill to every target.
`SKILL.md` states the requirement in its opening paragraphs, so an agent that receives the skill through an older APM
stops before creating a dossier instead of calling a tool it does not have.

## Requirements

- Claude Code v2.1.154 or later with [dynamic workflows](https://code.claude.com/docs/en/workflows) enabled: the
  pipeline is a workflow script, and the skill calls it with `Workflow({ scriptPath })`. On Pro, turn workflows on in
  `/config` → **Dynamic workflows**.
- A shell, `git`, and whatever the repository under review needs to build and test. The profile step runs those
  commands and records the ones that work, so the axes do not each rediscover them.
- The rubric skills three axes apply, installed beside this one: `test-authoring` for `test-strategy`,
  `docs-page-authoring` for `docs-pages`, and `telemetry-authoring` for `telemetry`. `apm install` brings all three as
  dependencies. The profile step lists the rubrics it finds, and the workflow refuses to start an axis whose rubric is
  missing. `telemetry` also judges the wording of messages by the developer-style skill of their language
  (`english-developer-style` for English) where one is installed, and says in its coverage where none was.
- Optional: a structural-search CLI such as `sb` for the surface and cycle summaries in the profile step. Without it,
  read the source roots directly.

A real run is large — a twelve-axis review spends its budget across scout, evidence, refutation, synthesis, and
consolidation stages, and the verifiers alone took 35% of it in the run the skill's model guidance is based on. The
default configuration for a service or a system is the coarse one: the archetype's default axis set from
`references/archetypes.md` (five to eight evidence axes and `architecture`, plus the two scout axes on a single
repository) at `depth: coarse`. Default every phase to a cheaper model while you are still shaping the run.

## Reports

A run writes two reports for two readers. `README.md`, one card per root-cause problem under `issues/`, and
`findings.csv` are for the team that fixes the code: the README says what the review is and what the team is asked to
do, and lists the problems in three priorities, each linked to a card that can be copied into a tracker.
`audit/synthesis.md` is for the person who ran the review: disagreements between axes, coverage, refutations, and the
verification rate. `scripts/findings-csv.py` rebuilds `findings.csv` and the generated blocks of the cards after a
manual edit of `findings.jsonl`.

The reports are written in Russian, with identifiers and paths in English. The section headings are fixed as
`references/report-format.md` writes them, some in English and some in Russian, because the workflow and the
completeness critic find sections by heading text. The Russian headings and labels live in `workflow/deep-review.js`,
`references/report-format.md`, `references/axes/architecture.md`, `scripts/findings-csv.py`, and `SKILL.md`; the
English ones the pipeline searches for are named in `workflow/deep-review.js`. Change the report language by renaming
them in all of these files at once.

## Paths

`SKILL.md` refers to its own files through `${CLAUDE_SKILL_DIR}`, which Claude Code replaces with the directory the
skill was loaded from: `~/.claude/skills/deep-review` for a user-level install, `<repo>/.claude/skills/deep-review` for
a project-level one. The session passes the same directory to the workflow as `args.skill`, and every axis prompt points
its agent at the reference packs under it. The script throws when `args.skill` is missing or is not an absolute path,
because an axis that cannot read its reference pack reviews from memory and does not report that it did.

A user-level install puts the workflow script outside the reviewed repository. Claude Code starts a workflow only from
a script the session may read, so add the skill directory with `/add-dir ~/.claude/skills/deep-review` (or a Read
allow rule for that path) before the first run; a project-level install needs nothing.
