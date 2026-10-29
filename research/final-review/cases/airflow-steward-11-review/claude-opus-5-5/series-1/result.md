I reviewed the one commit, `1b569a8` ("ci(secure-agent): add credential-isolation setup + pinned-tool manifest"). There is no separate task statement, so the claimed cases under item 2 come from the commit message alone. The change has no test suite, so I filled the form through the no-code analogues of §2a; each item names the one it used. The drift script ran and printed nothing, because none of the changed files are in a language it parses (Markdown, JSON, TOML, bash). I read the comments in the two shell scripts by hand instead.

Besides reading the diff, I ran:
- `bash -n` and `shellcheck` on both scripts: both clean.
- `claude-iso.sh` sourced in zsh and in bash, with a fake `claude` on the PATH.
- `check-tool-updates.sh` with a fake `curl` and a fake `python3` that lacks `tomllib`.
- `date -d` on this Mac.
- `uv run` inside this session's sandbox. That sandbox applies this repository's `.claude/settings.json`: reads under `~` are denied apart from the listed paths (`~/.cache/uv` among them), and writes are allowed only to `.` and `$TMPDIR`.

## Item 1: comments consistent with the code and with each other
(Analogue: every statement a changed file makes about another file or about the code beside it.)

- **`claude-iso.sh:39-41`**: the header says `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` bring the variable into the session. The code passes only the fixed list and the names in `CLAUDE_ISO_ALLOW`. I ran `GH_TOKEN=x claude-iso` and the fake `claude` received no `GH_TOKEN`. `secure-agent-setup.md:273` gives the correct form, so the two files disagree. A reader following the header gets a session without the token and no error.
- **`claude-iso.sh:85-90`**: the comment says a variable set on the invocation line is preserved and "we detect this…". The code does no such check.
- **`claude-iso.sh:104-109`**: this comment talks itself out of its own claim ("well, actually we can't reliably tell…") and ends with no code under it. It is a train of thought left in the file.
- **`check-tool-updates.sh:161-165`**: the comment says "plain `<` does the right thing". The code has no `<`; any version that differs from the pin gets "upgrade candidate". I ran a fake upstream `0.10.0` (from 2024) against pin `0.11.1`, and the script printed `upgrade candidate (aged past 7-day cooldown)`. That is a downgrade labeled as an upgrade.
- **`pinned-versions.toml:42-43`**: "The check script uses this [`pinned_at`] as the minimum age…". The script never reads `pinned_at`; `read_pinned` reads only `tools.*`. `secure-agent-setup.md:100-102` makes a similar claim about `pinned_at`.
- **`pinned-versions.toml:20-23`**: it cites "the per-package override for `uv`" as the model for its cooldown. `pyproject.toml:64-67` describes that override as an exemption from the cooldown, so it is the opposite example.
- **`pinned-versions.toml:89-90`**: it says a pin protects against "a silent autoupdate". Nothing in the change turns Claude Code's auto-updater off: no `DISABLE_AUTOUPDATER` and no `autoUpdates: false`. `claude-iso` also clears the environment, so such a variable couldn't get through anyway. The pin is overwritten at the first auto-update.
- **`pinned-versions.toml:93-95`**: `--no-save` is meaningless with `npm install -g`, and a global install never touches a project lockfile. The stated reason is false.
- **`secure-agent-setup.md:163`**: it calls `/schedule` "the framework's" slash command. `/schedule` is Claude Code's, not something this repository ships.
- **`secure-agent-setup.md:171-173`**: it says the scheduled agent "runs in the same secure setup". `/schedule` creates a cloud routine, which does not run under `claude-iso` or the host's bubblewrap/Seatbelt sandbox.
- **`secure-agent-setup.md:7` and `:69`**: the heading says "Three-layer defence", but its table lists four layers (0–3). The commit message also says four.
- **`secure-agent-setup.md:180-181`**: "The full block is below". The annotated block leaves out `$schema`. This is taste.

## Item 2: claimed cases covered
(Analogue: each case the commit message claims, against the file or run that makes it true; each documented command, against a run.)

