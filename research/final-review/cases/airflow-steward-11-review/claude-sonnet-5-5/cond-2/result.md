# Final review: `2efe27f..HEAD` (1b569a8, secure-agent setup)

**Inputs.** The task statement was not handed over, so item 2 uses the commit message alone. The change has no tests. It adds one JSON config, two shell scripts, one TOML manifest, and three markdown pages (`secure-agent-setup.md`, `tools/agent-isolation/README.md`, and hunks in `AGENTS.md` and `README.md`).

**Skills loaded.** I loaded `apm-authoring` and `english-developer-style`. The change adds no tests, so I did not load `test-authoring`. No doc-comment skill applies to shell or TOML.

**Drift script.** I ran it and it printed nothing and exited 0. It does not parse `.sh`, `.toml`, or `.md`, so the item 1 analogue (statements one file makes about another) was applied by hand. `bash -n` and `shellcheck` are clean on both scripts.

**Analogues used.** Item 1 reads statements across files. Item 2 reads claimed commands and behaviors. Items 3 and 3a read pre-existing state and placement. Item 5 reads the Verification detections. Item 6 reads the verification evidence. Item 7 reads the enumerating surfaces.

## Item 1: comments consistent with the code and with each other

- **F1 (substantive), `secure-agent-setup.md:69` and `:7`.** The heading says "Three-layer defence", but the table under it lists layers 0 to 3 (four). The commit message also says four layers. Request: rename the heading to "Four-layer defence" and fix the TOC anchor.
- **F2 (substantive), `tools/agent-isolation/claude-iso.sh:27-31` against `:76-96`.** The header documents `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` as one-session injection. The code only passes variables that are in the passthrough list or named in `CLAUDE_ISO_ALLOW`. I ran `GH_TOKEN=x claude-iso` and the child saw 0 `GH_TOKEN` entries. The comment block at `:76-83` first claims invocation-line variables are preserved, then says the opposite, and the comment at `:92-96` says it cannot tell. `secure-agent-setup.md:273` uses `CLAUDE_ISO_ALLOW`, so the doc and the header disagree. Request: fix the header examples to include `CLAUDE_ISO_ALLOW` and delete the two contradictory comment blocks.
- **F3 (substantive), `check-tool-updates.sh:152-157`.** The comment says "plain `<` does the right thing", but the code tests `==`. So any difference, including an upstream older than the pin, is reported as "upgrade candidate". Request: compare versions properly (`sort -V`) or correct the comment and status text.
- **F4 (substantive), `pinned-versions.toml:36-37`.** The comment says "The check script uses [`pinned_at`] as the minimum age the entries claim to satisfy." The script never reads `pinned_at`, and nothing checks `released <= pinned_at - 7 days`. Request: add that check to the script, or drop the sentence.
- **F5 (substantive), `secure-agent-setup.md:236-241`.** It says the agent "should never *see*" the `gh` and Gmail credentials, because `permissions.deny Read(...)` blocks the Read tool. But `sandbox.filesystem.allowRead` makes the same paths readable by any Bash command the agent runs, such as `cat ~/.config/gh/hosts.yml`. The doc also does not list this under "Residual risks". Request: state this gap in the residual risks, or narrow the sandbox allow to the `gh` binary.
- **F6 (substantive), `secure-agent-setup.md:171-175`.** The weekly routine is wired through `/schedule`, and the doc says the scheduled agent "runs in the same secure setup". In this environment `/schedule` creates cloud routines, which do not run under the local `.claude/settings.json` sandbox or `claude-iso`. The doc also calls it "the framework's `/schedule`", but it is a Claude Code command. Request: verify and correct the sentence, or document a local cron instead.
- **F7 (taste), `secure-agent-setup.md:180-181`.** It calls the JSON "the full block", but the doc block omits `$schema` and the `git push --force*` entries that `.claude/settings.json` has. Preferred: say "abridged".
- **F8 (taste), `pinned-versions.toml:93-95`.** The comment says `--no-save` keeps the install from drifting a project lockfile. A `-g` install touches no lockfile, so the flag has no effect.

## Item 2: claimed cases covered

Claims from the commit message, with the artifact that covers each:

| Claim | Covered by |
| --- | --- |
| Layers 0 to 3 | Layer 0 `claude-iso.sh`; 1 to 3 `.claude/settings.json`. No test. |
| 7-day cooldown pins | `check-tool-updates.sh`. It checks upstream but never checks the manifest invariant (F4). |
| Script is side-effect-free | Read from the source: no writes. |
| Valid JSON | Stated as a manual `python3` run. |
| Sandbox enforcement | The commit says it is untested. |

