# Research: blackbox-test-design

What loads [`agent-packages/blackbox-test-design`](../../agent-packages/blackbox-test-design/README.md), and what it
changes in the answer once loaded. The package ships no instructions file, so its description is the only thing that
loads it without being asked by name; `trigger/` measures that. `cases/` measures the answer.

## Trigger eval

`trigger/eval-set.json` holds 89 queries, 51 that should load the skill and 38 that should not:

| Kind | Count | Where it came from |
| --- | --- | --- |
| `original` | 20 | The first eval set, written with the skill: ten situations and ten near misses |
| `situation` | 38 | Written by an agent that read the skill and was told to describe situations, not the technique: migration before cutover, a vendor binary with a call budget, goldens that disagree, comparator design, a green suite that missed an incident, planning a round, coverage offered as proof, a short follow-up in the middle of a session, another team's undocumented service, and five in Russian |
| `near-miss` | 24 | Written by a second agent told to share keywords with the skill and need something else: tests of readable code, data and schema migrations, mocks and recorded fixtures of a vendor API, contract tests between owned services, load tests, a lecture on metamorphic testing; five in Russian |
| `borderline` | 7 | From the same agent, each with the label it chose and a `why` |

`trigger/run_trigger_eval.py` runs each query through `claude -p` in a scratch project holding every skill in
`agent-packages/`, with `--setting-sources project`, so the user's own CLAUDE.md, hooks, and skills stay out. A run
counts as triggered when the session calls the Skill tool with `blackbox-test-design` at any point; a run that ends in
an error or a timeout is left out of the rates and counted in `failed_runs`.

skill-creator's `run_eval.py` was tried first and reported a recall of 0% on the description that this harness
measures at 98%. It registers the description as a command rather than a skill, and it scores a run as not triggered
as soon as the first tool call is anything else. With `test-authoring` installed beside it, the first call is usually
`Skill(test-authoring)`.

Results for the description in `SKILL.md`, three runs per query, no run without a verdict
(`trigger/results-<model>.json` holds the rate of every query and the other skills each session loaded):

| Model | Should load (51) | Should not: original (10) | Should not: near miss (24) | Should not: borderline (4) | Queries passed |
| --- | --- | --- | --- | --- | --- |
| Opus | 50 | 0 | 0 | 4, at rates from 1/3 to 2/3 | 87 of 89 |
| Sonnet | 50 | 0 | 0 | 0 | 88 of 89 |

A query passes when the majority of its runs matches its label, so Opus fails only the borderline query it loads at
2/3.

The query it misses on both models is a short follow-up, `before i send this batch to the stand, sanity check it`,
which needs the session it was written for; a scratch project gives it none. The borderline query Opus loads on most
often, characterization tests for a legacy class whose source the team holds, is one where the skill's spelling
classes and idioms would still help choose inputs, so the description was not narrowed for it.

The description went through two edits from the one written with the skill. That one scored 87 of 89 on the default
model, in an earlier run against the skills installed on the author's machine rather than those in `agent-packages/`:

- `every test passed, so why did we miss this?` and `does our mutation score or coverage prove the spec right?` now
  name the reference. Without it, the description loaded on a golden suite for the team's own SQL formatter in every
  run; Opus still loads it in one run of three.
- `another team's undocumented service` and `dual run` were added, and the sentence that summarized the skill's
  content was cut, to stay under the 1020 characters `make check-descriptions` allows.

## Behavioral cases

Each case under `cases/` holds `prompt.md`, the input files under `files/`, and a `README.md` with the checks.
`cases/run-case.sh` runs one case in a scratch directory with `--setting-sources project`; both arms have
`test-authoring` installed, and the with-skill arm adds `blackbox-test-design` and leaves loading it to the session.
The results under `results/<arm>-<model>/` hold the files the session wrote, `run.txt` with the cost and the skills it
loaded, and `grading.json`, written by a separate agent that read the checks and the result.

| Case | What it asks |
| --- | --- |
| `parity-plan` | The last round of at most 50 requests to a shared legacy stand before cutover, with a green parity suite |
| `probe-vendor-jar` | Where a vendor jar differs from its documentation, in at most 60 runs, without decompiling it |
| `spec-proven` | Whether a spec that matches every golden, with a 98% mutation score and full pairwise coverage, is proven |
| `reconcile-goldens` | Six round 12 goldens that disagree with a spec whose region list has grown one mismatch at a time |
| `shadow-diff-normalizer` | A review of a normalizer that brings a shadow-traffic diff from 30% to under 1% |

Results on Opus, one run per arm, graded against every check of the case README:

| Case | With the skill | Without | Checks the arm without the skill failed |
| --- | --- | --- | --- |
| `parity-plan` | 12/12 | 7/12 | structural relations over uploads, identity collisions, a drop order, control replays and the legacy build, hypotheses labeled |
| `probe-vendor-jar` | 10/11 | 7/11 | duplicate rule names, tabs in coupon codes, evidence on every finding, a mechanism stated without the probe that backs it |
| `spec-proven` | 11/11 | 7/11 | structural relations, evaluation order, a second model, a prioritized list |
| `reconcile-goldens` | 8/8 | 7/8 | a drop order for round 13 |
| `shadow-diff-normalizer` | 8/9 | 9/9 | none; the arm with the skill failed to order its findings by the cost of being wrong |
| Total | 49/51 | 37/51 | |

The arm with the skill loaded `blackbox-test-design` from its description in all five cases; the arm without it loaded
`test-authoring` in two and no skill in three. In `probe-vendor-jar` the arm with the skill left duplicate rule names
untested, as the arm without it did. Both arms of `reconcile-goldens` replaced the region list with the general rule and
asked for the build that answered round 12, so that case separates the arms only on how the round is budgeted. The arms
without the skill depend only on `test-authoring`, so a change to `blackbox-test-design` re-runs the arms with it;
`skill-tree` and `skill-tree-test-authoring` in each result name the trees that produced it. The runs committed here
cost about $7.

`parity-plan`, `probe-vendor-jar`, and `spec-proven` were written with the skill, and an earlier revision of it scored
34 of 34 checks with the skill against 25 of 34 without, one Opus run each. `reconcile-goldens` and
`shadow-diff-normalizer` were added with the package, for the two uses those three did not reach: a mismatch in the
middle of a session, where the narrow fix is to extend an exception list, and the review of a comparator.
