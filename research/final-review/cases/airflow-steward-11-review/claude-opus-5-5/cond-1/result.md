I reviewed `2efe27f..HEAD` (one commit, 1b569a8) against the final-review form. Besides prose, the change adds two shell scripts. It has no tests and no task statement, so the claimed cases come from the commit message alone. I changed no files.

The most serious problems, confirmed by running the code:
- **The wrapper breaks the user's shell.** Sourcing `claude-iso.sh` from `.bashrc` and running `claude-iso` replaces the user's interactive shell with `claude`. Under zsh, which the doc recommends, the wrapper fails with `bad substitution`.
- **The documented `GH_TOKEN=... claude-iso` form drops the token.** Only variables named in `CLAUDE_ISO_ALLOW` pass through.

Other findings come from reading the text, and I flag where they rest on my knowledge of outside tools rather than a run. Notably, the "confirm before writing" rules are easy to sidestep, and the doc's claim that the agent never sees the gh token cannot be true as written.

# Final review: `2efe27f..1b569a8` — secure-agent setup

**Inputs.**
- **Task statement:** none was handed over. The claimed cases come only from the commit message.
- **Previous report:** none.
- **Drift script:** I ran `comment-drift.py 2efe27f HEAD` and it printed nothing. The change is Markdown, JSON, TOML and shell, which the script does not parse.
- **Analogues:** the docs and config get the §2a analogues. The two scripts are code with no tests. The `AGENTS.md` hunk is an instruction file and gets the table of added instructions.
- **Skills loaded:** `apm-authoring` and `english-developer-style`.

## Item 1: comments consistent with the code and with each other

Analogue: every statement a changed file makes about another file, about the config, or about a tool. The file and line references below are into the HEAD tree.

1. **The layer count disagrees.** `secure-agent-setup.md:69` (and its TOC entry, `:7`) is headed "Three-layer defence". The table under it lists four layers, numbered 0 to 3, and the commit message says "four layers". A reader will expect three. Request: rename the heading to "Layered defence" or "Four-layer defence", and regenerate the TOC.
2. **"The agent should never *see*" the credential is false.** This is `secure-agent-setup.md:236-241`, with the inline comment at `:214`.
   - `sandbox.filesystem.allowRead` lets Bash read `~/.config/gh/`. The agent's own Bash tool can therefore run `cat ~/.config/gh/hosts.yml` or `gh auth token` and get the token in its context. `Read(...)` only blocks the Read tool.
   - The opposite reading may also hold. Claude Code merges `Read` deny rules into the sandbox: the sandbox profile of this very review session lists `~/.config/gh` under both deny and allow-within-deny. If the deny wins, `gh` itself cannot read its token.
   - Either way, one of the two promises at `:237-241` is false, and nothing in the change shows which.
   - Request: in a sandboxed session, run `gh auth status` and `cat ~/.config/gh/hosts.yml`, then state the outcome you observe.
3. **The reason given for the curl deny is false.** `secure-agent-setup.md:218` says "network egress via Bash bypasses the sandbox proxy". With `sandbox.enabled`, Bash egress goes through the proxy, and only allowlisted hosts are reached. The deny rule also does not stop egress:
   - `python3 -c 'import urllib.request…'` is not denied.
   - `bash check-tool-updates.sh` is not denied either, and it calls `curl` internally.
   - Request: state the real reason, or drop the comment. Also list "Bash command-name denies are bypassed by any other interpreter" as a residual risk.
4. **The `ask` comments promise coverage the patterns do not give.** These are `secure-agent-setup.md:229-230` ("any non-default-method API call", "any payload-bearing API call") and the Layer-3 row at `:76`.
   - **Forms the patterns miss:** `Bash(gh api * -X *)` needs at least one token between `api` and `-X`. So `gh api -X POST repos/…` is not matched, and neither are `--method POST`, `-XPOST`, `--field`, `--raw-field` or `--input`.
   - **Write commands never listed:** `gh pr comment`, `gh pr review`, `gh pr close`, `gh gist create` and `gh repo create`.
   - **`git push` through a global option:** `git -C . push` does not match `Bash(git push *)`.
   - `github.com` and `api.github.com` are on the network allowlist, so each missed form is an unconfirmed write to a surface others can see, or an exfiltration route. `gh gist create` is one example.
   - Request: either cover these forms or narrow the claim. Also add "writes through `gh`/`git` forms not matched by `ask`" to Residual risks.
