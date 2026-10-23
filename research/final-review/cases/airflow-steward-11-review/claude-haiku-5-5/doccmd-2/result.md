## Final review: `2efe27f..HEAD` (commit `1b569a8`, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

**Setup.** No task statement was handed over, so the claimed cases come from the commit message, as the skill says. No previous report exists, so the §4 table is omitted. I loaded `final-review`, `english-developer-style`, and `test-authoring` from the provided skills directory. The change has no tests, so `test-authoring` was used only for the §2a analogues. `docs-page-authoring` and `apm-authoring` are not among the provided copies, so I did not load them. No doc-comment skill applies, since there is no code language here.

**Drift script.** `comment-drift.py 2efe27f… HEAD` exited 0 with no output. The change has no code members, so there was nothing to parse. The §2a analogues were used throughout.

**What I ran (read-only, offline):**
- `.claude/settings.json` parses as JSON. The deny (22), ask (14), allowRead (8), and domain (14) lists match the copy embedded in `secure-agent-setup.md`.
- `bash -n` and `shellcheck` are clean on both scripts.
- `claude-iso.sh` run with a stub `claude` that prints its environment. Results are in the item 2 and 3 notes below.
- `/bin/date -d` fails with "illegal option -- d". `tac` is present only through Homebrew. `sort -V` works.

**Not run:** the check script end to end (no network), `prek`, the real `claude` binary, the sandbox denials, and any Bash `cat` under Claude Code.

---

### Item 1: comments consistent with the code and with each other

Substantive findings F2, F3, F6, F7, F8, and F11 below. Each is a comment or cross-reference that contradicts the code or the file beside it. No narration of the change ("now", "no longer") was found in the new files.

### Item 2: claimed cases covered

There are no tests. The analogue is a run of each command the change tells someone to run.

| Command (where) | Promised outcome | Run here | Equivalent in CI or a script | Note |
|---|---|---|---|---|
| `python3 -c 'json.load(...)'` (commit test plan) | parses | ok | none | |
| `GH_TOKEN="$(gh auth token)" claude-iso`, `AWS_PROFILE=read-only claude-iso` (`claude-iso.sh:40–41`) | credential reaches the agent | **dropped** | none | F2 |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (doc:273–276) | credential reaches the agent | passes | none | the correct form |
| `source claude-iso.sh; claude-iso` (doc:251–261) | agent starts with passthrough env only | `GH_TOKEN`, `AWS_*`, `ANTHROPIC_API_KEY`, `TMPDIR` dropped; `HOME`, `PATH`, `SSH_AUTH_SOCK` kept | none | real `claude` not run |
| `bash tools/agent-isolation/check-tool-updates.sh` (commit, doc:144, README:47) | status table | not run (no network) | none | `date -d` and `tac` are GNU-only; see F5 |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (doc:136) | pinned install | not run | none | depends on npm |
| `apt-get install … bubblewrap=0.11.1-* socat=1.8.1.1-*` (doc:112–116) | pinned install | not run | none | apt wildcard pins not verified on any distro |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (doc:122–124) | pinned install | not run | none | not verified |
| `brew install socat` (doc:129) | install | not run | none | unpinned, as the doc admits |
| `/schedule weekly run …` (doc:167) | recurring run | not run | none | Claude Code command; F9 |
| verification block (doc:315–317): `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com` | denials, empty | the `echo` part passes (env stripped); the `cat` and `curl` parts not run | none | F14 |

For each `none`, the promised outcome depends on the sandbox and on Claude Code's rule engine, which I cannot run offline. For the check script, it depends on GNU `date`, GNU `tac`, network, and `python3` 3.11+ for `tomllib`.

Item 2 finding: the two header examples in `claude-iso.sh` promise an outcome the script does not deliver (F2).

### Item 3: boundaries, partitions, and the negative control

- **Control, run by me:** without `CLAUDE_ISO_ALLOW`, the variable is dropped. With `CLAUDE_ISO_ALLOW=GH_TOKEN`, it passes. This is the on/off pair for the wrapper, and both sides behave as the doc says.
- **Pre-existing state:** no run starts from an adopter's existing `.claude/settings.json` (F15). The doc's adopter step says to copy the file over the existing one. No run starts from a `claude` install other than the pin, and the wrapper does not check the version (F10).

