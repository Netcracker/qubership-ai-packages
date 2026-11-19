# Qubership Software Factory

## System concept

In the primary deployment, the GitHub App and its workers run on the same ordinary machine that hosts the application.
The system receives repository events and runs the selected agent workflows on that machine.
Independent workers on separate machines are an optional capability.

Agent profiles are defined through APM. Workflows are configured and versioned independently of the application code
and connected repositories. Agents within one workflow can use different compatible combinations of harnesses
and models. The architecture supports releasing a GitLab application from the same codebase.

## Purpose and product scope

- **F01 · MUST.** The system MUST receive GitHub events through an installed GitHub App and run agent automation to
  process those events.
- **F02 · MUST.** The system architecture MUST support releasing a GitHub App and a GitLab application from one
  codebase, with shared workflow and agent logic behind platform adapters. Both integrations MUST support self-hosting
  in an enterprise environment.

> - The intended use is to apply the system to everyday work and evaluate its usefulness.
> - Existing solutions can be compared against a minimal application contract before choosing a custom implementation.
> - Complex integrations can require clarification, discussion of edge cases, and human involvement.
> - Standardizing how different teams work is not a prerequisite for adoption.
> - Open-source and self-hosted solutions are relevant alternatives. Exclusive dependence on an external SaaS service is
>   unsuitable; a custom implementation is not a goal in itself.

## Agent profiles and workflows

- **F03 · MUST.** The system MUST allow centralized changes to agent workflow configuration without changing application
  code or the code or configuration of connected repositories.
- **F04 · MUST.** The system MUST store and load agent profiles as APM packages. The complete contents of each agent
  profile MUST be defined through APM.
- **F05 · MUST.** The system MUST allow configuration of agent workflows, including participating agents, stage order,
  and repeated cycles. Each agent within a workflow MUST allow any supported harness and compatible model combination,
  independently of the combinations used by other agents.
- **F06 · MUST.** The system MUST support an arbitrary number of configured workflows and allow manual selection of a
  workflow by a human or automatic workflow selection for processing a ticket.
- **F07 · MUST.** The system MUST version workflow definitions and pin a workflow version to each run when it starts. At
  run start, the system MUST save an immutable snapshot of the stage graph, APM profile versions, selected harnesses,
  models, and launch parameters. Execution and retries of that run MUST use the pinned version and saved snapshot.
  Subsequent configuration or profile changes MUST NOT alter a run already in progress. A new assignment in the same
  issue or PR after a run finishes MUST create a new run using the workflow version current at its start.
- **F08 · MUST.** The system MUST allow workflow configuration to define stages that require human review of a plan,
  part of an implementation, or another intermediate result. The system MUST pause the workflow at those stages and
  continue only after approval by an allowlisted participant.
- **F09 · SHOULD.** The system SHOULD allow multiple workflows to be assigned to one repository and executed
  sequentially or in parallel.
- **F10 · SHOULD.** The system SHOULD support persisting the statuses of autonomous workflows in labels on the
  corresponding issues or PRs.

> - Example workflow configuration: development with Pi and Qwen 3.7 through OpenRouter; review with Codex and GPT Sol
>   High; design with Claude Code and Claude.
> - Separate workflows can cover development, bug fixes, and documentation updates.

## Repository connections and events

- **F11 · MUST.** The system MUST allow participant allowlists to be configured. Only allowlisted participants may
  authorize starting or continuing a workflow or approving an action; the system MUST check the participant authorizing
  the action. The system MUST NOT take requests or opinions from comments by participants outside the allowlist into
  account in agent work.
- **F12 · MUST.** The system MUST NOT process PRs from external authors, including agent reviews and test execution for
  those PRs.
- **F13 · SHOULD.** The system SHOULD connect a selected GitHub repository through GitHub App permissions and receive
  its events without adding CI or workflow files to that repository.
- **F14 · MAY.** The system MAY expose a REST API for receiving GitHub events through the GitHub App integration layer
  and launching agent jobs.
- **F15 · MAY.** The system MAY receive GitHub and GitLab webhooks at separate endpoints and adapt their payloads for a
  shared agent job handler.
- **F16 · MAY.** The system MAY start an agent workflow when a PR or MR is created or receives new commits.
- **F17 · MAY.** The system MAY filter GitHub events programmatically before launching an agent so that excluded events
  do not incur a paid model call.

> - Separating event intake from agent job handling allows shared processing logic to remain independent of GitHub,
>   GitLab, or another event provider.
> - Fast reactions to GitHub events are preferable to waiting for the next periodic repository scan.
> - Labels are the preferred way to persist autonomous workflow statuses.
> - Repository onboarding can follow the Renovate model: grant the application access to the repository.
> - An example programmatic filter recognizes a Renovate PR and skips the agent call.

