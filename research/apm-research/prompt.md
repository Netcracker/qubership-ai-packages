## Goal
Pick one open-source tool, or several in the case of a hybrid architecture, to
manage skills, MCP servers, agents / sub-agents, commands, and instructions
(contributions to AGENTS.md / CLAUDE.md) in a corporate environment.

## Hard requirements (must-have)

1. **Primitives.** The manager must handle at minimum:
   - Skills (mandatory)
   - MCP servers (preferable, not a blocker)
   - Commands / slash commands
   - Instructions — contributions to AGENTS.md / CLAUDE.md
   - Agents / sub-agents

2. **Targets.** Install packages into known agents, at minimum:
   - Claude Code
   - Cursor
   - OpenCode
   - Codex (OpenAI)

3. **Versioned dependencies.** Packages must declare explicit versioned
   dependencies on other packages. Ideal — semver with range resolution
   (`^1.2.0`, `~1.2.3`); minimum — pinned refs with a lockfile and transitive
   resolution.

4. **Multi-repo sources.** Ability to pull packages from several repositories
   at once: public (GitHub OSS) and corporate (self-hosted GitLab, Bitbucket,
   Azure DevOps, private Gitea).

5. **Metadata.** Each package (skill) must include the following mandatory
   fields: `name`, `description`, `version`, `author`, `dependencies`. An
   official validation schema is a plus.

6. **Marketplace.** A way to list and search packages:
   - CLI — mandatory
   - Web UI — nice to have

7. **Licence.** MIT, Apache-2.0, or another business-friendly licence (BSD,
   MPL-2.0, ISC). GPL / AGPL — exclude or flag explicitly as a risk.

8. **OS support**: Windows, macOS, Linux.

## Research scope

Run an exhaustive search; do not stop at the obvious top three. Include:

- **Known candidates to verify** (already identified, check that data is
  current):
  - Microsoft APM (github.com/microsoft/apm)
  - Lola (github.com/RedHatProductSecurity/lola)
  - npx skills / skills.sh (github.com/vercel-labs/skills)
  - SkillKit (github.com/rohitg00/skillkit)
  - OpenSkills (npmjs.com/package/openskills)
  - ARM / ai-resource-manager (github.com/jomadu/ai-resource-manager)
  - Claude Code plugin marketplaces (native mechanism)

- **Look beyond those**:
  - Awesome-lists and surveys on agent skills / AI package managers from
    2025–2026
  - GitHub topics: `ai-package-manager`, `agent-skills`, `skill-manager`,
    `mcp-manager`
  - Hacker News, Reddit /r/LocalLLaMA and /r/ClaudeAI threads
  - Articles on dev.to, Medium, and engineering blogs of large companies
  - Alternative or lesser-known projects with fewer than 1k stars but active
  - Projects that do not call themselves a 'package manager' but solve the
    same problem (plugin manager, context manager, skill registry, etc.)
  - Proprietary or enterprise tools for a comparison baseline (but do not
    recommend them)

## Evaluation criteria for each candidate

For every tool found, collect:

**Formal parameters:**
- Name, URL, maintainer (organisation / author)
- Licence (exact name)
- Current version and date of the last release
- GitHub stars / forks / open issues / contributors
- Commit frequency over the last three months
- Implementation language

**Functional review (against the seven requirements above):**
- For each requirement: ✅ fully / ⚠️ partially / ❌ no
- A direct quote from the documentation or a code link backing the verdict
- If partial — what exactly is missing

**Architecture:**
- Manifest format (apm.yml / package.json / custom)
- How dependency resolution is built
- How conflicts are handled (same names from different sources)
- Lockfile format and reproducibility
- Support for private registries and authentication
- Security: package scanning, supply-chain protection, signatures

**Adoption and ecosystem:**
- How many public packages / skills are available
- Major adopters (if there are public references)
- Compatibility with open standards (AGENTS.md, Agent Skills spec, MCP)
- Community activity, presence of a governance model

**Risks:**
- Vendor lock-in (even for OSS tools)
- Bus factor (how many active maintainers)
- Maturity (versions below 1.0 — risk of breaking changes)
- Known security incidents or vulnerabilities

## Output format

### 1. Executive summary
Two or three paragraphs: which tool is recommended as primary, which as
fallback, the key trade-offs.

### 2. Comparative table
All candidates × the seven requirements + licence + popularity. Use
✅ / ⚠️ / ❌ plus numeric metrics where applicable.

### 3. Detailed review of the top-3 candidates
For each — every formal and functional parameter, quotes from the
documentation, a real example of `apm.yml` or the equivalent manifest, pros,
cons, and when to choose it.

### 4. Disqualified short list
Who was reviewed and rejected — with a specific reason (violates requirement
N, GPL licence, abandoned, etc.).

### 5. Hybrid architectures
If a single tool does not cover all requirements, propose combinations (for
example, 'APM for orchestration + npx skills for installation from a wide
catalogue').

### 6. Recommendation and adaptation plan
- Which tool to choose
- Which requirements it does not cover and how to compensate (custom
  extensions, wrappers, migration)
- Risks over a 12–24 month horizon (project decline, standards change)

## Anti-bias instructions

- Do not pick a tool by popularity — 7.5k stars do not outweigh a violation
  of requirement #3.
- Do not take the README at face value; verify claimed features against code
  or documentation.
- If you find a mismatch between the README and the real implementation,
  flag it explicitly.
- If a requirement is met only via 'planned on the roadmap', that is ❌, not
  ✅.
- For every recommendation, state the date of the last verification — the
  industry moves quickly.

## Adopter context (for calibrating recommendations)

- Corporate environment, infrastructure / ops team
- Kubernetes, Helm, ArgoCD, GitLab in use (self-hosted is possible)
- Scale: 300+ components, parallel use of Claude Code, OpenCode, Cursor
- An internal skills catalogue already exists with explicit dependencies
  (REGISTRY.yaml + Python resolver) — migration from it must be realistic
- Supply chain is critical: packages will be read by agents, and prompt
  injection through skill files is a real risk
