# Final review of `2efe27f..HEAD` (`ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)`)

**Inputs.**
- I read the diff in full: 8 files, all added except `AGENTS.md` and `README.md`, which gained a paragraph each.
- No task statement was handed over, so the claimed cases come from the commit message alone.
- I loaded `english-developer-style` and `apm-authoring` from the supplied skills directory. `AGENTS.md` is an instruction file, so `apm-authoring` applies to it.
- I did not load `test-authoring`, because the change has no tests.
- The change has shell scripts, JSON, TOML and Markdown. I ran `comment-drift.py 2efe27f HEAD`, and it printed nothing. Every file is new, or is prose that has no members. Item 1 therefore reads the comments by hand.
- `bash -n` is clean on both scripts, `shellcheck` reports nothing, the TOML and JSON parse, and the `README.md` anchor `#prerequisites-for-running-the-agent-skills` exists.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement a changed file makes about the code, another file, or the repository.

- **`claude-iso.sh:29-30` and the doc contradict the code.**
  - The header says to inject a credential with `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso`, with no `CLAUDE_ISO_ALLOW`.
  - Lines 78-82 say a variable set on the invocation line "is present in our env exactly when it was passed explicitly", and the code never honors that.
  - I ran `GH_TOKEN=abc claude-iso` against a stub `claude`. It printed 0 `GH_TOKEN` lines. With `CLAUDE_ISO_ALLOW=GH_TOKEN` it printed one.
  - The comment at lines 95-100 then says the opposite, so the file contradicts itself.
  - Request: delete the "invocation line" paragraph and the two header examples. Show only the `CLAUDE_ISO_ALLOW` form, as `secure-agent-setup.md:273` does.
  - **Substantive.**
- **`check-tool-updates.sh:153-156` describes a comparison that is not there.** The comment says "this lexical comparison is a heuristic… plain `<`". The code uses `==`, so any difference is reported as an "upgrade candidate". That includes an upstream version older than the pin. Request: fix the comment or implement the comparison. **Substantive.**
- **`pinned-versions.toml:36-37` says the check script uses `pinned_at`.** The script never reads it. Request: drop the sentence. **Substantive.**
- **The socat release date contradicts the commit's own output.**
  - The manifest and the doc say socat 1.8.1.1 was released 2026-03-13.
  - The commit message's script output shows `PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12` for the same version.
  - One of the two dates is wrong. The 7-day cooldown claim for socat depends on which.
  - Request: reconcile them. Say whether `released` means the tarball's `Last-Modified` or the announcement date, and use the same source in the manifest and the script.
  - **Substantive.**
- **`secure-agent-setup.md:69` says "Three-layer defence".**
  - The table below it lists layers 0 to 3, and the commit message says "four layers".
  - Request: rename the heading to "Four-layer defence" and update the TOC entry. **Substantive.**
- **The doc says "The full block is below" (`secure-agent-setup.md:180`).**
  - The block omits `$schema` and the `git push --force*` ask entries that `.claude/settings.json` has.
  - It is behaviorally equivalent, so I label this taste. I would say "abridged".
  - **Taste.**
- **The macOS note disagrees across files.**
  - The `toml` says socat is "Linux only; macOS does not need it".
  - The doc says socat is "optional" on macOS.
  - **Taste:** pick one.
- **`npm install -g --no-save` is explained in `pinned-versions.toml:98-100` as keeping "the local lockfile" from drifting.** `--no-save` does not apply to a global install, so the rationale describes nothing. It appears at three sites. **Taste:** drop the flag and the comment.
- **Narration.** I found no `now`, `no longer`, or `used to` in the added text.

## Item 2: claimed cases covered

Analogue used: claimed cases and commands the artifact tells a reader to run. Command lines are listed with the script or job that runs the same form.

The commit message claims four layers, the 7-day cooldown, a side-effect-free check script, a `/schedule` routine, and the adopter scaffold. Its test plan claims `prek`, a check-script run, and JSON validity. It also says the sandbox is unverified.

