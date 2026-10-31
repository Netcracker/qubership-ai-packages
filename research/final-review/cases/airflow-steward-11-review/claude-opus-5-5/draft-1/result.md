# Final review: `2efe27f..HEAD`, commit `1b569a8` "ci(secure-agent): add credential-isolation setup + pinned-tool manifest"

There was no task statement, so I took the claimed cases from the commit message alone. The change mixes shell code (`claude-iso.sh`, `check-tool-updates.sh`) with configuration (`.claude/settings.json`, `pinned-versions.toml`), a docs page, `README.md`, and an instruction file (`AGENTS.md`). The shell scripts are reviewed against the literal items. Everything else uses the §2a analogues, and each section says which one it used. I loaded `english-developer-style` and `apm-authoring`. `comment-drift.py` ran and printed nothing, because it does not parse shell, Markdown, JSON, or TOML, so I read the comments by hand. The change has no tests.

## Item 1: comments consistent with the code and with each other
(Shell comments read literally. For docs and config, the analogue: every statement one file makes about another.)

- **1a. The wrapper's header shows an injection form the code drops.** `tools/agent-isolation/claude-iso.sh:39-41` documents `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso`. The code keeps only variables listed in `CLAUDE_ISO_ALLOW`. I ran `GH_TOKEN=x AWS_PROFILE=ro bash claude-iso.sh` with a stub `claude`, and it printed `GH_TOKEN=unset AWS_PROFILE=unset`. A reader who follows the header starts a session with no token and no warning. **Request:** replace both lines with the `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` form that `secure-agent-setup.md:273` uses.
- **1b. Two comment blocks in the wrapper contradict the code and each other.** `claude-iso.sh:85-90` begins "any env var that the user set on the invocation line … is preserved", which is false. Lines `104-109` narrate a retraction ("well, actually we can't reliably tell") and then guard no code. **Request:** cut the first block down to its `CLAUDE_ISO_ALLOW` sentence and delete the second.
- **1c. The check script describes a comparison it never makes.** `check-tool-updates.sh:162-166` says "plain `<` does the right thing for ordered output". There is no `<`. The code flags any upstream version that differs from the pin. `secure-agent-setup.md:145-147` says the same line appears only when the release "is newer than the pin". **Request:** either compare versions (for example with `sort -V`) or say "differs from".
- **1d. The manifest claims the check script reads `pinned_at`. It does not.** `pinned-versions.toml:42-43` says "The check script uses this as the minimum age the entries below claim to satisfy", but `read_pinned` never reads that key. **Request:** drop the sentence, or make the script check every `released` date against `pinned_at - 7d`.
- **1e. The page counts three layers and lists four.** The heading and table of contents say "Three-layer defence" (`secure-agent-setup.md:7,69`), while the table lists layers 0 to 3 and the commit message says "four layers". **Request:** rename the heading to "Four-layer defence" or "Layered defence" and update the TOC.
- **1f. The "full block" in the page is not the file.** `secure-agent-setup.md:179-181` says the full `.claude/settings.json` follows. The block leaves out `$schema` and folds the two separate `git push --force*` entries into a comment. It is JSONC, so it cannot be copied as a `settings.json`. `tools/agent-isolation/README.md:55` and the commit message tell adopters to "scaffold … from the example block", but the page's own adopter steps (`:289-291`) say to copy the file. **Request:** call the block "annotated excerpt" and point adopters only at the file.
- **1g. The page's passthrough list is short of the code's.** `secure-agent-setup.md:264-267` says the wrapper "hard-allows only" a list. That list leaves out `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which `claude-iso.sh:57-74` passes through. **Request:** list them all, or say "for example".
- **1h. Two sources give different release dates for socat 1.8.1.1.** The manifest and the docs table give 2026-03-13. The script output quoted in the commit message prints `UPSTREAM@ 2026-02-12` for the same version. **Request:** reconcile the dates and state which source the `released` field is taken from.
- **1i. Three claims about `/schedule` do not hold.** The page says:
  - "The framework's `/schedule` slash-command" (`secure-agent-setup.md:163`), but `/schedule` is Claude Code's built-in command, not the framework's.
  - "The scheduled agent runs in the same secure setup" (`:171`). A scheduled routine is not started through `claude-iso`, and nothing shows the local sandbox applies to it.
  - "per step 5 above" (`:174`) points to the wrong step: step 5 is "Open the bump as its own PR".

  **Request:** correct the attribution, and state which of the layers a scheduled routine actually gets.

## Item 2: claimed cases covered
The cases come from the commit message alone.

| Claimed case or command | What runs it | Verdict |
| --- | --- | --- |
| `.claude/settings.json` parses as JSON | `python3 -c json.load` (I re-ran it: OK) | covered |
| `prek run --all-files` passes | the pre-commit gate; `prek` is not installed here, and `git diff --check` is clean | stated by the writer |
| `check-tool-updates.sh` runs end to end and prints the table | the writer's run, quoted in the commit message (Linux, network) | covered on Linux only, see 2a |
| `source claude-iso.sh` from `~/.bashrc` **or `~/.zshrc`**, then `claude-iso` (`secure-agent-setup.md:252`) | none | **2b, 2c** |
| Credential injection with `CLAUDE_ISO_ALLOW` (`:273`) | none; my stub run shows it works | covered by my run |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` and `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | none | **2d** |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` keeps 2.1.117 in use ("pinning matters because … a silent autoupdate", `pinned-versions.toml:86-92`) | none | **2e** |
| Verification commands (`secure-agent-setup.md:315-317`) each produce a denial | none; the commit message says sandbox enforcement is not exercised yet | **2f** |
| Layer 1 and Layer 2 split: `gh` and `oauth-draft-create` can read `~/.config/gh` and `~/.config/apache-steward`, but the Read tool cannot (`:236-241`) | none | **2f** |
| Layer 3: "visible-to-others writes … without an explicit yes" go through `ask` | none | **2g, plus Item 7** |
| `/schedule weekly run check-tool-updates.sh` surfaces candidates | none | **2h** |

