## Final review: `2efe27f..HEAD` (commit `1b569a8`)

**Change and inputs.** One commit, `1b569a8`, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)". It adds `.claude/settings.json`, `secure-agent-setup.md`, four files under `tools/agent-isolation/`, and paragraphs in `AGENTS.md` and `README.md`. There is no separate task statement, so the claimed cases come from the commit message, as instructed. This is the first review of the change, so there is no previous report.

**Skills loaded:** `final-review`, `english-developer-style`, `apm-authoring` (the instruction-file analogue for `AGENTS.md`). `test-authoring` was not loaded because the change has no tests. `docs-page-authoring` is not among the four skills named, so I did not load it.

**Drift script:** ran from the repo root with `2efe27f HEAD`. It printed nothing and exited 0. The change adds no Python, Go, or other parsed members, and the shell functions and TOML are not parsed, so I read all comments by hand.

**Analogues:** the change has no code, so each item uses its §2a analogue. The shell and TOML checks below are my own local runs. I changed no file in the repository and did not commit. Scratch copies and a fake `claude` binary are in `$TMPDIR/review-final`.

---

### Item 1: comments consistent with the code and with each other

Analogue: the statements one changed file makes about another file, the repository, or a document it cites.

- The check script's comments say it reports releases "newer than the pinned versions" and that "plain `<` does the right thing". The code only tests `==` (F4).
- The wrapper's block comment says variables set on the invocation line are preserved. The code drops them (F6). Its header examples repeat the same false claim (F5).
- The wrapper calls `SSH_AUTH_SOCK` harmless with no basis (F7).
- The "Three-layer defence" heading covers four layers (F9).
- `README.md` lists socat and bubblewrap as required, but the setup doc says they are not needed or optional on macOS (F10).
- The `AGENTS.md` instruction has no clause that ends it (F11, §2a table below).
- The manifest's socat `released` date disagrees with the check script's output for the same version (F8).
- Narration words (`now`, `no longer`, `used to`): none found.

Findings: F4, F5, F6, F7, F8, F9, F10, F11, F18.

### Item 2: claimed cases covered

Claimed cases, with the test that covers each:

| Claim | Test | Result |
|---|---|---|
| Wrapper strips credential-shaped variables | none | Reproduced with a fake `claude`: `GH_TOKEN`, `AWS_PROFILE`, and `TMPDIR` are unset in the session (F13) |
| Filesystem, tool-permission, and confirm layers enforce | none | Not run; the commit says so (F13) |
| Check script never installs, edits, or opens a PR | none | Read: only GET requests, no writes, holds |
| Every pin satisfies the 7-day cooldown | none | Dates parse and the arithmetic holds, but the socat date conflicts with the script's output (F8) |
| `settings.json` parses | none | Parses (run) |
| Check script prints the status table | none | Not reproduced (no network); on macOS the socat row fails (F2); inside the setup it is blocked (F1) |
| `prek` passes | none | Not run |

Hunks: every hunk in the diff is claimed by a sentence of the commit message, so there are no unclaimed hunks.

One claim fails on its own text: the commit says `AGENTS.md` links the new doc from an "agent prerequisites" section. `AGENTS.md` has no such section, only the "Local setup" link (F16).

Commands the change tells someone to run:

| Command (where) | Promised outcome | Same command run by the repo | Result |
|---|---|---|---|
| `sudo apt-get install … bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md` ~113–117; `pinned-versions.toml`) | pinned versions installed | none | Not run; the `-*` suffix requires a distro that carries 0.11.1 (F14) |
| `sudo dnf install bubblewrap-0.11.1 socat-1.8.1.1` (~121–124) | same | none | Not run; the form differs from apt and is unchecked on Fedora (F14) |
| `brew install socat` (~128) | socat, unpinned | none | Not run; the doc calls the pin best effort (F14) |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` | pinned Claude Code | none | Not run (F14) |
| `bash tools/agent-isolation/check-tool-updates.sh` (tools README; script) | status table | none; no CI job | Not reproduced; fails on macOS for socat (F2); blocked by the sandbox allowlist (F1) |
| `/schedule weekly run …` (doc) | scheduled run | none | Not run; outside the repo |
| `source claude-iso.sh`; `claude-iso` (doc; tools README) | Claude starts with no inherited credentials | none | Run with a fake `claude`: starts, and unlisted variables are dropped |
| `GH_TOKEN="$(gh auth token)" claude-iso`; `AWS_PROFILE=read-only claude-iso` (`claude-iso.sh:40–41`) | the variable reaches the session | none | Run: `GH_TOKEN` is unset (F5) |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (doc ~273) | the variable reaches the session | none | Run: passes |
| `cat ~/.aws/credentials`; `echo $AWS_ACCESS_KEY_ID`; `curl https://example.com` (doc Verification) | denial, empty, denial | none | Not run; denial-only rows (F12) |
| `git check-ignore .claude/settings.local.json` (doc) | prints the path if ignored | none | Not run |
| `python3 -c 'import json; …'` (commit message) | parses | none | Run: parses |
| `prek run --all-files` (commit message) | passes | the repo's prek hooks | Not run |

