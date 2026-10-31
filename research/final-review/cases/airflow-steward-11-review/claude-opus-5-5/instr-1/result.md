# Final review: `2efe27f..HEAD` (commit 1b569a8, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest")

I had no separate task statement, so the claimed cases come from the commit message alone. There is no earlier report to compare against.

Inputs used:
- The full diff.
- `comment-drift.py 2efe27f HEAD`. It printed nothing and exited 0, because it doesn't parse Markdown, JSON, TOML or shell.
- `bash -n` and `shellcheck` on both scripts. Both are clean.
- Runs of `claude-iso.sh` against a fake `claude` that prints its environment, under bash and under zsh.
- `date -d`, `tac` and `tomllib` tried on this macOS host.

Skills loaded: `english-developer-style`, `apm-authoring` (for the AGENTS.md hunk) and `test-authoring`.

Most of the change has no code members, so I used the §2a analogues for the docs, configuration and AGENTS.md. For the two shell scripts I used the form as written.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement one file makes about another file, about the code, or about Claude Code.

**Shell scripts**
- `claude-iso.sh:39-41` says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` pass one credential through. They don't.
  - I ran `GH_TOKEN=secret2 claude-iso` under bash and the fake `claude` received no `GH_TOKEN`.
  - Only names listed in `CLAUDE_ISO_ALLOW` get through, which is what `secure-agent-setup.md:273` correctly shows.
- `claude-iso.sh:85-90` says "any env var that the user set on the invocation line of `claude-iso` is preserved." That's false for the same reason.
- `claude-iso.sh:99-104` is an abandoned train of thought ("well, actually we can't reliably tell…") with no code under it.
- `check-tool-updates.sh:163-167` says "this lexical comparison … plain `<` does the right thing". The code at `:160` only does `==`. There is no ordering anywhere.
- `secure-agent-setup.md:144-147` says the check script flags a release "newer than the pin". It actually flags any version that differs from the pin, including an older one.
  - Example: the pin is younger than 7 days, so the newest aged release is older than the pin. The script then labels that older version "upgrade candidate".

**Pin manifest**
- `pinned-versions.toml:42-43` says "The check script uses this [`pinned_at`] as the minimum age". `read_pinned` never reads `pinned_at`.
- `pinned-versions.toml:69` says socat 1.8.1.1 was released 2026-03-13. The commit message's own run of the script shows `UPSTREAM@ 2026-02-12` for the same version.
- `pinned-versions.toml:86-92` says pinning protects against "a silent autoupdate". Nothing in the change turns off Claude Code's auto-updater:
  - `.claude/settings.json` has no `env.DISABLE_AUTOUPDATER` or autoupdate setting.
  - `claude-iso` would drop any such variable from the parent shell anyway.

**`secure-agent-setup.md`**
- `:7` and `:69`: the heading says "Three-layer defence", but the table below it has four layers (0–3). The commit message also says four.
- `:39-42` says the risk is reduced "to the *project tree*". The sandbox only covers Bash subprocesses. The agent's Read tool is limited by a short blocklist (`.claude/settings.json` `permissions.deny`), so it can still read files such as:
  - `~/.git-credentials`, `~/.npmrc`, `~/.pypirc`, `~/.gnupg/`, `~/.bash_history`.
- `:163`: "The framework's `/schedule` slash-command". `/schedule` belongs to Claude Code, not to the framework.
- `:171-172` says the scheduled agent "runs in the same secure setup". `/schedule` creates cloud routines, which run without `claude-iso` or bubblewrap on the user's host.
- `:218` says "network egress via Bash bypasses the sandbox proxy". That's the wrong way round: the sandbox's network allowlist exists to filter exactly the network traffic that Bash subprocesses make.
- `:229` says `Bash(gh api * -X *)` covers "any non-default-method API call". `gh api --method POST …`, `--field`, `--raw-field` and `--input` match none of the `ask` patterns.
- `:236-241` says `allowRead` lets bash read `~/.config/gh/` while `permissions.deny` blocks only the Read tool. This session's own sandbox config contradicts the "only the Read tool" part:
  - The sandbox config lists `~/.config/gh` and `~/.config/apache-steward` under the read-deny list (`denyOnly`) and also under the carve-outs (`allowWithinDeny`).
  - So Claude Code merges `Read(...)` deny rules into the Bash sandbox too.
  - Whether `gh` can still read its `hosts.yml` depends on which rule wins. Nothing in the change shows that, and I didn't read the credential files to find out.

**Wording I'd change, though both readings are defensible**
- `claude-iso.sh:73` calls `SSH_AUTH_SOCK` "harmless". The socket lets any subprocess sign with all loaded keys, and the `ask` rule only matches the literal `git push …` form.
- `pinned-versions.toml:23` cites the per-package override for `uv` as part of the 7-day convention. That override is actually an exemption from the convention.

## Item 2: claimed cases covered

There are no tests in the change. Claimed cases, from the commit message:

| Claimed case | Covered by |
| --- | --- |
| Layer 0 strips credential-shaped variables | My bash run confirms the passthrough works. No test in the change. Fails under zsh (Item 3). |
| One-credential injection | Header examples (`claude-iso.sh:40-41`) fail; the `CLAUDE_ISO_ALLOW` form works (my bash run). No test. |
| Layer 1 filesystem sandbox | None. The commit says the first run after merge will exercise it. |
| Layers 2 and 3 deny/ask rules | None. Missed `ask` patterns listed in Items 1 and 7. |
| Pins aged 7+ days | `pinned-versions.toml` dates. The socat date is contradicted by the commit's own run. |
| Check script lists newer, aged releases | The commit's run on Linux, where every row was "up to date". No case with a candidate and no case with the pin newer than upstream. |
| `settings.json` parses | Yes (`python3 -c json.load`). |
| `prek run --all-files` passes | The writer's claim. I didn't rerun it. |

Commands the change tells a reader to run, with what's known about each:

| Command (file:line) | Promised outcome | Run elsewhere? | Depends on |
| --- | --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:114`, `tools/agent-isolation/README.md:36`, toml) | pinned install | none | The distro archive must carry exactly 0.11.1 and 1.8.1.1. No supported Debian/Ubuntu release is named, and none was shown to carry them. |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (`:122`) | pinned install | none | Same dependency, for Fedora/RHEL. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (`:136`) | pinned runtime | none | The auto-updater then replaces the pin (Item 1). |
| `source …/claude-iso.sh` from `~/.zshrc` (`:252-253`) | defines `claude-iso` | none | The shell. Under zsh, `claude-iso` fails with `claude_iso_main:37: bad substitution` (my run). |
| `claude-iso` (`:261`) | session with a clean environment | none | When sourced, the function `exec`s and replaces the user's interactive shell. My run never reached the `echo AFTER-RETURN` placed after it. |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (`:273`) | token passed through | none | Works under bash (my run). |
| `check-tool-updates.sh` (`:144`, README) | candidate table | the commit's single run, on Linux | On macOS, `date -d` is GNU-only (`check-tool-updates.sh:101,103`). The socat row always prints "upstream lookup failed". Stock macOS also lacks `tac` (`:92`). |
| `/schedule weekly run …` (`:167`) | weekly candidates | none | Runs in the cloud. Inside the sandbox, `www.dest-unreach.org` isn't in `allowedDomains`, so the socat lookup fails there too. |
| `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com` (`:315-317`) | each denied | none | Bubblewrap/Seatbelt actually being active. Never run. |
| `git check-ignore .claude/settings.local.json` (`:305`) | ignored | none | The adopter's global gitignore. |

