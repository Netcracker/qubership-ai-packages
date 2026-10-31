# Final review: `4f69810..86028c3` (one commit: "lead the description with breaks unless the next release is a major")

**Claimed cases.** No task statement was handed over, so item 2 is answered from the commit message alone. No previous report exists, so there is no §4 table.

**Skills loaded.** I loaded `final-review` and read `english-developer-style` from the given directory. `test-authoring` was not needed, since there is no test code. `apm-authoring` is not among the three allowed skill copies, so I checked its rules by the form's analogues only.

**No-code change.** The commit is a skill, READMEs, version bumps, and research cases, so §2a applies throughout. The drift script was not run because there are no members to parse. The only gate I ran was `scripts/check-skill-descriptions.py`, which passed. I did not run `make check` or the install smoke test.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Three substantive findings.

- **Rule 5 contradiction.**
  - `SKILL.md:259` says that where §4 rule 5 copies the description into the commit body, "the lead stays" and "that body opens with its breaks and then its problem".
  - `SKILL.md:310` still says "Under §4 rule 5 the description is the commit body and takes the body's shape instead". The body's shape is problem first, as `SKILL.md:257` says.
  - `SKILL.md:86` says "Slot 1 opens the body". This is hedged for rule 5 in the added sentence, but the surrounding commit-body text still reads as problem first.
  - A reader gets two answers for a squash-merged description with a break.
- **Stale rule name in the case READMEs.**
  - Both `cases/pgjdbc-4367-breaks/README.md` and `cases/pgjdbc-4392-no-break/README.md` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". They cite it as SKILL.md §2.
  - The committed heading is "A break leads the description unless the next release from the target branch is a major". The rule's condition was inverted, from "promises compatibility" to "is not a major", and the quotation was not updated.
  - A reader greps for a sentence that does not exist.
- **Effort level.**
  - The commit message says Opus and Haiku ran at effort high.
  - `pgjdbc-4367-breaks/README.md` says "Haiku ran at effort `high`; Opus at the session's default". The `pgjdbc-4392-no-break` README says only "Haiku at effort `high`".
  - One of these statements is wrong.

Two smaller points:

- `SKILL.md:198` still says "Six slots, in order", while the same row now puts slot 3's break lines ahead of slot 1. The added paragraph covers it, so I rate this taste: put "(break lines may lead, below)" in the intro.
- `SKILL.md:490` says a break whose intent only a maintainer can settle goes in Scope as a question. `SKILL.md:238` says a failure extended to inputs that worked before goes "with the breaks, not in the Scope slot". These are probably reconcilable, since one is about intent and the other about classification. It needs one clause saying which wins for an unintended break.

No narrating words (`now`, `no longer`, `used to`) appear in the new rule text. The `now fails` and `now returns` in the example sentences are outcomes, not narration of the change.

## Item 2: claimed cases covered

The commit message makes six claims.

| Claim | Evidence |
| --- | --- |
| `pgjdbc-4367-breaks`, with the rule on Opus and Haiku, two runs each | Four results exist, with `skill-tree` files. The skill tree id `4798053…` matches `HEAD`. |
| Baseline on `origin/main`, one run each | The `baseline/` results exist. Their tree id `1f020ce…` matches `HEAD~1`. |
| `pgjdbc-4392-no-break`, two runs each | Four results exist, with `skill-tree` files. |
| Without the rule, both models put Why first and leave both breaks in place | Both baseline results open with `## Why`, with no break lead. In both, the result-shape line is in slot 3 and `grant insert` is in Scope. |
| With the rule, all four runs lead with the breaks and mark the result shape | All four open with `## Breaking changes`. The README table agrees. |
| Three of four move the extended failure out of Scope; one Opus run left it there | `opus/result-2.md` keeps `grant insert` in Scope, and the other three lead with it. This matches the README. |
| The control grows no section | None of the four control results has a `Breaking changes` heading or a compatibility sentence. |

The README word counts match `wc -w`.

Hunks no sentence claims: none. The version bumps in `apm.yml` and `marketplace.json`, the package README bullet, and the research README all belong to the change.

Commands in the changed files:

- The README's `git archive <rev> agent-packages/...` is a recipe for a manual run, with no script or CI job. It is not an outcome-bearing command, so I rate it taste.
- Whether `check-descriptions` or the `Makefile` runs anything over `research/.../cases` was not checked.

Claimed rule parts with no case:

- The major-release arm ("breaks stay first in slot 3").
- The unknown-release arm ("the breaks lead").
- The commit-body arm ("breaks as the first `User-visible:` lines", "that body opens with its breaks and then its problem").

Substantive: the first two are also item 3 partitions, and the third is a claimed behavior with no run. Either add a case per arm or have the commit message and README say that only the patch-release arm was run.

## Item 3: boundaries, partitions, negative control (analogue: genres, modes, the negative control)

- **Partitions the rule names:** a patch target, a major target, and an unknown target. Only the patch target is exercised, since the prompt gives `42.7.14`. Substantive, as above.
- **The mid-version case:** a minor release is neither a patch nor a major. The rule leads with breaks in a minor release, and no run covers that either. This is a taste-level note.
- **Negative control:** present. It is `pgjdbc-4392-no-break`, with two runs per model, and it checks that no heading or compatibility sentence appears.
- **Strength of the control:** it uses the same patch target as the breaks case, so it controls for "no break means no section". It does not control for a major target with a break.
- **State left by an earlier version:** not applicable.
- **Limited sample:** a single case family, two runs per model. The README is honest that the `grant insert` move is not reliable ("most of the time and not always").
- **Values users already pass:** not applicable.