For each `none`, the property the outcome depends on is: the distro's package set (apt, dnf), the macOS BSD userland (check script), and the sandbox allowlist (check script). Findings F1, F2, F5, F14.

### Item 3: boundaries, partitions, and the negative control

- **Control:** the verification block has only denial rows. No allowed-path row (for example `gh auth status`, `git status`, reading the project tree, or `uv run`) would catch an over-broad deny (F12).
- **Partitions:** the check script's failure branches, the wrong-tool case on macOS, and timeouts are not tested by any test (F13).
- **Limits on the same work:** the sandbox network allowlist does not admit the socat host the script queries (F1). The script's `curl` calls have no timeout, so a stalled connection never reaches the failure branch (F3). Other limits: the `[tool.uv] exclude-newer` and Dependabot 7-day cooldowns exist, but they do not wrap this work.
- **Pre-existing state:** the `sandbox.enabled` setting applies to every contributor who opens the repo. The doc does not say what happens when bubblewrap is missing on Linux (F17).
- **Replacement mechanism:** none.

### Item 3a: level, placement, and the environment

Each new behavior is observable in one process without a network: the wrapper's environment filtering (sourced function with a fake `claude` on `PATH`), and the check script's table parsing (stubbed `curl`). Neither has a test (F13). No test uses a skip, and no CI job in the change runs any new file.

### Item 4: names by content, not by position

One finding: "per step 5 above" (F18, taste).

### Item 5: the failure report

- The check script maps any lookup failure to "upstream lookup failed (rate limit / network)". On macOS the cause is a missing GNU tool, and `2>/dev/null` plus `|| continue` hides it (F2).
- No assertions exist in the change.

### Item 6: what the writer says it verified

The commit states: `prek` passes (not checked here), the check script runs end to end (not reproduced; fails on macOS), the JSON parses (verified), and sandbox enforcement has not been exercised. No red run on the base commit and no mutation verdict is stated for the wrapper or the check script. That absence is F13.

### Item 7: siblings of the change

- **Set of three tools (bubblewrap, socat, claude-code):** every file that lists the set names all three. I checked the README, the setup doc table and install commands, the manifest, the tools README, and the case statement in the script. Nothing is missing.
- **Stale count:** "Three-layer defence" appears at `secure-agent-setup.md:7` and `:69` over four layers (F9).
- **Helpers:** `gh_latest_aged` has two callers (bubblewrap and claude-code), `socat_latest_aged` has one, `read_pinned` has one, and `claude_iso_main` has one. All were read. The GNU-only defect (F2) is confined to the socat path, which is the same symptom on the other operating system.
- **Python version:** `read_pinned` needs `tomllib` (Python 3.11+). The doc names no Python version. I did not check the macOS system Python.

### §2a: added instructions in `AGENTS.md`

