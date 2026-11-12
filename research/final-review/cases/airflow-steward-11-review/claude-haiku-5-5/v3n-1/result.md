## Final review of `2efe27f..HEAD` (commit `1b569a8`, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

**Inputs.** No task statement was handed over, and I cannot ask, so the claimed cases come from the commit message, the new `secure-agent-setup.md`, and the file headers. No previous report exists, so there is no prior-findings table. The diff touches `.claude/settings.json`, `AGENTS.md`, `README.md`, `secure-agent-setup.md`, and four files under `tools/agent-isolation/`. There are no tests and no code members.

**Skills loaded.** `english-developer-style` and `apm-authoring` from the given skills directory. `apm-authoring` applies to `AGENTS.md` only, and this repo has no `apm.yml` or `.apm/`, so its "hand-edited AGENTS.md" pitfall does not apply. `test-authoring` was not loaded because the change has no tests. `docs-page-authoring` is not in the given set, so §2a's docs-page analogues were applied directly.

**Drift script.** Run as `comment-drift.py 2efe27f… HEAD`. It printed nothing and exited 0. The changed files are `.md`, `.sh`, `.toml`, and `.json`, which the parser does not cover, so Item 1 was read by hand.

**Checks I ran locally (no network, no files changed):**
- `shellcheck` and `bash -n` on both scripts: clean.
- `settings.json` parses as JSON.
- `claude-iso.sh` run with a fake `claude` that prints its environment:
  - `GH_TOKEN=… claude-iso` on the invocation line: `GH_TOKEN` dropped.
  - `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso`: `GH_TOKEN` passed.
  - `AWS_PROFILE` from the parent shell: dropped.
  - `SSH_AUTH_SOCK`: passed.
- `date -d` on this macOS host: `illegal option -- d`.
- Anchors: `README.md#prerequisites-for-running-the-agent-skills` and the `AGENTS.md` anchors resolve; the `doctoc` TOC headings match.

### Item 1: comments consistent with the code and with each other

Findings F1–F7, F12–F13 and F17–F21 below, which the form sorts here. Those touch:
- the wrapper's usage header and its "invocation line is preserved" comment (F2);
- the `SSH_AUTH_SOCK` comment (F3);
- the "the AGENT can't" comment on the deny list (F1);
- the "three-layer" heading (F5);
- the "`<` comparison" comment in the check script and the "newer than the pin" wording in the doc and the script header (F6);
- the `--no-save` rationale (F13).

No narration of the change (`now`, `no longer`, `used to`) was found.

### Item 2: claimed cases covered

**Claimed cases with no test.** The change has no tests and its test plan is a live run. The cooldown filter, the status logic, and the socat parse are claimed but unexercised (F12). Layer 2 and Layer 3 are claimed but unverified (F11). The sandbox enforcement is stated as untested in the commit.

**Commands the change tells a reader to run:**

| Command (location) | Promised outcome | Same command run in CI or a script? | Result here |
|---|---|---|---|
| `apt-get install … bubblewrap=0.11.1-* socat=1.8.1.1-*` (`secure-agent-setup.md:114-116`) | Pinned versions installed | none | Not run; needs a Debian/Ubuntu host (F14) |
| `dnf install bubblewrap-0.11.1 socat-1.8.1.1` (`:122-124`) | Pinned versions installed | none | Not run; needs a Fedora/RHEL host (F14) |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` (`:136`) | Pinned version installed | none | Not run (F13, F14) |
| `bash tools/agent-isolation/check-tool-updates.sh` (`:144`) | Table of upstream candidates | none | Not run; needs network |
| `/schedule weekly run …` (`:166-168`) | Weekly candidates surfaced | none | Not run (F9) |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN="$(gh auth token)" claude-iso` (`:273`) | Token passed for one session | none | Equivalent form passes `GH_TOKEN` (fake `claude`) |
| `GH_TOKEN="$(gh auth token)" claude-iso` (`claude-iso.sh:40`) | Token passed | none | **Fails**: token dropped (F2) |
| `AWS_PROFILE=read-only claude-iso` (`claude-iso.sh:41`) | Profile passed | none | Same mechanism as line 40: dropped (F2) |
| `python3 -c 'import json; json.load(...)'` (commit test plan) | Parses | none | Ran: parses |
| `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com` (`:315-317`) | Each denied or empty | none | Not run; no sandboxed session here |
| `git check-ignore .claude/settings.local.json` (`:305`) | Ignored | none | Not run |
| `prek run --all-files` (commit test plan) | Passes | none | Not run; `prek` not installed |

**Hunks against the claims.** Every hunk is claimed by a sentence of the commit or the doc, except the `install.brew` line for `claude-code` (F16).

### Item 3: boundaries, partitions, and the negative control