5. **"The full block is below" is not true.** At `secure-agent-setup.md:179-181`, the block shown omits `$schema` and the two `git push --force*` entries that `.claude/settings.json:65-66` has. Request: say "abridged", or match the file.
6. **The `/schedule` paragraph misstates what `/schedule` is.** At `secure-agent-setup.md:163` and `:171-175`:
   - `/schedule` is a Claude Code command, not "the framework's".
   - It creates cloud routines. Those do not run under `claude-iso` or this repository's local sandbox, so "runs in the same secure setup" is false.
   - Request: correct both sentences, or drop the routine recipe.
7. **The manifest says the check script reads `pinned_at`; it does not.** The claim is at `pinned-versions.toml:42-43` ("The check script uses this as the minimum age"). `check-tool-updates.sh` never reads `pinned_at`. Request: drop that sentence, or make the script enforce it.
8. **A comment describes a comparison the code does not make.** At `check-tool-updates.sh:163-167`, the comment talks about "plain `<`", but no comparison exists. Any mismatch prints "upgrade candidate", including an upstream version that is older than the pin. That contradicts "newer than the pin" in the commit message and in `tools/agent-isolation/README.md:30`. Request: compare the versions (for example with `sort -V`), or reword the status and both claims.
9. **The wrapper's comments describe a contract the code does not keep.**
   - `claude-iso.sh:39-41` gives `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` as usage. `:85-90` says variables set on the invocation line are preserved.
   - My run of `GH_TOKEN=x bash claude-iso.sh` showed `GH_TOKEN` absent from the child's environment. Only `CLAUDE_ISO_ALLOW` passes variables, which `secure-agent-setup.md:273` documents correctly.
   - `:104-109` narrates a decision that was reversed ("well, actually we can't reliably tell…"). It belongs to neither the code nor the doc.
   - Request: make the header examples use `CLAUDE_ISO_ALLOW`, and delete `:85-90` and `:104-109`.
10. **The socat `released` date disagrees with the date the check finds.** `pinned-versions.toml:69` says `2026-03-13`. The commit message's own run of the check shows `UPSTREAM@ 2026-02-12` for the same 1.8.1.1. The `released` field is the cooldown evidence, so one of the two dates is wrong. Request: state the source of `released` and use the same one in both places.

## Item 2: claimed cases covered

The claimed cases come from the commit message alone, since there is no task statement.

