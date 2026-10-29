I've finished the review. The commit adds no tests. Several of its central claims fail when run, and the review found nine substantive problems. Four matter most:
- **The wrapper's main use breaks.** Sourced in bash, calling `claude-iso` replaces your shell, so the terminal closes when Claude exits. Sourced in zsh, which the doc recommends, it fails with a "bad substitution" error.
- **The check script fails silently.** With macOS's stock Python 3.9 it prints only the table header and exits 0. The socat lookup cannot succeed on macOS, or inside the commit's own sandbox.
- **The new settings block one of the repo's own recipes.** The cve-org publication check that `sync-security-issue` uses runs `curl` against a host that isn't allowlisted. The settings deny `curl` and don't allow that host.
- **Several comments contradict the code**, including how to pass in one credential and what the check script does.

There was no separate task statement, so the claimed cases come from the commit message alone. The drift script printed nothing, because it does not parse shell, Markdown, JSON or TOML. I did every item by hand, using the skill's §2a analogues for the documentation files.

### Item 1: comments consistent with the code and with each other
These are findings, all checked against the code:
- **`claude-iso.sh` header, lines 39–41:** it says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` bring in one credential. They don't. I ran it with a stub `claude`, and both variables were dropped. Only `CLAUDE_ISO_ALLOW` passes a variable through.
- **`claude-iso.sh`, lines 84–90 and 104–109:** the first comment says a variable set on the command line is detected and kept. The second reverses itself mid-sentence ("well, actually we can't reliably tell") and sits above no code.
- **`check-tool-updates.sh`, lines 163–167:** the comment describes a "lexical comparison… plain `<`". The code only tests `==`. Any other upstream version, older ones included, is reported as an "upgrade candidate".
- **`pinned-versions.toml`, lines 42–43:** it says "The check script uses this [`pinned_at`]". `read_pinned` never reads `pinned_at`.
- **`pinned-versions.toml`, lines 95–97:** it says `--no-save` keeps a global install from changing a local lockfile. A `-g` install never touches a project lockfile, so the stated reason is false.
- **`secure-agent-setup.md`, line 69:** the heading says "Three-layer defence" but the table has four layers (0–3). The commit message says four.
- **`secure-agent-setup.md`, lines 264–266:** it says the wrapper passes `XDG_*` through. Only four `XDG_` variables pass. The list also leaves out `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, which the code does pass.
- **`secure-agent-setup.md`, line 218:** it says curl through Bash "bypasses the sandbox proxy". In this session, the script's own `curl` call reached `api.github.com` through the proxy, so the claim looks wrong.
- **`secure-agent-setup.md` line 98 and `pinned-versions.toml` lines 85–92:** they say pinning stops a silent autoupdate. Nothing in the change turns Claude Code's autoupdater off. `claude-iso` would also strip any `DISABLE_AUTOUPDATER` the user exported. Not verified against 2.1.117.
- **Data disagreement:** the manifest gives socat as released 2026-03-13. The commit message's own run shows `UPSTREAM@ 2026-02-12` for the same version.

These claims checked out: the pyproject `exclude-newer = "7 days"` and the per-package override for `uv`, the 7-day cooldowns in `dependabot.yml`, and the anchors `README.md#prerequisites-for-running-the-agent-skills`, `AGENTS.md#local-setup` and `AGENTS.md#confidentiality-of-the-tracker-repository`.

### Item 2: claimed cases covered
Shell scripts have no tests in the repo, and the commit adds none.

| Claimed case (source) | What covers it |
|---|---|
| Wrapper strips variables not on the passthrough list (commit, doc) | No test. My stub run confirmed it. |
| One credential injected for one session (doc lines 269–277) | No test. The `CLAUDE_ISO_ALLOW` form works with the stub; the header form fails (Item 1). |
| `source … claude-iso.sh` from `~/.bashrc` or `~/.zshrc`, then `claude-iso` (doc 251–261, README "Usage at a glance") | **none.** In bash, `exec` inside the sourced function replaces your shell; `echo SHELL-SURVIVED` never printed. In zsh, it fails with `claude_iso_main:37: bad substitution` because `${!var}` is bash-only. |
| `bash claude-iso.sh [args]` (header) | Works with the stub. |
| Check script prints the status table and upgrade candidates (commit) | Commit's run only, from an unstated platform. On macOS with `/usr/bin/python3` (3.9, no `tomllib`) it prints a traceback and the bare header, and **exits 0**. With Python 3.14 here, the socat lookup always fails because BSD `date` has no `-d`. Inside the commit's own sandbox it also fails because `www.dest-unreach.org` isn't allowlisted. |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` and `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (doc 112–125, toml) | **none.** Depends on which package versions each distro release carries, and whether apt accepts a glob in a version pin. Not verified, no network. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | none (not verified). |
| `/schedule weekly run tools/agent-isolation/check-tool-updates.sh` (doc 166–175) | **none.** `/schedule` is Claude Code's command, not the framework's. It creates cloud routines, so the claim that it "runs in the same secure setup" is not verified. |
| The doc's verification block (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com`) | none. The commit says end-to-end enforcement is left to the maintainer's first run. |
| The agent can't read `~/.config/gh` but bash can (doc 236–241) | **none, not verified.** In this session's derived sandbox config, `~/.config/gh` appears in both the deny list and the allow-within-deny list. Which one wins is unknown. I chose not to probe a credential path. |
| `.claude/settings.json` is valid JSON | `json.load` passes. |
| `.claude/settings.local.json` is gitignored by default (doc 303–305) | none. This repo's `.gitignore` doesn't list it. |

