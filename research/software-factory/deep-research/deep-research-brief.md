# Existing systems for Qubership Software Factory

Use ChatGPT Deep Research to investigate existing systems that already implement principles similar to Qubership Software Factory. Write the research plan, any clarification, and the complete final report in English. Proceed with the assumptions below rather than asking introductory questions.

## Decision to support

Determine whether we should adopt an existing system, extend one, combine a small number of existing components, or build our own orchestration layer. Finding and evaluating implemented solutions comes before proposing a new implementation. This is research for the whole system, not a prototype or MVP scope exercise.

The attached requirements-snapshot.md is the authoritative requirements baseline, containing F01–F54 with MUST, SHOULD, and MAY priorities. Read it in full and preserve these distinctions. Its comments provide context and examples, not additional mandatory requirements. Do not treat unanswered design questions as agreed decisions.

## Product context

We want an event-driven GitHub App that launches configurable Software Factory workflows for connected repositories. A priority scenario is issue-based development: discuss a plan, implement changes, and prepare a PR. Other workflows include review, bug fixes, research, and documentation updates.

The primary deployment is a self-hosted application and workers on the same ordinary machine. Independent workers on other machines are optional. A hosted-only SaaS is not an adequate sole foundation. Kubernetes and remote personal computers are not prerequisites. Future GitLab support from a shared codebase and enterprise self-hosting matter.

Workflows and agent profiles are centrally configured without changing connected repositories. APM packages define agent profiles. A workflow can combine compatible harnesses and models; a default multimodel harness is replaceable, and Claude Code and Codex are required integrations. API and subscription access modes matter. Unsupported combinations must fail before execution without silently substituting a model, harness, or paid API.

Each run pins an immutable snapshot of its workflow graph, APM profile versions, harnesses, models, and launch parameters. Human review checkpoints are configurable. Multiple workflows per repository and label-persisted statuses for autonomous workflows are SHOULD capabilities. Standardized label actions or explicit commands, rather than arbitrary free-text comments, are the preferred workflow control signals.

Authorization checks the person authorizing an action. Requests and opinions from non-allowlisted commenters must not influence agent work. PRs from external authors are excluded; the exact permission mechanism and definition of an external author remain open. A model must not receive a publication token: an agent produces a result artifact and a separate programmatic component publishes it.

Repository caching, automatic recovery when sufficient state survives, retained issue discussion context, agent telemetry, actual API expenses, and separately estimated subscription costs using current provider prices are relevant. Use the complete attachment for exact scope and priorities.

## Research scope and method

1. Discover a broad set of maintained or otherwise relevant existing systems. Cover complete coding-agent orchestration systems, GitHub/GitLab automation applications, and reusable orchestration components. Distinguish these categories instead of calling every CLI agent a Software Factory.
2. Shortlist approximately five of the strongest candidates for detailed comparison. Include commercial systems only where they offer a relevant capability benchmark or a verifiable self-hosted offering; do not let hosted-only products crowd out deployable open-source alternatives.
3. Possible discovery seeds include OpenHands, SWE-agent, Open SWE, PR-Agent/Qodo, and commercial coding-agent platforms such as Factory, Devin, or GitHub's coding-agent offerings. These are search leads, not claims that the products qualify or that the names, ownership, deployment modes, or capabilities are unchanged. Search beyond this list.
4. Treat denifilatoff/agent-flow and denifilatoff/reviewctl as our reference implementations, not independent alternatives that validate the decision to build. If their public code is accessible, use them only to clarify comparable behavior and label them separately. If inaccessible, do not infer their internals.
5. For each shortlisted system, inspect official documentation and public implementation where available. Distinguish features implemented in a released version or current commit, documented features not confirmed in code, extension points requiring development, roadmaps, and unknowns. Do not claim runtime verification from static source inspection.
6. Record the research date, repository identity, license, release or commit examined, maintenance evidence, and exact edition for gated features. Cite official docs and stable source permalinks for consequential claims. Repository stars are not evidence of feature completeness or production readiness.
7. Verify rather than assume GitHub App support, webhook handling, arbitrary workflow graphs and cycles, human checkpoints, run snapshots, credential boundaries, harness interchangeability, subscription support, and self-hostability. Generic extensibility does not mean an integration already exists.
8. Distinguish restart recovery, retry, event deduplication, and duplicate-publication prevention. Likewise, distinguish cloned worktrees from process isolation, retained conversation text from native session resumption, and telemetry from trustworthy cost accounting.
9. Also inspect stage-result validation, revision-bound review, isolated working directories, cancellation, retry/time limits, operator visibility, and configuration validation. These are additional comparison questions, not newly accepted requirements in our baseline.
10. For absent features, explain whether a small adapter or a core architectural change would be required. Do not invent implementation effort estimates, benchmarks, or undocumented subscription entitlements.

## Required report

1. Executive conclusion: the strongest adoption/extension options, major blockers, and whether a custom orchestration layer is justified by the evidence. Avoid recommending a rewrite merely because no product matches every optional feature.
2. Landscape table: candidate, category, deployment model, license/edition, GitHub/GitLab integration, harness/model flexibility, maintenance evidence, and reason to include or exclude it.
3. Detailed profiles for the shortlist: architecture, workflow/state model, human interaction, execution and repository handling, recovery, security/publication boundary, observability/costs, and practical integration gaps. Explain at least one end-to-end issue-to-PR path supported by each, or explicitly state that it is not supported.
4. A requirements coverage matrix for F01–F54 across the shortlist. Use supported, partial, requires custom development, unsupported, or unknown, with brief evidence and edition/version context. Group rows by topic if needed, but do not silently omit IDs. Identify MUST blockers separately from SHOULD and MAY gaps.
5. An architectural comparison focused on our deployment constraints. Compare adopting one system, extending one, and combining existing components. Name the orchestration, execution, provider-integration, profile-distribution, and telemetry responsibilities each option would cover.
6. A prioritized recommendation with explicit tradeoffs and open questions that could change it. Separate confirmed facts, inferences, and proposed decisions. Any suggested changes to our requirements must be clearly marked as suggestions.
7. Sources with direct links and a concise list of evidence gaps requiring a later hands-on evaluation. Do not fabricate a completed evaluation.

Use clear English and Markdown headings, tables, and named links. Keep the report decision-focused and substantive. Prefer primary evidence over marketing descriptions and preserve uncertainty where evidence is missing. Do not translate the report into Russian; a separate Russian translation will be prepared afterward.
