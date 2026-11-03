# Final review: `2efe27f..1b569a8` (one commit, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

**Inputs.** I had no separate task statement, so the claimed cases in item 2 come from the commit message alone. The drift script exited 0 and printed nothing. It doesn't parse shell, Markdown, JSON, or TOML, so I checked the shell scripts by reading and running them. For the docs, the config, and the AGENTS.md addition I used the §2a analogues, and each item says which one applies. Skills loaded: `english-developer-style`, `apm-authoring` (for the AGENTS.md instruction) and `test-authoring` (for the scripts). Nothing was changed or committed.

## Item 1: comments consistent with the code and with each other
Analogue for the docs: statements one file makes about another file. For the scripts: the comments read against the code.

- **`tools/agent-isolation/claude-iso.sh:40-41`.** The usage says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` inject a credential. The code drops both unless the variable is named in `CLAUDE_ISO_ALLOW`.
  - Run: `GH_TOKEN=x bash claude-iso.sh | grep -c GH_TOKEN` printed `0`.
  - A reader would think the token reached the session.
  - Request: change both examples to the `CLAUDE_ISO_ALLOW=...` form that `secure-agent-setup.md:273` already uses.
- **`claude-iso.sh:84-90` and `:102-108`.**
  - The first block says a variable "is present in our env exactly when it was passed explicitly". That is false: anything exported in the parent shell is present too.
  - The second block argues with itself ("well, actually we can't reliably tell…") and has no code under it.
  - Request: replace both blocks with one sentence on `CLAUDE_ISO_ALLOW`.
- **`check-tool-updates.sh:163-167`.** The comment describes a lexical `<` comparison. The code at `:160` only tests equality.
  - Any upstream version that differs from the pin is reported as "upgrade candidate". That includes an older one, which happens whenever the pin is newer than the newest release past the cooldown.
  - Request: add the version comparison the comment describes, or fix the comment and give the "older than pin" outcome its own status.
- **`pinned-versions.toml:42-43`.** The comment says "The check script uses this [`pinned_at`] as the minimum age…". `read_pinned` reads only `version` and `released`. Nothing reads `pinned_at`, and nothing checks that `released` is at least 7 days before it.
  - Request: drop the sentence, or make the script check it.
- **`pinned-versions.toml:84-92` (claude-code `purpose`).** It justifies the pin by "a silent autoupdate…". Nothing in the setup turns off Claude Code's autoupdater: no `DISABLE_AUTOUPDATER` and no `autoUpdates` in `.claude/settings.json`. `claude-iso` also strips `DISABLE_AUTOUPDATER` if the user exports it. So the npm pin lasts until the first autoupdate.
  - Request: turn off autoupdate in the setup, for example through the `env` key of `settings.json` or the passthrough list, or drop the claim.
- **`secure-agent-setup.md:69` (and its TOC entry).** The heading says "Three-layer defence". The table under it has four rows (0–3), and the commit message says "four layers".
  - Request: make the heading match the table.
- **`secure-agent-setup.md:264-267`.** The passthrough list leaves out `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`. It also writes `XDG_*`, while the script passes only four named `XDG_` variables (`claude-iso.sh:57-74`).
  - Request: list exactly what the script passes.
- **`secure-agent-setup.md:229-230` and `:76`.** The comments say "any non-default-method API call" and "any payload-bearing API call", and layer 3 claims it confirms "visible-to-others writes". None of the `ask` patterns match:
  - `gh api --method POST …` or `gh api -X POST <path>` (flag before the path);
  - `--field`, `--raw-field` or `--input`;
  - `gh pr comment`, `gh pr review`, `gh pr close`, `gh issue reopen`, `gh release edit/delete`, `gh label …`.
  - Request: add these patterns, or narrow the claims to what the patterns match.
- **`secure-agent-setup.md:163` and `:171`.** The doc calls `/schedule` "the framework's" slash command; it is built into Claude Code. It also says the scheduled agent "runs in the same secure setup". That routine is not started through `claude-iso` or the pinned local tools, and nothing in the change shows which settings it gets.
  - Request: correct the attribution, and state the routine's environment or drop the claim.
- **Taste:**
  - `pinned-versions.toml:97-99`: `--no-save` on a global npm install protects no project lockfile.
  - `secure-agent-setup.md:218`: the claim that Bash `curl` "bypasses the sandbox proxy" is unsupported. With the sandbox on, its egress goes through the proxy.
  - `pinned-versions.toml:68`: socat `released = 2026-03-13`, but the commit's own check run shows `UPSTREAM@ 2026-02-12` for the same version.

## Item 2: claimed cases covered
Claimed cases, from the commit message:

| Claim | Covered by |
| --- | --- |
| Layer 0: strip credential-shaped env vars | `claude-iso.sh`; works in bash when run directly (my run) |
| Layers 1–3 in `settings.json` | the file; JSON parses. The commit says enforcement was never exercised |
| 7-day cooldown pins | the TOML manifest; nothing enforces it (see item 1, `pinned_at`) |
| Side-effect-free check script that surfaces aged upgrade candidates | the script; the commit shows only the "up to date" run |
| README and AGENTS.md links | present; the anchors resolve |

Commands the change tells someone to run:

| Command | Promised outcome | What runs it | Finding |
| --- | --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:113-117`, tools README `:36`) | pinned install | none | **Substantive** (below) |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (`:122-125`) | pinned install | none | **Substantive** (below) |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (`:136`) | a pin that holds | none | **Substantive**: autoupdate is not turned off (item 1) |
| `source …/claude-iso.sh` from `~/.zshrc` (`:252`) | `claude-iso` usable | none | **Substantive** (below) |
| Same, from `~/.bashrc`, then `claude-iso` | starts a session | none | **Substantive** (below) |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (`:273`) | token passed through | my run in bash: works | none |
| `bash check-tool-updates.sh` (`:144`, tools README) | status table | the author's run, platform not stated | **Substantive** (below) |
| `/schedule weekly run …` (`:167`) | weekly candidates | none | **Substantive** (below) |
| Verification block (`:315-317`) | three denials | none ("first invocation after merge will exercise it") | **Substantive** (below) |

