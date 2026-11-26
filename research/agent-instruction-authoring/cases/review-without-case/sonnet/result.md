## Change 1: `adr-authoring`

| Sentence | Class | Two inputs | Result |
| --- | --- | --- | --- |
| Guarantee of a dependency: the Context fact applies only where the source is not a decision record; where it is, cite its rule by what it is about | Where a rule depends on a guarantee, which section carries it | A base image's README promises certificate loading; an accepted record's rule on retry limits is what the guarantee rests on | Class and inputs found. Boundary stated. |
| Context template: no rule of this record or another is restated (**One home**) | Context restating rules | A record about token signing whose Context repeats a key-length rule; a record about CI whose Context repeats a cache rule from another record | Class and inputs found. It cites an existing rule. |
| Numbers freeze: a rule of a record in another repository is cited as `owner/repo ADR-NNNN Rn` | Citing a rule across repositories | A record that builds on a platform team's record; a record that supersedes a record in a shared-standards repository | Class and inputs found. |
| Numbers freeze: every record the text cites appears under **Related ADRs**, except a retired number that Context maps | Whether a cited record is linked | A Justification citing ADR-0091 R7; a Confirmation entry citing another record's rule | Class and inputs found. Exception stated. |
| **One home**: stated once, in one rule; cite by number (or by section and quote where the record has no numbers) | Where a requirement lives | A timeout stated in a rule and again in Consequences; a record with unnumbered rules | Class and inputs found. |
| **One home**: name what a foreign rule is about, not what it decides | How a rule of another record is cited | A Justification citing a retry limit; a Consequences entry citing a trust rule | Class and inputs found. It gives an example. |
| **One home**: the rule's own record may say what the rule decides outside **Rules** and Context | What restating is allowed in the rule's own record | A **Negative** entry that names a cost; an **Open points** entry that names affected rules | Class and inputs found. It reconciles the sentences before it. |
| **Cite only what the reader needs** | Citations that change no verdict | A "see also" in a Justification; a rule that cites a neighboring rule it must merely not break | Class and inputs found. Boundary stated (earns its place if removing it changes what a checker tests). |
| **Every requirement is a rule**: a section that refers to a requirement cites the rule, not the record | References from **Confirmation** and **Implementation notes** | A Confirmation entry; an Implementation note on migration | Class and inputs found. |
| **No pointer rules**: also a rule that only repeats a requirement of another rule; leave it out, link in the Justification | Rules that add a number and no requirement | A rule that says another rule also holds for exports; a rule that repeats a timeout from an earlier rule | Class and inputs found. It adds the missing remedy to an existing heading. |
| Drafting checklist: adds **No pointer rules** and **Cite only what the reader needs**, and a read of cited sentences outside **Rules** | Pre-publication read | A Context section with a restated rule; a Consequences entry with a decorative citation | Class and inputs found. The additions cite existing rules. |

Verdict: general change

## Change 2: `apm-authoring`

| Sentence | Class | Two inputs | Result |
| --- | --- | --- | --- |
| The condition on when the part is absent comes first, then "where it is owed, what to state and where to stop" | Fixing an agent output whose section is empty or wrong | A commit body that guesses at a cause; a localization file whose placeholders were left untranslated, fixed by saying when a string needs no translation | Class and inputs found. Boundary stated. |
| "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise." | The reason for that order | A review section padded with "none found because…"; a PR description that always carries a "Testing" section | Class and inputs found. It states a distinction the earlier text left implicit and restates no other rule. |

The rest of the diff is rewrapping.

Verdict: general change

## Change 3: `problem-report-authoring`

