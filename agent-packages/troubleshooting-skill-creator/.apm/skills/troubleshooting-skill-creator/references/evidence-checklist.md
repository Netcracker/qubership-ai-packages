# Case verification checklist

Format and safety are audited by `troubleshooting-format.md`. This checklist governs the claims inside each case:
whether the cited sources support them, whether the failure can occur in this deployment, and whether the proposed
checks and fixes follow from the shipped code and configuration.

Run this audit over the compiled reference with a reviewer whose context does not contain the drafts or research notes.
The reviewer receives only the reference, this checklist, and the target repository path. Authors use the same rules
while writing, but an independent pass gates the handoff.

## Keep verification read-only

Verification observes source and generated artifacts. It never changes or starts a system.

Allowed verification includes:

- Reading repository code, manifests, templates, tests, and documentation.
- Rendering configuration offline, for example with `helm template` or a tool's documented read-only dry-run mode.
- Running static validators against generated files.
- Inspecting logs, configuration, command output, and other artifacts the user supplied.

Do not access a live cluster or service, start or restart a component, reproduce a failing path, apply a fix, or edit
the target repository during the audit. If a claim cannot be confirmed without one of those actions, leave the system
untouched and report the claim as unconfirmed.

## Report only gaps

Do not add evidence grades, confidence ratings, verification markers, or audit notes to
`references/troubleshooting.md`. The final reference contains the troubleshooting cases and their required sources,
not the history of how they were reviewed.

In chat, report only what the audit could not confirm. For each gap, name the case, the unconfirmed claim, why the
available evidence is insufficient, and what artifact or maintainer input would resolve it. Omit confirmed cases from
the report. If the audit finds no gaps, continue without a case-by-case verification appendix.

## Verify claims against the deployment

- **Check every source.** Open or inspect every required `**Sources:**` entry and confirm that it supports the symptom,
  cause, or fix attributed to it. A citation that only mentions the component does not support the case.
- **Render the configuration path offline.** Use the case's exact values with read-only renderers or validators. Reading
  a template predicts its output; rendering confirms what this repository produces without touching a deployment.
- **Pin upstream claims to the version that ships.** Determine the version from the build pipeline, Dockerfile, builder
  configuration, or lockfiles consumed by the build rather than from a manifest that the build does not use.
- **Attribute behavior to the implementing layer.** A value can be rewritten by a chart, defaulted by the component, or
  inherited upstream. Cite the repository file, upstream source, or documentation that implements the behavior.
- **Check shipped defaults.** A default cache, retry, or fallback can narrow a failure condition. State the actual
  precondition instead of describing the default installation as more fragile than it is.
- **Check command availability statically.** Verify diagnostic commands against the Dockerfile, image manifest,
  packaging files, or other repository evidence. If that evidence cannot confirm a binary or permission, report the
  command as unconfirmed rather than running it against a deployment.

## Constrain what a case asserts

- **Root cause names a traced mechanism.** An observation that merely co-occurs with the failure belongs under symptoms
  or checks. Back frequency words such as `usually` or `rare` with incident evidence, or remove them.
- **Risk statements name their preconditions.** Downtime, data-loss, and OOM claims identify the replica count, rollout
  strategy, probe behavior, capacity, or other condition that makes the risk reachable.
- **Fixes follow from evidence.** Trace each fix through code, configuration, a repository source, or authoritative
  upstream documentation. Use only offline renderers and read-only validators to check the resulting configuration.
- **Overrides state replace-versus-merge semantics.** Verify whether each override merges with defaults or replaces
  them, and state the behavior in the case.

## Keep the file coherent

- **Cite durably.** In-repository files use `path:line`. Third-party code uses `module@version/file` without a line
  number, so the reference remains useful after dependency updates.
- **Shared risks live once.** Put a warning shared by several cases in one reference section and link to that section by
  title from every affected case.
- **Cases do not contradict themselves or their neighbors.** Cross-reference cases that explain the same symptom with
  different causes, and resolve any symptom that the case's own root cause rules out.
