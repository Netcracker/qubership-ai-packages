## Change 1

**Sentences**

- **Guarantee of a dependency:** "Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base image's README, state the guarantee in **Context** as a fact, with its source."
  - Class: a rule that relies on a promise a dependency documents outside any decision record.
  - Inputs: a record on outbound TLS that relies on a base image's entrypoint trusting a certificate directory; a record on request retries that relies on an HTTP client's documented handling of idempotent methods.
  - This sentence gives the old sentence its boundary.
- **Guarantee of a dependency:** "Where its source is a decision record, cite its rule by what it is about instead (**One home**)."
  - Class: a rule that relies on what another record decides.
  - Inputs: a service record that relies on a platform record's rule on sidecar mTLS; a schema-migration record that relies on an organization record's rule on backup retention.
  - It cites **One home** and does not restate its condition.
- **Template, Context:** "…and no rule of this record or another is restated (**One home**)."
  - Class: a Context section that paraphrases a rule.
  - Inputs: a token record whose Context retells another record's key-rotation rule; a cache record whose Context previews its own TTL rule.
  - It is a citation, placed where the writer fills the section.
- **Numbers freeze:** "…and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`."
  - Class: a citation of a record kept in another repository.
  - Inputs: an application repository that cites a rule of the platform repository; a library that cites a rule of the organization's security repository.
- **Numbers freeze:** "Every record the text cites appears under **Related ADRs**, except a retired number that Context maps to its replacement…"
  - Class: a citation the reader cannot follow to a file.
  - Inputs: a Justification that cites a neighboring record's rule; a partial supersession that cites the rule it replaces.
  - It has one exception, and **Record numbers** explains it.
- **One home:** "a requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short quote where the record has no numbers)."
  - Class: a requirement repeated outside its rule.
  - Inputs: Implementation notes that repeat a timeout; a citation of an unnumbered legacy record.
  - It rewords the old rule and adds the unnumbered case.
- **One home:** "Where you cite a rule of another record, in any section, name what the rule is about, not what it decides…"
  - Class: a cross-record citation that copies the other rule's value.
  - Inputs: a Justification that says another record "allows three retries"; a Context that gives another record's token lifetime in minutes.
- **One home:** "In the rule's own record, a section other than **Rules** and Context may say what the rule decides, with its number…"
  - Class: a summary of a rule inside its own record.
  - Inputs: a Negative that names a changed default by rule number; an open point that asks for the value R5 needs.
  - It gives the previous sentence its boundary.
- **One home:** "A restatement drifts." and "A table that summarizes rules holds rule numbers."
  - The first keeps the old reason. The second is shortened and says the same thing.
- **Cite only what the reader needs** (all five sentences):
  - Class: a citation that changes no check and supplies no reason.
  - Inputs: a database-choice record with a "see also" to the logging record; an endpoint record whose rule reminds the reader that the authentication record still applies.
  - Quiet input: a rule whose extent depends on a term another record defines. The citation stays there.
  - The first sentence carries the boundary.
- **Every requirement is a rule:** "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record."
  - Class: a Confirmation entry or an implementation note that points at a whole record.
  - Inputs: a Confirmation entry that reads "as ADR-0091 requires"; Implementation notes that read "follow ADR-0040".
  - It is a citation.
- **No pointer rules:** "Leave it out; where an approver needs the link, give it in the Justification."
  - Class: a pointer rule whose link an approver still needs.
  - Inputs: "R9. ADR-0031 R4 applies to this client"; a rule that only says the admin API follows R1.
- **Drafting from the user's input:** the reading list gains **No pointer rules** and **Cite only what the reader needs**, and a second reading over the sentences outside **Rules** is added.
  - These name rules for a final check, so they are citations under rule 7.

**Patches**

- "a rule that only repeats a requirement of another rule" (**No pointer rules**). This restates **One home** ("a requirement is stated once, in one rule") without citing it (rule 7). A second rule that carries the same requirement already fails **One home**, so the two sections now state one rule. Drop the clause, or cite **One home** for it.

Verdict: contains patches

## Change 2

**Sentences**

