I filled the `final-review` form for the one commit `1b569a8` (`2efe27f..HEAD`). No task statement was supplied, so the claimed cases come from the commit message alone.

The change is mostly docs and config, plus two Bash scripts with no tests, so I used the §2a analogues for the docs and config. I applied items 1 and 5 to the script comments by hand. The drift script ran and printed nothing (exit 0) because it parses no shell, JSON, TOML or Markdown, so every comment check below is manual. I loaded `english-developer-style` and `test-authoring` from the given directory.

I ran these locally to check the claims:
- **`claude-iso.sh` with a stub `claude`:** run directly, then sourced in `bash` and in `zsh -f`.
- **BSD `date -d` on macOS.**
- **`bash -n` and `shellcheck`:** both clean.
- **Inspection:** `pyproject.toml`, `.github/dependabot.yml`, and the anchors the new files link to.

## Item 1: comments consistent with the code and with each other
Analogue: what each changed file says about itself, the other files, and the repository.

- **`claude-iso.sh:39-41` (header usage).** It says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` inject a credential. They don't: run with `GH_TOKEN=x AWS_PROFILE=ro bash claude-iso.sh`, the stub printed only `HOME`. Only the `CLAUDE_ISO_ALLOW` form passes them through, which is what `secure-agent-setup.md:273` correctly shows.
- **`claude-iso.sh:85-90`.** It says any variable set on the invocation line "is preserved", which is the same false claim. Lines 104-109 then take it back ("well, actually we can't reliably tell…"). That paragraph narrates the writer's doubt, describes no code, and contradicts the paragraph above it.
- **`pinned-versions.toml:42-43`.** It says "The check script uses this [`pinned_at`] as the minimum age…". `check-tool-updates.sh` never reads `pinned_at`: `read_pinned` prints only `version` and `released`.
- **`check-tool-updates.sh:163-167`.** The comment describes a lexical comparison where "plain `<` does the right thing". There is no comparison in the code. Any inequality, including an upstream version older than the pin, prints "upgrade candidate".
- **socat release date.** `pinned-versions.toml:69` and `secure-agent-setup.md:97` give `released = "2026-03-13"` for socat 1.8.1.1. The script's own output quoted in the commit message dates the same version `2026-02-12`. One of the two is wrong, and the manifest's cooldown promise rests on that date.
- **`secure-agent-setup.md:69` vs. `:71-76`.** The heading says "Three-layer defence", but the table lists four layers (0–3). The commit message also says four.
- **`secure-agent-setup.md:75`.** It says Layer 2 is "`permissions.deny` for Read/Edit/Write/Bash". `.claude/settings.json` has no Edit or Write rules.
- **`secure-agent-setup.md:236-241`.** It says Bash subprocesses can read `~/.config/gh/` and `~/.config/apache-steward/` but "the agent should never *see* it". Bash output goes into the agent's context, so `cat ~/.config/gh/hosts.yml` from the Bash tool would show the token. Either the split doesn't keep the token from the agent, or the sandbox also blocks Bash and `gh` breaks. Both outcomes contradict the paragraph.
- **`secure-agent-setup.md:229-230` and the same `ask` entries in `settings.json:74-76`.** The comments say "any non-default-method API call" and "any payload-bearing API call". The patterns `gh api * -X *` / `-f *` / `-F *` do not match:
  - `--method`, `--field`, `--raw-field`, or `--input`;
  - `-XPOST`;
  - a flag placed before the endpoint (`gh api -X POST repos/…`).
- **`secure-agent-setup.md:163`.** It calls `/schedule` "the framework's" slash command. It is Claude Code's built-in, and it creates cloud routines. Line 171 then says the scheduled agent "runs in the same secure setup the rest of the framework uses". A cloud routine doesn't run behind this host's `claude-iso` or bubblewrap.
- **`secure-agent-setup.md:181` ("The full block is below").** The block omits `$schema` and folds the two `--force` ask entries into one comment. (Taste.)
- **`settings.json` comment at `secure-agent-setup.md:218`.** "network egress via Bash bypasses the sandbox proxy" is a doubtful reason for denying `curl`: a sandboxed `curl` goes through the proxy. I couldn't settle this without the upstream docs. (Taste.)

## Item 2: claimed cases covered
Analogue: each claim, against the file or run that makes it true. No test code exists.

| Claim (commit message) | Where it holds | Covered? |
|---|---|---|
| Layer 0: clean env via `claude-iso.sh` | `claude-iso.sh` | Partly. The direct-run `env -i` path works. The sourced form, zsh, and the documented injection forms fail (items 1 and 3). |
| Layer 1: filesystem sandbox | `settings.json:3-17` | Present. Never exercised; the commit says so. |
| Layer 2: tool permissions | `settings.json:38-61` | Present for Read/Bash only (item 1). |
| Layer 3: confirm-on-write | `settings.json:62-77` | Partly; pattern gaps (item 1). |
| Every tool pinned ≥7 days before `pinned_at` | `pinned-versions.toml` | `claude-code` is at exactly 7 days. The socat date is contradicted (item 1). |
| The check script prints candidates aged past 7 days | `check-tool-updates.sh` | Only one claimed run, on Linux, with everything up to date. The candidate branch was never shown. |
| The check script is side-effect-free | `check-tool-updates.sh` | Holds by reading: it only runs `curl` GETs and HEADs and prints. |
| Weekly `/schedule` wiring surfaces candidates | `secure-agent-setup.md:161-175` | Not covered. A sandboxed run can't reach `www.dest-unreach.org`, which is not in `allowedDomains`, so socat always reports a failed lookup. |
| 2.1.123 not picked up (inside the cooldown) | Commit message | Rests on one claimed run. Nothing in the change records it. |
| README and AGENTS link to the new doc | `README.md:161`, `AGENTS.md:316` | Holds. The anchors exist. |

## Item 3: boundaries, partitions, and the negative control
- **Platform:**
  - The doc covers Linux and macOS, but on stock macOS `check-tool-updates.sh` can't run its socat lookup. BSD `date -d` fails (I confirmed `illegal option -- d`) and `/usr/bin/tac` doesn't exist.
  - Every socat lookup therefore prints "upstream lookup failed (rate limit / network)".
  - The only run shown is Linux.
- **Shell (zsh vs. bash):**
  - `secure-agent-setup.md:252` says to source the wrapper from `~/.zshrc`, and zsh is macOS's default shell.
  - Sourced in zsh, `claude-iso` fails with `claude_iso_main:37: bad substitution` because `${!var-}` is bash-only.
  - zsh also doesn't word-split `$CLAUDE_ISO_ALLOW`.
- **Invocation (sourced vs. direct):** the recommended form is to source the file and call the `claude-iso` function. That function calls `exec env -i …`, which replaces the user's interactive shell: in my run `SHELL-SURVIVED` never printed. Closing `claude` closes the terminal. Only `bash claude-iso.sh` behaves as intended.
- **Upstream release kinds:**
  - `gh_latest_aged` doesn't filter `prerelease` or `draft`, so a prerelease can come back as the upgrade candidate.
  - An upstream older than the pin also reports as a candidate (item 1).
- **Negative control:** nothing shows a denial actually happening. The Verification section lists commands that should fail, but the change doesn't report running them.
- **Pre-existing state:** "Adopter setup", step 2, says to copy `settings.json` into the adopter's tracker repo. It doesn't cover a repo that already has a `.claude/settings.json`, or a `settings.local.json` that adds allow rules. The copy overwrites the first, and the second loosens the result.

## Item 3a: level, placement, and the environment
- **Placement:** `tools/agent-isolation/` sits beside `tools/github` and `tools/gmail`, and its README follows the sibling layout. No finding.
- **Tests:** none exist for either script, and the repository has no shell-test harness. The scripts could have small tests: `claude-iso.sh` with a stub `claude` on `PATH`, as I ran it, and the check script's report loop with stubbed lookups. No CI job runs either script.
- **Repository gate:** `prek` was not run (no network to fetch hooks). I checked the doctoc TOCs by hand against the headings, and they match.

## Item 4: names by content, not by position
- **`secure-agent-setup.md:174`:** "(per step 5 above)" is an ordinal reference, and it points at the wrong step: step 5 is "Open the bump as its own PR", not the confirmation it describes. Name the step by its content instead.
- **Other cross-references** use named links ("[Install commands](#install-commands)"). None.

## Item 5: the failure report
- **`check-tool-updates.sh:150-153`:** every empty lookup prints "upstream lookup failed (rate limit / network)". The real cause is wrong in at least two cases:
  - the macOS `date -d`/`tac` failure;
  - a tool added to the manifest with no `case` branch (`*) latest_line=""`).

  The reader is sent to look for a network problem that isn't there.
- **Error messages:**
  - `claude-iso.sh:49` names the binary and the remedy. Fine.
  - `check-tool-updates.sh:43` names the path. Fine.

## Item 6: what the writer says it verified
- **Stated:** `prek` passes, one check-script run (all up to date), and the JSON parses.
- **Not stated:**
  - any run of `claude-iso.sh`;
  - any run of the Verification commands;
  - any run that produced an "upgrade candidate" line;
  - any macOS or zsh run.

  The sandbox itself is explicitly deferred to the maintainer's first session. None of the rules was shown failing on a bad case.

## Item 7: siblings of the change
Analogue: the indexes that list repo-root files and tools.
- **`AGENTS.md` "Repo-root files" list (around line 210):** it doesn't list `secure-agent-setup.md`.
- **`AGENTS.md` "References" section:** it lists `tools/github`, `gmail`, `vulnogram`, and `cve-org`, but not `tools/agent-isolation/`.

Only the "Local setup" paragraph was added. `git grep` finds no other reference to `agent-isolation` or `secure-agent` outside the new files.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The header usage forms drop the variable they claim to inject (confirmed) | Substantive | `tools/agent-isolation/claude-iso.sh:39-41` | Use the `CLAUDE_ISO_ALLOW=… VAR=… claude-iso` form |
| The comment claims invocation-line variables are kept, then takes it back | Substantive | `claude-iso.sh:85-109` | Delete both paragraphs and describe `CLAUDE_ISO_ALLOW` only |
| A sourced `claude-iso` calls `exec` and replaces the user's shell (confirmed) | Substantive | `claude-iso.sh:111,116-117` | Run `env -i` without `exec` in the function form, or run it in a subshell |
| Sourcing from `~/.zshrc`, as the doc recommends, fails with `bad substitution` (confirmed) | Substantive | `secure-agent-setup.md:252`, `claude-iso.sh:80,98` | Make the wrapper zsh-safe, or tell zsh users to run it with `bash` |
| The socat lookup fails on stock macOS (`date -d`, `tac`) and is reported as a network failure | Substantive | `check-tool-updates.sh:92,101,103,150-153` | Make the date parsing portable, and give the actual cause of a failed lookup |
| The comment describes a `<` comparison that doesn't exist; an older upstream is reported as a candidate | Substantive | `check-tool-updates.sh:160-168` | Compare versions, or correct the comment and the status text |
| Prereleases and drafts aren't filtered | Substantive | `check-tool-updates.sh:73-79` | Skip `r["prerelease"]` and `r["draft"]` |
| The manifest says the check script uses `pinned_at`; it doesn't | Substantive | `pinned-versions.toml:42-43` | Fix the comment or the script |
| socat `released` 2026-03-13 contradicts the 2026-02-12 date the script reported | Substantive | `pinned-versions.toml:69`, `secure-agent-setup.md:97` | Settle the date from upstream |
| "Three-layer defence" heads a four-layer table | Substantive | `secure-agent-setup.md:69` (and TOC) | Rename the heading |
| Layer 2 claims Edit/Write denies that don't exist | Substantive | `secure-agent-setup.md:75` | Add the rules or drop the claim |
| The "agent never sees" claim is false: Bash output reaches the agent | Substantive | `secure-agent-setup.md:236-241` | Restate what the split actually achieves |
| `gh api` ask patterns miss `--method`, `--field`, `--raw-field`, `--input`, and flag-first order | Substantive | `settings.json:74-76`, `secure-agent-setup.md:229-230` | Widen the patterns or narrow the "any" claim |
| `/schedule` is called the framework's, and its cloud run is said to have the local secure setup; the socat host isn't allowlisted | Substantive | `secure-agent-setup.md:163-175` | Correct the attribution and say where the routine runs and what it can reach |
| "per step 5 above" uses an ordinal and points at the wrong step | Substantive | `secure-agent-setup.md:174` | Name the step by its content |
| The adopter copy step ignores an existing `settings.json` or `settings.local.json` | Substantive | `secure-agent-setup.md:289-305` | Say to merge rather than overwrite, and to check the local overrides |
| No run of `claude-iso`, the Verification commands, or a candidate line is reported | Substantive | commit message, Test plan | Report those runs, including a macOS/zsh one |
| The AGENTS.md repo-root list and References don't list the new doc or the new tool directory | Substantive | `AGENTS.md` Repo-root files, References | Add both entries |
| The "full block" differs from `settings.json` | Taste | `secure-agent-setup.md:181-234` | Call it an annotated excerpt |
| The reason given for the `curl` deny is doubtful | Taste | `secure-agent-setup.md:218` | Give the reason the deny actually serves |

The review did not run the sandbox, `prek`, or any network lookup. The drift script parses none of the changed file types, so the comment checks were done by hand. I did not do a pass over the prose for style alone.
