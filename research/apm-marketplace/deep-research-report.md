# Deep-research report: an internal APM package store

| Field | Value |
| --- | --- |
| Date | 2026-05-29 |
| Brief | [deep-research-brief.md](./deep-research-brief.md) |
| Russian original | [deep-research-report.ru.md](./deep-research-report.ru.md) |
| APM version checked | 0.16.0 (`ec771e57`) |
| Run | 5 angles, 25 sources, 115 claims extracted, 25 verified |
| Verification result | 19 confirmed, 6 refuted; 15 findings after deduplication |
| Voting | adversarial, 3 votes per claim (2 of 3 needed to refute) |
| Cost | 107 agents, ~3.7M subagent tokens, ~21 min |

Source quality is high: almost every finding rests on primary sources (the `microsoft/apm` docs and code,
the official `docs.jfrog.com`, live GitHub manifests). Blogs are used only as corroboration.

## Executive summary

Both layers of the store are buildable with APM's stock mechanisms in 2026, but with one structural limit:
neither git-marketplace nor the Registry HTTP API has a catalog endpoint, and neither carries a package's
composition (primitive counts, dependency graph).

The public GitHub layer is built on git-marketplace (the `marketplace:` block in `apm.yml` compiles into
`.claude-plugin/marketplace.json`, byte-compatible with Anthropic; `source: github` supports a `repo` plus
`path` plus a pinned `ref`) — confirmed by real public manifests (`github/awesome-copilot`).

The corporate layer: Artifactory is officially named a target platform both for the VCS proxy
(`PROXY_REGISTRY_URL` over the Archive Entry Download API — GA, not experimental) and as a backend for the
Registry HTTP API. But you have to implement the API yourself, through a user plugin or a sidecar: JFrog has
no native APM format, and JFrog itself recommends migrating user plugins to Workers. No ready-made OSS APM
registry server exists; the registry is exactly three endpoints (`versions`/`download`/`PUT`), with
immutable versions via `409`, and reference test fixtures are provided.

No stock artifact returns the composition showcase or the version history — you build those with a separate
pipeline (clone plus reading `apm.yml`/`.apm`, or a sandbox install plus parsing the lockfile/`apm deps`),
the way the `awesome-copilot.github.com` catalog does when it shows "assets/files" counts.

## Synthesis, cross-checked against the demo

This section reconciles the research findings with what we verified live on the fork
`vlsi/qubership-ai-packages` (the demo artifacts are in `/tmp/qubership-demo` and `/tmp/consumer`).

### Corporate layer (Artifactory)

- **JFrog has no native "apm" repository type.** The URL `…/artifactory/api/apm/<repo>` from the APM docs is
  a named example (the base URL is "vendor-defined"), not a JFrog endpoint. You must implement the three
  Registry HTTP API endpoints yourself.
- Artifactory's generic building blocks are compatible: Deploy Artifact (`PUT {repoKey}/{path}`) covers
  `PUT …/versions/{v}`, and Archive Entry Download (`GET {repoKey}/{archive}!/{entry}`) covers the download.
  But `GET …/versions` with the right JSON is a code layer: a user plugin, a JFrog Worker, or a sidecar.
  - **User plugin** — JFrog recommends migrating to Workers; and it is not proven that a user plugin can
    serve an arbitrary `GET …/versions` (an open question).
  - **JFrog Worker (HTTP-triggered)** — the "right" path, but it needs an Enterprise X / Enterprise+
    licence.
  - **Sidecar service in front of Artifactory** — the most predictable option. No ready OSS server exists; a
    minimal server is three endpoints plus RFC 7807 plus sha256 plus immutable-`409`.
- **Works today, with no flags and no server of your own:** Artifactory as a VCS proxy
  (`PROXY_REGISTRY_URL`, GA) transparently fronts both GitHub and a private GitLab (the stock Remote VCS
  Repository, Git Provider GitLab). Limitation: nested GitLab subgroups give a two-level path.