| Claimed case | Covered by |
|---|---|
| Layer 0 strips credential-shaped variables | `claude-iso.sh`. My bash run confirms the stripping. In zsh, the macOS default shell that the doc tells readers to source it from (`secure-agent-setup.md:252`), `claude-iso` stops with `claude_iso_main:37: bad substitution`. The script uses bash-only syntax. **No coverage for zsh.** |
| Layer 0 does not harm the shell that sources it | Not claimed, but the doc's usage implies it. When sourced in bash, `claude_iso_main` runs `exec`, which replaces the user's interactive shell: `echo "SHELL CONTINUED"` after `claude-iso` never ran. When `claude` exits, the terminal closes. |
| Layers 1–3 in `.claude/settings.json` | The file parses as JSON, per the commit message. Enforcement is "not exercised", in the commit message's own words. |
| The deny/allow split: Bash can use `~/.config/gh` but the agent can't (doc `:236-241`) | **No run.** This session's effective sandbox lists `~/.config/gh` both in the read-deny list (copied from the `permissions.deny` `Read(...)` rule) and in the allow-within-deny list. Whether `gh` in Bash can read its token therefore depends on precedence that nobody has run. I did not read the credential to find out. |
| The framework's own skills work under this sandbox | **Fails.** `uv run --offline --project tools/vulnogram/generate-cve-json generate-cve-json --help` inside this sandbox gives `Failed to initialize cache at ~/.cache/uv … Operation not permitted`. `~/.cache/uv` is allowed for reads only, and uv needs to write there. `sync-security-issue` runs `uv run … generate-cve-json --attach` and `oauth-draft-create` on every run (`SKILL.md:1791`, `:1880`). |
| Write actions need confirmation (`permissions.ask`) | **Partly.** See the sibling list in item 7. In particular, the skills write `gh api -X PATCH repos/…` with the flag first (`sync-security-issue/SKILL.md:1353`, `:1390`, `:1694`, `:1701`). The pattern `gh api * -X *` needs text between `api` and ` -X`, so it does not appear to match these commands. I could not run Claude Code's matcher offline. |
| The check script reports aged upgrade candidates | It runs (verified with a fake `curl`). Three ways it gets this wrong: a downgrade is labeled an upgrade (item 1); on macOS the socat row always fails (item 3); without `tomllib` it prints no rows (item 3). |
| Pins satisfy the 7-day cooldown | The commit message's own output shows socat `UPSTREAM@ 2026-02-12`, while the manifest says `released = "2026-03-13"`. The two dates for the same version are a month apart, and nothing explains it. |

Documented commands, with the run behind each:

| Command | Run behind it | Notes |
|---|---|---|
| `apt-get install bubblewrap=0.11.1-* socat=1.8.1.1-*` (doc `:113-116`, tools `README.md`) | none | Works only on a distro that packages exactly these versions. From memory, which I could not check offline, current Debian and Ubuntu stable releases ship older bubblewrap and socat, so `=0.11.1-*` would fail with "version not found". Same for `dnf install bubblewrap-0.11.1`. |
| `npm install -g --no-save …@2.1.117` | none | Installs, but the auto-updater replaces it (item 1). |
| `source …/claude-iso.sh` from `~/.zshrc` | none | Fails, as above. |
| `bash check-tool-updates.sh` | the commit message's run (Linux, presumably) | macOS gives a different result (item 3). |
| `/schedule weekly run …` | none | Runs in the cloud, not in the local setup. |
| Verification block (`cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl`) | none | The commit message says it was not exercised. |
| `git check-ignore .claude/settings.local.json` | none | |

Every hunk belongs to a sentence of the commit message; there are no unclaimed hunks.

## Item 3: boundaries, partitions, and the negative control
(Analogue: the platforms, shells, and existing states the change claims to cover.)

- **macOS partition of the check script.** `socat_latest_aged` uses GNU `date -d`. On macOS, `date: illegal option -- d`, so every version takes `continue` and the row prints `upstream lookup failed (rate limit / network)`. The message names the wrong cause. `tac` is also absent on stock macOS; it is present here only through Homebrew. The doc treats macOS as a supported host (Seatbelt).
- **The sandbox partition of the check script.** `www.dest-unreach.org` is not in `allowedDomains`. Under the setup the doc says the scheduled agent uses, the socat lookup always fails, with the same misleading message.
- **Missing prerequisite.** With a `python3` that lacks `tomllib` (anything before 3.11), the script prints the header, the error, no rows, and the bump footer. A failure inside `<(read_pinned)` is not caught by `set -e`, so the empty table reads like a run with nothing to report.
- **Page-size boundary.** `per_page=20` with no paging. If 20 or more claude-code releases come out within the cooldown window, no aged release is found and the row prints "lookup failed". This is plausible given claude-code's release rate, but I did not check it.
- **Existing state the adopter already has.** `fix-security-issue` works in `environment.upstream_clone` (`SKILL.md:110`, `:275`), a clone outside the tracker tree and usually under `~`. `denyRead: ["~/"]` plus writes allowed only to cwd block reading and committing there. The adopter section says only "add any project-specific paths", while the framework's own skill needs this path. The same applies to `~/.cache/uv` (item 2).
- **Values users already pass.** `env -i` also drops `HTTPS_PROXY` / `NO_PROXY`, `CLAUDE_CONFIG_DIR`, and `NODE_EXTRA_CA_CERTS`. Behind a corporate proxy, `claude` cannot reach its API. None of these is a credential, and the doc does not mention that they are dropped.
- **Negative control.** The doc's verification block is the control, and it was never run.