| Command or claim | Outcome promised | Runs in CI or a script |
| --- | --- | --- |
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` | installs the pinned versions | none |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` | same | none |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | installs the pin | none |
| `source claude-iso.sh` from `~/.zshrc`, then `claude-iso` | clean-env launch | none |
| `/schedule weekly run check-tool-updates.sh` | surfaces candidates | none |
| Verification block (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl …`) | denials | none |

- **The apt and dnf pins depend on what the distro's repositories carry.**
  - A `bubblewrap=0.11.1-*` request on Debian or Ubuntu fails with "version not found" unless a repository ships that version.
  - Nothing in the change shows it does.
  - I could not check this offline. It is still a substantive request: either name the releases the pins were checked against, or tell the reader how to proceed when the pin is unavailable.
  - **Substantive.**
- **The weekly routine cannot succeed as documented for socat.**
  - The doc says the scheduled agent "runs in the same secure setup". That setup's `allowedDomains` does not list `www.dest-unreach.org`, the host `socat_latest_aged` queries over plain HTTP.
  - The lookup fails and the table reports `upstream lookup failed`.
  - Request: add the host to `allowedDomains`, or drop socat from the weekly check and say so. **Substantive.**
- **The check script does not work on the macOS host the doc supports.**
  - `date -d` is GNU-only. On macOS 25 it fails with `date: illegal option -- d`.
  - `tac` happened to exist in this environment through Homebrew.
  - On stock macOS the socat lookup falls through to `|| continue` and reports "lookup failed" for every candidate.
  - The commit's test plan ran it once, on an unstated platform.
  - Request: state that the script needs GNU coreutils, or avoid `date -d` and `tac`. **Substantive.**
- **`source claude-iso.sh` from `~/.zshrc` fails.**
  - `secure-agent-setup.md:252` tells readers to put it in `~/.bashrc or ~/.zshrc`.
  - I ran it under zsh with a stub `claude` on `PATH`, and it stopped with `claude_iso_main:37: bad substitution`. That is the `${!var-}` expansion, which is bash-only.
  - macOS defaults to zsh, and this was run on macOS.
  - Request: remove `~/.zshrc` from the doc and say the wrapper needs bash, or make the loop zsh-safe. **Substantive.**
- **The Verification block's `echo $AWS_ACCESS_KEY_ID`** is a check I could not run. I list it as the `none` row above and do not rate it separately.
- **Hunks beyond the claim.** I found none. The `AGENTS.md` and `README.md` additions are claimed in the commit message.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the partitions the change claims, the negative control, and pre-existing state. There are no tests and no negative-control trial.

- **Partitions claimed without evidence.**
  - The commit claims Linux (bubblewrap and socat) and macOS (Seatbelt). Its only run was the check script, and it names no platform. The sandbox enforcement is explicitly untested, and so is `claude-iso`.
  - Neither the Linux nor the macOS partition of the wrapper or the sandbox has a run.
  - Request: add one end-to-end run on each platform of the Verification block, or state in the doc that it is unverified. **Substantive.**
- **The negative control is missing.**
  - Verification shows only denials. It has no step that shows the allowed paths still work.
  - It has no check that `gh` still authenticates inside the sandbox, or that `uv` still reads `~/.cache/uv`. `allowRead` lists these paths, so each one is a claim.
  - Request: add one allowed-path check per listed category. **Substantive.**
- **Env-stripping side effects.**
  - `env -i` also drops `TMPDIR`, `ANTHROPIC_API_KEY` and other variables the agent may need, so a user who authenticates by API key cannot start a session.
  - `TMPDIR` is dropped on macOS.
  - The doc does not mention either.
  - Request: add one sentence on authentication, pointing to `CLAUDE_ISO_ALLOW=ANTHROPIC_API_KEY` if that is the intended route. **Substantive.**
- **Pre-existing state.**
  - Adopters who already have a `.claude/settings.json` are told to "copy" the file, which overwrites theirs.
  - Request: say to merge the `sandbox` and `permissions` keys. **Substantive.**
- **Existing setting reaching a new consumer.** `CLAUDE_ISO_ALLOW` is a new variable and no other consumer reads it. None.
- **Replaced mechanism.** None.
- **Limits.** None set in this change.

Added instructions (`AGENTS.md` and `README.md` are the only instruction-bearing files; the `README.md` paragraph is documentation addressed to the reader).

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a docs-only edit of the framework repo with no tracker content | a warning or refusal about the setup that the agent cannot act on, since it cannot change how it was launched | "only for sessions that read tracker or `<security-list>` content" |

Added instructions: 1, 1 row. Not findings: `AGENTS.md:318` (a link, not an instruction).

## Item 3a: level, placement, and the environment

Analogue used: which file each rule lives in, layout against siblings, and the repository's own gate.

- **Placement.**
  - `tools/agent-isolation/` follows the `tools/<name>/` pattern. Its README says it is "not a Python project", which is accurate.
  - The `pre-commit` config runs no hook on shell scripts, so `shellcheck` is not a gate. I ran it by hand and it was clean.
- **`.claude/settings.json`.** The file is in the registration location. The repository's gate does not validate its keys.
- **The `pre-commit` hooks** (`doctoc`, whitespace) are claimed passed. I did not re-run them, and the commit's claim stands unverified.
- None.

## Item 4: names by content, not by position

Analogue used: headings, cross-references, case names.

- The "Three-layer" heading is a count that went stale. It is filed under Item 1 and is not repeated here.
- The step references "per step 5 above" (`secure-agent-setup.md:174`) point by ordinal. The step is "open the bump as its own PR". **Taste:** name it.
- None otherwise.

## Item 5: the failure report

Analogue used: what a rule tells the reader to look at, and what a failure looks like.

- **The Verification block's expectations are not distinguishable.**
  - `cat ~/.aws/credentials # → permission denied (sandbox)` and the `curl` line (denied by `permissions.deny`) name different layers.
  - An empty `echo` and a missing variable look alike.
  - The doc does not say which message identifies which layer failing.
  - Request: for each command, name the layer that should produce the denial and its message. **Substantive.**
- **`check-tool-updates.sh` prints one status string for every failure.** "Upstream lookup failed (rate limit / network)" also covers the `date -d` and `tac` failures above. An operator would be sent looking at the network. **Substantive:** print the failing tool or step.

## Item 6: what the writer says it verified

Analogue used: the exemplar the change shows passing and the bad case it shows failing.

- The commit shows the check script's output and a JSON parse, and says plainly that sandbox enforcement is unverified.
- It gives no run of `claude-iso.sh` and no negative case for either script. The zsh failure, the `CLAUDE_ISO_ALLOW`-less invocation and the macOS `date` failure all passed unnoticed for that reason.
- The `comment-drift` script was not part of the change.

## Item 7: siblings of the change

Analogue used: places that enumerate or route to the artifact.

- **`AGENTS.md` "References" and "Reusable skills".** The `tools/` bullet list (`AGENTS.md:1130-1131`) names `tools/github`, `tools/gmail`, `tools/vulnogram` and `tools/cve-org`. It does not name the new `tools/agent-isolation/`. **Substantive:** add a bullet.
- **`README.md`** references the doc from the prerequisites section, as the commit says.
- **`AGENTS.md:53` (repository layout)** lists repo-root files and does not list `secure-agent-setup.md`. Request: add it. **Substantive.**
- **The tracker-adopter docs** that say how to scaffold `<project-config>` (`projects/_template/`) do not mention the `.claude/settings.json` copy. **Taste.**
- **Cooldown convention sites.**
  - `pyproject.toml` has `exclude-newer = "7 days"`, so the doc's claim holds.
  - `.github/dependabot.yml` has `cooldown: default-days: 7`.
  - But `exclude-newer-package = { uv = "1 day" }` (`pyproject.toml:76`) is an exception to the "7-day" convention. The doc and manifest mention only a "per-package override for `uv`" in the commit message and not in the files.
  - **Taste:** note the exception.
- **Symptom paths.** The remedy for `upstream lookup failed` names "rate limit / network" only. The causes found above (GNU `date`/`tac`, allowlist) are not named. Covered under Item 5.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Invocation-line credential injection documented but not implemented; the file contradicts itself | Substantive | `tools/agent-isolation/claude-iso.sh:29-30,78-82` | 1 |
| Comment describes a lexical `<` comparison; code uses `==` | Substantive | `tools/agent-isolation/check-tool-updates.sh:153` | 1 |
| Manifest says the script uses `pinned_at`; it does not | Substantive | `tools/agent-isolation/pinned-versions.toml:36` | 1 |
| socat release date 2026-03-13 contradicts the script's 2026-02-12 | Substantive | `tools/agent-isolation/pinned-versions.toml:75` | 1 |
| "Three-layer" heading over a four-layer table | Substantive | `secure-agent-setup.md:69` | 1 |
| "Full block" is abridged | Taste | `secure-agent-setup.md:180` | 1 |
| macOS socat: "Linux only" vs "optional" | Taste | `pinned-versions.toml:79`, `secure-agent-setup.md:127` | 1 |
| `--no-save` rationale does not apply to a global install | Taste | `pinned-versions.toml:98` | 1 |
| apt and dnf pins may not exist in distro repositories | Substantive | `secure-agent-setup.md:114-125` | 2 |
| Weekly routine cannot reach the socat host through the allowlist | Substantive | `.claude/settings.json:25-39` | 2 |
| `date -d` and `tac` break the check script on stock macOS | Substantive | `check-tool-updates.sh:93-100` | 2 |
| `source claude-iso.sh` from zsh fails with `bad substitution` | Substantive | `secure-agent-setup.md:252`, `claude-iso.sh:77` | 2 |
| No run on either platform; the sandbox and wrapper are unverified | Substantive | `secure-agent-setup.md:307` | 3 |
| Verification lacks allowed-path checks | Substantive | `secure-agent-setup.md:307-323` | 3 |
| `env -i` drops `ANTHROPIC_API_KEY` and `TMPDIR`, undocumented | Substantive | `claude-iso.sh:57-66` | 3 |
| "Copy" overwrites an adopter's existing `settings.json` | Substantive | `secure-agent-setup.md:289` | 3 |
| `AGENTS.md:312` instruction fires on sessions it cannot serve | Substantive | `AGENTS.md:312` | 3 |
| "per step 5 above" refers by ordinal | Taste | `secure-agent-setup.md:174` | 4 |
| Verification names no layer or message per denial | Substantive | `secure-agent-setup.md:313-320` | 5 |
| One status string for every lookup failure | Substantive | `check-tool-updates.sh:140` | 5 |
| No evidence that the scripts can fail (no negative case) | Substantive | commit message, Test plan | 6 |
| `tools/agent-isolation/` missing from the `AGENTS.md` tools list | Substantive | `AGENTS.md:1130` | 7 |
| `secure-agent-setup.md` missing from the `AGENTS.md` repo-root list | Substantive | `AGENTS.md:53` | 7 |
| Scaffold docs omit the `settings.json` step | Taste | `projects/_template/` | 7 |
| `uv` 1-day exception not named | Taste | `secure-agent-setup.md:87` | 7 |

**Not done.**
- I did not run the pre-commit hooks or the actual sandbox. Neither is possible offline, and the review form says not to supply the writer's evidence.
- The apt and dnf pin availability and the existence of the claude-code releases (2.1.117, 2.1.123) could not be checked without network access.
- Two of my own tests (`claude-iso.sh` in zsh and the `date -d` call) ran on a macOS host only. I did not run them on Linux.
