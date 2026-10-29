# Final review of `1b569a8` (ci(secure-agent): credential-isolation setup + pinned-tool manifest)

**Inputs.** There was no separate task statement, so the claimed cases come only from the commit message. There is no earlier report of this form for this change. `comment-drift.py 2efe27f HEAD` ran and printed nothing. It does not parse shell, Markdown, JSON, or TOML, and the commit contains only those, so I compared every comment against the code by hand. The change has two shell scripts and no tests. I answered the items literally for the scripts and used the §2a analogues for the docs, `.claude/settings.json`, and the TOML manifest. I loaded `english-developer-style` and `test-authoring`; no doc-comment skill applies to shell. `bash -n` passes on both scripts, `shellcheck` reports nothing, and `.claude/settings.json` is valid JSON.

## Item 1: comments consistent with the code and with each other
(Analogue for the docs: statements one file makes about another file or about the code, checked against that file.)

- **`claude-iso.sh:39-41`** says `GH_TOKEN="$(gh auth token)" claude-iso` injects a credential. The code at `:85-109` keeps a variable only if `CLAUDE_ISO_ALLOW` names it. I ran `GH_TOKEN=x bash claude-iso.sh` with a stand-in `claude`, and it printed `GH_TOKEN=unset`. Lines `:85-90` also say "any env var that the user set on the invocation line … is preserved". Lines `:104-109` then contradict that mid-comment ("well, actually we can't reliably tell"), which reads as the writer's working notes rather than a description of the code. `secure-agent-setup.md:273` gives the correct form, so two places disagree about the same fact.
- **`check-tool-updates.sh:163-167`** says "plain `<` does the right thing for ordered output". The script does no ordering comparison at all: `:160` tests only equality, and any other value is reported as "upgrade candidate". `secure-agent-setup.md:144-147` says a candidate line is printed only for a release that is "newer than the pin", which is also false.
- **`pinned-versions.toml:42-43`** says the check script uses `pinned_at` as the minimum age. `read_pinned` (`check-tool-updates.sh:115-123`) never reads `pinned_at`.
- **`secure-agent-setup.md:7, 69`**: the heading is "Three-layer defence", but the table under it has four layers (0 to 3). The commit message also says four.
- **`secure-agent-setup.md:214, 236-241`** say the agent "can't" see `~/.config/gh/` because the Read tool is denied, while `sandbox.filesystem.allowRead` lets Bash read it. The agent's own Bash tool is a sandboxed subprocess, and its output goes into the agent's context. So by the doc's own model, `cat ~/.config/gh/hosts.yml` or `gh auth token` puts the token in the agent's context. The same applies to `~/.config/apache-steward/`. Line `:40` ("reduces it to the project tree") also conflicts with this allowlist.
- **`secure-agent-setup.md:218`** says "network egress via Bash bypasses the sandbox proxy". The sandbox network allowlist exists to filter Bash subprocesses, `curl` included, so this explanation is wrong. Separately, a `Bash(curl *)` deny does not stop `python3 -c 'urllib…'`, which the doc does not mention.
- **`secure-agent-setup.md:229`** says `Bash(gh api * -X *)` covers "any non-default-method API call". That pattern requires an argument between `api` and `-X`, so it does not match the form the skills actually use, `gh api -X PATCH …` (see item 7). It also misses `--method`, `--input`, `--field`, and `--raw-field`.
- **`secure-agent-setup.md:180`** says "The full block is below", but the block leaves out `$schema` and the two `git push --force*` entries that the JSON contains. Minor.
- **`secure-agent-setup.md:252`** says to source the wrapper from `~/.zshrc`. Under zsh, calling `claude-iso` fails with `claude_iso_main:37: bad substitution` (the bash-only `${!var}`); I reproduced this.
- **`secure-agent-setup.md:264-266`** presents the passthrough list as complete but leaves out `LC_ALL` and `LC_CTYPE`, which the code passes through.
- **`secure-agent-setup.md:163`** calls `/schedule` "the framework's" slash command. No skill in `.claude/skills/` provides it; it is a Claude Code command.
- **`claude-iso.sh:73`** says `SSH_AUTH_SOCK` is harmless because push is gated behind ask. The socket lets any process authenticate as the user, for example with `ssh` or `git -c … push`, and none of those are gated.
- **`pinned-versions.toml:95-97`** says `--no-save` keeps a global install from drifting a local lockfile. `npm install -g` never touches a local lockfile. Taste.
- I checked these and they hold: `pyproject.toml:65,76` (the `exclude-newer` value and the `uv` override), `.github/dependabot.yml` (the 7-day cooldown), `README.md#prerequisites-for-running-the-agent-skills`, `tools/gmail/oauth-draft` and `tools/vulnogram/generate-cve-json` exist as cited, and both new doctoc TOCs match their headings.

