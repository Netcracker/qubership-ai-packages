## Final review: `2efe27f..HEAD`

**Scope.** The range is one commit, `1b569a8` (`ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)`), 8 files, +929 lines. No task statement was handed over, so the claimed cases come from the commit message. No previous report exists, so the §4 table is empty.

**Skills loaded.** `final-review`, and `english-developer-style`, which applies to the comments and docs in shell, TOML, JSON and Markdown. `test-authoring` was not loaded because the change has no tests. The artifact analogue for `secure-agent-setup.md`, `docs-page-authoring`, is not among the three copies I was given, so I did not load it.

**Drift script.** `comment-drift.py 2efe27f… HEAD` exited 0 with no output. It parses Python members and this commit changes none. I read every comment by hand.

**Checks run locally.** `bash -n` and `shellcheck` on both scripts are clean. `settings.json` parses and the manifest parses with `tomllib`. I ran `claude-iso.sh` once with a stub `claude` on `PATH` (in `$TMPDIR`, removed afterwards). I did not run the check script, since there is no network. `date -d` is rejected by the BSD `date` on this host.

---

### Item 1: comments consistent with the code and with each other

Several comments state things the code or config does not do (F1–F8). Two are about security: F1 says the agent cannot see the gh and Gmail credential paths, and F4 calls the ssh-agent socket harmless. Narration words (`now`, `no longer`, `used to`) do not appear in the changed files.

### Item 2: claimed cases covered

Claims from the commit message, with the test that covers each:

- C1 Layer 0 strips credential-shaped env vars. No test. I checked it by hand: the stub shows the stripping and the `CLAUDE_ISO_ALLOW` path work, and the documented invocation-line path does not (F2, F3).
- C2 Layer 1 filesystem sandbox denies reads outside the project. No test. The commit says enforcement is unverified until bubblewrap runs on a host.
- C3 Layer 2 tool deny rules. No test. The doc's verification list (`secure-agent-setup.md:315-317`) is never executed.
- C4 Layer 3 `ask` rules. No test and no verification step.
- C5 Check script is side-effect-free and surfaces candidates aged past 7 days. No test. The cutoff cannot be fixed because the script has no clock input (F10).
- C6 Pinned versions were released at least 7 days before `pinned_at`. Checked by reading: bubblewrap 03-21, socat 03-13 and claude-code 04-22 against `pinned_at` 04-29 all hold. claude-code is exactly 7 days, and the script's `<=` accepts it.
- C7 `/schedule` weekly wiring. Not checked.
- C8 README and AGENTS link the new doc. Both links exist, and the anchors `#local-setup`, `#confidentiality-of-the-tracker-repository` and `#prerequisites-for-running-the-agent-skills` are in the TOCs.

Findings: F10.

### Item 3: boundaries, partitions and the negative control

- The control for C1 exists and works: `CLAUDE_ISO_ALLOW=GH_TOKEN` passes the token, and its absence strips it. No test holds either side (F10).
- The verification section lists only denials. No control shows that allowed work still succeeds inside the sandbox (F11).
- Pre-existing state is not addressed. I did not check how an adopter's existing `.claude/settings.local.json` or user-level settings merge with the copied `settings.json`.

### Item 3a: level, placement and environment

- `claude-iso.sh` is testable at the smallest level, with a stub `claude` on `PATH`. I ran exactly that. No test exists (F10).
- The check script's status logic needs a fixed clock and a `curl` shim. Neither has an injection point (F10).
- Environment: the socat path fails on macOS (F9) and needs a host the sandbox does not allow (F8).

### Item 4: names by content, not by position

Two ordinal references remain: "per step 5 above" and "No layer above" (F16). The layers are otherwise named by content.

### Item 5: the failure report

- The socat failure on macOS prints `upstream lookup failed (rate limit / network)`, which names the wrong cause (F9).
- The missing-binary message in `claude-iso.sh` names its cause and the fix. The expected outputs in the verification section are clear.

### Item 6: what the writer says it verified

No red run and no mutation verdict is stated. The commit's test plan says `prek` passes, which I did not run, per this item. It also says filesystem enforcement is unverified, which is an honest gap. The writer should state, for each layer, the denial they saw.

### Item 7: siblings of the change

- The `claude-iso` passthrough list is copied into the doc and the two copies differ (F12).
- The 14-entry `allowedDomains` list matches between `settings.json` and the doc. The check script's host is missing from it (F8).
- The Read-deny and `allowRead` split for `~/.config/gh/` and `~/.config/apache-steward/` has a sibling reader: Bash. No `Bash(...)` deny covers reading those paths (F1).
- `gh_latest_aged` is called twice, for bubblewrap and claude-code. Both call sites are fine.
- `pinned_at` has no reader, though three places describe it as enforced (F5).
- Version strings match across the manifest, the doc install lines and the tools README.
- The cooldown citations hold: `pyproject.toml:65` has `exclude-newer = "7 days"`, and `.github/dependabot.yml` has `default-days: 7`.

