# Open SWE: adoption and foundation assessment

## Recommendation

Open SWE deserves a focused technical evaluation as a possible foundation for Qubership Software Factory.
The public evidence supports a real, actively developed system used by its creators. It does not yet support
depending on upstream as a stable, community-supported platform.

The practical adoption model is a maintained fork with explicit responsibility for deployment, security boundaries,
and upgrades. Whether that fork is cheaper to maintain than adapting agent-flow remains unproven.
The strongest reasons for caution are the closed external contribution policy, runtime dependencies, rapid change,
and gaps against our mandatory execution and publication contracts.

| Question | Assessment |
| --- | --- |
| Is this a substantial project worth evaluating? | Yes. Working integration code, active maintenance, releases, and concrete internal-use evidence justify evaluation. |
| Do recognizable people and publications discuss it? | Yes. Their roles range from builder and infrastructure partner to independent commentator. |
| Is independent production adoption well established? | Not by the reviewed evidence. The strongest operational account comes from LangChain. |
| Can we assume simple, fully independent deployment on our machine? | No. Backend hosting, agent runtime, sandboxing, and service entitlements need separate verification. |
| Should we select it immediately as the base? | No. Keep it shortlisted and resolve the decision gates below. |

## Evidence and version boundaries

The August 2025 launch and March 2026 framework release describe different generations. Old articles about
Manager/Planner/Programmer agents and Daytona cannot establish the behavior of the inspected Python/MDA version.
Even the March announcement describes sandbox recreation differently from the pinned documentation.
[2025 coverage](https://www.infoq.com/news/2025/08/langchain-open-swe/),
[2026 announcement](https://www.langchain.com/blog/open-swe-an-open-source-framework-for-internal-coding-agents),
[pinned runtime documentation](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/mda/README.md)
.

## Development activity and maintenance

The repository snapshot contains 11,135 stars, 1,312 forks, and 48 subscribers. Stars and forks demonstrate attention
and copying interest; they do not identify active deployments or independent maintainers. The contributor endpoint
returns 68 accounts across the repository's history, including automation. None of these counts is a user count.
[Repository API snapshot](https://api.github.com/repos/langchain-ai/open-swe) ,
[contributor snapshot](https://api.github.com/repos/langchain-ai/open-swe/contributors?per_page=100) .

Recent development is substantial and concentrated:

| Indicator | Observed value |
| --- | --- |
| Merged PRs dated September 29 through October 29, 2026, inclusive | 943 distinct results, all search pages retrieved |
| Author accounts in that window | 27, including affiliated accounts and automation |
| Ramon Nogueira / Mason Daugherty / Johannes du Plessis | 375 / 258 / 117 merged PRs |
| Top three author share | 79.5%; their profiles identify LangChain affiliation |
| PR bodies explicitly disclosing Open SWE generation | 625 of 943, or 66.3% |
| Top four contributor-account share across API contribution counts | 74.3%, a concentration signal rather than a bus factor |

The final date was still in progress; this is an inclusive calendar-date query, not a completed rolling 30-day period.
The first 100 commit results cover only October 27 through 29 and are not a monthly total.
The inspected head identifies an Open SWE-generated change with human and bot attribution.
Activity shows a maintained feedback loop without measuring independent human engineering capacity.
[merged-PR query](https://github.com/langchain-ai/open-swe/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-09-29..2026-10-29),
[inspected head](https://github.com/langchain-ai/open-swe/commit/daf121a9b055f340a29e072596570a8779588964).

The decisive governance finding is that the pinned README says the project is not accepting issues or external
contributions. The API also reports `has_issues: false` and `has_discussions: false`.
Open PRs and historical contributions do not override that published policy. A downstream team should plan to fix
its own blockers and carry changes unless a support relationship is established.
[Pinned README](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/README.md),
[repository settings snapshot](https://api.github.com/repos/langchain-ai/open-swe).

Historical contributions beyond the three dominant recent authors are documented. Dylan Boudro's PR #502 received a
review after about 2 hours 50 minutes
and merged after about 20 hours 49 minutes in July 2025. Palash Shah's PR #801 remained unmerged from August 2025
until March 2026, when it was closed because the project had been rewritten. These illustrate accepted contributions
and architectural churn; two examples cannot establish a representative response-time average.
The contributors' employment affiliations when those PRs were opened were not established.
The 165 open repository items in the snapshot match 165 open PRs and must not be reported as 165 bug reports.
[PR #502](https://github.com/langchain-ai/open-swe/pull/502),
[PR #801](https://github.com/langchain-ai/open-swe/pull/801).

Release artifacts are another positive signal, but their scope matters. A desktop/CLI release does not establish a
stable backend API, database migration policy, or long-term support branch. Those contracts must be checked separately.
[Release evidence](https://github.com/langchain-ai/open-swe/releases/tag/desktop-v0.3.10) ,
[release history](https://github.com/langchain-ai/open-swe/releases) .

## Notable people: what their participation actually shows

| Person | Verified involvement | Weight for an adoption decision |
| --- | --- | --- |
| Brace Sproul | Builder, launch advocate, and technical presenter; repository history also records contributions | Direct project participation and access to technical explanations; first-party evidence |
| Harrison Chase | LangChain founder; seven authored PR search results, including merged #2468 | Direct sponsor-leadership participation, rather than independent adoption |
| Christian Bromann | WebdriverIO head and LangChain engineer; eight contributor-API contributions and seven merged PRs in the measured window | Experienced open-source developer participation, with a sponsor affiliation |
| Ivan Burazin | Daytona CEO/co-founder publicly supported the launch using Daytona | Infrastructure-partner interest with a commercial relationship |
| Simon Willison | Linked Open SWE as an example of asynchronous coding agents on August 6, 2025 | Independent recognition; no hands-on endorsement or deployment claim |
| Pamela Fox | Shared technical takeaways from Sproul's Ambient Agents presentation | External developer interest; no claim that Microsoft operates Open SWE |
| Mitch Ashley | Futurum analyst quoted in DevOps.com's March 2026 article | Architectural commentary; the publisher belongs to the same media group |
| Tyler Folkman | Published skeptical commentary about the 2025 system | Evidence of criticism; numerical comparisons lack a reproducible benchmark in the retrieved post |

Sources:
[Sproul's launch post](https://www.linkedin.com/posts/brace-s_announcing-langchain-labs-newest-product-activity-7358908515479949312-K9YC)
,
[Chase's PR #2468](https://github.com/langchain-ai/open-swe/pull/2468),
[Bromann's profile](https://github.com/christian-bromann),
[Bromann's SDK integration PR](https://github.com/langchain-ai/open-swe/pull/4735),
[Burazin's partnership post](https://www.linkedin.com/posts/ivanburazin_so-happy-this-is-finally-live-open-swe-powered-activity-7359407332281282562-fpl5)
,
[Burazin's role](https://www.daytona.io/dotfiles/author/ivan-burazin),
[Willison's original post](https://simonwillison.net/2025/aug/6/asynchronous-coding-agents/),
[Fox's recap](https://www.linkedin.com/posts/pamela-s-fox_langchain-langgraph-activity-7353665925545410560-sIfP),
[Microsoft biography](https://developer.microsoft.com/en-us/advocates/pamela-fox),
[Ashley quotation](https://devops.com/open-swe-captures-the-architecture-that-stripe-coinbase-and-ramp-built-independently-for-internal-coding-agents)
,
[Folkman's commentary](https://www.linkedin.com/posts/tylerfolkman_langchain-dropped-open-swe-another-autonomous-activity-7369747588163510273-u46n)
.

This evidence supports visibility among technical audiences. It does not establish a broad set of influential
independent maintainers or organizations committed to supporting the code. A mention, partnership, code contribution,
and deployment are separate kinds of involvement.

## Media coverage and independent scrutiny

| Publication | Date | Substance | Evidence limit |
| --- | --- | --- | --- |
| InfoQ, Robert Krzaczyński | August 13, 2025 | Dedicated report on the original architecture and interaction model; includes critical community reaction | Launch reporting, not a current-version test |
| DevOps.com, Tom Smith | March 19, 2026 | Dedicated explanation of the framework release and reusable internal-agent patterns | Architecture analysis, not measured deployment reliability |
| Simon Willison's weblog | August 6, 2025 | Places Open SWE in the asynchronous coding-agent category | Brief link commentary |
| WorldofAI | Video identified; exact publication date not independently confirmed | Dedicated Open SWE video | Transcript and demonstration were not verified |

Sources: [InfoQ](https://www.infoq.com/news/2025/08/langchain-open-swe/),
[DevOps.com](https://devops.com/open-swe-captures-the-architecture-that-stripe-coinbase-and-ramp-built-independently-for-internal-coding-agents)
,
[Willison](https://simonwillison.net/2025/aug/6/asynchronous-coding-agents/),
[WorldofAI video](https://www.youtube.com/watch?v=zgn3HPRej_k).

The reviewed searches did not establish dedicated TechCrunch or VentureBeat coverage. Translations, directory listings,
SEO summaries, and repeated launch descriptions should not be counted as independent investigations. DevOps.com's
Futurum analyst quotation and the article are one connected source, rather than two independent endorsements.

Hacker News discussions raise useful questions about permissions, dependencies, and ecosystem quality, but largely
concern the 2025 generation. Their claims require retesting against the chosen commit.
[Launch discussion](https://news.ycombinator.com/item?id=44838733).

## Adoption evidence

LangChain's October 1, 2026 article by Sydney Runkle and Eugene Yurtsev is stronger evidence than a launch
demonstration.
It describes engineers using Open SWE through Slack and a web UI, trace-based task analysis, and an A/B experiment
covering 973 threads. The authors report median costs of $0.94 for routed threads and $2.61 for the control.
Merged-PR rates were 29.2% and 27.3%, with p = 0.49.
[Internal-use study](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness).

The study supports sustained first-party use and measurement. The lack of a statistically significant difference
does not prove equivalent quality. Thread traffic includes tasks that do not require a PR, so these percentages are
not a universal task-success rate. The cost result is specific to that experiment and is not our expected operating
cost.

The reviewed sources did not establish a named independent organization with documented deployment duration,
failure handling, upgrade experience, and outcomes. This remains an evidence gap, not a finding that no customers exist.
Stripe Minions, Ramp Inspect, and Coinbase Cloudbot are independently built architectural references in LangChain's
announcement. They are not established Open SWE deployments.
[Architecture comparison](https://www.langchain.com/blog/open-swe-an-open-source-framework-for-internal-coding-agents).

## Licensing, hosting, and dependence on the sponsor

Open SWE's own code carries the MIT license. Its README excludes `vendor/` from that repository-level grant.
The inspected vendored Managed Deep Agents SDK and `langchain-quickjs` each contain their own MIT license text.
Calling the whole vendor tree unlicensed would therefore be inaccurate. Preserve upstream notices and verify the
origin and scope of each included component before redistribution.
[Root license](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/LICENSE),
[vendor policy](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/vendor/README.md)
,
[SDK license](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/vendor/managed-deepagents-sdk/LICENSE)
,
[QuickJS package license](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/vendor/langchain-quickjs/LICENSE)
.

Code permissions and service access are separate. The installation documentation requires a license key for the
standalone LangGraph Agent Server, with PostgreSQL and Redis. The pinned runtime documentation also requires
`MDA_RUNTIME_URL`: new agent work is delegated to the Managed Deep Agents deployment, and the backend refuses startup
without its configuration. A Docker backend alone does not establish an independent, same-machine execution system.
[Installation contract](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/docs/INSTALLATION.md)
,
[MDA routing](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/mda/README.md).

The concrete risk is coupling to the sponsor's runtime and evolving APIs, rather than inability to inspect the source.
The project carries local changes to vendored SDK code. A fork may inherit coordination work across the application,
runtime, SDK, and deployment services. Written terms, supported deployment combinations, and an exit path matter
more here than additional social endorsements.
[Vendoring process](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/vendor/README.md)
.

## Fit with our mandatory requirements

| Requirement | Adoption question |
| --- | --- |
| F01: GitHub App intake | A direct strength: an App, webhook integration, and GitHub delivery already exist. |
| F02: shared GitHub/GitLab architecture | Demonstrate the provider boundary and scope the GitLab adapter; GitHub support alone is insufficient. |
| F03-F08: configurable workflows, APM, pinned runs, approvals | Distinguish model/tool customization from our configurable stage graphs, complete APM profiles, immutable run snapshots, and allowlisted checkpoints. |
| F22: separate publication component | Prove that an agent cannot obtain publication capability through shell, API tools, or a GitHub proxy. Hiding a raw token is insufficient. |
| F24: same-machine execution | Demonstrate the complete agent runtime on our host, not only a locally hosted dashboard/backend. |
| F29-F33: interchangeable harnesses and access methods | Model-provider selection does not establish Claude Code/Codex harness support, subscription access, or prelaunch compatibility enforcement. |
| F52-F54: telemetry and cost | Existing tracing is useful; verify every agent's coverage and separate actual API expense from subscription cost estimates linked to run/PR. |

The documented GitHub trust model grants coding sandboxes installation-wide App access in normal team workflows.
Workspace routing is not a credential boundary. That is a concrete mismatch with our F22 contract unless the execution
and publication paths are changed. Prompt instructions alone do not enforce the required boundary.
[GitHub trust model](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/docs/INSTALLATION.md#repository-trust-model)
.

CI definitions, automated tests, and published artifacts are favorable engineering signals. They do not establish
recovery correctness, containment, or enterprise readiness. The saved snapshot for the pinned SHA had four successful
workflow runs, Agent CI in progress, and another preview run pending. This is not an all-green CI result.
[Agent CI run](https://github.com/langchain-ai/open-swe/actions/runs/40900573785).

A third-party SafetyCard assessment also identifies
permission and approval concerns, but it is a static review of an older commit; its score is not accepted as an audit
result here.
[CI definition](https://github.com/langchain-ai/open-swe/blob/daf121a9b055f340a29e072596570a8779588964/.github/workflows/ci.yml)
,
[external static assessment](https://safetycard.dev/github.com/langchain-ai/open-swe).

## Conditions for selecting Open SWE

1. Establish a deployable baseline: pin a commit, document required services and entitlements, and run the entire
   GitHub issue-to-PR path with the execution placement we require.
2. Establish our authority boundary: an allowlisted trigger, exclusion of external PRs, artifact-only agent output,
   and a separate publisher. Test alternate write paths, not just the normal PR tool.
3. Demonstrate our extension points: APM profiles, one configurable multistage workflow, run snapshots, and the required
   Claude Code/Codex and API/subscription combinations. Record the actual changes needed.
4. Test restart, cancellation, retries, and configuration changes during an active run. Verify preserved work and
   absence of duplicate publication.
5. Establish maintenance ownership: identify an upstream contact or support arrangement, review API/migration policy,
   and measure the fork changes we must carry across an upstream update.
6. Seek independent operating references, or explicitly accept that our own evaluation supplies the missing evidence.

Select Open SWE if those checks show that retaining its integrations and user flows saves more maintenance than its
runtime and policy adaptations add. If they require replacing most execution and control logic, reuse selected
components and patterns while comparing another controller. The evidence does not justify a final build-versus-fork
decision or an engineering-duration estimate yet.

## Remaining unknowns

- A supported, fully independent production deployment matching our host and service constraints.
- Upstream support expectations while external issues and contributions are not accepted.
- Independent deployment outcomes, upgrade burden, and long-term compatibility commitments.
- Measured adaptation effort for our workflow, harness, authorization, and publication contracts.
