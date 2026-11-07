# Case: quadratic event processing in telemetry PR 173

A regression case for `adversarial-code-review` from [Netcracker/qubership-ai-agent-telemetry#173][pr]. The input pins
the revision that received [APPROVE with zero findings][missed-review], before two performance defects were reported.
The live pull request already contains fixes, so reviewing its latest head does not exercise the missed defects.

[pr]: https://github.com/Netcracker/qubership-ai-agent-telemetry/pull/173
[missed-review]: https://github.com/Netcracker/qubership-ai-agent-telemetry/pull/173#pullrequestreview-5668149575

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Performance, capacity, and cost*; §Finding content,
  for triggering conditions, concrete impact, and evidence.

## Frozen input and evidence

`repo`, `base`, and `head` pin the repository and the original review's revision tuple:
`6542db79adb6a47c339e52051752e0d70e0c4765...645858771c155b8fcedb8a251e927d88d1cbcd23`.
`prompt.md` supplies the task through the existing runner. It omits the later review and fixes so the reviewer must
find the defects from code. Keep this README and subsequent results out of the evaluating session.

The two [history-delivery][history] and [pending-call][pending] findings were published against
`e98e3f7254bb6d64352b2f4d464ddfadae93d09e`. Its `opencode_plugin.mjs` is identical to the file at the pinned head.
The comments report deterministic operation counts against OpenCode 2.1.4; these are source evidence, not fresh
measurements performed by this case.

[history]: https://github.com/Netcracker/qubership-ai-agent-telemetry/pull/173#discussion_r4398667336
[pending]: https://github.com/Netcracker/qubership-ai-agent-telemetry/pull/173#discussion_r4398667345

## Checks

Grade each check by reading `result.md`. A passing detection must be a finding with its condition, code location,
and impact. An unexplained mention of O(N²), a generic request for a benchmark, or a claim based only on nested
syntax does not pass.

1. Ordinary prompt delivery: identify `opencode_plugin.mjs:146-155`, where every delivered inbox event reads context
   and scans for one message, including prompts with no skill attachment. Explain O(deliveries × history size),
   becoming O(N²) over N deliveries as uncompacted history grows. The affected background observer delays subsequent
   telemetry events; it does not directly block prompt execution. The source fixture counted 500,500 inspected IDs
   for 1,000 deliveries and 2,001,000 for 2,000. Propose avoiding routine full-history lookup while preserving
   reload-before-delivery attachment recovery.
2. Pending nested calls: identify `opencode_plugin.mjs:108-109`, where each completion performs `findIndex` and
   `splice` on calls sharing an outer key. Explain the batch condition: N pending distinct tools completing in reverse
   registration order require N(N+1)/2 comparisons, with the same 500,500 and 2,001,000 counts. Sequential calls with
   one pending entry do not exhibit this growth. Repeated calls of one tool still shift array entries. OpenCode awaits
   completion hooks, so this work affects tool completion. Propose per-tool queues with cursors or equivalent linear
   bookkeeping that preserves repeated calls, terminal cleanup, and late-callback handling.
3. Evidence calibration: derive the aggregate cost or provide deterministic operation counts at N and 2N. Attribute
   any quoted fixture counts to their source; do not claim production latency or a fresh run without measuring it.
   Returning correct events or passing functional tests does not establish acceptable scaling.

Checks 1 and 2 are separate root causes. A report that finds one passes only that detection check. Do not require the
exact example numbers or a particular data structure when equivalent evidence and a safe remedy establish the defect.

## How to run

From the repository root, use the existing runner, once per model, arm, and run:

```bash
case_dir=research/adversarial-code-review/cases/telemetry-173-quadratic-work
bash research/adversarial-code-review/cases/run-review-case.sh "$case_dir" <model> <label> <skill-revision>
```

Use two runs each on the target models, Opus and Sonnet, for the unchanged skill and the candidate. Read all checks
in every result; retain `result.md`, `run.txt`, and `skill-tree` as the runner writes them. The historical zero-finding
review establishes the reported miss, but does not replace a fresh control for comparing skill revisions.

For a fixed-code control, copy the case outside the checkout and set its base to
`8e8a8662a0a0c28372a7c113a808f3db31af0678` and head to `671bdb520e86f22d1fcf35fa8df46db40e9da0be`.
The reviewer must not report either original defect when the observed-enqueue cache and cursor queues remove it.
Other independently established findings remain valid. Keep any recovery fallback conditional on its actual trigger;
a full-context lookup during recovery alone does not prove routine quadratic work.

## Results

No fresh model comparison is recorded yet. The PR's original approval and subsequent findings are historical evidence
of the miss, not evidence that the candidate skill improves detection.

The case oracle was checked locally on 2026-10-28 by extracting `opencode_plugin_test.mjs` from the fixed revision
into a temporary directory and running its four operation-count tests against each plugin revision:

```bash
node --test --test-name-pattern='delivers 2000 ordinary|matches .*pending tools' opencode_plugin_test.mjs
```

All four failed on the pinned faulty head and passed on `671bdb520e86f22d1fcf35fa8df46db40e9da0be`. The failing
head produced 2,000 context reads, 502,500 and 2,005,000 `event.tool` reads for the reverse-order batches, and
1,999,000 shifted entries for repeated calls. The `event.tool` metric includes reads outside the search predicate,
so it differs from the review's name-comparison metric. This verifies the code oracle, not the skill's detection rate.
