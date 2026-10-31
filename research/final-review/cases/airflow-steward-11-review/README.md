# Case: review apache/airflow-steward#11, a script documented for macOS that calls GNU-only tools

A regression case for `final-review`, not derived from the case it was written next to
([`authz-agent-122-review`](../authz-agent-122-review/)). The input is [apache/airflow-steward#11][pr], merged as
`1b569a83`, one commit on top of `2efe27f4`. It adds a secure setup for running Claude Code: a setup page with install
steps for Debian, Fedora, and macOS, a manifest of pinned tool versions, and
`tools/agent-isolation/check-tool-updates.sh`, which the page tells the maintainer to run before every bump, and to
schedule weekly.

The script calls `tac` and `date -d "<RFC 2822 date>"`, both GNU-only. On macOS, where the page says the setup runs,
`date -d` fails; the script hides the failure behind `2>/dev/null || continue` and reports `upstream lookup failed` for
socat. The later commit [`a9dbf6a9`][fix] (#26) replaced both calls and says it was verified on macOS. No target or CI
job in `1b569a83` runs the script; the commit message pastes one run, from a host it does not name.

[pr]: https://github.com/apache/airflow-steward/pull/11
[fix]: https://github.com/apache/airflow-steward/commit/a9dbf6a9ff94dba66b9c6b2d48ca1dc288742c22

## What it exercises

Whether the reviewer treats a command the change tells someone to run as a claimed case, and asks what its outcome
depends on, here a platform the change documents and a tool the script calls in turn. It is the same class as defect 2
of `authz-agent-122-review` (`helm test --logs` on a Job hook), with no Helm and no Kubernetes in it.

## Checks

Grade by reading `result.md`; the grep only finds the candidates.

1. **GNU-only calls on a documented platform.** Pass: a substantive finding that `check-tool-updates.sh` calls
   `date -d` (or `tac`), which macOS does not provide, while the setup page covers macOS, so the documented run fails
   or reports a false lookup failure there; the request is a run on macOS or a portable call. Partial: the report says
   the documented script was never run, or not on macOS, without naming a call that breaks there. Fail: neither.

   ```bash
   grep -niE 'date -d|\btac\b|gnu|bsd|macos|darwin' result.md
   ```

## Skill parts

- `final-review`: `SKILL.md` §2 item *Claimed cases covered*, §2a
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `2efe27f4b3ddb1b2a6cf75cadd39b1e2f078bdf8` (the parent of the merge commit), and `1b569a837831da11870aa77475aa94238a85a88a` (the change). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run; `run-review-case.sh` lists them. `pr180-<n>` ran the skills at `b3cc1f2` (without the rule on documented commands), `doccmd-<n>` at final-review tree `5086111` (with it, before a later edit that only split two sentences of the rule). |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/airflow-steward-11-review <model> <label> <rev>
```

The session needs no network. It runs on the machine that starts it, so on macOS it can observe `date -d` fail.

## Results, 2026-10-23

Two runs per model and arm.

| Model | Arm | Check 1 | Cost, USD |
| --- | --- | --- | --- |
| Opus | pr180 | pass, pass | 1.66, 1.35 |
| Opus | doccmd | pass, pass | 1.33, 1.34 |
| Haiku | pr180 | pass, pass | 0.19, 0.29 |
| Haiku | doccmd | pass, pass | 0.26, 0.32 |

The case does not tell the arms apart. Every run files the GNU-only calls as substantive, with or without the rule, and
most say they ran `date -d` on the macOS host and saw `illegal option -- d`. A defect that a local run of one call
exposes is found without a rule that asks for the run. The rule matters where the outcome depends on what a tool does
with the configuration and the reviewer cannot run it, as in `authz-agent-122-review`. This case stays as the check that
the rule costs nothing where the reviewer finds the defect anyway.

## Results of the `series` arm, 2026-10-23

`series-<n>` ran every rule in the series that adds the questions of `research/final-review/change-reach.md` and the
question on a replaced mechanism, in the wording of 2026-10-23: before two sentences were cut from the paragraphs on
values users already pass and on parallel paths, and before the question on a replaced mechanism was shortened. Opus,
two runs, as a no-regression check against the arm named below.

| Check | `series-1` | `series-2` | `doccmd` |
| --- | --- | --- | --- |
| 1 | pass | pass | pass, pass |

Unchanged. The new questions add real findings (the `ask` list misses forms the skills use, a root-file list misses
`secure-agent-setup.md`, "Three-layer defence" now describes four layers) and leave check 1 where it was. The reports
grow to 24 and 25 findings, in 19 and 17 turns against 13; cost 1.87 and 1.26 USD against 1.33 and 1.34.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`. Its §2a takes each added
instruction through three steps (choose an input that meets every condition the instruction states, label it before
writing a row, fill the row from the text) and gives a row only to a substantive input that no other item files. An
input the artifact already ends goes to a `Not findings:` line of line numbers, and a change with no rows gets one
`Added instructions: <n>, no rows.` line instead of a table. The runner also supplied `apm-authoring`, which the
earlier `instr` runs on tree `1b1ebc3e` did not have. Graded by reading `result.md`. Opus, Haiku, and, for the first
time in this case, Sonnet, two runs each.

| Model | Run | Check 1 | Table of added instructions | Cost, USD | Words |
| --- | --- | --- | --- | --- | --- |
| Opus | `instr-1` | pass | one row, valid | 1.31 | 2646 |
| Opus | `instr-2` | pass | one row, valid | 1.44 | 2457 |
| Haiku | `instr-1` | pass | one row, valid | 0.27 | 1890 |
| Haiku | `instr-2` | pass | one row, valid | 0.28 | 2500 |
| Sonnet | `instr-1` | pass | one row, two inputs: one valid, one noise | 0.64 | 2136 |
| Sonnet | `instr-2` | partial | one row, noise | 0.52 | 2367 |

Check 1 passes in five runs. Each files the `date -d` call as substantive with the request to make it portable or to
run it on macOS:

- Opus `instr-1`: "macOS: socat lookup always fails (`date -d`, `tac`)", request "Portable date parsing (python3), or
  say the script is Linux-only".
- Opus `instr-2`: "Check script fails on macOS (`date -d`, `tac`)", request "Make the date parsing portable, or declare
  it Linux-only".
- Haiku `instr-1` F6: "`date -d` fails here ("illegal option -- d"), so the row reports "rate limit / network"",
  request "Parse `Last-Modified` portably (Python or `date -j -f`)".
- Haiku `instr-2` F2: "`tac` (line 92) and `date -d` (line 101) are GNU-only. On this macOS, `date -d` returns
  "illegal option"", request "Use `python3` for the date parsing".
- Sonnet `instr-1` finding 4: "`date -d` is GNU-only, so the check breaks on macOS", request "Portable date handling,
  or document Linux only."

Sonnet `instr-2` is partial. Finding D names the call and the false report ("GNU-only `date -d` and `tac`, so on macOS
the failure reads as "rate limit / network""), but it merges three defects into one row, and its request asks to "Add
the host or drop socat from the script, distinguish the failure causes, and correct or verify the `released` date":
neither a portable call nor a run on macOS. Item 3 says the macOS defects have "no stated acceptance" and requests
nothing either. The check defines partial as naming no call; this report names the call but drops the request that
the pass requires, so it falls between the two and is graded partial.

The input edits `AGENTS.md` (the nine-line paragraph under "Local setup" that starts "Run the agent in the credential-
isolation setup") and `README.md`, so the table fires here. I read the change in the local clone
(`/Users/vlsi/Documents/code/apache/airflow-steward`, `2efe27f..1b569a8`) to mark each row and each instruction-file
finding. The paragraph ends no condition: it gives a reason ("The skills operate against pre-disclosure CVE content")
and no clause that says when it applies, and it addresses the person who starts the session. Every run writes one row,
so none exercises the `Added instructions: <n>, no rows.` form. The Opus and Haiku runs write `Not findings: none`,
which is right for that reason; the two Sonnet lines are assessed with their rows.

Rows:

- Opus `instr-1`, `AGENTS.md:312`, input "An agent already running, asked to fix a README typo", what it writes "It
  can't relaunch itself; it may warn or stall every turn", clause "for the person launching a session; an agent already
  running does not act on it". Valid: the typo session fires the unconditional sentence and gets nothing from it, and
  the clause says whom the paragraph addresses. "Stall every turn" is a guess, not an observed output. The findings
  table points to the row ("See the table under Item 3") instead of restating it, as §2a asks.
- Opus `instr-2`, input "An agent reading `AGENTS.md` inside a session that has already started", clause "for the
  human starting a session:", or move it to `README.md`, which already carries it. Valid; the README hunk does repeat
  the instruction. The clause cell carries a second request (the move), and the findings table restates the row as a
  taste finding ("`AGENTS.md` paragraph addresses the human, not the agent").
- Haiku `instr-1`, input "a session that fixes a README typo with no CVE content", clause "only where the session reads
  pre-disclosure CVE content". Valid. The table sits under its own heading after item 7, not in the item 3 section that
  §4 names, and F22 restates it as substantive with a request that adds "and stop if it does not", which reads two
  ways.
- Haiku `instr-2`, input "a typo fix in `README.md`, with no tracker or CVE content", what it writes "tells the user to
  relaunch under `claude-iso` before it edits, or stops", clause "only where the session reads tracker or pre-disclosure
  content". Valid. Same placement after item 7; F11 restates it as substantive and item 1 lists it a second time.
- Sonnet `instr-1`, two inputs in one row: "a session already inside the sandbox, or a docs-only edit session with no
  CVE content", clause "only where the session reads `<security-list>` or tracker content, and stop if
  `sandbox.enabled` is already on". The docs-only input and the first half of the clause are valid. The sandbox input
  and the second half are noise: the change's own `.claude/settings.json` sets `"enabled": true`, so every session in
  the repository has it on and the clause would end the instruction everywhere. The clause runs past fifteen words.
  `Not findings:` names `README.md:158-169` with a reason in words; that hunk is a docs page, not an instruction, and
  §2a wants line numbers alone. Finding 14 restates the clause.
- Sonnet `instr-2`, input "an agent already started without the wrapper, or in a session on another OS (macOS/zsh,
  where `claude-iso` fails)", clause "where the host is Linux with bash, otherwise report the limit and stop". Noise. A
  session started without the wrapper is the one the paragraph is written for, and the zsh failure is finding B, which
  per §2a step 2 carries its own clause and gets no row. The clause would withdraw the instruction on macOS, which the
  setup supports. The section sits after item 7, the line `Added instructions: 1, 1 row.` stands above a table although
  §2a reserves it for no rows, and `Not findings:` gives `AGENTS.md:315-319` "because the surrounding sentence already
  bounds it to this repository's skills": those lines are the rest of the same paragraph and bound nothing.

Instruction-file findings the runs file besides the rows:

- Opus `instr-1`, "New root doc and tools subtree missing from repository indexes" (`AGENTS.md:79-85`, References),
  substantive. Valid for "Repo-root files" (`AGENTS.md:79-86`), which lists the root documents and omits
  `secure-agent-setup.md`. Noise for the References list, which holds the tool adapters (`tools/github`, `gmail`,
  `vulnogram`, `cve-org`); `agent-isolation` is not one.
- Opus `instr-2`, "Root-file list misses the new page; "no source code" now false" (`AGENTS.md:79-91`), substantive.
  The root-file half is valid. The other half is noise for this change: "There is no source code to build or test" was
  already false at `2efe27f`, which ships `tools/gmail/oauth-draft` with its tests.
- Haiku `instr-2` F16, "The commit says `AGENTS.md` links the doc from an "agent prerequisites" section. There is no
  such section", substantive. Noise: the commit's sentence ("link to the new doc from the "agent prerequisites" section
  and from "Local setup"") pairs the README, whose section is "Prerequisites for running the agent skills"
  (`README.md:136`), with `AGENTS.md`'s "Local setup".
- Sonnet `instr-1` finding 15 (bundled with three other items) and Sonnet `instr-2` finding N, "`AGENTS.md` repo-root
  and tools lists omit the new doc and directory", taste. Valid for `secure-agent-setup.md` in "Repo-root files", noise
  for `tools/agent-isolation/` in References, as above. Sonnet `instr-2` calls the same finding "Substantive (low)" in
  item 7.
- Haiku `instr-1` files no other `AGENTS.md` finding. The `<framework>` placeholder findings (Haiku `instr-1` F24,
  Haiku `instr-2` F15, Sonnet `instr-1` item 2) cite `AGENTS.md` but are about the docs pages, and are not assessed
  here.

Against `1b1ebc3e`: check 1 stays pass for Opus and Haiku in all four runs; the new Sonnet runs give one pass and one
partial. The table improved for Haiku: `instr-1` now writes the row it skipped before, and `instr-2` moved from a
session the instruction serves (noise) to a docs-only session (valid). Both Opus rows stay valid; their clause moved
from "when the session reads tracker content" to "for the person launching a session". Four of the six runs still
restate the row in the findings table; only Opus `instr-1` points to it, and Sonnet `instr-2` files no finding for it.
Of the noise findings, the References half is gone from Opus `instr-2` and stays in Opus `instr-1`, and the two Sonnet
runs file it again as taste. Cost: Opus 1.31 and 1.44 against 1.86 and 1.11, Haiku 0.27 and 0.28 against 0.32 and
0.26. Words: Opus 2646 and 2457 against 2691 and 2456, Haiku 1890 and 2500 against 1707 and 1860.

## Results of V3n, 2026-10-31

`v3n-<n>` ran the working copy of branch `vs/instruction-patch-rules` whose final-review tree is `8545c2eb`: V3m with
one sentence added to step 2 of §2a, that only a condition ends an instruction. Graded by reading `result.md`.

| Model | Run | Check 1 | Table of added instructions | Cost, USD | Words |
| --- | --- | --- | --- | --- | --- |
| Opus | `v3n-1` | pass | one row, valid | 1.06 | 2566 |
| Opus | `v3n-2` | pass | one row, valid | 1.91 | 2685 |
| Haiku | `v3n-1` | pass | none | 0.32 | 2316 |
| Haiku | `v3n-2` | pass | none | 0.22 | 2358 |
| Sonnet | `v3n-1` | pass | one row in prose, noise | 0.35 | 2108 |
| Sonnet | `v3n-2` | pass | one row, valid | 0.64 | 2316 |

Check 1 passes in all six runs, against five of six on `796a9b8d`: each files `date -d` as GNU-only, and Sonnet `v3n-2`
asks to "say Linux or GNU coreutils is required, or use `python3`". Both Opus rows name a session that edits this
framework repository and reads no tracker content, with the clause "when the session reads `<security-list>` or
`<tracker>` content" or "when setting up a machine to run the skills against a tracker". Sonnet `v3n-2` names a
docs-only typo edit, with the same kind of clause. Sonnet `v3n-1` writes its row as a bullet, on a host without
bubblewrap or socat, which the paragraph does not address. Neither Haiku run writes the table, although the change
edits `AGENTS.md`.
