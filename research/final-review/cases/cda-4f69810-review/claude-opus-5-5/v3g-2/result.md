# Final review: `d79c43d..4f69810` (change-description-authoring 1.4.0)

I found six substantive findings and two taste findings.

There is no task statement, so item 2 takes its claimed cases from the commit message alone. The change has no code, so the form uses the §2a analogues throughout.
- **Drift script:** I ran `comment-drift.py d79c43d…` and it printed nothing, because the change touches only Markdown and YAML.
- **Skills loaded:** `english-developer-style` and `test-authoring`, from the given directory. `apm-authoring` is not among the three skills I was allowed to load, so I cite it only by the rule names final-review quotes.
- **Gates run:** `scripts/check-skill-descriptions.py` passed ("all 27 skill descriptions are within 1020 characters"), and so did `make check` (versions aligned, index in sync, exit 0).

## Item 1: comments consistent with the code and with each other
Analogue used: statements one changed file makes about another file, and the skill's worked examples.

- **The README contradicts the skill.** `README.md:28-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:97-100` and the commit message allow a consequence derived from the code, once it is traced to what a caller sees and marked as derived. A reader of the README would conclude that no consequence may ever be written.
- **The What-slot *After* example puts an outcome in prose.** `SKILL.md:353` says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome a caller can observe.
  - The paragraph right after it sends the same outcome (`IllegalStateException` from `Pool.acquire()`) to "User-visible changes".
  - That contradicts "A fact stated in slot 3 is not restated in slot 2" (around line 225).
  - It also contradicts the commit message's claim that the example "no longer puts an outcome in prose".
- **The *After* example's second sentence breaks its own rule.** "…used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly" gives a reason and then the edit (`sendWithRetry`→`sendDirect`). The rule at lines 342-345 cuts exactly that: "even under a lead-in that states a reason … state the reason for the decision, not the edit".
- **Cross-references checked and fine:** the §7 pointer "(§2, the What slot)", the §5 pointer for public identifiers, the changelog row's "(§2, slot 2)", and the slot counts ("Five slots", "Six slots", unchanged).

## Item 2: claimed cases covered
Claims from the commit message, each against the section that handles it and the checklist line that detects it:

| Claim | Section | Detection (§8) |
| --- | --- | --- |
| Slot 2: audit or code-reading defect names what found it, sentence ends there | 81, 90-96 | Symptom item |
| Changelog names the condition alone for it | 475 | Symptom item (the Changelog item does not mention it) |
| Derived consequence only when traced and marked as derived | 97-100 | Symptom item |
| "Say so" kept for a defect with no symptom by construction | 94-96 | Symptom item |
| What slot: a hunk-recoverable sentence is translation even with a reason lead-in; a public identifier is named once | 342-359 | Translation item (see item 5) |
| §7 points to the rule | 762-764 | Nothing item |
| §2 asks for "what changed that the diff does not show" | 288 | Decision item |
| Rejected alternatives: mechanism as a fact about the merged code | 370-373 | Alternatives item |
| Open questions: answered, kept in Scope for a maintainer, or dropped | 199, 458-464 | Discussion item |
| Slot 2 and What slot each carry a bad and a good example | 92-93, 349-358 | — |