Conclusion: for a quick result, use git-marketplace (discovery) plus the Artifactory VCS proxy (download),
both GA. Take the "Artifactory as an APM registry" road (version history via `/versions` plus REST) only if
the API or the history becomes a hard requirement: it needs code of your own and `apm experimental enable
registries` on the consumer.

### Public GitHub layer

- `source: github` is first-class and supports a subpath (`repo` plus `path` plus a pinned `ref`). The live
  `github/awesome-copilot` manifest (86 plugins) uses both forms: a shorthand string under
  `metadata.pluginRoot`, and an object `{source: github, repo, path, ref: <sha>}`.
- The composition showcase has a working reference: `awesome-copilot.github.com/skills/` — a browsable,
  sortable catalog (349 skills, assets/files counts) built by a separate build pipeline over a manifest that
  does not carry composition. It is a direct model for "HTML over JSON": compute the composition yourself
  (clone plus reading `apm.yml`/`.apm`, or a sandbox `apm install` plus `apm deps list`/`tree`).

### What the demo proved beyond the research

The research left these open; the local run confirmed them:

- **Instructions via `apm install`** (question 11): deployed into
  `.github/instructions/apm-authoring.instructions.md`; the skill landed in `.claude/`, `.agents/`, and
  `.windsurf/`.
- **The fork's transitive graph**: `go-microservice-dev-kit` resolved six cross-repo dependencies from the
  `feat/agent-packages` branch, and `apm deps tree` showed the graph with per-node composition. The research
  checked only upstream `main`.

### Corrections to earlier conclusions

- **Byte-compatibility across all runtimes is not confirmed.** The claim "`apm pack` does exactly one
  transform and the artifact is byte-compatible for Claude Code, Copilot CLI, and APM" was refuted (0-3).
  The format is Anthropic-compatible, and Copilot uses the same `.github/plugin/marketplace.json`, but
  whether Cursor, the Copilot CLI, and VS Code consume `.claude-plugin/marketplace.json` on current versions
  is not independently confirmed (question 7 stays open).
- **Fixed Artifactory VCS URL templates** (`downloadBranch`/`downloadTag`, `/api/vcs/tags`) are not
  confirmed (1-2): when configuring the proxy, check against your live Artifactory version.

### Two recommended architectures

| | Public GitHub layer | Corporate layer |
| --- | --- | --- |
| Mechanism | git-marketplace (aggregator or monorepo-hybrid) | git-marketplace (GitHub plus GitLab mix) plus the Artifactory VCS proxy |
| Discovery and listing | `apm marketplace browse`/`search` plus an HTML catalog | same |
| Install | `apm install pkg@mkt` (no flags) | same; downloads go through Artifactory |
| Version history | git tags plus `apm marketplace outdated` in CI | same; for a native `/versions`, a separate sidecar registry plus the experimental flag |
| Composition | pipeline: clone plus `apm deps`/`.apm` → HTML | same |
| Readiness | works today | works today (the proxy is GA) |

## Confirmed findings

15 findings after deduplication; the wording follows the verification protocol.