- **apt and dnf.**
  - The outcome depends on the distro archive carrying exactly these upstream versions. Debian and Fedora version strings also carry a packaging revision and sometimes an epoch.
  - No distro release is named, and where the archive lacks the version, apt and dnf refuse the install.
  - Request: run each form on a named distro release, or document the from-source path as the pinned one.
- **Sourcing from `~/.zshrc`.** The script uses bash-only `${!var}` and `BASH_SOURCE`. My run under `zsh -c 'source …; claude-iso'` failed with `claude_iso_main:37: bad substitution`. zsh is the macOS default shell, and the doc supports macOS.
- **Sourcing from `~/.bashrc`.** The function ends in `exec env -i …` (`:111`). When it is called from the interactive shell, `exec` replaces that shell, so the terminal closes when `claude` exits.
  - Run: `bash -c 'source claude-iso.sh; claude-iso >/dev/null; echo AFTER'` never printed `AFTER`.
  - Request: run `exec` in a subshell when sourced (`( exec env -i … )`), and support zsh or say the wrapper is bash-only.
- **`check-tool-updates.sh`.** The script needs GNU `date -d` (`:101`) and Python ≥ 3.11 for `tomllib` (`:117`).
  - On macOS, BSD `date -d` fails ("illegal option -- d"), so every socat tarball hits `continue`. The row always reads "upstream lookup failed (rate limit / network)".
  - With Python < 3.11, `read_pinned` fails inside `< <(…)`, which `pipefail` does not catch. The script prints the header and no rows, then exits 0.
  - Inside the change's own sandbox, `www.dest-unreach.org` is not in `allowedDomains`, so the socat lookup fails there too.
  - Request: a run on macOS and inside the sandbox. Use portable `date` parsing (or Python), state or check the Python version, and add the socat host to `allowedDomains` or say that lookup needs to run outside the sandbox.
- **`/schedule` routine.**
  - The outcome depends on the routine's network allowlist and the platform it runs on. Neither is shown, and the socat host is blocked under the setup the doc says the routine shares.
- **Verification block.** `echo $AWS_ACCESS_KEY_ID → empty` depends on whether Claude Code's Bash tool rebuilds its environment from the user's shell rc. Threat case 3 (`:54-57`) says these variables "live in `~/.bashrc`". Nothing shows the result.
  - Request: run the three commands on Linux and on macOS, starting from a parent shell and rc file that set a canary value (see item 5).
