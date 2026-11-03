# Final review: `2efe27f..1b569a8` (one commit: "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

There was no task statement. I took the claimed cases from the commit message alone.

The change has two kinds of files, so the form is filled two ways:
- **Shell scripts** (`claude-iso.sh`, `check-tool-updates.sh`): the code items apply directly.
- **Docs, config and an instruction file** (`secure-agent-setup.md`, `.claude/settings.json`, `pinned-versions.toml`, the README and AGENTS.md additions): I used the §2a analogues. The skills loaded were `english-developer-style` and `apm-authoring`.

The drift script ran and printed nothing, because it parses neither shell, Markdown, JSON nor TOML. I re-read every comment in the two scripts and the TOML by hand instead.

Commands I ran: `bash -n` and `shellcheck` (both clean on the two scripts); `claude-iso.sh` under bash and zsh with a stub `claude`; `check-tool-updates.sh` with a stub `curl` and with macOS `/usr/bin/python3` (3.9.6).

One disclosure: I also ran `check-tool-updates.sh` once unstubbed. Contrary to "there is no network", it reached `api.github.com` through this session's proxy. `www.dest-unreach.org` returned 502.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files, counts, mechanisms)

- **`claude-iso.sh:39-41`, the usage examples are wrong.** The header shows `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso`, but the code drops both variables. Run with a stub `claude`, `GH_TOKEN=secret claude-iso` printed no `GH_TOKEN`. A reader following the header starts a session without the credential and doesn't know why. Only the `CLAUDE_ISO_ALLOW=` form works, and that is the form `secure-agent-setup.md:273` shows.
- **`claude-iso.sh:84-89` is false.** It says "any env var that the user set on the *invocation* line of `claude-iso` is preserved."
- **`claude-iso.sh:102-107` contradicts itself and describes no code.** It says "we honour it … well, actually we can't reliably tell…".
- **`pinned-versions.toml:42-43` is false.** It says "The check script uses this [`pinned_at`] as the minimum age…". `read_pinned` (`check-tool-updates.sh:118-126`) reads only `cfg["tools"]`; nothing reads `pinned_at`.
- **`check-tool-updates.sh:163-167` describes a comparison that doesn't exist.** It talks about a "lexical comparison … plain `<` does the right thing". The code only tests `==`, and any different version is labelled "upgrade candidate". With a stubbed upstream whose newest aged release is 2.1.100 (older than the 2.1.117 pin), the script printed `claude-code 2.1.117 … 2.1.100 … upgrade candidate`.
- **`secure-agent-setup.md:69` miscounts the layers.** The heading says "Three-layer defence", but the table under it has four rows (0–3), and the commit message says "four layers".
- **`secure-agent-setup.md:264-267` misdescribes the passthrough list.** It omits `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, and its `XDG_*` suggests every XDG variable. The code passes four (`claude-iso.sh:57-73`).
- **`secure-agent-setup.md:39-42` and `:74` overstate the sandbox.** They say Bash reads are confined to the project tree. `denyRead` covers only `~/`, so `/etc`, `/tmp` and other mounts stay readable.
- **`secure-agent-setup.md:163` and `:171-175` misdescribe `/schedule`.** It is Claude Code's command, not "the framework's". The claim that the scheduled agent "runs in the same secure setup" is not backed by anything in the change: no `claude-iso`, no local `settings.json`.
- **`pinned-versions.toml:91-93` is false.** It says `--no-save` keeps a global install from drifting a local lockfile. `npm -g` never writes a project lockfile.
- **The manifest's socat date disagrees with the commit's own evidence.** The commit message shows the script printing socat `UPSTREAM@ 2026-02-12`, but the manifest records `released = "2026-03-13"`. Nothing in the change supports the manifest date.

## Item 2: claimed cases covered

Claimed cases, from the commit message:

| Claim | What covers it |
| --- | --- |
| Layer 0: clean env | `claude-iso.sh`. Works under bash with `CLAUDE_ISO_ALLOW`; the header form fails (item 1). |
| Layer 1: filesystem sandbox | `settings.json` `sandbox`. Not exercised: the commit says enforcement waits for "the maintainer's first invocation". |
| Layer 2: tool `deny` rules | `settings.json`. No run. |
| Layer 3: forced confirmation via `ask` | `settings.json`. No run, and the patterns don't match what they claim (below). |
| 7-day cooldown pins | `pinned-versions.toml`. The socat date is unsupported (item 1). |
| Side-effect-free check script | Holds: no writes. |
| Weekly `/schedule` wiring | No run. |
| "Adopters scaffold their own copy" | `secure-agent-setup.md` §Adopter setup. |
| JSON parses | Holds. |
| `prek` passes | Claimed; I did not re-run it. |

**The `ask` patterns don't cover what they claim.**
- `secure-agent-setup.md:229-230` says the patterns catch "any non-default-method API call" and "any payload-bearing API call".
- `Bash(gh api * -X *)` misses `gh api -X POST repos/…` (flag before the endpoint) and `--method`. The `-f`/`-F` rules miss `--field`, `--raw-field` and `--input`.
- `:76` claims all visible writes are confirmed, but `gh pr comment`, `gh pr review`, `gh pr close` and `gh issue reopen` are absent.
- Unverified: `git -C <dir> push` probably escapes `Bash(git push *)`.

**The pinned `claude-code` can be overwritten by auto-update.**
- The pin rationale (`pinned-versions.toml:84-94`) is that "a silent autoupdate … would change the framework's effective security posture".
- `settings.json` sets nothing that disables auto-update: no `env.DISABLE_AUTOUPDATER`, no `autoUpdates: false`.
- So an npm install of the pinned version can still auto-update itself.

**The deny/allow split for `~/.config/gh/` and `~/.config/apache-steward/` is unverified** (`secure-agent-setup.md:236-241`).
- The doc says Bash may read these paths while the Read tool may not.
- This session runs under the new `settings.json`. Its effective sandbox lists both paths in `denyOnly` (merged from `permissions.deny`) and also in `allowWithinDeny`.
- So which rule wins for Bash is unproven. If deny wins, `gh` and `oauth-draft` break in every skill.

Commands the change tells someone to run (none of them runs in CI):

| Command | Promised outcome | What runs it |
| --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (`:113-116`, `README.md` of the tool, toml) | Installs the pins | none |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (`:122-124`) | Installs the pins | none |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | Installs the pin | none |
| `source …/claude-iso.sh` in `~/.zshrc` (`:252`), then `claude-iso` | Clean-env session | none, and it fails (below) |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` | Token passed | none; I ran it under bash and it works |
| `bash check-tool-updates.sh` | Status table | none; misbehaves on macOS and Python < 3.11 (items 3 and 5) |
| `/schedule weekly run …` | Weekly candidates | none |
| Verification block (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com`) | Each denied | none; the commit says it was not run |

What each `none` depends on:
- **apt/dnf:** whether the distro's repository carries that exact upstream version. Distros ship their own bubblewrap/socat versions, so `=0.11.1-*` fails where the repository has another.
- **Sourcing from zsh:** the shell. Under `zsh -f`, `source claude-iso.sh; claude-iso` gave `claude_iso_main:37: bad substitution` (bash-only `${!var}`). zsh is the macOS default shell, and the doc names `~/.zshrc`.

**Hunks the commit message doesn't claim:** none. All eight files are listed in its table or its "README.md and AGENTS.md updates" sentence.

## Item 3: boundaries, partitions, and the negative control

Partitions the change claims, and how each is covered:
- **Linux / macOS:** neither the sandbox nor the scripts were run on either.
  - On macOS, `socat_latest_aged` calls GNU `date -d`. BSD `date` rejects it (`date: illegal option -- d`), so socat always reports "upstream lookup failed (rate limit / network)".
  - `tac` is not in the macOS base system.
- **bash / zsh:** zsh fails (item 2).
- **Fedora vs Debian:** no runs.

**Pre-existing state the new config will meet.** Committing `.claude/settings.json` turns the sandbox on for every existing contributor of this repo, and denies Bash reads under `~/` except the eight allowed paths. AGENTS.md "Local setup" tells contributors to run `prek run --all-files`. `prek` keeps its hook environments in `~/.cache/prek`, which is not in `allowRead`. No run from a sandboxed session shows `prek`, `gh` or `uv run` still working.

**No setting stops the agent leaving the sandbox.** The change doesn't set `sandbox.allowUnsandboxedCommands: false`, so the agent can re-run a command with the sandbox disabled: behind a permission prompt normally, and silently in bypass-permissions mode. The threat model (`:46-57`) doesn't name this path, and nothing closes it.

**Network allowlist vs the check script.** `www.dest-unreach.org` is missing from `allowedDomains`, so the socat lookup fails inside the setup the doc says the scheduled agent runs in. Here it returned 502.

**Limits.** `gh_latest_aged` reads only `per_page=20` releases. If none of those 20 is older than the cutoff (claude-code ships about daily), the output says "rate limit / network" instead of "no aged release in window".

**Added instructions** (AGENTS.md is an instruction file):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | A session editing this framework repo, which holds no CVE content | A relaunch warning or request the agent cannot act on itself | "when the session reads `<security-list>` or `<tracker>` content" |

Not findings: none.

## Item 3a: level, placement, and the environment

- **Level:** both scripts are testable in-process with stub `curl`/`claude`, as I did above. The repository adds no test and no `shellcheck` hook for them. `.pre-commit-config.yaml` has hooks only for the two Python projects, and no workflow touches `*.sh`. A small test of the `CLAUDE_ISO_ALLOW` passthrough and of the version-status logic is owed.
- **Placement:** `tools/agent-isolation/` follows the existing `tools/<name>/` layout, and the README there marks it as not a Python project. That's fine.
- **Environment:** `check-tool-updates.sh` needs Python ≥ 3.11 for `tomllib`, and neither the doc nor the script says so. With macOS `/usr/bin/python3` 3.9.6, it prints the header and the bump instructions with an empty table and exits 0. `set -e` does not see a failure inside a process substitution.

## Item 4: names by content, not by position

- `secure-agent-setup.md:174`: "per step 5 above". Step 5 is "Open the bump as its own PR", which is not the "deliberate confirmation" the sentence means. Name the step by its content.
- `secure-agent-setup.md:287`: "[Install commands](#install-commands) above" names its target, so it's fine.
- `tools/agent-isolation/README.md`: "the example block in `secure-agent-setup.md`" is fine.

## Item 5: the failure report

`check-tool-updates.sh:150-153` prints "upstream lookup failed (rate limit / network)" for every empty result:
- a real network failure;
- macOS `date`/`tac` missing;
- no aged release among the latest 20;
- an unknown tool name (the `*)` branch at `:144`).

The reader is sent to look for a rate limit in all four cases. And Python < 3.11 gives an empty table with exit 0 and no line at all (item 3a).

## Item 6: what the writer says it verified

The commit says JSON parsing, a `prek` pass and one end-to-end script run were done, all on the success path. It says outright that sandbox enforcement was not exercised. There is no denial run (the verification block), no run on the bad cases (a pin newer than upstream, macOS, zsh), and no red case for any rule.

## Item 7: siblings of the change

- `AGENTS.md:79-85` "Repo-root files" lists the other root documents but not `secure-agent-setup.md`.
- `AGENTS.md` "References" (`:1120-1132`) lists `tools/github/`, `tools/gmail/`, `tools/vulnogram/` and `tools/cve-org/`, but not `tools/agent-isolation/`.
- `pyproject.toml:21-29` and `.github/dependabot.yml` both list the cooldown-governed tool sets. Neither mentions the new manifest. That's acceptable, since the manifest is manual, but the doc says it is the "same convention" as both.
- The `claude-iso` usage text exists in three places (script header, tool README, `secure-agent-setup.md`). Only the doc's form is correct.

## Findings

All findings below are substantive except the last row, which is taste.

| # | Finding | File:line | Change requested |
| --- | --- | --- | --- |
| 1 | Header usage `GH_TOKEN=… claude-iso` drops the token (verified); false and self-contradicting comments | `claude-iso.sh:39-41, 84-89, 102-107` | Show the `CLAUDE_ISO_ALLOW=` form; delete the false comments |
| 2 | Sourcing from zsh fails with `bad substitution`, but the doc says `~/.zshrc` | `claude-iso.sh:80`, `secure-agent-setup.md:252` | Make the script zsh-compatible, or document it as bash-only |
| 3 | The script never reads `pinned_at`, though the manifest says it does | `pinned-versions.toml:42-43` | Fix the comment, or make the script use `pinned_at` |
| 4 | Comment describes a `<` comparison the code lacks; older upstream is labelled "upgrade candidate" (verified) | `check-tool-updates.sh:160-168` | Use a version-aware comparison, plus a test with an older upstream |
| 5 | Python < 3.11: empty table, exit 0 | `check-tool-updates.sh:118-126, 173` | Fail loudly on a parse error; state the Python requirement |
| 6 | Every empty lookup result is reported as "rate limit / network"; macOS `date -d`/`tac` always fail | `check-tool-updates.sh:84-108, 150-153` | Give each cause its own message; make the date handling portable or declare Linux-only |
| 7 | `ask` rules miss `--method`, `--field`, `--input`, flag-before-endpoint, and `gh pr comment/review/close`; the doc claims "any" | `settings.json`, `secure-agent-setup.md:76, 229-230` | Widen the patterns, or narrow the claim |
| 8 | No auto-update disable, so the claude-code pin can drift | `settings.json`, `pinned-versions.toml:84-94` | Set `DISABLE_AUTOUPDATER`/`autoUpdates`, or drop the claim |
| 9 | Precedence of the deny/allow split on `~/.config/gh` and `~/.config/apache-steward` is unproven | `secure-agent-setup.md:236-241` | A run of `gh auth status` from sandboxed Bash, plus a Read-tool denial |
| 10 | No `allowUnsandboxedCommands: false`, so the agent can run commands outside the sandbox | `settings.json` | Set it, or name the escape in the threat model |
| 11 | Commands not run on any configuration: apt/dnf version pins, verification block, `/schedule` | `secure-agent-setup.md:113-136, 167, 313-318` | A run on each supported distro, plus the denial block |
| 12 | Existing contributors' tools (`prek` cache) under the new `denyRead ~/` are untested | `settings.json:6-16` | A sandboxed `prek run --all-files` |
| 13 | "Three-layer" heading over four layers | `secure-agent-setup.md:69` | "Four-layer", with the TOC updated |
| 14 | Sandbox confinement overstated: only `~/` is denied | `secure-agent-setup.md:39-42, 74` | Say "outside the home directory's allowed paths" |
| 15 | Passthrough list in the doc doesn't match the code | `secure-agent-setup.md:264-267` | List the exact variables |
| 16 | socat `released` date contradicts the commit's own script output | `pinned-versions.toml:67` | Correct the date from the source |
| 17 | `/schedule` called the framework's, and its "same secure setup" is unsupported; `dest-unreach.org` missing from the allowlist | `secure-agent-setup.md:163-175` | Correct the attribution and the claim; add the host or note the failure |
| 18 | `--no-save` lockfile rationale is false | `pinned-versions.toml:91-93` | Drop the flag and the comment |
| 19 | AGENTS.md instruction fires in sessions with no CVE content | `AGENTS.md:312` | See the added-instructions table |
| 20 | Root-files and References lists omit the new doc and tool | `AGENTS.md:79-85, 1120-1132` | Add both |
| 21 | "per step 5 above" names the wrong step by position | `secure-agent-setup.md:174` | Name the step by its content |
| 22 | (Taste) `curl` deny reason "bypasses the sandbox proxy" is doubtful: sandboxed Bash goes through the proxy | `secure-agent-setup.md:218` | Reword the reason |

Not checked: I did not run `prek`, the Fedora/Debian install commands, or a real Claude Code session under the new `settings.json` to test denials. The sandbox precedence in finding 9 is inferred from this session's effective configuration, not observed. I did not do a style pass over the prose.
