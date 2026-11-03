# Final review: `2efe27f..HEAD`, one commit (`1b569a8`, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest")

**Scope and method.** No task statement was handed over, so the claimed cases come from the commit message alone. The change mixes docs (`secure-agent-setup.md`, `tools/agent-isolation/README.md`, the `README.md` hunk), an instruction file (the `AGENTS.md` hunk), a configuration (`.claude/settings.json`, `pinned-versions.toml`) and two bash scripts. The docs and configs are reviewed through the §2a analogues. The scripts have no tests, so their items were filled by reading the code and running small local probes. I loaded `english-developer-style` and `apm-authoring`, plus `test-authoring` for the scripts. `comment-drift.py 2efe27f HEAD` ran and printed nothing, because it does not parse bash, JSON, TOML or Markdown. `bash -n` and `shellcheck` pass on both scripts.

**Overall:** the shell wrapper and the update-check script each have bugs I confirmed by running them. Several claims in the setup page and the script comments are false, and none of the security controls the page promises has been run.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **`claude-iso.sh:39-41`**: the header says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` inject a credential. The code drops both unless `CLAUDE_ISO_ALLOW` names them. I ran the header's form and `GH_TOKEN` was absent from the child environment (0 matches); the `CLAUDE_ISO_ALLOW=GH_TOKEN` form passed it through. `secure-agent-setup.md:273` gives the correct form, so the two files disagree.
- **`claude-iso.sh:84-90`**: says "any env var that the user set on the *invocation* line … is preserved". That is false for the same reason.
- **`claude-iso.sh:103-108`**: a comment that contradicts itself ("We can tell … well, actually we can't reliably tell") and sits above no code. It records a design hesitation, not a fact about the code.
- **`check-tool-updates.sh:163-167`**: describes a "plain `<`" version comparison. The code only tests `==`, so any difference, including an upstream release older than the pin, is reported as "upgrade candidate".
- **`pinned-versions.toml:42-43`**: "The check script uses this [`pinned_at`] as the minimum age…". The script never reads `pinned_at`; `read_pinned` reads only `version` and `released`.
- **`pinned-versions.toml:96-98`**: says `--no-save` keeps the global install from drifting "the local lockfile". A `-g` install never touches a project lockfile, so the flag has no effect and the reason given is false.
- **`secure-agent-setup.md:69` vs `:71-76` and the commit message**: the heading says "Three-layer defence", while the table has four rows (layers 0 to 3) and the commit message says "four layers".
- **`secure-agent-setup.md:74` and `:39-42`**: say layer 1 stops "Bash subprocess reads outside the project tree" and reduces the risk "to the project tree". `denyRead` is only `~/`, so `/etc`, `/opt`, `/tmp` and other non-home paths stay readable, as do the eight `allowRead` home paths.
- **`secure-agent-setup.md:179-181`**: says "The full block is below". The block leaves out `$schema` and the separate `git push --force*` entries that are in `settings.json`.
- **`secure-agent-setup.md:163`**: calls `/schedule` "The framework's `/schedule` slash-command". It is Claude Code's built-in command; the framework ships no such command.
- **`secure-agent-setup.md:66-67`, `:347`**: tell readers to audit `~/.claude/.mcp.json`. User-scope MCP servers are configured in `~/.claude.json`, so the first path is likely not a real location. This is plausible, not verified.
- **`secure-agent-setup.md:236-241` (plausible)**: says `sandbox.filesystem.allowRead` lets Bash read `~/.config/gh/` while `Read(~/.config/gh/**)` blocks only the agent's Read tool. This review's own session runs with this `settings.json`, and its sandbox list carries `~/.config/gh` and `~/.config/apache-steward` in **both** the denied paths and the allowed-within-deny paths, along with the `.env` globs taken from the `Read(...)` rules. So Read deny rules are merged into the sandbox. Whether `gh` can still read `hosts.yml` has not been shown.

## Item 2: claimed cases covered

**Cases the commit message claims, and what covers each:**

| Claim | Evidence |
| --- | --- |
| Layer 0 strips credential env vars | Correct for bash when run directly (probe: `FOO_SECRET` dropped). Broken when sourced, and under zsh (Item 3). |
| Layers 1–3 enforce what the table says | No run. The commit message says enforcement is not exercised ("first invocation … after merge"). |
| Layer 3 asks before "visible-to-others writes" | The skills' own forms do not match the ask rules (Item 7). |
| Check script lists only aged releases newer than the pin | Not true: it uses inequality, not "newer" (Item 1). |
| Check script is side-effect free | Holds; the code only reads and prints. |
| Scheduled weekly routine via `/schedule` | No run. In the documented sandbox, `www.dest-unreach.org` is not in `allowedDomains`, so the socat lookup always fails there. |
| `settings.json` parses as JSON | Holds. |
| The pinned `released` dates | Contradicted: the commit message's own output shows socat `UPSTREAM@ 2026-02-12` against the manifest's `released = "2026-03-13"`. |

**Commands the change tells readers to run:**

| Command | Documented outcome | Run anywhere? | Depends on |
| --- | --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:113-117`, `tools/agent-isolation/README.md`) | Pinned install | none | Whether the distro archive carries those exact versions. Older Debian/Ubuntu releases ship older bubblewrap, so `apt` refuses an unknown version. |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | Pinned install | none | Same: the Fedora/RHEL repository contents. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | Pinned runtime | none | Claude Code's auto-updater. Nothing in `settings.json` (no `autoUpdates: false` or `env.DISABLE_AUTOUPDATER`) or in `claude-iso` (which strips env) turns it off, so the pin likely drifts on first launch. The manifest's own purpose text (`:84-90`) is about preventing exactly that. |
| `source …/claude-iso.sh` from `~/.zshrc`, then `claude-iso` | Clean-env session | none | The shell. Under zsh it fails with `claude_iso_main:37: bad substitution` (verified). |
| `/schedule weekly run …check-tool-updates.sh` | Weekly candidates | none | The sandbox network allowlist, as above. |
| The three verification commands (`:313-318`) | Each denied | none | Not run. |
| `git check-ignore .claude/settings.local.json` | Ignored | none | Whether the adopter's `.gitignore` covers it. |

**Hunks read the other way:** every hunk maps to a sentence of the commit message. None is unclaimed.

## Item 3: boundaries, partitions, and the negative control

- **Platform partition for `check-tool-updates.sh`.** The page claims macOS support. On macOS, `date -d` is GNU-only (I confirmed `date: illegal option -- d`), so every socat row prints "upstream lookup failed". `tac` is also missing from stock macOS. Only Linux was exercised.
- **Shell partition for `claude-iso.sh`.** The page says `~/.bashrc or ~/.zshrc`. Under zsh it fails (verified).
- **Sourced vs executed.** When sourced, `claude-iso` runs `exec env -i …` inside the interactive shell, so the user's shell is replaced and the tab closes when claude exits. Verified: "shell survived" never printed after the call under bash.
- **Invalid partition: broken manifest or Python < 3.11 (no `tomllib`).** `read_pinned` fails inside the process substitution, `set -e` does not catch it, and the script prints an empty table and exits 0. Verified with an invalid manifest: traceback on stderr, `rc=0`.
- **Limits.** None of the `curl` calls in `check-tool-updates.sh` has `--max-time`, including the per-tarball `HEAD` loop, so a stalled host blocks the run until whatever wraps it (a `/schedule` routine) times out. Nothing bounds the whole run.
- **Pre-existing state, sandbox writes (plausible).** The sandbox allows reads only for `~/.cache/uv`, `~/.local/share/uv` and `~/.local/bin`, and allows no home-directory writes. `uv run` (used by `generate-cve-json`), `prek` (which keeps its cache under `~/.cache/prek`), and the Gmail token refresh under `~/.config/apache-steward` all likely need to write or read there. None was run inside the sandbox.

**Added instructions** (the `AGENTS.md` hunk is the only instruction-file change):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | An agent reading `AGENTS.md` inside a session that has already started | Nothing it can act on: the session's launch is already fixed, yet the paragraph loads every turn | "for the human starting a session:", or move it to `README.md`, which already carries it |

Not findings: none.

## Item 3a: level, placement, and the environment

The scripts sit in a new `tools/agent-isolation/` directory, a layout that matches the other `tools/*` adapters. No CI job or `prek` hook runs `shellcheck` or `bash -n` on them. The other tool directories get ruff, mypy and pytest hooks. I ran the repository's gate equivalents offline (`bash -n`, `shellcheck`): both clean. The finding is that no CI job keeps them so.

## Item 4: names by content, not by position

`secure-agent-setup.md:174` says "per step 5 above". Step 5 is "Open the bump as its own PR", so name it that way rather than by its number. Otherwise none; headings and anchors are named by content, and all links resolve (I checked the `README.md#prerequisites-for-running-the-agent-skills` and `AGENTS.md#confidentiality-…` anchors).

## Item 5: the failure report

- **`check-tool-updates.sh`** reports every failed lookup as "upstream lookup failed (rate limit / network)". That includes the macOS `date -d` failure and a host missing from the allowlist, which are neither, so the message points the reader at the wrong cause. A broken manifest prints nothing but a traceback and exits 0.
- **`claude-iso.sh`** has a good failure message for a missing `claude` binary. Under zsh, the only output is the shell's own "bad substitution".

## Item 6: what the writer says it verified

The commit message states three runs: `prek`, the check script on the author's Linux host, and the JSON parse. It states no run of any denial (layers 1–3), no zsh or sourced-mode run of `claude-iso`, and no install command. It says outright that sandbox enforcement is untested. No negative case for any control is named.

## Item 7: siblings of the change

- **Ask rules vs the skills' own commands.** `Bash(gh api * -X *)` needs at least one argument between `gh api` and `-X`. The skills write `gh api -X PATCH repos/<tracker>/issues/comments/<id> --input …` and `gh api -X DELETE …` (`sync-security-issue/SKILL.md:1353,1390,1694`, `invalidate-security-issue:482`, `allocate-cve:487`, `deduplicate-security-issue:385,405`). That form matches no ask rule. Also not covered: `gh label create`, `gh repo fork`, `gh issue reopen`, and `git -C <dir> push`. The `fix-security-issue` form `gh api repos/… -X PATCH -F …` does match.
- **`allowedDomains` vs hosts the change itself contacts.** `www.dest-unreach.org` (the check script) is missing.
- **Root-file list.** `AGENTS.md:79-86` ("Repo-root files") lists the other root docs but not `secure-agent-setup.md`. `AGENTS.md:88` ("There is no source code to build or test") no longer holds now that the repo ships two scripts.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Sourced `claude-iso` replaces the interactive shell (`exec`) | Substantive | `claude-iso.sh:111` | Run `env -i …` without `exec` in the sourced path |
| `claude-iso` fails under zsh, which the page recommends | Substantive | `claude-iso.sh:79`; `secure-agent-setup.md:252` | Make it zsh-safe, or limit the page to bash |
| Header and comment say invocation-line vars pass through; they do not | Substantive | `claude-iso.sh:39-41,84-90,103-108` | Use the `CLAUDE_ISO_ALLOW` form; delete the stale and self-contradicting comments |
| The claude-code pin is likely undone by the auto-updater | Substantive (plausible) | `settings.json`; `pinned-versions.toml:84-98` | Disable auto-update in `settings.json`, or state the limit |
| Ask rules miss the skills' `gh api -X …`, `gh label create`, `gh repo fork`, `gh issue reopen`, `git -C … push` | Substantive | `settings.json:64-76` | Add `Bash(gh api -X *)` and the rest, or narrow the layer-3 claim |
| Read deny rules may block the `gh`/oauth-draft reads the page calls deliberate | Substantive (plausible) | `secure-agent-setup.md:236-241` | Run `gh auth status` in the sandbox and report |
| `uv`, `prek` and the token refresh need home-directory access the sandbox may not grant | Substantive (plausible) | `settings.json:5-17` | Run `uv run …generate-cve-json` and `prek run` in the sandbox |
| Check script fails on macOS (`date -d`, `tac`) | Substantive | `check-tool-updates.sh:91,100-102` | Make the date parsing portable, or declare it Linux-only |
| socat host not allowlisted, so the scheduled check always fails there | Substantive | `settings.json:20-35`; `secure-agent-setup.md:171` | Allowlist the host, or correct the page |
| Broken manifest gives exit 0 and an empty table | Substantive | `check-tool-updates.sh:117,175` | Read the manifest before the loop and fail on error |
| Comment claims a `<` comparison the code does not make | Substantive | `check-tool-updates.sh:163-167` | Compare versions, or say it only flags inequality |
| `pinned_at` said to be read by the script; it is not | Substantive | `pinned-versions.toml:42-43` | Fix the comment |
| "Three-layer" heading over four layers | Substantive | `secure-agent-setup.md:7,69` | "Four-layer" |
| Layer 1 overstated as blocking "outside the project tree" | Substantive | `secure-agent-setup.md:39-42,74` | Say "under `~/`, except the allowRead list" |
| "The full block" is not the full block | Substantive | `secure-agent-setup.md:179-234` | Match `settings.json`, or say "abridged" |
| socat `released` date contradicted by the script's own output | Substantive | `pinned-versions.toml:67` | Verify the date and fix one of the two |
| Pinned apt/dnf/npm commands never run on any distro | Substantive | `secure-agent-setup.md:110-137` | A run per distro, or name the distros where they work |
| No denial or verification command was run | Substantive | `secure-agent-setup.md:309-323` | Run them and state the output |
| `--no-save` with `-g` and its stated reason | Substantive | `pinned-versions.toml:94-98` | Drop the flag and its reason |
| No timeouts on the check script's `curl` calls | Substantive | `check-tool-updates.sh:66,89,96` | Add `--max-time` and an overall bound |
| Root-file list misses the new page; "no source code" now false | Substantive | `AGENTS.md:79-91` | Add the entry; reword the sentence |
| `/schedule` called "the framework's" command | Substantive | `secure-agent-setup.md:163` | "Claude Code's" |
| `~/.claude/.mcp.json` is likely not a real location | Taste (plausible) | `secure-agent-setup.md:67,347` | Point to `~/.claude.json` |
| `AGENTS.md` paragraph addresses the human, not the agent | Taste | `AGENTS.md:312-319` | Mark it as setup for humans, or keep it in `README.md` only |
| "the socket alone is harmless" for `SSH_AUTH_SOCK` | Taste | `claude-iso.sh:72` | Soften the claim |
| Deny comment says Bash `curl` bypasses the sandbox proxy | Taste | `secure-agent-setup.md:218` | Restate the reason |
| "per step 5 above" names a step by its number | Taste | `secure-agent-setup.md:174` | Name the step by content |

**Not checked:** no network was available, so I verified no upstream version, release date, distro archive or live Claude Code behavior. The sandbox, permission-merge and auto-updater findings come from this session's sandbox config and Claude Code's known defaults, not from a run. I did not do a style pass over the prose.
