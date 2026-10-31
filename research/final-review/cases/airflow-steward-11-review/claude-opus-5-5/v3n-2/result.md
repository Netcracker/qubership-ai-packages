# Final review: `2efe27f..HEAD` (1b569a8, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest")

The change gets **8 substantive requests**. It has no code with tests; it is docs, an instruction-file hunk (`AGENTS.md`), a configuration (`.claude/settings.json`), two shell scripts and a TOML manifest. The review followed §2a, using the analogue named under each item.

The defects that matter most:
- The new settings break steps in two existing skills (`sync-security-issue`, `fix-security-issue`).
- The wrapper fails in zsh, though the doc says to source it from `~/.zshrc`.
- Nothing stops Claude Code from auto-updating past its pin.

**Inputs:**
- There was no separate task statement. The claimed cases come from the commit message alone.
- `comment-drift.py 2efe27f HEAD` exited 0 with no output, because it does not parse shell, TOML, JSON or Markdown. I read every comment in the scripts by hand.
- Skills loaded: `english-developer-style` and `apm-authoring` (for the `AGENTS.md` hunk), plus `test-authoring`.
- No previous report exists.
- Running `check-tool-updates.sh` sent read-only GET requests to `api.github.com`, which this session's sandbox allows.

## Item 1: comments consistent with the code and with each other
Analogue: every statement a changed file makes about code, another file, or a count.

- **`check-tool-updates.sh:156-160`** says "this lexical comparison … plain `<` does the right thing". The code has no `<` comparison, only `==` at :152. Any upstream version that differs from the pin, even an older one, is reported as "upgrade candidate". The comment describes code that doesn't exist.
- **`pinned-versions.toml:42-43`** says "The check script uses this [`pinned_at`] as the minimum age the entries below claim to satisfy." `read_pinned` (`check-tool-updates.sh:117-125`) never reads `pinned_at`.
- **`claude-iso.sh:39-41`** gives the usage `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso`. The code drops both. I ran it: with `GH_TOKEN=abc claude-iso`, `GH_TOKEN` is absent from the child's environment. Only the `CLAUDE_ISO_ALLOW` form works.
- **`claude-iso.sh:85-90`** claims "any env var that the user set on the invocation line … is preserved. We detect this by…". Lines 100-105 take it back ("well, actually we can't reliably tell"), and no code follows either comment. A reader of the first block gets the behavior wrong.
- **`secure-agent-setup.md:218`** (doc copy only, `settings.json` itself has no comment) says "network egress via Bash bypasses the sandbox proxy". The same doc (:64-65, :338-341) describes the sandbox proxy as filtering Bash network traffic, so the two statements contradict each other. In this session's run, the sandbox proxy was what blocked the socat host.
- **`secure-agent-setup.md:229-230`** says the patterns gate "any non-default-method API call" and "any payload-bearing API call". `Bash(gh api * -X *)` needs at least one token between `api` and `-X`. So these are not gated:
  - `gh api -X POST repos/…` (flag first)
  - `--method`, `--field`, `--raw-field`, `--input`
- **`secure-agent-setup.md:69` and TOC :7**: the heading "Three-layer defence" sits over a table of four layers (0–3). The commit message says "four layers".
- **`pinned-versions.toml:84-87`** (claude-code `purpose`) says pinning stops "a silent autoupdate". Nothing in the change turns off Claude Code's auto-updater: no `DISABLE_AUTOUPDATER` in `settings.json` `env`, and `claude-iso` strips the environment. The npm-installed 2.1.117 can update itself, so the claimed property has nothing behind it.
- **`secure-agent-setup.md:163`** calls `/schedule` "The framework's `/schedule` slash-command". `.claude/skills/` has no such skill; it belongs to Claude Code.
- **`secure-agent-setup.md:171-173`** says the scheduled agent "runs in the same secure setup the rest of the framework uses". `/schedule` creates cloud routines, and they don't run under `claude-iso`, bubblewrap or this repo's local sandbox. Nothing in the change makes the sentence true.
- **`claude-iso.sh:72`**: "SSH_AUTH_SOCK … the agent gates push behind ASK; the socket alone is harmless". The ask rule matches only commands that start with `git push`. `git -C . push`, `ssh …` and a `git` alias get the agent socket without a prompt, so "harmless" is false.
- **Data inconsistency.** The manifest has socat 1.8.1.1 `released = "2026-03-13"`. The commit message's own script output shows `UPSTREAM@ 2026-02-12` for the same version. One of the two dates is wrong, and the cooldown argument rests on that date.
- **Taste:**
  - `secure-agent-setup.md:179-181` says "The full block is below", but the block leaves out `$schema` and the two `--force` ask entries.
  - `pinned-versions.toml:97-98` gives `--no-save` as protection for the "local lockfile". `npm install -g` touches no project lockfile.