Table of added instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release … is a major" | A change whose only differences are internal renames, or error-message wording changes that a caller does not catch | Might mark the wording change as a break under "a changed error code for a failure a caller may catch", and add a Breaking changes lead for a message-text change | The rule says "error code for a failure a caller may catch", which ends it for message text. No clause is needed. |
| "Where nothing says which release it is, the breaks lead" | A repository with no version file and a single-maintainer main branch | A lead for any break, which costs a paragraph by the rule's own stated trade-off | The text states this trade-off. Not a finding. |
| "A failure the change extends to inputs that worked before is a break" | A fix that makes an already-failing statement type fail the same way in more positions, where the new positions never worked | Might call `grant insert` after a `;` a break, when the earlier text was only "success without RETURNING" | The text says "inputs that worked before". `grant insert` is exactly that case. Not a finding. |
| "The description then opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings" | A short prose description of four paragraphs or fewer | A heading in a headingless description, or prose that leads with breaks and no heading | "where the description has headings" ends it. |

No row is a finding.

## Item 3a: level, placement, environment

- **Layout:** the new cases sit under `research/change-description-authoring/cases`. The research README layout list (`cases/`) and the closing paragraph are updated.
- **Sibling cases:** there are no sibling cases to share a fixture with, so no copied fixture.
- **Gate:** I ran only `check-skill-descriptions.py`, which passed. I did not run `make check`, the markdown lint, or the install smoke test. The research README says result files are excluded from markdownlint, and the new `result*.md` files are not shown to be excluded. I rate that a possible gap, not a finding.

## Item 4: names by content, not by position

Taste only. `result-2.md` is an ordinal name for a second run, and `README.md` then refers to `opus/result.md` and `opus/result-2.md`. A reader of the table can tell them apart only by row order. Name the files by what differs (a run date or seed).

## Item 5: the failure report (analogue: the rule's detection)

- The case READMEs list explicit checks, but the checks are not mechanized. A reader judges "passes" by eye.
- Check 3 in the breaks README says the line "is a break line, not left in Scope". This detects the intended property.
- Check 5 ("stated once") and the literals check detect their own rules.
- The skill's §8 checklist now has a Breaks item and the Problem item is edited.

## Item 6: what the writer says it verified

The commit carries its own evidence: baseline runs on `origin/main` that fail checks 1 to 3, and rule runs that pass them. Two limits:

- The sample is small.
- The Opus effort level conflicts between the commit message and the README (Item 1).

## Item 7: siblings of the change

- **Set members:** the version bump is in `apm.yml`, `marketplace.json`, and the package `apm.yml`. The two other `1.4.0` entries in `marketplace.json` (lines 22 and 46) are other packages. No lockfile entry names this package.
- **Package README:** the new bullet is present.
- **Other mentions of the break order:**
  - `SKILL.md:543` (the changelog entry) says breaking changes are "sorted first within their category". This is a different artifact and consistent with the new rule.
  - `SKILL.md:845` ("breaks first") is the existing slot-3 checklist line. The new Breaks checklist item sits beside it. The two read the same and are not in conflict.
- **Consumers of the skill outside the package:** I did not check `docs/` or the `.agents`/`.claude` copies, since those carry only the style skill.
- **Findings from rule 5:** the §4 rule 5 sites (`SKILL.md:310`, `:86`) are the real siblings, listed under Item 1.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Rule 5 contradiction: "the lead stays … opens with its breaks" against "takes the body's shape instead" | Substantive | `SKILL.md:259` vs `:310`, and `:86` | State once, in §2, what a rule-5 body looks like, and make `:310` and `:86` point to it. |
| The case READMEs quote a rule heading that does not exist | Substantive | `cases/pgjdbc-4367-breaks/README.md` (opening paragraph), `cases/pgjdbc-4392-no-break/README.md` (opening paragraph) | Quote the committed heading, "A break leads the description unless the next release from the target branch is a major". |
| The effort level of the Opus runs differs between the commit message and the README | Substantive | `cases/pgjdbc-4367-breaks/README.md` ("Running it") | Make both say the same; if Opus ran at the session default, correct the commit message, or the reverse. |
| The major and unknown-release arms and the commit-body arm are claimed by the rule and untested | Substantive | `SKILL.md:244–260` | Add a case for each arm, or say in the commit message and the README that only the patch arm was run. |
| `SKILL.md:198` says "Six slots, in order", but the rule now moves slot 3 ahead | Taste | `SKILL.md:198` | Add "(the break lines may lead, below)". |
| `SKILL.md:490` and `:238` could conflict on a break whose intent is open | Taste | `SKILL.md:238`, `:490` | One clause saying which applies to an unintended break. |
| `result-2.md` names a run by ordinal | Taste | `cases/*/*/result-2.md` | Name by what differs. |
| No minor-release case | Taste | `SKILL.md:244` | Name it in the rule, or leave it. |

**Not checked:** the `make check` gate, markdownlint, and the install smoke test were not run. I did not do a style-only pass over the prose, and I did not read the stored result files beyond the headings, the `Scope` lines, and the literals above. I did not verify the pgjdbc #4367 or #4392 facts against the upstream repository, since there is no network.