### Item 3a: level, placement, and the environment

The wrapper's behavior is observable in one process with a stub `claude` on `PATH`, and no network is needed. No test or gate does that today. The repository's `.pre-commit-config.yaml` has no shellcheck hook, and no CI job touches `tools/agent-isolation/` (F14, F18). The check script depends on GNU userland, which the doc's macOS path does not account for (F5).

### Item 4: names by content, not by position

One hit: `secure-agent-setup.md:174` says "per step 5 above" (F11). Other "above" and "below" references in the new files point to named sections.

### Item 5: the failure report

`check-tool-updates.sh:153` reports the socat row as "upstream lookup failed (rate limit / network)". On this host the real cause is the `date -d` call, which `|| continue` at line 101 swallows (F5). The reader is sent to the wrong cause. The wrapper's "not found on PATH" message reports reason and action and is fine.

### Item 6: what the writer says it verified

The commit states that the sandbox enforcement has not been run and is deferred to the first post-merge invocation. That statement is honest. Two things are still unsupported. The doc's Verification block says "Each command should produce a denial", and that block was not run (F14). The wrapper's env-stripping claim has no run in the commit. I ran the wrapper part above.

### Item 7: siblings of the change

- **Embedded settings copy vs. `.claude/settings.json`:** the rule lists match today. The doc copy will drift on the next edit (F20).
- **`claude-iso.sh` header vs. the doc:** the header gives the broken form, and the doc gives the working form (F2).
- **`projects/_template/`:** it has no `.claude/` directory. AGENTS.md calls it the scaffold adopters copy, and the commit says adopters copy from the doc. Whether the template should carry the settings file is a decision for the writer (F19).
- **Dependabot and `pyproject.toml` cooldowns cited by the check script:** both exist. `pyproject.toml:65` has `exclude-newer = "7 days"`, and `.github/dependabot.yml` has the 7-day cooldowns.

---