- "…first give that part a condition that ends it: when the part is absent, and, where it is owed, what to state and where to stop."
  - Class: an instruction whose output part is padded or wrong on inputs that don't need it.
  - Inputs: a changelog skill whose "Breaking changes" section reads "None" on a patch release; a review skill whose "Security" section guesses at risks in a change that only touches docs.
  - Quiet input: a commit subject line, which is owed on every input. The closing sentence ("Add one only where the reader needs X on every input") keeps the rule quiet there.
  - The old text offered the absence condition as an alternative. The new text makes it the first requirement, which gives the rule its missing boundary.
- "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise."
  - Class: the same. This sentence gives the reason for the order.
  - Inputs: a test-authoring skill that limits a doc comment to the contract but still writes one on every test; a pull request skill that limits "Risks" to observed risks but still writes the heading for a typo fix.

The rest of the hunk only rewraps unchanged text.

Verdict: general change

## Change 3

**Sentences, SKILL.md**

- **§3, Goal** (the new heading, its two new sentences, and the revised test):
  - Class: a report about a step when the task has other routes.
  - Inputs: a question on setting a proxy for one CLI subcommand, from a user who wants all traffic proxied; a request for a hook to rewrite headers that the library's middleware already rewrites.
  - Quiet inputs: a crash; a red build. This is a boundary.
- **§4, Ownership:** "where more than one could" and "Where the symptom sits in the project's own files … no isolation is owed."
  - Class: a defect whose location already names its owner.
  - Inputs, quiet: a dead link in docs; a null dereference whose trace stops in the library.
  - Input, fires: a TLS failure seen through a proxy, an ORM, and a driver.
  - This is a boundary.
- **§4, Search:** "The nearest hit is the closest item the search returned, one with another symptom included…"
  - Class: a search whose hits differ from the report.
  - Inputs: a Helm chart bug whose search returns an issue about another value of the same template; a CLI crash whose search returns a crash in another subcommand.
  - The sentence has no limit for a hit that shares nothing with the report. On a typo report, it makes the report cite an unrelated issue, against the reader deletion test of §7. It is not a patch, but it needs a rule-4 boundary.
- **§4, Search:** "Where the search found nothing, the report says so only in a slot…"
  - Class: a null search result.
  - Inputs: a GitHub form with an "I searched existing issues" field; a mailing-list report, which has no fields.
  - This is a boundary.
- **§4, Count:** "Where the count produced several reports, or a related report is known…" and "A single report with no known relative says nothing about dependencies."
  - Class: a dependency sentence on a report with no relative.
  - Inputs: a client and server split for a protocol change (fires); a lone docs typo (quiet).
  - This is a boundary.
- **§5, question 4:** "Where the observation shows the expectation by itself … the observation is the grounding and needs no sentence of its own."
  - Class: an expectation that the observation makes plain.
  - Inputs, quiet: a segfault in a CLI; a link in a README that returns 404.
  - Input, fires: a wrong rounding mode.
  - This is a boundary. The plain-words example swap rewords an example and leaves the rule as it was.
- **§6, Attribution:** "…wherever a reader could take one for another; a report whose evidence is all your own pasted output needs no label."
  - Class: evidence from mixed sources.
  - Inputs: a customer's log next to your own reproduction; a vendor document quoted beside your transcript.
  - Quiet input: a single CLI run of your own. This is a boundary.
- **§6, Redaction:** "Where you changed or removed anything … and where nothing changed, say nothing."
  - Class: the sanitization note.
  - Inputs: a public-tracker report with a renamed service (fires); a report in the team's backlog where nothing changed (quiet).
  - This is a boundary.
- **§6, Versions:** "…whose behavior the symptom could depend on", the revised test, and the README example.
  - Class: a layer that can't change the outcome.
  - Inputs: a JDBC driver bug that depends on the JVM (fires); a typo in a README (quiet).
  - This is a boundary.
- **§8, no form:** "a defect report opens with the core (§7)…", the reproducer condition, "A report whose parts fit in a few sentences carries no headings…", and "Any form's order replaces this one."
  - Class: an unstructured channel with no guide.
  - Inputs: an email to a maintainer; a GitHub project with no templates.