## Item 3a: level, placement, and the environment
(Analogue: where each piece lives, and what the repository's gates run.)

`tools/agent-isolation/` sits beside the other `tools/<name>/` directories, which fits the layout. Neither script is run by any CI job or prek hook: `tests.yml` covers only two pytest projects, and `.pre-commit-config.yaml` has no shellcheck. The zsh failure, the `exec`, and the macOS `date -d` failure would all have been caught by a run. `shellcheck` is clean, because it checks bash and these are portability problems. The JSON-parse check from the commit message is not a gate either.

## Item 4: names by content, not by position
- `secure-agent-setup.md:174`: "(per step 5 above)" points from one section to a numbered step in another. Inserting a step breaks it; "per the bump-PR step" would not.
- `check-tool-updates.sh:176-186`: the footer duplicates the doc's bump steps with its own numbering, which can drift from the doc's. This is taste.

## Item 5: the failure report
(Analogue: what a failure tells the reader to look at.)

The check script's only failure text, `upstream lookup failed (rate limit / network)`, covers three other causes: GNU-only `date`, a host not on the allowlist, and the page limit. A missing `tomllib` produces a table with no rows. `claude-iso` under zsh reports `bad substitution` with no hint that bash is required.

## Item 6: what the writer says it verified
The commit message states: prek passes, the check script ran against the real upstreams, and the JSON parses. It says outright that sandbox enforcement was not exercised. Nothing shows any rule failing: no denied read, no blocked `curl`, no `ask` prompt fired. The skills the setup must not break (`uv run`, `gh`) were not run under the sandbox either. My `uv run` result in item 2 is the first such run, and it fails.

## Item 7: siblings of the change
- **The `ask` list against the write commands the skills use:**
  - `gh label create` (4 uses): missing.
  - `gh repo fork` (2): missing.
  - `gh issue reopen` (1): missing.
  - `gh api -X PATCH|DELETE …` with the flag first: probably not matched (item 2).
  - `gh api --method` and `gh api --input` (`sync-security-issue/SKILL.md:1701` uses `--input`): not covered either.
- **Pinned version strings appear in five places:** the TOML `version` field, its `install.*` and `from_source` strings, the doc's table (`:94-98`), the doc's install blocks, and the `tools/agent-isolation/README.md` usage block. The bump steps (doc `:151-155`, script footer) name the TOML fields and "the install commands in this document". They leave out the doc's table, the TOML `install.*` strings, and the tools README.
- **`AGENTS.md` lists.** The "Repo-root files" list does not name `secure-agent-setup.md`, and the "References" list (`tools/github/` … `tools/cve-org/`) does not name `tools/agent-isolation/`.
- **The count "Three-layer defence"** contradicts the four layers listed below it.

## Findings

| # | Finding | Label | File:line | Requested change |
|---|---|---|---|---|
| 1 | `uv run` fails under the dogfooded sandbox, so `generate-cve-json` and `oauth-draft-create` can't run | Substantive | `.claude/settings.json:10-12` | Make the uv cache writable (or point `UV_CACHE_DIR` into an allowed path), then run `sync-security-issue`'s `uv run` commands under the sandbox. |
| 2 | Sourcing `claude-iso` and running it `exec`s over the user's interactive shell | Substantive | `claude-iso.sh:111`, `:117` | Run `env -i …` in a subshell, or without `exec`, when the file is sourced. |
| 3 | `claude-iso` breaks under zsh, which the doc tells readers to source it from | Substantive | `claude-iso.sh:79`; doc `:252` | Make it portable, or ship it as an executable and drop the `~/.zshrc` instruction. |
| 4 | The header's injection examples don't work; the comments at 85-90 and 104-109 contradict the code | Substantive | `claude-iso.sh:39-41`, `:85-109` | Use the `CLAUDE_ISO_ALLOW` form in the header and delete the two stale comments. |
| 5 | A downgrade is reported as "upgrade candidate"; the comment describes a `<` that doesn't exist | Substantive | `check-tool-updates.sh:158-166` | Compare versions (for example with `sort -V`) and report "older than pin" separately. |
| 6 | The socat lookup always fails on macOS (`date -d`, `tac`) and inside the sandbox (host not allowed), with a misleading message | Substantive | `check-tool-updates.sh:91-104`; `settings.json` network | Make the date and `tac` calls portable, add the host or document the gap, and print the actual cause. |
| 7 | Missing `tomllib` gives an empty table with no warning | Substantive | `check-tool-updates.sh:118-126`, `:169` | Check `read_pinned`'s exit status and fail loudly. |
| 8 | `pinned_at` is said to be read by the script; it isn't | Substantive | `pinned-versions.toml:42-43`; doc `:100-102` | Rewrite both sentences, or implement the check. |
| 9 | The claude-code pin does nothing against auto-update | Substantive | `pinned-versions.toml:84-91`; `settings.json` | Disable the auto-updater (for example `"env": {"DISABLE_AUTOUPDATER": "1"}`) and show that it holds. |
| 10 | The `ask` list misses the write forms the skills use (flag-first `-X`, `--method`, `--input`, `gh label create`, `gh repo fork`, `gh issue reopen`) | Substantive | `settings.json:61-77` | Add the patterns, and run one skill command to show the prompt fires. |
| 11 | The Bash-can/agent-can't split for `~/.config/gh` has not been run, and the effective sandbox puts the path in both lists | Substantive | doc `:236-241` | Run `gh auth status` under the sandbox and show the agent's `Read` being denied. |
| 12 | `fix-security-issue`'s upstream clone outside the tree is blocked by `denyRead ~/` and cwd-only writes | Substantive | `settings.json:5-16`; doc `:282-305` | Document the per-user `allowRead`/`allowWrite` entry for `upstream_clone`, or a `settings.local.json` example. |
| 13 | The apt and dnf install commands have no run on any distro | Substantive | doc `:110-125`; `pinned-versions.toml` `install.*` | Run them on the named distros, or document the from-source path. |
| 14 | `/schedule` is called "the framework's" and is said to run in the local secure setup; it is a cloud routine | Substantive | doc `:163-175` | Correct both sentences. |
| 15 | The heading says three layers; the table lists four | Substantive | doc `:7`, `:69` | Say "Four-layer defence" and regenerate the TOC. |
| 16 | The bump steps miss three of the five places the versions are written | Substantive | doc `:151-155`; script footer | List every copy, or stop repeating versions outside the TOML. |
| 17 | socat's `released` date disagrees by a month with the upstream date in the commit message's own output | Substantive | `pinned-versions.toml:63` | Confirm which date is right and correct the other. |
| 18 | `AGENTS.md` "Repo-root files" and "References" don't name the new doc and directory | Substantive | `AGENTS.md` repo-root list; References at about line 1132 | Add both entries. |
| 19 | The `--no-save` rationale is false | Substantive | `pinned-versions.toml:93-95`; doc `:136` | Drop the flag and the sentence. |
| 20 | The `uv` override is cited as the model for a cooldown when it is an exemption from one | Substantive | `pinned-versions.toml:20-23` | Drop the reference. |
| 21 | No CI job or hook runs either script; no `shellcheck` | Substantive | `.github/workflows`, `.pre-commit-config.yaml` | Add `shellcheck`, plus a bash and zsh smoke run of `claude-iso` with a fake `claude`. |
| 22 | `env -i` drops proxy and CA variables | Taste | `claude-iso.sh:56-74` | Add them to the passthrough list, or note it in the doc. |
| 23 | `per_page=20` with no paging | Taste | `check-tool-updates.sh:67` | Page, or raise the limit. |
| 24 | The ordinal "per step 5 above" | Taste | doc `:174` | Name the step by its content. |
| 25 | The annotated block isn't "the full block" (no `$schema`) | Taste | doc `:180` | Say "annotated excerpt". |

Not checked: I did not do a style pass over the prose. Nothing was run against a real upstream (there was no network), and I did not run Claude Code's permission matcher, bubblewrap on Linux, or the distro package versions. Findings 10, 11, and 13 therefore rest on reading the files, on this session's effective sandbox configuration, and on my memory of what distros ship, not on runs of those tools.
