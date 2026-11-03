I've run the checks and confirmed the main defects, so I'm now writing the report.

# Final review: `2efe27f..HEAD` (1b569a8, secure-agent setup)

**Inputs.** I had no separate task statement, so the claimed cases come from the commit message alone. I loaded `apm-authoring` and `english-developer-style`. `test-authoring` is not applicable because the change adds no tests. The drift script printed nothing: it does not parse shell, JSON, TOML or Markdown. Every item below therefore uses the no-code analogue (§2a). I did not review wording for style alone.

I ran these checks:
- `bash -n` on both scripts: syntax is fine.
- `shellcheck`: no output (it may not be installed, so I can't tell if it ran clean).
- `tomllib` load of the manifest: loads fine.
- Behavioural runs of `claude-iso.sh` against a fake `claude`:
  - With `GH_TOKEN` on the invocation line and no `CLAUDE_ISO_ALLOW`, the token is stripped.
  - With `CLAUDE_ISO_ALLOW=GH_TOKEN`, it passes through.
  - Sourced in bash, calling `claude-iso` ended the shell: `SHELL-STILL-ALIVE` was never printed.
  - Sourced in zsh, it failed with `bad substitution`.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files and about the code)

| Where | Statement | What is wrong |
|---|---|---|
| `claude-iso.sh:61-67`, header `:34-36` | "any env var that the user set on the invocation line is preserved"; header usage `GH_TOKEN="$(gh auth token)" claude-iso`, `AWS_PROFILE=read-only claude-iso` | False. I ran it: without `CLAUDE_ISO_ALLOW` the variable is dropped. The `NB:` paragraph directly below contradicts the sentence above it. |
| `claude-iso.sh:80-85` | A rambling comment ending "the conservative read: include these only when…" | It describes code that does not exist and leaves the reader unsure which rule applies. |
| `check-tool-updates.sh:163-167` | "this lexical comparison is a heuristic… plain `<` does the right thing" | The code uses `==`, not `<`. Any difference from the pin, including an older upstream, prints "upgrade candidate". |
| `pinned-versions.toml:34-35` | "The check script uses [`pinned_at`] as the minimum age…" | The script never reads `pinned_at`. |
| `secure-agent-setup.md:7`, `:69` | "Three-layer defence" | The table has layers 0-3 (four), and the commit message says four. |
| `secure-agent-setup.md:214-215`, `:236-241` | "the agent should never see it"; "Bash via oauth-draft tool, not the agent directly" | The sandbox `allowRead` for `~/.config/gh/` and `~/.config/apache-steward/` applies to every Bash command. `Read(...)` deny covers only the Read tool, so the agent can run `cat ~/.config/gh/hosts.yml` in Bash. The Gmail refresh token is reachable the same way. |
| `secure-agent-setup.md:171-173` | The scheduled agent "runs in the same secure setup" | `/schedule` creates a cloud routine. It does not run in the local `.claude/settings.json` sandbox. |
| `secure-agent-setup.md:100-102` and the `socat` row | "every version above had at least 7 days to settle"; `socat` released 2026-03-13 | The commit message's own run shows upstream `socat` 1.8.1.1 at 2026-02-12. The manifest date disagrees with what the script reports for the same version. |
| `claude-iso.sh:12-13` | "strip every credential-shaped environment variable" | It is an allowlist (`env -i`), not a credential filter. It also drops proxy and `CLAUDE_CODE_*` variables. |

## Item 2: claimed cases covered

| Claimed case | Evidence in the change |
|---|---|
| Layers 0-3 implemented | No test or run. Only the JSON-parse check was done, and the commit message says sandbox enforcement is untested. |
| `check-tool-updates.sh` runs end to end | Only the writer's pasted run; no CI job runs it. |
| `prek run --all-files` passes | Pasted claim only. |

Commands the change tells readers to run:

| Command | Promised outcome | Runs elsewhere? |
|---|---|---|
| `GH_TOKEN="$(gh auth token)" claude-iso` (script header) | Injects the token | none. I ran it and the token is dropped. |
| `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=… claude-iso` (doc) | Injects the token | I ran this form with `bash claude-iso.sh` and the token passes through. |
| `source …/claude-iso.sh` in `~/.zshrc` (doc `:252`) | Defines `claude-iso` | none. In zsh it fails with `bad substitution` at `${!var-}`. |
| `claude-iso` after sourcing | Starts a session | none. The function ends in `exec env -i …`, which replaces the interactive shell. In my bash run the shell ended after `claude` exited. |
| `/schedule weekly run …check-tool-updates.sh` | Weekly candidates | none. The script needs `curl`, which `permissions.deny` blocks (`Bash(curl *)`). It also needs `www.dest-unreach.org` over plain HTTP, which is not in `allowedDomains`. It uses GNU-only `date -d` and `tac` (macOS lacks them), so macOS users get "upstream lookup failed" for `socat`. |
| `apt-get install … bubblewrap=0.11.1-*`, `socat=1.8.1.1-*` | Installs the pinned versions | none. Distro repositories rarely carry these upstream versions. |
| Verification block (`cat ~/.aws/credentials`, `curl …`) | Denials | It is a documented check; no job runs it. |

Hunks no sentence claims: the commit message never mentions `$schema` in settings, the `Edit`-style entries in `ask`, `docker login`, `pip install --upgrade` and `uv self update` in `deny`, or the `Bash(git push --force …)` entries, which are redundant with `git push *`. All of these are small.

## Item 3: boundaries, partitions, negative control

- **Wrapper.** Two untested partitions: zsh versus bash, and sourced versus executed. The executed path works; the sourced path (the documented one) ends the shell.
- **Checker.**
  - Pinned equals upstream: only the happy path was run.
  - Upstream older than the pin: reports "upgrade candidate".
  - Upstream lookup failure: the code handles it, but no run was shown.
  - Drafts and prereleases in the GitHub releases list are not filtered, so a prerelease could become the "latest".
- **Pre-existing state.** None examined. Nothing checks a machine that already has a `.claude/settings.json` or a global `claude` install. The doc says "Pin separately from any system claude install" without saying how.
- **Limits and ordering.**
  - `denyRead ["~/"]` with `allowRead ["."]` depends on the project tree being under `~`.
  - If the project is outside `~`, that rule is moot.
  - `allowRead: "~/.local/bin/"` re-exposes every user-installed binary.
  - `deny` of `curl`/`wget` is bypassable through `python3 -c`, `git`, or `uv`, which the doc half-admits as "network egress via Bash bypasses the sandbox proxy".
- **Replaced mechanism.** None.
- **Added instructions.** `AGENTS.md:312-319` and the `README.md` paragraph each add one instruction ("Run the agent in the credential-isolation setup"). Input it does not serve: an adopter on a host without bubblewrap or socat. The agent writes: pointers to a setup it cannot satisfy. Ending clause: "where bubblewrap (Linux) or Seatbelt (macOS) is available". This is a taste-level row.

Not findings: none cited.

## Item 3a: level, placement, environment

- No in-process test exists for `claude_iso_main`, although the passthrough logic is checkable with a fake `claude` on `PATH` (what I did above). A bats or pytest test would catch the header/`ALLOW` contradiction.
- Registration: no prek hook runs `shellcheck` or `bash -n` on `tools/agent-isolation/*.sh`, so nothing checks the new scripts. The layout matches the sibling `tools/<name>/README.md` pattern.
- `README.md` in `tools/agent-isolation` hard-codes the path `/path/to/airflow-steward/`. That name is a leftover of the earlier de-Airflow sanitising commit (b73e240) and is not a framework-agnostic placeholder.

## Item 4: names by content, not by position

- `none` for ordinals in names.
- Taste: `secure-agent-setup.md` "Layers 1, 2, and 3" and "step 5 above" refer by position. Prefer naming them.

## Item 5: the failure report

- Analogue: what each rule tells the reader on failure. The Verification block names the expected output but not a hint for what to do when `cat ~/.aws/credentials` succeeds, which is the case that matters.
- The checker prints "upgrade candidate" for "older upstream", which is the wrong failure signal (see Item 1).
- `none` otherwise.

## Item 6: what the writer says it verified

The writer states a JSON-parse check, `prek`, and one run of the checker. No evidence that the rules can fail: no run showing the sandbox actually denies `~/.aws`, and none for the wrapper's passthrough or its sourced mode. The commit message admits sandbox enforcement is unverified.

## Item 7: siblings of the change

