# Final review of `2efe27f..HEAD`: commit 1b569a8, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)"

There was no separate task statement, so the claimed cases come from the commit message alone. I loaded `final-review`, `test-authoring` and `english-developer-style` from the given folder.

The change has two shell scripts, which count as code; everything else is docs or configuration and was reviewed through the "change with no code" analogues (§2a). I ran the drift script with `comment-drift.py 2efe27f HEAD`. It printed nothing: it does not parse shell, TOML, JSON or Markdown, so I checked every comment by hand. No previous report exists.

Tool runs:
- `bash -n` and `shellcheck` on both scripts: both clean.
- `claude-iso.sh` against a stub `claude` that prints its environment, run in bash and in zsh.
- `check-tool-updates.sh` with a `python3` stub that lacks `tomllib` and a `curl` stub that fails.
- BSD `/bin/date -d`: `illegal option -- d`.

## Item 1: comments consistent with the code and with each other

**Findings:**
- **Example commands that don't work.** `tools/agent-isolation/claude-iso.sh:40-41` gives `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` as the way to pass in one credential. The code drops both variables unless they are named in `CLAUDE_ISO_ALLOW`. Verified: with `GH_TOKEN=x AWS_PROFILE=ro` the stub saw neither. Only the form in `secure-agent-setup.md:273` is correct.
- **A comment that contradicts the code.** `claude-iso.sh:85-90` says any variable set on the same line as `claude-iso` is kept. It isn't.
- **A comment that argues with itself.** `claude-iso.sh:104-109` ("we can tell … well, actually we can't") is a draft of reasoning with no code under it.
- **A comparison that doesn't exist.** `check-tool-updates.sh:163-167` says "plain `<` does the right thing". The code has only `==`, so any difference, including an upstream release older than the pin, prints "upgrade candidate". `secure-agent-setup.md:145-147` repeats "newer than the pin".
- **A field the script never reads.** `pinned-versions.toml:42-43` says "The check script uses this [`pinned_at`] as the minimum age". `read_pinned` reads only `tools.*`.
- **Wrong reason for `--no-save`.** `pinned-versions.toml:97-99` says `--no-save` keeps a global install from changing a project's lockfile. `-g` never touches a project lockfile, so the flag is a no-op here.
- **Wrong layer count.** The heading `secure-agent-setup.md:69` (and its TOC entry, line 7) says "Three-layer defence". The table under it, and the commit message, list four layers (0–3).
- **Incomplete "only" list.** `secure-agent-setup.md:264-267` says the wrapper passes "only" a list of variables. The code also passes `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, and passes four named `XDG_` variables rather than all of `XDG_*`.
- **`/schedule` is described wrongly.** `secure-agent-setup.md:163` calls `/schedule` "the framework's" slash command; it is Claude Code's. Lines 171-175 say the scheduled agent "runs in the same secure setup". `/schedule` creates a cloud routine: no `claude-iso`, no host bubblewrap, none of the pinned tools.
- **"Any" is too strong.** `secure-agent-setup.md:229-230` says the `gh api` rules catch "any non-default-method" and "any payload-bearing" call. `Bash(gh api * -X *)` needs text between `api` and `-X`, so `gh api -X POST repos/…` (flag first) does not match. `--method`, `--field`, `--raw-field` and `--input` don't match either.
- **Probably false rationale (taste).** `secure-agent-setup.md:218` gives "network egress via Bash bypasses the sandbox proxy" as the reason for denying `curl`. As far as I know the sandbox proxy applies to Bash subprocesses; that is what `allowedDomains` does. I couldn't fetch the docs, so this stays taste.

## Item 2: claimed cases covered

**Cases claimed in the commit message, and what checks them:**

| Claimed case | What checks it |
|---|---|
| Layer 0 removes credential-shaped variables | None. My stub run shows it removes them, and also removes the variables the header comment says it keeps. |
| Layers 1–3 (sandbox, deny, ask) are enforced | None. The commit defers this to "the first invocation after merge". |
| The check script is side-effect free and lists only candidates past the cooldown | The writer ran it once; the platform is not stated. |
| Every pin is at least 7 days old | Matches the manifest dates: claude-code `2026-04-22` against `pinned_at` `2026-04-29` is exactly 7 days. |
| Each pin has a correct `released` date | **Contradicted.** The commit's own run shows socat `UPSTREAM@ 2026-02-12` against the manifest's `released = "2026-03-13"`. Nothing defines where `released` comes from, and the doc table repeats the unverified date. |
| README and AGENTS.md link the new doc | `README.md:161` and `AGENTS.md:316` both do. |

**Commands the change tells people to run:**

| Command | Promised outcome | What runs it | Finding |
|---|---|---|---|
| `bash …/check-tool-updates.sh` | A status table | none | Needs GNU `date -d` and `tac`. On macOS, BSD `date -d` fails, so every socat version is skipped and the row reads "upstream lookup failed (rate limit / network)". It also needs Python 3.11 or later for `tomllib`; on macOS 3.9, run with a stub, it printed an empty table and **exited 0**. Under the repo's own sandbox, `www.dest-unreach.org` is not in `allowedDomains`, so the socat lookup always fails, including in the `/schedule` flow. |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` | Installs the pins | none | The outcome depends on those exact upstream versions being in the host's configured repos. I believe current Debian stable and Ubuntu LTS ship older versions, which would make apt fail with "version not found". I couldn't verify this offline. |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | Installs the pins | none | Same dependency on what the repos carry. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | Pins Claude Code | none | Claude Code updates itself by default. Nothing in `.claude/settings.json` turns that off (for example `env.DISABLE_AUTOUPDATER`), and `claude-iso` would strip that variable anyway. The pin doesn't hold, which is the very drift `pinned-versions.toml:86-93` gives as the reason for pinning. |
| `source …/claude-iso.sh` from `~/.bashrc` or `~/.zshrc`, then `claude-iso` | Starts Claude with a clean environment | none | **zsh:** verified `claude_iso_main:37: bad substitution` (bash-only `${!var}`). zsh is the default macOS shell. **bash:** the function ends in `exec`, so when sourced it replaces the user's interactive shell. Verified: the stub ran, and an `echo` after `claude-iso` never ran, so the terminal closes when Claude exits. |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` | Passes `GH_TOKEN` through | none | Verified it works (run directly with bash). |
| The three "Verification" commands | Each is denied | none | Not run; depends on bubblewrap on the host. |
| `/schedule weekly run …` | Weekly list of candidates | none | See Item 1: it runs remotely, and the socat lookup fails under the allowlist anyway. |

