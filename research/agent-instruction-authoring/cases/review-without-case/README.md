# Case: a fresh reviewer tells patches from a general change

The input is three changes to skills, each made after a bad output, given as rule 9 asks: the skill's instruction files
as they read after the change, and the diff of those files, with no case, no case record, and no commit message. The
session plays the fresh reviewer.

- Change 1 is the `adr-authoring` hunk of pull request 252 (head `957872496f30`, against its merge base `8d5f4c35`).
  It adds clauses about citing rules to **Guarantee of a dependency**, the Context template, **One home**, and three
  other rules, and adds a rule, **Cite only what the reader needs**.
- Change 2 is the `apm-authoring` hunk of `b247f44c`. It sharpens the existing rule on fixing a bad output, with no new
  rule beside it. This is the input where the review has to stay quiet.
- Change 3 is the `problem-report-authoring` hunk of `091cd34b` (`SKILL.md` and references). Among its sentences is
  "`references/worked-cases.md`, case 7", a case number in the text.

The run was first made by hand on Sonnet at `80aa2828`, where the rule was numbered 8, with the same verdicts as the
checks below. That prompt was not kept; this one rebuilds it from the same three changes.

## Skill parts

- `SKILL.md`: "9. Review a change without the case", and the rules it names as patches and fixes: "4. Give every rule
  its boundary", "5. Redraw a rule that needs a third exception", "6. Keep the case out of the text", "7. State each
  rule once"
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Change 1 contains patches.** The result gives Change 1 `Verdict: contains patches` and quotes at least one
   sentence of its added text.
2. **Change 2 is general.** The result gives Change 2 `Verdict: general change`.
3. **Change 3 contains patches.** The result gives Change 3 `Verdict: contains patches` and quotes at least one
   sentence of its added text.

## Running it

```bash
research/agent-instruction-authoring/cases/run-case.sh research/agent-instruction-authoring/cases/review-without-case opus result
grep -n '^Verdict\|Verdict:' research/agent-instruction-authoring/cases/review-without-case/opus/result.md
```

The grep shows the three verdicts in order; read the quoted sentences to grade checks 1 and 3.

## Results

At skill tree `6c8d990a`, two runs per model. Opus passes all three checks in both runs. Sonnet passes checks 2 and 3
and fails check 1 in both: it reads the sentences of Change 1 that end in a citation, such as "no rule of this record
or another is restated (**One home**)", as citations of **One home**, though they restate its condition beside the
citation. Opus marks those sentences, or the clause of **No pointer rules** that repeats **One home**, as patches under
rule 7.
