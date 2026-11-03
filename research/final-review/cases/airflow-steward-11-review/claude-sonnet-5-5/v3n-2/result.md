I've finished running the checks (shell syntax, shellcheck, the wrapper under bash and zsh, the docs against the files they cite) and am now writing the report.

# Final review: `2efe27f..HEAD` (1b569a8, "ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)")

**Inputs.** There is no task statement, so the claimed cases come from the commit message alone, and item 2 is answered from that. The change has two parts:
- Code: two shell scripts, `check-tool-updates.sh` and `claude-iso.sh`.
- No-code: `.claude/settings.json`, a TOML manifest, `secure-agent-setup.md`, `tools/agent-isolation/README.md`, and short additions to `AGENTS.md` and `README.md`. `AGENTS.md` is an instruction file, so §2a applies to it.

**Skills loaded.** `english-developer-style` and `apm-authoring` (for the `AGENTS.md` hunk). `test-authoring` was not loaded, because the change has no tests. Beyond wording that makes a sentence read wrongly, this was not a style pass.

**Drift script.** It was run and printed nothing, since it does not parse shell scripts, Markdown, JSON or TOML. Under §2a this is expected, and the form is filled through the analogues.

## Item 1: comments consistent with the code and with each other

(Analogue: statements one file makes about another, counts, and claims about the code.)

| # | Finding | Evidence |
|---|---|---|
| 1a | The `claude-iso.sh` comment says an env var set on the invocation line "is preserved", and the header shows `GH_TOKEN=... claude-iso`. The code keeps a variable only if it is in `CLAUDE_ISO_ALLOW` or the passthrough list. I ran `GH_TOKEN=x claude-iso` and it was stripped. | `claude-iso.sh` lines 28-30 (header), the block starting at "Explicit single-credential injection", and the trailing "Common one-off injections" block. |
| 1b | The doc is titled "Three-layer defence" but its table lists layers 0-3. The commit message says four. | `secure-agent-setup.md:69-76`, and the TOC entry. |
| 1c | In `check-tool-updates.sh`, the comment says a lexical `<` comparison "does the right thing". The code uses `==`, so an upstream version older than the pin is also labeled "upgrade candidate". | `check-tool-updates.sh`, the "this lexical comparison" comment above the `status=` line. |
| 1d | Both `README.md`s call `claude-iso` a "Shell function". The file is a script that also works when executed. This is minor. | `tools/agent-isolation/README.md` Files table. |
| 1e | The doc says "The full block is below, annotated", but the block omits `$schema` and the `git push --force*` ask entries that `settings.json` has. | `secure-agent-setup.md:183-233` against `.claude/settings.json`. |
| 1f | The `pinned-versions.toml` header says to bump `pinned_at` "to today". The check script's docs and the `secure-agent-setup.md` bump steps repeat the procedure in three places (script heredoc, doc, TOML header). That is a drift risk, not a current contradiction, so I have not filed it. | |

Checked and consistent:
- The anchor `#prerequisites-for-running-the-agent-skills` exists at `README.md:136`.
- `exclude-newer` and the Dependabot 7-day cooldown exist as cited.
- The manifest pins match the doc table and the install commands.

## Item 2: claimed cases covered

Claims from the commit message, with the detection or run that covers each:

| Claim | Covered by |
|---|---|
| Layer 0 strips credential env vars, with a tiny passthrough list | The doc's Verification block (`echo $AWS_ACCESS_KEY_ID`). I ran it: it strips correctly in executed mode, but the sourced mode is broken (item 7). |
| Layers 1-3 deny reads, deny tools, and ask on writes | The Verification block has three commands. None exercises `permissions.ask`, and none exercises the "agent's Read tool is denied but Bash is allowed" split for `~/.config/gh`. The commit message admits sandbox enforcement was not exercised. |
| The check script prints a status table with a 7-day cutoff | Only the commit message's pasted run. No fixture or offline mode. |
| Each pin was released at least 7 days before `pinned_at` | Nothing machine-checks it. The commit's pasted table shows socat 1.8.1.1 at 2026-03-13 in the manifest and 2026-02-12 upstream, with the same version on both lines. One of the two dates is wrong. |
| `settings.json` parses as JSON | Claimed in the commit message. I did not re-run it, and `python3 -c 'json.load'` is the stated check. |

Commands the change tells someone to run, and what runs the same form:

| Command | Runs elsewhere |
|---|---|
| `bash tools/agent-isolation/check-tool-updates.sh` | `none`. It uses `date -d` and `tac`; `date -d` fails on macOS (I ran `date -d` here: `illegal option -- d`), and the doc advertises macOS support. Its socat lookup also fetches `www.dest-unreach.org`, which is not in `sandbox.network.allowedDomains`. The doc says the scheduled run happens inside this sandbox, so socat would print "upstream lookup failed". |
| `source .../claude-iso.sh` from `~/.zshrc`, then `claude-iso` | `none`. I ran it under zsh: `claude_iso_main:37: bad substitution`, from `${!var-}`. The doc names both `~/.bashrc` and `~/.zshrc`. |
| `source .../claude-iso.sh` from a bashrc, then `claude-iso` (twice in one shell) | `none`. I ran it under bash: the second `claude-iso` never ran, because the function ends in `exec` and replaces the user's interactive shell. Quitting `claude` would close the terminal. |
| `sudo apt-get install ... bubblewrap=0.11.1-* socat=1.8.1.1-*` and the `dnf` form | `none`. Whether those versions exist in any distro repository was not checked, and no network is available. |
| `/schedule weekly run tools/agent-isolation/check-tool-updates.sh ...` | `none`. Same sandbox-network and `date -d` issues as the first row. |

Diff hunks against the commit message: every hunk is claimed. The `AGENTS.md` and `README.md` edits are named in the message.

## Item 3: boundaries, partitions, and the negative control

- **Negative control.** Missing for the wrapper. No run shows that a credential variable set in the parent shell is absent in the child, and the `CLAUDE_ISO_ALLOW` arm (variable kept only when listed) is likewise unrun in the change. I ran both arms in executed mode. Executed mode is fine. The sourced mode is the problem (item 7).
- **Pre-existing state.** An adopter who already has a `.claude/settings.json` is told to "copy" the framework's file over it, with no merge guidance. The doc says nothing about existing `permissions` or `sandbox` keys, and nothing about whether the machine has Claude Code installed at another version. Substantive, taste-adjacent.
- **Faults on the replaced mechanism.** Not applicable: nothing is replaced.
- **Limits.** None set or moved.
- **Values users already pass.** `claude-iso` drops `ANTHROPIC_API_KEY`. The doc does not say how an API-key user authenticates (only the OAuth flow gets `DISPLAY`). I did not check this: Claude Code may store credentials under `~/.claude`, which `denyRead ~/` hides from Bash subprocesses. This is unverified, and I list it under what the review did not check.
- **Partitions the pin policy claims.** "At least 7 days": no test covers equality or the one-day-short boundary (`<=` against `cooldown_cutoff_epoch`). The 2.1.117 pin is exactly 7 days before `pinned_at`, which is fine.

Added instructions (§2a table) for the `AGENTS.md` hunk, which adds one: "Run the agent in the credential-isolation setup".

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| `AGENTS.md` "Run the agent in the credential-isolation setup" (new paragraph under *Local setup*) | A docs-only edit of a canned-response typo by a contributor with no pre-disclosure content | Tells the user to adopt the sandbox setup and points at `secure-agent-setup.md` | "only where the session reads `<tracker>` or `<security-list>` content" |

Not findings: none beyond the single row above. The `README.md` hunk is documentation for humans and adds no instruction for an agent.

## Item 3a: level, placement, and the environment

- **Smallest level.** The wrapper's environment filtering can be observed in one process with a stub `claude` on `PATH`; I did exactly that. A bats-style test or a pytest-subprocess test would catch findings 7a and 7b. None exists. The repo's CI (`tests.yml`, `pre-commit.yml`) does not run `shellcheck` or `bash -n` on the new scripts. Local `shellcheck` is clean.
- **Placement.** Both scripts sit with their manifest in `tools/agent-isolation/`, matching the sibling `tools/` layout.
- **Gate.** `prek`/`doctoc` produced the TOC for the two new `.md` files, per the commit message. I did not re-run the gate.

## Item 4: names by content, not by position

`none`. I read headings, cross-references and case names: `Layer 0`...`Layer 3` are ordinals, but they are the layers' own names throughout both documents and the commit message, and each is also named by mechanism in the table. The step list "(per step 5 above)" in `secure-agent-setup.md:174` is a positional reference that goes stale on insertion. Taste.

## Item 5: the failure report

The doc's Verification block names the expected result for each command but not what a failure looks like. If `cat ~/.aws/credentials` succeeds, the reader is not told what to conclude, and the third command (`curl`) is denied by `permissions.deny` before the sandbox is reached, so it does not test the network allowlist. It tests a weaker property than the one claimed ("the sandbox's network proxy"). Substantive. The request is a check that goes through an allowed tool to a non-allowlisted host, such as `python3 -c 'urllib.request.urlopen("https://example.com")'`.

## Item 6: what the writer says it verified

The commit message states a green `prek` run, one end-to-end run of the check script, and a JSON parse of `settings.json`. It states no run of `claude-iso.sh` at all, and it says outright that sandbox enforcement was not exercised. There is no red/green evidence for any rule. I did not run the suite and did not apply the settings.

## Item 7: siblings of the change