Commands the change tells someone to run (the outcome column says what I saw, and the last column says what runs the same form):

| Command | Promised outcome | Runs in CI or scripts |
| --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` | install | none |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | install | none |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | install | none |
| `source claude-iso.sh; claude-iso` | launches claude | none |
| `GH_TOKEN=... claude-iso` | injects the token | none; F2 shows it does not |
| `bash check-tool-updates.sh` | status table | none; ran once by hand per the commit message |
| `/schedule weekly …` | routine | none; F6 |
| `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com` | denials | none |
| `git check-ignore .claude/settings.local.json` | ignored | none; `.gitignore` has no such entry |

For each `none`, I checked the property the outcome depends on:

- **F9 (substantive), `claude-iso.sh:117`.** `exec env -i … claude` runs inside a function when the file is sourced, which is the documented use. I confirmed that after `claude-iso` returns, the calling shell is gone (`SHELL-STILL-ALIVE` never printed). Request: run it in a subshell, or without `exec` when sourced.
- **F10 (substantive), shell portability.** The doc says to source the wrapper from `~/.zshrc`. `${!var-}` is a bash-only expansion; `zsh -c 'var=HOME; echo ${!var-}'` gives `bad substitution`. `for var in $CLAUDE_ISO_ALLOW` also does not word-split in zsh. Request: use a zsh-safe indirect expansion, or say bash only.
- **F11 (substantive), `check-tool-updates.sh:66-79` and `.claude/settings.json`.** The socat lookup uses GNU `date -d` and `tac`, so it fails on macOS, which the doc says is supported. It also fetches `www.dest-unreach.org`, which is not in `allowedDomains`, so under the dogfooded sandbox the socat row always reports "lookup failed". Request: add the host to the allowlist or take the socat version from another source, and use portable date handling.
- **F12 (substantive), the commit message output table.** It shows socat 1.8.1.1 as released 2026-02-12 upstream, while the manifest records `released = "2026-03-13"` for the same version. One of them is wrong, which undermines the "aged past 7 days" evidence. Request: reconcile the date.
- **F13 (taste), apt and dnf pins.** No sentence says those exact distro package versions exist on a supported release. I could not check this offline.

Claims read the other way: every hunk in the diff is claimed by the commit message. Nothing is out of scope.

## Item 3: boundaries, partitions, and the negative control

Added instructions: 1 (`AGENTS.md:312` "Run the agent in the credential-isolation setup").

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a docs-only edit session, or a non-Claude agent, with no tracker content read | tells the user to relaunch under `claude-iso` and sandbox settings that name only Claude Code | "only where the session reads tracker or `<security-list>` content" |

Not findings: none.

- **F14 (substantive).** The suite has no positive control. The Verification section tests only denials. Nothing runs `gh`, `uv`, or an allowlisted fetch under `claude-iso` plus the sandbox to show the setup does not break the skills. This matters because `env -i` drops variables such as `ANTHROPIC_API_KEY`, `TMPDIR`, proxy variables, and `DISABLE_AUTOUPDATER`. Request: add a run that starts one skill under `claude-iso` and the sandbox, on both Linux and macOS, with output.
- **F15 (substantive), pre-existing state.** `secure-agent-setup.md:289-291` says to copy `settings.json` into `<your-tracker>/.claude/settings.json`. An adopter who already has that file loses it, with no merge instruction. Request: give a merge instruction, or have the adopter keep their existing permissions.
- **F16 (substantive), pin rationale.** `pinned-versions.toml:81-87` pins `claude-code` to stop silent autoupdate. The doc never disables autoupdate, and `claude-iso` strips any `DISABLE_AUTOUPDATER` variable. The pin does not hold. Request: disable the updater in `settings.json` `env`, or in the wrapper passthrough, and verify.

## Item 3a: level, placement, and the environment

- **F17 (taste).** The scripts have no test and are not in a CI or prek hook. The change adds no `shellcheck` hook, although `shellcheck` was available and clean here. Preferred: add the hook.
- The layout matches its siblings under `tools/`. There is no registration gate to run.

## Item 4: names by content, not by position

- **F18 (taste), `secure-agent-setup.md:174`.** "per step 5 above" points at an ordinal, and step 5 is "Open the bump as its own PR". Name the step by content.
- **F19 (taste).** The script's trailing text (`check-tool-updates.sh:177-187`) gives a four-step bump procedure, while `secure-agent-setup.md:141-156` gives five. The two lists differ.

## Item 5: the failure report

- **F20 (substantive), `secure-agent-setup.md:313-320`.** The text says each command "should produce a denial", but `echo $AWS_ACCESS_KEY_ID` prints an empty line and is not a denial. The `curl` check hits the `permissions.deny` rule first, so it never tests the `allowedDomains` network allowlist. The detection checks a weaker property than the one it is attached to. Request: add a fetch to a non-allowlisted host through a non-`curl` tool, and a Bash `cat ~/.config/gh/hosts.yml` (see F5).

## Item 6: what the writer says it verified

The commit message states that `prek` passes, that the check script ran, and that the JSON parses. It states that sandbox enforcement is untested. It says nothing about `claude-iso.sh` ever being run, and F2 and F9 show it was not exercised. There is no failing-case evidence for any rule, since the setup is a set of denials with no deliberate trial of one.

## Item 7: siblings of the change

- **F21 (substantive), `AGENTS.md:1130-1132`.** The "References" list enumerates `tools/github/`, `tools/gmail/`, `tools/vulnogram/`, and `tools/cve-org/`, and the new `tools/agent-isolation/` is missing. Request: add the entry.
- The "three-layer" prose elsewhere (`AGENTS.md:375`, `README.md:646`, `CONTRIBUTING.md:284`) refers to the confidentiality rule and is unrelated.
- **F22 (substantive), `.github/dependabot.yml`.** The change claims the pins mirror the Dependabot convention, but Dependabot does not track these pins, and no scheduled job runs `check-tool-updates.sh`. Request: either name the scheduled job or say the check is manual.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Heading says three layers, table has four | Substantive | `secure-agent-setup.md:69` | 1 |
| `claude-iso` header examples do not work; contradictory comments | Substantive | `claude-iso.sh:27-31, 76-96` | 1 |
| Comment says `<`, code uses `==` | Substantive | `check-tool-updates.sh:152-157` | 1 |
| Manifest says script uses `pinned_at`; it does not | Substantive | `pinned-versions.toml:36` | 1 |
| Agent can read `gh` token via Bash; the deny/allow split claim is false | Substantive | `secure-agent-setup.md:236` | 1 |
| `/schedule` claimed to run in the same secure setup | Substantive | `secure-agent-setup.md:171` | 1 |
| "Full block" omits entries from the real file | Taste | `secure-agent-setup.md:180` | 1 |
| `--no-save` comment on a global install | Taste | `pinned-versions.toml:93` | 1 |
| `exec` in sourced function kills the user's shell | Substantive | `claude-iso.sh:117` | 2 |
| Wrapper is bash-only but documented for `~/.zshrc` | Substantive | `claude-iso.sh:73`, `secure-agent-setup.md:252` | 2 |
| socat lookup breaks on macOS and under the sandbox allowlist | Substantive | `check-tool-updates.sh:66-79` | 2 |
| socat release date disagrees with the commit's own output | Substantive | `pinned-versions.toml:63` | 2 |
| apt and dnf pinned versions unverified | Taste | `secure-agent-setup.md:112-125` | 2 |
| No positive control under the wrapper and sandbox | Substantive | `secure-agent-setup.md:307` | 3 |
| Adopter copy overwrites an existing `settings.json` | Substantive | `secure-agent-setup.md:289` | 3 |
| `claude-code` pin defeated by autoupdate; variable stripped | Substantive | `pinned-versions.toml:81` | 3 |
| Added instruction has no end condition | Substantive | `AGENTS.md:312` | 3 |
| No `shellcheck` hook or script tests | Taste | `.pre-commit-config.yaml` | 3a |
| "step 5 above" is positional | Taste | `secure-agent-setup.md:174` | 4 |
| Bump-step lists differ (4 vs 5) | Taste | `check-tool-updates.sh:177` | 4 |
| Verification detections test a weaker property | Substantive | `secure-agent-setup.md:313-320` | 5 |
| `claude-iso.sh` never run; no red evidence for any rule | Substantive | commit message | 6 |
| `AGENTS.md` References list lacks `tools/agent-isolation/` | Substantive | `AGENTS.md:1130` | 7 |
| No scheduled job runs the check script | Substantive | `.github/dependabot.yml` | 7 |

I did not run the Linux install commands or the sandbox itself, because there is no network and no bubblewrap here.