## Item 2: claimed cases covered
Claims come from the commit message only; there was no task statement.

| Claimed case | Where it is handled or tested |
|---|---|
| Layer 0 strips env vars | `claude-iso.sh`. I ran it under bash and it holds. Under zsh it fails (see the commands table). |
| Layers 1-3 in `settings.json` | File present and parses (I verified). No positive control (item 3). |
| Pins aged at least 7 days at `pinned_at` | claude-code 04-22 against 04-29 is exactly 7 days. Socat's date is disputed (item 1). |
| Script reports candidates "newer than the pin AND aged" | Only "aged" is checked; "newer" is equality only (item 1). |
| Script is side-effect-free | Holds; I read the code. |
| Weekly `/schedule` surfaces candidates with no install permission | Nothing runs it, and the setup claim is unsupported (item 1). |
| `README.md` and `AGENTS.md` link the doc | Present. |

Documented commands, each with what runs the same form:

| Command (file:line) | Promised outcome | What runs it |
|---|---|---|
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (doc :114, README :35) | installs the pins | none. Depends on whether the distro archive carries those versions; Debian 12 and Ubuntu 24.04 ship older bubblewrap. **Substantive**: run on each named distro, or document building from source. |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (:122) | installs the pins | none, same dependency on the archive. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (:136) | a pinned runtime | none. The auto-updater moves it (item 1). |
| `source …/claude-iso.sh` from `~/.bashrc` **or `~/.zshrc`** (:252) | a working `claude-iso` | I ran it under zsh. `claude-iso` fails with `claude_iso_main:37: bad substitution`, because `${!var}` is bash-only (zsh needs `${(P)var}`). **Substantive**. |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (:273) | injects one credential | I ran it under bash and it works; under zsh it fails as above. |
| `GH_TOKEN=… claude-iso` (`claude-iso.sh:40`) | injects | I ran it, and the token is dropped (item 1). |
| `bash check-tool-updates.sh` (README :46, doc :144) | status table | I ran it in this sandbox. bubblewrap and claude-code resolve. socat reports "upstream lookup failed (rate limit / network)" because `www.dest-unreach.org` is not in `allowedDomains`. On macOS it also fails because `date -d` is GNU-only (`date: illegal option -- d` here). |
| `/schedule weekly run …` (:167) | weekly candidates | none. |
| Verification block (:315-317) | three denials | none (the writer says so). |
| `git check-ignore .claude/settings.local.json` (:305) | ignored by default | none. |

Every hunk is claimed by a sentence of the commit message.

## Item 3: boundaries, partitions, and the negative control
Analogue: platforms, shells, pre-existing state, and the values users already pass.

- **No positive control.** The Verification section checks only denials. The design's stated reason is that Bash may *use* `~/.config/gh/` and `~/.config/apache-steward/` while the Read tool may not (:236-241), and nothing checks the Bash half. In this session's effective sandbox, `~/.config/gh` appears in both the deny list (merged from `permissions.deny`) and the allow-within-deny list, so which one wins is a real question. **Request**: add `gh auth status` and an `oauth-draft-create --help` (or a dry run) to Verification as must-succeed lines, run on Linux and macOS.
- **Partitions with no evidence.** Linux with bubblewrap and macOS with Seatbelt: the sandbox wasn't exercised on either (the writer says so). zsh: broken. macOS for the check script: socat lookup broken.
- **Pre-existing state.**
  - Adopter step 2 (:289-291) says to copy `settings.json` over `<your-tracker>/.claude/settings.json`. A tracker that already has one (allow rules, hooks, MCP settings) loses it, and no merge step is given. **Request**: say to merge the keys.
  - Every existing contributor to this repo gets the checked-in sandbox on their next session. `prek` keeps hook environments under `~/.cache/prek`, which is not in `allowRead`. This is plausible, not run. **Request**: run `prek run --all-files` from an agent Bash call under the new settings.
