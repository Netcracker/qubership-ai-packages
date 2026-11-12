Status: I've finished reading the diff and running the checks, so this is the final report. The task statement was not handed over, so I took the claimed cases from the commit message (`1b569a8`). The drift script was not run: the change has no members or doc comments for it to parse (shell scripts, JSON, TOML and Markdown only), so the §2a analogues apply. I loaded `apm-authoring` and `english-developer-style` for `AGENTS.md`, the docs and the scripts. `test-authoring` has no tests to apply to here. `bash -n` passes and `shellcheck` reports nothing. I ran `claude-iso.sh` under bash and zsh with a stub `claude`.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement one file makes about another file or about its own code.

- **Substantive.** `secure-agent-setup.md:69` is headed "Three-layer defence", but its table lists four layers (0–3) and the commit message says four. The TOC entry repeats the wrong count.
- **Substantive.** `claude-iso.sh:39-41` documents `GH_TOKEN="$(gh auth token)" claude-iso` and `AWS_PROFILE=read-only claude-iso` as injection. The code drops both, because only the passthrough list and `CLAUDE_ISO_ALLOW` are kept (lines 56-102). The doc (`:269-280`) says the variable must be named in `CLAUDE_ISO_ALLOW`. The comments at `claude-iso.sh:85-90` ("we detect this by comparing the inherited env…") and `:104-109` ("well, actually we can't reliably tell") describe logic that does not exist. Request: fix the usage lines to include `CLAUDE_ISO_ALLOW`, and delete both comments.
- **Substantive.** `secure-agent-setup.md:264-266` lists the passthrough as "`XDG_*`" and omits `LC_ALL`, `LC_CTYPE` and `WAYLAND_DISPLAY`. The code passes only four XDG names, and the doc's list lacks the other three.
- **Substantive.** `check-tool-updates.sh:163-167` says "plain `<` does the right thing". The code uses `==` and `!=`, so any difference is labelled "upgrade candidate".
- **Substantive.** `pinned-versions.toml:36-37` says "The check script uses [`pinned_at`] as the minimum age". The script never reads `pinned_at`.
- **Substantive.** `secure-agent-setup.md:179-181` says "The full block is below". It omits `$schema` and the `git push --force*` ask entries that `.claude/settings.json:57-58` has. This is minor, but "full" is false.
- **Substantive.** `secure-agent-setup.md:214-215, 236-241` says the agent "should never see" the gh and OAuth credentials, because `Read()` is denied while `sandbox.allowRead` permits them. `Read()` deny rules do not cover `Bash(cat ~/.config/gh/hosts.yml)`, which `allowRead` lets through. The claim is stronger than the config.
- **Substantive.** `secure-agent-setup.md:218` says "network egress via Bash bypasses the sandbox proxy". This contradicts the doc's own Layer 1 and the network allowlist.
- **Substantive.** `secure-agent-setup.md:163-175` says `/schedule` is "the framework's" command and that the scheduled agent "runs in the same secure setup". `/schedule` is a Claude Code feature that creates cloud routines, and a cloud routine does not run under this local `.claude/settings.json` sandbox. The claim is unsupported.
- **Taste.** `claude-iso.sh:73` says the socket is "harmless", and `git push` is covered only by the `ask` rule for the agent's own Bash command, so `ssh`/`ssh-add` through the agent socket is not gated. Say so under Residual risks.
- **Taste.** The `pinned-versions.toml:98-100` comment about `--no-save` and "the local lockfile" does nothing for a `-g` install.

## Item 2: claimed cases covered
The cases the commit message claims are listed with the check that covers each. Commands the change tells someone to run are listed with the script or job that runs the same form.