| Claimed case or documented command | Covered by | Outcome |
| --- | --- | --- |
| Settings JSON parses | the commit's `python3 -c json.load` run; I reran it | ok |
| `prek run --all-files` passes | the commit's own statement | ok (this is a consistency gate) |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:113-116`, `pinned-versions.toml:62,78`) | none | **Substantive.** The result depends on the versions in each distro's archive. As I know them, Ubuntu 24.04 ships bubblewrap 0.9.x, Debian 13 ships 0.11.0, and socat 1.8.0.x, so the pinned version string matches nothing. Request: run it on each supported release, or document a form that runs (no pin, or a from-source install). |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | none | **Substantive**, same property. As I know it, RHEL 9 ships bubblewrap 0.4.x. Same request. |
| `npm install -g … claude-code@2.1.117` pins the runtime (`pinned-versions.toml:86-93`, rationale "silent autoupdate") | none | **Substantive.** Nothing disables the auto-updater: there is no `env.DISABLE_AUTOUPDATER` and no `autoUpdates: false`. `env -i` in `claude-iso` also drops a `DISABLE_AUTOUPDATER` the user exported. So the pin decays on the first update. Request: set the updater off in `.claude/settings.json` `env` (or add the variable to the passthrough list), and show the run where it holds. |
| `source …/claude-iso.sh` from `~/.bashrc` or `~/.zshrc`, then `claude-iso` (`secure-agent-setup.md:249-262`) | none; I ran it with a stub `claude` | **Substantive, confirmed.** Under bash, the sourced function runs `exec`, which replaces the user's interactive shell: `echo SHELL-SURVIVED` after it never ran. Under zsh: `claude_iso_main:37: bad substitution`, and `claude` is never launched. Request: in the function, run `env -i …` in a subshell instead of `exec`, and either support zsh or say the file is bash-only and drop `~/.zshrc`. |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` | my run | ok |
| `GH_TOKEN="$(gh auth token)" claude-iso` (`claude-iso.sh:40`) | my run | **fails** (filed under item 1, finding 9) |
| `bash check-tool-updates.sh` prints the status table | the commit's run, apparently on Linux and outside the sandbox | **Substantive** for the two other configurations the change claims. Inside the dogfooded sandbox, `www.dest-unreach.org` is not in `allowedDomains`, so socat always reports "lookup failed". This includes the weekly-routine use the doc recommends. On macOS, BSD `date` lacks `-d`, so socat fails the same way. Request: add the host to the allowlist or note the gap, and use portable date parsing (for example Python). |
| Verification commands (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl …`) deny | none. The commit defers this to "the maintainer's first invocation … after merge". | **Substantive.** Request: one sandboxed run with its output, on Linux and on macOS. |

Reading the claims the other way: every hunk is claimed by the commit message.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the platforms, shells and consumers the change claims. The negative control is the statement of what still works.

- **Platforms and shells.** Linux and macOS are claimed, and so are bash and zsh (`:252`). Only Linux with bash shows evidence. The zsh and macOS failures are filed in item 2.
- **No positive control.** The Verification section checks only denials. Nothing checks that the tools the framework needs still work under the sandbox: `gh`, `uv run`/`prek`, and `oauth-draft-create`. Finding 2 of item 1 says `gh` may not. Request: add positive checks next to the denials, for example `gh auth status`, `prek run --all-files` and an `oauth-draft` dry run.
- **The upstream clone sits outside what the sandbox allows.** This is a consumer the new config meets. `fix-security-issue` writes into and tests in `environment.upstream_clone` (`.claude/skills/fix-security-issue/SKILL.md:273-282`), a path outside the tracker's working tree. `denyRead: ["~/"]` with only `.` allowed blocks Bash reads there, and the sandbox's default write scope (the working directory) blocks writes. The adopter step at `secure-agent-setup.md:294-296` says only "add any project-specific paths". Request: name the upstream clone in the `allowRead` guidance and the write allowance it needs, or run `fix-security-issue` once under this config.

## Item 3a: level, placement, and the environment

The wrapper's environment filtering can be observed in one process, with a stub `claude` as I did. Yet no test exists, and no hook runs `shellcheck` or the scripts. By contrast, the sibling tools (`generate-cve-json`, `oauth-draft`) each have pytest, ruff and mypy hooks in `.pre-commit-config.yaml`. **Substantive.** Request: a small shell test of `claude-iso` (passthrough, `CLAUDE_ISO_ALLOW`, the shell surviving after a sourced call), wired as a hook, plus a `shellcheck` hook.

`shellcheck` reports nothing on either script, and `bash -n` passes. Placing `.claude/settings.json` and `tools/agent-isolation/` there matches the repository layout.

## Item 4: names by content, not by position

`secure-agent-setup.md:174` says "per step 5 above". That step's content is "Open the bump as its own PR", so the reference goes stale if the list changes. Taste, minor. Request: "per the PR step of *Bumping a pinned version*".

## Item 5: the failure report

- **The lookup-failure message names the wrong cause.** `check-tool-updates.sh:153` prints "upstream lookup failed (rate limit / network)" for every failure, including a host blocked by the sandbox and missing GNU `date -d`/`tac`. A reader is sent to look for the wrong cause. Substantive. Request: let the `curl` and `date` stderr through, or name the failing step.
- **The Verification section tests a weaker property than the rule.** It checks only the literal `curl` form. The rule it backs is "no egress outside the allowlist", which `python3 -c urllib…` would test. Substantive. Request: verify egress with a non-`curl` client to a host off the allowlist.

## Item 6: what the writer says it verified

The commit states three things: the JSON parses, `prek` passes, and the check script ran. It explicitly does not state that any denial, or any still-working tool, was exercised. There is no bad case shown failing and no good case shown passing for the sandbox and permission rules. Substantive. Request: the run asked for in item 2 (Verification commands) and item 3 (positive control).

## Item 7: siblings of the change

The change adds a repo-root doc and a `tools/` adapter directory. Two places in `AGENTS.md` list the other members and do not name the new ones:
- **"Repo-root files"** (`AGENTS.md:79-86`) lists `README.md` and `how-to-fix-a-security-issue.md` but not `secure-agent-setup.md`.
- **"References"** (`AGENTS.md`, end of file) lists `tools/github/`, `tools/gmail/`, `tools/vulnogram/` and `tools/cve-org/`, but not `tools/agent-isolation/`.

Request: add both entries.

### Added instructions (the `AGENTS.md` hunk)

Added instructions: 1.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | any session already running, such as fixing a typo in a doc | a reminder to relaunch under `claude-iso`, which the agent cannot do itself | "when the user asks how to set up or launch the agent" |

Not findings: none.

## Findings index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| A sourced `claude-iso` replaces the user's shell (`exec`), and fails under zsh | Substantive | `tools/agent-isolation/claude-iso.sh:111`, `secure-agent-setup.md:252` | 2 |
| Header examples and comments promise invocation-line passthrough the code drops; comment narrates a reversed decision | Substantive | `claude-iso.sh:39-41,85-90,104-109` | 1 |
| Claim that the agent never sees the gh/OAuth credential is untested and contradicts the config | Substantive | `secure-agent-setup.md:214,236-241` | 1 |
| `ask` patterns miss `gh api -X …` forms, `gh pr comment`/`gist create`, and `git -C . push` | Substantive | `.claude/settings.json:64-77`, `secure-agent-setup.md:76,229-230` | 1 |
| Claude Code pin is defeated by the auto-updater | Substantive | `pinned-versions.toml:86-100` | 2 |
| apt/dnf pinned install commands do not match distro package versions | Substantive | `secure-agent-setup.md:113-125`, `pinned-versions.toml:62-63,78-79` | 2 |
| Check script fails for socat inside the sandbox and on macOS | Substantive | `check-tool-updates.sh:90-103`, `.claude/settings.json:19-34` | 2 |
| Verification denials never run | Substantive | `secure-agent-setup.md:309-318` | 2, 6 |
| `/schedule` described as the framework's and as running in the local secure setup | Substantive | `secure-agent-setup.md:163,171-175` | 1 |
| "Three-layer defence" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | 1 |
| The curl deny's stated reason is false, and the rule is bypassable | Substantive | `secure-agent-setup.md:218` | 1 |
| `pinned_at` said to be read by the check script; it is not | Substantive | `pinned-versions.toml:42-43` | 1 |
| Comment describes a missing `<` comparison; an older upstream shows as "upgrade candidate" | Substantive | `check-tool-updates.sh:160-168` | 1 |
| socat `released` date disagrees with the date the check reports | Substantive | `pinned-versions.toml:69` | 1 |
| "The full block is below" shows an abridged block | Substantive | `secure-agent-setup.md:179-181` | 1 |
| No positive control; upstream clone blocked for `fix-security-issue` | Substantive | `secure-agent-setup.md:282-318` | 3 |
| No test or hook for the shell scripts | Substantive | `tools/agent-isolation/` | 3a |
| Lookup-failure message names the wrong cause; verification checks only literal `curl` | Substantive | `check-tool-updates.sh:153`, `secure-agent-setup.md:317` | 5 |
| New doc and tool directory missing from the `AGENTS.md` lists | Substantive | `AGENTS.md:79-86`, References | 7 |
| Instruction to relaunch addressed to an agent that cannot act on it | Substantive | `AGENTS.md:312` | 3 (table) |
| "per step 5 above" refers by position | Taste | `secure-agent-setup.md:174` | 4 |

Some checks could not be done. The drift script does not parse these file types. With no network, I could not check the distro package versions or Claude Code's sandbox behavior on Linux. I also did not read `~/.config/gh` to settle which of the two promises in item 1, finding 2 holds, because that would mean reading a credential the task does not involve.