Hunks: every file in the diff is named in the commit's Files table or its README/AGENTS sentence. No hunk is unclaimed.

## Item 3: boundaries, partitions, and the negative control

**Partitions without evidence**
- **Platform.** Every run was on Linux, but macOS is claimed (Seatbelt, `secure-agent-setup.md:127`). The check script fails its socat lookup there.
- **Shell.** bash works; zsh, which the doc explicitly names, fails.
- **Sourced vs executed.** Sourced `claude-iso` replaces the calling shell.
- **Pin newer than the newest aged release.** Falsely reported as an upgrade candidate (Item 1).
- **No aged release in the last 20.** `per_page=20` at `check-tool-updates.sh:68` against a project that releases often. The row reads as a "rate limit / network" failure.

**State the change will meet**
- **An existing Claude Code install.** It keeps auto-updating past the pin.
- **Environment variables users already rely on.** `env -i` now drops them before Claude Code starts, and the doc says nothing about that. Each one changes what Claude Code itself does:
  - `ANTHROPIC_API_KEY`, or the Bedrock/Vertex selector variables: the session can't authenticate.
  - `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS`: no network behind a corporate proxy.
  - `TMPDIR` on macOS: the temp directory, which the sandbox treats as writable, changes.

No mechanism is replaced and no limit is set, so the fault-timing and limit paragraphs don't apply.

