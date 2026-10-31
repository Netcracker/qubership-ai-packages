# Final review: `2efe27f..HEAD` (1b569a8, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest")

I had no separate task statement, so the claimed cases come from the commit message only. The change has no code in a language the drift script parses (JSON, Markdown, shell, TOML). The script exited 0 and printed nothing. So I filled the form through the §2a analogues for the docs, `AGENTS.md`, and `.claude/settings.json`, and through the literal items for the two shell scripts. Loaded skills: `english-developer-style`, `apm-authoring` (for `AGENTS.md`), and `test-authoring` (for the scripts). I changed no files.

What I ran locally:
- **Syntax and lint:** `bash -n` and `shellcheck` pass on both scripts.
- **JSON:** `.claude/settings.json` parses.
- **`claude-iso.sh`:** sourced in bash and in zsh, with a fake `claude` on `PATH`.
- **macOS tools:** checked `date -d`, `tac` and `/usr/bin/python3` (3.9.6).
- **Repo greps:** searched for every host, `curl` recipe, and version-string site.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

1. **`claude-iso.sh:39-41`**: the header says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` inject a credential for one session. I ran it: both variables arrive unset (`fake-claude GH_TOKEN=unset AWS_PROFILE=unset`). Only names listed in `CLAUDE_ISO_ALLOW` pass through, which `secure-agent-setup.md:273` gets right. A user who copies the header form ends up with no token and doesn't know why. **Request:** use the `CLAUDE_ISO_ALLOW=… claude-iso` form in the header. **Substantive.**
2. **`claude-iso.sh:85-90` and `:101-106`**: the first comment says "any env var that the user set on the invocation line … is preserved". The second retracts it ("well, actually we can't reliably tell"). Only the retraction matches the code. **Request:** delete the first claim and the retraction, and keep one sentence: only `CLAUDE_ISO_ALLOW` names pass through. **Substantive.**
3. **`pinned-versions.toml:42-43`**: "The check script uses this [`pinned_at`] as the minimum age …". `read_pinned` (`check-tool-updates.sh:115-122`) never reads `pinned_at`. **Request:** remove the sentence, or make the script check `released + 7d <= pinned_at`. **Substantive.**
4. **`check-tool-updates.sh:161-166`**: the comment describes a "lexical comparison … plain `<`", but the code only tests equality. Any upstream version that differs from the pin is labelled "upgrade candidate", including an older one (for example, after an upstream release is withdrawn). **Request:** make the comment describe the equality check, or compare with `sort -V`. **Substantive.**
5. **`secure-agent-setup.md:69` and TOC `:7`**: the heading says "Three-layer defence", but the table under it has four layers (0–3), and the commit message says four. **Request:** retitle the section "Layered defence" or "Four-layer defence". **Substantive.**
6. **`secure-agent-setup.md:264-266`**: "hard-allows only a tiny passthrough list (…)" leaves out `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, which `claude-iso.sh:57-73` passes through. A reader auditing what leaks gets an incomplete list. **Request:** list them all, or say "see `passthrough` in the script". **Substantive.**
7. **`secure-agent-setup.md:201` comment and `:218` comment**: the allowlist is described as "every host the framework legitimately reaches". It leaves out `cveawg.mitre.org`, which `tools/cve-org/tool.md:66` and `.claude/skills/sync-security-issue/SKILL.md:873` call. The reason `:218` gives for denying `Bash(curl *)` ("bypasses the sandbox proxy") is also doubtful for sandboxed Bash. **Request:** add the MITRE host (and `services.nvd.nist.gov` if the NVD fallback in `tools/cve-org/tool.md:49` is meant to run), and reword the reason. **Substantive.**
8. **`secure-agent-setup.md:163`**: "The framework's `/schedule` slash-command". `/schedule` is a Claude Code command; the framework ships nothing by that name. **Substantive** (a reader looks for it in the repo).
9. **Commit message vs `pinned-versions.toml:69`**: the check-script output quoted in the commit gives socat `UPSTREAM@ 2026-02-12`, but the manifest says `released = "2026-03-13"`. One of the two is wrong, and the doc table copies the manifest. **Request:** pick the right date and say where it came from (HTTP `Last-Modified` or the release announcement). **Substantive.**

## Item 2: claimed cases covered (from the commit message)