- **7a (sourced mode kills the shell).** `claude-iso()` calls `exec`. Verified as described in item 2. Request: run `claude_iso_main` in a subshell when sourced (`( claude_iso_main "$@" )`) and keep `exec` for the executed path.
- **7b (zsh).** The doc tells zsh users to source it. `${!var-}` and `local -a ... =(...)` are bash-only. Verified: `bad substitution`. Request: either drop zsh from the doc or use `${(P)var}` under a zsh branch.
- **7c (macOS).** The doc scopes socat and bubblewrap away from macOS, which signals macOS is a supported host. `check-tool-updates.sh` uses GNU `date -d`, and `tac` is not on stock macOS (it is present here only through Homebrew). Request: say Linux or GNU coreutils is required, or use `python3` for the date handling.
- **7d (allowlist).** `www.dest-unreach.org` is read by the script and absent from `allowedDomains`, and the same fetch uses plain `http://`. Also, the settings file allows `Read(~/.config/gh/**)` for Bash while `check-tool-updates.sh` needs nothing from there. Request: add the host to the allowlist, or note that the socat row needs an unsandboxed run.
- **7e (set membership).** A new "Layer" or tool was added to a set: `bubblewrap`, `socat`, `claude-code` appear in the doc table, the TOML, and `tools/agent-isolation/README.md`. They are consistent. The `AGENTS.md` "References" and "Reusable skills" lists name `tools/gmail/`, `tools/vulnogram/` and others but not `tools/agent-isolation/`, so the list that enumerates tool adapters omits the new directory. Substantive, small.
- **7f (old size).** Searched "three" and "both" in prose: only the "Three-layer defence" heading (1b) counts the set as before the table's fourth row.
- **7g (twin paths).** The "Verification" and "Adopter setup" blocks only name Linux and macOS. Windows/WSL is not mentioned either way; I treated that as out of scope.

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| Sourced `claude-iso` replaces the interactive shell via `exec` | Substantive | `claude-iso.sh`, final `claude-iso() { claude_iso_main "$@"; }` and `exec env -i` | Run in a subshell when sourced |
| Documented zsh use fails with `bad substitution` | Substantive | `claude-iso.sh:37`; `secure-agent-setup.md:252` ("~/.bashrc or ~/.zshrc") | Make the script zsh-safe, or drop zsh from the doc |
| Comment and header say an invocation-line variable is preserved; code strips it unless listed in `CLAUDE_ISO_ALLOW` | Substantive | `claude-iso.sh` header and the "Explicit single-credential injection" and "Common one-off injections" comment blocks | Delete the false comments; keep the `CLAUDE_ISO_ALLOW` contract |
| `check-tool-updates.sh` uses `date -d` and `tac`; macOS is advertised | Substantive | `check-tool-updates.sh` `socat_latest_aged` | Declare GNU-only, or port |
| socat lookup host is not in `allowedDomains`; the scheduled-run recipe would report "upstream lookup failed" | Substantive | `.claude/settings.json` network list; `secure-agent-setup.md:161-175` | Add the host, or document the exception |
| No test or CI step for either script; the negative control for env stripping is absent | Substantive | `tools/agent-isolation/` | A stub-`claude` test for both arms, plus `shellcheck` in CI |
| Verification step 3 tests `permissions.deny`, not the network allowlist; no failure reading is given | Substantive | `secure-agent-setup.md:312-323` | Add an allowlist test and say what a failure looks like |
| "Three-layer" heading against four layers | Substantive | `secure-agent-setup.md:69` and TOC | Rename to four layers |
| Comment says `<` comparison, code uses `==` | Substantive | `check-tool-updates.sh` status block | Fix the comment, or compare semver |
| Doc's "full block" omits `$schema` and two ask entries | Substantive | `secure-agent-setup.md:183-233` | Sync, or say "abridged" |
| socat `released` date disagrees between manifest and upstream in the commit's own output | Substantive | `pinned-versions.toml` socat entry | Check the date and correct one side |
| `tools/agent-isolation/` is absent from `AGENTS.md`'s tool-adapter reference list | Substantive | `AGENTS.md` References section | Add a line |
| "Copy" over an existing `.claude/settings.json` has no merge guidance | Taste | `secure-agent-setup.md:289-291` | Say to merge, not overwrite |
| "per step 5 above" is a positional reference | Taste | `secure-agent-setup.md:174` | Name the step by content ("open the bump as its own PR") |

**Not checked.** I did not run the check script against upstream (no network). I did not verify that the `sandbox.filesystem.allowRead` and `denyRead` keys, or the `Read(//**/...)` pattern, mean what the doc says in Claude Code 2.1.117, or that those apt and dnf versions exist. I did not run the test suite or `prek`, and I did not do a pass over the prose for style alone.
