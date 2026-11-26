## Change 1

**Sentences**

1. "Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base image's README, state the guarantee in **Context** as a fact, with its source."
   - Class: a record that relies on a promise made by a library, an image, or a platform.
   - Inputs: an ADR on outbound TLS that relies on a base image loading certificates from a directory; an ADR on retries that relies on an HTTP client's documented retry of idempotent methods.
   - Result: it gives the existing Context instruction its missing boundary (rule 4), so it is a fix.
2. "Where its source is a decision record, cite its rule by what it is about instead (**One home**)."
   - Class: a record that relies on a guarantee that another team's record settles.
   - Inputs: a service ADR that relies on a platform repository's ADR on sidecar mTLS; a client ADR that relies on a library team's ADR on pagination tokens.
   - Result: the class holds, but "by what it is about" restates One home.
3. Context template: "and no rule of this record or another is restated (**One home**)."
   - Class: Context paragraphs that paraphrase rules.
   - Inputs: a superseding record whose Context repeats the old rule's threshold; a record whose Context summarizes a sibling record's retry limit.
   - Result: it restates One home.
4. "and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`."
   - Class: citations across repositories.
   - Inputs: a service ADR that cites an organization-wide security ADR; a library ADR that cites the platform's logging ADR.
   - Result: general.
5. "Every record the text cites appears under **Related ADRs**, except a retired number that Context maps to its replacement (**Record numbers**), which has no file to link."
   - Class: citations a reader cannot follow from the metadata.
   - Inputs: a Justification that cites another record's rule; a Negative entry that cites the record whose answer this record changes.
   - Result: general. It has one exception, and that exception points to an existing rule.
6. "a requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short quote where the record has no numbers)."
   - Class: a requirement mentioned in more than one place.
   - Inputs: a Confirmation entry that repeats a timeout value; a record without numbered rules that is cited from a newer one.
   - Result: general.
7. "Where you cite a rule of another record, in any section, name what the rule is about, not what it decides: …"
   - Class: citations across records that copy the cited rule's content.
   - Inputs: a Justification that says "ADR-0031 R4 allows three retries"; a Negative entry that restates another record's key rotation period.
   - Result: general.
8. "In the rule's own record, a section other than **Rules** and Context may say what the rule decides, with its number, as **Negative**, **Open points**, and **Confirmation** do."
   - Class: mentions of a rule inside its own record.
   - Inputs: a Negative entry that names the changed default of R5; an open point that names the placeholder in R3.
   - Result: it gives One home the boundary that the Consequences and Open points sections already depend on, so it is a fix.
9. "A table that summarizes rules holds rule numbers."
   - Class: tables that summarize rules.
   - Inputs: a table that maps endpoints to rules; a table that maps layers to rules.
   - Result: general.
10. "in any section, a citation earns its place where removing it would change what a checker tests, or would leave an approver without the reason for a rule or the cost of a consequence."
    - Class: citations of neighboring records.
    - Inputs: a token-format rule followed by "see also ADR-0040"; a database ADR's Justification that cites the logging record because both mention retention.
    - Result: general.
11. "Leave out a citation that only shows the writer knows the neighboring records: …"
    - Class and inputs: the same as sentence 10.
    - Result: general. The four items are members of one class, not exceptions.
12. "A rule in force applies to every change whether or not it is cited."
    - Result: this is the reason for sentences 10 and 11, with the same inputs. General.
13. "Where a rule reads unclearly without a citation, rewrite the citing rule rather than adding a citation."
    - Class: rules that rely on a citation to make sense.
    - Inputs: "tokens as in ADR-0091"; "the hosts that ADR-0012 allows".
    - Result: general.
14. "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record."
    - Class: Confirmation or Implementation notes that point at a whole record.
    - Inputs: a Confirmation entry that says "as ADR-0091 states"; an Implementation note that says "follow ADR-0042".
    - Result: the class holds, but the sentence restates One home.
15. "a rule that only repeats a requirement of another rule, or only says that another rule applies, adds a number and no requirement."
    - Class: pointer rules.
    - Inputs: "R7. Logging follows ADR-0020."; "R4. Tokens are validated as ADR-0091 R3 requires."
    - Result: the "only repeats a requirement" clause restates One home.