| Sentence | Class | Two inputs | Result |
| --- | --- | --- | --- |
| §3 Goal: state it where the step may not be the only way; a crash, a red build, a typo, or a broken page is its own goal | Task versus step | "How do I limit retries by elapsed time?"; a crash with a stack trace | Class and inputs found. Boundary stated. The checklist item mirrors it. |
| §4 Ownership: no isolation where the symptom sits in the project's own files | Isolation owed only where more than one project could own the defect | A dead link in a docs page; a crash whose trace stops in the project's code | Class and inputs found. Boundary stated. |
| §4 Nearest hit is the closest item returned, another symptom included | What the duplicate search records | A closed will-not-fix with a related symptom; an open report with a different error | Class and inputs found. |
| §4 Null search: stated only in a slot that asks for the query, otherwise in the hand-over note | Where "found nothing" goes | A form with a "searched for" field; a mailing-list post | Class and inputs found. Boundary stated. |
| §4 Dependencies stated only where several or related reports exist | Dependency lines | A single report with no relatives; a client and a server report that need a coordinated change | Class and inputs found. Boundary stated. |
| §5 Q4: an observation that shows the expectation by itself is the grounding | Self-evident expectations | A crash; a link that returns 404 | Class and inputs found. Boundary stated. |
| §5 Q4: the plain-words example for a weak grounding changed to "nothing in the documentation promises this; it rests on our own setup" | Wording of a weak grounding | A request resting on one team's setup; a regression of undocumented behavior | Class and inputs found. It replaces an example. |
| §6 Source labels only where a reader could confuse the kinds; none for all-own evidence | Attribution | A report that is all your own run; a report mixing a user's log with your run | Class and inputs found. Boundary stated. The checklist item mirrors it. |
| §6 Redaction: say what changed only where something changed | The change note | A public-repo reproducer with nothing removed; a log with a token | Class and inputs found. Boundary stated. |
| §6 Versions: only layers whose behavior the symptom could depend on | Version listing | A typo in a README; a deployment failure through a chart and a cluster | Class and inputs found. Boundary stated. The checklist items mirror it. |
| §8 No-form order: core first, other parts only where their condition holds | Report shape without a form | A one-sentence docs typo; a library defect with a reproducer | Class and inputs found. Conditions stated. |
| §8 "A report whose parts fit in a few sentences carries no headings… (case 7)" | Headings | Same two inputs | Class and inputs found. It cites the worked case. |
| §11 preface: items apply only where their rule applies; no "none" answers; own-repo issue answers go in the hand-over note | Checklist applicability | A question to a forum; an issue filed in your own repository | Class and inputs found. Boundary stated. |
| §11 item edits (Ownership, Duplicates, Count, Grounding, Reproducer, Redaction, Form, Request) | Same boundaries as the rules they ask about | See the rows above | Citations of the rules above. |
| `colleague-message.md` Goal row: holds where you ask how to do something | Chat message | "How do I run this migration locally?"; "main is red" | Class and inputs found. It applies a rule already bounded in §3. |
| `colleague-message.md` output row: where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim | Output in chat with a link | A CI run link; a log viewer link | Class and inputs found. It states the genre's exception to §7. |
| `colleague-message.md` Reproducer row: tool versions only where the failure could depend on them; a failure CI shows too does not | Versions in chat | A failure that appears only locally; a failure CI also shows | Class and inputs found. |
| `project-conventions.md`: only the acceptance criterion is "most often lacking"; ownership, duplicates, and disclosure need no line | Self-filed issue | A backlog request; an issue you file to fix yourself | Class and inputs found. It matches the changed rules. |
| `request-genre.md`: the duplicate search "goes in the prior-proposals slot" | Where the search result goes | A request with a prior discussion; a request with none | Class and inputs found. |
| `request-genre.md` slots: who else is blocked, scope, prior proposals, and alternatives, each only where its condition holds | Request slots | A one-line change; a change that adds a dependency | Class and inputs found. Boundaries stated. |
| `request-genre.md` Grounding: "the task and what it costs today… with who else has it where you know" | Grounding for a new need | A new capability; an improvement | Class and inputs found. |
| `worked-cases.md`: case 7, and the header edits | A report that is only its core | A misspelled variable on a docs page; a dead link | Class and inputs found. It is an example, and the header says it is constructed. |

Two sentences are patches:

1. `request-genre.md`, in the slots introduction: "A slot is what the request says, not a heading: a request that fits in a few paragraphs carries no headings, and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."
   - Rule 7 makes it a patch. It restates the §8 rule on headings and slots.
   - It also restates the §7 rule that each section carries a fact absent from earlier ones.
   - Its "setting that does not serve you" clause repeats the negative-result rule of §3, which the Alternatives bullet in the same file already cites. That clause fits one input (a setting that fails) and names no class.
2. §8, last sentence of the no-form paragraph: "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."
   - Rule 7 makes it a patch. It repeats the clause in the `request-genre.md` sentence above, so the headings rule now has two homes that can drift.
   - The home should be one of them, with the other citing it by name.

Verdict: contains patches
