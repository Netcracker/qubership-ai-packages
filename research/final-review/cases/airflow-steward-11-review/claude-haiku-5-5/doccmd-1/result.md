## Final review: `2efe27f..HEAD` (one commit, `1b569a8`)

**Scope.** The range holds one commit, `1b569a8 ci(secure-agent): add credential-isolation setup + pinned-tool manifest (#11)`. It adds `.claude/settings.json`, `secure-agent-setup.md`, `tools/agent-isolation/{README.md, claude-iso.sh, check-tool-updates.sh, pinned-versions.toml}`, and edits `AGENTS.md` and `README.md`. The claimed cases come from the commit message. There is no task statement and no previous report of this form, so §4 does not apply.

**Analogues.** This change has no code members and no tests. Items 1 to 7 were answered with the §2a analogues: docs, config, and shell scripts. The skills loaded were `english-developer-style` and `test-authoring`, from the copies under the given skills directory.

**Drift script.** `comment-drift.py 2efe27f 1b569a8` ran, exited 0, and printed nothing. None of the changed files is a language it parses (shell, TOML, JSON, Markdown). Shell comments were read by hand.

**What was run.** `bash -n` and `shellcheck -x` pass on both scripts with no warnings. `.claude/settings.json` parses as JSON. `pinned-versions.toml` parses as TOML. `date -d` was run to test the GNU-only call, and `grep` was used to test `pinned_at`. `check-tool-updates.sh` was not run, because it calls `curl`. Nothing was run in a sandboxed agent session, and `prek` was not run.

---

### Item 1: comments consistent with the code and with each other

Findings:
- `claude-iso.sh:85-90` says a variable set on the invocation line "is preserved". The code (`:56-83`, `:96-102`) passes only the passthrough list and `CLAUDE_ISO_ALLOW`. `:104-109` then says "we can't reliably tell" and trails off. The two comments contradict each other and the code.
- `claude-iso.sh:73` says the `SSH_AUTH_SOCK` socket is "harmless". The doc's own threat model names lateral pivot through env vars (`secure-agent-setup.md:54-57`), and a forwarded agent socket lets processes in the session sign with the user's keys.
- `check-tool-updates.sh:163-167` says "plain `<` does the right thing". The script has no `<`; it compares with `!=` at `:160`.
- `pinned-versions.toml:42-43` says the check script "uses this [`pinned_at`] as the minimum age". The script never reads it: `read_pinned` (`:115-122`) reads only `version` and `released`. `grep` confirms this.
- `secure-agent-setup.md:69` is headed "Three-layer defence", but the table at `:71-76` has four rows (0 to 3). The commit message says four layers.
- `secure-agent-setup.md:214-215` and `:236-241` say the agent "never sees" the `~/.config/gh` and `~/.config/apache-steward` credentials, because `permissions.deny` blocks the Read tool. Bash can still read them: `allowRead` permits it and no Bash rule denies `cat` or `gh auth token`. See Item 2, substantive.
- `secure-agent-setup.md:146-147` (and `tools/agent-isolation/README.md:29`, and the script header at `check-tool-updates.sh:22`) say candidates are releases "newer than the pin". The code reports any difference (`:160-169`).

### Item 2: claimed cases covered

Claims from the commit message, one line each:
- **Four layers, each implemented.** Layer 0 exists, but the wrapper's documented usage is broken (below). Layers 1 to 3 are configuration only. The commit says sandbox enforcement is not verified until after merge. Nothing shows any layer enforcing. Layer 3 is named "confirm-on-write" in the commit message, but the `ask` list (`settings.json:62-77`) covers only `git` and `gh` writes, not Edit or Write. The doc (`:76`) describes it accurately.
- **Wrapper strips credential-shaped variables.** Holds by reading: `env -i` with the passthrough list (`claude-iso.sh:111`). No test exists.
- **Every pin is at least 7 days older than `pinned_at`.** Holds by arithmetic: 03-21, 03-13, 04-22 against 04-29. The claude-code pin is exactly 7 days, which "at least" permits. But the commit's own table gives socat `PINNED@ 2026-03-13` and `UPSTREAM@ 2026-02-12` for the same version. The script's upstream date is the tarball's `Last-Modified`, not a release date, so the `released` value has no source the script reproduces.
- **Check script is side-effect-free and prints candidates past the cutoff.** Holds by reading: it only issues `curl` GETs and reads the manifest. The "candidate" arm is never shown in the commit's table (see Item 3). The "newer" wording does not match the code (Item 1).
- **Doc walks through the `/schedule` wiring.** Present at `secure-agent-setup.md:161-175`.
- **Settings file is valid JSON.** Verified.
- **`prek` passes.** Not run here.
- **Check script runs end to end.** Not run here. Reading `:101` and `:103` shows `date -d` is GNU-only. On this darwin host `date -d` is rejected (`illegal option`), so `|| continue` skips every socat tarball and the socat row always prints `upstream lookup failed (rate limit / network)`. That is the wrong cause.
- **Threat model: GitHub and Gmail tokens are protected** (`secure-agent-setup.md:34-37`). Not held. Bash can read both credentials (`allowRead`, `settings.json:7-16`), and nothing denies `cat` or `gh auth token`. Egress is limited only by the command-name prefix `Bash(curl *)` (`settings.json:51`), which `python3 -c`, `sh -c`, or `/usr/bin/curl` pass. The allowed hosts include `github.com` and `gmail.googleapis.com`. The doc's comment that Bash "bypasses the sandbox proxy" (`:218`) is asserted, not shown. The residual-risks section does not list this path.

