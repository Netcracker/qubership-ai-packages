## Final review: `2efe27f..HEAD` (one commit, `1b569a8`)

**Inputs.** No task statement was handed over, so item 2 takes its claims from the commit message of `1b569a8` alone. The class-comment and test sources are absent because the change adds no tests. There was no previous report, so the table over earlier findings is empty. The change has no code members, so `comment-drift.py` ran (exit 0) and printed nothing. It does not parse shell, TOML, JSON, or Markdown.

**Analogues used.** The change is a mix: two shell scripts, a TOML manifest, a JSON settings file, a docs page, a tools README, and an edit to `AGENTS.md`. Items 1-7 apply to the code and the docs. The §2a analogues apply to `AGENTS.md`, the one instruction file. I read `english-developer-style` and `apm-authoring` from the copies under the skills directory, because the Skill tool did not find `english-developer-style` by name. I did not load `test-authoring`, since the change adds no tests.

**Checks run locally.** Nothing was changed or committed. `.claude/settings.json` parses as JSON, and `pinned-versions.toml` parses with `tomllib`. Both scripts pass `bash -n` and `shellcheck` with no output. I ran `claude-iso.sh` with a fake `claude` on `PATH` that prints its environment, and `check-tool-updates.sh` on this macOS host.

---

### Item 1: comments consistent with the code and with each other

Three of the four `code-changed` sites in the scripts have comments that the code contradicts. Findings F1, F4, F5, F9, and F10 cover them.

- **F1, `claude-iso.sh` 39-41, 85-86, 104-109.** The usage lines `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` drop the variable. The wrapper passes only the passthrough list and `CLAUDE_ISO_ALLOW`. With the fake `claude`, the first form reached the child without `GH_TOKEN`, and `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=tokC claude-iso` passed it. The comment at 85-86 says "any env var that the user set on the invocation line is preserved", which is false. The comment at 104-109 says "we honour it" and then says the wrapper cannot tell.
- **F4, `claude-iso.sh` 73.** The comment says the `SSH_AUTH_SOCK` socket "alone is harmless".
- **F5, `secure-agent-setup.md` 69.** The heading says "Three-layer defence", over a table with four layers (0-3). The commit message says four.
- **F9, `secure-agent-setup.md` 85-86 and 127-130; `README.md` 158-163.** The doc says "every system-level tool … is pinned". The macOS paragraph says `brew install socat` has "no pin enforced". The README calls bubblewrap "required", and the doc says it is not needed on macOS.
- **F10, `pinned-versions.toml`, `[tools.claude-code]` comment.** The comment says `--no-save` keeps the global install from drifting a project's lockfile. With `-g`, npm installs into the global prefix, so the flag does nothing here. `npm install --help` lists both flags. The `-g` behavior comes from npm's documented semantics, not from a run.
- **F11, `secure-agent-setup.md` 264-267.** The doc's passthrough list omits `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which the script passes.
- **F13, `check-tool-updates.sh` 57-60.** The comment says a non-zero exit covers "rate limit, network error". A stalled connection never exits, because `curl` has no `--max-time`.

### Item 2: claimed cases covered

Claims from the commit message: four layers, each implemented; the wrapper strips credential-shaped variables; the check script is side-effect-free and prints upgrade candidates aged past 7 days; pinned dates satisfy the cooldown; the check script "verified these by querying upstream"; `AGENTS.md` links the doc from an "agent prerequisites" section and from "Local setup".

- No test covers any layer. The commit's own test plan says sandbox enforcement is untested until a maintainer runs it after merge. That is F15 and F14.
- **F7.** `AGENTS.md` has no "agent prerequisites" section (`git grep -i prerequisite` finds nothing). Only the "Local setup" link was added.
- **F6.** The commit's check output shows `socat 1.8.1.1 PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12` for the same version. The manifest's `released` date for socat is contradicted by the commit's own evidence. The script's upstream column is the tarball's HTTP `Last-Modified` (`check-tool-updates.sh` 96-103), not a release date.
- The cooldown boundary holds. `claude-code` 2.1.117 (2026-04-22) against `pinned_at` 2026-04-29 is exactly 7 days, and the `<=` test accepts it.
- The hunks all belong to a claim of the commit message. None is orphaned.

**Command lines in the changed files.** Each is listed with its outcome and whether a script or CI job runs the same form.

