# Skill, MCP, and AGENTS.md package manager research

Comparative evaluation of open-source tools that manage AI coding-agent primitives (skills, MCP
servers, slash commands, AGENTS.md / CLAUDE.md contributions, and sub-agents). Target estate: a
corporate platform running Claude Code, Cursor, OpenCode, and Codex side by side over 300+
components.

Two deep-research passes (17 April 2026 and 21 May 2026) reach the same primary recommendation:
**Microsoft APM** (`github.com/microsoft/apm`, MIT).

## Goal

Pick one open-source tool, or a hybrid stack, that:

- manages all five primitive types from a single manifest;
- installs into Claude Code, Cursor, OpenCode, and Codex;
- declares versioned dependencies with transitive resolution and a lockfile;
- pulls packages from multiple git hosts, including self-hosted GitLab;
- carries a business-friendly licence (MIT, Apache-2.0, BSD, MPL-2.0, ISC);
- runs on Windows, macOS, and Linux.

The brief, the scoring rubric, and an anti-bias section are written out in `prompt.md`
(English translation; `prompt.ru.md` keeps the Russian original).

## Methodology

Both passes follow the same protocol:

1. Author the hard requirements and the scoring rubric by hand in `prompt.md`.
1. Feed the brief into a deep-research LLM session with web access. The agent surveys GitHub
   topics (`ai-package-manager`, `agent-skills`, `skill-manager`, `mcp-manager`), awesome-lists,
   Hacker News and Reddit threads, dev.to and engineering blogs, and proprietary baselines for
   context.
1. For each candidate, the agent collects formal metadata (licence, stars, release cadence,
   language), scores it against the seven functional requirements with direct citations from the
   README or source, and notes gaps.
1. The agent produces a comparative table, a top-3 deep dive, a short list of disqualified
   candidates, hybrid options, and a migration plan.

The April pass (`results-2026-04-17.md`; original Russian in `results-2026-04-17.ru.md`) ran on
17 April 2026. The May pass (`results-2026-05-21.md`) ran on 21 May 2026 to check whether the
conclusions still held after a month of rapid releases.

## Findings

Both passes recommend **Microsoft APM** (MIT) as primary. It is the only surveyed tool that
combines all five primitives, the four required targets, transitive dependency resolution, a
content-hashed lockfile (`apm.lock.yaml`), multi-host git sources, an enterprise policy file
(`apm-policy.yml`), and a hidden-Unicode supply-chain scanner.

Both passes flag the same gap: no tool surveyed implements semver range resolution (`^1.2.0`,
`~1.2.3`) between skill packages. APM pins to exact git refs and resolves missing refs to a
concrete commit SHA in the lockfile. That sits at the brief's "minimum acceptable" tier.

Two named candidates are excluded on licence grounds: Red Hat Lola (GPL-2.0-or-later) and ARM /
ai-resource-manager (GPL-3.0). The Claude Code native plugin marketplace targets only Claude
Code, so it cannot serve as the single source of truth. It does work as a downstream publishing
endpoint via `apm pack --format plugin`.

## Differences between the April and May reviews

The primary recommendation is unchanged. The supporting picture shifted in several ways:

| Topic | April 2026 ([`results-2026-04-17.md`](results-2026-04-17.md)) | May 2026 ([`results-2026-05-21.md`](results-2026-05-21.md)) |
| --- | --- | --- |
| APM version | v0.8.11 | v0.13.0 |
| APM popularity | ~1.2k–1.7k stars | 2.4k stars, 180 forks |
| APM bundle default | `bundle-format: apm` | Default flipped to `plugin` in v0.12.0; opt-in restore needed |
| Vercel `skills` | 7.5k stars | 19.4k stars, 1.6k forks |
| `gh skill` | Launched the day before the report; "watch closely" | Re-classified as a flat file copier (per maintainer prose); useful complement, not a primary |
| Semver ranges | Listed as an APM-specific gap | Confirmed as a category-wide gap; APM maintainer quoted verbatim on `renovatebot/renovate#42507` |
| Newly surfaced tool | not covered | `intellectronica/ruler` (MIT, 2.6k stars, 32 named targets) as an optional supplement |
| Hybrid stack | APM + MCPM + Snyk Agent Scan + LiteLLM marketplace pattern | APM + `npx skills` and `gh skill` for discovery + mcpm.sh or `ravitemer/mcp-hub` for MCP runtime + Renovate for tag bumps |
| Supply-chain framing | Long CVE list (mcp-remote RCE, Flowise RCE, ClawJacked, ToxicSkills) | Condensed into a caveats block; weight moves onto APM's own audit + policy story |
| Re-evaluation cadence | Implicit | Calendar event every 6 months (Nov 2026, May 2027) |
| Lola | Original repo, 13 stars | Original 13 / 7 plus active `LobsterTrap/lola` fork at 63 / 17; still GPL |

Both passes agree on the disqualifications, the shape of the migration plan (around 12 weeks,
GitLab self-hosted as the primary registry, `apm audit --ci` gating the pipeline), and the
bus-factor warning (two named APM maintainers; the MIT licence keeps a fork on the table as
fallback).

## Files

- `prompt.md`: research brief and scoring rubric, English translation.
- `prompt.ru.md`: Russian original of the brief (source of truth).
- `results-2026-04-17.md`: first deep research pass, 17 April 2026, English translation.
- `results-2026-04-17.ru.md`: Russian original of the first pass (source of truth).
- `results-2026-05-21.md`: second deep research pass, 21 May 2026 (already English).