## State, recovery, and data

- **F18 · MUST.** After a restart, the system MUST automatically resume unfinished runs when sufficient data is
  available to restore their state and continue execution.
- **F19 · MAY.** The system MAY store agent run state in a local SQLite database or a cloud database accessible to
  system components.
- **F20 · MAY.** The system MAY obtain issues, PRs, and comments from an existing local GitHub mirror instead of
  implementing its own data retrieval and synchronization.
- **F21 · MAY.** A duplicate-detection agent MAY search a local mirror of GitHub issues and comments for similar issues
  to reduce calls to GitHub Search.

> - Recovering a workflow stage from a GitHub issue after losing local SQLite state is a possible recovery approach.
> - Scaling to hundreds of repositories raises API limit concerns and makes repeated full scans with a personal access
>   token undesirable.
> - GitHub statuses and labels can represent the workflow stage, with local SQLite holding execution details such as
>   attempt counts.
> - A local database can complement GitHub without copying all platform data.
> - A local mirror can use incremental updates after its initial load.
> - git-crawl is a candidate for a local mirror of issues, PRs, and comments. Its availability of labels for final
>   classification and statistics remains an open question.
> - Resetting the attempt count after losing temporary state is a possible recovery behavior.

## Execution, statuses, and results

- **F22 · MUST.** An agent MUST produce a result artifact, and a separate programmatic component MUST publish that
  artifact to GitHub. The model MUST NOT receive a token with publication permissions.
- **F23 · MUST.** Workers MUST cache local repository clones between agent jobs and reuse the prepared working
  environment. For subsequent work, a worker MUST update an existing clone to the required revision instead of cloning
  the repository again.
- **F24 · MUST.** The system MUST support executing agent jobs on workers running on the same machine as the GitHub App.
- **F25 · SHOULD.** The system SHOULD exclude debug logs, internal execution journals, and large amounts of internal
  operational data from comments published to GitHub by agent automation.
- **F26 · SHOULD.** A worker SHOULD give an agent access to the code of multiple related repositories within one job
  that checks their integration.
- **F27 · MAY.** The system MAY report agent job statuses to the corresponding GitHub issue or PR, including starting,
  running, and error states.
- **F28 · MAY.** The system MAY delegate agent jobs to independent workers running on machines separate from the GitHub
  App.

> - Final classification of a PR's outcome after it is merged is a possible automation scenario.
> - A process that exits loses its in-memory state; a long-running process can retain state between events.
> - Compilation, Docker, kind or Kubernetes, and heavy integration tests consume worker resources beyond LLM costs.
> - Infrastructure cost comparisons also include environment preparation, startup, and repository cloning, even when VM
>   costs are not directly visible to the user.
> - An example result artifact identifies a PR and contains a proposed comment for a programmatic component to publish.
> - A repository cache TTL is one possible retention mechanism. Caching reduces repeated downloads and load on GitHub
>   and workers.

## Harnesses, models, billing, and credentials

- **F29 · MUST.** The system MUST provide a default noninteractive harness for running agents with different LLMs and
  support replacing it with another supported harness.
- **F30 · MUST.** The system MUST allow model access through either an API or a subscription, including for personal
  open-source work.
- **F31 · MUST.** The system MUST securely store tokens, passwords, and other credentials for AI services and GitHub. It
  MUST release those secrets only to authorized programmatic components.
- **F32 · MUST.** The system MUST support connecting and running the Claude Code and Codex harnesses for agent jobs.
- **F33 · MUST.** Before launching an agent, the system MUST check compatibility between the selected harness, model,
  and model access method. If the combination is unsupported, the system MUST report an error and MUST NOT launch the
  agent. It MUST NOT automatically substitute the harness or model or switch from a subscription to a paid API.
- **F34 · MAY.** The system MAY route agents' LLM requests through an API router or proxy, including in an enterprise
  environment.

> - Moving a subscription token from a session into GitHub secrets can be inconvenient and risky.
> - Model budgets and review quality are separate considerations when selecting models.
> - Comparisons of value and cost depend on the model, payment method, and evaluation conditions.
> - codex exec is an example of a noninteractive agent launcher.
> - Personal open-source use benefits from the freedom to experiment without depending on a small centrally managed API
>   budget.
> - The mechanism for securely storing AI service and GitHub credentials remains to be selected.
> - Pi and OpenCode are candidates for the default multimodel harness; the choice is not yet confirmed. OpenRouter is an
>   example model provider.

## Agent and human interaction

- **F35 · SHOULD.** The system SHOULD enable agents in different sessions to exchange messages and coordinate joint
  work, including distributing changes and commits among agents.
- **F36 · SHOULD.** When continuing work on a GitHub issue, the system SHOULD use the issue's associated main agent
  session with its accumulated discussion context instead of starting a new session with empty context.
