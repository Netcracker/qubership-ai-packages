# Final review: `2efe27f..1b569a8` ("ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

**Setup.** There is no separate task statement. The claimed cases come from the commit message alone, and the claimed cases in item 2 are limited to what that message says.

The change is mostly docs and configuration, plus two shell scripts. I loaded `apm-authoring` for the `AGENTS.md` hunk and `english-developer-style`. `docs-page-authoring`, the doc-comment skills and `test-authoring` are not among the four skills I was given, so I did not load them.

The drift script ran with no output (it parses no members in these file types). No test files exist.

I did not run the suite. I ran `bash -n` and `shellcheck` on both scripts, which are clean. I parsed the JSON and TOML, and ran `claude-iso.sh` against a stub `claude` in bash and zsh. The sandbox itself and the network lookups were not exercised. The no-network environment blocks the lookups, and the commit message says the sandbox has not been run either.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **Layer count.** `secure-agent-setup.md:7,69` is headed "Three-layer defence" and its table lists four layers (0–3). The commit message says "four layers". The README and `AGENTS.md` hunks don't count them. **Substantive**, because the heading and the table contradict each other.
- **Settings block.** The "full block" at `secure-agent-setup.md:183-234` is not the file:
  - It drops `$schema`.
  - It drops the `git push --force` and `--force-with-lease` `ask` entries. The comment on line 224 says they are covered by `git push *`, which is true only if that pattern matches them.
  - It collapses the one-per-line arrays.

  Two copies of one config will drift. **Taste**: link the file, or say the block is abridged.
- **Comment contradicts code.** `check-tool-updates.sh:163-167` says "this lexical comparison … plain `<`". The code at line 160 uses `!=`. It never compares order, so any difference from upstream is reported as an "upgrade candidate". **Substantive**: the comment is false and describes a check the script does not perform.
- **Stale reasoning.** `claude-iso.sh:85-90` says the script detects variables set "on the invocation line". Lines 104-109 then admit "we can't reliably tell". The code only honors `CLAUDE_ISO_ALLOW`. **Substantive**, because lines 85-90 describe a mechanism that does not exist. Delete that paragraph.
- **Manifest vs script.** `pinned-versions.toml` pins socat `released = "2026-03-13"`. The commit message's own script output shows upstream `2026-02-12` for the same `1.8.1.1`. The "released" column the cooldown claim rests on is wrong for one of the two sources. **Substantive**.
- **Narration.** No `now` or `no longer` narration in the changed files. Em-dash use in the README and `AGENTS.md` hunks is sparing and matches the surrounding text.

## Item 2: claimed cases covered (analogue: sections and runs)

Claimed cases from the commit message, and what covers each:

| Claim | Covered by |
|---|---|
| Layer 0 strips credentials (`claude-iso.sh`) | `secure-agent-setup.md:309-323` verification block. Its `echo $AWS_ACCESS_KEY_ID  # → empty` detects nothing, because the variable is empty whenever it was never set. Nothing exports it first. |
| Layer 1 filesystem sandbox | The verification block's `cat ~/.aws/credentials`. The commit message says it is unexercised. |
| Layer 2 tool permissions | The `curl` line in the verification block tests `permissions.deny`, not the network allowlist. Nothing checks that an unlisted host is blocked. |
| Layer 3 confirm-on-write | None. |
| Check script "runs end-to-end" | One transcript in the commit message. I could not re-run it with no network. |
| Valid JSON | Covered (re-checked). |
| `/schedule` routine surfaces candidates | Contradicted, see below. |

**Commands the change tells someone to run, and what runs them:**

- `apt-get install bubblewrap=0.11.1-*` and `socat=1.8.1.1-*` (doc, README, TOML): **none**. The outcome depends on the distro's package version strings. Debian and Ubuntu package versions rarely match the upstream version plus `-*`. Nobody ran it.
- `dnf install bubblewrap-0.11.1`: **none**. The same property applies.
- `npm install -g --no-save @anthropic-ai/claude-code@2.1.117`: **none**. `--no-save` has no effect on a global install, because there is no project lockfile to leave alone. The TOML comment about the "local lockfile" is therefore wrong.
- `bash check-tool-updates.sh`: the commit message shows one run, on a GNU `date` system.
  - Under macOS BSD `date`, `date -d` (`:101,103`) fails. I confirmed that `date -d` is an illegal option here.
  - The socat row then always reports "lookup failed", yet the doc supports macOS.
  - **Substantive**: a run on macOS, or a portable `date`.