## Item 2: claimed cases covered
(There is no task statement; these are the cases the commit message claims. Analogue: the section, or the verification step, that shows each one works.)

| Claimed case | Covered by |
|---|---|
| Layer 0 strips credential env vars | Doc verification `echo $AWS_ACCESS_KEY_ID`. The sourced form has a defect (item 3). |
| Layer 0 lets a user inject one credential | Not covered, and the header's documented form fails (item 1). |
| Layer 1 filesystem sandbox | Doc verification `cat ~/.aws/credentials`. |
| Layer 2 deny rules | Doc verification `curl https://example.com`. |
| Layer 3 confirm-on-write | **No verification step**, and the patterns miss the skills' own write commands (item 7). |
| Pins are aged at least 7 days (`pinned_at`) | Holds by the dates: claude-code 04-22 against pinned_at 04-29. But the commit's own output shows socat `PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12` for the same 1.8.1.1, so the manifest's `released` date disagrees with what the script measured. |
| The check script reports aged upgrade candidates | Only the all-up-to-date path was shown. The "upgrade candidate" branch never ran. |
| The check script excludes releases inside the cooldown | Shown by the run: 2.1.123 was not picked. |
| A weekly `/schedule` routine surfaces candidates | Not run. Inside this repo's sandbox, `www.dest-unreach.org` is not in `allowedDomains`, so the socat row would always read "lookup failed". |
| `README.md` and `AGENTS.md` link the new doc | Present. |
| settings.json parses | Holds (I checked). |

## Item 3: boundaries, partitions, and the negative control
(Analogue for the docs: the modes and situations the change claims to cover.)

- **The wrapper's sourced mode is broken.** `exec env -i …` runs inside a function in the user's interactive shell, so the shell itself is replaced. `bash -c "source claude-iso.sh; claude-iso; echo AFTER"` never printed `AFTER`. In real use, the terminal session ends when Claude exits. The doc's primary instruction is to source the wrapper, and only the `bash claude-iso.sh` mode works as intended.
- **Shell partition:** bash works and zsh fails. zsh is the macOS default, and the doc names `~/.zshrc`.
- **OS partition for the check script:** `tac` and `date -d` are GNU-only. On stock macOS the socat row always reports "upstream lookup failed (rate limit / network)". The script does not say it is Linux-only, and it does not say it needs Python 3.11 or later for `tomllib`.
- **Boundary in `gh_latest_aged`:** when none of the 20 most recent releases is old enough, the script prints the "rate limit / network" message. The same happens for an unknown tool name (`:145-147`). Two different outcomes produce one misleading message. Pre-releases are not filtered, so an aged pre-release would be proposed as a candidate.
- **Negative control:** the Verification section (`secure-agent-setup.md:312-318`) lists only denials. Nothing checks that the allowed paths still work (`gh auth status`, `uv run`, a `git push` that prompts). Nothing checks the credential-in-allowRead case: is `~/.config/gh/hosts.yml` readable from the agent's Bash tool?
- **Inherited state:** an adopter who already has a `.claude/settings.json` in their tracker is told to "copy" the framework's file (`:289-291`), with no instruction to merge. Taste-adjacent, but it is the inherited-state partition.

## Item 3a: level, placement, and the environment
The scripts have no tests. Neither the CI workflow nor any repository gate runs `shellcheck` or `bash -n` on them; the only gate is `pre-commit.yml`, and I did not find these checks in it. The new directory's layout matches its siblings under `tools/` (a README and tool files). I did not run `prek`, because it may rewrite files and I was told not to change any.

## Item 4: names by content, not by position
- `secure-agent-setup.md:174`: "per step 5 above". This should be "the bump PR in [Bumping a pinned version]".
- Otherwise none. Headings, the TOC, and the layer names all refer by content.

## Item 5: the failure report
(Analogue: what each rule tells the reader to look at.)
- The check script's single failure message, "upstream lookup failed (rate limit / network)", covers four different causes: a network error, no aged release in the window, an unknown tool, and missing GNU tools. A reader acts on the wrong cause.
- The Verification section's expected outputs name the layer that should deny each command. That part is good.

## Item 6: what the writer says it verified
The commit message states one check-script run (all up to date), the JSON parse, and `prek`. It states no run of `claude-iso` in either mode, no run of the "upgrade candidate" branch, and no run of the Verification commands. It says the sandbox "will be exercised" after merge, which is a plan rather than evidence. My run of the wrapper above shows that its sourced form and its documented `GH_TOKEN=` form both fail.