Commands the change tells someone to run, each with its outcome and what runs the same thing:
1. `GH_TOKEN="$(gh auth token)" claude-iso` (`claude-iso.sh:40`). Promised: the token reaches Claude. The code strips it (`:56-83`). No script or job runs this form. Fails as documented.
2. `AWS_PROFILE=read-only claude-iso` (`claude-iso.sh:41`). Same failure as 1.
3. `CLAUDE_ISO_ALLOW="GH_TOKEN" GH_TOKEN=... claude-iso` (`secure-agent-setup.md:273`). By reading, it passes the variable through. Not run.
4. `bash tools/agent-isolation/check-tool-updates.sh` (`tools/agent-isolation/README.md:47`, `secure-agent-setup.md:144`, `:166`). Promised: a status table with candidates. Not run. The socat row fails on this host (above).
5. Verification block (`secure-agent-setup.md:315-317`): `cat ~/.aws/credentials`, `echo $AWS_ACCESS_KEY_ID`, `curl https://example.com`. Each is expected to be denied or empty. Not run. No run in the repo covers them.

### Item 3: boundaries, partitions, and the negative control

- The Verification block (`secure-agent-setup.md:313-318`) lists only denial cases. No control shows the allowed paths still work (`gh auth status`, `git status`, `uv run`). It also omits the Bash-read case that would show the leak in Item 2. This is a suite that tests only the failing corner.
- The check script's "up to date" arm is shown in the commit table. The "upgrade candidate" arm, which is the reason the script exists, is never shown.
- Inherited state: `secure-agent-setup.md:289-296` tells adopters to copy `settings.json` into a tracker that may already have one. It names no merge or remedy. Substantive, minor.

### Item 3a: level, placement, and the environment

No test exists at any level. The cooldown arithmetic (`check-tool-updates.sh:53-54`, `:101-103`, `:160-169`) can be exercised offline with a fixed date and a recorded JSON or HTML fixture. That is the smallest level that observes it. Request: such a fixture, or a pasted run on a Linux host. `tomllib` (`:117`) needs Python 3.11 or later. Neither the doc nor the README states this.

### Item 4: names by content, not by position

- `secure-agent-setup.md:174` says "(per step 5 above)". Name the step by its content: "the bump procedure's last step".

### Item 5: the failure report

- `check-tool-updates.sh:152-153` says "upstream lookup failed (rate limit / network)" for every failure. For socat on a darwin host, the real cause is `date -d` and `tac`, so the reader is sent to the network. Substantive.
- `claude-iso.sh:49` and the manifest-read error at `check-tool-updates.sh:42-44` name their causes correctly. Nothing else in the form applies.

### Item 6: what the writer says it verified

Neither a red run nor a mutation verdict is stated. The commit says enforcement of the sandbox and deny rules is untested until a maintainer runs the session after merge. Request: say, in the commit or in the doc, that layers 1 to 3 have no evidence yet, or run the Verification block on Linux and paste the output.

### Item 7: siblings of the change

- `date -d` and `date -u -d` are both at `check-tool-updates.sh:101` and `:103`. Same defect, both sites.
- `gh_latest_aged` has two callers (`:137`, `:140`). Both parse `published_at` with Python. No defect found there.
- Passthrough list: `secure-agent-setup.md:264-267` omits `LC_ALL`, `LC_CTYPE`, `XDG_RUNTIME_DIR`, and `WAYLAND_DISPLAY`, and writes `XDG_*`, which is broader than the four variables the code names (`claude-iso.sh:56-74`).
- Layer 2 row (`secure-agent-setup.md:75`) says the deny list covers "Read/Edit/Write/Bash". `settings.json` has no Edit or Write entries.
- Install commands are consistent across `pinned-versions.toml`, the doc, and the tools README. The `allowedDomains` and `allowRead` lists match between the JSON and the annotated block in the doc.

---

### Findings