- **Commands:** the changed text contains no command lines, so there are none to check.
- **Hunks read the other way:** the version bumps 1.3.0→1.4.0 (`apm.yml:168`, the package's `apm.yml:2`, `marketplace.json:291`) are claimed by no sentence of the message. The two earlier commits of this package each said so ("Version 1.2.0 to 1.3.0."). Every other hunk maps to a claim above.

## Item 3: boundaries, partitions, and the negative control
- **Partitions without evidence.** The trial drafted one pull request description. The slot-2 rule also changes the commit body (line 81) and the changelog entry (line 475), and the skill claims both as artifacts. Neither has any evidence, and only one input change was used.
- **Earlier version left behind:** the package installs over 1.3.0 by replacing the files, and nothing persists between versions, so this partition does not apply.

Table of added instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it, end the sentence there; changelog gives "the condition alone" (81, 90-93, 475, §8 Symptom) | An audit-found defect whose new failing test reproduces `IllegalStateException: pool closed` | Slot 2 and the changelog give no diagnostic, so R3 has nothing to grep (§3: "the symptom omitted costs R3 the whole entry") | "where no run or test has shown the failure" |
| Maintainer-only question kept in the Scope slot (199, 458-464, §8 Discussion) | Squash with "title and description" (§4 rule 5) | An open question written into the permanent commit body, already settled by the time it merges | "outside a description that §4 rule 5 makes a commit body, where it goes in a comment" |
| Translation test, sentence by sentence (§8 line 826) | A description that adds a system property, or one sentence that pairs a reason with its edit | It deletes the property name the diff shows, and keeps the reason-plus-edit sentence (detail under item 5) | Stated in the findings table |

Not findings:
- "A consequence derived from the code earns a sentence only after it is traced…", ended by "only after it is traced to the point where a caller sees it".
- "An obstacle the change itself removes is a step…", ended by "check the mechanism against the code after the change".
- "what changed that the diff does not show", ended by its own condition.

## Item 3a: level, placement, and the environment
None. The rules sit in the package's `SKILL.md`, the README summary is updated, and `apm.yml` and the marketplace index are in sync (`make check` passed). No added sentence reads as generic tutorial text.

## Item 4: names by content, not by position
- `SKILL.md:358`, "the first sentence says why", points to a sentence by its ordinal. "The startup sentence" would name it by content. This is taste.
- The parenthetical "(measured: three of three drafts repeated as open a question the code answered)" at line 464 is attached to the "Leave a question out only when…" sentence. The measurement supports "answered", not "left out". This is taste.

## Item 5: the failure report
Each new rule is reached by a checklist item. The Translation detection (line 826, "delete each sentence…; where the diff still says it, leave it deleted") checks a different property from the rule, in two directions:
1. **It keeps too much.** A sentence with a reason lead-in survives the test, because the diff does not say the reason. The rule says that sentence is still translation. The commit message reports that drafters check against §8 rather than §2, and that translation "persists in about one draft in two". This gap fits that result.
2. **It cuts too much.** A sentence that names a public identifier the change adds is something "the diff still says", so the item deletes it, against the exception at lines 345-347.

## Item 6: what the writer says it verified
- **Stated:** counts over fifteen blind Opus drafts, and an admission of what was not covered:
  - the drafts ran against 1.0.1, three minor versions back;
  - the current open-question rule and the What-slot example were not re-run.
- **Not in the repository:** the drafts. `research/change-description-authoring/` has no trial directory, unlike `research/problem-report-authoring/trial`.
- **The symptom arms add up to 14 drafts (2 + 10 + 2), not fifteen.** The message doesn't say where the fifteenth went.
- **No noise check:** none of the runs used an input where an added item is noise (§2a asks for one), and none checked that the output did not grow there.
- **"Hunk translation dropped":** the message gives no counts before or after.
- I did not run any trial myself.

## Item 7: siblings of the change
None.
- **Index entries:** the marketplace and `apm.yml` entries are bumped. The descriptions there and in the frontmatter didn't need to change, because the set of artifacts is the same.
- **Umbrella:** `qubership-repo-essentials` includes the package by path with no pinned version, and earlier bumps of this package didn't touch it either.
- **`english-developer-style`:** its commit/PR module (lines 492-510, all three copies) says "state the observable defect or the violated contract" first. That fits the audit rule.
- **Other skills:** no other skill states the old "no observable symptom" rule.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| An audit-found defect reproduced by a test loses its diagnostic in slot 2 and in the changelog | Substantive | SKILL.md:81, 92, 475 | Add "where no run or test has shown the failure" to the rule |
| The Translation checklist item keeps reason-plus-edit sentences and deletes new public identifiers | Substantive | SKILL.md:826 | Restate the item as the rule: cut the edit even after a reason, and keep a public identifier the change adds, removes, or renames |
| The What *After* example states an outcome in prose that also goes on a User-visible line; its second sentence keeps the edit after the reason | Substantive | SKILL.md:353-355 | Rewrite it so it gives the reason only and leaves the failure to the User-visible line, as the commit message claims |
| The README forbids any predicted failure; the skill allows a traced one marked as derived | Substantive | README.md:28-30 | Align the README with SKILL.md:97-100 |
| Under §4 rule 5 the maintainer-only question lands in the permanent commit body | Substantive | SKILL.md:461 | Add a clause for rule 5 that moves the question to a comment |
| The trial covers only PR descriptions from one input and an old version, and the drafts are not in the repo | Substantive | commit message; research/ | Draft a commit body and a changelog entry under 1.4.0, add an input where the rules are noise, and store the drafts or say where they are |
| Version bump hunks are claimed by no sentence of the message | Taste | apm.yml:168 and two more | Add "Version 1.3.0 to 1.4.0." as the earlier commits did |
| Ordinal "the first sentence", and a measurement attached to the wrong sentence | Taste | SKILL.md:358, 464 | Name the sentence by its content, and move the parenthetical |

I did not run any drafting trial, did not load `apm-authoring` (as instructed), and did not do a style-only pass over the prose.