- **2a. The check script misreports socat on macOS.** `check-tool-updates.sh:101` uses GNU `date -d`. BSD `date` rejects it (I ran it here: "illegal option -- d"), so every tarball is skipped and the table says "upstream lookup failed (rate limit / network)", which is the wrong reason. `tac` (`:92`) is also missing from stock macOS. The page treats macOS as a supported host. **Request:** parse dates in the Python helper the script already uses, or say the script is Linux-only.
- **2b. Sourcing the wrapper fails in zsh.** The page tells users to source it from `~/.zshrc`. In zsh, `${!var-}` (`claude-iso.sh:80`) fails: I ran `zsh -c 'source claude-iso.sh; claude-iso'` and got `claude_iso_main:37: bad substitution`, so no session starts. The property this depends on is that `${!var}` indirect expansion exists only in bash. **Request:** support zsh (for example `${(P)var}` behind a shell check), or drop `~/.zshrc` and tell zsh users to run it as `bash claude-iso.sh`.
- **2c. Sourcing the wrapper replaces the user's shell.** `claude-iso` calls `exec env -i …` (`claude-iso.sh:111`). When the file is sourced, as the page recommends, that `exec` replaces the interactive shell. I ran `bash -c 'source …; claude-iso; echo SHELL-SURVIVED'` and the echo never ran. In a real terminal the tab closes when Claude exits. **Request:** in the sourced branch, run `env -i …` in a subshell or without `exec`, and keep `exec` only for direct execution.
- **2d. The pinned package versions may not exist in distro repositories.** Whether these install commands succeed depends on each distro's repository carrying exactly 0.11.1 and 1.8.1.1. Nothing in the change shows that any supported Debian, Ubuntu, Fedora, or RHEL release does. **Request:** run the commands on the distro releases the page means and name those releases, or document a from-source fallback.
- **2e. Nothing stops Claude Code from updating itself past the pin.** By default Claude Code updates itself, so installing 2.1.117 does not keep 2.1.117 in use. Nothing in the change turns the auto-updater off: there is no `env.DISABLE_AUTOUPDATER` in `settings.json`, and the variable is not in the wrapper's passthrough list. Because `claude-iso` strips the environment, a user's own `DISABLE_AUTOUPDATER` is removed too. Two smaller points in the same area: `--no-save` has no effect with `-g`, so the reason given at `pinned-versions.toml:97-99` is wrong, and "npm (the only stable channel today)" is a claim the change does not support. **Request:** set `"env": {"DISABLE_AUTOUPDATER": "1"}` in `.claude/settings.json`, or add the variable to the passthrough list, and fix the `--no-save` reason.
- **2f. The sandbox and permission split is promised but never run.** The outcome depends on how Claude Code 2.1.117 combines `permissions.deny Read(...)` with `sandbox.filesystem.allowRead` for the same path. If the Read deny rules are also applied to Bash in the sandbox, `gh` loses its token and every skill's `gh` call fails. If not, the split works as the page says. The change leaves this to "the maintainer's first invocation after merge". **Request:** on 2.1.117, inside a sandboxed session on Linux and on macOS, run `gh auth status`, `oauth-draft-create --help` with real credentials, a Read-tool attempt on `~/.config/gh/hosts.yml`, and the three verification commands. Record the results in the page.
- **2g. The `ask` patterns for `gh api` miss the form the skills use.** The rules are `Bash(gh api * -X *)`, `-f`, and `-F`. Each needs text between `api` and the flag. The skills' own calls put `-X` first: `gh api -X PATCH repos/<tracker>/issues/comments/<id> --input …` (`tools/github/status-rollup.md:219`, `sync-security-issue/SKILL.md:1701`) and `gh api -X DELETE …` (`sync-security-issue/SKILL.md:1390,1723`). By the pattern's literal text, comment deletes and PATCH calls with `--input` skip the confirmation the page promises. **Request:** add `Bash(gh api -X *)` and `Bash(gh api --method *)`, or run those exact commands on 2.1.117 and show they prompt.
- **2h. The scheduled check can never look up socat.** A run inside this setup cannot reach `www.dest-unreach.org`, because that host is not in `allowedDomains`, so the socat lookup always fails there. **Request:** add the host, or state the limitation.