| Claimed case or command | Covered by |
| --- | --- |
| Layer 0 strips credentials | No test. Under bash I ran `GH_TOKEN=x AWS_PROFILE=y CLAUDE_ISO_ALLOW=GH_TOKEN claude-iso` and only `GH_TOKEN` survived, as claimed. |
| Layers 1–3 enforce | The "Verification" block (`:312-318`) is documentation only. No CI job runs it, and the commit message admits sandbox enforcement is untested. |
| `check-tool-updates.sh` prints the status table | `none` in CI. It was run once by hand outside the sandbox, which is not the configuration it is documented for. |
| `source claude-iso.sh` from `~/.zshrc` (`:249-253`) | `none`. Under zsh, `claude-iso` fails with `claude_iso_main:37: bad substitution` (`${!var-}` is bash-only). The doc offers zsh as a supported rc file. This is a substantive finding. |
| `check-tool-updates.sh` inside the secured setup (`:166-175`) | `none`. It `curl`s `www.dest-unreach.org` over http, which is not in `allowedDomains` (`.claude/settings.json:19-32`). The socat row will always read "upstream lookup failed". On macOS the script also uses `tac` and `date -d`, which is GNU-only, so it fails the same way. It needs Python 3.11+ for `tomllib`, which the doc does not state. This is a substantive finding. |
| `apt-get install bubblewrap=0.11.1-*` and `dnf install bubblewrap-0.11.1` | `none`. Whether distro repositories carry that exact version is not checked. The doc gives no fallback beyond a `from_source` field in the TOML. This is a substantive finding: run it per distro or state the dependency. |
| `npm install -g --no-save @anthropic-ai/claude-code@2.1.117` ("pinned") | `none`. Nothing disables Claude Code's auto-update, so the pin the TOML calls load-bearing (`:84-92`) is not enforced. This is a substantive finding. |
| Pinned dates satisfy the 7-day cooldown | The commit's own table shows socat 1.8.1.1 as `2026-03-13` in the manifest and `2026-02-12` upstream. The two sources disagree about the same version. This is a substantive finding: the manifest's `released` date is unverified against the script's source. |

Claims read the other way: `.claude/settings.json` applies to every contributor who runs Claude Code in this repo (denyRead of `~/`, a network allowlist, `ask` rules). Only the commit message's "framework dogfoods" sentence claims it, and no hunk exceeds the claim otherwise.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the partitions are bash/zsh, Linux/macOS, and sandbox on/off; the negative control is the statement of what still works.

- **Substantive.** There is no negative control. The verification block only shows denials. It does not show that the permitted paths work (`gh auth status`, `uv`, `git commit` with `denyRead ~/`), and it does not check writes. `allowRead` grants read only, yet uv's cache and tool venvs are written under `~/.cache/uv`. Request: run the allowed operations inside the sandbox.
- **Substantive.** The pre-existing state is not considered. Users who authenticate Claude Code with `ANTHROPIC_API_KEY` (which the wrapper strips and the doc names as a stripped variable) will find `claude-iso` unable to authenticate. The injection example covers only `GH_TOKEN`.
- **Substantive.** Neither partition has a run: the zsh and macOS runs above fail (Item 2).
- **Taste.** The `ask` list contains the redundant `git push --force*` entries.

Added instructions (`AGENTS.md:312`, "Run the agent in the credential-isolation setup"; `README.md:158-168`): 2, no rows.
Not findings: `AGENTS.md:312-319`, `README.md:158-168`. Both scope the instruction to the skills' pre-disclosure content.

## Item 3a: level, placement, and the environment
- The layout matches the sibling `tools/` directories, and the TOC markers are present.
- **Substantive.** The repository's pre-commit gate was not run by me. The commit message says `prek run --all-files` passed. The shell scripts are not covered by a `shellcheck` hook (not found in the commit), so a local `shellcheck` run is the substitute and it is clean.
- **Taste.** `secure-agent-setup.md:253`, `tools/agent-isolation/README.md:40,47` and `claude-iso.sh` hard-code `airflow-steward`. The repository is mid-rename to Steward (`NOTICE`, `README.md:66`).

## Item 4: names by content, not by position
None. I checked the headings and cross-references (the "step 5 above" reference at `secure-agent-setup.md:174` is a numbered step, which is fine). Minor: "Three-layer" is a count, covered in Item 1.

## Item 5: the failure report
Analogue used: what a rule tells the reader to look at when it fails.
- **Substantive.** The verification block gives three commands but not how to tell a denial from a real leak when one fails. `echo $AWS_ACCESS_KEY_ID` returns empty if the variable was never set, so it proves nothing unless the variable is exported first. Request: say to export a dummy value before running it.
- The check script's `upstream lookup failed (rate limit / network)` is one message for several causes, including the macOS and sandbox failures above.

