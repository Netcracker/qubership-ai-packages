I've finished running the checks and am writing the report now. These are the confirmed results:

- The `claude-iso` wrapper drops variables set only on the invocation line.
- Sourcing the wrapper and running `claude-iso` replaces the calling shell.
- Sourcing the wrapper in zsh fails with "bad substitution".

# Final review: `2efe27f..HEAD` (1b569a8, secure-agent setup)

**Inputs.** There is no separate task statement. The claimed cases come from the commit message and the docs themselves, and I answered item 2 from those alone. This change is docs, JSON/TOML config and three shell scripts, so I read the no-code analogues of §2a for the docs and config and the literal form for the scripts.

I did not load `test-authoring` or `javadoc-authoring`, because the change has no test code. I applied `apm-authoring` to the `AGENTS.md` hunk only, and wording enters only where a sentence reads wrongly.

`comment-drift.py` printed nothing. It does not parse new shell, Markdown, JSON or TOML files, so I read the comments by hand. `bash -n` and `shellcheck` are clean. `settings.json` and the TOML parse.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement a file makes about another file, a count, or a command's behavior.

1. **`claude-iso.sh:73-80`: the comment contradicts the code.**
   - The comment says "any env var that the user set on the invocation line of `claude-iso` is preserved".
   - The code keeps only `passthrough` plus names listed in `CLAUDE_ISO_ALLOW`.
   - I ran it with `GH_TOKEN=x AWS_PROFILE=y` on the line: neither reached the child.
   - The header usage (`claude-iso.sh:39-40`) says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` work. They do not.
   - Lines 96-102 then say the opposite ("include these only when the user named them in CLAUDE_ISO_ALLOW"). That block reads as unfinished thinking.
   - Request: rewrite the header and the comments to the real contract, `CLAUDE_ISO_ALLOW="X" X=… claude-iso`. `secure-agent-setup.md:273` already documents that form.
2. **`check-tool-updates.sh:164-168`: stale comment.** It says "lexical comparison … plain `<`", but the code tests only `==`.
   - Any difference, including an upstream older than the pin, is reported as "upgrade candidate". Rewrite the comment, or compare for real.
3. **Pinned date versus upstream date.**
   - The commit message's own output shows socat 1.8.1.1 with `PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12`, for the same version.
   - The manifest claims "released 2026-03-13", and the doc table (`secure-agent-setup.md:97`) repeats it.
   - The script never compares the dates and the commit does not explain the gap.
   - Request: correct the date, or say why it differs.
4. **Layer count.**
   - The doc heading is "Three-layer defence" (`secure-agent-setup.md:69`, and the TOC) over a table with layers 0-3, which is four.
   - The commit message says "four layers".
   - `secure-agent-setup.md:78` says "Layers 1, 2, and 3" share the settings file.
   - Request: rename the heading to four layers.
5. **`AGENTS.md:312-319` and `README.md:158-169` say "7-day upstream cooldown" for the tools.** `secure-agent-setup.md:127-130` admits that macOS Homebrew is unpinned. Taste, not a request.
6. **`secure-agent-setup.md:98`** says to pin claude-code "separately from any system claude install", but the wrapper uses `command -v claude`, which is whichever claude is first on `PATH`. Mixed with item 1 of §7, so no separate request.
7. **`secure-agent-setup.md:315-317`: the verification comments disagree with their commands.**
   - `cat ~/.aws/credentials` is annotated "permission denied (sandbox)", which is plausible.
   - `curl https://example.com` is annotated "blocked by permissions.deny", but that rule is a Claude permission and not a sandbox denial.
   - Neither says what a reader should see, only the mechanism.
   - Taste.
8. No `now`/`no longer`/`used to` narration found.

## Item 2: claimed cases covered

Claimed cases and commands, each with a covering script or CI job:

| Claim or command | Covered by | Outcome |
|---|---|---|
| `bash check-tool-updates.sh` prints the table (commit message, `README` of the tool) | None in CI. The writer ran it once, with network, on a GNU system. | See below. |
| Weekly `/schedule … check-tool-updates.sh` (`secure-agent-setup.md:167`) | None. The scheduled agent runs under `permissions.deny Bash(curl *)`. | See below. |
| `claude-iso` with `GH_TOKEN=… claude-iso` (script header) | None | False (item 1). |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (doc) | None. I ran it and it works. | Holds. |
| `source claude-iso.sh` from `~/.zshrc` (`secure-agent-setup.md:250-253`, tool `README`) | None | Substantive, see below. |
| `claude-iso`, once sourced, starts a session (doc) | None | Substantive, see below. |
| `sudo apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*`, `dnf install bubblewrap-0.11.1` | None | Not verified. See the finding on versions on current distros. |
| `npm install -g --no-save …` | None | `--no-save` is meaningless with `-g`. Taste. |
| `cat ~/.aws/credentials`, `curl`, `echo $AWS_ACCESS_KEY_ID` verification block | None, and the commit message admits the sandbox is untested | Acknowledged, not a gap I can close. |
| `prek run --all-files` passes | The commit message states it | Not re-run. |