---

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Says the agent cannot see the gh and Gmail credentials, but `allowRead` lets Bash read them and no Bash deny covers reads. The doc's own mechanism (`:240-241`) limits the Read deny to the Read tool. | substantive | `.claude/settings.json:214-215`; `secure-agent-setup.md:236-241` | Correct both comments. Either deny Bash reads of those paths (a narrowing, not a boundary) or drop them from `allowRead` and say what breaks. Record the residual in "Residual risks". |
| F2 | Says env vars set on the `claude-iso` invocation line are preserved. The code does not do this. Verified: `GH_TOKEN=x claude-iso` (sourced) reaches claude with no `GH_TOKEN`. | substantive | `tools/agent-isolation/claude-iso.sh:85-90` | Delete the claim. State that `CLAUDE_ISO_ALLOW` is the only route. |
| F3 | Usage examples `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=... claude-iso` do not work. Verified: both are stripped. | substantive | `tools/agent-isolation/claude-iso.sh:39-41` | Use the form in `secure-agent-setup.md:273`: `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=... claude-iso`. |
| F4 | "the socket alone is harmless" is false. Any same-user process that reaches the ssh-agent socket can get signatures from the loaded keys. | substantive | `tools/agent-isolation/claude-iso.sh:73` (also passthrough at `secure-agent-setup.md:265`) | Say what the socket grants, or drop `SSH_AUTH_SOCK` and keep it as a stated residual risk. |
| F5 | Manifest says the check script uses `pinned_at` as the minimum age. The script never reads it: `read_pinned` emits only name, version and released. The doc repeats the claim. | substantive | `tools/agent-isolation/pinned-versions.toml:42-43`; `secure-agent-setup.md:100-102` | Make the script check `pinned_at`, or delete the claim from both places. |
| F6 | Comment says the script tests "newer than" and that "plain `<` does the right thing". The code only tests `!=` and reports any difference. The doc repeats "newer". | substantive | `tools/agent-isolation/check-tool-updates.sh:21-23, 163-166`; `secure-agent-setup.md:144-147` | Say "differs from the pin" in all three places. |
| F7 | Heading says "Three-layer defence" over a table of four layers (0 to 3). The commit message says four. | substantive | `secure-agent-setup.md:69` (TOC line 7) | Rename to "Four-layer defence" or "Layered defence". |
| F8 | Comment says `allowedDomains` lists "every host the framework legitimately reaches". The check script fetches `www.dest-unreach.org`, which is not listed, and the doc says the scheduled run uses the same sandbox. The socat row would fail there. | substantive | `.claude/settings.json:201`; `secure-agent-setup.md:201`; `check-tool-updates.sh:90, 96`; `secure-agent-setup.md:171-172` | Add the host with a comment, or move the socat lookup to a path the sandbox allows. Fix the comment otherwise. |
| F9 | `date -d` is GNU-only and fails on macOS (verified). The `|| continue` turns each failure into "upstream lookup failed (rate limit / network)", which names the wrong cause. `tac` is also GNU. | substantive | `check-tool-updates.sh:91-92, 101, 103` | Parse the HTTP date portably, for example with Python's `email.utils`, which the script already calls. Or document the script as Linux-only and print the real cause. |
| F10 | No test or check covers any of C1 to C6 in the commit message. A stub `claude` on `PATH` tests `claude-iso` at the smallest level. The status logic needs an injectable clock and a `curl` shim. | substantive | `tools/agent-isolation/` (no test file); `check-tool-updates.sh:53-54` | Add a shell test for `claude-iso` with a stub `claude` that prints its env. Add a fixture for the check script with a stub `curl` and a clock override, such as an env var or an argument. |
| F11 | Verification lists only denials. Nothing shows that allowed work still runs in the sandbox. | substantive | `secure-agent-setup.md:307-323` | Add expected-success commands, such as `gh auth status`, `git ls-remote origin` and `uv --version`. A too-tight sandbox otherwise looks like a pass. |
| F12 | Passthrough list in the doc omits `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`, which the script passes. | substantive | `secure-agent-setup.md:264-266`; `claude-iso.sh:61-72` | List all of them, or refer the reader to the script's array. |
| F13 | Layer 2 row names Edit and Write, but the deny config has no Edit or Write rules. | taste | `secure-agent-setup.md:75` | Say "Read and Bash". |
| F14 | Self-questioning comment block ("well, actually we can't reliably tell") describes a check the code does not perform. | taste | `claude-iso.sh:104-109` | Delete the block. The rule is already stated at lines 92-95. |
| F15 | "Strips every credential-shaped variable" describes a pattern filter. The code is an allowlist that drops everything else. | taste | `claude-iso.sh:22-24`; `tools/agent-isolation/README.md:30`; `secure-agent-setup.md:73` | Say "drops every variable not on the passthrough list". |
| F16 | Ordinal references: "per step 5 above" and "No layer above". | taste | `secure-agent-setup.md:174, 333` | Name the referent: the PR-review step of the bump procedure, and the layer in the table. |
| F17 | Manifest gives socat 1.8.1.1 a release date of 2026-03-13. The commit's own check output shows the same version's tarball dated 2026-02-12. The two dates measure different things. | taste | `pinned-versions.toml:69`; commit message output table | Confirm which date is the release date, and say so in the manifest comment. I could not check upstream offline. |
| F18 | Usage paths use `airflow-steward`, while the rest of the doc uses placeholders and AGENTS says the repo will be renamed. | taste | `tools/agent-isolation/README.md:40`; `secure-agent-setup.md:253` | Use `<framework>/tools/agent-isolation/claude-iso.sh`, per the placeholder table in AGENTS. |

---

**Not checked.** I did not run the sandbox (Seatbelt or bubblewrap), so F1 rests on reading the config and the doc. I did not check how Claude Code merges project and user permission rules, or whether `SSH_AUTH_SOCK` reaches the sandbox. I did not run the check script, `prek`, or the doctoc TOCs, and I did not verify upstream release dates offline. The socat claim in F9 comes from the BSD error, not a macOS run. The style pass was limited to wording that changes a sentence's meaning, as the skill directs. Nothing in the repository was changed or committed. My stub experiment ran in `$TMPDIR` and was removed.