## Item 6: what the writer says it verified
The commit message states a table from one run of `check-tool-updates.sh`, a JSON parse of `settings.json`, and the `prek` hooks. It states no run of the sandbox, `claude-iso` or the install commands, and it admits so for the sandbox. I did not run anything to supply the missing evidence.

## Item 7: siblings of the change
- The set "pinned tools" (`bubblewrap`, `socat`, `claude-code`) is listed consistently across the doc, the TOML and `tools/agent-isolation/README.md`.
- `README.md` and `AGENTS.md` link to the doc, and the doc's anchors exist (`README.md:136`, `AGENTS.md` "Local setup").
- **Substantive.** `CONTRIBUTING.md` and `.claude/skills/*` were not updated, and `.claude/settings.json` now constrains skill runs. For example, the allowlist omits `www.cve.org`'s API host and `api.github.com` is present, but I did not read every skill for hosts it uses. I read the allowlist against `tools/vulnogram` and `tools/gmail` only by name. Treat this as not fully checked.
- The 7-day cooldown wording is consistent with `pyproject.toml:65` and `.github/dependabot.yml`. The `uv = "1 day"` override is mentioned in the TOML header.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "Three-layer" heading over a four-layer table | Substantive | `secure-agent-setup.md:69` | 1 |
| Usage lines claim injection that `CLAUDE_ISO_ALLOW` is needed for; two comments describe nonexistent logic | Substantive | `claude-iso.sh:39-41, 85-90, 104-109` | 1 |
| Passthrough list in the doc differs from the code | Substantive | `secure-agent-setup.md:264`, `claude-iso.sh:56-74` | 1 |
| Comment says `<` comparison; the code uses `!=` | Substantive | `check-tool-updates.sh:163-167` | 1 |
| TOML says the script reads `pinned_at`; it does not | Substantive | `pinned-versions.toml:36` | 1 |
| "Full block" omits `$schema` and force-push entries | Substantive | `secure-agent-setup.md:179` | 1 |
| Agent "never sees" gh/OAuth credentials, but `Bash(cat …)` can read them via `allowRead` | Substantive | `secure-agent-setup.md:236`, `.claude/settings.json:5-13` | 1 |
| "Bash bypasses the sandbox proxy" contradicts Layer 1 | Substantive | `secure-agent-setup.md:218` | 1 |
| `/schedule` is described as the framework's and as running in the same sandbox | Substantive | `secure-agent-setup.md:163-175` | 1 |
| `SSH_AUTH_SOCK` called harmless; not in Residual risks | Taste | `claude-iso.sh:73` | 1 |
| `--no-save` comment misleading for `-g` | Taste | `pinned-versions.toml:98` | 1 |
| `claude-iso.sh` fails under zsh (`bad substitution`) | Substantive | `claude-iso.sh:79,98`; `secure-agent-setup.md:249` | 2 |
| Check script's host is outside `allowedDomains`; GNU-only `tac`/`date -d`; Python 3.11+ unstated | Substantive | `check-tool-updates.sh:90-103`, `.claude/settings.json:19` | 2 |
| Pinned apt/dnf versions not verified to exist | Substantive | `secure-agent-setup.md:112-125` | 2 |
| Claude Code pin not enforced against auto-update | Substantive | `pinned-versions.toml:84-92` | 2 |
| socat release date disagrees with the script's source | Substantive | `pinned-versions.toml:70`, commit table | 2 |
| No negative control; uv cache needs write, not just read | Substantive | `secure-agent-setup.md:307-323` | 3 |
| `ANTHROPIC_API_KEY` auth breaks under the wrapper | Substantive | `secure-agent-setup.md:73,269-277` | 3 |
| Hard-coded `airflow-steward` path | Taste | `secure-agent-setup.md:253` | 3a |
| Verification block cannot tell "denied" from "never set" | Substantive | `secure-agent-setup.md:315-318` | 5 |
| Skills' hosts not read against the allowlist | Substantive | `.claude/settings.json:19-32` | 7 |

Checks not done: the sandbox itself (no bubblewrap here), the install commands, and any network lookup. Those findings rest on reading the code and on local bash/zsh runs.