- **Reverse reading.**
  - `.claude/settings.json` applies to every contributor's session in this repo. Its `Bash(curl *)` deny and its domain list change how existing skills behave (item 7).
  - No sentence of the commit claims or checks that effect. Request: a sentence that claims it, with a run of the affected skill steps, or the fix in item 7.

## Item 3: boundaries, partitions, and the negative control
Analogue for the config and docs: claimed partitions and the control that should stay working. The scripts are covered as written.

- **Partitions with no evidence.**
  - Check script: only "up to date" was run. Not run: "upgrade candidate", "older than pin" (misreported, item 1) and "lookup failed".
  - `claude-iso`: sourced vs executed, bash vs zsh, with vs without `CLAUDE_ISO_ALLOW`. None was run by the writer; my runs found the two defects in item 2.
- **Negative control missing.** The Verification block checks only denials. Nothing checks that the work the setup must allow still runs under it. It doesn't (item 7):
  - `sync-security-issue:873` and `tools/cve-org/tool.md:66,90` run `curl` against `cveawg.mitre.org`. Both the `curl` deny and the domain list block that.
  - `tools/gmail/ponymail-archive.md:139` falls back to `curl` against `lists.apache.org`.
  - `fix-security-issue` works in `environment.upstream_clone`, a clone outside the working directory, typically under `~/`. `denyRead: ["~/"]` with only `.` allowed blocks its reads, and the sandbox writes only to the working directory.
  - Request: add a positive control run covering each skill's network and filesystem steps, or widen the allowlists.
- **Values users already pass.** `env -i` now cuts off variables users set for Claude Code itself: `ANTHROPIC_API_KEY` (only login method for API-key users), `CLAUDE_CODE_USE_BEDROCK`/`_VERTEX`, `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`, `DISABLE_AUTOUPDATER`. The doc names none of them.
  - Request: list which of these to pass through `CLAUDE_ISO_ALLOW`, or add the non-secret ones to the passthrough list.
- **Instructions added to AGENTS.md:**

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a docs-only edit in this framework repo, which by `:59-70` holds no CVE content | a request to relaunch under `claude-iso` before a typo fix | "when the session reads `<tracker>` or `<security-list>` content" |

Not findings: none.

## Item 3a: level, placement, and the environment
None. Placement: `tools/agent-isolation/` matches the `tools/<name>/` layout. The scripts have no tests and the repo has no shell test harness. The comparison logic and the passthrough rule could be checked offline, but item 3 already asks for runs. `shellcheck` and `bash -n` are clean, and the JSON and TOML both parse. I could not run the gate, `prek run --all-files`: `prek` is not installed here.

## Item 4: names by content, not by position
- `secure-agent-setup.md:174` refers to "per step 5 above". Name the step by content ("the bump PR"). **Taste.**

## Item 5: the failure report
- **`secure-agent-setup.md:315-316`.**
  - `cat ~/.aws/credentials` also "fails" when the file doesn't exist.
  - `echo $AWS_ACCESS_KEY_ID` is also empty when the parent shell never set it.
  - So both checks pass on a machine where nothing was isolated, a weaker property than the one claimed.
  - Request: plant canaries first (a dummy `~/.aws/credentials`, and `AWS_ACCESS_KEY_ID=canary` exported in the parent shell), and expect "denied", not "fails".
- **`check-tool-updates.sh:152-154`.** Every lookup failure is labelled "rate limit / network", including a missing GNU `date`, a missing `tomllib` or a host blocked by the sandbox.
  - Request: print the failing step, or forward its stderr.

## Item 6: what the writer says it verified
- The writer ran the check script once, with every tool "up to date", and parsed the JSON.
- The writer says the sandbox enforcement is untested.
- Nothing shows any denial working, the Verification block run, `claude-iso` tested sourced or under zsh, or the setup run with the existing skills. Items 2 and 3 ask for those runs.

## Item 7: siblings of the change
Analogue: every place that lists the members of a set the change adds to.

