## Final review: `2efe27f..HEAD` (commit `1b569a8`, 8 files, +929)

**Setup.** No previous report exists, so this is round one. No task statement was handed over, so the claimed cases come from the commit message, the doc, and the manifest. Skills loaded: `english-developer-style` and `apm-authoring`. `apm-authoring` applies because `AGENTS.md` is an instruction file; this repo has no `apm.yml`, so its hand-edit rule does not apply. `docs-page-authoring` is not among the four, so the docs-page analogues come from `final-review` §2a. `test-authoring` was not loaded because the change has no test code. The drift script ran and printed nothing, since no Python member changed and the shell and TOML files are not parsed.

**Claims taken from the commit message:** C1 four layers, each implemented; C2 layers 1–3 in `settings.json`, layer 0 in `claude-iso.sh`; C3 every pin released at least 7 days before `pinned_at`; C4 the check script is side-effect-free and surfaces only aged candidates; C5 the doc's `/schedule` wiring; C6 README and AGENTS links; C7 `prek` passes, the script runs end-to-end, the settings parse, and sandbox enforcement is untested.

**Run locally:** `bash -n` passes on both scripts, `settings.json` parses, `git show --check` is clean, and `claude-iso` was run against a stub `claude` in `$TMPDIR` (four cases, below). Nothing in the repo was touched.

### Item 1: comments consistent with the code and with each other

Analogue: the code analogue for the shell scripts, the §2a analogue for `AGENTS.md` and the doc.

- `claude-iso.sh:85–90` says any variable set on the invocation line is preserved. The code keeps only names listed in `CLAUDE_ISO_ALLOW`. The same comment says "we detect this by comparing the inherited env", but no comparison exists (F2).
- `claude-iso.sh:104–109` says "we honour it" and then reverses itself. The block has no code (F2).
- `claude-iso.sh:73` says the agent socket is "harmless" with no support for that claim (F3).
- `check-tool-updates.sh:163–167` says a lexical `<` comparison decides upgrades. The code at line 160 tests `==` (F5).
- `secure-agent-setup.md:69` is headed "Three-layer defence" over a four-row table (F17).
- Other comments checked against the code and found true: the cooldown `<=` (lines 75, 102), the bump steps, the TOC anchors, and the `pyproject.toml` (line 65) and Dependabot (`cooldown` 7 days) citations.

### Item 2: claimed cases covered

