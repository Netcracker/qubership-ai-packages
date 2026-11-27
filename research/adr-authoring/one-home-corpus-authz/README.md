# One home across records: a labeled corpus from qubership-authz-agent

These are 342 findings of one kind: text in an Architecture Decision Record (ADR) that restates a rule, a constraint, or
a consequence that another record owns, instead of citing it. Two arms of one review prompt produced them over 20 ADRs
of [Netcracker/qubership-authz-agent](https://github.com/Netcracker/qubership-authz-agent), and blind judges labeled
each one. The corpus is kept so that a change to the **One home** rule, or to the check before publishing, can be
measured against known cases without labeling them again.

Nothing here is a regression case: there is no `prompt.md` and `check.py` does not read this directory.

## What was run

Records under check, each read at one commit:

| Records | Source | Commit |
| --- | --- | --- |
| ADR-0097, 0098, 0099, 0100, 0102, 0103 | PR [#226](https://github.com/Netcracker/qubership-authz-agent/pull/226) | `8519dc09` |
| ADR-0101 | PR [#235](https://github.com/Netcracker/qubership-authz-agent/pull/235) | `a165cb32` |
| ADR-0104 | PR [#329](https://github.com/Netcracker/qubership-authz-agent/pull/329) | `65e78e2a` |
| ADR-0105 | PR [#332](https://github.com/Netcracker/qubership-authz-agent/pull/332) | `29f6b396` |
| ADR-0106 | PR [#330](https://github.com/Netcracker/qubership-authz-agent/pull/330) | `ae609500` |
| ADR-0107 | PR [#359](https://github.com/Netcracker/qubership-authz-agent/pull/359) | `fb564ae8` |
| ADR-0082, 0083, 0090, 0091, 0092, 0093, 0094, 0095, 0096 | `main` | `7f557794` |

Each record got one run of each arm, with Opus, from `briefs/brief.md`. The arms differ only in the procedure the brief
inserts:

- **B** (`briefs/proc-B.txt`): the One home rule as the skill states it, applied across the related records.
- **V** (`briefs/proc-V.txt`): the same rule plus a counterfactual check: list the constraints the record takes from
  other records, suppose each one changes, and write down every line that would then need an edit, the title and the
  Decision sentence included.

The findings of both arms were shuffled into eight batches, and a judge that did not know the arms labeled each batch
from `briefs/judge-brief.md`.

## The data

`findings.jsonl` holds one finding per line:

| Field | Meaning |
| --- | --- |
| `id` | Judge item id, `J<batch>-<n>` |
| `record` | The record under check in the run that produced the finding; the lines may be in another record |
| `arm` | `B` or `V` |
| `pr`, `commit` | The checkout the run read; `pr` is null for `main` |
| `lines`, `quote` | Where the restatement is, relative to `docs/decisions/`, and its text |
| `owner`, `owner_quote`, `why` | The rule the reviewer named as the owner, its text, and the reviewer's reason |
| `verdict` | `TP`, `FP_CITATION` (only names the topic), `FP_OWN` (a decision of this record), `FP_WRONG`, or `UNSURE` |
| `severity` | For a `TP`: `high` where the restatement already disagrees with its owner, `low` otherwise |
| `group` | Findings that describe the same text share a group, prefixed with the batch |
| `judge_reason` | The judge's one sentence |

`python3 research/adr-authoring/one-home-corpus-authz/summary.py` prints the counts below; `--high` adds the 25
high-severity groups with links to their lines.

## Results

| Arm | Findings | TP | FP_OWN | FP_CITATION | Precision | TP high |
| --- | --- | --- | --- | --- | --- | --- |
| B | 149 | 131 | 15 | 3 | 0.88 | 19 |
| V | 193 | 156 | 22 | 14 | 0.81 | 18 |

Of 177 groups of confirmed findings, both arms found 106, V alone 47, and B alone 24. Without ADR-0101 (see the
caveats) the new records split 20 to 21. One run per arm costs about 103000 tokens and 65–72 seconds; a judge batch of
34–54 items costs 109000–142000 tokens.

What the counts show:

- V does not find more restatements in general. With one run per arm, run-to-run variance is as large as the difference
  between the arms.
- V does flag a count or a set restated in the title, the Decision sentence, and Context ("both providers", "two
  kinds"). In ADR-0105 it flagged lines 1, 27–28, 37–38, and 55; B flagged none of them.
- V's extra findings cost precision: `FP_CITATION` rose from 3 to 14, mostly short labels beside a correct citation.
- 20 of the 25 high-severity groups quote text that cites the owning rule and paraphrases it beside the citation, and
  the paraphrase has dropped or changed a condition of the rule: "accepted" is missing from ADR-0091 R14 item 1, and
  "at its first pull after the start" from ADR-0095 R5. The other 5 restate the rule with no citation. Only 12 of the
  25 contain a literal such as a status code, a path, or a duration.

## Caveats

- One run per arm and record, and judges of the same model family as the reviewers.
- The V run on ADR-0101 read the checkouts of other PRs, which the brief did not forbid then; later briefs did. Its 16
  findings against B's 4 are not comparable.
- Groups are assigned within a batch. A text found from two records in different batches, such as ADR-0096 lines
  37–39, counts as two groups.
- Line numbers are those of the listed commit; several of these PRs have moved on since.