### Item 3: boundaries, partitions, and the negative control
- **Platforms:** the change supports Linux and macOS, but only one unnamed platform was run. On macOS the socat lookup and an old Python both fail.
- **Shells:** bash and zsh are both documented; zsh fails.
- **Execution modes:** for the wrapper, "sourced" fails and "executed" works.
- **Starting state:** nothing covers a host that already has a newer Claude Code installed, or autoupdates on. The npm pin doesn't stop autoupdate.
- **Negative control:** the commit gives no denial run.

### Item 3a: level, placement, and the environment
- No test exists, and no CI job or hook runs either script. `.pre-commit-config.yaml` has doctoc and the basic text hooks only, with no shellcheck.
- `shellcheck` reports nothing on either script, and `bash -n` passes.
- Placement under `tools/agent-isolation/` with a README matches the other tool folders.

### Item 4: names by content, not by position
- `secure-agent-setup.md:174` says "per step 5 above"; name the step by its content, e.g. "the bump PR".
- The "Three-layer" count is already listed under Item 1.

### Item 5: the failure report
- When `read_pinned` fails, the check script prints the header and exits 0, so a cron or `/schedule` run reports success with an empty table.
- Any lookup failure is labelled "rate limit / network", even when the cause is a missing `date -d` or `tomllib`.

### Item 6: what the writer says it verified
- The commit reports: `prek` passing, one run of the check script on an unstated platform, and JSON parsing.
- It reports no run of `claude-iso` and no denial check, and says so.

### Item 7: siblings of the change
- **`tools/cve-org/tool.md:66,90` and `.claude/skills/sync-security-issue/SKILL.md:873`** run `curl -sSf https://cveawg.mitre.org/...`. The new settings deny `Bash(curl *)` and don't allow `cveawg.mitre.org`, so the publication check that `sync-security-issue` uses is blocked under the commit's own settings.
- **Places that hard-code the pinned versions:** the toml `install.*` strings, the version table at doc lines 94–98, and `tools/agent-isolation/README.md` lines 36–37. Neither the bump steps in the doc (139–156) nor the ones the script prints name these.
- **Lists of repo files and tools:** `AGENTS.md` "Repo-root files" (line 79) and the `tools/` entries under "References" (around line 1129) don't list `secure-agent-setup.md` or `tools/agent-isolation/`.

### Findings
| Finding | Label | File:line | Request |
|---|---|---|---|
| Sourced wrapper: `exec` replaces the user's shell (bash) or fails with "bad substitution" (zsh) | Substantive | `tools/agent-isolation/claude-iso.sh:111`, `:96`; doc 251–253 | Run `env -i …` without `exec` in the sourced path (or in a subshell); use a zsh-safe lookup or document bash only; run both shells. |
| Header's one-credential examples don't work; the comments contradict themselves | Substantive | `claude-iso.sh:39-41`, `:84-90`, `:104-109` | Use the `CLAUDE_ISO_ALLOW` form; delete the comment that reverses itself. |
| Check script exits 0 when the manifest can't be parsed; needs Python ≥ 3.11, GNU `date`, and a host not on the allowlist | Substantive | `check-tool-updates.sh:117-125`, `:85-106`, `:179` | Fail with a non-zero exit when `read_pinned` fails; state the requirements or make the date parsing portable; add `www.dest-unreach.org` to the allowlist or document the failure. |
| `curl` denied and `cveawg.mitre.org` not allowlisted, which blocks the `sync-security-issue` check-published recipe | Substantive | `.claude/settings.json:51`, `:19-34` | Reconcile with `tools/cve-org/tool.md`: allow the host and add `Bash(curl -sSf https://cveawg.mitre.org/*)` to the ask list, or switch the recipe to a non-curl method. |
| Comment describes a `<` comparison the code doesn't do; any different version counts as an "upgrade candidate" | Substantive | `check-tool-updates.sh:163-167` | Compare versions, or correct the comment and the status text. |
| `pinned_at` said to be used by the check script; it isn't | Substantive | `pinned-versions.toml:42-43` | Fix the comment, or make the script use the field. |
| "Three-layer" heading over four layers; passthrough list in the doc is wrong | Substantive | `secure-agent-setup.md:69`, `:264-266` | Make the count and the list match the code. |
| Install commands and `/schedule` never run on the configurations they promise; socat release date disagrees with the commit's run | Substantive | doc 112–137, 163–175; toml 69 | Run them on named distros, or mark them unverified; correct the date. |
| Pin doesn't stop autoupdate | Substantive | toml 85–92, doc 98 | Document turning off autoupdate in `settings.json` (env or the `autoUpdates` setting). Not verified. |
| Version strings hard-coded in places the bump steps don't name; AGENTS.md lists not updated | Substantive | toml `install.*`, README 36–37, AGENTS.md 79/1129 | Extend the bump steps, or drop the duplicated versions; add the list entries. |
| "per step 5 above" | Taste | `secure-agent-setup.md:174` | Name the step by its content. |
| Reason given for `--no-save` | Taste | `pinned-versions.toml:95-97` | Drop the flag or the stated reason. |
| Claim that curl through Bash bypasses the proxy | Taste (unverified) | `secure-agent-setup.md:218` | Rephrase it, e.g. "defence in depth". |

**Not checked:** I didn't run the suite or `prek`, or any install command. I didn't verify the apt/dnf/npm availability, the settings semantics in Claude Code 2.1.117, or which sandbox rule wins for `~/.config/gh`. I didn't load `english-developer-style` or do a prose-style pass. The check script reached `api.github.com` once through the sandbox proxy, despite the brief saying there was no network. I changed no repository files; the stub `claude` used for the wrapper runs is in `$TMPDIR/rv`.