- **Cases with no test:** C1 and C2 (env stripping, `CLAUDE_ISO_ALLOW`), C4 (the check script's behavior), and the `/schedule` wiring. Requests in F13.
- **Command lines, each with `none` as the runner:**
  - the apt and dnf pin installs (`secure-agent-setup.md:112–124`);
  - the npm claude-code install (`:136`);
  - `claude-iso` and `CLAUDE_ISO_ALLOW=… claude-iso` (`:259–277`). The doc form works in the stub run. The header form in `claude-iso.sh:39–41` does not (F1);
  - the verification block (`:315–317`, F15);
  - `check-tool-updates.sh`, which fails the socat row on darwin (F6);
  - `/schedule weekly run …` (`:166–168`, F8);
  - `git check-ignore` (`:305`).
- **Hunks:** every hunk is claimed by a sentence of the commit message or the description. No unclaimed hunk.
- **Commit-message evidence against the manifest:** F9.

### Item 3: boundaries, partitions, negative control, limits, pre-existing state

- **Control:** the stub run shows the control behaves as intended. `GH_TOKEN` is dropped without `CLAUDE_ISO_ALLOW` and kept with it. No test in the change pins that.
- **Boundary:** `claude-code` is pinned exactly 7 days old (`pinned_at` 04-29, released 04-22). The `<=` cutoff is untested at that boundary (F13).
- **Limits:** no `--max-time` on any `curl` in the check script (F7).
- **Pre-existing state:** a tree that already has `.claude/settings.local.json` or user-level rules was not checked.

### Item 3a: level and placement

The `claude-iso` env handling is observable in one process with a stub `claude`. The change has no test at any level (F13).

### Item 4: names by content

`secure-agent-setup.md:174` says "per step 5 above" (F14).

### Item 5: failure report

`claude-iso.sh:49` names the reason and the action. The socat row on darwin prints "rate limit / network" for a date-parse failure, which is the wrong reason (F6).

### Item 6: what the writer says it verified

No red run, no mutation run, and no test. The commit states that sandbox enforcement was not run. The verification block asserts outcomes nobody has run (F15).

### Item 7: siblings

- The `gh` ask list omits verbs the skills use or that post to the tracker (F16).
- The Read-deny list is an enumeration (F18).
- The allowlist omits the socat host the doc's own routine needs (F8).
- The doc's allowlist and deny list match `settings.json`.
- All three pinned tools appear consistently in the manifest, the doc, the check script's `case`, and the README.

### §2a table: `AGENTS.md`

Added instructions: 1 (the imperative at `AGENTS.md:312`).

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup." | a session that fixes a README typo with no CVE content | an instruction it cannot check or act on | "only where the session reads pre-disclosure CVE content" |

Not findings: none.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Header example `GH_TOKEN="$(gh auth token)" claude-iso` (and `AWS_PROFILE=…`) drops the variable without `CLAUDE_ISO_ALLOW`. Stub: absent in both the header and direct-exec forms. | substantive | `tools/agent-isolation/claude-iso.sh:39–41` | Use the `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` form the doc uses (`secure-agent-setup.md:273`). |
| F2 | Comments say invocation-line variables are preserved and "we honour it", and claim an env comparison; the code keeps only `CLAUDE_ISO_ALLOW` names. | substantive | `claude-iso.sh:85–90`, `104–109` | Delete 104–109; rewrite 85–90 to say `CLAUDE_ISO_ALLOW` is the only route. |
| F3 | "the socket alone is harmless": an agent socket lets any process in the session sign with the user's SSH keys, and SSH keys are in the threat model. | substantive | `claude-iso.sh:73`; `secure-agent-setup.md:36` | Drop `SSH_AUTH_SOCK`, or state the risk in the comment and the residual-risks section. |
| F4 | The doc's passthrough list omits `LC_ALL`, `LC_CTYPE`, `WAYLAND_DISPLAY`, and reduces four `XDG_*` names to a glob. | substantive | `secure-agent-setup.md:264–266` vs `claude-iso.sh:56–74` | List the set the code has. |
| F5 | Comment says a lexical `<` decides upgrades; the code tests `==`, so an older upstream also prints "upgrade candidate". The doc says "newer than the pin". | substantive | `check-tool-updates.sh:160`, `163–168`; `secure-agent-setup.md:144–147` | Compare versions (`sort -V` or Python), then fix the comment and doc. |
| F6 | Socat row on darwin always fails: `tac` is not stock, and `date -d` fails here ("illegal option -- d"), so the row reports "rate limit / network". The commit claims an end-to-end run. | substantive | `check-tool-updates.sh:92`, `101`, `103` | Parse `Last-Modified` portably (Python or `date -j -f`), and report a parse failure as such. |
| F7 | No `--max-time` on any `curl`; the socat loop makes one HEAD request per version. | substantive | `check-tool-updates.sh:68`, `90`, `96` | Add `--max-time`. |
| F8 | `www.dest-unreach.org` is not in the sandbox allowlist, so the socat row fails under the framework's own settings. The doc says the scheduled run uses the same setup. | substantive | `.claude/settings.json:19–34`; `secure-agent-setup.md:171–175` | Add the host, or drop the socat row from the routine, and say which. |
| F9 | Commit table gives socat `PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12` for the same version 1.8.1.1. The manifest says 2026-03-13. | substantive | commit `1b569a8` message; `pinned-versions.toml:69` | The message cannot be edited in history: correct it in the PR description, and reconcile the manifest date with what the script reads. |
| F10 | C2 (layer 0 keeps the named credential in and drops the rest) and C4 (script never installs, edits, or PRs) have no test by name. | substantive | commit C2, C4 | See F13. |
| F11 | Boundary at exactly 7 days (`<=`) is not tested. | substantive | `check-tool-updates.sh:75`, `102` | Add a fixture-based check at the cutoff. |
| F12 | Pre-existing `.claude/settings.local.json` or user-level rules are not considered. | taste | `.claude/settings.json` | State that the project file is the only one assumed. |
| F13 | No in-process test for `claude-iso`, although a stub `claude` makes it one. Four cases to pin: default drop, named keep, multi-name keep, header form. | substantive | `tools/agent-isolation/` | Add a shell test that runs those four cases and fails on F1's form. |
| F14 | "per step 5 above" points by ordinal. | taste | `secure-agent-setup.md:174` | "per the bump procedure above". |
| F15 | The verification block's expected outcomes are unrun; the commit says so. | substantive | `secure-agent-setup.md:312–318` | Run the block inside `claude-iso` on macOS Seatbelt, and paste the outputs into the PR description. |
| F16 | Ask list omits `gh pr comment`, `gh pr review`, `gh pr close`, `gh label create` (used by `fix-security-issue/SKILL.md:680` and `sync-security-issue/SKILL.md:241`), `gh issue reopen`. `gh api` patterns miss `--method`, `-XPOST`, `--field`, `--raw-field`. | substantive | `.claude/settings.json:62–76` | Add the verbs and the long and attached flag forms. |
| F17 | "Three-layer defence" over a table of layers 0–3; the commit says four. | substantive | `secure-agent-setup.md:69`, `7`, `71–76` | "Four layers (0–3)" and regenerate the TOC. |
| F18 | Read-tool deny list is an enumeration: `~/.npmrc`, `~/.pypirc`, `~/.git-credentials`, `~/.gnupg`, `~/.config/op` are not denied. Prefix rules do not catch `bash x.sh` or `python3 -c`. The doc's Layer 2 row says it stops dotfile reads. | substantive | `.claude/settings.json:38–53`; `secure-agent-setup.md:75` | Add the paths, or list the gap as a residual risk. |
| F19 | "the agent should never see it": `gh auth token` is not denied, and Bash can read `~/.config/gh` through `allowRead`. The Read deny blocks only the Read tool. | substantive | `secure-agent-setup.md:236–241`; `.claude/settings.json:6`, `19`, `44` | Correct the sentence, and list it as a residual risk or deny the Bash forms. |
| F20 | "Every system-level tool the secure setup depends on is pinned": `python3` ≥ 3.11 (`tomllib`) and `curl` are not. | substantive | `secure-agent-setup.md:85–86`; `check-tool-updates.sh:116–121` | Say which dependencies are unpinned. |
| F21 | README says bubblewrap and socat are "required"; the doc says bubblewrap is not needed on macOS. | substantive | `README.md:165–166`; `secure-agent-setup.md:127–130` | "On Linux, bubblewrap and socat are required." |
| F22 | "Run the agent in the credential-isolation setup." has no end condition. | substantive | `AGENTS.md:312–313` | "Where a session reads pre-disclosure CVE content, run it under the setup in `secure-agent-setup.md`, and stop if it does not." |
| F23 | Sourced `claude-iso` uses `exec`, which replaces the interactive shell, so the terminal closes on exit. The doc does not say so. | taste | `claude-iso.sh:111` | State it, or run in a subshell. |
| F24 | Example paths use `airflow-steward`; the repo is to be renamed, and `AGENTS.md` names a `<framework>` placeholder for this. | taste | `secure-agent-setup.md:253`; `tools/agent-isolation/README.md:40`, `47` | Use `<framework>`. |

**Not checked:** `prek run --all-files` was not run and `shellcheck` is not installed here. Sandbox enforcement needs bubblewrap or Seatbelt and a live session. External links (`code.claude.com`) and upstream API results need network access. I did not test whether Claude Code's matcher treats a bare `git push` against `git push *`. The style pass over the prose was not done; this review covers only the form above.
