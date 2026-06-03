# Deep-research brief: an internal APM package store

| Field | Value |
| --- | --- |
| Date | 2026-05-29 |
| Tool | deep-research (fan-out search, fetch, adversarial verification, synthesis) |
| Run ID | `wf_ab15b1cc-858` |
| Task ID | `w1c7e06vo` |
| Result | [deep-research-report.md](./deep-research-report.md) |
| Russian original | [deep-research-brief.ru.md](./deep-research-brief.ru.md) |

This is the brief sent to deep research, kept verbatim for the record. The report later refined or refuted
some of the "established facts" below — chiefly the byte-compatibility of the artifact across runtimes.
Cross-check against the report's "Refuted claims" section.

## Context and goal

We are designing an internal APM package store (Microsoft APM, `github.com/microsoft/apm`) with two layers:

1. a public GitHub layer for OSS packages, discoverable without access to the corporate network;
1. a corporate layer where JFrog Artifactory exists and some packages live in an internal GitLab.

The goal is an end-to-end demo: a producer publishes a package, and a consumer finds it in the store and
installs it.

Requirements:

- see the list of available packages;
- see a package's composition (number of dependencies, skills, instructions);
- track version releases (a version history is desirable);
- a programmatic API for an AI agent — nice to have, not a demo blocker.

The packages live in different git repositories and are developed by different teams. The demo is prepared
in the public fork `github.com/vlsi/qubership-ai-packages` (a monorepo with packages under
`agent-packages/`: `apm-authoring`, with instructions and a skill; and `go-microservice-dev-kit`, an
umbrella with six transitive cross-repo dependencies on the `feat/agent-packages` branch).

## Established facts (from the APM sources)

Passed in as context, marked "do not re-verify".

- APM has three delivery mechanisms:
  - **git-marketplace**: the `marketplace:` block in `apm.yml` is compiled by `apm pack` into
    `.claude-plugin/marketplace.json` (the Anthropic Claude Code format), plus optionally
    `.agents/plugins/marketplace.json` for Codex; you register it with `apm marketplace add` and install
    with `apm install pkg@mkt`;
  - **HTTP registry**: the `registries:` block plus `apm publish` over the Registry HTTP API; the client
    sits behind the `apm experimental enable registries` flag;
  - **bundle**: `apm pack` builds a self-contained tar for `apm install ./bundle`.
- The Registry HTTP API has exactly three endpoints: `GET /v1/packages/{owner}/{repo}/versions`,
  `GET …/versions/{version}/download`, and `PUT …/versions/{version}`. There is no "list packages"
  endpoint.
- git-marketplace has no version history: each entry carries one resolved `ref` plus a `sha` (there is no
  `versions[]` array).
- The discovery commands (`apm marketplace browse`, the top-level `apm search QUERY@MARKETPLACE`) emit text
  only; they have no `--json` flag.
- A single `marketplace.json` can mix sources from different hosts (GitHub, GitLab, Azure DevOps): the
  `source` discriminator is `github`, `url`, or `git-subdir`. GitLab is first-class (`GITLAB_APM_PAT`);
  Azure DevOps, Gitea, and Bitbucket go through generic git.
- The `microsoft/apm` repository ships no OSS registry server (only test mocks).
- APM uses Artifactory two ways: as a VCS proxy (`PROXY_REGISTRY_URL`, works today, not experimental) and
  as a dedicated registry implementing the Registry HTTP API (`registry-http-api.md` names the audience
  "Artifactory plugins").
- `marketplace.json` does not carry a package's composition — neither primitive counts nor a dependency
  list. Transitive dependencies are not expanded at `apm pack` time (only the package's own `ref` plus
  `sha` is resolved). Transitive resolution happens only on the consumer's `apm install` (in the lockfile,
  `depth: 1` is a direct dependency, `2+` transitive).
- APM reports composition from a package's contents, not from its manifest: `apm view <pkg>` (counts of
  skills, prompts, instructions, hooks), `apm deps list` (columns Prompts, Instructions, Agents, Skills),
  `apm deps tree`, and `apm deps why --json`. For a marketplace entry, `apm view NAME@MARKETPLACE` returns
  only `name`, `version`, `description`, `source`, and `tags`.
- instructions are a first-class APM primitive: `apm install` compiles them into `.github/instructions/`,
  `.github/copilot-instructions.md`, `.cursor/rules/`, and `AGENTS.md`/`CLAUDE.md`. The
  plugin/marketplace.json schema has no `instructions` primitive, so a native `/plugin install` does not
  deploy raw instructions.
