# Case: openjdk/jdk#33173, a defect an audit found

The input is notes on [openjdk/jdk#33173](https://github.com/openjdk/jdk/pull/33173): an automated audit found that
`JNIHandles::is_same_object` upcalls into `ValueObjectMethods` without initializing it, and the change initializes the
class at startup instead of adding one more on-demand initialization. The notes list every hunk, give the issue
discussion that rejected the one-line fix, and the review question on `VERBOSE` that the review answered. Nobody has
seen the defect fail. The drafts that led to #130 were written for this pull request; the notes here are prose, with
no code from the diff.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 2: a defect nobody has observed, a derived consequence; Pull request description: the
  What slot and translation, rejected alternatives, Scope and open questions), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **What found the defect is not named** (`finder_not_named`). The slot ends at the condition that reaches the
   defect; the audit is the route, not the result.
2. **No statement about failures seen or not seen** (`no_absence_claim`). "No failure has been reported", "has not
   been observed", and the like fail: the sentence ends at the condition.
3. **No predicted symptom** (`no_predicted_symptom`, read). No sentence says what a JNI caller would see, such as a
   `NullPointerException` or a null `UNSAFE`, unless it is traced to the caller and marked as derived; the notes carry
   no such trace.
4. **No hunk read aloud** (`no_hunk_translation`). No sentence says that the per-site initializations are removed or
   dropped; the reason they are no longer needed is the content, and the diff shows the removal.
5. **The alternative is rejected by a mechanism of the merged code** (`alternative_by_mechanism`, read). The one-line
   fix in `is_same_object` is rejected because the next upcall could repeat the omission, or because eager
   initialization with the asserts exposes a too-early use. The `value.bsm.debug` property and the `initPhase1()`
   ordering are an obstacle this change removes, not a reason against the alternative.
6. **The answered review question is not open** (`answered_question_not_open`). `VERBOSE` stays; no sentence asks
   whether to remove it.
7. **The property is named** (`property_named`). `value.bsm.debug` is a public identifier the change makes inert, so
   it is named once, the exception the translation rule allows.

## Running it

As in [the cases README](../README.md). `controls/run-B.md` is a draft from the research behind #130, written under an
earlier version of the skill. `controls/unnamed-and-reopened.md` is `controls/main-opus.md` with the audit and the
property taken out, and the answer to the review question replaced by the question, marked as left open.
`controls/main-opus.md` is the Opus result of 2026-10-20, written when the skill still asked for the audit to be named.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Finder not named (1) | No absence claim (2) | No prediction (3) | No hunk (4) | Alternative (5) | Not open (6) | Property (7) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes | passes | passes | passes |
| Opus r2 | passes | passes | passes | passes | passes | passes | passes |
| Haiku r1 | passes | passes | passes | fails: "the per-site initialize calls are removed" | passes | passes | passes |
| Haiku r2 | passes | fails: "What a JNI caller observes … is not established here" | passes | fails: "The `initialize` calls in … are removed" | passes | passes | passes |
| Opus baseline | fails: "found the missing call" | fails | passes | fails | passes | passes | passes |
| Haiku baseline | fails: "A post-integration audit … confirmed that fix" | fails | passes | fails | passes | passes | passes |
| `controls/run-B.md` | fails: "an audit of the VM upcalls … found one more" | passes | fails: a null `UNSAFE`, not traced | fails | fails: the `initPhase1` obstacle | passes | passes |
| `controls/unnamed-and-reopened.md` | passes | passes | passes | fails | passes | fails | fails |
| `controls/main-opus.md` | fails: "An automated post-integration audit … found another upcall" | passes | passes | fails: "The upcall sites drop their on-demand initializations" | passes | passes | passes |

The new runs no longer name the audit. Opus r1 and r2 say the interpreter, `JVM_IHashCode`, and the C2 path "no longer
initialize" the class themselves, which the script accepts as not reading the hunk aloud; both Haiku runs say the
initializations are removed.