Every hunk is claimed by a sentence of the commit message.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the platforms, shells and pre-existing state the change claims to support.

**Partitions with no evidence:**
- macOS for the check script (see Item 2).
- zsh for the wrapper (see Item 2).
- Sourcing the wrapper versus running it directly: only the direct form works without killing the shell.

**Values users already pass.** `claude-iso` now sits in front of every variable users export. It drops, with no sentence in the doc saying so:
- `HTTPS_PROXY` and `NO_PROXY`
- `NODE_EXTRA_CA_CERTS`
- `TMPDIR`
- `CLAUDE_CONFIG_DIR`
- `ANTHROPIC_BASE_URL`
- `CLAUDE_CODE_USE_BEDROCK` or `CLAUDE_CODE_USE_VERTEX`, and the cloud credentials those need

Users behind a proxy, or who sign in through API keys, Bedrock or Vertex, get a session that doesn't work. Request: list these in the doc with the `CLAUDE_ISO_ALLOW` remedy, or pass the non-secret ones through.

**Pre-existing state: the credential split.** The doc says the Bash sandbox can read `~/.config/gh/` while the Read tool cannot (`secure-agent-setup.md:236-241`). This review session runs under this exact settings file, and its sandbox lists `~/.config/gh` both in `denyRead` and in "allow within deny". So Claude Code merges `permissions.deny` Read rules into the sandbox's deny list, and whether `gh` still works depends on which list wins. Nobody has run this. Request: run `gh auth status` from inside a session with this config, on Linux and on macOS. I did not read the credential directory myself.

**Limits:** the `curl` calls in `check-tool-updates.sh:68,90,96` have no `--max-time`. A peer that stops answering hangs the weekly run with no output. The socat loop sends one HEAD request per version, one after another.

**Fault reporting:** every lookup failure prints the same "rate limit / network" text, whatever the cause: BSD `date`, missing `tac`, or a manifest tool with no `case` branch (lines 145-147, 150-153).

## Item 3a: level, placement, and the environment

- The wrapper's environment filtering can be observed in one process with a stub `claude`, as I did, but there is no test.
- `.pre-commit-config.yaml` has ruff, mypy and pytest hooks for the two Python tools, and nothing (shellcheck, `bash -n`, a stub-based test) for the new `tools/agent-isolation/*.sh`.
- Placement under `tools/<name>/` with a README matches the sibling tools.

## Item 4: names by content, not by position

- `secure-agent-setup.md:174` says "per step 5 above". Name the step: "the bump-PR step".
- No other references by position.

## Item 5: the failure report

- `check-tool-updates.sh`: when `read_pinned` fails, the table is empty and the exit status is 0 (verified). A scheduled run reports success with no rows.
- The lookup-failure message names a cause (rate limit or network) that is often wrong (see Item 3).

## Item 6: what the writer says it verified

The commit states:
- `prek` passes.
- One run of the check script, platform not stated.
- The JSON parses.

There is no evidence that any deny or ask rule fails when it should: the "Verification" block was not run, and the commit says sandbox enforcement is untested. There is also no run of the wrapper.

## Item 7: siblings of the change

These lists enumerate the same set and don't name the new files:
- **`AGENTS.md`, "Repo-root files" list:** names `README.md`, `how-to-fix…` and `new-members-onboarding.md`, but not `secure-agent-setup.md` or `.claude/settings.json`.
- **`AGENTS.md:1124-1132`, References list of `tools/` adapters:** lists github, gmail, vulnogram and cve-org, but not `tools/agent-isolation/`.
- **`CONTRIBUTING.md:39-49`, "Root docs" list:** doesn't name `secure-agent-setup.md`.

