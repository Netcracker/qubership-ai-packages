I'm reviewing the commit against the final-review form. I've read the diff and run the checks: `bash -n`, shellcheck, a JSON and TOML parse, and fake-`claude` runs of the wrapper under bash and zsh. Now I'm writing up the report.

# Final review: `2efe27f..1b569a8` (secure-agent setup)

**Task statement:** none was handed over. The claimed cases come from the commit message alone. This is a change with no tested code, so each item below uses the §2a analogue. The drift script was not run: the files are Markdown, JSON, TOML, and shell, and it has nothing to parse. I loaded `apm-authoring` and `english-developer-style`. `AGENTS.md` is an instruction file, so `apm-authoring` applies to that hunk only.

**Claimed cases (commit message):**
1. Four layers, each implemented.
2. The 7-day cooldown on every pin.
3. A side-effect-free check script.
4. A `/schedule` weekly routine.
5. The `README.md` and `AGENTS.md` links.
6. The pinned versions "all aged past 7 days".
7. The test plan: `prek`, the script run, the JSON parse, and the sandbox enforcement left unrun.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files)

1. `secure-agent-setup.md:7` and `:69` say "Three-layer defence", while the table at `:71-76` and the commit message list four layers (0–3). The TOC entry repeats it.
2. `claude-iso.sh:39-41` documents `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` as working. `:85-90` says a variable set on the invocation line is preserved. The code only keeps variables named in `CLAUDE_ISO_ALLOW`. I ran `GH_TOKEN=x claude-iso` and the token was dropped. With `CLAUDE_ISO_ALLOW=GH_TOKEN` it passed. Lines `:104-109` ("well, actually we can't reliably tell") then say the opposite of `:85-90`.
3. `secure-agent-setup.md:264-265` lists the passthrough set as `XDG_*`, `DISPLAY`, and so on. The code at `claude-iso.sh:56-74` also passes `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`. Four XDG variables, not a glob.
4. `secure-agent-setup.md:183-234` says "The full block is below". It drops `$schema` and the `git push --force*` entries that `.claude/settings.json:56-57` has. The doc's comment "including --force / --force-with-lease variants" describes entries the doc block no longer shows.
5. `check-tool-updates.sh:163-167` says "plain `<` does the right thing", but the code at `:160` uses `==`. The comment is stale. A pin that is newer than the latest aged release would also print "upgrade candidate".
6. `secure-agent-setup.md:214-215`, `:236-241`, and `:39-42` say the agent can't read `~/.config/gh` or `~/.config/apache-steward`, and that the setup "reduces it to the project tree". Those same directories are in `sandbox.filesystem.allowRead` (`settings.json:11-12`). `permissions.deny Read(...)` covers the Read tool. It does not cover `cat ~/.config/gh/hosts.yml` or `gh auth token` through the Bash tool, and the sandbox allows both. I could not check Claude Code's rule semantics offline, so this holds if the upstream docs match. The Gmail refresh token and the gh token are the two secrets the threat model names.
7. `settings.json` and `secure-agent-setup.md:218`: the comment "network egress via Bash bypasses the sandbox proxy" is false for a sandboxed Bash. The proxy filters it, and that is the premise of the network section.
8. `pinned-versions.toml:79-82`: "`--no-save` so the global install doesn't drift the local lockfile". `--no-save` has no effect on `-g`.
9. `check-tool-updates.sh:31-33` says the README suggests `/schedule weekly`. The README only mentions it in a usage comment. This holds loosely.
10. Narration: `claude-iso.sh:92` ("NB") and `:104-109` are thinking-aloud comments. Taste.

## Item 2: claimed cases covered

| Claim | Covered by | Result |
|---|---|---|
| Layer 0 clean env | `claude-iso.sh`, run by me | See findings A and B. |
| Layers 1–3 | Not run. The commit admits it. | Verification section at `:309-318` covers only 3 denials. |
| Every pin ≥7 days old | Nothing enforces it. | The script compares versions only, never `released` against `pinned_at`. |
| socat 1.8.1.1 released 2026-03-13 | The commit's own run printed UPSTREAM@ 2026-02-12 | The pin date contradicts the evidence in the commit message. |
| Check script works | One run on the author's host | Finding D. |
| `/schedule` weekly | Not run | Finding E. |
| Install commands (apt, dnf, npm) | Not run | Finding F. |
| Cooldown conventions in `pyproject.toml` and `dependabot.yml` | Checked | They hold (`exclude-newer = "7 days"`, `default-days: 7`). |
| `README.md#prerequisites-for-running-the-agent-skills` | Checked | The anchor exists at `README.md:136`. |