Substantive findings from the command rows, each from a run:

- **`exec` inside a sourced function replaces the user's shell.** With `bash -c 'source claude-iso.sh; claude-iso; echo ALIVE'`, `ALIVE` never printed. When the user quits claude, the terminal closes, and the doc recommends exactly this usage. Request: run the command in a subshell, `( exec env -i … )`, or drop the `exec` when sourced.
- **zsh is the macOS default, and the doc names `~/.zshrc`.** Under `zsh -c 'source …; claude-iso'` I got `claude_iso_main:37: bad substitution`. `${!var-}` is bash-only. `BASH_SOURCE` is also bash-specific, so the sourced-detection line would misfire. Request: use bash-only wording ("bash"), or make it portable.
- **`check-tool-updates.sh` is GNU-only.**
  - `date -d` and `tac` do not exist on stock macOS.
  - socat lookups fall through `|| continue` and end as "upstream lookup failed (rate limit / network)", which is a wrong reason.
  - The doc supports macOS for everything else.
  - I did not run the script (no network). The commit's run was on one GNU host.
  - Request: say "Linux/GNU only", or use Python for the dates.
- **The scheduled weekly agent runs the script through `curl` inside the script, not through a Bash `curl` call.** The `deny Bash(curl *)` rule matches the command text, so it likely does not block the script. The sandbox allowlist, however, lacks `api.github.com`'s sibling `www.dest-unreach.org`, so the socat lookup will be refused. The script also uses `http://` for that host. Request: either add the host with a comment, or run only the GitHub entries inside the sandbox and say so.
- **Unclaimed hunks:** none beyond the scope of the commit message.

## Item 3: boundaries, partitions, negative control

Analogue used: partitions are the platforms and modes the docs claim (Linux, macOS, bash, zsh, sourced, executed, apt, dnf), and the negative control is the "does not defend" list.

- **Platforms.** Only one run is stated (GNU, network). macOS and zsh each fail for the reasons above. Evidence for macOS sandbox behaviour: none, and the commit says so.
- **Execution modes of `claude-iso.sh`.** Executed-directly worked (my run). Sourced-bash worked but kills the shell. Sourced-zsh fails.
- **Pre-existing state.** `.claude/settings.json` is new, but an adopter or maintainer will already have a `.claude/settings.json` or `settings.local.json`. The doc says "copy", with no merge advice. Taste.
- **Limits that disagree.**
  - `sandbox.filesystem.denyRead ["~/"]` with `allowRead ["."]`: the doc says cwd is the tracker. A session started in `~/code/<tracker>` works, but the doc does not say what happens when `.` lies inside `~/` and `~/` is denied. Whether the more specific allow wins is a property of Claude Code, and nothing in the change shows a run. The commit concedes that nothing was exercised. Substantive request: one run of the verification block on a real host, stated in the description.
  - `~/.config/gh/` is allowed for Bash and denied for the Read tool. The doc explains this.
- **A setting that now reaches a new consumer: `SSH_AUTH_SOCK` passthrough.** The comment calls the socket "harmless", but any process in the session can sign with the loaded keys while the socket is available. Taste, since the doc's threat model says "ssh keys" matter. The same goes for `DISPLAY`/`WAYLAND_DISPLAY`. Mention it under residual risks.
- **Replacement mechanism:** nothing replaced.
- **Negative control for the check script.** There is no run that shows the "upgrade candidate" branch or the "lookup failed" branch. The commit shows only the all-up-to-date table. Substantive: the status that matters has no evidence. Request: show one run, or a stubbed one, that gets "upgrade candidate".

## Item 3a: level, placement, environment

The behavior is scripts and config, so the smallest level is a shell test (for example a `bats` file or a pre-commit hook) for `claude-iso`: assert the child's environment under bash. None exists. Substantive and cheap, and it would have caught items 1, `exec` and zsh. Placement: the new directory matches the sibling `tools/<name>/` layout and has a `README`. `.github/workflows` has no shell lint job, so `shellcheck` on the new scripts runs nowhere, but it is clean when I ran it.

## Item 4: names by content, not by position

The doc's names are by content (Layer 0..3 are ordinals, but they are the document's chosen names, and the table gives each a content name). "Step 5 above" (`secure-agent-setup.md:174`) is a positional reference. Taste.

## Item 5: failure report

Analogue: what each rule tells the reader to look at.

- The verification block says what each command "should" produce but not how to tell a sandbox denial from a failure for another reason (missing file). Taste.
- `check-tool-updates.sh` prints "upstream lookup failed (rate limit / network)" for every failure cause, including the GNU `date` one. Covered by Item 2.

## Item 6: what the writer says it verified

The commit lists `prek` passing, one end-to-end run of the check script, and a JSON parse. It states no red run and no check that any rule can fail. It says outright that the sandbox is untested. No run of `claude-iso` is stated, and the one I did exposes three failures. Say so in the report: no evidence that the wrapper or the settings work.