- `/schedule weekly run tools/agent-isolation/check-tool-updates.sh` (`secure-agent-setup.md:166-169`): the doc says the routine "runs in the same secure setup". That setup denies `Bash(curl *)`, and the script's only network calls are `curl`. `www.dest-unreach.org` is not in `allowedDomains` either. The documented routine cannot produce a table. **Substantive**: run the script under the dogfooded settings, or add the host and a non-`curl` fetch.
- `source … claude-iso.sh` from `~/.zshrc` (`:249-254`): the file is bash-only. In zsh the call fails with `claude_iso_main:37: bad substitution`, because `${!var-}` is not zsh syntax. The doc and README tell macOS and zsh users to do exactly this. **Substantive**.
- `claude-iso.sh:111`: `exec env -i …` runs inside the sourced function, so `claude-iso` replaces the user's interactive shell. When Claude exits, the terminal closes. A bash sourced run confirmed that the line after `claude-iso` never executes. **Substantive**: drop `exec` when sourced, or run in a subshell or `command`.

**Hunks no sentence claims:**

- `AGENTS.md` and `README.md` are claimed ("link from agent prerequisites and Local setup").
- `tools/agent-isolation/README.md:40,47` and `secure-agent-setup.md:253` use `/path/to/airflow-steward/`. The prior commit `b73e240` ("drop Airflow remnants") removed such remnants, and the project convention is `<framework>`. **Taste**: use the placeholder.

## Item 3: boundaries, partitions, and the negative control

- **Platforms.** Linux and macOS are both claimed. Only a GNU system was exercised (the commit message transcript). The bash and zsh partitions are untested by the author. I ran them: bash works, zsh fails.
- **Sourced vs direct invocation.** Both are documented. Direct invocation works. Sourced invocation kills the shell (above).
- **Pre-existing state.** The change leaves environments around. Users with an existing `~/.claude/settings.json`: user and project settings merge, so the doc should say user-level `allow` rules can override the project's `ask`/`deny`. Not covered. **Taste**, since I could not verify the merge semantics offline.
- **`sandbox.filesystem.allowRead` / `denyRead` key names.** I could not check them against Claude Code's schema offline. The commit message says the sandbox is unexercised, so the whole of Layers 1 and 2 is unverified. **Substantive**: a run with `claude-iso` showing the three denials from the verification block.
- **`SSH_AUTH_SOCK` passthrough** (`claude-iso.sh:73`). `~/.ssh` is denied for reads, but a live agent socket lets any Bash subprocess sign with the user's keys. "Residual risks" doesn't mention it. **Substantive**: add it, or require opt-in through `CLAUDE_ISO_ALLOW`.
- **Replaced mechanism and limits.** Nothing is replaced, and no limits are moved.
- **Added instructions** (the `AGENTS.md` instruction, the only instruction the change adds for the agent):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a session already inside the sandbox, or a docs-only edit session with no CVE content | tells the user to re-run in the setup, or checks for `claude-iso` on every session | "only where the session reads `<security-list>` or tracker content, and stop if `sandbox.enabled` is already on" |

Not findings: `README.md:158-169` (a statement to the user, not an instruction to the agent).

## Item 3a: level, placement, and the environment (analogue)

- `.claude/settings.json` is placed where Claude Code reads it. It is the first file under `.claude/` outside `skills/`.
- Adopter instructions copy it into the tracker's `.claude/` directory. That is the right place.
- The tool lives in a new `tools/agent-isolation/`, which matches the siblings. Its README says it is not a Python project, which is true.
- No hook or CI job runs `shellcheck` or `check-tool-updates.sh`. The commit message's `prek run --all-files` passed, but the scripts have no coverage and the TOML is not parsed anywhere. **Taste**.

## Item 4: names by content, not by position

- `secure-agent-setup.md:174` "per step 5 above" and `:81` "below" refer by position. **Taste**: "the bump PR step".
- "Layer 0" through "Layer 3" are ordinals, but they are the document's defined names, so they are fine.
- Otherwise **none**.

## Item 5: the failure report (analogue: what the verification tells the reader)