- **Values users already pass.** `env -i` now also drops variables the `claude` binary itself reads: `HTTPS_PROXY`/`HTTP_PROXY`, `NODE_EXTRA_CA_CERTS`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`/`_VERTEX`, `CLAUDE_CONFIG_DIR`. A user behind a proxy, or on Bedrock or Vertex, gets a `claude` that cannot connect or authenticate, and nothing tells them why. **Substantive. Request**: name these in the passthrough list or in the doc's `CLAUDE_ISO_ALLOW` paragraph.
- **Limits (taste).** No `curl` call in `check-tool-updates.sh` sets `--max-time`. On a host that silently drops packets, each request waits for the OS connect timeout, and socat makes one HEAD request per tarball.

Added instructions: 1 (the `AGENTS.md` hunk; the `README.md` hunk is a docs page).

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | a session editing this framework repo, with no tracker content | a setup reminder the running agent cannot act on | "when setting up a machine to run the skills against a tracker" |

Not findings: none.

## Item 3a: level, placement, and the environment
- The repository's gate, `prek`, was not run: its hook environments need node and network. `bash -n` and `shellcheck` pass on both scripts.
- No CI job runs `shellcheck` on `tools/agent-isolation/*.sh`, and none runs the check script. **Taste.**
- Placement: `tools/<name>/` holds "tool adapters … the skills invoke" (`AGENTS.md`); `agent-isolation` is not invoked by any skill and has a `README.md` where its siblings have a `tool.md`. **Taste.**
- The setup doc at the repository root matches `how-to-fix-a-security-issue.md` and its siblings.

## Item 4: names by content, not by position
- `secure-agent-setup.md:174` "(per step 5 above)" points to "Open the bump as its own PR". Name it by content, e.g. "the bump PR's review".
- Otherwise none. Layer numbers are used as names, and the section links are anchors.

## Item 5: the failure report
Analogue: what a failure looks like to the reader.

- `check-tool-updates.sh:144-148,151-153` reports every empty lookup as "upstream lookup failed (rate limit / network)". That includes three non-network causes:
  - a tool in the manifest with no lookup function (`*)` branch)
  - a sandbox-denied host
  - `date -d` failing on macOS

  **Substantive**: give each cause its own message.
- With `python3` < 3.11 (no `tomllib`; macOS ships 3.9.6 as `/usr/bin/python3`), the script prints an empty table and exits **0**. I ran this with a shim. The error goes to stderr, and the process-substitution failure is never checked. A scheduled run would report "nothing to do". **Substantive.**

## Item 6: what the writer says it verified
- The writer states that the JSON parses, that `prek` passes, and gives one end-to-end run of the check script.
- The writer says the sandbox was not exercised.
- No run of `claude-iso` is stated in any shell, and nothing shows the Verification commands produce denials.
- No bad case is named. For example, nothing shows the deny rules failing an attempt they should block, or the positive path succeeding.

## Item 7: siblings of the change
Analogue: places that enumerate the framework's hosts, paths and files.

- **`allowedDomains`, commented "every host the framework legitimately reaches"** (doc :201).
  - `sync-security-issue/SKILL.md:873` and `tools/cve-org/tool.md:66,90` run `curl -sSf https://cveawg.mitre.org/api/cve/<CVE-ID>`. `Bash(curl *)` denies the command, and `cveawg.mitre.org` is not allowlisted. The skill's check-published step now fails.
  - Also missing from the allowlist:
    - `services.nvd.nist.gov` (`cve-org/tool.md:49`)
    - `www.dest-unreach.org` (the change's own check script)

  **Substantive.** Request: allowlist these hosts and switch the skill's `curl` to a permitted form, or note the breakage as follow-up.
- **`denyRead: ["~/"]`.** `fix-security-issue` works in `environment.upstream_clone`, a separate clone outside the tracker's cwd: it creates a branch, runs tests, and runs `uv tool install prek`. Under the sandbox those Bash steps cannot read that tree, and the sandbox's default write scope is cwd. **Substantive.** Request: an `allowRead` (and write) entry for the clone, or a documented step, or name it as follow-up.
- **`AGENTS.md` lists.**
  - "Repo-root files" (:39-45) lists `README.md`, `how-to-fix-a-security-issue.md` and `new-members-onboarding.md`, but not the new `secure-agent-setup.md`.
  - "References" lists `tools/github/`, `tools/gmail/`, `tools/vulnogram/` and `tools/cve-org/`, but not `tools/agent-isolation/`.

  **Substantive**: both are sets that now miss a member.

## Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| Existing skill steps broken: `curl` denied and `cveawg.mitre.org`/NVD not allowlisted | Substantive | `.claude/settings.json:20-35,52`; `sync-security-issue/SKILL.md:873` | Allowlist the hosts and fix the skill's command, or name it as follow-up |
| `fix-security-issue` upstream clone outside `allowRead` and the write scope | Substantive | `.claude/settings.json:6-16` | Add an entry or a documented step, or name it as follow-up |
| `claude-iso` fails in zsh (`bad substitution`), though the doc says to source it from `~/.zshrc` | Substantive | `claude-iso.sh:80,95`; doc :252 | Use a portable lookup, or document bash-only |
| Header usage and :85-90 comment contradict the code; :100-105 is a stream-of-thought comment | Substantive | `claude-iso.sh:39-41,85-105` | Use the `CLAUDE_ISO_ALLOW` form and delete the retracted claim |
| `env -i` drops proxy/CA/Bedrock/Vertex variables that `claude` reads | Substantive | `claude-iso.sh:56-74` | Pass them through, or document them |
| Pin does not stop auto-update | Substantive | `pinned-versions.toml:84-87`; `settings.json` | Set `DISABLE_AUTOUPDATER` in `settings.json` `env`, or drop the claim |
| `/schedule` routine said to run "in the same secure setup" | Substantive | doc :163,171-173 | Correct the claim, or say where the routine runs |
| Ask patterns miss flag-first and long-form `gh api` writes | Substantive | `settings.json:74-76`; doc :229-230 | Add the patterns, or correct the "any …" comments |
| "Bash bypasses the sandbox proxy" contradicts the doc's own threat model | Substantive | doc :218 | Correct the comment |
| Comment on a `<` comparison that does not exist; "newer" never checked | Substantive | `check-tool-updates.sh:150-160` | Compare versions, or correct the comment and the status text |
| `pinned_at` said to be read by the script, which never reads it | Substantive | `pinned-versions.toml:42-43` | Correct the comment, or use the field |
| Socat release date conflicts with the script's own output | Substantive | `pinned-versions.toml:67`; commit message | Confirm one date |
| Heading "Three-layer" over four layers | Substantive | doc :7,69 | Rename |
| One failure message for every lookup cause; old Python gives an empty table and exit 0 | Substantive | `check-tool-updates.sh:117-125,144-148` | Separate messages; fail when the manifest read fails |
| Socat lookup fails on macOS (`date -d`) and in the sandbox (host not allowlisted) | Substantive | `check-tool-updates.sh:100-103` | Portable date parsing; allowlist the host |
| No positive control in Verification | Substantive | doc :309-318 | Add must-succeed `gh`/oauth-draft lines and run them |
| Adopter "copy" overwrites an existing `settings.json` | Substantive | doc :289-291 | Say to merge the keys |
| Install commands not run on any distro | Substantive | doc :110-125; README :35 | Run on each named distro, or document the source build |
| `SSH_AUTH_SOCK` called "harmless" | Substantive | `claude-iso.sh:72` | Correct the claim, or gate `ssh` and `git -C … push` |
| `AGENTS.md` repo-root and References lists miss the new file and directory | Substantive | `AGENTS.md:39-45`, References | Add the entries |
| `AGENTS.md:312` instruction has no condition | Substantive | `AGENTS.md:312` | Add the clause from the item 3 table |
| "(per step 5 above)" | Substantive | doc :174 | Name the step by content |
| "Full block" omits entries; `--no-save` lockfile rationale | Taste | doc :179; `pinned-versions.toml:95-98` | Reword |
| No `curl` timeouts; no CI `shellcheck`; `tools/` placement | Taste | `check-tool-updates.sh`; `.github/workflows` | Add `--max-time`; a CI job |

This review did not check:
- the sandbox's behavior on Linux or macOS, beyond what this session's own sandbox showed;
- the `apt`, `dnf`, `npm` and `brew` commands, which need network;
- the `prek` gate;
- whether the pinned upstream release dates are correct;
- the prose for style alone.