The ask rules have siblings too. They cover `gh pr create`, `edit` and `merge`, but not:
- `gh pr comment`, `gh pr review` and `gh pr close`
- `gh issue reopen`
- `gh api -X …` with the flag first
- `git -C <dir> push`

All of these are writes others can see, which the doc's Layer 3 says need an explicit yes.

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | Sourced wrapper `exec`s and replaces the user's shell | Substantive | `claude-iso.sh:111,117` | Run `exec` in a subshell for the sourced function (`( claude_iso_main "$@" )`), or have the function call the script |
| 2 | Wrapper breaks under zsh, though the doc says to source it from `~/.zshrc` | Substantive | `claude-iso.sh:80,98`; `secure-agent-setup.md:252` | Make it POSIX/zsh-safe, or ship it as an executable and stop recommending `source` |
| 3 | Header usage lines and comment say variables on the invocation line pass through; they don't | Substantive | `claude-iso.sh:40-41,85-90,104-109` | Use the `CLAUDE_ISO_ALLOW` form; delete the self-contradicting comment |
| 4 | Check script fails silently (exit 0, empty table) without `tomllib`, and mislabels every failure as rate limit or network | Substantive | `check-tool-updates.sh:115-123,150-153` | Check the Python version up front, exit non-zero when parsing fails, report the actual cause |
| 5 | socat lookup is GNU-only (`date -d`, `tac`), so it always fails on macOS | Substantive | `check-tool-updates.sh:92,101,103` | Use the Python already in use for date parsing and ordering, or state Linux-only |
| 6 | socat lookup host is outside the repo's own `allowedDomains`, so the documented `/schedule` flow always fails for socat | Substantive | `.claude/settings.json:20-35`; `check-tool-updates.sh:90` | Add the host, or document the expected failure |
| 7 | The documented `<` comparison doesn't exist; an older upstream release shows as an upgrade | Substantive | `check-tool-updates.sh:160-169`; `secure-agent-setup.md:145-147` | Compare versions, or correct the comment and the doc |
| 8 | Claimed `pinned_at` use by the script doesn't exist | Substantive | `pinned-versions.toml:42-43` | Fix the comment, or implement the check |
| 9 | Claude Code pin isn't enforced because self-update stays on | Substantive | `.claude/settings.json`; `pinned-versions.toml:86-93` | Disable self-update in settings and pass the variable through the wrapper |
| 10 | `/schedule` described as the framework's command and as running "in the same secure setup" | Substantive | `secure-agent-setup.md:163-175` | Say it is a Claude Code cloud routine, and say what isolation it actually gets |
| 11 | `gh api` ask patterns miss flag-first and long-form flags; several write commands are not gated | Substantive | `.claude/settings.json:63-77`; `secure-agent-setup.md:229-230` | Add the patterns, or weaken "any" in the doc |
| 12 | The gh and apache-steward read split is unverified, and this session shows the deny merged into the sandbox | Substantive | `secure-agent-setup.md:236-241` | Run `gh auth status` inside a session with this config |
| 13 | No run of the deny, ask or sandbox rules, and no run of the wrapper | Substantive | commit "Test plan" | Run the "Verification" block on Linux and macOS and paste the output |
| 14 | apt and dnf version pins never run; may not exist in distro repos | Substantive | `secure-agent-setup.md:112-125`; `README.md:36` | Run them on the named distros, or document a source-build fallback |
| 15 | Socat `released` date contradicts the commit's own upstream date | Substantive | `pinned-versions.toml:69`; `secure-agent-setup.md:97` | Define the source of `released` and correct the date |
| 16 | Wrapper drops proxy, CA, `TMPDIR` and Bedrock/Vertex variables with no note | Substantive | `claude-iso.sh:56-74`; `secure-agent-setup.md:264-267` | Document them with the remedy, or pass the non-secret ones |
| 17 | "Three-layer" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | Rename it "Four-layer defence" and regenerate the TOC |
| 18 | Passthrough list in the doc differs from the code | Substantive | `secure-agent-setup.md:264-267` | List the code's variables exactly |
| 19 | `curl` calls have no timeout | Substantive | `check-tool-updates.sh:68,90,96` | Add `--max-time` |
| 20 | New files missing from the repo-root, tools and root-docs lists | Substantive | `AGENTS.md` repo-root files and References lists; `CONTRIBUTING.md:39-49` | Add the entries |
| 21 | No hook or test checks the new shell scripts | Substantive | `.pre-commit-config.yaml` | Add a shellcheck hook and a stub-`claude` test of the passthrough |
| 22 | `--no-save` rationale is false for `-g` | Substantive | `pinned-versions.toml:97-99` | Drop the flag or the rationale |
| 23 | "per step 5 above" refers to a step by position | Substantive | `secure-agent-setup.md:174` | Name the step by its content |
| 24 | `curl` deny rationale ("bypasses the sandbox proxy") is probably false | Taste | `secure-agent-setup.md:218` | Rationale: "removes a direct exfiltration command", or similar |

**Not checked:** no network run of the check script or the install commands, no run of the sandbox or permission rules under a real `claude` session, no fetch of the cited Claude Code docs, and no pass over the prose for style alone.
