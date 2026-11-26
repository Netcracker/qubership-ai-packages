## Change 1

**Guarantee of a dependency**
- "Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base image's README, state the guarantee in **Context** as a fact, with its source." Class: a record that relies on a promise another party made, where the promise is not a decision record. Inputs: a TLS record that relies on a base image's README saying its entrypoint loads mounted certificates; a caching record that relies on a library's documented promise that its client is thread-safe. It should stay quiet for a record that relies on no outside promise. This sentence gives an existing rule its missing boundary (rule 4), so it is a fix.
- "Where its source is a decision record, cite its rule by what it is about instead (**One home**)." Class: a record that relies on another record's decision. Inputs: a service's retry record that relies on the platform repository's ADR on gateway timeouts; a token record that relies on an accepted ADR on key rotation. Sending these to a citation instead of to Context is a general change. However, "by what it is about" repeats a condition that **One home** already states.

**Template, Context placeholder**
- "No requirement belongs here, and no rule of this record or another is restated (**One home**)." Class: Context that retells rules. Inputs: a superseding record whose Context recounts the rule it replaces; a database record whose Context retells another record's retention rule. This restates the Context limit that **One home** already sets.

**Numbers freeze**
- "and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`." Class: citing a rule across repositories. Inputs: a service ADR that cites the organization's platform ADR; a library ADR that cites a rule in a security-policy repository. General.
- "Every record the text cites appears under **Related ADRs**, except a retired number that Context maps to its replacement (**Record numbers**), which has no file to link." Class: a cited record with no link. Inputs: a Justification that cites ADR-0031; a Negative that cites an ADR in another repository. It stays quiet for a retired number. This is the rule's one exception. General.

**One home**
- "A requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short quote where the record has no numbers)." Class: a requirement that appears in more than one place. Inputs: a Confirmation entry that refers to R3; a superseding record that refers to a statement in an old record without numbers. General.
- "Where you cite a rule of another record, in any section, name what the rule is about, not what it decides: …" Class: a citation across records that copies the decision. Inputs: a Justification that cites another record's retry limit; a Context that cites another record's token lifetime. General.
- "A restatement drifts." This is the reason for the rule. General.
- "In the rule's own record, a section other than **Rules** and Context may say what the rule decides, with its number, as **Negative**, **Open points**, and **Confirmation** do." Class: where a record may describe its own rules. Inputs: a Negative that names a default its R4 changes; an open point that names what R2 would decide. It stays quiet in Context. General.
- "A table that summarizes rules holds rule numbers." This is a rewording and needs no check.

**Cite only what the reader needs** (all five sentences)
- Class: citations that change neither what a checker tests nor what an approver learns.
- Inputs: an auth record with a "see also" to the logging ADR; a Confirmation entry reminding the reader that ADR-0012 R2 still applies.
- It stays quiet for a Justification citation that gives the reason for R3.
- The rule states its own boundary ("earns its place where…"). General.

**Every requirement is a rule**
- "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record." This restates **One home**'s "Everywhere else, cite it by number".

**No pointer rules**
- "a rule that only repeats a requirement of another rule, or only says that another rule applies, adds a number and no requirement." The added clause, "only repeats a requirement of another rule", restates **One home**'s "a requirement is stated once, in one rule".
- "Leave it out; where an approver needs the link, give it in the Justification." Class: a rule that only links to another rule. Inputs: an R9 that says "ADR-0091 R7 applies"; an R5 that repeats R2 for one endpoint. General.

**Drafting from the user's input**
- The longer list of rules to read against, and "Then read every sentence outside **Rules** that cites a rule … against **One home** and **Cite only what the reader needs**." These sentences only name rules for the agent to run, which counts as a citation under rule 7. Inputs: a Context that cites another record; a Consequences section that cites a rule. General.

Verdict: contains patches

Patches:
- "Where its source is a decision record, cite its rule by what it is about instead (**One home**)." Rule 7: "by what it is about" restates a condition of **One home**. The routing in the sentence is a fix and can stay. Only the restated clause has to go.
- "No requirement belongs here, and no rule of this record or another is restated (**One home**)." Rule 7: it restates **One home**'s limit on Context.
- "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record." Rule 7: it restates **One home**'s "cite it by number".
- "a rule that only repeats a requirement of another rule, …" Rule 7: it restates **One home**'s "stated once, in one rule".

