# Change 1: `adr-authoring`

Each sentence below has a class and two inputs, and none is a patch.

| Sentence (added or changed) | Class | Two inputs |
| --- | --- | --- |
| Guarantee of a dependency: the source is not a decision record, so state it in Context with its source. Where the source is a decision record, cite its rule by what it is about. | Where a rule depends on a fact that someone else guarantees. | A base image's README guarantee. A retry limit that another ADR fixes. |
| Context template: "no rule of this record or another is restated (**One home**)". This is a citation. | What Context may contain. | A record on a logging library. A record on token lifetime. |
| Numbers freeze: the `owner/repo ADR-NNNN Rn` form, and every cited record appears under Related ADRs unless Context maps its retired number. | How to cite a rule across repositories and records. | A rule in a platform repo cited from a service repo. A retired record number cited from an external document. |
| One home: cite by number, or by section and short quote where the record has no numbers. For another record's rule, name what it is about. Own-record sections other than Rules and Context may say what a rule decides. | Where and how a requirement is mentioned outside its rule. | A Negative entry that names an accepted cost. A Justification that cites a retry rule of another record. |
| Cite only what the reader needs, with its test, its list of citations to leave out, and "rewrite the citing rule". | Citations that show the writer's knowledge and change no check. | A "see also" in Context. A rule that only shares a subject with the one being written. |
| Every requirement is a rule: a referring section "cites the rule that states it, not the record". | How Confirmation and Implementation notes refer to requirements. | A Confirmation entry for an architecture test. An Implementation note on a migration. |
| No pointer rules: now also covers a rule that "only repeats a requirement of another rule", with the approver's link going to the Justification. | A rule that adds a number and no requirement. | A rule that restates another record's limit. A rule that says "R3 also applies here". |
| Pre-publish read: adds No pointer rules and Cite only what the reader needs, plus a read of every citing sentence outside Rules. | Final review of a record. | A new record. A rewrite of an accepted record. |

The **One home** restatement ban already existed. The new sentences are boundaries (rule 4) and a citation, not a second statement of it.

Verdict: general change

# Change 2: `apm-authoring`, rule 4

| Sentence | Class | Two inputs |
| --- | --- | --- |
| Give the part a condition that ends it: "when the part is absent, and, where it is owed, what to state and where to stop." | A part of an agent's output that is empty or wrong. | A changelog "Breaking changes" section on a patch release. A test-plan section on a docs-only pull request. |
| "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise." | Why both halves of the condition are needed. | A summary section on a one-line change. A risk list on a refactor with no behavior change. |

The sentences give the rule its missing boundary (rule 4 of the skill under review), and they only reorder the existing clauses. No sentence restates a rule elsewhere.

Verdict: general change

# Change 3: `problem-report-authoring`

## General sentences

- **Goal rule:** the goal is needed only where another way to the task may exist. A crash, red build, typo or broken page is its own goal.
  - Inputs: how to do X through an API, and a crash.
- **Isolation rule:** no isolation is owed where the symptom sits in the project's own files. This also covers the Ownership checklist item.
  - Inputs: a dead link in docs, and a trace that stops in the project's code.
- **Nearest hit:** defined as the closest item returned, with a different symptom included.
  - Inputs: a duplicate with a different symptom, and an open pull request.
- **Null search:** stated only in a slot for what you searched, otherwise it goes to the note.
  - Inputs: a form with a "searched" field, and a mailing list.
- **Dependencies:** stated only where there are several reports or a known relative.
  - Inputs: a protocol change needing client and server, and a single bug.
- **Question 4:** an observation that shows the expectation by itself needs no grounding sentence. The weak-grounding example was also reworded.
  - Inputs: a 404 link, and a crash.
- **Evidence source:** labels are needed only where one kind of evidence could be mistaken for another.
  - Inputs: a reporter's log mixed with your run, and an all-self-run report.
- **Redaction:** say nothing where nothing was changed.
  - Inputs: a public repository reproducer, and a log with a token removed.
- **Version of layers:** limited to layers whose behavior the symptom could depend on.
  - Inputs: a typo in a README, and a driver-version-dependent crash.
- **Section 8 no-form order:** each part appears only where its condition holds.
  - Inputs: a one-word typo report, and a multi-layer reproducer.
- **Checklist preamble and items:** an item whose condition is unmet is skipped.
  - Inputs: a question, and a team backlog item.
- **Own-repository issue:** Ownership, Duplicates and Disclosure answers go in the hand-over note.
  - Inputs: an issue filed to fix yourself, and a public bug report.
- **Colleague table:**
  - Goal holds only where you ask how to do something.
  - Run-link trim: paste the claim-carrying lines and say nothing about the trim.
  - Tool versions only where the failure could depend on them.
  - Inputs: a CI link in a thread, and a local-only failure.
- **`project-conventions.md`:** the non-goals slot is dropped from the "most often lacks" list, and the "line each" wording is replaced by "need no line". Both are consistent with the checklist.
- **Request genre slots:** each slot gets its condition, and the grounding paragraph becomes conditional on "who else has it".
  - Inputs: a one-paragraph request, and a costly default change.

I also noticed that the typo and misspelled-name example recurs in the goal rule, isolation, Question 4, the versions rule, section 8 and worked case 7. Each sentence still has two distinct inputs, so I don't count it as a patch. It does lean on one domain (rule 2).

## Patches

1. **`request-genre.md`:** "A slot is what the request says, not a heading: a request that fits in a few paragraphs carries no headings, and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."
   - Rule 7 makes it a patch twice over:
     - "carries no headings" restates the condition already in section 8 ("one that fits in a few paragraphs carries no headings").
     - The setting clause restates the negative-result rule of section 3, and the Alternatives bullet in the same file already says "One kind moves: a setting you tried…".
   - It is also tied to one failure shape (a setting filed in the wrong role), where the rest of the sentence is general. That is rule 6.
2. **`request-genre.md`:** "otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says."
   - Rule 7: it cites section 4 but restates its condition (null search goes to the note unless a slot exists). The citation alone would suffice.
3. **`SKILL.md` §8:** "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."
   - Rule 7: it repeats the sentence on the defect report just before it. The request-genre file then states it a second time. It should be a citation, with one home.

Verdict: contains patches