Reverse direction: every hunk is claimed in the commit message's file table. No version or dependency changes outside the claims.

## Item 3: boundaries, partitions, and the negative control
(For config: state the change will meet, and values users already pass. For the instruction file: the table below.)

- **3a. The wrapper strips variables users already set for Claude itself.** The environment of every existing user is state this change meets. Besides `DISABLE_AUTOUPDATER` (2e), the wrapper removes:
  - Bedrock and Vertex selectors (`CLAUDE_CODE_USE_BEDROCK` with `AWS_*`, `CLAUDE_CODE_USE_VERTEX`), so those users cannot authenticate;
  - `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS`, so users behind a corporate proxy cannot connect;
  - `CLAUDE_CONFIG_DIR`, so users with a custom config directory start without their configuration.

  **Request:** pass through the variables Claude Code itself reads, or document them as `CLAUDE_ISO_ALLOW` cases and run the wrapper with each.
- **3b. Users who push over SSH cannot push in the sandbox.** Both `denyRead ["~/"]` and `Read(~/.ssh/**)` hide `~/.ssh/known_hosts` and `~/.ssh/config`. The sandbox proxies only HTTP(S) to the allowed domains. So `git push` to an SSH remote fails inside the sandbox, yet `claude-iso.sh:73` passes `SSH_AUTH_SOCK` through "for git push". **Request:** run a push to an SSH remote in the sandbox, or tell users to use HTTPS remotes with the `gh` credential helper and drop the `SSH_AUTH_SOCK` passthrough.
- **3c. Checked with nothing to report:** no limit is set or moved, and no mechanism is replaced.
- **3d. A missing parser fails quietly.** `read_pinned` needs Python 3.11 or later for `tomllib`. On an older `python3`, the process substitution fails, the loop gets no rows, and the script still prints its header and exits 0. **Request:** add `set -o pipefail` coverage or an explicit check, so a parse failure exits non-zero.

**Added instructions in `AGENTS.md`:**

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a session editing framework docs with no tracker or security-list content | a reminder to restart under `claude-iso`, which it cannot act on | "when the session reads `<tracker>` or `<security-list>` content" |

Not findings: none.

## Item 3a: level, placement, and the environment
- The new directory follows the `tools/<name>/` layout. `README.md` in place of `tool.md` is defensible, because these are not tool adapters, and the README says so.
- `shellcheck` reports nothing on either script, and `bash -n` passes on both.
- I could not run `prek`; it is not installed here.
- The scripts have no tests. The defects in 2b and 2c are visible with a stub `claude`, so a small bats or plain-shell test with a stub binary would be enough. **Request:** add one.

## Item 4: names by content, not by position
- "per step 5 above" (`secure-agent-setup.md:174`) points to the wrong step (see 1i). **Request:** name the step by its content, for example "the maintainer's review of the release notes".

## Item 5: the failure report
- The check script reports every failed lookup as "upstream lookup failed (rate limit / network)". On macOS, a BSD `date` failure and a missing `tac` are reported under the same wrong reason (2a). **Request:** print the step that failed.
- The verification section's detections fit the rules they check.

## Item 6: what the writer says it verified
- The writer verified that the JSON parses, that `prek` passes, and one Linux run of the check script.
- The writer did not run the wrapper in any shell. The commit message says outright that sandbox enforcement was not exercised.
- No evidence that the denials can fail is given: no run of the verification commands on a configured host, and no negative case.

