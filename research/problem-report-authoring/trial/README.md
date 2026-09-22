# The trial

The skill was tried on the case that produced it, before the package was called done. This directory
holds everything the trial used and produced.

**One genre only.** Both arms wrote a bug report. The request genre and the colleague message were not
tried, so nothing here is evidence about them.

## Method

Two Sonnet sessions were given the same input, `facts.md`: the notes from an investigation into how
parameterized JUnit tests appear in the XML report Gradle writes, ending with the instruction to draft
the issue for `gradle/gradle`. Neither session was shown the reports that were eventually accepted.

- The control arm was given the notes alone and wrote `control.md`.
- The treatment arm was told to read the skill in full, open its reference files where the skill says
  to, and follow it. It wrote `treatment.md`.

The two drafts were then compared against each other and against the accepted
[gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079).

## What the control arm did and did not do

The worst framing defect did not recur: the control opened with the symptom and put its reading of
Gradle's source below it, under an explicit "this is a reading of the source rather than a confirmed
root cause", with two sections after it. Four defects remained.

| Defect | Where | Rule it violates |
| --- | --- | --- |
| Expected behavior with no literal in it: "each `<testcase>` identifies which method produced it", illustrated with JUnit console output rather than an XML value | `control.md`, Expected behavior | The expected-behavior test, questions 1 and 2 |
| The project's form never read: expected ordered before current, which the Gradle bug form inverts, and no self-contained reproducer, which that form requires | `control.md`, section order | Read the target project first; the form's order wins |
| Two merged pull requests named as possibly related and left unverified | `control.md`, "Possibly related JUnit changes" | Reproduce on a supported version; search and record |
| The index form from another tool reported neutrally as encoding both indices | `control.md`, Investigation notes | Identifiers resolve by content, not by position |

## What the treatment arm did

- Read `.github/ISSUE_TEMPLATE/10_contributor_bug_report.yml` and `CONTRIBUTING.md` before writing,
  and used the form's field labels and order.
- Checked the two pull requests named in the notes and established that both were already in the
  version under test, so the report does not blame the test framework for something already fixed.
- Read Gradle's source at the `v9.7.1` tag rather than at `HEAD`, and ran `git blame` on the line it
  names.
- Marked the proposed rendering as illustrative rather than as a required literal.
- Placed the configuration setting under Current Behavior as a failed attempt rather than as the
  frame of the report.
- Justified filing one report rather than two.
- Handed over three gaps it could not close: the tracker search, with the query terms to run; the
  reproducer re-run, with the command; and the human sign-off, which it raised as a question rather
  than answering.

**Where the treatment draft sits under the rule as it now stands.** The draft traces the defect into
Gradle's source inside `### Current Behavior`, which the rule's second question forbids: a sentence
naming the place in the project's code as the cause does not belong in the passage that states the
symptom. It passes the first question, because deleting its marked reasoning leaves the report
standing. The rule reached that shape after the trial, so this is where the draft is behind the skill
rather than something the trial found.

## What the trial changed in the skill

The treatment arm reported two places where the skill's own text was ambiguous. Both were fixed before
the package was called done.

- The execution rule read as though a proposed expected behavior had to have been run, which is
  impossible for behavior that does not exist yet. Question 5 of the expected-behavior test now
  separates the proposed rendering from the claims around it, and requires a transcript only for the
  second.
- The rule placing causal analysis last did not say what to do when the project's form puts a
  narrative field first, which is the case the treatment arm hit. The framing section answers it
  without reference to position at all: the analysis is marked as a guess, the report has to stand
  when that block is deleted, and no sentence naming the cause sits inside the symptom, the steps or
  the pasted output.

## Files

| File | What it is |
| --- | --- |
| `facts.md` | The input both arms were given |
| `control.md` | The draft written without the skill |
| `treatment.md` | The draft written with the skill |