- A marketplace is the `marketplace:` block in `apm.yml` plus a committed `.claude-plugin/marketplace.json`
  in any repository; an existing or package repository can be a marketplace itself (single-plugin,
  monorepo-hybrid) — a dedicated repository is not required.

## Research questions

External sources, with links and dates; all current as of 2026.

1. **[Critical]** Can JFrog Artifactory host an endpoint that implements the APM Registry HTTP API
   (`GET`/`PUT /v1/packages/.../versions`, `/download`)? Work it through with step-by-step configuration and
   links to the official JFrog docs: (a) a generic repository plus `apm publish` — does the URL template
   `…/artifactory/api/apm/<repo>` correspond to anything real; (b) an Artifactory user plugin; (c) no
   support, so a sidecar service in front of Artifactory is needed. Separately: configuring Artifactory as a
   VCS remote (the Archive Entry Download API) to front a private GitLab and GitHub (for
   `PROXY_REGISTRY_URL`).
1. Does an OSS server implementing the APM Registry HTTP API exist (Microsoft or community repositories)? If
   not, estimate the effort for a minimal server (three endpoints, RFC 7807, immutable versions, sha256) and
   whether reference conformance tests exist.
1. How to make the corporate packages browsable when there is no catalog endpoint: compare a git-marketplace
   index, the Artifactory browser/AQL, and custom HTML over JSON. Give a recommendation.
1. The public GitHub git-marketplace: how real public APM marketplaces are built —
   `DevExpGbb/zava-agent-config`, `github/awesome-copilot`, `microsoft/apm-sample-package`. How to add
   specific packages: the `agent-packages/` tree in `Netcracker/qubership-ai-packages` on `main`, and the
   package `agent-packages/fiber-server-utils-go-usage` in
   `Netcracker/qubership-core-lib-go-fiber-server-utils` on `feat/agent-packages` — are these full APM
   packages (with `apm.yml`) or skill folders; is the per-primitive path form needed
   (`owner/repo/path/to/primitive`).
1. Topology for multi-team plus two hosts: compare "one corporate aggregator index" against "per-team
   marketplaces plus an aggregator" — selection criteria, auto-updating entries (PR, `apm marketplace
   outdated`, a CI cron, `microsoft/apm-action` mode `release`), and a migration path between the topologies.
   A separate public GitHub index is mandatory.
1. Version tracking: how to be notified of new package versions in a marketplace (Dependabot-style
   approaches, `apm marketplace outdated` in CI). For an Artifactory registry — what `/versions` gives you.
1. Multi-runtime currency (as of 2026): do Cursor, the GitHub Copilot CLI, and VS Code Copilot really
   consume `.claude-plugin/marketplace.json`; what are each one's limits.
1. A recommendation for the fastest guaranteed-working e2e demo (two tracks: GitHub git-marketplace; and
   corporate — git-marketplace plus an Artifactory proxy, or an Artifactory registry), with exact
   `apm marketplace init`/`package add`/`pack`/`add`/`install` commands and what to commit.
1. A composition showcase: how to build a catalog that shows, per package, the number of dependencies and
   primitives (skills, instructions, agents, hooks) when `marketplace.json` does not carry it. Compare the
   approaches: (a) clone and read `apm.yml` plus the `.apm/` tree at catalog-build time; (b) a sandbox
   `apm install` plus parsing the lockfile or `apm deps list`; (c) `apm view`/`apm deps tree`. Is there a
   machine-readable package-composition manifest in APM, or on its roadmap.
1. Transitive dependencies: how a consumer can see a package's full graph from the marketplace before
    installing (or only through install plus the lockfile). Account for MCP dependencies
    (`dependencies.mcp`).
1. instructions behaviour across the real runtimes: which paths (`apm install`, Claude `/plugin install`,
    Cursor add marketplace) deploy file-glob instructions (into `copilot-instructions.md`, `.cursor/rules`,
    `AGENTS.md`) and which do not. Confirm on current versions (2026).
1. Minimum of new repositories: validate the topology "each package repository carries its own
    `marketplace:` block" plus one aggregator in an existing repository. Can `apm marketplace add` point at
    a manifest in a subfolder or a branch, or must it sit in the repository root? Migration from co-located
    to a dedicated aggregator.

## Response format

A structured report on the questions above; for each, a conclusion plus sources with links and dates. At the
end, two recommended architectures (the GitHub layer and the corporate layer via Artifactory) and a
step-by-step demo scenario with commands for the `vlsi/qubership-ai-packages` fork.