16. "Leave it out; where an approver needs the link, give it in the Justification."
    - Class and inputs: the same as sentence 15.
    - Result: general.
17. The added names in the pre-publish list, and "Then read every sentence outside **Rules** that cites a rule, … against **One home** and **Cite only what the reader needs**."
    - Class: the review of citations before a record is published.
    - Inputs: a Justification that cites another record; a Negative entry that cites its own rule.
    - Result: these name rules and do not restate them, so they are citations. General.

Verdict: contains patches

**Patches**

- "cite its rule by what it is about instead (**One home**)": rule 7. "By what it is about" copies One home's rule for citing another record. "Cite its rule instead (**One home**)" keeps the boundary without the copy.
- "and no rule of this record or another is restated (**One home**)": rule 7. One home already excludes Context, both within a record and across records. The template line copies that condition instead of only naming the rule.
- "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record.": rule 7. One home already says "Everywhere else, cite it by number", and Numbers freeze says how to cite across records.
- "a rule that only repeats a requirement of another rule": rule 7. One home already says that a requirement is stated once, in one rule.

## Change 2

**Sentences**

1. "first give that part a condition that ends it: when the part is absent, and, where it is owed, what to state and where to stop."
   - Class: a part of an agent's output that comes out empty, padded, or guessed.
   - Inputs: a changelog skill whose agent writes "Breaking changes: none" on a patch release; a pull request description instruction whose agent fills "Testing" on a docs-only change.
   - Result: general. It makes the condition for when the part is absent mandatory, and no longer one choice of two.
2. "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise."
   - Class: the same as sentence 1. This sentence gives the reason the absence condition comes first.
   - Inputs: a "Risks" section capped at two sentences that still appears on a dependency bump; a "Migration" section in release notes, limited to one step, that is still written for a release with nothing to migrate.
   - Result: general. No other part of this skill states it, and the pitfall entry only cites rule 4.

The other lines in the hunk were only rewrapped.

Verdict: general change

## Change 3

**Sentences, SKILL.md**

1. §3: "State the goal where the step you got stuck on may not be the only way to it." With it: "A maintainer who knows another way…", and the test, which now has a condition.
   - Class: a report where the blocked step serves a larger task.
   - Inputs: a feature request for a header option when the goal is to propagate a trace ID; a forum question about forcing a CLI flag when the goal is a reproducible build.
   - Result: boundary (rule 4), a fix.
2. §3: "A crash, a red build, a typo, or a broken page is its own goal, and the report needs no sentence for it."
   - Class: the side of sentence 1 where it stays quiet.
   - Inputs: a segfault at startup; a docs page that fails to render.
   - Result: a fix.
3. §4: "Isolate which project owns the defect, where more than one could, …" and "Where the symptom sits in the project's own files, … no isolation is owed."
   - Class: a symptom seen through a stack, and the case where only one project can own it.
   - Inputs: a JDBC error seen through an ORM, where the rule fires; a NullPointerException whose trace stops in the library's own class, where it stays quiet.
   - Result: a fix.
4. §4: "The nearest hit is the closest item the search returned, one with another symptom included: …"
   - Class: searches that return related items but no duplicate.
   - Inputs: a closed issue with another stack trace in the same parser; a discussion of a neighboring configuration option, found for a feature request.
   - Result: general. See note 1.
5. §4: "Where the search found nothing, the report says so only in a slot … ; with no such slot, the query goes to the hand-over note."
   - Class: searches with no hit.
   - Inputs: a GitHub form with an "I searched existing issues" field; a mailing-list report, which has no such slot.
   - Result: boundary, a fix.
6. §4: "Where the count produced several reports, or a related report is known, each report says what it depends on…" and "A single report with no known relative says nothing about dependencies."
   - Class: sets of related reports.
   - Inputs: a protocol change split between a client report and a server report; a build-tool report linked to a test-framework report.
   - Result: a fix.
7. Question 4: "Where the observation shows the expectation by itself, … the observation is the grounding and needs no sentence of its own."
   - Class: expectations that the observation already proves.
   - Inputs: a segfault; a link that returns 404.
   - Result: a fix.