1. **Artifactory as a target registry platform** (high, 3-0). JFrog is officially named a target platform
   for a private APM registry implementing the Registry HTTP API; the documented URL
   `…/artifactory/api/apm/<repo>` is a named example (a vendor-defined base URL), not a normative template
   and not a native JFrog endpoint. Sources:
   [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md),
   [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

1. **Three endpoints, no catalog** (high, 3-0). The Registry HTTP API has exactly three endpoints
   (`GET …/versions`, `GET …/versions/{v}/download`, `PUT …/versions/{v}`); there is structurally no catalog
   endpoint — every path is scoped under `{owner}/{repo}`. This blocks a browsable storefront directly over
   the registry. The reference client `src/apm_cli/deps/registry/client.py` has exactly
   `list_versions`/`download_archive`/`publish_version`. Source:
   [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

1. **The `apm publish` contract** (high, 3-0). `apm publish` builds a flat `tar.gz` (`apm.yml` and `.apm/`
   at the root) and uploads it via `PUT /v1/packages/{owner}/{repo}/versions/{version}`; `apm.yml` must
   declare `version:`; versions are immutable — republishing the same version returns `409 Conflict`.
   Sources:
   [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md),
   [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

1. **JFrog recommends Workers over user plugins** (high, 3-0). The `jfrog/artifactory-user-plugins` README:
   "JFrog Workers is the recommended cloud-native solution… Consider migrating." Workers run over REST (an
   HTTP-triggered Worker) but need an Enterprise X/Enterprise+ licence (Pro X with Artifactory 7.94). User
   plugins are not formally deprecated. Sources:
   [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins),
   [docs.jfrog.com](https://docs.jfrog.com/).

1. **No OSS registry server** (high, 3-0). `microsoft/apm` ships no ready OSS server implementing the APM
   Registry HTTP API (only the client and test mocks); the spec names the audience "Server implementers
   (Artifactory plugins, Nexus formats, OSS reference servers)" as prospective. The spec is self-contained
   ("build a conformant registry from this doc alone") and ships reference test fixtures (§9). Source:
   [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

1. **`PROXY_REGISTRY_URL` is GA** (high, 3-0, with one related claim at 2-1). Not experimental: it rewrites
   every GitHub-hosted dependency download to the Artifactory Archive Entry Download API, transparently
   fronting the upstream git host (GitHub, GitLab). `ARTIFACTORY_BASE_URL` is a deprecated alias. Coverage:
   installing GitHub deps — yes; Azure DevOps, MCP, policy-fetch — no. Sources:
   [registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md),
   [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload).

1. **Fronting GitLab via a Remote VCS Repository** (high, 3-0). JFrog provides a stock (GA) Remote VCS
   Repository: type VCS, Git Provider GitLab, URL `https://gitlab.com/`. This is exactly what
   `registry-proxy.md` prescribes. Limitation: nested subgroups (`group/subgroup/project`) give a two-level
   path. Sources:
   [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages),
   [registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md).

1. **The Archive Entry Download API** (high, 3-0). `GET {jfrog_url}/artifactory/{repoKey}/{archivePath}!/{entryPath}`
   (no `/api/` in the path), where `!` separates the archive name from the entry path; it returns a single
   file from inside a stored archive. For a whole archive, there is a separate endpoint, Retrieve
   Folder/Repository Archive (Pro-only). Source:
   [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload).

1. **The Deploy Artifact REST API** (high, 3-0). A single `PUT` to an arbitrary `repoKey` plus path under
   `/artifactory/`, with the content as the body, and no package-type-specific endpoint. A generic
   repository plus a sidecar/Worker can accept a `PUT` at any path — technically compatible with the `PUT`
   part of the APM Registry API. But `GET …/versions` with the right JSON does not come for free — it needs
   a code layer. Sources:
   [deploy-artifact](https://jfrog.com/help/r/jfrog-rest-apis/deploy-artifact),
   [deployartifact](https://docs.jfrog.com/artifactory/reference/deployartifact).

1. **A GitHub source with a subpath** (high, 3-0). `source: github` is first-class and supports a subpath
    (`repo` plus `path` plus a pinned `ref`). The `github/awesome-copilot` manifest (86 plugins): 67
    shorthand strings under `metadata.pluginRoot`, and 19 objects `{source: github, repo, path, ref: 40-char
    sha}` (13 with `path`). `path` points at the plugin-root directory, not at a single primitive file.
    Sources:
    [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json),
    [microsoft/apm](https://github.com/microsoft/apm).

1. **No version history in git-marketplace** (high, 3-0). Each entry carries one resolved `ref` (the highest
    tag matching the range at build time) plus a `sha` plus one `version` string; there is no `versions[]`
    array. Publishing a new version means re-running `apm pack` plus re-tagging. Version tracking is done by
    external means (a CI cron, `apm marketplace outdated`, Dependabot-style approaches). The registry API's
    `/versions` returns a version list only for the registry layer. Sources:
    [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md),
    [claude-code-marketplace.schema.json](https://github.com/microsoft/apm/blob/main/tests/fixtures/schemas/claude-code-marketplace.schema.json).

1. **The composition showcase is built by a pipeline** (high, 3-0). The real public catalog
    `awesome-copilot.github.com/skills/` is browsable and sortable (349 skills, sorts by Name A-Z and
    Recently Updated) and shows per-skill counts of "N assets, M files", computed by a separate build
    pipeline (`parseSkillMetadata` recursively lists references/assets/scripts). The counts are file-level,
    not APM primitive-level. For an APM showcase, build the composition with a pipeline: (a) clone plus
    reading `apm.yml`/`.apm`; (b) a sandbox `apm install` plus parsing the lockfile/`apm deps list`; (c)
    `apm view`/`apm deps tree`. Sources:
    [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/),
    [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json).

1. **Host-agnostic install** (high, 3-0). APM installs from GitHub, GitLab, Bitbucket, Azure DevOps, GitHub
    Enterprise, Gitea, Gogs, and any git host — which supports a two-layer topology from a single
    `marketplace.json`. Nuance: the github family, GitLab, and Azure DevOps have dedicated backends (cheap
    commit-resolve); Bitbucket, Gitea, and Gogs go through `GenericGitBackend` (best-effort, no cheap
    commit-resolve). Sources:
    [microsoft/apm](https://github.com/microsoft/apm),
    [README](https://raw.githubusercontent.com/microsoft/apm/main/README.md).

1. **The registries client sits behind an experimental flag** (high, 3-0). Enabled with `apm experimental
    enable registries`, checked with `apm experimental list`, rolled back with `apm experimental reset
    registries`. It gates parsing of the `registries:` block, the registry resolver, and the `registry.*`
    keys. The corporate road via the Registry HTTP API needs the flag on the consumer; git-marketplace and
    `PROXY_REGISTRY_URL` do not. Source:
    [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md).

1. **The upstream Netcracker composition** (high, 3-0). `Netcracker/qubership-ai-packages` (`main`) is a
    monorepo with six package folders under `agent-packages/`: `apm-authoring`, `english-developer-style`,
    `french-developer-style`, `go-microservice-dev-kit`, `markdown-line-length-120`,
    `russian-developer-style`. Nuance: the fork's `feat/agent-packages` branch differs from `main`, and its
    composition is checked separately (in our demo the fork held `apm-authoring` and
    `go-microservice-dev-kit`). Source:
    [Netcracker/qubership-ai-packages](https://github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages).

## Refuted claims

These matter for decisions: the wordings below did not survive the adversarial vote.

1. **"`apm pack` does exactly one transform (`packages`→`plugins`); the artifact is byte-compatible for
   Claude Code, Copilot CLI, and APM"** — refuted (0-3). Specifically, there is no confidence in
   byte-compatibility across all three runtimes; treat it with care. Source:
   [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md).
1. **"APM treats instructions, skills, prompts, agents, hooks, plugins, and MCP as first-class primitives in
   a single manifest, for showing composition"** — refuted (0-3) as worded. instructions are a first-class
   APM primitive, but the plugin/marketplace.json schema has no `instructions` primitive; a native
   `/plugin install` does not deploy raw instructions. Critical for question 11. Source:
   [microsoft/apm](https://github.com/microsoft/apm).
1. **Fixed Artifactory VCS URL templates** (`downloadBranch`/`downloadTag`, `/api/vcs/tags`,
   `/api/vcs/branches`) — not confirmed (1-2). When designing the VCS proxy, check against your live
   Artifactory version. Source:
   [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages).
1. **"User plugins only offer `POST …/api/plugins/execute/{name}`"** — refuted (0-3). A user plugin can
   potentially serve arbitrary REST paths, but there is no positive proof that it serves the needed
   `GET …/versions`. Source:
   [executePluginCode](https://docs.jfrog.com/integrations/reference/executePluginCode).
1. **"The user-plugins sample repository has no template for a custom REST endpoint"** — refuted (0-3).
   Source: [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins).
1. **"No plugin entry carries composition metadata"** — 1-2 (the stronger wording did not pass, because some
   entries carry a minimum of fields), but operationally composition is absent from the manifest. Source:
   [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json).

## Open questions

1. **Question 7 (multi-runtime, 2026).** Do Cursor, the GitHub Copilot CLI, and VS Code Copilot consume
   `.claude-plugin/marketplace.json` on current versions, and what are the limits? There is no direct
   confirmation among the surviving claims; the byte-compatibility claim was refuted. This needs a separate
   check against the runtimes' live docs.
1. **Question 11 (instructions behaviour).** Which paths deploy file-glob instructions into
   `.github/copilot-instructions.md`/`.cursor/rules`/`AGENTS.md`, and which do not — on current versions.
   Partly closed by our demo (`apm install` deploys into `.github/instructions/`).
1. **Implementing the Registry HTTP API on Artifactory.** Is a user plugin enough to serve the three REST
   paths (`GET`/`PUT` with arbitrary paths and `409`/RFC 7807 codes), or is a sidecar/HTTP-triggered Worker
   needed?
1. **The fork's `feat/agent-packages` branch.** Partly closed by our demo: `go-microservice-dev-kit`
   resolved six transitive cross-repo dependencies (`apm deps tree`), and the lockfile records `depth 2+`.
1. **The effort for a minimal OSS registry server.** The size of the conformance suite and whether a ready
   test runner exists for checking a third-party server are not quantified.

## Verification scope and caveats

- The report synthesises 19 claims that passed the adversarial vote; no new independent checks were made at
  synthesis time. Some claims about APM mechanics were given as "established facts, do not re-verify".
- Time sensitivity: everything is current as of 2026, `microsoft/apm` at HEAD v0.16.0. registries is behind
  an experimental flag and the contract may change. The bundled Claude Code marketplace schema is dated
  2026-04-23. The `awesome-copilot` catalog was indexed 27 May 2026, and the "349 skills" count drifts.
  JFrog Workers need an Enterprise X/Enterprise+ licence (Pro X with Artifactory 7.94) — check against your
  specific installation.
- Source quality is high: 14 findings at 3-0, one related at 2-1 (the "every package download" wording).

## Sources

| URL | Quality | Angle | Claims |
| --- | --- | --- | --- |
| [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md) | primary | mechanics | 5 |
| [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md) | primary | mechanics | 5 |
| [microsoft/apm](https://github.com/microsoft/apm) | primary | mechanics | 5 |
| [guides/registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md) | primary | mechanics | 5 |
| [enterprise/registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md) | primary | mechanics | 5 |
| [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages) | primary | Artifactory | 5 |
| [executePluginCode](https://docs.jfrog.com/integrations/reference/executePluginCode) | primary | Artifactory | 4 |
| [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins) | primary | Artifactory | 5 |
| [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload) | primary | Artifactory | 5 |
| [deploy-artifact](https://jfrog.com/help/r/jfrog-rest-apis/deploy-artifact) | primary | Artifactory | 5 |
| [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json) | primary | ecosystem | 5 |
| [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/) | primary | ecosystem | 5 |
| [Netcracker/qubership-ai-packages](https://github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages) | primary | ecosystem | 5 |
| [VS Code: agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins) | primary | runtimes | 5 |
| [GitHub Copilot CLI plugins](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins) | primary | runtimes | 4 |
| [VS Code: custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) | primary | runtimes | 4 |
| [Cursor: plugins](https://cursor.com/docs/plugins) | primary | runtimes | 5 |
| [microsoft/apm#1134](https://github.com/microsoft/apm/issues/1134) | primary | versions and topology | 5 |
| [microsoft/apm-action](https://github.com/microsoft/apm-action) | primary | versions and topology | 5 |
| [APM: marketplaces guide](https://microsoft.github.io/apm/guides/marketplaces/) | primary | versions and topology | 5 |
| [Dependabot: AI-agent remediation](https://github.blog/changelog/2026-04-07-dependabot-alerts-are-now-assignable-to-ai-agents-for-remediation/) | primary | versions and topology | 4 |
| [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference) | primary | versions and topology | 4 |
| [DevOps guide to APM (blog)](https://dev.to/pwd9000/agent-package-manager-apm-a-devops-guide-to-reproducible-ai-agents-4c25) | blog | versions and topology | 5 |