## Item 7: siblings

- **Set of tools:** the three tools (bubblewrap, socat, claude-code) are listed in the manifest, the doc table, the tool `README`, the commit message, and the install snippets. The lists agree. Counted in prose: the "Three-layer" heading disagrees with four layers (item 1 of §1).
- **Placeholder drift:** `/path/to/airflow-steward/` at `secure-agent-setup.md:253`, `tools/agent-isolation/README.md:40` and `:47` names the pre-sanitization project, and the repo's recent history (b73e240) removed Airflow remnants. Substantive request: use `<framework>` per the placeholder table in `AGENTS.md`, and note the third site that spells out `.apache-steward/apache-steward/` at `:301`.
- **Referenced files that must exist:** `.github/dependabot.yml` and `pyproject.toml` exist, and the `exclude-newer` and 7-day cooldown claims hold (pyproject line 65; dependabot cooldown 7).
- `README.md#prerequisites-for-running-the-agent-skills` exists (line 136).
- **Where the secure-setup rule should be listed but is not:** the allowlist in `.claude/settings.json` has no Gmail-adjacent domain beyond `oauth2.googleapis.com`/`gmail.googleapis.com`, and no `www.dest-unreach.org` for the check script (above). The sandbox hosts do not include `www.googleapis.com`; I did not verify whether the oauth-draft tool needs it.
- **`AGENTS.md` instruction added at 312-319:** it tells the agent to "run in the credential-isolation setup" but agents cannot choose their own launch wrapper. Counted below.

### Added instructions

Instruction (`AGENTS.md:312` "Run the agent in the credential-isolation setup"):

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `AGENTS.md:312` "Run the agent in the credential-isolation setup" | an agent already running, with no control over how it was launched | a refusal, or a remark asking the user to relaunch | "only where the session has not started yet / the user asks about setup" |

Not findings: the `README.md:158` paragraph (a statement for the user, not an instruction to the agent).

The `AGENTS.md` paragraph mixes a user-facing instruction with the agent file. Under `apm-authoring` it belongs in the human docs, or in a "when the user asks about setup" form. Taste, not a request.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Header and comments say invocation-line vars are preserved; code keeps only `CLAUDE_ISO_ALLOW` (verified by run) | Substantive | `claude-iso.sh:39-40`, `:73-80`, `:96-102` | 1 |
| `exec` in the sourced function replaces the user's shell (verified by run) | Substantive | `claude-iso.sh:109` | 2 |
| zsh fails with "bad substitution", but the doc says `~/.zshrc` | Substantive | `claude-iso.sh:37`, `secure-agent-setup.md:250-253` | 2 |
| Check script is GNU-only (`date -d`, `tac`) and reports a wrong cause on macOS | Substantive | `check-tool-updates.sh:90-99` | 2 |
| `www.dest-unreach.org` not in the sandbox allowlist, so the scheduled socat check will be refused | Substantive | `.claude/settings.json:20-35`, `check-tool-updates.sh:80-82` | 2 |
| No evidence the sandbox, the `denyRead ["~/"]` + `allowRead ["."]` combination, or the verification block works | Substantive | `secure-agent-setup.md:307-323` | 3 |
| "Upgrade candidate" and "lookup failed" branches have no run | Substantive | `check-tool-updates.sh:138-170` | 3 |
| No shell test for the wrapper's environment | Substantive | `tools/agent-isolation/claude-iso.sh` | 3a |
| No evidence the wrapper or the settings can fail (no red run, no mutation) | Substantive | commit message | 6 |
| `/path/to/airflow-steward/` and `.apache-steward/apache-steward/` spelled out instead of `<framework>` | Substantive | `secure-agent-setup.md:253,301`; `tools/agent-isolation/README.md:40,47` | 7 |
| Stale "plain `<`" comment; any difference reported as a candidate | Substantive | `check-tool-updates.sh:164-168` | 1 |
| socat pin date 2026-03-13 against upstream 2026-02-12, unexplained | Substantive | `pinned-versions.toml`, `secure-agent-setup.md:97` | 1 |
| "Three-layer defence" heading over a four-layer table | Substantive | `secure-agent-setup.md:69` | 1 |
| `SSH_AUTH_SOCK` called "harmless"; missing from residual risks | Taste | `claude-iso.sh:63`, `secure-agent-setup.md:325-348` | 3 |
| `AGENTS.md` paragraph is a user instruction in an agent file | Taste | `AGENTS.md:312` | 7 |
| "7-day cooldown" wording for Homebrew-installed tools | Taste | `README.md:158-169`, `secure-agent-setup.md:127-130` | 1 |
| `--no-save` with `-g`; "step 5 above" is positional | Taste | `secure-agent-setup.md:136,174` | 4 |

Checks I could not do: network lookups (the check script's output, distro package version strings such as `bubblewrap=0.11.1-*`), the sandbox on a host with bubblewrap, and `prek`. I did not change any file or commit.