Added instructions: 1.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md:312` "Run the agent in the credential-isolation setup." | a typo fix in `README.md`, with no tracker or CVE content | tells the user to relaunch under `claude-iso` before it edits, or stops | none in the text; needs "only where the session reads tracker or pre-disclosure content" |

Not findings: none.

---

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The sandbox allowlist omits `www.dest-unreach.org`, which the socat lookup queries. The weekly run is supposed to use the same sandbox, so the socat row should fail there. The allowlist is described as "every host the framework legitimately reaches". Not run: no network. | substantive | `.claude/settings.json` `sandbox.network.allowedDomains`; `tools/agent-isolation/check-tool-updates.sh:90,96` | Add the host, or move the socat lookup out of the sandboxed run, and run the check inside the sandbox |
| F2 | `tac` (line 92) and `date -d` (line 101) are GNU-only. On this macOS, `date -d` returns "illegal option". The socat row then prints "upstream lookup failed (rate limit / network)" every time. | substantive | `check-tool-updates.sh:92,101` and the report loop | Use `python3` for the date parsing, as `gh_latest_aged` already does, and replace `tac` with a portable form; name the real cause in the failure line instead of hiding it |
| F3 | The `curl` calls have no timeout. A stalled connection never returns, so the failure branch never runs and the weekly run hangs. | substantive | `check-tool-updates.sh:68,90,96` | Add `--max-time` (and `--connect-timeout`) to each call |
| F4 | The comments say the script reports releases "newer than the pin" and that plain `<` gives ordered output. The code only tests `==`. A pin newer than upstream is also reported as an "upgrade candidate". | substantive | `check-tool-updates.sh:22,160–168` | Fix the comments to say "differs from the pin", or implement the ordered comparison |
| F5 | The header examples `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` do not pass the variable through `env -i`. Run with a fake `claude`: `GH_TOKEN` is unset. The `CLAUDE_ISO_ALLOW` form in the doc does pass it. | substantive | `claude-iso.sh:40–41` | Replace the examples with the `CLAUDE_ISO_ALLOW` form used in `secure-agent-setup.md:273` |
| F6 | The block comment says variables set on the invocation line are "preserved" and that "we honour it", then says the code cannot tell. The code drops them. | substantive | `claude-iso.sh:88–96` and `:104–110` | Delete the paragraph; state that `CLAUDE_ISO_ALLOW` is the only path |
| F7 | "The socket alone is harmless" is unsupported. An SSH agent socket lets any process in the session sign with loaded keys. The threat model names this credential class, and the residual risks omit it. | substantive | `claude-iso.sh:73`; `secure-agent-setup.md` Residual risks (~325) | Drop the claim; either drop the passthrough or add it to the residual risks |
| F8 | The manifest gives socat 1.8.1.1 `released = "2026-03-13"`. The commit's own check output gives `UPSTREAM@ 2026-02-12` for the same version. The script derives that date from the tarball's `Last-Modified`. | substantive | `pinned-versions.toml:69`; `check-tool-updates.sh:96–103`; commit message table | Pick one source for the date; if `Last-Modified`, say so and stop calling it the release date |
| F9 | "Three-layer defence" heads a table with four layers (0–3). The commit says four. | substantive | `secure-agent-setup.md:7,69` | Retitle to "Four-layer defence" in both the TOC and the heading |
| F10 | The README calls bubblewrap, socat, and claude-code "required system tools". The setup doc says bubblewrap is not needed on macOS and socat is optional there. | substantive | `README.md:165` | Qualify by platform, matching the setup doc |
| F11 | The `AGENTS.md` instruction has no clause that ends it. A running agent cannot satisfy it, because it is already running. | substantive | `AGENTS.md:312` | Scope it: "When a session will read tracker or pre-disclosure content, start it with `claude-iso`", addressed to the operator |
| F12 | The verification block has denial rows only, with no control. An over-broad deny would pass. | substantive | `secure-agent-setup.md` Verification (~307–320) | Add allowed-path rows (`gh auth status`, `git status`, reading `AGENTS.md`, `uv run`) and require each to succeed |
| F13 | No claimed case has a test, and the commit states none was run for the enforcement layers. No red run on the base commit or mutation verdict is stated for the wrapper or the script. | substantive | the new files; commit "Test plan" | Add a shell test that puts a fake `claude` on `PATH` and asserts the environment; add a stubbed-`curl` run for the script's failure paths; record the red run for each |
| F14 | The documented install commands (apt with `=0.11.1-*`, dnf with a different form, brew, npm) have no run and no CI counterpart. The change names no distro release, so their outcome is unknown. | substantive | `secure-agent-setup.md:113–131`; `pinned-versions.toml` `install.*` | Run on one named Debian/Ubuntu release and one Fedora release, or state the versions as unverified |
| F15 | `/path/to/airflow-steward/` appears in new docs. The framework is project-agnostic (`AGENTS.md:55`), and commit b73e240 removed Airflow remnants. | substantive | `secure-agent-setup.md:253`; `tools/agent-isolation/README.md:40,47` | Use the `<framework>` placeholder |
| F16 | The commit says `AGENTS.md` links the doc from an "agent prerequisites" section. There is no such section; only the "Local setup" link exists. | substantive | commit message; `AGENTS.md` | Reword the claim, or add the link where it is claimed |
| F17 | `.claude/settings.json` enables the sandbox for every contributor who opens the repo. The doc says bubblewrap is "required on Linux" but not what happens when it is absent. Not verified: I did not check Claude Code's behavior offline. | substantive | `secure-agent-setup.md:96`; `.claude/settings.json` `sandbox.enabled` | State the fail mode, or run on a Linux host without bubblewrap |
| F18 | "per step 5 above" points at a step by position. | taste | `secure-agent-setup.md:174` | Name the step: "the 'Open the bump as its own PR' step" |

---

## Not checked

The check script's upstream queries (no network), any apt, dnf, npm, or brew install, the bubblewrap and Seatbelt enforcement, `prek`, Claude Code's handling of the settings keys (no schema check offline), the external doc links, the `AGENTS.md` anchors, and the wrapper's effect on `TMPDIR` in a real Claude Code session (the wrapper drops it; I did not test what depends on it). `bash -n` passed on both scripts, `shellcheck` with default checks printed nothing, and the TOML and JSON both parse.