8. Question 4: the new example, "nothing in the documentation promises this; it rests on our own setup".
   - Class: weak grounding stated in plain words.
   - Inputs: reliance on an undocumented iteration order; a request based on your own deployment.
   - Result: general.
9. §6: "…the report says which wherever a reader could take one for another; a report whose evidence is all your own pasted output needs no label."
   - Class: evidence from more than one source.
   - Inputs: a vendor ticket that mixes a customer's log with your reproduction; a bug report that pastes a CI run and a colleague's observation.
   - Result: a fix.
10. §6: "Where you changed or removed anything, say in one sentence … and where nothing changed, say nothing."
    - Class: notes on what was sanitized.
    - Inputs: a public issue with substituted service names; a vendor ticket with a redacted token.
    - Result: a fix.
11. §6: "…every layer between it and the symptom whose behavior the symptom could depend on", the matching test, and "A misspelled name in a README fails under any version of the tool that reads it, …"
    - Class: version lists.
    - Inputs: an operator failure that depends on the cluster version; a rendering defect that depends on the browser.
    - Result: a fix.
12. §8: "Where there is no form and no guide, a defect report opens with the core (§7): what you did and what you observed, with the pasted output, and what you expected."
    - Class: defect reports with no form.
    - Inputs: a report on a mailing list; an issue in a repository with no template.
    - Result: the class holds, but the sentence restates §7.
13. §8: "The parts below follow it in this order, each only where its condition holds: …"
    - Class: optional parts of a report with no form.
    - Inputs: a one-command CLI crash; a docs typo.
    - Result: the reproducer condition is new, but the grounding and version conditions restate §5 and §6.
14. §8: "A report whose parts fit in a few sentences carries no headings: …"
    - Class: short reports.
    - Inputs: a docs typo; a CLI crash with one pasted error.
    - Result: general.
15. §8: "A request and a question take the slots their references name, in that order, under the same rule: …"
    - Class: requests and questions.
    - Inputs: a feature request on GitHub; a question on a forum.
    - Result: the class holds, but the sentence restates `request-genre.md`.
16. §11 intro: "An item applies only where the rule it asks about applies, … skipped, not answered with 'none'." With it: "An item that applies is answered by pointing at a sentence …" and "they go in the review or the hand-over note".
    - Class: checklist items that do not apply to a draft.
    - Inputs: the Observation set item on a crash that reproduces every time; the Measurement item on a typo report.
    - Result: general.
17. §11: "…its Ownership, Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the issue."
    - Class: issues you file in order to fix them yourself.
    - Inputs: a team member who files a bug they will fix; a maintainer who files in their own repository.
    - Result: general. Its second copy is listed under Patches.
18. §11: the conditions added to the Goal, Ownership, Duplicates, Count, Grounding, Attribution, Redaction, Form, and Request items.
    - Class: the same as each item's rule.
    - Result: each condition copies the condition of its rule, which the new intro already defers to.

**Sentences, references**

19. `colleague-message.md`, Goal row: "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none."
    - Class: chat messages.
    - Inputs: asking how to pin a dependency; reporting a red build.
    - Result: restates §3.
20. `colleague-message.md`, Failing output row: "Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim."
    - Class: chat messages backed by a run link.
    - Inputs: a red CI build posted to the team channel; a failing test on a branch.
    - Result: general. It changes how §7 applies in this genre, and stating such changes is what the table is for.
21. `colleague-message.md`, Reproducer row: "The versions of your tools only where the failure could depend on them; a failure CI shows too does not."
    - Class: versions in a chat message.
    - Inputs: a local build failure; a CI failure.
    - Result: the CI clause is new, but the first clause restates the §6 boundary.
22. `project-conventions.md`: "for a request, the acceptance criterion, the slot a backlog item most often lacks" and "ownership, duplicates, and disclosure need no line in it."
    - Class: items in a team's own backlog.
    - Inputs: a backlog feature request; a bug you file to fix yourself.
    - Result: both have a copy elsewhere.
23. `request-genre.md`: "the duplicate search by finding whether someone asked before; what it found goes in the prior-proposals slot below."
    - Class: prior proposals for a request.
    - Inputs: a request that was rejected before; a request discussed earlier in a forum.
    - Result: general.