| Command (location) | Promised outcome | Same form runs in repo? | Checked here |
|---|---|---|---|
| `sudo apt-get install … bubblewrap=0.11.1-* socat=1.8.1.1-*` (doc 113-116; tools README) | pinned versions installed | none; depends on the distro carrying those versions | not run (no network) |
| `sudo dnf install bubblewrap-0.11.1 socat-1.8.1.1` (doc 122-124) | same | none; dnf matching a name-version without a release not checked | not run |
| `brew install socat` (doc 129) | socat installed, unpinned | none | n/a |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (doc 136; TOML) | pinned claude-code installed | none; `--no-save` has no effect with `-g` (F10) | not run |
| `source …/claude-iso.sh`, then `claude-iso` (doc 253, 262) | claude started with the passthrough env | none | fake `claude`: passthrough works |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN="$(gh auth token)" claude-iso` (doc 272-276) | `GH_TOKEN` reaches claude | none | fake `claude`: `GH_TOKEN` present |
| `GH_TOKEN=… claude-iso`, `AWS_PROFILE=… claude-iso` (`claude-iso.sh` 40-41) | the variable reaches claude | none | fake `claude`: dropped (F1) |
| `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com` (doc 315-317) | denied, empty, blocked | none | not run (F14) |
| `bash tools/agent-isolation/check-tool-updates.sh` (doc 144; tools README) | candidates listed | none in CI | `bash -n` and shellcheck clean; macOS socat row fails (F3); network not run |
| `/schedule weekly run tools/agent-isolation/check-tool-updates.sh …` (doc 166-168) | recurring routine | none (an agent routine, not in repo) | not run |

### Item 3: boundaries, partitions, and the negative control

- **Pre-existing state.** Adopters who copy `.claude/settings.json` into a tracker that already has one lose the file. F8.
- **Negative control.** The three denials in the Verification block are the control arm. None was run. F14.
- **Limits.** The change sets no limit. The one missing limit on the same work is the `curl` timeout in `check-tool-updates.sh` (F13). The `/schedule` routine's own limits are not in this repo.
- **Values users already pass.** None. `CLAUDE_ISO_ALLOW` is new, so no existing consumer reads it.
- **Replaced mechanism.** None. Nothing is replaced.

### Item 3a: level, placement, and environment

The behavior the wrapper claims is observable in one process with a fake `claude` on `PATH`, with no server or sandbox. The change has no such test. F15 names the test I ran. The sandbox and permission rules need Claude Code to enforce them, so they are not testable in the repo; that is F14.

**Platform.** The check script assumes GNU `date`. On this macOS host, `date -d` fails with `illegal option -- d`, so the socat row always reports "upstream lookup failed (rate limit / network)". F3.

### Item 4: names by content, not by position

- **F12.** `secure-agent-setup.md` 174 says "per step 5 above". Step 5 is "Open the bump as its own PR", which has a content name. The same paragraph names Layers 1-3 by number (line 78), although the table names each one.

### Item 5: the failure report

- **F3.** On macOS, the socat row prints "upstream lookup failed (rate limit / network)" for a `date` failure.
- **F13.** The same message is printed when no release in the newest 20 is aged past 7 days. The message names the wrong cause in both cases.

### Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict are stated. The commit's test plan says the sandbox enforcement is untested until a maintainer runs it after merge. The gates I ran are consistency checks, not evidence that the rules can fail: JSON and TOML parse, and both scripts pass `bash -n` and shellcheck. F14.

### Item 7: siblings of the change

Checked with no finding:

- The three-tool set (bubblewrap, socat, claude-code) appears in the `case` statement, both tables, the install blocks, the tools README usage, and the manifest.
- The deny, ask, allow, and network lists in `settings.json` match the jsonc block in the doc entry for entry.
- The "Three-layer" count is stale against four layers (F5).
- The passthrough list is stale against the script (F11).
- The `AGENTS.md` link is missing from the claimed section (F7).

**Taste.** The example paths `/path/to/airflow-steward/` (doc 253; tools README usage) reintroduce a project-named path into a framework that the previous commit cleaned of Airflow remnants. A `<steward-checkout>` placeholder, as in the AGENTS placeholder convention, would avoid that.

### §2a instruction table (`AGENTS.md`)

Added instructions: 1.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a docs-only typo fix in this repo, no skill run, no tracker content | a directive to run every session in the sandbox setup | "only where the session runs a skill against tracker content" |

Not findings: none.

---

### Findings

Ordered most severe first. Labels: substantive, or taste (no churn was reported).

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The usage forms drop the credential they name (verified). Two comment paragraphs state behavior the code lacks. | substantive | `tools/agent-isolation/claude-iso.sh` 39-41, 85-86, 104-109 | Use the `CLAUDE_ISO_ALLOW` form in the header. Delete or rewrite the two false paragraphs. |
| F3 | `date -d` is GNU-only. On macOS the socat row always fails and prints a network message. | substantive | `check-tool-updates.sh` 101, 103 | Parse the date in Python, as `read_pinned` already does, or use `date -j -f`. Make the failure name the step that failed. |
| F2 | `exec` inside the sourced function replaces the user's interactive shell (verified). | substantive | `claude-iso.sh` 111 | Drop `exec`, or say in the doc that the terminal shell is replaced. |
| F4 | "The socket alone is harmless" is unsupported. Any process in the session can use the agent's keys, and `Bash(git push *)` does not gate `git -C <dir> push`. Whether the sandbox proxy carries ssh was not checked. | substantive | `claude-iso.sh` 73 | Reword as an accepted risk with that scope, or drop the socket from the passthrough. |
| F5 | "Three-layer defence" heading over four layers. The commit says four. | substantive | `secure-agent-setup.md` 7, 69 | Rename to "Four-layer defence" and update the TOC entry. |
| F6 | The socat `released` date is contradicted by the commit's own output for the same version. The script's column is file `Last-Modified`, not a release date. | substantive | `pinned-versions.toml` `[tools.socat]`; `check-tool-updates.sh` 96-103 | Correct the date from the release announcement. State in the script which date it compares. |
| F7 | The commit says `AGENTS.md` links the doc from an "agent prerequisites" section. No such section exists, and only the Local setup link was added. | substantive | `AGENTS.md` (Local setup) | Add the link under the matching section, or correct the claim in the commit message. |
| F8 | "Copy `.claude/settings.json` into your tracker" overwrites an existing file that may hold the adopter's own permissions. | substantive | `secure-agent-setup.md` 289-291 | Say to merge into an existing file. |
| F9 | "Every system-level tool … is pinned" and "required system tools" are false for macOS, where bubblewrap is not needed and socat is unpinned. | substantive | `secure-agent-setup.md` 85-86, 127-130; `README.md` 158-163 | Scope the sentence to Linux and say what macOS does. |
| F10 | `--no-save` with `-g` has no effect, and the stated reason does not hold. | substantive | `pinned-versions.toml` `[tools.claude-code]` comment; `secure-agent-setup.md` 136 | Drop `--no-save` and its reason, or give the real one. |
| F11 | The doc's passthrough list omits three variables the script passes. | substantive | `secure-agent-setup.md` 264-267 vs `claude-iso.sh` 56-74 | List the three, or point to the script. |
| F12 | "per step 5 above" names a step by its position. Layers 1-3 are also referenced by number. | substantive (step 5); taste (layers) | `secure-agent-setup.md` 174; 78 | Name the step by its heading, e.g. "the bump procedure". |
| F13 | `curl` has no `--max-time`, so a stalled call never returns and the comment's error handling does not fire. The "no aged release" case prints a network message. | substantive | `check-tool-updates.sh` 57-60, 68, 152-153 | Add `--max-time` to each call. Give "no aged release" its own message. |
| F14 | No run backs the sandbox claims. The three denials in Verification are not run, and the commit says sandbox enforcement is untested until after merge. No red run is stated. | substantive | `secure-agent-setup.md` 312-318 | Run the three commands in a `claude-iso` session on a Linux bubblewrap host and on macOS. Paste the output into the PR. Show the base-commit failure, where `cat ~/.aws/credentials` succeeds. |
| F15 | The wrapper's claims have no test. The fake-`claude` check I ran would catch F1 at once. | substantive | `claude-iso.sh` | Add a test that puts a fake `claude` on `PATH`, prints its env, and asserts the passthrough, the dropped `GH_TOKEN`, and the `CLAUDE_ISO_ALLOW` pass. Run it in CI or the repo's test gate. |
| F16 | The `AGENTS.md` instruction fires on every session, including a docs-only edit. | substantive | `AGENTS.md:312` | Add the clause "only where the session runs a skill against tracker content." |
| F17 | Example paths name the framework repo as `airflow-steward`, a project-named remnant. | taste | `secure-agent-setup.md` 253; `tools/agent-isolation/README.md` usage | Use a `<steward-checkout>` placeholder. |

**Not checked.** The verification denials and the upstream network calls were not run. Apt and dnf version availability was not checked. The `prek` hooks were not run, and the TOC was compared by reading the headings. Claude Code's settings keys (`sandbox.filesystem.*`, `sandbox.network.*`) were not checked against its schema, and no Linux bubblewrap run was done. The npm `-g` behavior in F10 is from documentation, not a run.