Commands the change tells someone to run, each with the job that runs the same form:
- `check-tool-updates.sh`: no CI job. It is the author's one run, on GNU `date` and `tac`.
- `apt-get install bubblewrap=0.11.1-*` and `socat=1.8.1.1-*`: `none`. The outcome depends on the distro archive. Debian and Ubuntu archives ship one fixed version per release, so a `0.11.1-*` pin probably errors "Version not found" on a stock release. Not run.
- `dnf install bubblewrap-0.11.1`: `none`. Same dependency on the repository.
- `npm install -g --no-save @anthropic-ai/claude-code@2.1.117`: `none`.
- `/schedule weekly run …`: `none`.

Hunks with no claiming sentence: none. Every file is listed in the commit message.

## Item 3: boundaries, partitions, and the negative control

- **Platforms.** Only the Linux/GNU host is evidenced. macOS has two defects, both with no stated acceptance:
  - `claude-iso.sh` fails in zsh (finding B). The doc names `~/.zshrc`, and zsh is the macOS default.
  - `socat_latest_aged` uses `date -d` and `tac`, which BSD lacks. Every lookup falls through to `|| continue`, then to the status text "upstream lookup failed (rate limit / network)". That message is wrong for a portability fault.
- **Faults of the check script.**
  - Rate limit: unauthenticated GitHub allows 60 requests per hour. The script fails soft with a message.
  - Python below 3.11 makes `tomllib` fail under `set -e`, and the script aborts with a traceback.
  - Allowlist: the script reaches `www.dest-unreach.org`, which is not in `sandbox.network.allowedDomains`. Inside the setup, the socat row always reports lookup failure.
- **Allowlist against the repo's own tools.**
  - `tools/cve-org/tool.md:28-66` tells the agent to `curl https://cveawg.mitre.org/api/cve/<id>`. The host is not allowed, and `Bash(curl *)` is denied. The `sync-security-issue` check-published recipe is broken inside this setup. The fix is a documented alternative path or an added host.
  - Not checked: `gh api … -X` and `-f` in the `ask` rules. A form like `gh api -X POST <url>` has no token before `-X`, so `gh api * -X *` likely misses it. `--method` and `--field` are not listed at all. That weakens layer 3. Taste or substantive; I label it substantive but low-confidence.
- **Existing state.** The setup never meets a pre-existing `.claude/settings.json` in an adopter repo (step 2 says "copy"). The doc has no merge instruction. Taste.
- **Pre-existing autoupdate.** The pin rationale (`pinned-versions.toml:88-94`) is that a silent autoupdate would change the security posture. No step disables auto-update (the setting or `DISABLE_AUTOUPDATER`), and `env -i` in the wrapper strips any such variable. The pin protects only the first install. I could not confirm the exact setting name offline.
- **Control.** The verification section has only denials. Add one positive control that `gh` and `git` still work, and one `ask` check.

## Item 3a: level, placement, and the environment

- **Offline check.** `bash -n` and `shellcheck` are clean on both scripts. The JSON and TOML parse.
- **No test.** No test or CI job runs either script. A check of `released ≤ pinned_at − 7 days`, which needs no network, would be the smallest test for the 7-day rule. The wrapper's behavior (finding A) can be tested in-process with a stub `claude` on `PATH`, as I did.
- **Layout.** The new directory matches its siblings (`tools/<name>/` with a README). The scripts are executable (`100755`).
- **Registry.** `AGENTS.md` and `README.md` list tool adapters, and none lists `tools/agent-isolation/` or `secure-agent-setup.md`. See Item 7.

## Item 4: names by content, not by position

none. Headings and cross-references use content ("Install commands", "Adopter setup"). "Layer 0–3" is a stable label, not an ordinal into a list. The only fault is the "Three-layer" count, filed under Item 1.

## Item 5: the failure report (analogue: what a rule tells the reader to look at)

- The verification block (`:313-318`) comments only "→ permission denied" and "→ empty". It does not say what a leaked result looks like, beyond the closing sentence. The `curl` line is blocked by two mechanisms (`deny` and the allowlist), so it cannot tell which layer failed. Use a host that is on the allowlist, or `wget`, to isolate the `deny` rule.
- The check script's one failure message covers rate limit, network, and portability, so it hides the cause. The `|| true` swallows the exit code.

## Item 6: what the writer says it verified

The commit lists three checks:
- `prek run --all-files` passes.
- The check script ran end-to-end.
- The JSON parses.

It states that sandbox enforcement is untested. It has no bad case for the wrapper and none for the cooldown rule. I did not run the suite. The commit's own script run shows socat dates 2026-03-13 against 2026-02-12 and prints "✓ up to date", so the evidence it offers contradicts the manifest.

## Item 7: siblings of the change

- **Added members, by name.** `grep -n 'agent-isolation\|secure-agent'` over the Markdown files other than the new ones finds none outside the `AGENTS.md` and `README.md` hunks. The `AGENTS.md` "Repository purpose" list of repo-root files and "References" list of `tools/<name>/` do not name `secure-agent-setup.md` or `tools/agent-isolation/`. `AGENTS.md:7`–adjacent lists stay at the old size. Substantive (low).
- **The same defect, other paths.**
  - The `exec` defect also hits the "Or invoke directly" form. That form is fine: `exec` in a script is expected there.
  - The `date -d` defect occurs at `check-tool-updates.sh:101` and `:103`, both in the socat function.
  - `AGENTS.md` and the repo guidance say "project-agnostic" and `b73e240` dropped project remnants. The docs hard-code `/path/to/airflow-steward/` (`:253`, README `:35`), which is the repo's current name, so this is fine now. Taste.