| Claimed case | Covering section, test, or run |
| --- | --- |
| Layer 0 strips credential-shaped env vars | `claude-iso.sh`. No test. My run confirms stripping in bash. |
| `CLAUDE_ISO_ALLOW` opt-in injection | `claude-iso.sh:91-98`. No test. My run confirms it works. |
| Layers 1–3 in `settings.json` | `.claude/settings.json`. The commit says enforcement was not exercised ("first invocation after merge will exercise it"). |
| Deny/allow split: Bash *uses* `~/.config/gh/`, the agent can't Read it (`secure-agent-setup.md:236-241`) | none (see finding 2b below) |
| Pins satisfy the 7-day cooldown | Manifest dates. `claude-code` is exactly 7 days old on `pinned_at` (boundary met). |
| Check script is side-effect-free and reports candidates | Commit shows one run on the "up to date" branch only. |
| Weekly `/schedule` routine surfaces candidates | none |
| Pin holds `claude-code` at 2.1.117 | none |

Commands the change tells readers to run:

| Command | Promised outcome | What runs it |
| --- | --- | --- |
| `sudo apt-get install … bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:113-117`, `tools/agent-isolation/README.md:36`) | Installs the pins | none |
| `sudo dnf install bubblewrap-0.11.1 socat-1.8.1.1` (`:122-125`) | Installs the pins | none |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (`:136`) | Pins Claude Code | none |
| `source …/claude-iso.sh` from `~/.bashrc` **or `~/.zshrc`** (`:252-253`) | Defines `claude-iso` | none |
| `bash tools/agent-isolation/check-tool-updates.sh` (`:144`) | Prints the status table | The commit's single Linux run |
| `/schedule weekly run …check-tool-updates.sh…` (`:166-169`) | Surfaces candidates | none |
| The verification trio `cat ~/.aws/credentials` / `echo $AWS_ACCESS_KEY_ID` / `curl https://example.com` (`:313-318`) | Each is denied | none |

Findings:

- **2a. The pinned `apt`/`dnf` forms install only where the distro release carries exactly that upstream version.** The outcome depends on which distro release the host runs, and the doc names none. As far as I know, current LTS releases ship older bubblewrap/socat (for example, Ubuntu 24.04 ships 0.9.x and 1.8.0.x), so `=0.11.1-*` would fail with "Version not found". **Request:** run each form on the supported releases, or name the releases where the pin resolves and give a from-source fallback. **Substantive.**
- **2b. The deny/allow split for `~/.config/gh/` and `~/.config/apache-steward/` is unverified.** The commit says enforcement was not exercised. In this very session, the effective sandbox lists `~/.config/gh` under read `denyOnly` *and* `/Users/vlsi/.config/gh` under `allowWithinDeny`. So the `permissions.deny Read(...)` rule also reaches the Bash sandbox, and which entry wins is untested. I did not probe the credential path. **Request:** run `gh auth status` and `oauth-draft` from sandboxed Bash, plus an agent `Read` of the same file, on both Linux and macOS. **Substantive.**
- **2c. `.claude/settings.json:51` (`Bash(curl *)` deny) blocks recipes the framework's own skills tell the agent to run.** These are `sync-security-issue/SKILL.md:873` (`curl -sSf https://cveawg.mitre.org/...`), `tools/cve-org/tool.md:66,90` and `tools/gmail/ponymail-archive.md:139`. With the setup applied, the "CVE is live" check in sync cannot run. **Request:** replace the recipes with a non-`curl` form, narrow the deny rule, or name the conflict and the workaround in the doc. **Substantive.**
- **2d. Nothing holds `claude-code` at 2.1.117.** The manifest's own rationale (`pinned-versions.toml:87-91`) is to avoid "a silent autoupdate". But Claude Code's auto-updater is still on: `settings.json` sets no `DISABLE_AUTOUPDATER`/`autoUpdates`, and the doc says nothing about it. `claude-iso.sh:47` also runs whichever `claude` comes first on `PATH`, which may be a native install rather than the npm pin. **Request:** disable auto-update in the documented setup, or drop the claim that the pin prevents drift. **Substantive.**
- **2e. The zsh form is broken.** Sourcing in zsh fails: `claude_iso_main:37: bad substitution`, because `${!var-}` is bash-only. **Request:** drop `~/.zshrc` from `:252`, or make the script portable to zsh. **Substantive.**
- **2f. The scheduled routine cannot report socat.** The doc says the routine "runs in the same secure setup" (`:171`). That setup's `allowedDomains` does not include `www.dest-unreach.org`, so the socat lookup always fails there. **Request:** add the host, or state that socat is checked by hand. **Substantive.**