- **Network allowlist vs hosts the skills reach.**
  - `cveawg.mitre.org` (cve-org adapter, `sync-security-issue`) and `www.dest-unreach.org` (this change's own script) are missing.
  - Hosts I found in skill and tool docs but didn't check for reachability: `services.nvd.nist.gov`, `www.apache.org`.
  - Request: add the hosts the skills use, or name the steps that will not work under the setup.
- **`Bash(curl *)` deny vs skills that tell the agent to run `curl`.** `sync-security-issue/SKILL.md:624,873`, `tools/cve-org/tool.md:66,90`, `tools/gmail/ponymail-archive.md:139`.
  - Request: put these on `ask`, or move the skills to a non-curl path (for example `gh api`).
- **Filesystem allowlist vs `environment.upstream_clone`** (`fix-security-issue/SKILL.md:110,275`). The clone sits outside `.`, so `fix-security-issue` cannot work in it.
- **`AGENTS.md:79-86`, "Repo-root files".** It does not list the new root file `secure-agent-setup.md`.
- **`AGENTS.md:1129-1132`, tool adapters in "References".** It lists `github`, `gmail`, `vulnogram` and `cve-org`, but not the new `tools/agent-isolation/`.
- **Passthrough list in the doc vs the script.** See item 1.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Usage shows credential injection without `CLAUDE_ISO_ALLOW`; it is dropped | Substantive | `claude-iso.sh:40-41` | 1 |
| Comment claims variables are present "exactly when passed explicitly", plus a block arguing with itself | Substantive | `claude-iso.sh:84-108` | 1 |
| Comment claims a `<` comparison; code only tests equality, so an older upstream shows as an upgrade | Substantive | `check-tool-updates.sh:160-167` | 1 |
| `pinned_at` said to be used by the script; never read | Substantive | `pinned-versions.toml:42-44` | 1 |
| Pin justified by blocking autoupdate; autoupdate not turned off, and `claude-iso` strips `DISABLE_AUTOUPDATER` | Substantive | `pinned-versions.toml:84-92` | 1 |
| "Three-layer defence" heading over a four-layer table | Substantive | `secure-agent-setup.md:69` | 1 |
| Passthrough list in the doc doesn't match the script | Substantive | `secure-agent-setup.md:264-267` | 1 |
| `gh api` "any non-default-method / payload-bearing" and "visible-to-others writes" claims are not met by the `ask` patterns | Substantive | `secure-agent-setup.md:76,229-230` | 1 |
| `/schedule` called the framework's, and said to run in the same setup | Substantive | `secure-agent-setup.md:163,171` | 1 |
| `--no-save` rationale, curl-bypasses-proxy claim, socat release date | Taste | `pinned-versions.toml:97`, `secure-agent-setup.md:218`, `pinned-versions.toml:68` | 1 |
| apt and dnf pinned installs never run on a named distro | Substantive | `secure-agent-setup.md:113-125` | 2 |
| Sourced from `~/.zshrc`, the wrapper fails with "bad substitution" | Substantive | `claude-iso.sh:37,116`; `secure-agent-setup.md:252` | 2 |
| Sourced in bash, `exec` replaces the interactive shell | Substantive | `claude-iso.sh:111,117` | 2 |
| Check script: BSD `date`, `tomllib` silent failure, socat host blocked by the sandbox | Substantive | `check-tool-updates.sh:90,101,117,173` | 2 |
| Verification block and `/schedule` routine never run | Substantive | `secure-agent-setup.md:167,313-317` | 2 |
| Effect of the dogfooded `settings.json` on existing skills not claimed | Substantive | `.claude/settings.json` | 2 |
| No positive control: existing skill steps blocked (curl, cveawg, upstream clone) | Substantive | `.claude/settings.json` | 3 |
| Claude Code's own auth, proxy, and autoupdate variables dropped by `env -i`, undocumented | Substantive | `claude-iso.sh:56-74` | 3 |
| AGENTS.md instruction fires on docs-only sessions | Substantive | `AGENTS.md:312` | 3 |
| "per step 5 above" | Taste | `secure-agent-setup.md:174` | 4 |
| Verification checks pass when nothing is isolated | Substantive | `secure-agent-setup.md:315-316` | 5 |
| Every lookup failure labelled "rate limit / network" | Substantive | `check-tool-updates.sh:152-154` | 5 |
| Allowlist and curl deny don't cover hosts and commands the skills use | Substantive | `.claude/settings.json` | 7 |
| New root doc and tool directory missing from AGENTS.md lists | Substantive | `AGENTS.md:79-86,1129-1132` | 7 |

I could not run the repository gate (`prek run --all-files`) because `prek` is not installed and there is no network. The drift script can't parse the change's file types, so I filled every item by hand.