## Change 2

- "first give that part a condition that ends it: when the part is absent, and, where it is owed, what to state and where to stop." Class: a part of an agent's output that is empty or wrong on some inputs. Inputs: a "Testing" section in a pull-request-description skill, which should be absent for a change that only edits docs; a "Breaking changes" entry in a changelog skill. Both lie in this skill's scope of authoring instructions. The sentence now requires both conditions in a fixed order, so it is a general change.
- "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise." Class: the same. This is the reason the first sentence now asks for both conditions. Inputs: the two above. General.

Verdict: general change

## Change 3

**§3**
- The Goal rule's new heading, "A maintainer who knows another way…", "A crash, a red build, a typo, or a broken page is its own goal…", and the test conditioned on "where a reader could know another way". Class: reports where the reporter's step may not be the only way to the task. Inputs: a question about how to pass a custom header through a client; a request for a retry limit by elapsed time where a timeout setting may already exist. It stays quiet for a crash report. These sentences give the rule its boundary (rule 4), so they are a fix.

**§4**
- Ownership: "where more than one could" and "Where the symptom sits in the project's own files, … no isolation is owed." Class: the isolation step. Inputs: a JDBC timezone defect seen through an ORM, where the rule fires; a dead link in a project's docs, where it is quiet. The second sentence is an example of the same boundary, not a new exception. Fix.
- "The nearest hit is the closest item the search returned, one with another symptom included: …" Class: reporting duplicate-search results. Inputs: a test-report defect where the search returns an issue about display names; an operator defect where the search returns an issue about the chart. General. Note that on a large tracker almost every search returns something, so this sentence leaves no input where the nearest-hit sentence stays out (rules 4 and 8).
- "Where the search found nothing, the report says so only in a slot the form or the genre has for what you searched, …; with no such slot, the query goes to the hand-over note." Class: a search with no result. Inputs: a GitHub form with an "I searched existing issues" field; a report to a mailing list. Fix.
- Count: "Where the count produced several reports, or a related report is known, …" and "A single report with no known relative says nothing about dependencies." Class: dependency statements. Inputs: a protocol change split into client and server reports; a defect split between a build tool and a test framework. It stays quiet for a single typo report. Fix.

**§5, question 4**
- "Where the observation shows the expectation by itself, … the observation is the grounding and needs no sentence of its own." Class: grounding that the observation already shows. Inputs: a DST conversion error, where the rule fires; a link that returns 404, where it is quiet. Fix.
- The new example of a weak grounding is a rewording and needs no check.

**§6**
- Attribution: "wherever a reader could take one for another; a report whose evidence is all your own pasted output needs no label." Inputs: a report that mixes a user's log with your own reproduction; a support ticket that combines a documented limit with an observation. Fix.
- Redaction: "Where you changed or removed anything, … and where nothing changed, say nothing." Inputs: a vendor ticket with a substituted hostname; a public report with a redacted token. Fix.
- Versions: "… whose behavior the symptom could depend on" and the matching test. Inputs: a defect in a Kubernetes operator; a defect in a browser rendering. Fix.
- "A misspelled name in a README fails under any version of the tool that reads it, …" This is an example of the quiet input. General, but see the note at the end.

**§8**
- "Where there is no form and no guide, a defect report opens with the core (§7): what you did and what you observed, with the pasted output, and what you expected." Class: reports with no form. Inputs: a report on a mailing list; a report to a project with no templates. General, though the clause after "(§7)" restates how §7 defines the core.
- "The parts below follow it in this order, each only where its condition holds: …" See the patches below.
- "A report whose parts fit in a few sentences carries no headings: …" Class: short reports. Inputs: a dead link; one CLI flag that a docs page names wrongly. General.
- "Any form's order replaces this one." This is a rewording.
- "A request and a question take the slots their references name, … under the same rule: …" See the patches below.