Hunks the commit message doesn't claim: none. Every file is listed in its table.

## Item 3: boundaries, partitions, and the negative control

- **3a. The check script has untested partitions.** Only the all-equal branch was run; nothing exercised "upgrade candidate" or "lookup failed".
  - On stock macOS, a platform the doc supports, `date -d` fails (BSD `date: illegal option -- d`). `tac` is absent unless coreutils is installed, and `/usr/bin/python3` is 3.9.6, which has no `tomllib`.
  - Result: socat always shows "lookup failed". With the system Python, `read_pinned` fails inside `< <(…)`, so the script prints an empty table and exits 0.
  - Separately, `per_page=20` misreports "no aged release among the latest 20" as a rate-limit or network failure. That happens whenever `claude-code` ships more than 20 releases in 7 days.
  - **Request:** run the script on macOS, and give "no aged release" its own status. **Substantive.**
- **3b. Pre-existing state is not handled.** Adopter step 2 (`secure-agent-setup.md:289-291`) tells readers to *copy* `settings.json` into a tracker that may already have its own `.claude/settings.json` (hooks, permissions). An existing native Claude install also competes on `PATH` (see 2d). **Request:** add a merge instruction for an existing file. **Substantive.**
- **3c. No timeouts in the check script.** The `curl` calls in `check-tool-updates.sh` set no `--max-time`. Against a hung host, the weekly routine waits forever. **Request:** bound each call. **Substantive.**

Added instructions (`AGENTS.md`):

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | A docs edit in this framework repo, session started with plain `claude` | A demand to relaunch under `claude-iso` before editing | "when the session will read tracker or `<security-list>` content" |

Not findings: none.

## Item 3a: level, placement, and the environment

The two shell scripts have behavior you can observe in one process: env stripping, the `CLAUDE_ISO_ALLOW` path, and manifest parsing. I tested all three in seconds with a fake `claude`. Yet neither script has a test, and no `shellcheck` hook runs in `.pre-commit-config.yaml`. **Request:** add a small test or hook next to the existing pytest hooks, with a fake `claude` on `PATH`. **Substantive.**

Placement matches the sibling `tools/<name>/` layout. I could not run the repo gate (`prek`): it is not installed, and `pre-commit` needs network to fetch hooks.

## Item 4: names by content, not by position

- `secure-agent-setup.md:174` says "(per step 5 above)", and the footer of `check-tool-updates.sh` says "The 7-day cooldown above". Both could name the step by its content ("the step that opens the bump as its own PR"). **Taste.**

## Item 5: the failure report

- **5a. The check script names the wrong cause.** It prints `upstream lookup failed (rate limit / network)` (`check-tool-updates.sh:153`) for every failure, including BSD `date`, a missing `tac`, and no aged release in the window. A missing `tomllib` prints nothing at all and exits 0. **Request:** print the real cause, and exit non-zero when the manifest cannot be read. **Substantive.**
- **5b. The verification block tests weaker properties than it claims** (`:313-318`). `curl example.com` tests the permission rule, not the network allowlist. Nothing tests the claimed gh/`apache-steward` split. **Request:** add one check per claimed layer. **Substantive.**

## Item 6: what the writer says it verified

The commit states:
- `prek` passed.
- JSON parses.
- One live run of the check script (the up-to-date branch only).
- Sandbox enforcement was **not** exercised.

There is no run of `claude-iso.sh`, no run of the install commands, and no bad case shown failing (for example, a credential read being denied). I'm noting this as stated; I did not run anything to supply it.

## Item 7: siblings of the change