- **F37 · SHOULD.** To control workflow execution, the system SHOULD respond to standardized user actions on a GitHub
  issue or PR, such as adding or removing a label or posting a specific command. A free-text message is not, by itself,
  a workflow control signal.
- **F38 · MAY.** The system MAY run a development workflow for an issue, including planning, code changes, pushing
  changes to a working branch, and creating a PR through the programmatic publication component. Human review and
  approval of transitions MUST occur at the stages defined in that workflow's configuration.

> - Example interaction: the system adds a Need Human label; a person posts a comment and removes the label, after which
>   the workflow can continue.
> - The priority system scenario is issue-based development: discuss the plan, modify the code, and prepare a PR.
> - A chat between sessions or shared context are possible mechanisms for agent communication.
> - Plan review can require an interactive discussion, potentially continuing in a local session.
> - Agent instructions and skills are separate from the launch mechanism. Changing where an agent runs does not improve
>   its instructions by itself.

## Automation scenarios and review quality

- **F39 · SHOULD.** The system SHOULD run agent PR reviews that analyze code and can execute tests for the change under
  review.
- **F40 · SHOULD.** A review agent SHOULD distinguish defects within the PR's scope from incidental findings outside
  that scope and avoid requiring unrelated defects to be fixed in that PR.
- **F41 · MAY.** The system MAY run an agent workflow that automatically merges Renovate dependency update PRs.
- **F42 · MAY.** A bug-fixing agent MAY attempt to reproduce a reported bug before changing code to fix it.
- **F43 · MAY.** The system MAY launch an agent to analyze review comments on a specific PR and prepare responses to
  those comments.
- **F44 · MAY.** A review agent MAY create separate issues for defects outside the scope of the PR under review.
- **F45 · MAY.** A review agent MAY check whether the code's level of abstraction matches the functionality implemented
  by the PR under review.
- **F46 · MAY.** A review agent MAY identify new code in the PR under review that duplicates functionality in the
  standard library or a widely used existing library.
- **F47 · MAY.** The system MAY run a research agent workflow to examine a question from different perspectives and
  compare solutions before implementing its own.
- **F48 · MAY.** The system MAY launch research subagents with different search questions and prompts to examine the
  same question from different perspectives.
- **F49 · MAY.** After finding a bug, a review agent MAY search other similar parts of the codebase for the same class
  of defect.
- **F50 · MAY.** A defect-detection agent MAY use previously fixed bugs and similar fixes as examples when searching for
  new defects, including through embeddings.
- **F51 · MAY.** The system MAY assign each review subagent a distinct persona and analysis approach to obtain different
  perspectives on the same problem.

> - If a bug cannot be reproduced, the agent's prompt and skills determine whether to prepare a fix or ask a human. No
>   single deterministic rule applies to all workflows.
> - Agent profiles and techniques for finding similar bugs benefit from concrete usage examples.
> - A research process can include initial information gathering, a second pass over findings, independent review, and
>   revisions based on feedback.
> - Techniques for finding similar bugs can be evaluated through experiments with concrete examples.
> - Delivering language-specific skills for file review without filling the context with irrelevant Java or Go
>   instructions remains an open question.
> - Comparing existing solutions before proposing a custom implementation helps avoid premature implementation
>   decisions.
> - Research scenarios can extend beyond a single repository.

## Telemetry, statistics, and costs

- **F52 · MUST.** Every launched agent MUST send telemetry through integration with qubership-ai-agent-telemetry or
  through its harness's native telemetry.
- **F53 · MUST.** The system MUST show actual API expenses and, separately, estimated subscription run costs in dollars
  for each agent run and its associated PR. Estimated costs MUST be calculated from model usage and current provider
  prices through integration with a tool that tracks usage and updated pricing.
- **F54 · SHOULD.** The system SHOULD store actual API expenses and estimated subscription run costs as separate
  structured numeric values associated with the run and its PR, independently of GitHub labels.

> - ccusage is an example tool for estimating subscription run costs using model prices.
> - GitHub events, final classification results, and labels from a local mirror are possible inputs for PR and agent
>   activity statistics.
> - A mirror's SQLite database is a possible statistics data source.
> - The application database is a possible store for numeric cost data.
> - Evaluation can account for practical value, LLM costs, and execution resources.

## Workflow decision logic

- **F55 · SHOULD.** The system SHOULD support integrating decision models or engines to evaluate configured workflow
  branches, including whether to accept a ticket for processing, which status to assign, and whether human intervention
  is required. Each such decision SHOULD use an explicitly documented and tested definition of its inputs, permitted
  outcomes, and reason codes. A decision requiring human intervention SHOULD produce a `Need Human` outcome with a
  specific reason code and a human-readable explanation.
