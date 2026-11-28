# openspec

APM package with the [OpenSpec](https://github.com/Fission-AI/OpenSpec) change workflow for agent sessions. Depend on
this one package and the agent picks up the whole workflow — the skills that propose a change, explore the problem
before committing to one, implement its tasks, keep its artifacts coherent, verify the result against them, and archive
it — through the package's transitive APM dependencies.

OpenSpec keeps a change's plan in the repository: a proposal, the specification deltas it introduces, and the task list
that implements them. The skills read and write that tree through the OpenSpec CLI, so the agent's plan survives a
session and a second reviewer can audit it.

## Prerequisite: the OpenSpec CLI

The skills shell out to `openspec`, and they check that the project already has an OpenSpec root before they write
anything. Install the CLI (`npm install --global @fission-ai/openspec`) and run `openspec init` in the project once;
without it the skills have nothing to drive. APM installs the skills, not the CLI.

## What it includes

Each dependency is one upstream skill, installed under the harness's own skills directory:

- `openspec-propose` — draft a new change with its proposal, specification deltas and task list in one step.
- `openspec-explore` — a thinking partner for investigating an idea or clarifying requirements before a change exists.
- `openspec-apply-change` — work through the tasks of a change, from the first task to resuming an interrupted one.
- `openspec-update-change` — revise the artifacts of an in-flight change and keep them consistent with each other.
- `openspec-verify-change` — check that the implementation matches the artifacts, before archiving.
- `openspec-sync-specs` — fold a change's delta specs into the main specs without archiving the change.
- `openspec-archive-change` — finalize a completed change and move it to the archive.

## Source and pinning

The skills are not copied into this repository. Each dependency points at its own directory in the upstream repository,
pinned to the commit of an OpenSpec release tag, with that tag in the trailing comment:

```yaml
- Fission-AI/OpenSpec/skills/openspec-propose#f1cd852f4edce22b8df9548a4df889172ca8ff25  # v2.2.0
```

Renovate rewrites the SHA and the tag together, in one grouped pull request for all seven. Review it as a content
change rather than a build fix: the package ships agent instructions, so no test here fails when upstream rewrites
them. The seven pins move as one set, because a mixed set describes two different workflows at the same time.