## Item 7: siblings of the change
- **Write commands that the skills use and the `ask` list does not cover:**
  - `gh label create` (`fix-security-issue/SKILL.md:680`, `tools/github/operations.md:201`)
  - `gh issue reopen` (`tools/github/operations.md:150`)
  - `gh repo fork` (`fix-security-issue/SKILL.md:146,293`)
  - the `gh api -X …` forms from 2g
  - `git -C <dir> push`, which skips `Bash(git push *)`

  Every other write the skills issue (`gh issue create`, `edit`, `close`, `comment`, `gh pr create`, `edit`, `merge`) is listed. **Request:** add these to `permissions.ask`.
- The doc's annotated copy of the settings and the actual file are two lists of the same set. They differ (1f).
- Mentioned without a request: the `AGENTS.md` References list of `tools/` directories does not name `tools/agent-isolation/`, but it already left out `tools/ponymail/`.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| `claude-iso` sourced from an rc file `exec`s over the interactive shell | Substantive | `tools/agent-isolation/claude-iso.sh:111` | 2c |
| `claude-iso` fails in zsh with "bad substitution", but the page recommends `~/.zshrc` | Substantive | `tools/agent-isolation/claude-iso.sh:80`, `secure-agent-setup.md:252` | 2b |
| Header documents an injection form that the code drops | Substantive | `tools/agent-isolation/claude-iso.sh:39-41` | 1a |
| Contradictory or narrating comment blocks about invocation-line variables | Substantive | `tools/agent-isolation/claude-iso.sh:85-90,104-109` | 1b |
| Pin defeated by Claude Code's auto-update; `DISABLE_AUTOUPDATER` stripped | Substantive | `tools/agent-isolation/pinned-versions.toml:86-100`, `.claude/settings.json` | 2e |
| Sandbox `allowRead` and `Read` deny split for `gh` and oauth credentials never run | Substantive | `secure-agent-setup.md:236-241` | 2f |
| `ask` patterns for `gh api` miss `-X`-first and `--method` calls | Substantive | `.claude/settings.json:74-76` | 2g |
| Write commands the skills use are missing from `ask` | Substantive | `.claude/settings.json:62-77` | 7 |
| Wrapper strips variables Claude needs (Bedrock, proxy, config dir) | Substantive | `tools/agent-isolation/claude-iso.sh:57-74` | 3a |
| SSH push cannot work in the sandbox, yet `SSH_AUTH_SOCK` is passed "for git push" | Substantive | `tools/agent-isolation/claude-iso.sh:73` | 3b |
| apt and dnf pinned versions not shown to exist in any distro | Substantive | `secure-agent-setup.md:112-125` | 2d |
| socat lookup broken on macOS (`date -d`, `tac`) and misreported as network failure | Substantive | `tools/agent-isolation/check-tool-updates.sh:92,101` | 2a, 5 |
| Scheduled run cannot reach the socat host | Substantive | `.claude/settings.json:19-34` | 2h |
| Comment claims a `<` comparison that does not exist | Substantive | `tools/agent-isolation/check-tool-updates.sh:162-166` | 1c |
| `pinned_at` said to be used by the script, but it is not read | Substantive | `tools/agent-isolation/pinned-versions.toml:42-43` | 1d |
| "Three-layer defence" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | 1e |
| "Full block" is not the file; adopters told two different sources | Substantive | `secure-agent-setup.md:179-181`, `tools/agent-isolation/README.md:55` | 1f |
| socat release date differs between manifest and script output | Substantive | `tools/agent-isolation/pinned-versions.toml:66` | 1h |
| `/schedule` called the framework's; "same secure setup" unproven; "step 5" points to the wrong step | Substantive | `secure-agent-setup.md:163-175` | 1i, 4 |
| `AGENTS.md` instruction has no condition limiting it to sessions with tracker content | Substantive | `AGENTS.md:312` | 3 |
| Manifest parse failure exits 0 with an empty table | Substantive | `tools/agent-isolation/check-tool-updates.sh:118-126` | 3d |
| No test with a stub `claude` for the wrapper | Substantive | `tools/agent-isolation/` | 3a |
| Page's passthrough list is incomplete | Taste | `secure-agent-setup.md:264-267` | 1g |

`comment-drift.py` could not parse any of the changed file types, and `prek` is not installed here, so the pre-commit gate was not re-run. Nothing about the sandbox's behavior itself could be checked without the configured Linux host and Claude Code 2.1.117.