Added instructions (AGENTS.md): 1.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | An agent already running, asked to fix a README typo | It can't relaunch itself; it may warn or stall every turn | "for the person launching a session; an agent already running does not act on it" |

Not findings: none.

## Item 3a: level, placement, and the environment

- Both scripts can be tested in one process, with no network needed:
  - `claude-iso.sh`: a fake `claude` on `PATH` that prints its environment, as I did here.
  - `check-tool-updates.sh`: a fixture manifest and a stubbed `curl`.
- There is no test and no gate: `.pre-commit-config.yaml` has no shellcheck or shell-test hook. The finding is the missing in-process tests for `claude_iso_main` and for the status logic in `check-tool-updates.sh`.
- Placement: `tools/agent-isolation/` sits beside the other `tools/<system>/` subtrees and fits there.
- Generic-tutorial prose: none worth filing.

## Item 4: names by content, not by position

- `secure-agent-setup.md:174`: "(per step 5 above)" points at "Open the bump as its own PR". It should name that step by its content.
- Everything else (headings, "Layer 0–3" labels) is named by content.

## Item 5: the failure report

- `check-tool-updates.sh:153` prints "upstream lookup failed (rate limit / network)" for every empty result. That includes:
  - missing GNU `date`/`tac` on macOS;
  - a host the sandbox blocks;
  - no release in the 20-item page that is old enough.
- So the message names a cause that is usually wrong. It should name the step that produced nothing.
- `claude-iso.sh:49`: the "not found on PATH" message is clear.

## Item 6: what the writer says it verified

- The commit states three things: the check script ran (all rows up to date), the JSON parses, and prek passes.
- It explicitly says the sandbox wasn't exercised.
- There's no run of `claude-iso`, of any Verification command, of an upgrade-candidate case, or of macOS.
- So there is no evidence that any of the four layers denies what the doc says it denies.

## Item 7: siblings of the change

New entries missing from lists that name their siblings:
- `secure-agent-setup.md` is a new root doc. It's missing from:
  - `AGENTS.md:79-85` (Repo-root files);
  - `CONTRIBUTING.md:40-49` (Root docs);
  - `CONTRIBUTING.md:83-89` (directory tree).
- `tools/agent-isolation/` is a new tools subtree. It's missing from:
  - `CONTRIBUTING.md:119-143` (tree);
  - `AGENTS.md` References, which lists `tools/github`, `tools/gmail`, `tools/vulnogram` and `tools/cve-org`.