## Added instructions (`AGENTS.md:312-319`)

`Added instructions: 1, 1 row.`

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | an agent already started without the wrapper, or in a session on another OS (macOS/zsh, where `claude-iso` fails) | tells the user to restart in `claude-iso`, which errors in zsh | "where the host is Linux with bash, otherwise report the limit and stop" |

Not findings: `AGENTS.md:315-319`, because the surrounding sentence already bounds it to this repository's skills.

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| A | `claude-iso` called from a sourced function does `exec`, so it replaces the user's interactive shell. When claude exits, the terminal closes. Confirmed by running it: the line after `claude-iso` never ran. | Substantive | `claude-iso.sh:111,117` | Run `env -i … "$claude_bin" "$@"` without `exec` in the function form, or use a subshell. Keep `exec` only for the script form. |
| B | The script uses `${!var-}`, which fails in zsh (`bad substitution`, confirmed). The doc names `~/.zshrc`. | Substantive | `claude-iso.sh:79,98`; `secure-agent-setup.md:249-254` | Use portable indirect expansion, or say bash only and give a zsh form. |
| C | Invocation-line variables are documented as preserved but dropped. The comments at `:85-90`, `:39-41`, and `:104-109` contradict the code and each other. | Substantive | `claude-iso.sh:39-41,85-109` | Document `CLAUDE_ISO_ALLOW` only, delete the contradicting comments. |
| D | The check script's socat lookup needs a host that `allowedDomains` lacks, so it always fails inside the setup. It also uses GNU-only `date -d` and `tac`, so on macOS the failure reads as "rate limit / network". The pin date for socat (2026-03-13) contradicts the commit's own run (2026-02-12). | Substantive | `check-tool-updates.sh:85-108,153`; `pinned-versions.toml:78`; `settings.json:18-33` | Add the host or drop socat from the script, distinguish the failure causes, and correct or verify the `released` date. |
| E | "The scheduled agent runs in the same secure setup" is unproven. A `/schedule` routine runs as a cloud agent, not under this local `settings.json`. | Substantive | `secure-agent-setup.md:171-175` | State where the routine runs, or drop the sentence. |
| F | Install commands were not run. A pin like `bubblewrap=0.11.1-*` probably does not exist in stock apt archives. `--no-save` does nothing for `-g`. | Substantive | `secure-agent-setup.md:110-137`; `pinned-versions.toml:62,79-82` | Run each on a named distro, or state which repository provides the version. |
| G | Nothing enforces "every pin aged ≥7 days". The cooldown rule has no detection. | Substantive | `check-tool-updates.sh:160`; `pinned-versions.toml:4-28` | Compare `released` with `pinned_at` offline, and fail on <7 days. |
| H | The doc's "the agent can't read gh and Gmail credentials" is contradicted by the Bash path. The residual-risks section omits it and `SSH_AUTH_SOCK`. | Substantive (rests on upstream semantics) | `secure-agent-setup.md:39-42,214-215,236-241,325-348`; `claude-iso.sh:73` | Say what the Bash tool can read, or move those directories out of `allowRead`. Add both items to residual risks. |
| I | `cveawg.mitre.org` is unreachable and `curl` is denied, so the cve-org recipe breaks inside this setup. | Substantive | `settings.json:18-33,38-39`; `tools/cve-org/tool.md:28-66` | Add the host, or give a non-`curl` form. |
| J | "Three-layer" heading with four layers. | Substantive | `secure-agent-setup.md:7,69` | Rename to four layers, regenerate the TOC. |
| K | The doc's JSON block differs from the file. The wrapper passthrough list is misstated. The stale `<` comment and the false "bypasses the sandbox proxy" comment. | Substantive | `secure-agent-setup.md:183-234,264`; `check-tool-updates.sh:163`; `:218` | Align or drop the claims. |
| L | The pin's rationale (autoupdate) has no step to disable auto-update. | Taste | `pinned-versions.toml:88-94` | Add the step or reword the rationale. |
| M | `gh api -X`, `--method`, `--field` ask patterns can be bypassed by flag position. | Taste (low confidence) | `settings.json:70-76` | Test the patterns, or use broader ones. |
| N | `AGENTS.md` repo-root and tools lists omit the new doc and directory. | Taste | `AGENTS.md` | Add one line each. |

**Not checked:** I did not run the test suite or `prek`. I did not exercise the sandbox, the `permissions` rules, or the install commands, and I could not read Claude Code's upstream documentation offline. Findings H and M rest on how those rules behave there. No prose-style pass was done beyond places where a sentence reads wrongly.