## Report

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The doc says the agent cannot read the gh and Gmail-token paths. `permissions.deny` covers the Read tool only, and `allowRead` lets Bash read those paths. Nothing denies Bash `cat`, and `//**/.env` in the project tree is open the same way. This is the threat model's case 2. I could not run Claude Code here to confirm. | substantive | `secure-agent-setup.md:214`, `:236–241`; `.claude/settings.json:38–61` | Correct the annotation and add the residual risk, or route the credential through a narrow command only. Run `cat` on each path from the agent's Bash tool and paste the output. |
| F2 | `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=… claude-iso` inject nothing. Verified: `GH_TOKEN=x claude-iso` does not reach the child. | substantive | `tools/agent-isolation/claude-iso.sh:40–41` | Replace with the `CLAUDE_ISO_ALLOW` form the doc uses. |
| F3 | The comment says variables set on the invocation line are preserved. That is false (F2). The block below it says "we can't reliably tell", and it has no code. | substantive | `claude-iso.sh:85–87`, `:104–108` | Delete both claims and the dead block. Keep only the `CLAUDE_ISO_ALLOW` statement. |
| F4 | "The socket alone is harmless" is unsupported. Anything that can reach the agent socket can have it sign with loaded keys. Residual risks does not mention this. | substantive | `claude-iso.sh:73`; `secure-agent-setup.md:325–348` | State what the socket exposes and add it to residual risks, or drop the passthrough and say what breaks. |
| F5 | GNU-only `tac` and `date -d`. On this host `/bin/date -d` fails, and line 101 silently skips every socat version. Line 153 then blames "rate limit / network". The socat row in the commit was produced on a GNU host, and the doc presents macOS as a supported path without this caveat. | substantive | `check-tool-updates.sh:92`, `:101`, `:153` | Use a portable date parse, such as the `python3` the script already needs, and a `tac`-free loop. Make the failure message name the step. Or state Linux-only in both the README and the doc. |
| F6 | Status says "upgrade candidate" for any difference. A pin newer than the latest aged upstream would be reported as a downgrade. The comment describes a lexical `<` comparison the code does not make. | substantive | `check-tool-updates.sh:160–169` (comment `:163–167`) | Compare versions properly, or print "pin ahead of aged upstream". Fix the comment. |
| F7 | The heading says "Three-layer defence", but the table lists layers 0–3, and the commit message says four layers. | substantive | `secure-agent-setup.md:69` | Rename the heading to match the table. |
| F8 | Layer 2 says `permissions.deny` covers Read, Edit, Write, and Bash. There are no Edit or Write rules. | substantive | `secure-agent-setup.md:75` | Name only the rules that exist, or add the rules and test them. |
| F9 | "The framework's `/schedule`" is Claude Code's command, not the framework's. "The scheduled agent runs in the same secure setup" is asserted without evidence. A routine running elsewhere would have neither the host sandbox nor the pins. | substantive | `secure-agent-setup.md:163–172` | Attribute the command correctly. State where the routine runs, or drop the claim. |
| F10 | The doc says pinning stops `claude-code` drifting. The wrapper runs whichever `claude` is first on `PATH` and never checks its version. | substantive | `secure-agent-setup.md:98`; `claude-iso.sh:47` | Check `claude --version` against the pin in the wrapper, or soften the claim. |
| F11 | "Per step 5 above" is an ordinal reference. Step 5 of the bump procedure opens the PR. It does not state the maintainer's confirmation the sentence attributes to it. | substantive | `secure-agent-setup.md:174` | Refer by section name, for example "per Bumping a pinned version above". |
| F12 | The doc's passthrough list omits `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`. `TMPDIR` is dropped, which I saw in the run, and nothing says so. Effect on macOS temp paths not verified. | substantive | `secure-agent-setup.md:264–266`; `claude-iso.sh:56–74` | Make the doc list match the script. Say whether `TMPDIR` is intentionally dropped, and test a temp write from the wrapped session. |
| F13 | README calls bubblewrap and socat "required system tools". The doc says macOS needs neither, and socat is optional there. | substantive | `README.md:164–165`; `secure-agent-setup.md:127–130` | Qualify by platform. |
| F14 | Nothing in the change has been run. The Verification block, the `claude-iso` env claim, and the check script's "end-to-end" output are unverified in this commit. The check's output in the commit cannot be reproduced offline. | substantive | `secure-agent-setup.md:307–323`; commit test plan | Run the three Verification commands on a host and paste the output, plus the F1 `cat` cases. Add a stub-`claude` env check for the wrapper, as I ran above. |
| F15 | The adopter step says to copy `settings.json` over the tracker's file, with no merge instruction. The example block is JSONC with `//` comments, so pasting it yields invalid JSON. | substantive | `secure-agent-setup.md:183–233`, `:289–292`; `tools/agent-isolation/README.md:55` | Say to merge the keys into an existing file. Say to strip comments, or provide plain JSON. |
| F16 | Layer 3 is described as covering visible-to-others writes. `gh pr comment`, `gh pr review`, `gh issue reopen`, and `gh release edit` are not in `ask`. | substantive | `.claude/settings.json:62–75` (`permissions.ask`) | Add them, or narrow the claim to the listed commands. |
| F17 | The socat `released` date (2026-03-13) disagrees with the upstream date for the same version in the commit's own output (2026-02-12). The source of 2026-03-13 is not given. | substantive | `pinned-versions.toml:67–69`; commit table | State the source of each `released` date, or correct it. |
| F18 | No shellcheck or `bash -n` hook, and no CI for the two scripts. | taste | `.pre-commit-config.yaml` | Consider adding a shellcheck hook. The author may decline. |
| F19 | `projects/_template/` has no settings file, and the commit does not say whether it should. | taste | `projects/_template/` | Decide whether the adopter scaffold carries the settings file. |
| F20 | The doc embeds a second copy of `settings.json`. It matches today, and it will drift on the next edit. | taste | `secure-agent-setup.md:183–233` | Consider linking to the file instead of copying it. |

**Not checked:** the check script end to end (no network), `prek run --all-files`, the real `claude` binary, the sandbox and permission behavior under Claude Code, the Linux `apt` and `dnf` install commands, and the impact of dropping `TMPDIR` on macOS. No files were changed and nothing was committed.
