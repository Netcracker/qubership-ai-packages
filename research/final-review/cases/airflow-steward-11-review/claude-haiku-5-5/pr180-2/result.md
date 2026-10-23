# Final review: `2efe27f..HEAD` (commit `1b569a8`, `ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)`)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message, as the skill allows. Item 2 is answered from that message alone. There is no earlier report, so §4's table does not apply. I read all eight changed files whole. The change has no Python members, so the drift script ran and printed nothing. It parses Python-style members only, so it is not evidence for shell, TOML, or Markdown. Every item uses the §2a analogues. I loaded `final-review`, `english-developer-style`, and `test-authoring`, from the copies under the skills directory.

## Item 1: comments consistent with the code and with each other

Analogue: each statement a changed file makes about another file, about the code, or about a count.

- F2: the setup doc's heading says "Three-layer defence" over a four-row table (layers 0 to 3).
- F4: `pinned-versions.toml` says the check script reads `pinned_at`. It does not.
- F5: the check script's comment describes a `<` comparison. The code only tests `==`.
- F10: `claude-iso.sh` describes invocation-line variables that are preserved. The code does not do that, and a later block retracts it.
- F11: the wrapper is described as stripping credential-shaped variables. The code is an allowlist.
- F1: `settings.json` (in the doc's annotated copy) says the agent cannot read the gh and Gmail OAuth paths. The rules do not enforce that.
- F3: "every system-level tool ... is pinned", while the same setup uses `gh` and `uv`, which are not pinned.
- Narration words (`now`, `no longer`, `used to`): none in the new files.
- Checked and consistent: the `[tool.uv] exclude-newer = "7 days"` and Dependabot 7-day cooldown claims (`pyproject.toml:65`, `.github/dependabot.yml`), and the README and AGENTS.md text.

## Item 2: claimed cases covered

Analogue: the claimed cases have no test, because this is configuration. Each claim is checked by reading or arithmetic.

- Layer 0 and layers 1 to 3 are present. Layer 1 (the sandbox) has no test, and the commit says the first run is the maintainer's.
- The check script never installs, edits the manifest, or opens a PR. Verified: it has no writes, no `git`, and no install.
- Every pin is at least 7 days before `pinned_at` 2026-04-29. Verified: bubblewrap 39 days, socat 47, claude-code exactly 7.
- The settings JSON parses (`json.tool`). The manifest parses (`tomllib`).
- Not reproduced: "prek passes" and "the script runs end-to-end, queries upstream". There is no network, and prek's doctoc hook would rewrite files.
- F14 (taste) and F17 (taste) are wording points only.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the paths and commands the rules cover, and the control is a path that must stay allowed.

- No control exists for the deny rules. The uncovered partition is a Bash read of `~/.config/gh` and `~/.config/apache-steward`, which is F1.
- The network partition misses two hosts the framework uses (F7).
- The inherited state is an adopter's existing `.claude/settings.json`, which the copy step overwrites (F14).

## Item 3a: level, placement, and environment

- Enforcement exists only across the process boundary. No CI job runs it, and no in-process test is owed. The first run is the maintainer's, and F1 names the case that run must include.
- Offline gates run: `bash -n` and `shellcheck` are clean on both scripts. `prek` was not run, for the reason in Item 2.
- Layout: `tools/agent-isolation/README.md` where sibling adapters use `tool.md` (F16, taste).

## Item 4: names by content, not by position

- F15 (taste): `secure-agent-setup.md:174` says "per step 5 above". Name the pull-request step by its content.
- No test or case names exist in the change.

## Item 5: the failure report

- F6: `check-tool-updates.sh:152-153` prints "upstream lookup failed (rate limit / network)". On macOS the cause is `date -d`, which BSD `date` rejects (verified: `date: illegal option -- d`), and `tac`, which is absent on stock macOS. The reported cause is wrong.
- `claude-iso.sh:49` names the reason and the action. No finding.

## Item 6: what the writer says it verified

- The writer states the shell and JSON checks, the script run, and that sandbox enforcement is untested. That last statement is the honest part. F1 and F8 are the claims the first run would catch.
- No red-run evidence applies to a configuration change. Nothing else is claimed.

## Item 7: siblings of the change

Analogue: the sibling sites are the other callers of each rule.

- **`Bash(curl *)` deny (F8).** At least five instructed bare-`curl` sites are blocked: `sync-security-issue/SKILL.md:873`, `tools/cve-org/tool.md:66` and `:90`, and `tools/gmail/ponymail-archive.md:81` and `:139`. Two more mention curl at `sync-security-issue/SKILL.md:624` and `:742`. The criterion is a bare `curl` command in an instruction. I did not read every line of every skill, so this count is for that criterion only.
- **Allowed hosts (F7).** `cveawg.mitre.org` and `www.dest-unreach.org` are missing.
- **`ask` rule (F9).** `gh label create`, `gh issue reopen`, and `gh repo fork` are visible writes that the rule does not catch.
- **Checked and consistent:** the oauth-draft path `~/.config/apache-steward/gmail-oauth.json` matches `allowRead`, and the README anchor `#prerequisites-for-running-the-agent-skills` exists.

## Findings

Substantive findings are requests. Taste findings are noted for the record, and churn findings are not reported.

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The agent is said never to see the gh and Gmail OAuth tokens. Both paths are in `allowRead`, and only the Read tool is denied, so Bash can read them. | substantive | `secure-agent-setup.md:212-215, 236-241`; `.claude/settings.json:11,15` | State the real boundary, add it to residual risks, and have the first run `cat` one of these paths. |
| F2 | The heading says three layers over a four-layer table. | substantive | `secure-agent-setup.md:69, 71-76` | Change "Three-layer" to "Four-layer", or fix the count. |
| F3 | "Every system-level tool ... is pinned" is false: `gh`, `uv`, and `git` are used and unpinned. | substantive | `secure-agent-setup.md:85-86, 193-195` | Narrow the claim to the three pinned tools, or list the unpinned ones. |
| F4 | `pinned_at` is said to be read by the check script. It is not. | substantive | `pinned-versions.toml:42-43`; `check-tool-updates.sh:115-123` | Delete the sentence, or make the script read the field. |
| F5 | The comment describes a `<` comparison. The code tests only `==`, and any difference is an upgrade candidate. | substantive | `check-tool-updates.sh:160, 163-167` (header 21-22) | Correct the comment to "not equal", or implement the comparison. |
| F6 | On macOS, `date -d` and `tac` fail. The socat row always reports "rate limit / network". | substantive | `check-tool-updates.sh:92, 101, 152-153` | Parse dates with `python3`, which the script already uses, and print the real cause. Or state the script is Linux-only. |
| F7 | The doc claims the allowlist covers every host the framework reaches. `cveawg.mitre.org` and `www.dest-unreach.org` are missing, so the sandboxed weekly check fails for socat. | substantive | `secure-agent-setup.md:201`; `settings.json` allowedDomains; `check-tool-updates.sh:90` | Add both hosts, or narrow the claim. |
| F8 | The `Bash(curl *)` deny blocks the framework's own instructed curl calls, and `cveawg.mitre.org` is not allowed. | substantive | `.claude/settings.json` deny; `secure-agent-setup.md:218`; `sync-security-issue/SKILL.md:873`; `tools/cve-org/tool.md:66, 90`; `tools/gmail/ponymail-archive.md:81, 139` | Route those calls through an allowed path, or narrow the deny rule, and reconcile the doc. |
| F9 | The `ask` list omits visible writes the skills run: `gh label create`, `gh issue reopen`, and `gh repo fork`. | substantive | `secure-agent-setup.md:223-231`; `fix-security-issue/SKILL.md:146, 680`; `tools/github/labels.md:74`; `tools/github/operations.md:150` | Add them to `ask`, or narrow the Layer 3 description. |
| F10 | The comment says invocation-line variables are preserved and detectable. The code honors only `CLAUDE_ISO_ALLOW`, and a later block retracts the claim. | substantive | `claude-iso.sh:85-91, 104-109` (contrast 96-102) | Delete both blocks. The `CLAUDE_ISO_ALLOW` comment at 92-95 already documents the mechanism. |
| F11 | The wrapper is described as stripping credential-shaped variables. The code is an allowlist that drops every other variable. | substantive | `claude-iso.sh:21-23`; `secure-agent-setup.md:245-246` | Say it drops every variable not on the passthrough list. |
| F12 | "The socket alone is harmless": an SSH agent socket lets any process that reaches it request signatures. The `ask` rule matches `git push` strings only. | substantive | `claude-iso.sh:72-73` | Remove the claim, add the socket to residual risks with its mitigation, or drop the passthrough. |
| F13 | The doc's passthrough list omits `LC_ALL`, `LC_CTYPE`, and `WAYLAND_DISPLAY`, which the script passes. | substantive | `secure-agent-setup.md:264-266`; `claude-iso.sh:61-72` | Complete the list. |
| F14 | Adopter step 2 says to copy `settings.json` into the tracker, which overwrites an existing file. | substantive | `secure-agent-setup.md:289-291` | Say to merge into an existing file. |
| F15 | "per step 5 above" refers to a step by position. | taste | `secure-agent-setup.md:174` | Name the pull-request step by its content. |
| F16 | The tool directory uses `README.md`, where sibling adapters use `tool.md`. | taste | `tools/agent-isolation/README.md` (siblings: `AGENTS.md:1129-1131`) | Rename to `tool.md`, or say why not. |
| F17 | The commit calls `settings.json` an "example". It is the live config. | taste | commit message | Reword on the next commit. |

## Not checked

This review did not run `prek` or the test suite, because `prek` would rewrite files. It made no network calls, so it did not query upstream or confirm the socat row, and it did not check the Claude Code sandbox key names against the schema. The drift script does not parse shell, TOML, or Markdown. No pass over the prose for style alone was done.