The verification block (`:312-318`) names an expected denial for each of its three commands, but only the `cat` and `curl` lines can fail on a real misconfiguration. See item 2 for the `echo` line, which never fails. Nothing tells the reader how to distinguish "denied by sandbox" from "file absent". **Substantive**, the same as the item 2 row. The request is to create a canary file and variable first.

## Item 6: what the writer says it verified

The commit message states the TOC hook, the script's transcript, and the JSON parse. It does not state a red run for any rule. It says outright that the sandbox is unexercised. No mutation evidence exists, such as a case where a deny rule is removed and the verification command now leaks. **Substantive**.

## Item 7: siblings of the change

- `AGENTS.md` "Repo-root files" and "References" lists name `tools/<name>/` adapters. Neither lists `secure-agent-setup.md` or `tools/agent-isolation/`. The README has the link. **Taste**.
- `tools/agent-isolation/README.md:11-13` says the README's example uses `bubblewrap=0.11.1-*`. That version string appears in four places (TOML, doc, README, comment). The bump procedure lists only the doc.
  - The bump procedure at `check-tool-updates.sh:179-184` and `secure-agent-setup.md:151-156` doesn't name the tools README or the `install.*` fields in the TOML.
  - A bump following those steps leaves stale versions. **Substantive**.
- Sets with a count: "Three-layer" in the heading vs the commit message's "four layers". Covered under item 1.
- `curl` as the fetch tool is a sibling of the `curl` deny rule (item 2).

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | `exec` in the sourced function replaces the user's shell | Substantive | `tools/agent-isolation/claude-iso.sh:111` | Run `claude` in a subshell or via `command` when sourced; keep `exec` for direct runs. |
| 2 | The wrapper is bash-only, but the docs tell zsh users to source it (`bad substitution`) | Substantive | `claude-iso.sh:80,98`; `secure-agent-setup.md:249-254` | Make it portable, or say bash only. |
| 3 | The `/schedule` routine can't work under the dogfooded settings (`curl` denied, socat host not allowed) | Substantive | `secure-agent-setup.md:161-175`; `check-tool-updates.sh:68,90,96` | Run it under the settings, then allow the hosts or change the fetch. |
| 4 | `date -d` is GNU-only, so the check breaks on macOS | Substantive | `check-tool-updates.sh:101,103` | Portable date handling, or document Linux only. |
| 5 | The comment says a lexical `<` comparison; the code uses `!=` | Substantive | `check-tool-updates.sh:163-167` | Fix the comment, or compare order. |
| 6 | The socat `released` date (03-13) disagrees with the upstream date for the same version (02-12) in the commit's own output | Substantive | `pinned-versions.toml` socat entry | Reconcile which date is right. |
| 7 | "Three-layer" heading over a four-layer table | Substantive | `secure-agent-setup.md:7,69` | Rename the heading. |
| 8 | The verification block's `echo $AWS_ACCESS_KEY_ID` cannot fail; nothing tests the network allowlist or Layer 3 | Substantive | `secure-agent-setup.md:312-318` | Seed a canary variable and file; add an unlisted-host check. |
| 9 | No evidence the sandbox or deny rules work; no red run | Substantive | commit message | One session showing the denials. |
| 10 | Stale invocation-line paragraph describes a mechanism that doesn't exist | Substantive | `claude-iso.sh:85-90,104-109` | Delete it. |
| 11 | `SSH_AUTH_SOCK` passthrough lets subprocesses use keys the Read deny hides | Substantive | `claude-iso.sh:73` | Make it opt-in, or list it under Residual risks. |
| 12 | The bump steps omit the tools README and the `install.*` fields | Substantive | `secure-agent-setup.md:151-156`; `check-tool-updates.sh:179-184` | Name every place the version appears. |
| 13 | Package version strings (`bubblewrap=0.11.1-*`) and `--no-save` on a global npm install are unrun and partly wrong | Substantive | `secure-agent-setup.md:115-136`; TOML | Run on one Debian and one Fedora image, and drop `--no-save` and its comment. |
| 14 | `AGENTS.md` instruction fires on every session | Substantive | `AGENTS.md:312` | End it: "only where the session reads tracker or `<security-list>` content". |
| 15 | The inline settings copy is abridged; `/path/to/airflow-steward`; "step 5 above"; missing `AGENTS.md` list entries | Taste | various | See the sections above. |

This review did not check wording for style beyond places where a sentence is false or reads wrongly, and it did not run the suite or any network operation.