- **Control.** The wrapper's control holds: a variable not on the passthrough list and not named in `CLAUDE_ISO_ALLOW` is dropped (`AWS_PROFILE` absent, verified).
- **Missing partition.** The sandbox `allowRead` partition for `~/.config/gh` and `~/.config/apache-steward` is the failing corner and has no control or run (F1).
- **Pre-existing state.** Adopters copy `settings.json` into a tracker repo that may already have one, and the doc does not say what to do (F22).
- **Limits.** `curl` calls in the check script have no timeout, so one stalled request can hold up the weekly routine (F12).
- **3a.** No test is at any level (F12).

### Item 4: names by content, not by position

One finding: `secure-agent-setup.md:174` says "per step 5 above" (F18).

### Item 5: the failure report

None. The change has no assertions; the script's failure message `upstream lookup failed` names no cause and is not reported.

### Item 6: what the writer says it verified

The change states the sandbox enforcement is untested and that a red run is left to the maintainer. No red run, mutation run, or negative check on the `gh`/`apache-steward` path is stated. The only stated checks are `prek`, the live script run, and JSON parse.

### Item 7: siblings of the change

- **Platform sibling.** `date -d` and `tomllib` make the check script fail on macOS, which the doc treats as supported (F7).
- **Allowlist sibling.** `dest-unreach.org` is used by the script and the weekly routine but is absent from `allowedDomains` (F9).
- **Passthrough list.** The doc's list omits `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which the script passes (F15).
- **Ask list.** `gh pr comment` and `gh pr review` are not in `ask` (F21).
- **Version sibling.** Pinned versions agree across the doc, the manifest, `tools/agent-isolation/README.md`, and the root `README`. The socat release date does not (F8).
- **Remedies.** None in the doc have a symptom row. Nothing else to check.

### Added instructions (§2a)

