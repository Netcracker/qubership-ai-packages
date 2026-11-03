# Case: review a skill edit that fixes bad drafts by adding what to write

A regression case for `final-review` on a change with no code. The input is commit `4f69810` of this repository, one
commit on top of `d79c43d`: it edits `change-description-authoring` after blind drafts of one pull request
description invented a symptom for a defect an audit had found, and then, under a ban on that, wrote "no failure has
been observed" instead. The commit message says "Each fix therefore says what to write": slot 2 now requires the
description to name what found the defect (`An audit of the retry paths found this.`), and a checklist item asks for
it.

That rule applies to every description of a defect nobody observed, including those where the finder is a review tool or
an internal sweep, and it drops the diagnostic of a defect an audit found and a user later reproduced. Three weeks later
the pgjdbc maintainers called the descriptions written under the skill too long;
[Netcracker/qubership-ai-packages#199](https://github.com/Netcracker/qubership-ai-packages/pull/199) lists the rule
among the sources and proposes the condition that ends the slot instead: the trigger condition, and stop.

## What it exercises

Whether the reviewer reads the analogue of *Boundaries, partitions, and the negative control* for an instruction
file: for an instruction the change adds, what the agent produces on an input the instruction does not serve, and
whether the fix is a condition that ends the slot rather than one more thing to write.

## Skill parts

- `final-review`: `SKILL.md` §2a, the analogues of *Boundaries, partitions, and the negative control* and *What the
  writer says it verified*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Checks

Graded by reading the report.

1. **The added slot-2 rule is tested on an input it does not serve.** A finding names such an input and what the rule
   produces there: an internal review, tool, or sweep named where the reader gains nothing, or the diagnostic of a
   defect that was later reproduced dropped. A finding that only questions the wording of the rule, or the measured
   figures, does not pass.
2. **The finding asks for a condition, not more text.** The request is to end the slot at the trigger condition, or to
   name when the finder belongs, rather than to add a further instruction on how to name the finder.
3. **The evidence is checked for the noise side.** A finding notes that the commit's evidence covers drafts that
   invented a symptom, and nothing shows the rule on a description where naming the finder is noise.

## Controls

[`cda-86028c3-review`](../cda-86028c3-review/) is the noise input for the same analogue: a skill edit whose added rule
already carries the condition that ends it.

## Running it

As in the other cases: `research/final-review/cases/run-review-case.sh research/final-review/cases/cda-4f69810-review
<model> <label> [<rev>]` from the repository root. With `<rev>` set to `origin/main` the skills come from before the
analogues for instruction files were added; that run is the baseline.

## Results

`base-1` ran the skills from `origin/main`, before the analogues for instruction files were added, as the baseline.
`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules` (variant V3m below, rewrapped) on
2026-10-30, with `apm-authoring` given to the reviewer as well; the `1b1ebc3e` runs these labels held before are in
git. Graded by reading `result.md`, 2026-10-30. A finding stated only in an item's prose, not in the findings table, is
partial for check 3.

| Model | Run | Check 1 | Check 2 | Check 3 | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | baseline `base-1` | pass: "A writer could drop the reproduced diagnostic" | partial: asks to "State that a reproduced diagnostic is quoted as observed", no restriction of the rule | partial: "No draft with an observed, quoted symptom was run", not an input where the finder is noise | 1888 | 0.98 |
| Opus | `instr-1` | pass: "For an audit-found defect that a test or a user then reproduced, the changelog loses the literal that R3 greps for", filed under item 1 as a conflict, with no row | pass: "Limit them to '… and no observation or reproduction shows a symptom'" | pass: "No noise-case check for the added rules", substantive | 1767 | 0.92 |
| Opus | `instr-2` | pass: the `:475` row, "An audit-found defect whose new regression test reproduces an exception" | pass: "unless a test or a run reproduced the symptom; then quote it" | pass: "No noise check", substantive, naming "a defect with an observed symptom" | 1986 | 1.17 |
| Sonnet | `instr-1` | fail: "Not findings: `:93` (the audit rule is ended by its own condition…)"; the `:98` row on an observed exception is about the derived-consequence label, not the finder | fail: asks to "State which wins when both apply" | fail: the unrun rules are "stated honestly, so it is not a finding"; no noise input | 1825 | 0.37 |
| Sonnet | `instr-2` | fail: "Not findings: `:92` (ends at 'end the sentence there')" | fail: asks to "State which wins when a defect found by code reading also has no symptom" | partial: "the audit rule has no example where the rule is noise, such as a defect with an observed symptom", in the prose: "I don't file this separately" | 1218 | 0.27 |
| Haiku | `instr-1` | pass: "For a defect an audit found that also has an observed symptom, 'end the sentence at what found it' conflicts with 'carry what a person observes'" | pass: "the end-at-finder rule applies only when none is observed" | fail: no noise-side gap; F7 asks only for runs of the final wording | 1577 | 0.23 |
| Haiku | `instr-2` | pass: "'An audit found this.' with the log line dropped" | pass: "only where no symptom has been observed" | partial: "no control for a defect that is both audit-found and observed", in the prose, filed only as the rule's finding 1 | 1651 | 0.15 |

On `796a9b8d` both Opus runs pass all three checks, as both V3m runs without `apm-authoring` and both `1b1ebc3e` runs
did, in shorter reports: 1767 and 1986 words, against 2141 and 2051 on V3m and 2244 and 1877 on `1b1ebc3e`. `instr-2`
keeps the row on the reproduced diagnostic at `:475`, as both V3m runs did. `instr-1` writes "Added instructions: 7, no
rows" and files the same input in item 1, as a conflict between the audit rules and the Symptom checklist, with the
condition as its request; the checks pass it, but the row is gone.

Haiku passes checks 1 and 2 in both runs, as on `1b1ebc3e`: `instr-2` in a row on `:92` and one on `:475`, `instr-1`
as a conflict in item 1. Check 3 fails in `instr-1` and is partial in `instr-2`, against one pass and one fail before.
Sonnet fails checks 1 and 2 in both runs, against one run of two on `1b1ebc3e`: each closes the audit rule under
`Not findings:` as ended by "end the sentence there", and files instead that the audit rule and the no-symptom rule
overlap, asking which wins. Sonnet check 3 fails in `instr-1` and is partial in `instr-2`; both runs were partial
before.

## Iterations on the wording

Variants of the §2a wording, run on this case, graded by reading. The variants are described in
[`cda-86028c3-review`](../cda-86028c3-review/README.md#iterations-on-the-wording); V1 to V2b ran on 2026-10-28, V3 to
V3m on 2026-10-30, V3n on 2026-10-31; V3g, V3k and V3l were not kept.

| Variant | Model | Runs | Check 1 | Check 2 | Check 3 | Words |
| --- | --- | --- | --- | --- | --- | --- |
| V1 | Haiku | v1-1, v1-2 | pass, pass | pass, partial | partial, partial | 1591, 1544 |
| V1b | Haiku | v1b-1, v1b-2, v1b-3 | fail, partial, pass | fail, fail, partial | fail, partial, partial | 1455, 1187, 1320 |
| V1c | Haiku | v1c-1, v1c-2, v1c-3 | pass, pass, pass | pass, pass, pass | partial, partial, pass | 1286, 1522, 1644 |
| V1c | Sonnet | v1c-1, v1c-2 | fail, pass | fail, pass | fail, pass | 1750, 1747 |
| V1d | Sonnet | v1d-1, v1d-2, v1d-3 | pass, pass, pass | pass, partial, pass | fail, pass, pass | 1443, 1682, 1326 |
| V1e | Sonnet | v1e-1, v1e-2, v1e-3, v1e-4 | pass, fail, pass, partial | pass, fail, pass, partial | pass, fail, fail, fail | 2528, 1639, 2124, 1935 |
| V1f | Sonnet | v1f-1, v1f-2, v1f-3, v1f-4 | partial, fail, pass, pass | partial, fail, pass, pass | pass, partial, partial, partial | 2556, 2080, 1898, 2680 |
| V2 | Sonnet | v2-1, v2-2, v2-3 | fail, fail, fail | fail, fail, fail | partial, fail, partial | 1206, 1321, 1967 |
| V2b | Sonnet | v2b-1, v2b-2, v2b-3 | partial, fail, pass | partial, fail, pass | fail, partial, fail | 1481, 1907, 2047 |
| V3 | Haiku | v3-1, v3-2 | pass, fail | pass, fail | fail, fail | 1163, 1492 |
| V3 | Sonnet | v3-1, v3-2 | fail, partial | fail, partial | partial, partial | 1800, 1891 |
| V3b | Haiku | v3b-1, v3b-2 | pass, fail | pass, fail | fail, fail | 1331, 1880 |
| V3b | Sonnet | v3b-1, v3b-2 | pass, pass | pass, pass | partial, partial | 1358, 1498 |
| V3c | Sonnet | v3c-1, v3c-2 | partial, partial | partial, partial | fail, fail | 1732, 2264 |
| V3d | Sonnet | v3d-1, v3d-2 | pass, partial | pass, partial | pass, partial | 1875, 1731 |
| V3d | Opus | v3d-1, v3d-2 | pass, pass | pass, pass | pass, pass | 2168, 1990 |
| V3e | Sonnet | v3e-1, v3e-2 | pass, partial | pass, partial | fail, partial | 1749, 1783 |
| V3e | Opus | v3e-1, v3e-2 | pass, pass | pass, pass | pass, pass | 2273, 2041 |
| V3f | Opus | v3f-1, v3f-2 | pass, pass | pass, pass | pass, pass | 1862, 2044 |
| V3g | Opus | v3g-1, v3g-2 | pass, pass | pass, pass | pass, pass | 1920, 1877 |
| V3h | Opus | v3h-1, v3h-2 | pass, pass | pass, pass | pass, pass | 1903, 2135 |
| V3i | Opus | v3i-1, v3i-2 | pass, pass | pass, pass | pass, pass | 2060, 1950 |
| V3j | Opus | v3j-1, v3j-2 | pass, pass | pass, pass | pass, pass | 1845, 2629 |
| V3k | Opus | v3k-1, v3k-2 | pass, pass | pass, pass | pass, pass | 2169, 2163 |
| V3l | Opus | v3l-1, v3l-2 | fail, pass | fail, pass | pass, pass | 1832, 1913 |
| V3m | Opus | v3m-1, v3m-2 | pass, pass | pass, pass | pass, pass | 2141, 2051 |
| V3n | Opus | v3n-1, v3n-2 | pass, pass | pass, pass | pass, pass | 1695, 2063 |
| V3n | Sonnet | v3n-1 to v3n-4 | fail, pass, pass, pass | fail, pass, pass, pass | fail, pass, pass, pass | 1876, 1487, 1448, 1657 |
| V3n | Haiku | v3n-1, v3n-2 | pass, pass | pass, pass | fail, partial | 1152, 1588 |

V1c-1, V1e-2, V2-1, V2-2, V2-3, V2b-2, Haiku V3-2 and V3b-2 reach the observed-diagnostic input and close it with "the
rule's own condition ends it" or "not a finding". Sonnet V3c, V3d-2 and V3e-2 reach it and file it as taste, which the
checks count as partial.

The trade across variants: on Sonnet, V1d had the most target hits (check 1 passes in 3 of 3), and V1e to V2b gave
some of them up for a quieter control, V2 hitting none. The V3 variants, which change how rows are counted and written
rather than which input is chosen, did not cost the target: Opus passes every check in all sixteen V3d to V3k runs, and
Sonnet passes checks 1 and 2 in 4 of 8 V3b to V3e runs against 1 of 3 on V2b.

V3l, which sends an instruction that reads two ways to item 1, lost the row in v3l-1: the report wrote "6, no rows",
called every input a conflict or an ambiguity filed under item 1, and filed none of them there. V3m sends an ambiguity
to item 1 only where one of its readings serves the input, and both of its runs keep the row on the observed
diagnostic, at `:475` "the condition alone", with the clause "where no failure of it has been observed" and "unless a
test or a report has since shown the diagnostic".

V3n, on the working copy whose final-review tree is `8545c2eb`, adds to step 2 that only a condition ends an
instruction: a clause on where the output stops, such as "end the sentence there", says what the agent writes once the
instruction fires. Both Sonnet runs on `796a9b8d` had put the audit rule on the `Not findings:` line as ended by that
clause. On V3n three Sonnet runs of four reach the observed diagnostic and ask for a condition: v3n-2 and v3n-4 in a
row on `:91` ("only where no failure has been observed", "only where no symptom has been observed"), v3n-3 as an
ambiguity in item 1 ("restrict to 'where no one observed it'"). v3n-1 still writes "the audit rule on a defect with an
observed symptom (the rule's condition ends it)" under `Not findings:`. Both Opus runs pass all three checks, v3n-1 with
the input filed under item 1 as an ambiguity and "Added instructions: 8, no rows", v3n-2 with a row on `:475`. Both
Haiku runs pass checks 1 and 2, v3n-1 in a row on `:91` and v3n-2 in item 1.

## Results of the `cond` arm, 2026-10-31

`draft-<n>` ran final-review tree `3d6a0954`, which had shortened the analogue of *What the writer says it verified* to
"the exemplars include an input like the one its row in the table below takes"; `cond-<n>` ran tree `385ba703`, which
keeps that sentence as before. Both trees also condition the hunk and command rules, shorten the §2a analogue of
*Boundaries, partitions, and the negative control* to one sentence, and change the report of §4 to an index. Graded by
reading `result.md`. The committed tree `a24f8021` differs from `385ba703` in the outcome sentence of the command rule,
which this case's change, adding no command, does not reach; by line wrapping; and by the word restored in "an item with
a finding gives the file and line" in §2, which every run since `3d6a0954` read without "finding". The `cond` results
stand for it.

| Model | Run | Check 1 | Check 2 | Check 3 | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `draft-1` | pass | pass | fail | 1951 | 0.94 |
| Opus | `draft-2` | pass | pass | fail | 1543 | 1.19 |
| Opus | `cond-1` | pass | pass | pass | 1840 | 1.18 |
| Opus | `cond-2` | pass | pass | pass | 1845 | 1.12 |
| Sonnet | `draft-1` | pass | pass | fail | 1553 | 0.45 |
| Sonnet | `draft-2` | pass | pass | fail | 1696 | 0.40 |
| Sonnet | `cond-1` | fail | fail | fail | 1451 | 0.43 |
| Sonnet | `cond-2` | pass | pass | fail | 1747 | 0.29 |

- **Check 3 needs the sentence.** Both Opus `draft` runs lose it: their evidence finding is about untested genres. With
  the sentence back, both Opus runs file it again (`cond-1`, `result.md:76`: "§2a asks for a bad case where each added
  item is noise … with a check that the output did not grow there. The commit states none."). The sentence asks
  whether the writer showed the noise input; the table asks the reviewer to construct one, and the shortening had read
  the two as the same.
- **Sonnet** fails check 3 in every run of both arms, as in `instr` (fail, partial). `cond-1` closes the audit rule
  under `Not findings:` as ended by its own condition (`result.md:67`), the failure of `instr-1`; `cond-2` writes the
  row. `cond-2` ends on "and the `english-developer-style` pass", a check the form does not ask for.
- **The report.** No index carries a request. Opus `cond-1` points to the row ("Table row in Item 3"); Sonnet `cond-2`
  restates it in the index without a pointer.