- `.claude/skills/` and `tools/gmail/oauth-draft` read `~/.config/apache-steward/`. That is covered by `allowRead`, but `claude-iso.sh` drops `XDG_CONFIG_HOME` when unset, which is fine, and keeps it when set. This is consistent.
- `tools/ponymail/tool.md:122` documents `.claude/settings.json` scopes, and nothing there mentions the new project file. Check that it does not contradict `permissions`.
- Any skill that calls `curl` (for example, tools using `lists.apache.org` or `cve.org`) now meets `Bash(curl *)` deny. I did not search all skills for `curl` use.
- Sets: the set of tools is listed in the README, the doc, the manifest and the README for the directory. All name three tools consistently. `gh api * -X *` is listed but `-XPOST` (no space) bypasses the pattern.
- Counts: "Three-layer" versus four layers (see Item 1). The documented setting list mentions `Edit`/`Write` in the table row for layer 2 ("Read/Edit/Write/Bash") but `deny` contains only `Read` and `Bash` entries.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | `exec` inside the sourced `claude-iso` function replaces the interactive shell, so the documented use ends the terminal on exit | Substantive | `claude-iso.sh:96` | Run in a subshell (`( exec env -i … )`) or drop `exec`. |
| 2 | Documented `source` into `~/.zshrc` fails (`${!var-}` bad substitution); the script is bash-only | Substantive | `claude-iso.sh:37,56-60`; `secure-agent-setup.md:252` | Use a portable indirection or state bash-only and remove `~/.zshrc`. |
| 3 | Header usage and the "invocation line" sentence promise pass-through that does not happen without `CLAUDE_ISO_ALLOW`; the trailing comment contradicts it | Substantive | `claude-iso.sh:34-36,61-67,80-85` | Replace with one accurate paragraph and fix the header examples. |
| 4 | The checker cannot run under the setup it documents: `curl` is denied, `dest-unreach.org` is not allowed and is HTTP, `/schedule` is a cloud routine | Substantive | `check-tool-updates.sh`; `secure-agent-setup.md:161-175`; `settings.json` | Reconcile (allow the host, use `git`/`gh` instead of `curl`, or drop the claim). Show a run inside the sandbox. |
| 5 | The checker uses GNU-only `date -d` and `tac`; macOS is documented as supported | Substantive | `check-tool-updates.sh:93-104` | Replace with portable code (the Python already in use), or document Linux-only. |
| 6 | Any version mismatch is reported as an upgrade candidate, including an older upstream; the comment cites a `<` that is not in the code | Substantive | `check-tool-updates.sh:163-172` | Compare versions (`sort -V`), report "pin is newer" separately, and fix the comment. |
| 7 | "Agent never sees" the gh and Gmail tokens is false: Bash can `cat` them through the `allowRead` entries | Substantive | `secure-agent-setup.md:214-215,236-241`; `settings.json` | State the real property, or drop those two `allowRead` entries and use a scoped token mechanism. |
| 8 | `socat` release date in the manifest (2026-03-13) disagrees with the pasted run (2026-02-12); the checker compares only version strings | Substantive | `pinned-versions.toml`; `secure-agent-setup.md:97` | Reconcile the date, or have the checker flag a date mismatch. |
| 9 | `pinned_at` is described as read by the script but is not | Substantive | `pinned-versions.toml:34-35` | Fix the sentence or implement the check. |
| 10 | "Three-layer defence" heading and TOC versus four layers; the table row for layer 2 lists `Edit/Write` that `deny` does not contain | Substantive | `secure-agent-setup.md:7,69,75` | Rename to four layers; list only entries that exist. |
| 11 | Distro install lines (`bubblewrap=0.11.1-*`) and `brew … claude-code@2.1.117 (when available)` are not shown to resolve | Substantive | `pinned-versions.toml`; `secure-agent-setup.md:110-125` | Run on a Debian and a Fedora host, or say the pin is best-effort. |
| 12 | The `deny` set is bypassable (`curl` alternatives, `-XPOST` spacing) and the doc leans on it as a layer | Taste | `settings.json`; `secure-agent-setup.md:218` | Say it is a speed bump, not a boundary. |
| 13 | No prek hook runs `shellcheck` or `bash -n` on the new scripts; no test for the wrapper | Taste | `.pre-commit-config.yaml` | Add a hook or a small test with a fake `claude`. |
| 14 | `/path/to/airflow-steward/` in the README and doc is a project-name leftover | Taste | `tools/agent-isolation/README.md:41,48`; `secure-agent-setup.md:253` | Use `<framework>`. |
| 15 | Unclaimed hunks (`$schema`, extra `deny`/`ask` entries) | Taste | `settings.json` | Add one sentence to the description, or drop. |

## Not checked

I did not run the suite, `prek`, or the checker against the network (none is available here), and I did not verify the upstream release dates or package versions. I did not run the sandbox enforcement either. I did not search every skill for `curl` use, and I did not review prose for style alone.