## Item 7: siblings of the change
- **The `permissions.ask` list against the skills' own write commands.** `git grep` finds `gh api -X PATCH|DELETE repos/<tracker>/…` used by `sync-security-issue/SKILL.md:1353,1390,1694,1701,1723`, `allocate-cve/SKILL.md:487`, `deduplicate-security-issue/SKILL.md:385,405`, `invalidate-security-issue/SKILL.md:482`, and `tools/github/status-rollup.md:219,321`. None of these match `gh api * -X *`, so comment edits and deletions run without confirmation. These are also missing from `ask`: `gh label create` (`fix-security-issue/SKILL.md:680`, `tools/github/operations.md:201`), `gh issue reopen` (`operations.md:150`), and `gh repo fork` (`fix-security-issue/SKILL.md:146,293`). The general publishing commands `gh pr comment`, `gh pr review`, `gh pr close`, and `gh gist create` are missing too, and `gh gist create` is an exfiltration path.
- **`allowedDomains` against the hosts the new script calls:** `www.dest-unreach.org` is missing.
- **Indexes:** `AGENTS.md` → References lists `tools/github|gmail|vulnogram|cve-org` but not `tools/agent-isolation/`. The repo-root file list near the top of `AGENTS.md` does not list `secure-agent-setup.md`.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| A sourced `claude-iso` replaces the user's interactive shell (`exec` inside a function) | Substantive | `claude-iso.sh:111,116-117` | Run `env -i` in a subshell or without `exec` when sourced, or document only `bash claude-iso.sh` |
| zsh sourcing fails with "bad substitution", but the doc says `~/.zshrc` | Substantive | `secure-agent-setup.md:252`, `claude-iso.sh:80` | State that the wrapper is bash-only, or make it portable |
| The header's `GH_TOKEN=… claude-iso` example drops the token, and the comments at `:85-109` contradict themselves | Substantive | `claude-iso.sh:39-41,85-109` | Use the `CLAUDE_ISO_ALLOW` form and delete the narrated aside |
| "The agent can't see" the gh and oauth tokens is false while `allowRead` exposes them to the agent's Bash tool | Substantive | `secure-agent-setup.md:40,214,236-241` | Restate the threat honestly, or remove the paths from `allowRead` |
| The `ask` patterns miss `gh api -X …`, `--method`, `--input`, `gh label create`, `gh issue reopen`, `gh repo fork`, `gh pr comment/review/close`, and `gh gist create` | Substantive | `.claude/settings.json:63-77`, doc `:229-230` | Add the patterns, and fix the "any non-default-method" claim |
| The "lexical `<`" comment describes a comparison that does not exist; any inequality is called a candidate | Substantive | `check-tool-updates.sh:160-168`, doc `:144-147` | Compare versions (`sort -V`) or correct both texts |
| The `pinned_at` comment says the script uses the value; it does not | Substantive | `pinned-versions.toml:42-43` | Remove the claim or implement the check |
| The "Three-layer" heading sits over a four-layer table | Substantive | `secure-agent-setup.md:69` | "Four-layer defence" (regenerate the TOC) |
| "Bash bypasses the sandbox proxy" is the wrong reason for the curl deny | Substantive | `secure-agent-setup.md:218` | State the real reason, and that the deny is bypassable |
| socat `released` date disagrees with the script's own upstream date | Substantive | `pinned-versions.toml:67` | Reconcile with the upstream release date |
| The check script is GNU-only (`tac`, `date -d`), and the socat host is outside `allowedDomains` | Substantive | `check-tool-updates.sh:92,101,103`; settings.json | Say "Linux only", or make it portable; add the host or note it |
| One failure message covers four causes; pre-releases are not filtered | Substantive | `check-tool-updates.sh:75,145-153` | Use distinct messages; skip `prerelease` |
| Verification has no positive control, no Layer 3 check, and no allowRead-credential check | Substantive | `secure-agent-setup.md:312-318` | Add `gh auth status`, a prompted `git push`, and a `cat ~/.config/gh/hosts.yml` expectation |
| "SSH_AUTH_SOCK … harmless" | Substantive | `claude-iso.sh:73` | State the real exposure |
| The doc's "full block" omits entries; the passthrough list omits `LC_*` | Substantive (low) | `secure-agent-setup.md:180,264-266` | Make the doc match the file |
| "The framework's `/schedule`" | Substantive (low) | `secure-agent-setup.md:163` | Say it is Claude Code's `/schedule` |
| "per step 5 above" | Substantive (low) | `secure-agent-setup.md:174` | Name the step by content |
| AGENTS.md References and the root-file list skip the new directory and doc | Substantive (low) | `AGENTS.md:1124-1133` | Add the entries |
| The `--no-save` rationale | Taste | `pinned-versions.toml:95-97` | Drop the flag or the rationale |

This review did not run the check script against upstream (no network), did not run `prek`, did not test sandbox precedence for paths that appear in both `allowRead` and the Read denies, did not check that apt or dnf ship the pinned package versions, and did no pass over the prose for style alone.
