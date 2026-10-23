I filled in the final-review form for commit `1b569a8` (`2efe27f..HEAD`). The review found several substantive problems. The two worst are that sourcing `claude-iso.sh`, the documented way to use it, ends the user's shell, and that the dogfooded `.claude/settings.json` blocks a command and a host the framework's own `sync-security-issue` skill needs.

**Inputs.** There was no separate task statement, so I took the claimed cases from the commit message alone. `comment-drift.py 2efe27f HEAD` ran (exit 0) and printed nothing, because it does not parse shell, TOML, JSON, or Markdown. So I read every comment by hand. The change has no tests. I used the code items for the two shell scripts and the §2a analogues for the docs, the manifest, and the settings file. I ran `bash -n`, `shellcheck` (clean), a JSON parse of `.claude/settings.json` (valid), and `claude-iso.sh` against a stub `claude`, under bash 5.3 and zsh on macOS.

## Item 1: comments consistent with the code and with each other
I checked every statement a changed file makes about another file or about its own code. Analogue: a statement one file makes about another counts as a comment.

- **`tools/agent-isolation/claude-iso.sh:39-41`**: the usage header says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` inject a credential for one session. The code only passes on a variable listed in `CLAUDE_ISO_ALLOW`. With `GH_TOKEN=tok bash claude-iso.sh` the stub saw no `GH_TOKEN`. A reader following the header gets a session without the token. `secure-agent-setup.md:273` has the correct form.
- **`claude-iso.sh:100-105`**: this comment block argues with itself ("we honour it … well, actually we can't reliably tell") and has no code under it. It reads like a working note.
- **`claude-iso.sh:84-89`**: the comment says an explicitly set variable "is preserved" by "the documented contract". It is not preserved, as above.
- **`check-tool-updates.sh:164-169`**: the comment describes a lexical `<` comparison, but the code only tests `==`. Any difference prints "upgrade candidate", including an upstream that is *older* than the pin, or a tag spelled differently.
- **`pinned-versions.toml:42-43`**: says "The check script uses [`pinned_at`] as the minimum age the entries below claim to satisfy." `read_pinned` never reads `pinned_at`.
- **`secure-agent-setup.md:69` (and TOC line 7)**: the heading says "Three-layer defence", but the table under it has four layers (0–3). The commit message also says "four layers".
- **`secure-agent-setup.md:218`**: the comment says "network egress via Bash bypasses the sandbox proxy". Lines 74 and 236-241 say the sandbox governs Bash subprocesses, and `allowedDomains` only means something if Bash traffic goes through the proxy. The doc contradicts itself.
- **`secure-agent-setup.md:236-241`** (and line 214): says `~/.config/gh/` and `~/.config/apache-steward/` can be used by subprocesses but the agent "should never *see*" them. `sandbox.allowRead` lets the agent's own Bash tool `cat ~/.config/gh/hosts.yml` (or run `gh auth token`), and that output lands in the context. The `Read(...)` deny covers only the Read tool. This rests on the upstream permissions docs; I did not verify it against 2.1.117.
- **`secure-agent-setup.md:264-267`**: says the wrapper allows "only" a list of variables. The list leaves out `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which `claude-iso.sh:57-73` passes on.
- **`secure-agent-setup.md:163, 171-175`**: calls `/schedule` "the framework's" command (it is Claude Code's). It says the scheduled agent "runs in the same secure setup", but a scheduled cloud routine runs neither `claude-iso` nor the host's bubblewrap.
- **`check-tool-updates.sh:31-33`**: says "The README in this directory suggests wiring it to `/schedule weekly`". The walkthrough is in `secure-agent-setup.md`; the README only mentions it in passing.
- **`pinned-versions.toml:96-98`**: says `--no-save` keeps a global npm install from drifting a local lockfile. `-g` never touches a local lockfile. Taste.
- The claims about `pyproject.toml` (`exclude-newer = "7 days"`, the `uv` override), `.github/dependabot.yml` (7-day cooldown), `tools/gmail/oauth-draft`, `oauth-draft-create`, and the README anchor `#prerequisites-for-running-the-agent-skills` all check out against the tree.

## Item 2: claimed cases covered
Claimed cases (from the commit message) against what covers them:

| Claimed case | Covered by |
|---|---|
| Layer 0: env vars stripped | My stub run: `FOO` and `GH_TOKEN` dropped, `HOME` kept. No test in the repository. |
| Layer 0: `CLAUDE_ISO_ALLOW` brings one variable in | My stub run: `GH_TOKEN` passed on. No test in the repository. |
| Layers 1–3 enforced | Nothing. The commit says the "first invocation after merge will exercise it". |
| Check script: prints only candidates newer than the pin and past the cooldown | Nothing for "newer": the code does not compare order (Item 1). A pasted run shows only the "up to date" case. |
| Check script has no side effects | Read from the source: it only calls `curl`, `python3`, and `printf`. |
| Pins are at least 7 days old | Manifest dates against `pinned_at = 2026-04-29`: holds, with claude-code at exactly 7 days. |

Commands the change tells someone to run:

| Command | Promised outcome | What runs that form | What it depends on |
|---|---|---|---|
| `source …/claude-iso.sh` from `~/.bashrc` **or `~/.zshrc`**, then `claude-iso` | A Claude session with a clean env | My run only | **bash sourced**: `exec` replaces the user's interactive shell, so the shell closes when Claude exits (the stub printed nothing after `claude-iso`). **zsh sourced**: `claude_iso_main:37: bad substitution` (`${!var}` is bash-only). zsh is the macOS default, and the doc says macOS is supported. **Substantive.** |
| `bash claude-iso.sh [args]` | Same | My run | Works. |
| `bash check-tool-updates.sh` (also via `/schedule`) | Status table | Pasted run in the commit (host not stated, apparently Linux) | `tac` and `date -d` are GNU-only. On stock macOS, `/bin/date -d` fails ("illegal option"), and there is no `/usr/bin/tac`, so the socat row always reports "lookup failed (rate limit / network)", which is wrong. `tomllib` needs Python ≥ 3.11. Inside the repository's own sandbox, `www.dest-unreach.org` is not in `allowedDomains`. Not verified on Linux. |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` | Pinned install | none | It needs the distribution to carry those exact versions, and apt to accept `=ver-*` globs. Not verified. Current Debian/Ubuntu stable ship older versions of both. |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | Pinned install | none | Repository availability. Not verified. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | Pinned runtime | none | Not verified (no network). |
| Verification block (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com`) | Each one denied | none | The sandbox and the deny rule. Not run. |
| `git check-ignore .claude/settings.local.json` | "Claude Code does this by default" | none | Not verified. |

The commit also contradicts itself on socat. The manifest says released `2026-03-13`; the pasted run shows the upstream tarball dated `2026-02-12`.

## Item 3: boundaries, partitions, and the negative control
Partitions are shells × run modes for the wrapper, platforms for the check script, and upstream states for the comparison.

- **Wrapper:** the zsh-sourced and bash-sourced partitions are broken (Item 2), and nothing in the change exercised them.
- **Check script:** for the comparison, the partitions "upstream older than pin" and "upstream is a prerelease" are uncovered. `gh_latest_aged` does not skip `prerelease` or `draft` entries. The only control is the "up to date" run.
- **Platform:** the macOS partition of the check script is untested, and it misreports (Item 2).
- **State left behind:** an adopter who already has a `.claude/settings.json` gets no merge guidance. Step 2 of the adopter setup says to "copy" over it.

## Item 3a: level, placement, and the environment
Analogue: where each rule lives and what the repository's gate checks.

- There are no tests, and there is no CI job for the shell scripts. Two small offline checks would fit: the status comparison (feed stub upstream lines) and the env filtering (a stub `claude`, as I did).
- The new directory sits as a sibling of the existing `tools/*` adapters, and its README explains why it is not a Python project. Placement is fine.
- I did not run `prek run --all-files`.

## Item 4: names by content, not by position
- `secure-agent-setup.md:174`: "per step 5 above" names a step by its number. Name it by content ("the bump PR") instead.
- Nothing else found in the headings or the cross-references.

## Item 5: the failure report
Analogue: what each rule tells the reader to look at.

- The check script prints "upstream lookup failed (rate limit / network)" for *every* lookup failure. On macOS the cause is the missing GNU tools, so the message sends the reader to the wrong cause.
- The Verification section names the denial expected for each command. Good.

## Item 6: what the writer says it verified
- The commit pastes one check-script run (all "up to date"), a JSON parse, and `prek`.
- There is no run of `claude-iso` in any mode, and no evidence for layers 1–3. The commit says so itself.
- Nothing shows that a rule can fail: no "upgrade candidate" run, no denied command.

## Item 7: siblings of the change
I searched `.claude/skills`, `tools`, and `projects` for the hosts the framework reaches and for `curl` use.

- **Substantive:** `sync-security-issue/SKILL.md:873` and `tools/cve-org/tool.md:66,90` run `curl -sSf https://cveawg.mitre.org/...`. The settings deny `Bash(curl *)`, and `cveawg.mitre.org` is not in `allowedDomains`.
- **Substantive:** `sync-security-issue/SKILL.md:284,624` curl `lists.apache.org` and `cveprocess.apache.org`, which the same deny rule blocks.
- **Substantive:** `allocate-cve/SKILL.md:138` suggests `curl … astral.sh`, which is blocked too.
- `services.nvd.nist.gov` (one reference) is also outside the allowlist.

So the dogfooded config breaks the framework's own skills. The doc's statement that the allowlist is "every host the framework legitimately reaches" (`secure-agent-setup.md:201`) is false.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Sourcing the wrapper and running `claude-iso` ends the user's shell, because of `exec` inside a function | Substantive | `claude-iso.sh:107,115-117` | Run `env -i …` without `exec` in the sourced path, or run it in a subshell. |
| The wrapper fails in zsh (`bad substitution`), yet the doc says to source it from `~/.zshrc` | Substantive | `claude-iso.sh:80`; `secure-agent-setup.md:252` | Make it portable, or document "bash only, run as `bash claude-iso.sh`". |
| The header's `GH_TOKEN=… claude-iso` / `AWS_PROFILE=… claude-iso` forms silently drop the variable | Substantive | `claude-iso.sh:39-41` | Use the `CLAUDE_ISO_ALLOW=` form. Remove the self-contradicting comment at 84-89 and 100-105. |
| `curl` deny plus a missing `cveawg.mitre.org` break `sync-security-issue` and the cve-org check | Substantive | `.claude/settings.json:51,22-36` | Allow those hosts and the skills' `curl` forms (or move them to `ask`), or change the skills. Then fix the "every host" comment. |
| The "bypasses the sandbox proxy" rationale contradicts the doc's own model | Substantive | `secure-agent-setup.md:218` | State the real reason for the deny, or drop it. |
| "Agent should never see" the gh and OAuth credentials is not true for the agent's Bash tool | Substantive | `secure-agent-setup.md:236-241` | Restate what the split actually prevents (the Read tool only). |
| Version comparison is `==` only; the comment describes `<`; older or prerelease upstreams print "upgrade candidate" | Substantive | `check-tool-updates.sh:161-170,66-80` | Compare in version order and skip prereleases, or fix the comment and the doc's "newer than the pin". |
| The check script is GNU-only (`tac`, `date -d`), and on macOS it misreports a network failure | Substantive | `check-tool-updates.sh:92,99-101` | Make it portable, or state "Linux only" and give a specific error. |
| The manifest claims the script uses `pinned_at`; it does not | Substantive | `pinned-versions.toml:42-43` | Fix the comment or implement the check. |
| "Three-layer" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | Rename it (and regenerate the TOC). |
| `/schedule` described as the framework's, and as running "in the same secure setup" | Substantive | `secure-agent-setup.md:163,171-175` | Correct both statements. |
| socat release date: `2026-03-13` in the manifest vs `2026-02-12` in the pasted run | Substantive | `pinned-versions.toml:67` | Confirm the date and fix one of them. |
| The apt, dnf, and npm pin commands were never run; they depend on the distribution carrying the versions | Substantive | `secure-agent-setup.md:113-137` | Run them on the supported distributions, or mark them as unverified. |
| No partition tests, and no evidence a rule can fail (upgrade-candidate run, a denial) | Substantive | `tools/agent-isolation/` | Add stub-based checks, or paste a red/denied run. |
| "Only" passthrough list omits `LC_*` and `WAYLAND_DISPLAY` | Substantive | `secure-agent-setup.md:264-267` | List them all. |
| "per step 5 above" names a step by its number | Taste | `secure-agent-setup.md:174` | Name the step by content. |
| `--no-save` rationale for a global install | Taste | `pinned-versions.toml:96-98` | Drop the flag or the comment. |
| Check-script header points to the README for `/schedule` | Taste | `check-tool-updates.sh:31-33` | Point to `secure-agent-setup.md`. |

Not checked: I ran neither the check script nor the install commands (no network), did not exercise layers 1–3 under a real sandbox, did not run `prek`, ran nothing on Linux, and did no style-only pass over the prose.