Other incomplete lists:
- **Passthrough list.** `secure-agent-setup.md:264-267` lists the variables kept, but leaves out `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, which `claude-iso.sh:56-74` passes through.
- **Bump procedure.** `secure-agent-setup.md:151-156` and `check-tool-updates.sh:177-184` name the places to edit. They miss three places that carry the version:
  - the pins table at `secure-agent-setup.md:94-98`;
  - `tools/agent-isolation/README.md:36-37`;
  - the toml `install.*` strings.
  
  They also say to update install commands only "if the distro package version string has shifted", but those commands always contain the version.
- **`ask` list.** Layer 3 claims to cover "visible-to-others writes", but these write commands aren't in the list:
  - `gh pr comment`, `gh pr review`, `gh pr close`;
  - `gh issue reopen`;
  - `gh release upload`, `gh release edit`;
  - `gh workflow run`;
  - `gh api --method`, `gh api --field`, `gh api --input`.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| Sourced `claude-iso` `exec`s and replaces the user's shell | Substantive | `claude-iso.sh:111,117` | Run `env -i` without `exec` in the sourced path (or in a subshell) |
| zsh: `bad substitution` | Substantive | `claude-iso.sh:79`; `secure-agent-setup.md:252` | Make it zsh-safe, or document bash only and drop `~/.zshrc` |
| Header injection examples don't inject | Substantive | `claude-iso.sh:39-41,85-90` | Use the `CLAUDE_ISO_ALLOW` form; delete the false comment |
| Abandoned musing comment with no code | Substantive | `claude-iso.sh:99-104` | Delete it |
| Downgrade reported as "upgrade candidate"; the `<` comment describes code that doesn't exist | Substantive | `check-tool-updates.sh:160-168`; `secure-agent-setup.md:144` | Compare versions (`sort -V`); report a pin newer than upstream separately |
| macOS: socat lookup always fails (`date -d`, `tac`) | Substantive | `check-tool-updates.sh:92,101,103` | Portable date parsing (python3), or say the script is Linux-only |
| Lookup-failure message names the wrong cause | Substantive | `check-tool-updates.sh:153` | Name the step that came back empty |
| `pinned_at` said to be read by the script | Substantive | `pinned-versions.toml:42-43` | Fix the comment, or make the script check it |
| socat `released` contradicts the commit's own run | Substantive | `pinned-versions.toml:69` | Reconcile the date |
| Pin not enforced against auto-update | Substantive | `.claude/settings.json`; `pinned-versions.toml:86-92` | Turn off the auto-updater, or document that the pin doesn't hold |
| "Three-layer" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | "Four-layer" or "Layered" |
| Risk "reduced to the project tree" while the Read tool is only blocklisted | Substantive | `secure-agent-setup.md:39-42` | Narrow the claim, or add the missing deny rules |
| `/schedule` called the framework's, and said to run in the same setup | Substantive | `secure-agent-setup.md:163-175` | Correct both; note the cloud environment and the blocked socat host |
| "Bash bypasses the sandbox proxy" | Substantive | `secure-agent-setup.md:218` | Correct the comment |
| `ask` patterns miss `--method`/`--field`/`--input` and other gh write subcommands | Substantive | `.claude/settings.json` `ask`; `secure-agent-setup.md:229` | Add the patterns, or narrow the claim |
| `allowRead` vs `Read` deny split never run; Claude Code merges `Read` denies into the sandbox | Substantive | `secure-agent-setup.md:236-241` | Run `gh auth status` in the sandbox on Linux and macOS |
| Install and Verification commands never run on any named distro or OS | Substantive | `secure-agent-setup.md:110-136,313-318` | A run per distro/OS, or name the distros the pins exist on |
| Users' existing auth, proxy and `TMPDIR` variables dropped silently | Substantive | `claude-iso.sh:56-74`; `secure-agent-setup.md:264` | Document them, or add them to the passthrough |
| Passthrough list in the doc incomplete | Substantive | `secure-agent-setup.md:264-267` | List `LC_*` and `WAYLAND_DISPLAY` |
| Bump procedure misses the pins table, the README and the toml `install.*` strings | Substantive | `secure-agent-setup.md:151-156`; `check-tool-updates.sh:177-184` | Name every place that carries the version |
| New root doc and tools subtree missing from repository indexes | Substantive | `AGENTS.md:79-85`, References; `CONTRIBUTING.md:40-49,83-143` | Add the entries |
| No in-process tests or shellcheck gate for the scripts | Substantive | `tools/agent-isolation/*.sh`; `.pre-commit-config.yaml` | Fake-`claude` and stubbed-`curl` tests; a shellcheck hook |
| AGENTS.md instruction fires for an agent that's already running | Substantive | `AGENTS.md:312` | See the table under Item 3 |
| "step 5 above" refers by position | Substantive | `secure-agent-setup.md:174` | Name the step by content |
| `SSH_AUTH_SOCK` "harmless" | Taste | `claude-iso.sh:73` | Say what the socket grants |
| uv override cited as part of the convention it's exempt from | Taste | `pinned-versions.toml:23` | Drop the citation |

I didn't check: prek or any network-dependent run (the upstream lookups and the distro package availability), the filesystem sandbox on Linux, the CVE/confidentiality rules (nothing in the change touches tracker content), or the prose for style alone.