24. `request-genre.md`, slots intro: "Every request carries the first two." and "Each other slot appears only where its condition holds, …"
    - Class: requests of different sizes.
    - Inputs: a two-paragraph request for a CLI flag; a request that changes a default.
    - Result: general.
25. `request-genre.md`, slots intro: "…and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."
    - Result: restates the Alternatives bullet and §3.
26. `request-genre.md`: the conditions on "Who else is blocked…", "What is out of scope…", and "Alternatives…".
    - Class: request slots whose need varies with the request.
    - Inputs: a request that adds a dependency; a request for a documentation example.
    - Result: boundaries, fixes.
27. `request-genre.md`, prior-proposals slot: "Where the process makes what you searched a required field, the query goes there; otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says."
    - Result: restates §4.
28. `request-genre.md`, grounding: "the grounding is then the task and what it costs today, stated as such, with who else has it where you know."
    - Class: new needs with no documented promise.
    - Inputs: a new export format; a new hook point.
    - Result: general.
29. `request-genre.md`, backlog: "the acceptance criterion is the one a backlog item most often lacks."
    - Result: a copy of the sentence in `project-conventions.md`.
30. `worked-cases.md`: the intro changes and case 7.
    - Class: reports with nothing past the core.
    - Inputs: a misspelled variable on a configuration page; a dead link in a README.
    - Result: general. See note 3.

Verdict: contains patches

**Patches**

- "otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says" (`request-genre.md`): rule 7. It restates §4 and has already drifted from it. §4 sends a null result, with its query, to any slot that "the form or the genre has". The request genre has this slot, but the copy sends the result to the note unless the process makes the field required.
- "a setting that does not serve you is stated beside the problem and not again under alternatives" (`request-genre.md`): rule 7. It restates the Alternatives bullet's "One kind moves…" in the same file and the negative-result rule of §3.
- "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings." (§8): rule 7. It copies the new slots intro of `request-genre.md`.
- "a defect report opens with the core (§7): what you did and what you observed, with the pasted output, and what you expected" (§8): rule 7. It restates the core of §7, and the copy has drifted: §7 says "the one piece of evidence that shows the gap", while the copy says "with the pasted output".
- In §8: "what the expectation rests on, where the core does not show it (§5, question 4); the version of every layer, where the symptom could depend on more than the project's files at the commit the report names (§6)": rule 7. Each condition restates the boundary this change adds to question 4 or to §6, in different words.
- The conditions added to the §11 items Goal, Ownership, Duplicates, Count, Grounding, Attribution, Redaction, Form, and Request: rule 7. The new intro says that each rule states when its item applies, so these copies are a second home. They already drift: Grounding says "where the core does not show the expectation", while question 4 says "where the observation shows the expectation by itself".
- "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none" (`colleague-message.md`): rule 7. §3 now carries this boundary, so "Holds" was enough.
- "The versions of your tools only where the failure could depend on them" (`colleague-message.md`): rule 7. It restates the new §6 boundary. The CI clause after it is new and can stay.
- "ownership, duplicates, and disclosure need no line in it" (`project-conventions.md`): rule 7. It restates the new §11 sentence on issues you file to fix yourself, and the two copies were edited together in this change.
- "the acceptance criterion, the slot a backlog item most often lacks" (`project-conventions.md`) and "the acceptance criterion is the one a backlog item most often lacks" (`request-genre.md`): rule 7. The same statement has two homes, and this change edited both.

**Notes for the author**

1. The definition of the nearest hit includes items with another symptom. A large tracker returns something for almost any query, so the sentence that names the difference now fires on nearly every report, a docs typo included. It needs the input where it stays quiet (rule 4).
2. One example now appears in five rules: a typo or misspelled name in §3, §4, question 4, §6, and §8, and again in case 7. Rule 2 asks for examples from unrelated inputs, and rule 9 warns about one sentence per failed case.
3. The case 7 draft matches, one for one, the boundaries this change adds to §4, question 4, §6, and §8. If it reproduces the input of the case behind the change, rule 6 applies to it.