`AGENTS.md`: `Added instructions: 1, no rows.` Its scope ambiguity goes to F19 under Item 1. `Not findings: none.`

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The `allowRead` entries for `~/.config/gh/` and `~/.config/apache-steward/` let a Bash subprocess read the gh token and the Gmail OAuth file. `permissions.deny` covers only the Read tool, so `cat` from the agent's Bash tool succeeds. The comment "the AGENT can't" is false, and prompt injection (threat 2) reaches the Gmail token. | Substantive | `.claude/settings.json:11,15`; `secure-agent-setup.md:193,197,214-215,236-241,75` | Remove the "agent can't see it" claim. Add both paths to Residual risks and the threat model. Add a Verification line for the Bash read. Or move the token out of the file (wrapper injection). |
| F2 | The documented one-off injection `GH_TOKEN=… claude-iso` is dropped by `env -i`. The header and the "invocation line is preserved" comment say otherwise. Verified. | Substantive | `tools/agent-isolation/claude-iso.sh:40-41, 86-87, 104-109` | Use the `CLAUDE_ISO_ALLOW` form in the header. Correct the comment at 86-87. Delete the dead "well, actually" block at 104-109. |
| F3 | `SSH_AUTH_SOCK` is passed through, and its comment says "the socket alone is harmless". Any process that can reach the agent socket can sign with its keys. That contradicts the threat model's "SSH keys" protection. | Substantive | `claude-iso.sh:73`; `secure-agent-setup.md:36, 265` | Remove the variable, or state the exposure in Residual risks and correct the comment. |
| F4 | Layer 2 says `permissions.deny` covers Read/Edit/Write/Bash and stops "cat-ing dotfiles". The config has no Edit or Write rules and no Bash `cat` rule. | Substantive | `secure-agent-setup.md:75` | Name only the rules that exist. |
| F5 | The heading says "Three-layer defence", but the table has four layers (0–3). The commit message says four. | Substantive | `secure-agent-setup.md:69` (TOC line 7) | Rename to "Four-layer defence" and update the TOC in the same edit. |
| F6 | The check script says it reports releases "newer than the pinned versions", and a comment says a plain `<` comparison does the work. The code has no `<`. Any inequality is labeled "upgrade candidate", including an older upstream. The doc repeats "newer than the pin". | Substantive | `check-tool-updates.sh:21-23, 163-168`; `secure-agent-setup.md:145-147` | Compare with `sort -V` or Python, or say "differs from the pin" in all three places. |
| F7 | `date -d` is GNU-only. On this macOS host it fails with `illegal option -- d`. The `|| continue` at line 101 skips every socat tarball, so the socat row always reads "upstream lookup failed" on macOS. `tomllib` at line 117 needs Python 3.11 or later, and the doc's macOS path does not install one. | Substantive | `check-tool-updates.sh:101, 117`; `secure-agent-setup.md:127-130` | Parse the date in Python (already a dependency here), and state the Python requirement. Or scope the script to Linux. |
| F8 | The manifest says socat 1.8.1.1 was released 2026-03-13. The check output in the commit message shows upstream `UPSTREAM@ 2026-02-12` for the same version. The release-date field contradicts the script's own evidence. | Substantive | `pinned-versions.toml` (`released` for socat, line 69); commit message table; `secure-agent-setup.md:97` | Verify the release date and state which field the script uses. |
| F9 | `allowedDomains` lacks `www.dest-unreach.org`. The script's socat lookup and the `/schedule` routine depend on it, so inside the configured sandbox that row cannot resolve. | Substantive | `.claude/settings.json:20-33`; `secure-agent-setup.md:201-207, 163-169`; `check-tool-updates.sh:90, 96` | Add the host to the allowlist, or state that the routine cannot check socat. |
| F10 | The `ask` patterns `gh api * -X *`, `-f`, `-F` do not match `gh api -X POST …`, `gh api … --method PATCH`, or `gh api … --field x=y`. The doc says "any non-default-method API call" and "any payload-bearing API call". Reasoned from the pattern text with an `fnmatch` approximation, not run in Claude Code. | Substantive | `.claude/settings.json:74-76`; `secure-agent-setup.md:229-230` | Add the flag-first and long-form patterns, or narrow the claim. |
| F11 | The Verification list covers `~/.aws`, the env var, and `curl`. It does not cover the `gh` or `apache-steward` reads (F1), any Layer 3 `ask`, or Edit/Write. The doc says verification "verif[ies] the setup actually denies what it claims to". | Substantive | `secure-agent-setup.md:307-323` | Add one line per claimed denial, starting with F1's paths. |
| F12 | No test covers the cooldown filter, the status logic, or the socat parse. The only evidence is a live run. The `curl` calls at lines 68, 90, and 96 have no `--max-time`, so a stalled request can hang the weekly run. | Substantive | `check-tool-updates.sh:68, 90, 96`; commit test plan | Add a fixture test for the three functions and the status line. Add `--max-time` to each `curl`. |
| F13 | The `--no-save` rationale is "so the global install doesn't drift the local lockfile". As I understand npm's documented behavior, `npm install -g` does not read or write the project's `package.json` or lockfile, so the stated reason does not apply. Not checked against npm here. | Substantive | `pinned-versions.toml` (`install.npm` comment, lines 97-100) | Drop the rationale or the flag. |
| F14 | The apt and dnf install commands, and the npm command, are run by no CI and were not run here. Whether `bubblewrap=0.11.1-*` and `bubblewrap-0.11.1` select a package is unknown offline. | Substantive | `secure-agent-setup.md:114-116, 122-124, 136` | Run the apt and dnf forms on a Debian/Ubuntu host and a Fedora host and paste the output. |
| F15 | The doc's passthrough list omits `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which the script passes. | Substantive (low) | `secure-agent-setup.md:264-267`; `claude-iso.sh` passthrough array | Make the doc list match the array. |
| F16 | `install.brew` for `claude-code` is a hunk no sentence claims. The doc says npm is "the only stable channel today", and the brew line says "(when available)". | Substantive (low) | `pinned-versions.toml:101` | Remove the line or claim it in the doc. |
| F17 | The doc says socat is "optional" on macOS and suggests `brew install socat`. The manifest's socat purpose says "macOS does not need it". | Taste | `secure-agent-setup.md:127-130`; manifest socat `purpose` | Pick one. The reader prefers the manifest's wording. |
| F18 | "per step 5 above" points by ordinal. | Taste | `secure-agent-setup.md:174` | Name the step: "the bump procedure's PR step". |
| F19 | The `AGENTS.md` sentence "Run the agent in the credential-isolation setup" reads as a rule that fires on every session, including doc-only edits with no CVE content. | Taste | `AGENTS.md`, Local setup, first added paragraph | State the condition: "when the session reads tracker or `<security-list>` content". |
| F20 | The header cites "the per-package override for `uv`" as part of the 7-day convention. That override is `"1 day"`. | Taste | `pinned-versions.toml` header; `pyproject.toml:76` | Say the convention has one exception. |
| F21 | `gh pr comment` and `gh pr review` are visible-to-others writes and are not in `ask`. | Taste | `secure-agent-setup.md:225-230`; `settings.json` ask list | Add them, or say the list is partial. |
| F22 | Adopters copy `settings.json` into a tracker repo that may already have one. The doc does not say whether to merge or overwrite. | Taste | `secure-agent-setup.md:289-291` | Say merge or overwrite. |

### Not checked

I did not run the sandboxed Claude Code session, the `prek` hooks, any `apt`, `dnf`, or `npm` install, or any network call, and did not check the claims against Claude Code's permission-matching source. I did not do a style pass over the prose beyond the wording the form asks for. A reviewer has not seen the threat model's residual risks as a whole. Local scratch output is in a `isotest.*` directory under `$TMPDIR`, outside the repository. No file in the repository was changed, and nothing was committed.