- **7a. The version strings live in more places than the bump procedure names.** They appear in five places: `pinned-versions.toml` `version`, the toml's `install.*` strings (`:62-65,78-80,100-101`), `secure-agent-setup.md:96-136`, and `tools/agent-isolation/README.md:36-37`. The bump procedure (`secure-agent-setup.md:151-155`, the footer of `check-tool-updates.sh`, and `pinned-versions.toml:37-40`) names only `version`/`released`/`pinned_at` and the doc's install block. **Request:** list every site, or derive them all from the toml. **Substantive.**
- **7b. `AGENTS.md` lists the other tools and root docs but not the new ones.** "Repo-root files" (`AGENTS.md:79-86`) leaves out `secure-agent-setup.md`, and "References" (`AGENTS.md:1122-1132`) lists `tools/github|gmail|vulnogram|cve-org/` but not `tools/agent-isolation/`. **Substantive.**
- **7c. The `curl` deny and the domain allowlist conflict with other readers of the same setting.** See 2c and Item 1 finding 7. Of the 4 `curl` recipes in `tools/` and `.claude/skills/`, I read all 4.
- **7d. A clean exit on the sourced path closes the user's terminal.** When `claude-iso.sh` is sourced (the documented use), `exec` at `:111` replaces the user's interactive shell: my bash run never reached the following `echo`. So the terminal closes when `claude` exits. **Request:** run `env -i …` in a subshell, or drop `exec` on the sourced path. **Substantive.**

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Header usage injects credentials that are actually stripped | Substantive | `tools/agent-isolation/claude-iso.sh:39` | 1 |
| Comment claims invocation-line vars are preserved, then retracts it | Substantive | `tools/agent-isolation/claude-iso.sh:85` | 1 |
| `pinned_at` said to be used by the check script; it is not | Substantive | `tools/agent-isolation/pinned-versions.toml:42` | 1 |
| Comment describes a `<` comparison the code does not do | Substantive | `tools/agent-isolation/check-tool-updates.sh:161` | 1 |
| "Three-layer" heading over four layers | Substantive | `secure-agent-setup.md:69` | 1 |
| Passthrough list in doc incomplete | Substantive | `secure-agent-setup.md:264` | 1 |
| Allowlist missing `cveawg.mitre.org`; curl-deny rationale doubtful | Substantive | `secure-agent-setup.md:201` | 1 |
| `/schedule` called a framework command | Substantive | `secure-agent-setup.md:163` | 1 |
| socat release date conflicts with the commit's script output | Substantive | `tools/agent-isolation/pinned-versions.toml:69` | 1 |
| Pinned apt/dnf forms unverified on any distro release | Substantive | `secure-agent-setup.md:113` | 2 |
| gh/`apache-steward` deny/allow split unverified | Substantive | `.claude/settings.json:9` | 2 |
| `Bash(curl *)` deny breaks the framework's own curl recipes | Substantive | `.claude/settings.json:51` | 2 |
| Auto-update not disabled; claude-code pin does not hold | Substantive | `tools/agent-isolation/pinned-versions.toml:83` | 2 |
| Sourcing from `~/.zshrc` fails with "bad substitution" | Substantive | `secure-agent-setup.md:252` | 2 |
| Scheduled routine cannot reach the socat host | Substantive | `secure-agent-setup.md:171` | 2 |
| Check script untested on macOS and on the candidate branch; >20-release window | Substantive | `tools/agent-isolation/check-tool-updates.sh:92` | 3 |
| Adopter copy overwrites an existing settings file | Substantive | `secure-agent-setup.md:289` | 3 |
| No timeout on upstream `curl` calls | Substantive | `tools/agent-isolation/check-tool-updates.sh:68` | 3 |
| AGENTS.md instruction fires on sessions with no tracker content | Substantive | `AGENTS.md:312` | 3 |
| Shell scripts have no test and no shellcheck hook | Substantive | `.pre-commit-config.yaml:26` | 3a |
| Positional references ("step 5 above") | Taste | `secure-agent-setup.md:174` | 4 |
| One catch-all failure message; empty manifest exits 0 | Substantive | `tools/agent-isolation/check-tool-updates.sh:153` | 5 |
| Verification block tests weaker properties than claimed | Substantive | `secure-agent-setup.md:313` | 5 |
| Bump procedure misses version sites | Substantive | `secure-agent-setup.md:151` | 7 |
| AGENTS.md file lists omit the new doc and directory | Substantive | `AGENTS.md:79` | 7 |
| `exec` on the sourced path closes the user's shell | Substantive | `tools/agent-isolation/claude-iso.sh:111` | 7 |

I could not run the repository's `prek` gate (it isn't installed, and fetching hooks needs network), and I did not probe the real credential paths for finding 2b.