- **§11, opening:** "An item applies only where the rule it asks about applies … skipped, not answered with 'none'" and the sentences on where the answers go.
  - Class: running the checklist on a draft where a rule's condition is absent.
  - Inputs: a review of a typo report, where the Measurement item is skipped; a review of a support ticket with no workaround.
  - This gives the old "every item gets an answer" its boundary.
- **§11, checklist items** (Goal, Ownership, Duplicates, Count, Grounding, Attribution, Reproducer, Redaction, Form, Request):
  - They name the new conditions of the rules they check. A final checklist that names a rule is citing it (rule 7).

**Sentences, references**

- **colleague-message.md, "Failing output pasted as text" row:** "Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim."
  - Class: a chat message backed by a CI link.
  - Inputs: a red pipeline with a run link; a failing nightly job linked from the CI dashboard.
  - Quiet input: a local failure with no link.
  - This changes the shape of the §7 trim rule for this genre, which is what the table is for.
- **project-conventions.md, backlog paragraph:** "for a request, the acceptance criterion, the slot a backlog item most often lacks" and "ownership, duplicates, and disclosure need no line in it."
  - Class: a request or a self-filed issue in a team's own backlog.
  - Inputs: a Jira story for an export button; an issue for a flaky test you will fix yourself.
  - Each sentence repeats one in another file: the first matches request-genre.md, and the second matches §11. The duplication existed before this change, and the change edits both copies the same way. Making one copy cite the other would remove it.
- **request-genre.md:**
  - The opening reword ("what it found goes in the prior-proposals slot below") keeps the same rule.
  - The paragraph that opens **The slots**:
    - Class: a short request padded with empty slots.
    - Inputs: a request for `--json` on one CLI command; a request for a configuration key that raises a timeout.
  - The boundaries on "Who else is blocked", "What is out of scope", and "Alternatives":
    - Inputs: a request that adds a new dependency (fires); a request for a missing anchor in the docs (quiet).
  - The revised grounding sentence for a new need:
    - Class: a request whose need no document promises.
    - Inputs: a request for a CLI feature no page mentions; a request for a library option no page mentions.
  - The acceptance criterion moved up the list. A move needs no class.
- **worked-cases.md, opening and case 7:**
  - Class: a report that is only its core.
  - Inputs: a dead link in a README; a wrong default in `--help` output.
  - A misspelled name is now the example in four places: §5 question 4, §6 versions, §8, and case 7. Four examples of one input teach the agent that the boundaries "no heading" and "no version" are about typos (rule 2). Spread them across a 404 link, a wrong default, and a crash.

**Patches**

1. colleague-message.md, "The goal, not only the step" row: "Holds where you ask how to do something and the step may not be the only way…"
   - It restates the boundary that §3 now has, with a different extent (rule 7). §3 applies wherever "a reader could know another way to what you were doing". The row applies only where "you ask how to do something", so a message about a blocked task that isn't a how-to question is governed by two rules that disagree.
2. colleague-message.md, "Reproducer" row: "The versions of your tools only where the failure could depend on them…"
   - It restates the condition of the §6 version rule (rule 7).
3. §8: "the version of every layer, where the symptom could depend on more than the project's files at the commit the report names (§6)" and "what the expectation rests on, where the core does not show it (§5, question 4)."
   - Both restate the conditions of the rules they cite, and the version condition already uses other words than §6 (rule 7). "Each only where its rule holds (§5 question 4, §6)" would carry them.
4. §8: "A request and a question take the slots their references name … under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."
   - It restates the paragraph this change adds to request-genre.md, under **The slots** (rule 7).
5. request-genre.md, prior-proposals slot: "Where the process makes what you searched a required field, the query goes there; otherwise a search that found nothing goes to the hand-over note, as §4 of the skill says."
   - It restates the rule on null search results in §4 (rule 7).
6. request-genre.md, Alternatives slot: "…it belongs with the problem statement, in a sentence that says it does not fix it, as §3 of the skill says."
   - It restates §3, and the edit makes the copy disagree with its source (rule 7). §3 still allows "a heading or a sentence", and worked case 3 uses a heading.

Verdict: contains patches