Labels follow §3. Substantive items are requests. Taste items are the reviewer's preference.

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Bash can read `~/.config/gh` and `~/.config/apache-steward`. Deny rules cover only the Read tool, and no rule covers `cat` or `gh auth token`. The "agent never sees it" rationale is wrong. | substantive | `secure-agent-setup.md:214-215, 236-241`; `.claude/settings.json:7-16, 44-45` | Add Bash denies for these paths and for `gh auth token`, or document the path as a residual risk and drop the "never sees" claim. |
| 2 | Bash egress is limited by command-name prefixes. `python3 -c`, `sh -c`, and `/usr/bin/curl` pass. Allowed hosts include GitHub and Google. The residual-risks section omits it. Not run. | substantive | `.claude/settings.json:51`; `secure-agent-setup.md:218, 325-348` | List it as a residual risk, or narrow the allowed hosts and the egress rules. |
| 3 | `GH_TOKEN=... claude-iso` and `AWS_PROFILE=... claude-iso` are stripped by the code. The documented usage does not work. | substantive | `tools/agent-isolation/claude-iso.sh:39-41` vs `:56-83, 96-102` | Use the `CLAUDE_ISO_ALLOW` form from `secure-agent-setup.md:273`. |
| 4 | Comments say invocation-line variables are preserved, then disclaim it. The code does not preserve them. | substantive | `claude-iso.sh:85-90, 104-109` | Delete both; state only the `CLAUDE_ISO_ALLOW` rule. |
| 5 | "The socket alone is harmless" for `SSH_AUTH_SOCK`. A forwarded agent socket lets processes sign with the user's keys, which is the pivot the threat model names. | substantive | `claude-iso.sh:73`; `secure-agent-setup.md:54-57` | Remove the variable from passthrough, or state the exposure in the comment. |
| 6 | The doc, script header, README, and commit say candidates are "newer than the pin". The code reports any difference. The comment at `:163-167` describes a `<` comparison that does not exist. | substantive | `check-tool-updates.sh:22, 160-169`; `tools/agent-isolation/README.md:29`; `secure-agent-setup.md:146-147` | Compare versions, or correct all four statements. |
| 7 | `date -d` and `tac` are GNU-only. On this darwin host the socat row always fails, and the failure message names the network. | substantive | `check-tool-updates.sh:91, 101, 103, 152-153` | Use a portable date parse, or say the script is Linux-only. Name the failing step in the message. |
| 8 | The manifest says the script uses `pinned_at` as the minimum age. The script never reads it. | substantive | `pinned-versions.toml:42-43`; `check-tool-updates.sh:115-122` | Correct the comment, or implement the check. |
| 9 | "Three-layer defence" heading over a four-row table. | substantive | `secure-agent-setup.md:7, 69, 71-76` | Rename to "Four-layer defence", and update the TOC entry. |
| 10 | Layer 2 says deny covers Edit and Write. The deny list has no such entries. | substantive | `secure-agent-setup.md:75`; `.claude/settings.json:37-61` | Correct the row, or add the rules. |
| 11 | Verification shows denials only. No allowed-path control, and no Bash-read case. | substantive | `secure-agent-setup.md:313-318` | Add controls (`gh auth status`, `git status`, `uv run`) and the Bash-read case. |
| 12 | The socat `released` date (2026-03-13) does not match the script's upstream date (2026-02-12) for the same version. The date has no reproducible source. | substantive | `pinned-versions.toml:69`; commit table | State where `released` comes from, or reconcile. |
| 13 | No red run and no mutation verdict. The sandbox layers are unverified by the commit's own statement. | substantive | commit test plan | State that layers 1 to 3 have no evidence, or run the Verification block on Linux and paste the output. |
| 14 | Cooldown logic has no offline test. Shell and the GNU/BSD split make it fragile. | substantive | `check-tool-updates.sh:53-54, 101-103, 160-169` | Add a fixture run with a fixed date, or paste a Linux run. |
| 15 | Passthrough list in the doc is incomplete and inaccurate about `XDG_*`. | substantive | `secure-agent-setup.md:264-267` vs `claude-iso.sh:56-74` | Make the doc list match the code. |
| 16 | No merge or remedy for adopters whose tracker already has a `.claude/settings.json`. | substantive | `secure-agent-setup.md:289-296` | Name the merge step, or say the file must be absent first. |
| 17 | `tomllib` needs Python 3.11 or later. This is not stated. | substantive | `check-tool-updates.sh:117` | State the Python requirement in the README. |
| 18 | "Confirm-on-write" in the commit message, where the `ask` list covers only `git` and `gh`. The doc is accurate. | taste | commit message; `.claude/settings.json:62-77` | Leave the doc as is. Note the name in the next commit. |
| 19 | "(per step 5 above)" refers to a position. | taste | `secure-agent-setup.md:174` | Name the procedure by content. |
| 20 | Example path names `airflow-steward`, which AGENTS.md says is being renamed. The placeholder convention would be `<framework>`. | taste | `tools/agent-isolation/README.md:40`; `secure-agent-setup.md:253` | Use `<framework>` or a neutral path. |

---

**Not checked:** I did not run `check-tool-updates.sh` (it needs network and `curl`), the Verification commands (they need a live agent session with bubblewrap or Seatbelt), `prek`, or any `gh` call. I did not do a style pass over the prose beyond wording that changes a claim, which is the scope the skill sets.