**§11**
- The preamble: "An item applies only where the rule it asks about applies, …", "An item that applies is answered by pointing at…", "they go in the review or the hand-over note…". Class: checklist items whose rule has a condition. Inputs: a crash report reviewed against Goal; a single report reviewed against Count. General.
- "an issue you file in your own repository to fix yourself is read the same way, and its Ownership, Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the issue." Inputs: an issue you file before fixing your own bug; a follow-up issue in a team service. General.
- The changed items for Goal, Ownership, Duplicates, Count, Grounding, Attribution, Reproducer, Redaction, Form, and Request name rules for the checklist, which counts as a citation. General.

**references/colleague-message.md**
- Goal row. See the patches below.
- Failing output row: "Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim." Class: chat messages that link the full log. Inputs: a red build with a CI link; a failing job with a link to its log viewer. General. It changes §7's trim rule, though, so it belongs in a row about §7, not §6.
- Reproducer row. See the patches below.

**references/project-conventions.md**
- "for a request, the acceptance criterion, the slot a backlog item most often lacks." See the patches below.
- "ownership, duplicates, and disclosure need no line in it." See the patches below.

**references/request-genre.md**
- "what it found goes in the prior-proposals slot below." This is a rewording plus a narrowing that matches §4. General.
- "Every request carries the first two. Each other slot appears only where its condition holds, …" and "A slot is what the request says, not a heading: a request that fits in a few paragraphs carries no headings". Class: short requests. Inputs: a request for a CLI option; a request for a new API in a library. General.
- "and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives." See the patches below.
- The boundaries on the slots: Who else is blocked ("where you know or the change is costly"), Out of scope ("where the request could be read as asking for more"), Prior proposals ("where the search found something or the process asks"), and Alternatives ("where you considered one a maintainer would suggest"). Inputs: a request that adds a dependency; a request to change a default. Fix.
- "otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says." See the patches below.
- "it belongs with the problem statement, in a sentence that says it does not fix it, as §3 of the skill says." See the patches below.
- Grounding: "the task and what it costs today, stated as such, with who else has it where you know." Fix.
- Backlog: "the acceptance criterion is the one a backlog item most often lacks." See the patches below.

**references/worked-cases.md**
- The changed introduction and Case 7. Class: a report that is only its core. Inputs: a misspelled environment variable; a dead link. General.

Verdict: contains patches

Patches:
- colleague-message.md, Goal row: "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none". Rule 7: it restates the boundary that §3 now carries. "Holds" would say the same thing.
- colleague-message.md, Reproducer row: "The versions of your tools only where the failure could depend on them". Rule 7: it restates the new condition of §6's version rule.
- SKILL.md §8: "The parts below follow it in this order, each only where its condition holds: what the expectation rests on, where the core does not show it (§5, question 4); the version of every layer, where the symptom could depend on more than the project's files at the commit the report names (§6); …". Rule 7: it restates the conditions of question 4 and of §6. The §6 copy has already drifted ("whose behavior the symptom could depend on" against "more than the project's files at the commit the report names").
- SKILL.md §8: "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings." Rule 7: it restates the new introduction to the slots in request-genre.md.
- request-genre.md: "and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives." Rule 7: it restates the summary rule of §7 and §9, and the negative-result rule of §3, which the Alternatives bullet in the same file also restates.
- request-genre.md: "otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says." Rule 7: it restates §4's rule for a search with no result.
- request-genre.md: "it belongs with the problem statement, in a sentence that says it does not fix it, as §3 of the skill says." Rule 7: it restates §3 and has already drifted from it. §3 still allows "under a heading or in a sentence".
- project-conventions.md: "ownership, duplicates, and disclosure need no line in it." Rule 7: it restates §11's rule for an issue you file to fix yourself.
- project-conventions.md: "for a request, the acceptance criterion, the slot a backlog item most often lacks", together with request-genre.md: "the acceptance criterion is the one a backlog item most often lacks". Rule 7: the same statement lives in two files, and this change had to edit both copies.

For the author: a misspelled name in a document is the example in question 4, in §6's version rule, in §8, and in Case 7. Rule 2 asks for examples from different kinds of input. If this is the input of the case that prompted the change, rule 6 also applies.
